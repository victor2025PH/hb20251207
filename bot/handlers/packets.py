"""
Lucky Red - 紅包處理器（擴展版）
處理紅包相關的所有功能
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from loguru import logger
from decimal import Decimal
from datetime import datetime, timedelta
import re

from shared.config.settings import get_settings
from shared.database.connection import get_db
from shared.database.models import User, RedPacket, RedPacketClaim, CurrencyType, RedPacketType, RedPacketStatus
from bot.keyboards import get_packets_menu, get_back_to_main
from bot.constants import PacketConstants
from bot.utils.packet_helpers import extract_packet_data, format_packet_info, get_packet_type_text

settings = get_settings()


async def packets_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理紅包菜單回調"""
    from bot.utils.user_helpers import get_user_from_update
    
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    
    # 獲取用戶（帶緩存）
    db_user = await get_user_from_update(update, context)
    if not db_user:
        await query.message.reply_text("請先使用 /start 註冊")
        return
    
    if action == "list":
        await show_packets_list(query, db_user)
    elif action == "send":
        await show_send_packet_guide(query, db_user)
    elif action == "send_menu":
        await send_packet_menu_callback(update, context)
    elif action == "my":
        await show_my_packets(query, db_user)


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理用戶文本輸入（金額、數量、群組 ID/鏈接或祝福語）"""
    from bot.utils.user_helpers import get_user_from_update
    from bot.keyboards.reply_keyboards import (
        get_send_packet_amount_keyboard,
        get_send_packet_count_keyboard,
        get_send_packet_group_keyboard,
        get_packets_reply_keyboard,
    )
    from telegram import ReplyKeyboardMarkup, KeyboardButton
    
    text = update.message.text.strip()
    
    # 獲取用戶（帶緩存）
    db_user = await get_user_from_update(update, context)
    if not db_user:
        return
    
    # 檢查發紅包流程步驟
    step = context.user_data.get('send_packet_step')
    packet_data = context.user_data.get('send_packet', {})
    
    # 處理自定義金額輸入
    if step == 'amount_input':
        try:
            amount = float(text)
            if amount <= 0:
                await update.message.reply_text("金額必須大於0，請重新輸入：")
                return
            
            packet_data['amount'] = amount
            context.user_data['send_packet'] = packet_data
            context.user_data['send_packet_step'] = 'count'
            
            currency = packet_data.get('currency', 'usdt')
            packet_type = packet_data.get('packet_type', 'random')
            
            from bot.handlers.packets import show_count_input
            query = type('Query', (), {
                'edit_message_text': lambda self, *args, **kwargs: update.message.reply_text(*args, **kwargs),
                'message': update.message
            })()
            await show_count_input(query, db_user, context)
            await update.message.reply_text(
                "選擇或輸入數量：",
                reply_markup=get_send_packet_count_keyboard(currency, packet_type, str(amount)),
            )
            return
        except ValueError:
            await update.message.reply_text("請輸入有效的數字，例如：100")
            return
    
    # 處理自定義數量輸入
    elif step == 'count_input':
        try:
            count = int(text)
            if count <= 0:
                await update.message.reply_text("數量必須大於0，請重新輸入：")
                return
            if count > PacketConstants.MAX_COUNT:
                await update.message.reply_text(f"數量不能超過 {PacketConstants.MAX_COUNT}，請重新輸入：")
                return
            
            packet_data['count'] = count
            context.user_data['send_packet'] = packet_data
            context.user_data['send_packet_step'] = 'group'
            
            # 如果是紅包炸彈，需要設置炸彈數字
            if packet_data.get('packet_type') == 'equal':
                if count == 5:
                    packet_data['bomb_number'] = None  # 雙雷
                elif count == 10:
                    packet_data['bomb_number'] = None  # 單雷
                else:
                    await update.message.reply_text("紅包炸彈只能選擇 5 份（雙雷）或 10 份（單雷），請重新輸入：")
                    return
                context.user_data['send_packet'] = packet_data
            
            from bot.handlers.packets import show_group_selection
            query = type('Query', (), {
                'edit_message_text': lambda self, *args, **kwargs: update.message.reply_text(*args, **kwargs),
                'message': update.message
            })()
            await show_group_selection(query, db_user, context)
            await update.message.reply_text(
                "輸入群組 ID 或鏈接：",
                reply_markup=get_send_packet_group_keyboard(),
            )
            return
        except ValueError:
            await update.message.reply_text("請輸入有效的數字，例如：20")
            return
    
    # 處理群組 ID 輸入
    elif step == 'group_input' or context.user_data.get('waiting_for_group'):
        context.user_data['waiting_for_group'] = True
        await handle_group_input(update, db_user, text, context)
        return
    
    # 處理祝福語輸入
    elif context.user_data.get('waiting_for_message'):
        await handle_message_input(update, db_user, text, context)
        return


async def handle_group_input(update, db_user, text, context):
    """處理群組 ID/鏈接輸入"""
    from bot.utils.security import validate_chat_id
    import re
    
    packet_data = context.user_data.get('send_packet', {})
    
    # 嘗試解析群組 ID 或鏈接
    chat_id = validate_chat_id(text)
    
    # 方式二：是群組鏈接
    if chat_id is None:
        # 匹配 t.me/xxx 或 @xxx
        match = re.search(r'(?:t\.me/|@)([a-zA-Z0-9_]+)', text)
        if match:
            username = match.group(1)
            try:
                from telegram import Bot
                bot = Bot(token=settings.BOT_TOKEN)
                chat = await bot.get_chat(f"@{username}")
                chat_id = chat.id
            except Exception as e:
                logger.error(f"Error getting chat from username: {e}", exc_info=True)
                await update.message.reply_text(
                    f"無法獲取群組信息：{str(e)}\n\n請確保：\n1. 群組鏈接正確\n2. Bot 在群組中\n3. 群組有公開 username",
                    parse_mode="Markdown"
                )
                return
    
    if chat_id:
        packet_data['chat_id'] = chat_id
        context.user_data['send_packet'] = packet_data
        context.user_data.pop('waiting_for_group', None)
        context.user_data['send_packet_step'] = 'confirm'
        
        # 顯示確認界面
        from bot.keyboards.reply_keyboards import get_send_packet_confirm_keyboard
        currency = packet_data.get('currency', 'usdt')
        packet_type = packet_data.get('packet_type', 'random')
        amount = packet_data.get('amount', 0)
        count = packet_data.get('count', 1)
        message = packet_data.get('message', PacketConstants.DEFAULT_MESSAGE)
        
        text = f"""
