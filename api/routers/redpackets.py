"""
Lucky Red - 紅包路由
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, asc
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Union
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import random
from loguru import logger

from shared.database.connection import get_db_session
from shared.database.models import (
    User, RedPacket, RedPacketClaim, CurrencyType, RedPacketType, RedPacketStatus,
    RedPacketVisibility, RedPacketSource
)
from shared.config.settings import get_settings
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from api.utils.telegram_auth import get_tg_id_from_header

settings = get_settings()
router = APIRouter()
bot = Bot(token=settings.BOT_TOKEN)


def get_enum_value(value) -> str:
    """安全獲取枚舉或字符串的值"""
    if hasattr(value, 'value'):
        return value.value
    return str(value)


class CreateRedPacketRequest(BaseModel):
    """創建紅包請求"""
    currency: Union[CurrencyType, str] = CurrencyType.USDT
    packet_type: Union[RedPacketType, str] = RedPacketType.RANDOM
    total_amount: float = Field(..., gt=0)
    total_count: int = Field(..., ge=1, le=100)
    message: str = Field(default="", max_length=256)  # 默认值将在创建时使用 i18n
    chat_id: Optional[int] = None
    chat_title: Optional[str] = None
    bomb_number: Optional[int] = None  # 紅包炸彈數字（0-9）
    
    @field_validator('currency', mode='before')
    @classmethod
    def normalize_currency(cls, v):
        """將 currency 轉換為小寫並映射到 CurrencyType 枚舉"""
        if isinstance(v, str):
            v_lower = v.lower()
            currency_map = {
                "usdt": CurrencyType.USDT,
                "ton": CurrencyType.TON,
                "stars": CurrencyType.STARS,
                "points": CurrencyType.POINTS,
            }
            return currency_map.get(v_lower, CurrencyType.USDT)
        return v
    
    @field_validator('packet_type', mode='before')
    @classmethod
    def normalize_packet_type(cls, v):
        """將 packet_type 轉換並映射到 RedPacketType 枚舉"""
        if isinstance(v, str):
            v_lower = v.lower()
            # 映射前端使用的 'fixed' 到后端的 'equal'（平分）
            packet_type_map = {
                "random": RedPacketType.RANDOM,
                "fixed": RedPacketType.EQUAL,  # 固定金額 = 平分
                "equal": RedPacketType.EQUAL,
                "exclusive": RedPacketType.EXCLUSIVE,
            }
            return packet_type_map.get(v_lower, RedPacketType.RANDOM)
        return v


class RedPacketResponse(BaseModel):
    """紅包響應"""
    id: int
    uuid: str
    currency: str
    packet_type: str
    total_amount: float
    total_count: int
    claimed_amount: float
    claimed_count: int
    message: str
    status: str
    created_at: datetime
    message_sent: bool = False  # 消息是否成功發送到群組
    share_link: Optional[str] = None  # 分享鏈接（如果機器人不在群組中）
    is_claimed: Optional[bool] = None  # 當前用戶是否已領取（需要認證）
    
    class Config:
        from_attributes = True


class ClaimResult(BaseModel):
    """領取結果"""
    success: bool
    amount: float
    is_luckiest: bool
    message: str


@router.post("/create", response_model=RedPacketResponse)
async def create_red_packet(
    request: CreateRedPacketRequest,
    sender_tg_id: Optional[int] = Depends(get_tg_id_from_header),
    db: AsyncSession = Depends(get_db_session)
):
    """創建紅包"""
    # 立即記錄請求信息，用於調試（使用簡單格式，避免被過濾）
    logger.info(f"[CREATE_RED_PACKET] Request received: sender_tg_id={sender_tg_id}, chat_id={request.chat_id}, chat_id_type={type(request.chat_id).__name__}, amount={request.total_amount}, count={request.total_count}")
    logger.info(f"[CREATE_RED_PACKET] chat_id details: value={request.chat_id}, is_none={request.chat_id is None}, bool_value={bool(request.chat_id)}")
    
    if sender_tg_id is None:
        raise HTTPException(status_code=401, detail="Telegram user ID is required")
    
    # 查找發送者
    result = await db.execute(select(User).where(User.tg_id == sender_tg_id))
    sender = result.scalar_one_or_none()
    
    if not sender:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 使用LedgerService檢查餘額
    from api.services.ledger_service import LedgerService
    currency_str = get_enum_value(request.currency).upper()
    current_balance = await LedgerService.get_balance(
        db=db,
        user_id=sender.id,
        currency=currency_str
    )
    
    if current_balance < Decimal(str(request.total_amount)):
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # 驗證紅包炸彈規則
    if request.packet_type == RedPacketType.EQUAL:  # 紅包炸彈（固定金額）
        if request.bomb_number is None:
            raise HTTPException(status_code=400, detail="Bomb number is required for bomb red packet")
        if request.bomb_number < 0 or request.bomb_number > 9:
            raise HTTPException(status_code=400, detail="Bomb number must be between 0 and 9")
        
        # 驗證紅包數量：單雷10個，雙雷5個
        if request.total_count not in [5, 10]:
            raise HTTPException(
                status_code=400,
                detail="Bomb red packet count must be 5 (雙雷) or 10 (單雷)"
            )
    
    # 使用LedgerService扣除餘額（創建賬本條目）
    from api.services.ledger_service import LedgerService
    try:
        currency_str = get_enum_value(request.currency)
        await LedgerService.create_entry(
            db=db,
            user_id=sender.id,
            amount=-Decimal(str(request.total_amount)),  # 負數表示扣除
            currency=currency_str.upper(),
            entry_type='SEND_PACKET',
            related_type='red_packet',
            description=f"發送紅包: {request.total_amount} {currency_str}",
            created_by='user'
        )
    except ValueError as e:
        # 餘額不足
        raise HTTPException(status_code=400, detail=str(e))
    
    # 判斷紅包可見性和來源類型
    if request.chat_id is None:
        # 公開紅包
        visibility = RedPacketVisibility.PUBLIC
        source_type = RedPacketSource.USER_PUBLIC
    else:
        # 私密紅包
        visibility = RedPacketVisibility.PRIVATE
        source_type = RedPacketSource.USER_PRIVATE
    
    # 創建紅包
    from bot.utils.i18n import t
    # 如果消息为空，使用默认祝福语
    default_message = request.message if request.message else t('default_blessing', user=sender)
    
    packet_uuid = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=24)
    packet = RedPacket(
        uuid=packet_uuid,
        sender_id=sender.id,
        currency=request.currency,
        packet_type=request.packet_type,
        total_amount=Decimal(str(request.total_amount)),
        total_count=request.total_count,
        message=default_message,
        chat_id=request.chat_id,  # 公開紅包時為 NULL
        chat_title=request.chat_title,
        bomb_number=request.bomb_number if request.packet_type == RedPacketType.EQUAL else None,
        expires_at=expires_at,
        visibility=visibility,
        source_type=source_type,
    )
    
    db.add(packet)
    await db.commit()
    await db.refresh(packet)
    
    # 初始化红包到Redis（用于高并发抢红包）
    try:
        from api.services.redis_claim_service import RedisClaimService
        await RedisClaimService.init_packet(
            packet_uuid=packet_uuid,
            packet_data={
                'sender_id': sender.id,
                'currency': get_enum_value(request.currency),
                'packet_type': get_enum_value(request.packet_type),
                'total_amount': float(request.total_amount),
                'total_count': request.total_count,
                'claimed_amount': 0,
                'claimed_count': 0,
                'status': 'ACTIVE',
                'expires_at': int(expires_at.timestamp()),
                'bomb_number': request.bomb_number if request.packet_type == RedPacketType.EQUAL else None,
            }
        )
        logger.info(f"✅ 红包已初始化到Redis: {packet_uuid}")
    except Exception as e:
        logger.warning(f"⚠️ 初始化Redis红包失败（将使用数据库模式）: {e}")
    
    # 融合任務系統：標記發紅包任務完成（使用新的數據庫會話）
    try:
        from api.routers.tasks import mark_task_complete_internal
        from shared.database.connection import get_db_session
        # 創建新的數據庫會話來標記任務完成
        async def mark_send_task():
            try:
                async for new_db in get_db_session():
                    await mark_task_complete_internal("send_packet", sender_tg_id, new_db)
                    break
            except Exception as e:
                logger.warning(f"Failed to mark send_packet task complete: {e}")
        
        # 異步調用任務完成標記（不阻塞創建響應）
        import asyncio
        asyncio.create_task(mark_send_task())
    except Exception as e:
        logger.warning(f"Failed to mark send_packet task complete: {e}")
    
    # 發送紅包消息到群組（如果指定了群組）
    message_sent = False
    share_link = None
    
    # 立即記錄 chat_id 狀態（使用簡單格式，避免被過濾）
    logger.info(f"[SEND_CHECK] request.chat_id={request.chat_id}, type={type(request.chat_id).__name__}, bool={bool(request.chat_id)}, is_none={request.chat_id is None}")
    
    # 確保 chat_id 是整數類型
    chat_id = None
    if request.chat_id is not None:
        try:
            chat_id = int(request.chat_id)
            logger.info(f"[SEND_TO_GROUP] Preparing to send red packet to group {chat_id} (original={request.chat_id}, type={type(request.chat_id).__name__})")
            logger.info(f"[SEND_TO_GROUP] Packet info: uuid={packet.uuid}, amount={packet.total_amount}, count={packet.total_count}")
        except (ValueError, TypeError) as e:
            logger.error(f"[SEND_TO_GROUP] chat_id conversion failed: {request.chat_id} (type={type(request.chat_id).__name__}), error={e}")
            chat_id = None
    else:
        logger.info(f"[SEND_TO_GROUP] request.chat_id is None, skipping group send")
    
    if chat_id:
        try:
            # 檢查機器人是否在群組中
            bot_info = await bot.get_me()
            logger.info(f"[BOT_INFO] Bot ID={bot_info.id}, Username=@{bot_info.username}")
            
            try:
                bot_member = await bot.get_chat_member(chat_id, bot_info.id)
                bot_status = bot_member.status
                logger.info(f"[BOT_STATUS] Bot status in group {chat_id}: {bot_status}")
                
                # 將 bot_status 轉換為字符串以便比較
                bot_status_str = str(bot_status).lower()
                logger.info(f"[BOT_STATUS_DETAIL] status={bot_status_str}, type={type(bot_status).__name__}")
                
                if bot_status_str not in ['left', 'kicked']:
                    # 機器人在群組中，檢查是否有發送消息的權限
                    can_send = False
                    
                    # 檢查權限屬性
                    if hasattr(bot_member, 'can_send_messages'):
                        can_send = bot_member.can_send_messages
                        logger.info(f"🔍 從 can_send_messages 屬性獲取權限: {can_send}")
                    elif bot_status_str in ['administrator', 'creator']:
                        # 管理員和創建者通常有發送消息的權限
                        can_send = True
                        logger.info(f"🔍 管理員/創建者身份，默認有發送權限")
                    elif bot_status_str == 'member':
                        # 普通成員，默認有發送權限（除非群組設置了限制）
                        can_send = True
                        logger.info(f"🔍 普通成員身份，默認有發送權限")
                    else:
                        # 其他狀態，嘗試發送（如果失敗會被捕獲）
                        can_send = True
                        logger.warning(f"⚠️  未知的機器人狀態: {bot_status_str}，將嘗試發送")
                    
                    logger.info(f"📋 權限檢查結果: can_send={can_send}, bot_status={bot_status_str}")
                    
                    if not can_send:
                        logger.warning(f"⚠️  機器人在群組 {chat_id} 中但沒有發送消息的權限 (status={bot_status_str})")
                        share_link = f"{settings.MINIAPP_URL}/claim/{packet.uuid}"
                    else:
                        # 機器人在群組中且有權限，發送紅包消息
                        try:
                            # 安全獲取 packet_type 和 currency 的值
                            packet_type_str = get_enum_value(request.packet_type)
                            currency_str = get_enum_value(packet.currency)
                            
                            # 使用發送者的語言設置構建群組消息
                            from bot.utils.i18n import t
                            # 獲取發送者的語言設置
                            sender_lang = sender.language_code if sender.language_code else "en"
                            
                            # 構建群組中的紅包消息（使用發送者的語言）
                            random_packet_type = t('random_packet_type', user=sender)
                            bomb_packet_type = t('bomb_packet_type', user=sender)
                            type_text = random_packet_type if packet_type_str == "random" else bomb_packet_type
                            
                            amount_label = t('amount_label_short', user=sender)
                            quantity_label = t('quantity_label_short', user=sender)
                            shares_label = t('shares_label', user=sender)
                            click_to_claim = t('click_to_claim', user=sender)
                            claim_button_text = t('claim_red_packet', user=sender)
                            
                            group_message = f"""
