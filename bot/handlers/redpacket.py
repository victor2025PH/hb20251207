"""
Lucky Red - 紅包處理器
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger
from decimal import Decimal
import uuid
import random
from datetime import datetime, timedelta

from shared.config.settings import get_settings
from shared.database.connection import get_db
from shared.database.models import User, RedPacket, RedPacketClaim, CurrencyType, RedPacketType, RedPacketStatus
from telegram import Bot

settings = get_settings()


async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /send 命令"""
    user = update.effective_user
    chat = update.effective_chat
    
    # 獲取用戶 ID（不返回 ORM 對象）
    from bot.utils.user_helpers import get_user_id_from_update
    from bot.utils.i18n import t
    user_id = user.id if user else None
    tg_id = await get_user_id_from_update(update, context)
    
    # 只能在群組中發紅包
    if chat.type == "private":
        await update.message.reply_text(t('send_command_group_only', user_id=tg_id))
        return
    
    # 解析參數: /send <金額> <數量> [祝福語]
    args = context.args
    if len(args) < 2:
        send_usage = t('send_command_usage', user_id=tg_id)
        send_example = t('send_command_example', user_id=tg_id)
        await update.message.reply_text(f"{send_usage}\n{send_example}")
        return
    
    try:
        amount = Decimal(args[0])
        count = int(args[1])
        default_message = t('default_blessing', user_id=tg_id)
        message = " ".join(args[2:]) if len(args) > 2 else default_message
    except (ValueError, IndexError):
        await update.message.reply_text(t('send_command_invalid_params', user_id=tg_id))
        return
    
    if amount <= 0 or count <= 0:
        await update.message.reply_text(t('send_command_amount_count_positive', user_id=tg_id))
        return
    
    if count > 100:
        await update.message.reply_text("每個紅包最多100份")
        return
    
    # 檢查餘額
    with get_db() as db:
        db_user = db.query(User).filter(User.tg_id == user.id).first()
        
        if not db_user:
            await update.message.reply_text("請先使用 /start 註冊")
            return
        
        if (db_user.balance_usdt or 0) < amount:
            await update.message.reply_text(f"餘額不足，當前 USDT 餘額: {float(db_user.balance_usdt or 0):.2f}")
            return
        
        # 扣除餘額
        db_user.balance_usdt = (db_user.balance_usdt or 0) - amount
        
        # 創建紅包
        packet = RedPacket(
            uuid=str(uuid.uuid4()),
            sender_id=db_user.id,
            chat_id=chat.id,
            chat_title=chat.title,
            currency=CurrencyType.USDT,
            packet_type=RedPacketType.RANDOM,
            total_amount=amount,
            total_count=count,
            message=message,
            expires_at=datetime.utcnow() + timedelta(hours=24),
        )
        db.add(packet)
        db.commit()
        db.refresh(packet)
        
        packet_uuid = packet.uuid
    
    # 使用用戶的語言設置發送紅包消息（使用 user_id）
    from bot.utils.i18n import t
    
    user_name = user.first_name or user.username or f'用戶{user.id}'
    sent_red_packet_text = t('sent_red_packet', user_id=tg_id, name=user_name)
    amount_label = t('amount_label_short', user_id=tg_id)
    quantity_label = t('quantity_label_short', user_id=tg_id)
    shares_label = t('shares_label', user_id=tg_id)
    click_to_claim = t('click_to_claim', user_id=tg_id)
    claim_button_text = t('claim_red_packet', user_id=tg_id)
    
    text = f"""
🧧 *{sent_red_packet_text}*

{amount_label}{amount} USDT | {quantity_label}{count} {shares_label}
📝 {message}

{click_to_claim}
"""
    
    keyboard = [[InlineKeyboardButton(claim_button_text, callback_data=f"claim:{packet_uuid}")]]
    
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def claim_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理搶紅包回調"""
    query = update.callback_query
    if not query:
        logger.error("[CLAIM_CALLBACK] No callback_query in update")
        return
    
    user = query.from_user
    user_id = user.id if user else None
    callback_data = query.data if query.data else "[無數據]"
    
    # 立即記錄日誌
    logger.info(f"[CLAIM_CALLBACK] Received callback: '{callback_data}' from user {user_id}")
    
    # 立即響應回調（避免 Telegram 超時）
    try:
        await query.answer("處理中...", cache_time=0)
    except Exception as e:
        logger.error(f"[CLAIM_CALLBACK] Error answering query: {e}")
        # 繼續處理，即使 answer 失敗
    
    # 解析紅包 UUID
    try:
        packet_uuid = query.data.split(":")[1]
        logger.info(f"[CLAIM_CALLBACK] Parsed packet_uuid: {packet_uuid}")
    except (IndexError, AttributeError) as e:
        logger.error(f"[CLAIM_CALLBACK] Invalid callback data: {callback_data}, error: {e}")
        try:
            await query.answer("無效的紅包鏈接", show_alert=True)
        except:
            pass
        return
    
    # 先快速檢查是否已領取（避免重複搶包時只顯示"處理中"）
    packet_id = None
    user_id = None
    logger.info(f"[CLAIM_CALLBACK] Opening database session to check packet {packet_uuid}")
    with get_db() as db:
        # 查找紅包
        packet = db.query(RedPacket).filter(RedPacket.uuid == packet_uuid).first()
        
        if not packet:
            logger.error(f"[CLAIM_CALLBACK] Packet not found: {packet_uuid}")
            try:
                await query.answer("紅包不存在", show_alert=True)
            except:
                pass
            return
        
        logger.info(f"[CLAIM_CALLBACK] Packet found: id={packet.id}, status={packet.status}, amount={packet.total_amount}, count={packet.total_count}")
        
        # 在會話內保存 ID（避免 DetachedInstanceError）
        packet_id = packet.id
        packet_status_check = packet.status
        packet_expires_at = packet.expires_at
        packet_currency = packet.currency
        
        if packet_status_check != RedPacketStatus.ACTIVE:
            logger.warning(f"[CLAIM_CALLBACK] Packet is not active: status={packet_status_check}")
            try:
                await query.answer("紅包已被搶完或已過期", show_alert=True)
            except:
                pass
            return
        
        if packet_expires_at and packet_expires_at < datetime.utcnow():
            logger.warning(f"[CLAIM_CALLBACK] Packet expired: expires_at={packet_expires_at}")
            packet.status = RedPacketStatus.EXPIRED
            db.commit()
            try:
                await query.answer("紅包已過期", show_alert=True)
            except:
                pass
            return
        
        # 查找用戶
        logger.info(f"[CLAIM_CALLBACK] Looking up user: tg_id={user.id}")
        db_user = db.query(User).filter(User.tg_id == user.id).first()
        if not db_user:
            logger.info(f"[CLAIM_CALLBACK] User not found, creating new user: tg_id={user.id}, username={user.username}")
            db_user = User(tg_id=user.id, username=user.username, first_name=user.first_name)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        else:
            logger.info(f"[CLAIM_CALLBACK] User found: id={db_user.id}, tg_id={db_user.tg_id}")
        
        # 在會話內保存 user_id
        user_id = db_user.id
        
        # 檢查是否已領取（在顯示"處理中"之前檢查）
        existing = db.query(RedPacketClaim).filter(
            RedPacketClaim.red_packet_id == packet_id,
            RedPacketClaim.user_id == user_id
        ).first()
        
        if existing:
            # 獲取貨幣符號
            currency_symbol_map = {
                CurrencyType.USDT: "USDT",
                CurrencyType.TON: "TON",
                CurrencyType.STARS: "Stars",
                CurrencyType.POINTS: "Points",
            }
            currency_symbol = currency_symbol_map.get(packet_currency, "USDT")
            await query.answer(f"你已經領過了！獲得 {float(existing.amount):.2f} {currency_symbol}", show_alert=True)
            return
    
    # 如果未領取，現在顯示"處理中"並繼續處理
    await query.answer("處理中...", cache_time=0)
    
    # 重新打開數據庫會話進行實際的搶包操作
    with get_db() as db:
        # 重新查詢 packet 和 db_user（避免 DetachedInstanceError）
        packet = db.query(RedPacket).filter(RedPacket.id == packet_id).first()
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not packet or not db_user:
            await query.answer("數據錯誤，請重試", show_alert=True)
            return
        
        # 再次檢查是否已領取（防止並發搶包）
        existing = db.query(RedPacketClaim).filter(
            RedPacketClaim.red_packet_id == packet.id,
            RedPacketClaim.user_id == db_user.id
        ).first()
        
        if existing:
            currency_symbol_map = {
                CurrencyType.USDT: "USDT",
                CurrencyType.TON: "TON",
                CurrencyType.STARS: "Stars",
                CurrencyType.POINTS: "Points",
            }
            currency_symbol = currency_symbol_map.get(packet.currency, "USDT")
            await query.answer(f"你已經領過了！獲得 {float(existing.amount):.2f} {currency_symbol}", show_alert=True)
            return
        
        # 計算金額
        remaining_amount = packet.total_amount - packet.claimed_amount
        remaining_count = packet.total_count - packet.claimed_count
        
        if remaining_count <= 0:
            packet.status = RedPacketStatus.COMPLETED
            db.commit()
            await query.answer("紅包已被搶完", show_alert=True)
            return
        
        # 根據紅包類型計算金額（保留兩位小數）
        if packet.packet_type == RedPacketType.EQUAL:  # 紅包炸彈（需要隨機金額以便檢測炸彈）
            # 炸彈紅包也需要隨機金額，但總和必須等於總金額
            # 最後一個包直接取剩餘金額，其他包隨機分配
            if remaining_count == 1:
                # 最後一份直接取剩餘金額，確保至少 0.01
                claim_amount = max(remaining_amount, Decimal("0.01"))
                claim_amount = round(claim_amount, 2)  # 保留兩位小數
                # 如果四捨五入後為 0，確保至少 0.01
                if claim_amount <= 0:
                    claim_amount = Decimal("0.01")
            else:
                # 計算平均金額
                avg_amount = remaining_amount / Decimal(str(remaining_count))
                # 隨機範圍：平均金額的 50% 到 150%
                min_amount = avg_amount * Decimal("0.5")
                max_amount = avg_amount * Decimal("1.5")
                # 確保不會超過剩餘金額，且為其他包留出至少 0.01
                max_amount = min(max_amount, remaining_amount - Decimal("0.01") * (remaining_count - 1))
                # 確保 max_amount 至少等於 min_amount
                if max_amount < min_amount:
                    max_amount = min_amount
                # 生成隨機金額
                claim_amount = Decimal(str(random.uniform(float(min_amount), float(max_amount))))
                # 確保至少 0.01
                claim_amount = max(claim_amount, Decimal("0.01"))
                # 確保不超過剩餘金額
                claim_amount = min(claim_amount, remaining_amount - Decimal("0.01") * (remaining_count - 1))
                claim_amount = round(claim_amount, 2)  # 保留兩位小數
        else:  # 手氣最佳（隨機金額）
            if remaining_count == 1:
                # 最後一份直接取剩餘金額，確保至少 0.01
                claim_amount = max(remaining_amount, Decimal("0.01"))
                claim_amount = round(claim_amount, 2)  # 保留兩位小數
                # 如果四捨五入後為 0，確保至少 0.01
                if claim_amount <= 0:
                    claim_amount = Decimal("0.01")
            else:
                max_amount = remaining_amount * Decimal("0.9") / remaining_count * 2
                claim_amount = Decimal(str(random.uniform(0.01, float(max_amount))))  # 最小 0.01
                claim_amount = min(claim_amount, remaining_amount - Decimal("0.01") * (remaining_count - 1))
                claim_amount = round(claim_amount, 2)  # 保留兩位小數
        
        # 獲取貨幣符號映射（提前定義，用於錯誤提示）
        currency_symbol_map = {
            CurrencyType.USDT: "USDT",
            CurrencyType.TON: "TON",
            CurrencyType.STARS: "Stars",
            CurrencyType.POINTS: "Points",
        }
        
        # 檢查是否踩雷（僅紅包炸彈）
        is_bomb = False
        penalty_amount = None
        if packet.packet_type == RedPacketType.EQUAL and packet.bomb_number is not None:
            # 獲取金額的最後一位小數（兩位小數）
            amount_str = f"{float(claim_amount):.2f}"
            # 找到最後一個數字（小數點後第二位）
            last_digit = None
            if '.' in amount_str:
                decimal_part = amount_str.split('.')[1]
                if len(decimal_part) >= 2:
                    last_digit = int(decimal_part[1])  # 小數點後第二位
                elif len(decimal_part) == 1:
                    last_digit = int(decimal_part[0])  # 小數點後第一位
            else:
                # 如果沒有小數點，取個位數
                last_digit = int(amount_str[-1])
            
            # 如果最後一位數字等於炸彈數字，則踩雷
            if last_digit == packet.bomb_number:
                is_bomb = True
                
                # 計算賠付金額
                # 單雷（10個包）：賠付全額
                # 雙雷（5個包）：賠付雙倍
                if packet.total_count == 10:  # 單雷
                    penalty_amount = packet.total_amount
                else:  # 雙雷（5個包）
                    penalty_amount = packet.total_amount * Decimal("2")
                
                # 檢查用戶餘額是否足夠賠付
                currency_field_map = {
                    CurrencyType.USDT: "balance_usdt",
                    CurrencyType.TON: "balance_ton",
                    CurrencyType.STARS: "balance_stars",
                    CurrencyType.POINTS: "balance_points",
                }
                balance_field = currency_field_map.get(packet.currency, "balance_usdt")
                current_balance = getattr(db_user, balance_field, 0) or Decimal(0)
                
                if current_balance < penalty_amount:
                    currency_symbol = currency_symbol_map.get(packet.currency, "USDT")
                    await query.answer(
                        f"⚠️ 餘額不足！需要 {float(penalty_amount):.2f} {currency_symbol} 才能參與搶紅包（可能踩雷需賠付）",
                        show_alert=True
                    )
                    return
        
        # 創建領取記錄
        claim = RedPacketClaim(
            red_packet_id=packet.id,
            user_id=db_user.id,
            amount=claim_amount,
            is_bomb=is_bomb,
            penalty_amount=penalty_amount if is_bomb else None,
        )
        db.add(claim)
        
        # 更新紅包
        packet.claimed_amount += claim_amount
        packet.claimed_count += 1
        
        # 標記最佳手氣（僅手氣最佳類型，當紅包搶完時）
        is_luckiest = False
        if packet.packet_type == RedPacketType.RANDOM and packet.claimed_count >= packet.total_count:
            # 查找所有搶包記錄（包括剛創建的），找出金額最大的
            all_existing_claims = db.query(RedPacketClaim).filter(
                RedPacketClaim.red_packet_id == packet.id
            ).all()
            
            # 找到金額最大的記錄
            max_amount = Decimal(0)
            luckiest_claim_id = None
            for existing_claim in all_existing_claims:
                if existing_claim.amount > max_amount:
                    max_amount = existing_claim.amount
                    luckiest_claim_id = existing_claim.id
            
            # 標記最佳手氣（清除之前的標記，設置新的）
            if luckiest_claim_id:
                # 清除所有記錄的最佳手氣標記
                for existing_claim in all_existing_claims:
                    existing_claim.is_luckiest = False
                # 設置新的最佳手氣
                luckiest_claim = db.query(RedPacketClaim).filter(RedPacketClaim.id == luckiest_claim_id).first()
                if luckiest_claim:
                    luckiest_claim.is_luckiest = True
                    # 如果當前用戶是最佳手氣
                    if luckiest_claim.id == claim.id:
                        is_luckiest = True
        
        # 保存是否剛完成（用於發送提醒消息）
        just_completed = False
        if packet.claimed_count >= packet.total_count:
            if packet.status != RedPacketStatus.COMPLETED:
                just_completed = True
            packet.status = RedPacketStatus.COMPLETED
            packet.completed_at = datetime.utcnow()
        
        # 保存 is_luckiest 到變量（在會話內）
        is_luckiest_value = is_luckiest
        
        # 保存是否剛完成和最佳手氣用戶信息（用於發送提醒消息）
        just_completed_value = just_completed
        luckiest_user_tg_id = None
        luckiest_user_name = None
        if just_completed_value:
            if packet.packet_type == RedPacketType.RANDOM:
                # 手氣最佳：找到最佳手氣用戶
                luckiest_claim = db.query(RedPacketClaim).filter(
                    RedPacketClaim.red_packet_id == packet.id,
                    RedPacketClaim.is_luckiest == True
                ).first()
                if luckiest_claim:
                    luckiest_user = db.query(User).filter(User.id == luckiest_claim.user_id).first()
                    if luckiest_user:
                        luckiest_user_tg_id = luckiest_user.tg_id
                        luckiest_user_name = luckiest_user.first_name or '用戶'
            elif packet.packet_type == RedPacketType.EQUAL:
                # 炸彈紅包：找到贏最多的人（金額最大的，排除踩雷的）
                all_claims_for_winner = db.query(RedPacketClaim).filter(
                    RedPacketClaim.red_packet_id == packet.id
                ).all()
                max_net_amount = Decimal("-999999")
                winner_user_id = None
                for claim_record in all_claims_for_winner:
                    net_amount = claim_record.amount
                    if claim_record.is_bomb and claim_record.penalty_amount:
                        net_amount = net_amount - claim_record.penalty_amount
                    if net_amount > max_net_amount:
                        max_net_amount = net_amount
                        winner_user_id = claim_record.user_id
                if winner_user_id:
                    winner_user = db.query(User).filter(User.id == winner_user_id).first()
                    if winner_user:
                        luckiest_user_tg_id = winner_user.tg_id
                        luckiest_user_name = winner_user.first_name or '用戶'
        
        # 更新用戶餘額（根據貨幣類型）
        currency_field_map = {
            CurrencyType.USDT: "balance_usdt",
            CurrencyType.TON: "balance_ton",
            CurrencyType.STARS: "balance_stars",
            CurrencyType.POINTS: "balance_points",
        }
        balance_field = currency_field_map.get(packet.currency, "balance_usdt")
        current_balance = getattr(db_user, balance_field, 0) or Decimal(0)
        
        if is_bomb:
            # 踩雷：扣除賠付金額（金額退回紅包池，用戶需要賠付）
            # 用戶獲得 claim_amount，但需要賠付 penalty_amount
            # 實際餘額變化：claim_amount - penalty_amount（通常是負數）
            net_change = claim_amount - penalty_amount
            setattr(db_user, balance_field, current_balance + net_change)
            
            # 發送者獲得賠付金額
            sender = db.query(User).filter(User.id == packet.sender_id).first()
            if sender:
                sender_balance = getattr(sender, balance_field, 0) or Decimal(0)
                setattr(sender, balance_field, sender_balance + penalty_amount)
        else:
            # 正常領取：增加餘額
            setattr(db_user, balance_field, current_balance + claim_amount)
        
        db.commit()
        
        # 獲取發送者信息
        sender = db.query(User).filter(User.id == packet.sender_id).first()
        sender_name = sender.first_name if sender else "Unknown"
        
        # 在數據庫會話內讀取所有需要的屬性值
        packet_id = packet.id  # 保存 packet.id，避免 DetachedInstanceError
        total_amount = float(packet.total_amount)
        claimed_count = packet.claimed_count
        total_count = packet.total_count
        packet_message = packet.message
        packet_status = packet.status
        packet_uuid = packet.uuid
        packet_currency = packet.currency
        packet_bomb_number = packet.bomb_number
        packet_type = packet.packet_type
        
        # 獲取貨幣符號
        currency_symbol_map = {
            CurrencyType.USDT: "USDT",
            CurrencyType.TON: "TON",
            CurrencyType.STARS: "Stars",
            CurrencyType.POINTS: "Points",
        }
        currency_symbol = currency_symbol_map.get(packet_currency, "USDT")
        
        # 檢查是否踩雷（從 claim 記錄中讀取）
        is_bomb_value = claim.is_bomb if hasattr(claim, 'is_bomb') else False
        penalty_amount_value = claim.penalty_amount if hasattr(claim, 'penalty_amount') and claim.penalty_amount else None
        
        # 保存 is_luckiest（在會話內讀取）
        is_luckiest_value = is_luckiest
        
        # 獲取所有已搶紅包的記錄（在同一個會話中查詢，避免 DetachedInstanceError）
        all_claims = db.query(RedPacketClaim).filter(
            RedPacketClaim.red_packet_id == packet_id
        ).order_by(RedPacketClaim.claimed_at.asc()).all()
        
        # 獲取所有搶包用戶的信息（在數據庫會話內讀取所有屬性）
        claimers_info = []
        for claim_record in all_claims:
            # 在會話內讀取所有需要的屬性值
            claim_user_id = claim_record.user_id
            claim_amount = float(claim_record.amount)
            claim_is_bomb = claim_record.is_bomb if hasattr(claim_record, 'is_bomb') else False
            claim_penalty = float(claim_record.penalty_amount) if hasattr(claim_record, 'penalty_amount') and claim_record.penalty_amount else None
            claim_is_luckiest = claim_record.is_luckiest if hasattr(claim_record, 'is_luckiest') else False
            
            # 查詢用戶信息
            claimer_user = db.query(User).filter(User.id == claim_user_id).first()
            if claimer_user:
                claimer_name = claimer_user.first_name or '用戶'
                claimers_info.append({
                    'name': claimer_name,
                    'amount': claim_amount,
                    'is_bomb': claim_is_bomb,
                    'penalty': claim_penalty,
                    'is_luckiest': claim_is_luckiest,
                })
        
        # 按金額排序（用於排行榜顯示）
        claimers_info_sorted = sorted(claimers_info, key=lambda x: x['amount'], reverse=True)
    
    # 獲取發送者的語言設置以顯示正確的提示
    from bot.utils.i18n import t
    with get_db() as db:
        sender_user = db.query(User).filter(User.id == packet.sender_id).first()
        if sender_user:
            double_thunder = t('double_thunder_text', user=sender_user)
            single_thunder = t('single_thunder_text', user=sender_user)
            claim_bomb_alert_template = t('claim_bomb_alert', user=sender_user)
            claim_success_luckiest_template = t('claim_success_luckiest', user=sender_user)
            claim_success_template = t('claim_success', user=sender_user)
            processing_complete = t('send_command_processing', user=sender_user)
        else:
            double_thunder = "雙雷"
            single_thunder = "單雷"
            claim_bomb_alert_template = "💣 踩雷了！需要賠付 {penalty:.2f} {currency}（{thunder_type}）"
            claim_success_luckiest_template = "🎉 恭喜獲得 {amount:.2f} {currency}！\n🏆 你是最佳手氣！"
            claim_success_template = "🎉 恭喜獲得 {amount:.2f} {currency}！"
            processing_complete = "處理完成"
    
    # 根據是否踩雷和是否最佳手氣顯示不同的提示
    if is_bomb_value and penalty_amount_value:
        thunder_type = single_thunder if total_count == 10 else double_thunder
        alert_text = claim_bomb_alert_template.format(
            penalty=float(penalty_amount_value),
            currency=currency_symbol,
            thunder_type=thunder_type
        )
    elif is_luckiest_value and packet_status == RedPacketStatus.COMPLETED:
        alert_text = claim_success_luckiest_template.format(
            amount=float(claim_amount),
            currency=currency_symbol
        )
    else:
        alert_text = claim_success_template.format(
            amount=float(claim_amount),
            currency=currency_symbol
        )
    
    # 確保彈窗提示始終顯示（無論什麼情況）
    try:
        await query.answer(alert_text, show_alert=True)
    except Exception as e:
        logger.error(f"Failed to show alert: {e}")
        # 如果彈窗失敗，至少嘗試簡單的 answer
        try:
            await query.answer(processing_complete, show_alert=False)
        except:
            pass
    
    # 使用發送者的語言設置更新消息
    from bot.utils.i18n import t
    # 在會話內重新查詢發送者以獲取語言設置
    with get_db() as db:
        sender_user = db.query(User).filter(User.id == packet.sender_id).first()
        if sender_user:
            # 獲取翻譯文本
            sent_red_packet_text = t('sent_red_packet', user=sender_user, name=sender_name)
            amount_label = t('amount_label_short', user=sender_user)
            quantity_label = t('quantity_label_short', user=sender_user)
            shares_label = t('shares_label', user=sender_user)
            claimed_red_packet = t('claimed_red_packet', user=sender_user)
            user_claimed = t('user_claimed', user=sender_user)
            user_claimed_with_amount = t('user_claimed_with_amount', user=sender_user)
            user_claimed_bomb = t('user_claimed_bomb', user=sender_user)
            red_packet_completed = t('red_packet_completed', user=sender_user)
            red_packet_leaderboard = t('red_packet_leaderboard', user=sender_user)
            best_luck = t('best_luck', user=sender_user)
            best_luck_marker = t('best_luck_marker', user=sender_user)
            bomb_number_display = t('bomb_number_display', user=sender_user)
            claim_red_packet_remaining = t('claim_red_packet_remaining', user=sender_user)
            double_thunder_text = t('double_thunder_text', user=sender_user)
            single_thunder_text = t('single_thunder_text', user=sender_user)
        else:
            # 如果查詢失敗，使用默認值（中文）
            sent_red_packet_text = f"{sender_name} 發了一個紅包"
            amount_label = "💰 金額："
            quantity_label = "👥 數量："
            shares_label = "份"
            claimed_red_packet = "已搶包："
            user_claimed = "{name} 搶到了紅包"
            user_claimed_with_amount = "{name} 搶到了 {amount:.2f} {currency}！"
            user_claimed_bomb = "{name} 搶到了 {amount:.2f} {currency}，💣 踩雷了！需賠付 {penalty:.2f} {currency}"
            red_packet_completed = "✅ 紅包已搶完"
            red_packet_leaderboard = "📊 搶包排行榜："
            best_luck = "🏆 {name} 是本次最佳手氣！"
            best_luck_marker = "🏆 {name} (最佳手氣)"
            bomb_number_display = "💣 炸彈數字: {number} | {thunder_type}"
            claim_red_packet_remaining = "🧧 搶紅包 ({remaining} 份剩餘)"
            double_thunder_text = "雙雷"
            single_thunder_text = "單雷"
    
    # 更新消息（使用已保存的變量，而不是數據庫對象）
    text = f"""