✅ *確認發送紅包*

*紅包信息：*
• 幣種：{currency.upper()}
• 類型：{"手氣最佳" if packet_type == "random" else "紅包炸彈"}
• 金額：{amount} {currency.upper()}
• 數量：{count} 份
• 祝福語：{message}
• 群組 ID：{chat_id}

請確認是否發送：
"""
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_send_packet_confirm_keyboard(),
        )
    else:
        await update.message.reply_text(
            "無法識別群組 ID 或鏈接。\n\n請輸入：\n• 群組 ID（數字，例如：-1001234567890）\n• 群組鏈接（例如：https://t.me/groupname 或 @groupname）",
            parse_mode="Markdown"
        )


async def handle_message_input(update, db_user, text, context):
    """處理祝福語輸入"""
    from bot.utils.security import sanitize_message
    
    packet_data = context.user_data.get('send_packet', {})
    packet_data['message'] = sanitize_message(text)  # 使用安全清理
    context.user_data['send_packet'] = packet_data
    context.user_data.pop('waiting_for_message', None)
    
    # 進入群組選擇
    await show_group_selection_from_message(update, db_user, context)


async def show_group_selection_from_message(update, db_user, context):
    """從消息中顯示群組選擇"""
    packet_data = context.user_data.get('send_packet', {})
    
    # 在會話內獲取用戶發過紅包的群組
    with get_db() as db:
        from shared.database.models import User
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await update.message.reply_text("發生錯誤，請稍後再試")
            return
        
        packets = db.query(RedPacket).filter(
            RedPacket.sender_id == user.id
        ).order_by(RedPacket.created_at.desc()).limit(10).all()
    
    text = f"""
➕ *發紅包 - 選擇群組*

*紅包信息：*
• 幣種：{packet_data.get('currency', 'usdt').upper()}
• 類型：{"手氣最佳" if packet_data.get('packet_type') == "random" else "紅包炸彈"}
• 金額：{packet_data.get('amount')} {packet_data.get('currency', 'usdt').upper()}
• 數量：{packet_data.get('count')} 份
• 祝福語：{packet_data.get('message', PacketConstants.DEFAULT_MESSAGE)}

