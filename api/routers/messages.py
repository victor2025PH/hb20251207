"""
消息相關 API
"""

from datetime import datetime
from typing import Optional, List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from loguru import logger

from shared.database.connection import get_db_session
from shared.database.models import (
    User,
    Message,
    MessageType,
    MessageStatus,
    UserNotificationSettings,
)
from api.utils.telegram_auth import get_tg_id_from_header
from api.routers.auth import get_current_user_from_token

router = APIRouter()


# Pydantic 模型
class MessageResponse(BaseModel):
    id: int
    message_type: str
    status: str
    title: Optional[str]
    content: str
    action_url: Optional[str]
    source: Optional[str]
    source_name: Optional[str]
    can_reply: bool
    meta_data: Optional[dict]  # 使用 meta_data 而不是 metadata
    created_at: datetime
    read_at: Optional[datetime]
    reply_to_id: Optional[int]

    model_config = {"from_attributes": True}


class MessageListResponse(BaseModel):
    total: int
    page: int
    limit: int
    unread_count: int
    messages: List[MessageResponse]


class UnreadCountResponse(BaseModel):
    unread_count: int
    unread_by_type: dict


class NotificationSettingsResponse(BaseModel):
    notification_method: str
    enable_system: bool
    enable_redpacket: bool
    enable_balance: bool
    enable_activity: bool
    enable_miniapp: bool
    enable_telegram: bool


class UpdateNotificationSettingsRequest(BaseModel):
    notification_method: Optional[str] = None
    enable_system: Optional[bool] = None
    enable_redpacket: Optional[bool] = None
    enable_balance: Optional[bool] = None
    enable_activity: Optional[bool] = None
    enable_miniapp: Optional[bool] = None
    enable_telegram: Optional[bool] = None


class ReplyRequest(BaseModel):
    content: str