🧧 *{packet.message}*

{type_text}
{amount_label}{float(packet.total_amount):.2f} {currency_str.upper()}
{quantity_label}{packet.total_count} {shares_label}

{click_to_claim}
"""
                            # 構建搶紅包按鈕
                            claim_keyboard = [[
                                InlineKeyboardButton(
                                    claim_button_text,
                                    callback_data=f"claim:{packet.uuid}"
                                )
                            ]]
                            
                            logger.info(f"[SEND_MESSAGE] Sending message to group {chat_id} (type={type(chat_id).__name__})")
                            logger.info(f"[SEND_MESSAGE] Message preview: {group_message[:100]}...")
                            logger.info(f"[SEND_MESSAGE] Button data: {claim_keyboard}")
                            
                            # 尝试发送消息，如果 Markdown 解析失败，使用 HTML 或纯文本
                            try:
                                sent_message = await bot.send_message(
                                    chat_id=chat_id,
                                    text=group_message,
                                    parse_mode="Markdown",
                                    reply_markup=InlineKeyboardMarkup(claim_keyboard)
                                )
                            except TelegramError as parse_error:
                                # Markdown 解析失败，尝试使用 HTML
                                error_msg = str(parse_error).lower()
                                if "can't parse" in error_msg or "parse" in error_msg:
                                    logger.warning(f"⚠️  Markdown 解析失败，尝试使用 HTML: {parse_error}")
                                    # 转换 Markdown 到 HTML
                                    html_message = group_message.replace("*", "<b>").replace("*", "</b>")
                                    html_message = html_message.replace("_", "<i>").replace("_", "</i>")
                                    sent_message = await bot.send_message(
                                        chat_id=chat_id,
                                        text=html_message,
                                        parse_mode="HTML",
                                        reply_markup=InlineKeyboardMarkup(claim_keyboard)
                                    )
                                else:
                                    # 其他错误，重新抛出
                                    raise
                            message_sent = True
                            logger.info(f"[SEND_SUCCESS] Red packet message sent to group {chat_id}, message_id={sent_message.message_id}, date={sent_message.date}")
                        except TelegramError as tg_error:
                            error_msg = str(tg_error).lower()
                            logger.error(f"[SEND_FAILED] Failed to send red packet to group {chat_id}: {type(tg_error).__name__}: {str(tg_error)}")
                            logger.exception(tg_error)  # 記錄完整的堆棧跟踪
                            
                            # 檢查是否是權限問題
                            if "not enough rights" in error_msg or "can't send messages" in error_msg or "forbidden" in error_msg:
                                logger.warning(f"[SEND_FAILED] Bot does not have permission to send messages (group {chat_id})")
                            # 發送失敗，返回分享鏈接
                            share_link = f"{settings.MINIAPP_URL}/claim/{packet.uuid}"
                        except Exception as e:
                            logger.error(f"[SEND_FAILED] Unexpected error sending red packet to group {chat_id}: {type(e).__name__}: {str(e)}")
                            logger.exception(e)  # 記錄完整的堆棧跟踪
                            # 發送失敗，返回分享鏈接
                            share_link = f"{settings.MINIAPP_URL}/claim/{packet.uuid}"
                else:
                    # 機器人不在群組中，返回分享鏈接
                    logger.warning(f"[SEND_SKIP] Bot not in group {chat_id} (status={bot_status}), returning share link")
                    share_link = f"{settings.MINIAPP_URL}/claim/{packet.uuid}"
            except TelegramError as member_error:
                error_msg = str(member_error).lower()
                logger.warning(f"[BOT_CHECK_FAILED] Failed to check bot member status: {error_msg}")
                logger.exception(member_error)  # 記錄完整的堆棧跟踪
                if "chat not found" in error_msg or "not enough rights" in error_msg or "forbidden" in error_msg:
                    # 機器人不在群組中，返回分享鏈接
                    logger.warning(f"⚠️  機器人無法訪問群組 {chat_id}，返回分享鏈接")
                    share_link = f"{settings.MINIAPP_URL}/claim/{packet.uuid}"
                else:
                    # 其他錯誤，嘗試直接發送
                    logger.info(f"🔄 嘗試直接發送消息到群組 {chat_id}...")
                    try:
                        packet_type_str = get_enum_value(request.packet_type)
                        currency_str = get_enum_value(packet.currency)
                        
                        type_text = "🎲 手氣最佳" if packet_type_str == "random" else "💣 紅包炸彈"
                        group_message = f"""