請選擇群組：
"""
    
    keyboard = []
    
    # 添加已發過紅包的群組
    seen_chats = set()
    for packet in packets[:5]:
        if packet.chat_id and packet.chat_id not in seen_chats:
            seen_chats.add(packet.chat_id)
            chat_title = packet.chat_title or f"群組 {packet.chat_id}"
            keyboard.append([
                InlineKeyboardButton(
                    f"📱 {chat_title[:20]}",
                    callback_data=f"packets:send:confirm:{packet_data['currency']}:{packet_data['packet_type']}:{packet_data['amount']}:{packet_data['count']}:{packet_data.get('bomb_number', '')}:{packet_data.get('message', 'default')}:{packet.chat_id}"
                ),
            ])
    
    keyboard.append([
        InlineKeyboardButton("📝 輸入群組鏈接/ID", callback_data=f"packets:send:group_input:{packet_data['currency']}:{packet_data['packet_type']}:{packet_data['amount']}:{packet_data['count']}:{packet_data.get('bomb_number', '')}:{packet_data.get('message', 'default')}"),
    ])
    
    keyboard.append([
        InlineKeyboardButton("◀️ 返回", callback_data="menu:packets"),
    ])
    
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def confirm_and_send_from_message(update, db_user, context):
    """從消息確認並發送紅包"""
    packet_data = context.user_data.get('send_packet', {})
    
    currency = packet_data.get('currency', 'usdt')
    packet_type = packet_data.get('packet_type', 'random')
    amount = Decimal(str(packet_data.get('amount', 0)))
    count = int(packet_data.get('count', 1))
    bomb_number = packet_data.get('bomb_number')
    message = packet_data.get('message', PacketConstants.DEFAULT_MESSAGE)
    chat_id = packet_data.get('chat_id')
    
    if not chat_id:
        await update.message.reply_text("請選擇或輸入群組")
        return
    
    # 驗證參數
    if amount <= 0 or count <= 0:
        await update.message.reply_text("金額和數量必須大於0")
        return
    
    if count > PacketConstants.MAX_COUNT:
        await update.message.reply_text(f"每個紅包最多{PacketConstants.MAX_COUNT}份")
        return
    
    # 在會話內檢查餘額
    with get_db() as db:
        from shared.database.models import User
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await update.message.reply_text("發生錯誤，請稍後再試")
            return
        
        balance = getattr(user, f"balance_{currency}", 0) or Decimal(0)
    if balance < amount:
        await update.message.reply_text(f"餘額不足，當前餘額: {float(balance):.2f}")
        return
    
    # 創建紅包
    try:
        from bot.utils.api_client import get_api_client
        from bot.utils.security import sanitize_message
        
        # 清理消息
        message = sanitize_message(message)
        
        # 使用統一的 API 客戶端
        api_client = get_api_client()
        result = await api_client.post(
            "/redpackets/create",
            data={
                "currency": currency,
                "packet_type": packet_type,
                "total_amount": float(amount),
                "total_count": count,
                "message": message,
                "chat_id": chat_id,
                "bomb_number": bomb_number,
            },
            tg_id=db_user.tg_id
        )
        
        await update.message.reply_text(
            f"✅ *紅包發送成功！*\n\n"
            f"*紅包信息：*\n"
            f"• UUID: `{result.get('uuid', '')}`\n"
            f"• 金額：{float(amount):.2f} {currency.upper()}\n"
            f"• 數量：{count} 份\n"
            f"• 祝福語：{message}\n\n"
            f"紅包已發送到群組！",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error sending packet: {e}", exc_info=True)
        error_msg = str(e)
        if "餘額不足" in error_msg or "Insufficient balance" in error_msg:
            error_msg = "餘額不足"
        elif "HTTP" in error_msg or "Request" in error_msg:
            error_msg = "網絡錯誤，請稍後再試"
        await update.message.reply_text(f"❌ 發送失敗：{error_msg}")
    
    # 清除臨時數據
    context.user_data.pop('send_packet', None)
    context.user_data.pop('waiting_for_group', None)
    context.user_data.pop('waiting_for_message', None)


async def show_packets_list(query, db_user):
    """顯示可搶的紅包列表"""
    with get_db() as db:
        # 獲取未過期且未領完的紅包
        packets = db.query(RedPacket).filter(
            RedPacket.status == RedPacketStatus.ACTIVE,
            RedPacket.expires_at > datetime.utcnow()
        ).order_by(RedPacket.created_at.desc()).limit(10).all()
    
    if not packets:
        text = """
📋 *可搶紅包*

目前沒有可搶的紅包

💡 提示：在群組中發送紅包，其他用戶就可以搶了
"""
        keyboard = [
            [
                InlineKeyboardButton("➕ 發紅包", callback_data="packets:send"),
            ],
            [
                InlineKeyboardButton("◀️ 返回", callback_data="menu:packets"),
            ],
        ]
    else:
        text = "📋 *可搶紅包列表*\n\n"
        for i, packet in enumerate(packets[:5], 1):
            claimed = packet.claimed_count or 0
            remaining = packet.total_count - claimed
            text += f"{i}. {packet.message or PacketConstants.DEFAULT_MESSAGE}\n"
            text += f"   💰 {float(packet.total_amount):.2f} {packet.currency.value.upper()}\n"
            text += f"   👥 {remaining}/{packet.total_count} 份剩餘\n\n"
        
        keyboard = [
            [
                InlineKeyboardButton("📱 查看完整列表", web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/packets")),
            ],
            [
                InlineKeyboardButton("➕ 發紅包", callback_data="packets:send"),
            ],
            [
                InlineKeyboardButton("◀️ 返回", callback_data="menu:packets"),
            ],
        ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_send_packet_guide(query, db_user):
    """顯示發紅包選項"""
    text = """
➕ *發紅包*

請選擇發送方式：