# WebSocket 連接管理器
class ConnectionManager:
    """管理 WebSocket 連接"""

    def __init__(self):
        # user_id -> WebSocket
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(
            f"WebSocket connected: user_id={user_id}, total={len(self.active_connections)}"
        )

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(
                f"WebSocket disconnected: user_id={user_id}, total={len(self.active_connections)}"
            )

    async def send_personal_message(self, message: dict, user_id: int):
        """發送消息給特定用戶"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
                return True
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                self.disconnect(user_id)
                return False
        return False

    def is_user_online(self, user_id: int) -> bool:
        """檢查用戶是否在線"""
        return user_id in self.active_connections


# 全局連接管理器
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 連接端點（支持 JWT Token 和 Telegram initData）"""
    # 從查詢參數或請求頭獲取認證信息
    query_params = dict(websocket.query_params)
    user_id = None

    # 檢測認證信息
    token = query_params.get("token") or websocket.headers.get(
        "Authorization", ""
    ).replace("Bearer ", "")
    init_data_str = query_params.get("init_data") or websocket.headers.get(
        "X-Telegram-Init-Data"
    )

    has_initData = bool(init_data_str)
    has_jwt_token = bool(token)

    logger.info(
        f"[WS] New connection on /ws, has_initData={has_initData}, has_jwt={has_jwt_token}"
    )

    # Step 1: 嘗試 Telegram 認證（如果有 initData）
    if has_initData:
        logger.info("[WS] Attempting Telegram authentication")
        try:
            from api.utils.telegram_auth import (
                parse_telegram_init_data,
                verify_telegram_init_data,
            )
            from api.services.identity_service import IdentityService
            from shared.database.connection import AsyncSessionLocal
            from shared.config.settings import get_settings

            settings = get_settings()

            # 驗證 initData 的 hash（如果 BOT_TOKEN 配置了則驗證）
            should_verify = bool(settings.BOT_TOKEN)
            if should_verify and not verify_telegram_init_data(init_data_str):
                logger.warning("[WS] Telegram initData hash 驗證失敗")
                user_id = None
            else:
                # 解析 initData
                user_data = parse_telegram_init_data(init_data_str)
                if user_data and "id" in user_data:
                    tg_id = int(user_data["id"])
                    logger.info(f"[WS] 從 initData 中提取到 tg_id: {tg_id}")

                    # 獲取或創建用戶
                    db = AsyncSessionLocal()
                    try:
                        user = await IdentityService.get_or_create_user_by_identity(
                            db=db,
                            provider="telegram",
                            provider_user_id=str(tg_id),
                            provider_data={
                                "id": tg_id,
                                "username": user_data.get("username"),
                                "first_name": user_data.get("first_name"),
                                "last_name": user_data.get("last_name"),
                                "language_code": user_data.get(
                                    "language_code", "zh-TW"
                                ),
                            },
                        )
                        user_id = user.id
                        logger.info(
                            f"[WS] Authenticated WebSocket user_id={user_id} via Telegram"
                        )
                    except Exception as e:
                        logger.error(
                            f"[WS] Failed to get/create user: {e}", exc_info=True
                        )
                        user_id = None
                    finally:
                        await db.close()
                else:
                    logger.warning("[WS] Telegram initData 中沒有用戶信息")
                    user_id = None
        except Exception as e:
            logger.error(f"[WS] Telegram authentication failed: {e}", exc_info=True)
            user_id = None

        # 如果 Telegram 認證失敗，嘗試降級到 JWT（如果有 JWT token）
        if not user_id and has_jwt_token:
            logger.info(
                "[WS] Telegram authentication failed, falling back to JWT token auth"
            )
            try:
                from api.routers.auth import decode_jwt_token
                from shared.database.connection import AsyncSessionLocal

                user_id = decode_jwt_token(token)
                db = AsyncSessionLocal()
                try:
                    result = await db.execute(select(User).where(User.id == user_id))
                    user = result.scalar_one_or_none()
                    if user:
                        logger.info(
                            f"[WS] Authenticated WebSocket user_id={user_id} via JWT"
                        )
                    else:
                        logger.warning(f"[WS] JWT user not found: user_id={user_id}")
                        user_id = None
                finally:
                    await db.close()
            except Exception as e:
                logger.error(f"[WS] JWT token validation failed: {e}")
                user_id = None

    # Step 2: 如果沒有 Telegram initData，嘗試 JWT Token
    elif has_jwt_token:
        logger.info("[WS] No Telegram initData, falling back to JWT token auth")
        try:
            from api.routers.auth import decode_jwt_token
            from shared.database.connection import AsyncSessionLocal

            user_id = decode_jwt_token(token)
            db = AsyncSessionLocal()
            try:
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
                if user:
                    logger.info(
                        f"[WS] Authenticated WebSocket user_id={user_id} via JWT"
                    )
                else:
                    logger.warning(f"[WS] JWT user not found: user_id={user_id}")
                    user_id = None
            finally:
                await db.close()
        except Exception as e:
            logger.error(f"[WS] JWT token validation failed: {e}")
            user_id = None

    # 如果兩種認證方式都失敗，關閉連接
    if not user_id:
        logger.warning("[WS] Closing WebSocket: auth failed")
        try:
            await websocket.close(code=1008, reason="Unauthorized")
        except Exception as e:
            logger.error(f"[WS] Error closing unauthorized connection: {e}")
        return

    # 接受連接並建立會話
    try:
        await websocket.accept()
        logger.info(f"[WS] Connection accepted for user_id={user_id}")
    except Exception as e:
        logger.error(f"[WS] Failed to accept connection: {e}")
        return

    # 建立連接管理器會話
    await manager.connect(websocket, user_id)
    logger.info(
        f"[WS] WebSocket connection established and kept alive for user_id={user_id}"
    )

    try:
        while True:
            # 接收心跳消息或其他消息
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
                    logger.debug(f"[WS] Heartbeat received from user {user_id}")
                else:
                    logger.debug(f"[WS] Received message from user {user_id}: {data}")
            except WebSocketDisconnect:
                # 正常断开连接
                logger.info(f"[WS] Client disconnected user_id={user_id}")
                break
            except Exception as e:
                logger.error(
                    f"[WS] Error receiving message from user {user_id}: {e}",
                    exc_info=True,
                )
                # 继续循环，尝试接收下一条消息
                continue
    except WebSocketDisconnect:
        logger.info(f"[WS] Client disconnected user_id={user_id}")
    except Exception as e:
        logger.error(f"[WS] Unexpected error for user_id={user_id}: {e}", exc_info=True)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass
    finally:
        manager.disconnect(user_id)
        logger.info(f"[WS] Cleaned up connection for user_id={user_id}")


