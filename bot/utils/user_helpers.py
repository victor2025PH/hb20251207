"""
Lucky Red - 用戶輔助工具
提供統一的用戶獲取和管理功能（只返回 user_id，不返回 ORM 對象）
"""
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from shared.database.connection import get_db
from shared.database.models import User
from bot.utils.cache import UserCache
from loguru import logger


async def get_or_create_user_id(
    tg_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    use_cache: bool = True
) -> Optional[int]:
    """
    獲取或創建用戶，返回 user_id（不返回 ORM 對象）
    
    Args:
        tg_id: Telegram 用戶 ID
        username: 用戶名（可選）
        first_name: 名字（可選）
        last_name: 姓氏（可選）
        use_cache: 是否使用緩存
    
    Returns:
        用戶 ID 或 None
    """
    with get_db() as db:
        # 嘗試從緩存獲取
        if use_cache:
            cached_data = UserCache.get_user_data(tg_id, db)
            if cached_data:
                return cached_data['id']
        
        # 從數據庫查詢
        db_user = db.query(User).filter(User.tg_id == tg_id).first()
        
        if not db_user:
            # 創建新用戶
            db_user = User(
                tg_id=tg_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"Created new user: {tg_id}")
            # 清除緩存
            if use_cache:
                UserCache.invalidate(tg_id)
            return db_user.id
        
        # 更新用戶信息（如果提供）
        updated = False
        if username and db_user.username != username:
            db_user.username = username
            updated = True
        if first_name and db_user.first_name != first_name:
            db_user.first_name = first_name
            updated = True
        if last_name and db_user.last_name != last_name:
            db_user.last_name = last_name
            updated = True
        
        if updated:
            db.commit()
            # 清除緩存以確保數據最新
            if use_cache:
                UserCache.invalidate(tg_id)
        
        return db_user.id


async def get_user_id_from_update(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    use_cache: bool = True
) -> Optional[int]:
    """
    從 Update 對象獲取用戶 ID（不返回 ORM 對象）
    
    Args:
        update: Telegram Update 對象
        context: Bot 上下文
        use_cache: 是否使用緩存
    
    Returns:
        用戶 ID 或 None
    """
    user = update.effective_user
    if not user:
        return None
    
    # 檢查上下文緩存（只存儲 user_id，不存儲 ORM 對象）
    if 'user_id' in context.user_data:
        return context.user_data['user_id']
    
    # 獲取或創建用戶
    user_id = await get_or_create_user_id(
        tg_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        use_cache=use_cache
    )
    
    # 保存到上下文（只存儲 user_id）
    if user_id:
        context.user_data['user_id'] = user_id
    
    return user_id


def require_user_registered(func):
    """
    裝飾器：要求用戶已註冊
    
    Usage:
        @require_user_registered
        async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # 這裡可以安全地使用 context.user_data['user_id']
            user_id = context.user_data['user_id']
            ...
    """
    from functools import wraps
    
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = await get_user_id_from_update(update, context)
        
        if not user_id:
            if update.callback_query:
                await update.callback_query.answer(
                    "請先使用 /start 註冊",
                    show_alert=True
                )
            elif update.message:
                await update.message.reply_text("請先使用 /start 註冊")
            return None
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper


# 向後兼容的函數（已廢棄，將逐步移除）
async def get_or_create_user(
    tg_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    use_cache: bool = True
) -> Optional[int]:
    """
    已廢棄：請使用 get_or_create_user_id
    為了向後兼容，此函數現在返回 user_id 而不是 User 對象
    """
    logger.warning("get_or_create_user is deprecated, use get_or_create_user_id instead")
    return await get_or_create_user_id(tg_id, username, first_name, last_name, use_cache)


async def get_user_from_update(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    use_cache: bool = True
) -> Optional[int]:
    """
    已廢棄：請使用 get_user_id_from_update
    為了向後兼容，此函數現在返回 user_id 而不是 User 對象
    """
    logger.warning("get_user_from_update is deprecated, use get_user_id_from_update instead")
    return await get_user_id_from_update(update, context, use_cache)