*方式一：* 在群組中使用命令
在群組中輸入：`/send <金額> <數量> [祝福語]`

*方式二：* 使用機器人菜單
選擇群組和設置參數
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📝 使用菜單發送", callback_data="packets:send_menu"),
        ],
        [
            InlineKeyboardButton("◀️ 返回", callback_data="menu:packets"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def send_packet_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理發紅包菜單回調"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    sub_action = parts[2] if len(parts) > 2 else ""
    
    # 獲取用戶（帶緩存）
    from bot.utils.user_helpers import get_user_from_update
    db_user = await get_user_from_update(update, context)
    if not db_user:
        await query.message.reply_text("請先使用 /start 註冊")
        return
    
    if action == "send_menu":
        await show_send_packet_menu(query, db_user)
    elif action == "send":
        if sub_action == "type":
            currency = parts[3] if len(parts) > 3 else "usdt"
            await show_packet_type_selection(query, db_user, currency)
        elif sub_action == "amount":
            currency = parts[3] if len(parts) > 3 else "usdt"
            packet_type = parts[4] if len(parts) > 4 else "random"
            await show_amount_input(query, db_user, currency, packet_type)
        elif sub_action == "count":
            currency = parts[3] if len(parts) > 3 else "usdt"
            packet_type = parts[4] if len(parts) > 4 else "random"
            amount = parts[5] if len(parts) > 5 else None
            context.user_data['send_packet'] = {
                'currency': currency,
                'packet_type': packet_type,
                'amount': amount,
            }
            await show_count_input(query, db_user, context)
        elif sub_action == "bomb":
            currency = parts[3] if len(parts) > 3 else "usdt"
            packet_type = parts[4] if len(parts) > 4 else "random"
            amount = parts[5] if len(parts) > 5 else None
            count = int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else None
            context.user_data['send_packet'] = {
                'currency': currency,
                'packet_type': packet_type,
                'amount': amount,
                'count': count,
            }
            await show_bomb_number_selection(query, db_user, context)
        elif sub_action == "message":
            currency = parts[3] if len(parts) > 3 else "usdt"
            packet_type = parts[4] if len(parts) > 4 else "random"
            amount = parts[5] if len(parts) > 5 else None
            count = int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else None
            bomb_number = int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else None
            context.user_data['send_packet'] = {
                'currency': currency,
                'packet_type': packet_type,
                'amount': amount,
                'count': count,
                'bomb_number': bomb_number,
            }
            await show_message_input(query, db_user, context)
        elif sub_action == "group":
            currency = parts[3] if len(parts) > 3 else "usdt"
            packet_type = parts[4] if len(parts) > 4 else "random"
            amount = parts[5] if len(parts) > 5 else None
            count = int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else None
            bomb_number = int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else None
            message = parts[8] if len(parts) > 8 and parts[8] != "default" else PacketConstants.DEFAULT_MESSAGE
            context.user_data['send_packet'] = {
                'currency': currency,
                'packet_type': packet_type,
                'amount': amount,
                'count': count,
                'bomb_number': bomb_number,
                'message': message,
            }
            await show_group_selection(query, db_user, context)
        elif sub_action == "group_input":
            currency = parts[3] if len(parts) > 3 else "usdt"
            packet_type = parts[4] if len(parts) > 4 else "random"
            amount = parts[5] if len(parts) > 5 else None
            count = int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else None
            bomb_number = int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else None
            message = parts[8] if len(parts) > 8 and parts[8] != "default" else PacketConstants.DEFAULT_MESSAGE
            context.user_data['send_packet'] = {
                'currency': currency,
                'packet_type': packet_type,
                'amount': amount,
                'count': count,
                'bomb_number': bomb_number,
                'message': message,
            }
            await show_group_link_input(query, db_user, context)
        elif sub_action == "confirm":
            chat_id = int(parts[9]) if len(parts) > 9 and parts[9].isdigit() else None
            if chat_id:
                context.user_data.setdefault('send_packet', {})['chat_id'] = chat_id
            await confirm_and_send_packet(query, db_user, context)


async def show_send_packet_menu(query, db_user):
    """顯示發紅包主菜單（用於回覆鍵盤流程）"""
    # 在會話內重新查詢用戶以確保數據最新
    with get_db() as db:
        from shared.database.models import User
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        usdt_balance = float(user.balance_usdt or 0)
        ton_balance = float(user.balance_ton or 0)
        points_balance = user.balance_points or 0
    
    text = f"""
➕ *發紅包*

*當前餘額：*
• USDT: `{usdt_balance:.4f}`
• TON: `{ton_balance:.4f}`
• 能量: `{points_balance}`

請選擇紅包幣種：
"""
    
    keyboard = [
        [
            InlineKeyboardButton("USDT", callback_data="packets:send:type:usdt"),
            InlineKeyboardButton("TON", callback_data="packets:send:type:ton"),
        ],
        [
            InlineKeyboardButton("能量", callback_data="packets:send:type:points"),
        ],
        [
            InlineKeyboardButton("◀️ 返回", callback_data="menu:packets"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_packet_type_selection(query, db_user, currency: str):
    """顯示紅包類型選擇"""
    # 在會話內重新查詢用戶以確保數據最新
    with get_db() as db:
        from shared.database.models import User
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        balance = float(getattr(user, f"balance_{currency}", 0) or 0)
    
    # 檢查餘額，如果為 0 則提醒
    if balance <= 0:
        currency_upper = currency.upper()
        currency_name = "USDT" if currency == "usdt" else "TON" if currency == "ton" else "能量"
        text = f"""
❌ *餘額不足*

您的 {currency_name} 餘額為 `{balance:.4f}`

請先充值後再發紅包！

*充值方式：*
• 點擊「💰 錢包」→「💵 充值」
• 或使用 miniapp 進行充值
"""
        keyboard = [
            [
                InlineKeyboardButton("💰 前往充值", callback_data="menu:wallet"),
            ],
            [
                InlineKeyboardButton("◀️ 返回", callback_data="menu:packets"),
            ],
        ]
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return
    
    currency_upper = currency.upper()
    text = f"""
➕ *發紅包 - {currency_upper}*

*當前餘額：* `{balance:.4f}` {currency_upper}

*選擇紅包類型：*
• 手氣最佳 - 隨機金額分配，領取完成後金額最大的用戶將被標記為"最佳手氣"
• 紅包炸彈 - 固定金額分配，如果領取金額的小數點後最後一位數字與炸彈數字相同，將觸發炸彈

請選擇類型：
"""
    
    keyboard = [
        [
            InlineKeyboardButton("🎲 手氣最佳", callback_data=f"packets:send:amount:{currency}:random"),
        ],
        [
            InlineKeyboardButton("💣 紅包炸彈", callback_data=f"packets:send:amount:{currency}:equal"),
        ],
        [
            InlineKeyboardButton("◀️ 返回", callback_data="packets:send_menu"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_amount_input(query, db_user, currency: str, packet_type: str):
    """顯示金額輸入"""
    # 在會話內重新查詢用戶以確保數據最新
    with get_db() as db:
        from shared.database.models import User
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        balance = float(getattr(user, f"balance_{currency}", 0) or 0)
    
    currency_upper = currency.upper()
    type_text = "手氣最佳" if packet_type == "random" else "紅包炸彈"
    
    text = f"""
➕ *發紅包 - {currency_upper} - {type_text}*

*當前餘額：* `{balance:.4f}` {currency_upper}

請選擇或輸入紅包總金額：
"""
    
    # 根據餘額提供快捷金額選項
    quick_amounts = []
    if balance >= 100:
        quick_amounts = [10, 50, 100]
    elif balance >= 50:
        quick_amounts = [10, 20, 50]
    elif balance >= 10:
        quick_amounts = [5, 10, 20]
    else:
        quick_amounts = [1, 5, 10] if balance >= 1 else []
    
    keyboard = []
    if quick_amounts:
        row = []
        for amt in quick_amounts:
            if amt <= balance:
                row.append(InlineKeyboardButton(str(amt), callback_data=f"packets:send:count:{currency}:{packet_type}:{amt}"))
        if row:
            keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton("📝 自定義金額", callback_data=f"packets:send:amount_custom:{currency}:{packet_type}"),
    ])
    keyboard.append([
        InlineKeyboardButton("◀️ 返回", callback_data=f"packets:send:type:{currency}"),
    ])
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_count_input(query, db_user, context):
    """顯示數量輸入"""
    packet_data = context.user_data.get('send_packet', {})
    currency = packet_data.get('currency', 'usdt')
    packet_type = packet_data.get('packet_type', 'random')
    amount = packet_data.get('amount')
    
    if not amount:
        await query.answer("請先輸入金額", show_alert=True)
        return
    
    currency_upper = currency.upper()
    type_text = "手氣最佳" if packet_type == "random" else "紅包炸彈"
    
    # 紅包炸彈只能選擇 5 或 10
    if packet_type == "equal":
        text = f"""
➕ *發紅包 - {currency_upper} - {type_text}*

*金額：* `{amount}` {currency_upper}

請選擇紅包數量：
💣 紅包炸彈只能選擇 5 份（雙雷）或 10 份（單雷）
"""
        keyboard = [
            [
                InlineKeyboardButton("5 份（雙雷）", callback_data=f"packets:send:bomb:{currency}:{packet_type}:{amount}:5"),
                InlineKeyboardButton("10 份（單雷）", callback_data=f"packets:send:bomb:{currency}:{packet_type}:{amount}:10"),
            ],
            [
                InlineKeyboardButton("◀️ 返回", callback_data=f"packets:send:amount:{currency}:{packet_type}"),
            ],
        ]
    else:
        text = f"""
➕ *發紅包 - {currency_upper} - {type_text}*

*金額：* `{amount}` {currency_upper}

請選擇紅包數量（1-100）：
"""
        keyboard = [
            [
                InlineKeyboardButton("5", callback_data=f"packets:send:count:{currency}:{packet_type}:{amount}:5"),
                InlineKeyboardButton("10", callback_data=f"packets:send:count:{currency}:{packet_type}:{amount}:10"),
                InlineKeyboardButton("20", callback_data=f"packets:send:count:{currency}:{packet_type}:{amount}:20"),
            ],
            [
                InlineKeyboardButton("📝 自定義數量", callback_data=f"packets:send:count_custom:{currency}:{packet_type}:{amount}"),
            ],
            [
                InlineKeyboardButton("◀️ 返回", callback_data=f"packets:send:amount:{currency}:{packet_type}"),
            ],
        ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_bomb_number_selection(query, db_user, context):
    """顯示炸彈數字選擇"""
    packet_data = context.user_data.get('send_packet', {})
    currency = packet_data.get('currency', 'usdt')
    packet_type = packet_data.get('packet_type', 'random')
    amount = packet_data.get('amount')
    count = packet_data.get('count')
    
    if packet_type != "equal":
        # 如果不是紅包炸彈，跳過這一步
        await show_message_input(query, db_user, context)
        return
    
    currency_upper = currency.upper()
    thunder_type = "單雷" if count == 10 else "雙雷"
    
    text = f"""
➕ *發紅包 - {currency_upper} - 紅包炸彈*

*金額：* `{amount}` {currency_upper}
*數量：* `{count}` 份（{thunder_type}）

請選擇炸彈數字（0-9）：
如果領取金額的小數點後最後一位數字與炸彈數字相同，將觸發炸彈
"""
    
    keyboard = []
    row = []
    for i in range(10):
        row.append(InlineKeyboardButton(str(i), callback_data=f"packets:send:message:{currency}:{packet_type}:{amount}:{count}:{i}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([
        InlineKeyboardButton("◀️ 返回", callback_data=f"packets:send:count:{currency}:{packet_type}:{amount}"),
    ])
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_message_input(query, db_user, context):
    """顯示祝福語輸入"""
    packet_data = context.user_data.get('send_packet', {})
    currency = packet_data.get('currency', 'usdt')
    packet_type = packet_data.get('packet_type', 'random')
    amount = packet_data.get('amount')
    count = packet_data.get('count')
    bomb_number = packet_data.get('bomb_number')
    
    currency_upper = currency.upper()
    type_text = "手氣最佳" if packet_type == "random" else "紅包炸彈"
    
    text = f"""
➕ *發紅包 - {currency_upper} - {type_text}*

*金額：* `{amount}` {currency_upper}
*數量：* `{count}` 份
{f"*炸彈數字：* `{bomb_number}`" if bomb_number is not None else ""}

請輸入祝福語（可選）：
直接發送消息作為祝福語，或點擊使用默認祝福語
"""
    
    keyboard = [
        [
            InlineKeyboardButton("✅ 使用默認祝福語", callback_data=f"packets:send:group:{currency}:{packet_type}:{amount}:{count}:{bomb_number or ''}:default"),
        ],
        [
            InlineKeyboardButton("📝 輸入祝福語", callback_data=f"packets:send:message_input:{currency}:{packet_type}:{amount}:{count}:{bomb_number or ''}"),
        ],
        [
            InlineKeyboardButton("◀️ 返回", callback_data=f"packets:send:bomb:{currency}:{packet_type}:{amount}:{count}" if bomb_number is not None else f"packets:send:count:{currency}:{packet_type}:{amount}"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    
    # 如果點擊了輸入祝福語，設置等待狀態
    if query.data and "message_input" in query.data:
        context.user_data['waiting_for_message'] = True


async def show_group_search(query, db_user, context):
    """顯示群組搜索結果（用於回覆鍵盤流程）"""
    packet_data = context.user_data.get('send_packet', {})
    
    # 在會話內獲取用戶發過紅包的群組
    with get_db() as db:
        from shared.database.models import User
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        packets = db.query(RedPacket).filter(
            RedPacket.sender_id == user.id
        ).order_by(RedPacket.created_at.desc()).limit(10).all()
    
    text = f"""
🔍 *查找群組*

*紅包信息：*
• 幣種：{packet_data.get('currency', 'usdt').upper()}
• 類型：{"手氣最佳" if packet_data.get('packet_type') == "random" else "紅包炸彈"}
• 金額：{packet_data.get('amount')} {packet_data.get('currency', 'usdt').upper()}
• 數量：{packet_data.get('count')} 份

*已發過紅包的群組：*
"""
    
    if not packets:
        text += "\n暫無已發過紅包的群組，請輸入群組 ID 或鏈接。"
    else:
        seen_chats = set()
        for i, packet in enumerate(packets[:5], 1):
            if packet.chat_id and packet.chat_id not in seen_chats:
                seen_chats.add(packet.chat_id)
                chat_title = packet.chat_title or f"群組 {packet.chat_id}"
                text += f"\n{i}. {chat_title}"
                # 保存到 context 以便後續使用
                if 'recent_groups' not in context.user_data:
                    context.user_data['recent_groups'] = []
                context.user_data['recent_groups'].append({
                    'chat_id': packet.chat_id,
                    'title': chat_title
                })
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
    )


async def show_group_selection(query, db_user, context):
    """顯示群組選擇"""
    packet_data = context.user_data.get('send_packet', {})
    
    # 在會話內獲取用戶發過紅包的群組
    with get_db() as db:
        from shared.database.models import User
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        packets = db.query(RedPacket).filter(
            RedPacket.sender_id == user.id
        ).order_by(RedPacket.created_at.desc()).limit(10).all()
    
    text = f"""
➕ *發紅包 - 選擇群組*

*紅包信息：*
• 幣種：{packet_data.get('currency', 'usdt').upper()}
• 類型：{"手氣最佳" if packet_data.get('packet_type') == "random" else "紅包炸彈"}
• 金額：{packet_data.get('amount')} {packet_data.get('currency', 'usdt').upper()}
• 數量：{packet_data.get('count')} 份
• 祝福語：{packet_data.get('message', PacketConstants.DEFAULT_MESSAGE)}

*方式一：* 在群組中使用命令
在目標群組中輸入：`/send <金額> <數量> [祝福語]`

*方式二：* 選擇已發過紅包的群組
"""
    
    keyboard = []
    
    # 添加已發過紅包的群組
    seen_chats = set()
    for packet in packets[:5]:
        if packet.chat_id and packet.chat_id not in seen_chats:
            seen_chats.add(packet.chat_id)
            chat_title = packet.chat_title or f"群組 {packet.chat_id}"
            keyboard.append([
                InlineKeyboardButton(
                    f"📱 {chat_title[:20]}",
                    callback_data=f"packets:send:confirm:{packet_data['currency']}:{packet_data['packet_type']}:{packet_data['amount']}:{packet_data['count']}:{packet_data.get('bomb_number', '')}:{packet_data.get('message', 'default')}:{packet.chat_id}"
                ),
            ])
    
    keyboard.append([
        InlineKeyboardButton("📝 輸入群組鏈接/ID", callback_data=f"packets:send:group_input:{packet_data['currency']}:{packet_data['packet_type']}:{packet_data['amount']}:{packet_data['count']}:{packet_data.get('bomb_number', '')}:{packet_data.get('message', 'default')}"),
    ])
    
    keyboard.append([
        InlineKeyboardButton("◀️ 返回", callback_data="menu:packets"),
    ])
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_group_link_input(query, db_user, context):
    """顯示群組鏈接輸入提示"""
    packet_data = context.user_data.get('send_packet', {})
    
    text = """
➕ *發紅包 - 輸入群組*

請輸入群組 ID 或群組鏈接：

*方式一：* 輸入群組 ID（數字）
例如：`-1001234567890`

*方式二：* 輸入群組鏈接
例如：`https://t.me/groupname` 或 `@groupname`

💡 提示：也可以在目標群組中直接使用命令 `/send <金額> <數量> [祝福語]`
"""
    
    keyboard = [
        [
            InlineKeyboardButton("◀️ 返回", callback_data=f"packets:send:group:{packet_data['currency']}:{packet_data['packet_type']}:{packet_data['amount']}:{packet_data['count']}:{packet_data.get('bomb_number', '')}:{packet_data.get('message', 'default')}"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    
    # 設置狀態，等待用戶輸入
    context.user_data['waiting_for_group'] = True


async def confirm_and_send_packet(query, db_user, context):
    """確認並發送紅包"""
    packet_data = context.user_data.get('send_packet', {})
    
    currency = packet_data.get('currency', 'usdt')
    packet_type = packet_data.get('packet_type', 'random')
    amount = Decimal(str(packet_data.get('amount', 0)))
    count = int(packet_data.get('count', 1))
    bomb_number = packet_data.get('bomb_number')
    message = packet_data.get('message', PacketConstants.DEFAULT_MESSAGE)
    chat_id = packet_data.get('chat_id')
    
    # 使用安全工具驗證
    from bot.utils.security import validate_amount, validate_packet_count
    from bot.utils.permissions import check_balance
    
    # 驗證金額
    balance = getattr(db_user, f"balance_{currency}", 0) or Decimal(0)
    is_valid, error_msg = validate_amount(str(amount), currency, balance)
    if not is_valid:
        await query.answer(error_msg, show_alert=True)
        return
    
    # 驗證數量
    is_valid, error_msg = validate_packet_count(count, packet_type)
    if not is_valid:
        await query.answer(error_msg, show_alert=True)
        return
    
    # 檢查權限和餘額
    has_permission, error_msg = check_balance(db_user, amount, currency)
    if not has_permission:
        await query.answer(error_msg, show_alert=True)
        return
    
    # 如果沒有選擇群組，提示用戶在群組中使用命令
    if not chat_id:
        text = f"""
✅ *紅包已準備好！*

*紅包信息：*
• 幣種：{currency.upper()}
• 類型：{"手氣最佳" if packet_type == "random" else "紅包炸彈"}
• 金額：{float(amount):.2f} {currency.upper()}
• 數量：{count} 份
{f"• 炸彈數字：{bomb_number}" if bomb_number is not None else ""}
• 祝福語：{message}

*發送方式：*
請在目標群組中輸入以下命令：

`/send {float(amount)} {count} {message}`

或者使用 miniapp 選擇群組發送
"""
        
        keyboard = [
            [
                InlineKeyboardButton(
                    "📱 使用 miniapp 發送",
                    web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/send")
                ),
            ],
            [
                InlineKeyboardButton("◀️ 返回", callback_data="menu:packets"),
            ],
        ]
        
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return
    
    # 創建紅包
    try:
        from bot.utils.api_client import get_api_client
        from bot.utils.security import sanitize_message
        from bot.utils.ui_helpers import show_loading
        
        # 顯示加載狀態
        await show_loading(query, "正在發送紅包...")
        
        # 清理消息
        message = sanitize_message(message)
        
        # 使用統一的 API 客戶端
        from bot.utils.logging_helpers import log_packet_action
        
        api_client = get_api_client()
        result = await api_client.post(
            "/redpackets/create",
            data={
                "currency": currency,
                "packet_type": packet_type,
                "total_amount": float(amount),
                "total_count": count,
                "message": message,
                "chat_id": chat_id,
                "bomb_number": bomb_number,
            },
            tg_id=db_user.tg_id
        )
        
        # 記錄紅包操作
        log_packet_action(
            user_id=db_user.tg_id,
            action="create",
            packet_id=result.get('id'),
            amount=float(amount),
            currency=currency,
            success=True
        )
        
        # 清除用戶緩存（因為餘額已更新）
        from bot.utils.cache import UserCache
        UserCache.invalidate(db_user.tg_id)
        
        # 使用輔助函數格式化信息
        packet_info = format_packet_info(currency, packet_type, amount, count, bomb_number, message)
        
        text = f"""
✅ *紅包發送成功！*

*紅包信息：*
{packet_info}
• UUID: `{result.get('uuid', '')}`

紅包已發送到群組！
"""
    except Exception as e:
        logger.error(f"Error sending packet: {e}", exc_info=True)
        error_msg = str(e)
        if "餘額不足" in error_msg or "Insufficient balance" in error_msg:
            error_msg = "餘額不足"
        elif "HTTP" in error_msg or "Request" in error_msg:
            error_msg = "網絡錯誤，請稍後再試"
        
        # 記錄失敗操作
        log_packet_action(
            user_id=db_user.tg_id,
            action="create",
            amount=float(amount),
            currency=currency,
            success=False
        )
        
        text = f"""
❌ *發送失敗*

錯誤：{error_msg}

請重試或使用 miniapp 發送
"""
    
    keyboard = [
        [
            InlineKeyboardButton("◀️ 返回", callback_data="menu:packets"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    
    # 清除臨時數據
    context.user_data.pop('send_packet', None)
    context.user_data.pop('waiting_for_group', None)
    context.user_data.pop('waiting_for_message', None)


async def show_my_packets(query, db_user):
    """顯示我發送的紅包"""
    # 在會話內重新查詢用戶以確保數據最新
    with get_db() as db:
        from shared.database.models import User
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        packets = db.query(RedPacket).filter(
            RedPacket.sender_id == user.id
        ).order_by(RedPacket.created_at.desc()).limit(10).all()
    
    if not packets:
        text = """
🎁 *我的紅包*

您還沒有發送過紅包

快去發一個吧！
"""
    else:
        text = "🎁 *我發送的紅包*\n\n"
        for i, packet in enumerate(packets[:5], 1):
            claimed = packet.claimed_count or 0
            total = packet.total_count
            status_emoji = "✅" if packet.status == RedPacketStatus.COMPLETED else "⏳" if packet.status == RedPacketStatus.ACTIVE else "❌"
            text += f"{status_emoji} {i}. {packet.message or PacketConstants.DEFAULT_MESSAGE}\n"
            text += f"   💰 {float(packet.total_amount):.2f} {packet.currency.value.upper()}\n"
            text += f"   👥 {claimed}/{total} 已領取\n\n"
    
    keyboard = [
        [
            InlineKeyboardButton(
                "📱 查看完整記錄",
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/packets")
            ),
        ],
        [
            InlineKeyboardButton("◀️ 返回", callback_data="menu:packets"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