🧧 *{sent_red_packet_text}*

{amount_label}{total_amount:.2f} {currency_symbol} | {quantity_label}{claimed_count}/{total_count} {shares_label}
"""
    
    # 如果是紅包炸彈，顯示炸彈信息
    if packet_type == RedPacketType.EQUAL and packet_bomb_number is not None:
        thunder_type = single_thunder_text if total_count == 10 else double_thunder_text
        text += bomb_number_display.format(number=packet_bomb_number, thunder_type=thunder_type) + "\n"
    
    text += f"📝 {packet_message}\n\n"
    
    # 根據紅包是否完成，顯示不同的信息
    if packet_status == RedPacketStatus.COMPLETED:
        # 紅包已搶完：顯示完整的排行榜和金額
        if claimers_info_sorted:
            text += f"{red_packet_leaderboard}\n"
            for idx, claimer in enumerate(claimers_info_sorted, 1):
                # 構建顯示文本
                rank_icon = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
                name_text = claimer['name']
                
                # 添加最佳手氣標記（僅手氣最佳類型）
                if claimer['is_luckiest'] and packet_type == RedPacketType.RANDOM:
                    name_text = best_luck_marker.format(name=name_text)
                
                # 添加踩雷標記
                if claimer['is_bomb'] and claimer['penalty']:
                    text += f"{rank_icon} {user_claimed_bomb.format(name=name_text, amount=claimer['amount'], currency=currency_symbol, penalty=claimer['penalty'])}\n"
                else:
                    text += f"{rank_icon} {user_claimed_with_amount.format(name=name_text, amount=claimer['amount'], currency=currency_symbol)}\n"
            text += "\n"
            
            # 如果紅包已搶完且是手氣最佳類型，顯示最佳手氣提示
            if packet_type == RedPacketType.RANDOM:
                luckiest_claimer = next((c for c in claimers_info_sorted if c['is_luckiest']), None)
                if luckiest_claimer:
                    text += f"{best_luck.format(name=luckiest_claimer['name'])}\n"
        
        text += red_packet_completed
        keyboard = []
    else:
        # 紅包未完成：只顯示誰搶到了紅包，不顯示金額
        if claimers_info_sorted:
            text += f"{claimed_red_packet}\n"
            for claimer in claimers_info_sorted:
                # 只顯示名字，不顯示金額
                text += f"🧧 {user_claimed.format(name=claimer['name'])}\n"
            text += "\n"
        
        remaining = total_count - claimed_count
        keyboard = [[InlineKeyboardButton(claim_red_packet_remaining.format(remaining=remaining), callback_data=f"claim:{packet_uuid}")]]
    
    # 更新群組消息
    try:
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
        )
        logger.info(f"Red packet message updated successfully for packet {packet_uuid}, claimed: {claimed_count}/{total_count}")
    except Exception as e:
        logger.error(f"Failed to edit message: {e}")
        # 如果編輯失敗，至少確保用戶收到了提示
        # 嘗試發送新消息作為備用
        try:
            if query.message and query.message.chat:
                await query.message.reply_text(
                    f"🎉 {user.first_name} 搶到了 {float(claim_amount):.2f} {currency_symbol}！",
                    parse_mode="Markdown"
                )
        except Exception as e2:
            logger.error(f"Failed to send backup message: {e2}")
    
    # 如果紅包剛完成，發送提醒消息給下一個發送者
    if just_completed_value and luckiest_user_tg_id and query.message and query.message.chat:
        try:
            bot = Bot(token=settings.BOT_TOKEN)
            
            # 構建提醒消息
            reminder_text = ""
            if packet_type == RedPacketType.RANDOM:
                # 手氣最佳提醒
                reminder_text = f"""🎉 *恭喜 {luckiest_user_name} 成為最佳手氣！*