@router.get("/", response_model=MessageListResponse)
async def get_messages(
    message_type: Optional[MessageType] = Query(None),
    status: Optional[MessageStatus] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """獲取消息列表（支持 JWT Token 和 Telegram initData）"""
    user = current_user

    # 構建查詢
    query = select(Message).where(
        and_(Message.user_id == user.id, Message.status != MessageStatus.DELETED)
    )

    if message_type:
        query = query.where(Message.message_type == message_type)

    if status:
        query = query.where(Message.status == status)
    else:
        # 默認只返回未讀消息
        query = query.where(Message.status == MessageStatus.UNREAD)

    # 獲取總數
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分頁
    query = query.order_by(Message.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    # 執行查詢
    result = await db.execute(query)
    messages = result.scalars().all()

    # 獲取未讀數量
    unread_query = select(func.count()).where(
        and_(
            Message.user_id == user.id,
            Message.status == MessageStatus.UNREAD,
            Message.status != MessageStatus.DELETED,
        )
    )
    unread_result = await db.execute(unread_query)
    unread_count = unread_result.scalar() or 0

    return MessageListResponse(
        total=total,
        page=page,
        limit=limit,
        unread_count=unread_count,
        messages=[MessageResponse.model_validate(msg) for msg in messages],
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """獲取未讀消息數量（支持 JWT Token 和 Telegram initData）"""
    user = current_user

    # 獲取總未讀數量
    unread_query = select(func.count()).where(
        and_(
            Message.user_id == user.id,
            Message.status == MessageStatus.UNREAD,
            Message.status != MessageStatus.DELETED,
        )
    )
    unread_result = await db.execute(unread_query)
    total_unread = unread_result.scalar() or 0

    # 按類型統計
    unread_by_type = {}
    for msg_type in MessageType:
        type_query = select(func.count()).where(
            and_(
                Message.user_id == user.id,
                Message.message_type == msg_type,
                Message.status == MessageStatus.UNREAD,
                Message.status != MessageStatus.DELETED,
            )
        )
        type_result = await db.execute(type_query)
        count = type_result.scalar() or 0
        if count > 0:
            unread_by_type[msg_type.value] = count

    return UnreadCountResponse(unread_count=total_unread, unread_by_type=unread_by_type)


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """獲取單條消息詳情（支持 JWT Token 和 Telegram initData）"""
    user = current_user

    # 獲取消息
    result = await db.execute(
        select(Message).where(
            and_(Message.id == message_id, Message.user_id == user.id)
        )
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return MessageResponse.model_validate(message)


@router.put("/{message_id}/read")
async def mark_as_read(
    message_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """標記消息為已讀（支持 JWT Token 和 Telegram initData）"""
    user = current_user

    # 獲取消息
    result = await db.execute(
        select(Message).where(
            and_(Message.id == message_id, Message.user_id == user.id)
        )
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.status = MessageStatus.READ
    message.read_at = datetime.utcnow()
    await db.commit()

    return {"success": True}


@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """刪除消息（支持 JWT Token 和 Telegram initData）"""
    user = current_user

    # 獲取消息
    result = await db.execute(
        select(Message).where(
            and_(Message.id == message_id, Message.user_id == user.id)
        )
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.status = MessageStatus.DELETED
    message.deleted_at = datetime.utcnow()
    await db.commit()

    return {"success": True}


@router.post("/{message_id}/reply", response_model=MessageResponse)
async def reply_message(
    message_id: int,
    request: ReplyRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_from_token),
):
    """回復消息（支持 JWT Token 和 Telegram initData）"""
    user = current_user

    # 獲取原消息
    result = await db.execute(
        select(Message).where(
            and_(
                Message.id == message_id,
                Message.user_id == user.id,
                Message.can_reply == True,
            )
        )
    )
    original_message = result.scalar_one_or_none()
    if not original_message:
        raise HTTPException(status_code=404, detail="Message not found or cannot reply")

    # 創建回復消息
    reply = Message(
        user_id=user.id,
        message_type=MessageType.MINIAPP,
        status=MessageStatus.UNREAD,
        title=f"回復: {original_message.title or '消息'}",
        content=request.content,
        reply_to_id=message_id,
        can_reply=False,
        source="user",
        source_name=user.first_name or user.username or "用戶",
    )
    db.add(reply)
    await db.commit()
    await db.refresh(reply)

    return MessageResponse.model_validate(reply)


@router.get("/settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    tg_id: Optional[int] = Depends(get_tg_id_from_header),
    db: AsyncSession = Depends(get_db_session),
):
    """獲取通知設置"""
    if not tg_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 獲取用戶
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 獲取或創建設置
    result = await db.execute(
        select(UserNotificationSettings).where(
            UserNotificationSettings.user_id == user.id
        )
    )
    settings = result.scalar_one_or_none()

    if not settings:
        # 創建默認設置
        settings = UserNotificationSettings(user_id=user.id, notification_method="both")
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return NotificationSettingsResponse.model_validate(settings)


@router.put("/settings", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    request: UpdateNotificationSettingsRequest,
    tg_id: Optional[int] = Depends(get_tg_id_from_header),
    db: AsyncSession = Depends(get_db_session),
):
    """更新通知設置"""
    if not tg_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 獲取用戶
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 獲取或創建設置
    result = await db.execute(
        select(UserNotificationSettings).where(
            UserNotificationSettings.user_id == user.id
        )
    )
    settings = result.scalar_one_or_none()

    if not settings:
        settings = UserNotificationSettings(user_id=user.id)
        db.add(settings)

    # 更新設置
    if request.notification_method is not None:
        settings.notification_method = request.notification_method
    if request.enable_system is not None:
        settings.enable_system = request.enable_system
    if request.enable_redpacket is not None:
        settings.enable_redpacket = request.enable_redpacket
    if request.enable_balance is not None:
        settings.enable_balance = request.enable_balance
    if request.enable_activity is not None:
        settings.enable_activity = request.enable_activity
    if request.enable_miniapp is not None:
        settings.enable_miniapp = request.enable_miniapp
    if request.enable_telegram is not None:
        settings.enable_telegram = request.enable_telegram

    settings.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(settings)

    return NotificationSettingsResponse.model_validate(settings)
