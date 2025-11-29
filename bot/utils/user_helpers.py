"""
Lucky Red - 用戶輔助工具
提供統一的用戶獲取和管理功能
"""
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from shared.database.connection import get_db
from shared.database.models import User
from bot.utils.cache import UserCache
from loguru import logger


async def get_or_create_user(
    tg_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    use_cache: bool = True
) -> Optional[User]:
    """
    獲取或創建用戶（帶緩存）
    
    Args:
        tg_id: Telegram 用戶 ID
        username: 用戶名（可選）
        first_name: 名字（可選）
        last_name: 姓氏（可選）
        use_cache: 是否使用緩存
    
    Returns:
        用戶對象或 None
    """
    with get_db() as db:
        # 嘗試從緩存獲取
        if use_cache:
            cached_user = UserCache.get_user(tg_id, db)
            if cached_user:
                return cached_user
        
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
        
        # 更新用戶信息（如果提供）
        if username and db_user.username != username:
            db_user.username = username
        if first_name and db_user.first_name != first_name:
            db_user.first_name = first_name
        if last_name and db_user.last_name != last_name:
            db_user.last_name = last_name
        
        if username or first_name or last_name:
            db.commit()
            # 清除緩存以確保數據最新
            if use_cache:
                UserCache.invalidate(tg_id)
        
        # 在返回前訪問常用屬性，確保它們被加載到內存中
        # 然後將對象從會話中分離，這樣即使會話關閉也可以訪問已加載的屬性
        try:
            _ = db_user.id
            _ = db_user.tg_id
            _ = db_user.username
            _ = db_user.first_name
            _ = db_user.last_name
            _ = db_user.level
            _ = db_user.balance_usdt
            _ = db_user.balance_ton
            _ = db_user.balance_points
            # 將對象從會話中分離
            db.expunge(db_user)
        except Exception as e:
            logger.warning(f"Error expunging user {tg_id}: {e}")
            # 如果分離失敗，至少確保基本屬性已加載
        
        return db_user


async def get_user_from_update(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    use_cache: bool = True
) -> Optional[User]:
    """
    從 Update 對象獲取用戶
    
    Args:
        update: Telegram Update 對象
        context: Bot 上下文
        use_cache: 是否使用緩存
    
    Returns:
        用戶對象或 None
    """
    user = update.effective_user
    if not user:
        return None
    
    # 檢查上下文緩存
    if 'db_user' in context.user_data:
        return context.user_data['db_user']
    
    # 獲取或創建用戶
    db_user = await get_or_create_user(
        tg_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        use_cache=use_cache
    )
    
    # 保存到上下文
    if db_user:
        context.user_data['db_user'] = db_user
    
    return db_user


def require_user_registered(func):
    """
    裝飾器：要求用戶已註冊
    
    Usage:
        @require_user_registered
        async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # 這裡可以安全地使用 context.user_data['db_user']
            db_user = context.user_data['db_user']
            ...
    """
    from functools import wraps
    
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        db_user = await get_user_from_update(update, context)
        
        if not db_user:
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