🧧 *{packet.message}*

{type_text}
💰 金額：{float(packet.total_amount):.2f} {currency_str.upper()}
👥 數量：{packet.total_count} 份

🎁 點擊下方按鈕搶紅包！
"""
                        claim_keyboard = [[
                            InlineKeyboardButton(
                                "🧧 搶紅包",
                                callback_data=f"claim:{packet.uuid}"
                            )
                        ]]
                        
                        logger.info(f"📨 直接發送消息到群組 {chat_id}...")
                        sent_message = await bot.send_message(
                            chat_id=chat_id,
                            text=group_message,
                            parse_mode="Markdown",
                            reply_markup=InlineKeyboardMarkup(claim_keyboard)
                        )
                        message_sent = True
                        logger.info(f"✅ 直接發送成功，消息ID: {sent_message.message_id}")
                    except Exception as send_error:
                        logger.error(f"❌ 直接發送也失敗: {type(send_error).__name__}: {str(send_error)}")
                        logger.exception(send_error)
                        share_link = f"{settings.MINIAPP_URL}/claim/{packet.uuid}"
        except Exception as e:
            logger.error(f"❌ 檢查機器人狀態時發生未預期的錯誤: {type(e).__name__}: {str(e)}")
            logger.exception(e)
            share_link = f"{settings.MINIAPP_URL}/claim/{packet.uuid}"
    else:
        logger.info("ℹ️  未指定 chat_id，這是公開紅包，不發送到群組")
    
    # 返回響應
    response = RedPacketResponse(
        id=packet.id,
        uuid=packet.uuid,
        currency=packet.currency.value,
        packet_type=packet.packet_type.value,
        total_amount=float(packet.total_amount),
        total_count=packet.total_count,
        claimed_amount=float(packet.claimed_amount),
        claimed_count=packet.claimed_count,
        message=packet.message,
        status=packet.status.value,
        created_at=packet.created_at,
        message_sent=message_sent,  # 機器人在群組中時為 True
        share_link=share_link  # 機器人不在群組中時返回分享鏈接
    )
    
    return response


@router.post("/{packet_uuid}/claim", response_model=ClaimResult)
async def claim_red_packet(
    packet_uuid: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """領取紅包（支持Redis高并发，支持 Telegram 和 JWT Token 認證）"""
    logger.info(f"🎯 收到搶紅包請求: packet_uuid={packet_uuid}, type={type(packet_uuid).__name__}")
    """領取紅包（支持Redis高并发，支持 Telegram 和 JWT Token 認證）"""
    from api.routers.auth import get_current_user_from_token
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    
    # 尝试通过 JWT Token 或 Telegram initData 获取用户
    claimer = None
    try:
        security = HTTPBearer(auto_error=False)
        credentials: Optional[HTTPAuthorizationCredentials] = None
        try:
            credentials = await security(request)
        except:
            pass  # 如果没有 Bearer token，继续尝试 Telegram initData
        
        claimer = await get_current_user_from_token(
            request=request,
            credentials=credentials,
            x_telegram_init_data=request.headers.get("X-Telegram-Init-Data"),
            db=db
        )
    except HTTPException as e:
        # 如果认证失败，尝试回退到 Telegram initData（仅通过 header）
        claimer_tg_id = get_tg_id_from_header(
            x_telegram_init_data=request.headers.get("X-Telegram-Init-Data")
        )
        if claimer_tg_id is None:
            raise HTTPException(
                status_code=401, 
                detail="需要登錄才能搶紅包。請通過 Telegram MiniApp 訪問或先登錄。"
            )
        
        # 查找領取者
        result = await db.execute(select(User).where(User.tg_id == claimer_tg_id))
        claimer = result.scalar_one_or_none()
        
        if not claimer:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"認證錯誤: {e}")
        raise HTTPException(
            status_code=401, 
            detail="需要登錄才能搶紅包。請通過 Telegram MiniApp 訪問或先登錄。"
        )
    
    if not claimer:
        raise HTTPException(
            status_code=401, 
            detail="需要登錄才能搶紅包。請通過 Telegram MiniApp 訪問或先登錄。"
        )
    
    # 查找紅包（支持 uuid 或 id）
    try:
        # 先嘗試用 uuid 查找
        result = await db.execute(select(RedPacket).where(RedPacket.uuid == packet_uuid))
        packet = result.scalar_one_or_none()
        
        # 如果找不到，嘗試用 id 查找（如果 packet_uuid 是數字）
        if not packet and packet_uuid.isdigit():
            packet_id = int(packet_uuid)
            result = await db.execute(select(RedPacket).where(RedPacket.id == packet_id))
            packet = result.scalar_one_or_none()
            if packet:
                logger.info(f"🔄 使用 ID 找到紅包: id={packet_id}, uuid={packet.uuid}")
        
        if not packet:
            logger.error(f"❌ 紅包不存在: packet_uuid={packet_uuid}")
            raise HTTPException(status_code=404, detail="Red packet not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 查找紅包時發生錯誤: {e}")
        raise HTTPException(status_code=404, detail="Red packet not found")
    
    # 尝试使用Redis高并发抢红包
    from api.services.redis_claim_service import RedisClaimService
    claim_id = str(uuid.uuid4())
    
    # 使用實際的 uuid
    actual_uuid = packet.uuid
    logger.info(f"🎯 使用實際 UUID 搶紅包: {actual_uuid}")
    
    success, error_code, amount, packet_status = await RedisClaimService.claim_packet(
        packet_uuid=actual_uuid,
        user_id=claimer.id,
        claim_id=claim_id
    )
    
    if success and amount:
        # Redis抢红包成功，异步同步到数据库
        # 将同步任务加入队列
        try:
            from api.services.queue_service import get_queue_service
            queue_service = get_queue_service()
            
            await queue_service.enqueue_ledger_sync(
                packet_uuid=packet_uuid,
                user_id=claimer.id,
                claim_id=claim_id,
                amount=float(amount),
                currency=packet.currency.value.upper(),
                packet_status=packet_status
            )
            
            logger.info(f"✅ 账本同步任务已加入队列: packet={packet_uuid}, user={claimer.id}")
        except Exception as e:
            logger.warning(f"⚠️ 加入队列失败，使用同步模式: {e}")
            # 回退到同步模式
            result = await db.execute(select(RedPacket).where(RedPacket.uuid == packet_uuid))
            packet = result.scalar_one_or_none()
            
            if not packet:
                raise HTTPException(status_code=404, detail="Red packet not found")
            
            # 创建领取记录
            claim = RedPacketClaim(
                red_packet_id=packet.id,
                user_id=claimer.id,
                amount=amount,
                is_bomb=False,
                penalty_amount=None,
            )
            db.add(claim)
            
            # 更新红包状态
            packet.claimed_amount += amount
            packet.claimed_count = packet_status['claimed_count']
            if packet_status['status'] == 'COMPLETED':
                packet.status = RedPacketStatus.COMPLETED
                packet.completed_at = datetime.utcnow()
            
            await db.commit()
            
            # 使用LedgerService更新余额
            from api.services.ledger_service import LedgerService
            await LedgerService.create_entry(
                db=db,
                user_id=claimer.id,
                amount=amount,
                currency=packet.currency.value.upper(),
                entry_type='CLAIM_PACKET',
                related_type='red_packet',
                related_id=packet.id,
                description=f"領取紅包: {amount} {packet.currency.value}",
                created_by='user'
            )
            
            # 处理推荐奖励（Tier 1 & Tier 2）
            try:
                from api.services.referral_service import ReferralService
                await ReferralService.process_referral_reward(
                    db=db,
                    user_id=claimer.id,
                    amount=amount,
                    currency=packet.currency.value.upper(),
                    reward_type='redpacket',
                    metadata={
                        'packet_id': packet.id,
                        'packet_uuid': packet.uuid
                    }
                )
            except Exception as e:
                logger.warning(f"处理推荐奖励失败: {e}")
        
        return ClaimResult(
            success=True,
            amount=float(amount),
            is_luckiest=False,  # 需要等红包领完后才能确定
            message=f"恭喜領取 {amount} {packet.currency.value}！"
        )
    
    # Redis不可用或失败，回退到数据库模式
    if error_code == "REDIS_NOT_AVAILABLE":
        logger.warning("Redis不可用，使用数据库模式抢红包")
    else:
        logger.warning(f"Redis抢红包失败: {error_code}，回退到数据库模式")
    
    # 查找紅包
    result = await db.execute(select(RedPacket).where(RedPacket.uuid == packet_uuid))
    packet = result.scalar_one_or_none()
    
    if not packet:
        raise HTTPException(status_code=404, detail="Red packet not found")
    
    if packet.status != RedPacketStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Red packet is not active")
    
    if packet.expires_at and packet.expires_at < datetime.utcnow():
        packet.status = RedPacketStatus.EXPIRED
        await db.commit()
        raise HTTPException(status_code=400, detail="Red packet expired")
    
    # 檢查是否已領取
    result = await db.execute(
        select(RedPacketClaim).where(
            and_(
                RedPacketClaim.red_packet_id == packet.id,
                RedPacketClaim.user_id == claimer.id
            )
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already claimed")
    
    # 計算領取金額
    remaining_amount = packet.total_amount - packet.claimed_amount
    remaining_count = packet.total_count - packet.claimed_count
    
    if remaining_count <= 0:
        packet.status = RedPacketStatus.COMPLETED
        await db.commit()
        raise HTTPException(status_code=400, detail="Red packet is empty")
    
    if packet.packet_type == RedPacketType.EQUAL:
        amount = remaining_amount / remaining_count
    else:
        # 隨機金額 (保證最後一個人能拿到剩餘)
        if remaining_count == 1:
            amount = remaining_amount
        else:
            max_amount = remaining_amount * Decimal("0.9") / remaining_count * 2
            amount = Decimal(str(random.uniform(0.01, float(max_amount))))
            amount = min(amount, remaining_amount - Decimal("0.01") * (remaining_count - 1))
    
    amount = round(amount, 8)
    
    # 紅包炸彈：檢查是否踩雷
    is_bomb = False
    penalty_amount = Decimal(0)
    
    if packet.packet_type == RedPacketType.EQUAL and packet.bomb_number is not None:
        # 獲取金額的最後一位有效數字
        # 方法：將金額轉換為整數（乘以100000000，保留8位小數精度），然後取模10
        # 這樣可以準確獲取最後一位數字，不受小數點影響
        amount_int = int(amount * Decimal("100000000"))  # 轉換為整數（8位小數精度）
        last_digit = amount_int % 10  # 取最後一位數字
        
        # 檢查是否等於炸彈數字
        if last_digit == packet.bomb_number:
            is_bomb = True
            # 計算賠付：單雷（10個）賠1倍，雙雷（5個）賠2倍
            multiplier = 1 if packet.total_count == 10 else 2
            penalty_amount = amount * Decimal(multiplier)
    
    # 創建領取記錄
    claim = RedPacketClaim(
        red_packet_id=packet.id,
        user_id=claimer.id,
        amount=amount,
        is_bomb=is_bomb,
        penalty_amount=penalty_amount if is_bomb else None,
    )
    db.add(claim)
    
    # 更新紅包狀態
    packet.claimed_amount += amount
    packet.claimed_count += 1
    
    is_luckiest = False
    is_completed = packet.claimed_count >= packet.total_count
    
    if is_completed:
        packet.status = RedPacketStatus.COMPLETED
        packet.completed_at = datetime.utcnow()
    
    # 使用LedgerService更新餘額（創建賬本條目）
    from api.services.ledger_service import LedgerService
    
    # 計算實際獲得金額（考慮紅包炸彈懲罰）
    actual_amount = amount
    penalty_amount = Decimal(0)
    
    # 紅包炸彈懲罰邏輯
    if is_bomb:
        penalty_amount = amount * 2  # 觸發炸彈，扣除雙倍金額
        
        # 檢查餘額是否足夠賠付
        current_balance = await LedgerService.get_balance(
            db=db,
            user_id=claimer.id,
            currency=packet.currency.value.upper()
        )
        
        # 先加上領取金額，再扣除罰金
        balance_after_claim = current_balance + amount
        if balance_after_claim < penalty_amount:
            # 如果餘額不足，只扣除現有餘額（不能為負）
            actual_penalty = balance_after_claim
            penalty_amount = actual_penalty
            claim.penalty_amount = penalty_amount
            actual_amount = -actual_penalty  # 負數表示扣除
        else:
            actual_amount = amount - penalty_amount  # 領取金額減去罰金
        
        # 將罰金轉給發送者
        sender_result = await db.execute(select(User).where(User.id == packet.sender_id))
        sender = sender_result.scalar_one_or_none()
        if sender and penalty_amount > 0:
            await LedgerService.create_entry(
                db=db,
                user_id=sender.id,
                amount=penalty_amount,
                currency=packet.currency.value.upper(),
                entry_type='REDPACKET_BOMB_PENALTY',
                related_type='red_packet',
                related_id=packet.id,
                description=f"紅包炸彈罰金: {penalty_amount} {packet.currency.value}",
                created_by='system'
            )
    
    # 創建領取記錄的賬本條目
    await LedgerService.create_entry(
        db=db,
        user_id=claimer.id,
        amount=actual_amount,
        currency=packet.currency.value.upper(),
        entry_type='REDPACKET_CLAIM',
        related_type='red_packet',
        related_id=packet.id,
        description=f"領取紅包: {amount} {packet.currency.value}" + 
                    (f" (觸發炸彈，扣除 {penalty_amount})" if penalty_amount > 0 else ""),
        created_by='user'
    )
    
    # 先提交以便查詢包含當前的 claim
    await db.commit()
    await db.refresh(claim)
    
    # 計算手氣最佳（僅對隨機紅包，且紅包已領完）
    if is_completed and packet.packet_type == RedPacketType.RANDOM:
        # 查詢所有領取記錄，按金額降序、領取時間升序排序
        # 這樣可以找出金額最大的，如果金額相同則選最早領取的
        result = await db.execute(
            select(RedPacketClaim)
            .where(RedPacketClaim.red_packet_id == packet.id)
            .order_by(desc(RedPacketClaim.amount), asc(RedPacketClaim.claimed_at))
        )
        all_claims = result.scalars().all()
        
        if all_claims:
            # 第一個就是手氣最佳的（金額最大，如果相同則最早領取）
            luckiest_claim = all_claims[0]
            luckiest_claim.is_luckiest = True
            # 如果當前領取者是最佳手氣
            if luckiest_claim.id == claim.id:
                is_luckiest = True
            await db.commit()
    
    # 紅包領完後發送群組通知
    if is_completed and packet.chat_id:
        try:
            from api.services.group_notification_service import notify_packet_result
            await notify_packet_result(db, packet.id)
        except Exception as e:
            logger.error(f"Failed to send group notification: {e}")
    
    # 發送消息通知（異步，不阻塞響應）
    try:
        from api.services.message_service import MessageService
        message_service = MessageService(db)
        await message_service.send_redpacket_notification(
            user_id=claimer.id,
            redpacket_id=packet.id,
            amount=float(amount),
            currency=packet.currency.value,
            is_claimed=True
        )
        # 發送餘額變動通知
        await message_service.send_balance_notification(
            user_id=claimer.id,
            amount=float(amount),
            currency=packet.currency.value,
            transaction_type="receive",
            balance_after=float(await LedgerService.get_balance(db, claimer.id, packet.currency.value.upper()))
        )
    except Exception as e:
        logger.error(f"Failed to send message notification: {e}")
    
    # WebSocket 實時推送
    try:
        from api.services.notification_service import notification_service
        # 通知領取者（餘額變動）
        await notification_service.notify_packet_claimed(
            db, claimer.id, packet.sender_id, 
            amount - penalty_amount if is_bomb else amount,
            packet.currency.value, str(packet.id),
            is_bomb=is_bomb, is_lucky=is_luckiest
        )
    except Exception as e:
        logger.error(f"Failed to send WebSocket notification: {e}")
    
    # 構建消息
    if is_bomb:
        # 使用 i18n 翻译消息
        from bot.utils.i18n import t
        try:
            # 尝试从发送者获取语言
            sender_result = await db.execute(select(User).where(User.id == packet.sender_id))
            sender = sender_result.scalar_one_or_none()
            if sender:
                bomb_triggered_msg = t('bomb_triggered_message', user=sender, amount=float(amount), currency=packet.currency.value.upper(), penalty=float(penalty_amount)) if t('bomb_triggered_message', user=sender) != 'bomb_triggered_message' else f"💣 踩雷了！獲得 {amount} {packet.currency.value.upper()}，但需賠付 {penalty_amount} {packet.currency.value.upper()}！"
            else:
                bomb_triggered_msg = f"💣 踩雷了！獲得 {amount} {packet.currency.value.upper()}，但需賠付 {penalty_amount} {packet.currency.value.upper()}！"
        except:
            bomb_triggered_msg = f"💣 踩雷了！獲得 {amount} {packet.currency.value.upper()}，但需賠付 {penalty_amount} {packet.currency.value.upper()}！"
        
        message = bomb_triggered_msg
    else:
        message = f"恭喜獲得 {amount} {packet.currency.value.upper()}！"
        if is_luckiest:
            message += " 🎉 手氣最佳！"
    
    return ClaimResult(
        success=True,
        amount=float(amount - penalty_amount if is_bomb else amount),  # 實際到賬金額
        is_luckiest=is_luckiest,
        message=message
    )


@router.get("/list", response_model=List[RedPacketResponse])
@router.get("", response_model=List[RedPacketResponse])  # 兼容 /api/redpackets 路径
async def list_red_packets(
    request: Request,
    status: Optional[RedPacketStatus] = None,
    chat_id: Optional[int] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db_session)
):
    """
    獲取公開紅包列表
    
    只返回公開紅包（chat_id 為 NULL），不包含發送到指定群組或用戶的私密紅包。
    公開紅包包括：
    - 用戶主動發送的公開隨機紅包
    - 任務紅包（需要完成任務才能領取）
    - 獎勵紅包（系統獎勵、活動獎勵等）
    """
    # 尝试获取当前用户（可选，不强制认证）
    current_user = None
    try:
        from api.routers.auth import get_current_user_from_token
        from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
        security = HTTPBearer(auto_error=False)
        credentials: Optional[HTTPAuthorizationCredentials] = None
        try:
            credentials = await security(request)
        except:
            pass
        current_user = await get_current_user_from_token(
            request=request,
            credentials=credentials,
            x_telegram_init_data=request.headers.get("X-Telegram-Init-Data"),
            db=db
        )
    except:
        # 未认证用户，继续执行但不检查领取状态
        pass
    
    # 默认只返回活跃红包
    if status is None:
        status = RedPacketStatus.ACTIVE
    
    query = select(RedPacket).order_by(RedPacket.created_at.desc()).limit(limit)
    
    # 只返回公開紅包（chat_id 為 NULL）
    # 私密紅包（發送到指定群組或用戶的）不顯示在公開頁面
    query = query.where(RedPacket.chat_id.is_(None))
    
    # 过滤状态
    query = query.where(RedPacket.status == status)
    
    # 过滤过期红包（只过滤有过期时间的红包）
    query = query.where(
        (RedPacket.expires_at.is_(None)) | (RedPacket.expires_at > datetime.utcnow())
    )
    
    # 如果指定了 chat_id，則只返回該群組的公開紅包（通常不會用到）
    if chat_id:
        query = query.where(RedPacket.chat_id == chat_id)
    
    result = await db.execute(query)
    packets = result.scalars().all()
    
    # 如果用户已认证，检查每个红包是否已领取
    if current_user:
        packet_ids = [p.id for p in packets]
        if packet_ids:
            # 批量查询用户已领取的红包
            claims_result = await db.execute(
                select(RedPacketClaim.red_packet_id).where(
                    and_(
                        RedPacketClaim.red_packet_id.in_(packet_ids),
                        RedPacketClaim.user_id == current_user.id
                    )
                )
            )
            claimed_packet_ids = {row[0] for row in claims_result.all()}
            
            # 为每个红包设置 is_claimed 字段
            for packet in packets:
                packet.is_claimed = packet.id in claimed_packet_ids
    
    return packets


@router.get("/recommended", response_model=List[RedPacketResponse])
async def get_recommended_packets(
    request: Request,
    tg_id: Optional[int] = Depends(get_tg_id_from_header),
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session)
):
    """獲取推薦紅包（根據用戶活躍度）"""
    from sqlalchemy import case, func as sql_func
    
    # 尝试获取当前用户（可选，不强制认证）
    current_user = None
    try:
        from api.routers.auth import get_current_user_from_token
        from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
        security = HTTPBearer(auto_error=False)
        credentials: Optional[HTTPAuthorizationCredentials] = None
        try:
            credentials = await security(request)
        except:
            pass
        current_user = await get_current_user_from_token(
            request=request,
            credentials=credentials,
            x_telegram_init_data=request.headers.get("X-Telegram-Init-Data"),
            db=db
        )
    except:
        # 未认证用户，继续执行但不检查领取状态
        pass
    
    # 計算用戶活躍度
    activity_score = 0
    user = None
    if tg_id:
        result = await db.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()
        if user:
            # 活躍度計算：簽到天數 + 邀請人數 + 搶包次數 + 發包次數
            checkin_days = (user.total_checkin_count or 0) * 10
            invite_count = (user.invite_count or 0) * 5
            claim_count_result = await db.execute(
                select(sql_func.count(RedPacketClaim.id)).where(RedPacketClaim.user_id == user.id)
            )
            claim_count = claim_count_result.scalar() or 0
            send_count_result = await db.execute(
                select(sql_func.count(RedPacket.id)).where(RedPacket.sender_id == user.id)
            )
            send_count = send_count_result.scalar() or 0
            activity_score = checkin_days + invite_count + claim_count + send_count
    
    # 獲取推薦紅包（只返回公開紅包和任務紅包）
    query = select(RedPacket).where(
        RedPacket.status == RedPacketStatus.ACTIVE,
        RedPacket.expires_at > datetime.utcnow(),
        RedPacket.chat_id.is_(None)  # 只返回公開紅包
    )
    
    # 根據活躍度排序
    if activity_score > 50:
        # 活躍用戶：優先推薦高價值紅包和任務紅包
        query = query.order_by(
            case(
                (RedPacket.source_type == RedPacketSource.TASK, 0),
                (RedPacket.source_type == RedPacketSource.REWARD, 1),
                else_=2
            ),
            RedPacket.total_amount.desc(),
            RedPacket.created_at.desc()
        )
    else:
        # 新用戶：優先推薦任務紅包和公開紅包
        query = query.order_by(
            case(
                (RedPacket.source_type == RedPacketSource.TASK, 0),
                (RedPacket.visibility == RedPacketVisibility.PUBLIC, 1),
                else_=2
            ),
            RedPacket.created_at.desc()
        )
    
    result = await db.execute(query.limit(limit))
    packets = result.scalars().all()
    
    # 如果用户已认证，检查每个红包是否已领取
    claimed_packet_ids = set()
    if current_user:
        packet_ids = [p.id for p in packets]
        if packet_ids:
            # 批量查询用户已领取的红包
            claims_result = await db.execute(
                select(RedPacketClaim.red_packet_id).where(
                    and_(
                        RedPacketClaim.red_packet_id.in_(packet_ids),
                        RedPacketClaim.user_id == current_user.id
                    )
                )
            )
            claimed_packet_ids = {row[0] for row in claims_result.all()}
    
    # 轉換為響應格式
    responses = []
    for packet in packets:
        is_claimed = packet.id in claimed_packet_ids if current_user else None
        responses.append(RedPacketResponse(
            id=packet.id,
            uuid=packet.uuid,
            currency=packet.currency.value,
            packet_type=packet.packet_type.value,
            total_amount=float(packet.total_amount),
            total_count=packet.total_count,
            claimed_amount=float(packet.claimed_amount),
            claimed_count=packet.claimed_count,
            message=packet.message,
            status=packet.status.value,
            created_at=packet.created_at,
            message_sent=False,
            share_link=None,
            is_claimed=is_claimed
        ))
    
    return responses


@router.get("/{packet_uuid}", response_model=RedPacketResponse)
async def get_red_packet(
    request: Request,
    packet_uuid: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    獲取單個紅包信息（支持 UUID 或 ID）
    注意：此路由必須放在所有具體路徑（如 /list, /recommended）之後
    """
    # 尝试获取当前用户（可选，不强制认证）
    current_user = None
    try:
        from api.routers.auth import get_current_user_from_token
        from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
        security = HTTPBearer(auto_error=False)
        credentials: Optional[HTTPAuthorizationCredentials] = None
        try:
            credentials = await security(request)
        except:
            pass
        current_user = await get_current_user_from_token(
            request=request,
            credentials=credentials,
            x_telegram_init_data=request.headers.get("X-Telegram-Init-Data"),
            db=db
        )
    except:
        # 未认证用户，继续执行但不检查领取状态
        pass
    
    # 先嘗試用 uuid 查找
    result = await db.execute(select(RedPacket).where(RedPacket.uuid == packet_uuid))
    packet = result.scalar_one_or_none()
    
    # 如果找不到，嘗試用 id 查找（如果 packet_uuid 是數字）
    if not packet and packet_uuid.isdigit():
        packet_id = int(packet_uuid)
        result = await db.execute(select(RedPacket).where(RedPacket.id == packet_id))
        packet = result.scalar_one_or_none()
        if packet:
            logger.info(f"🔄 使用 ID 找到紅包: id={packet_id}, uuid={packet.uuid}")
    
    if not packet:
        logger.error(f"❌ 紅包不存在: packet_uuid={packet_uuid}")
        raise HTTPException(status_code=404, detail="Red packet not found")
    
    # 检查用户是否已领取
    is_claimed = None
    if current_user:
        claim_result = await db.execute(
            select(RedPacketClaim).where(
                and_(
                    RedPacketClaim.red_packet_id == packet.id,
                    RedPacketClaim.user_id == current_user.id
                )
            )
        )
        is_claimed = claim_result.scalar_one_or_none() is not None
    
    # 转换为响应格式
    return RedPacketResponse(
        id=packet.id,
        uuid=packet.uuid,
        currency=packet.currency.value,
        packet_type=packet.packet_type.value,
        total_amount=float(packet.total_amount),
        total_count=packet.total_count,
        claimed_amount=float(packet.claimed_amount),
        claimed_count=packet.claimed_count,
        message=packet.message,
        status=packet.status.value,
        created_at=packet.created_at,
        message_sent=False,
        share_link=None,
        is_claimed=is_claimed
    )