📢 *請發送下一個紅包*
💰 金額：{total_amount:.2f} {currency_symbol}
👥 數量：{total_count} 份
🎮 類型：手氣最佳
📝 祝福語：{packet_message}

💡 提示：您可以使用 miniapp 或 /send 命令發送紅包"""
            elif packet_type == RedPacketType.EQUAL and packet_bomb_number is not None:
                # 炸彈紅包提醒
                thunder_type = "單雷" if total_count == 10 else "雙雷"
                reminder_text = f"""💣 *恭喜 {luckiest_user_name} 贏得最多！*

📢 *請發送下一個紅包炸彈*
💰 金額：{total_amount:.2f} {currency_symbol}
👥 數量：{total_count} 份（{thunder_type}）
💣 炸彈數字：{packet_bomb_number}
📝 祝福語：{packet_message}

💡 提示：您可以使用 miniapp 或 /send 命令發送紅包"""
            
            if reminder_text:
                await bot.send_message(
                    chat_id=query.message.chat.id,
                    text=reminder_text,
                    parse_mode="Markdown",
                    reply_to_message_id=query.message.message_id
                )
                logger.info(f"Reminder message sent to {luckiest_user_name} (tg_id: {luckiest_user_tg_id}) for next red packet")
        except Exception as e:
            logger.error(f"Failed to send reminder message: {e}")

