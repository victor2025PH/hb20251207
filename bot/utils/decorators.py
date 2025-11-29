"""
Lucky Red - 裝飾器工具
提供錯誤處理、性能追蹤等功能
"""
from functools import wraps
from typing import Callable, Any
import time
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes


def handle_errors(
    show_alert: bool = True,
    alert_message: str = "發生錯誤，請稍後再試"
):
    """
    統一錯誤處理裝飾器
    
    Args:
        show_alert: 是否顯示錯誤提示
        alert_message: 錯誤提示消息
    
    Usage:
        @handle_errors()
        async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            try:
                return await func(update, context, *args, **kwargs)
            except Exception as e:
                # 記錄詳細錯誤信息
                logger.error(
                    f"Error in {func.__name__}: {e}",
                    exc_info=True,
                    extra={
                        "function": func.__name__,
                        "user_id": update.effective_user.id if update.effective_user else None,
                        "chat_id": update.effective_chat.id if update.effective_chat else None,
                    }
                )
                
                # 嘗試向用戶顯示錯誤提示
                if show_alert:
                    try:
                        if update.callback_query:
                            await update.callback_query.answer(
                                alert_message,
                                show_alert=True
                            )
                        elif update.message:
                            await update.message.reply_text(
                                f"❌ {alert_message}\n\n錯誤詳情：{str(e)}"
                            )
                    except Exception as alert_error:
                        logger.warning(f"Failed to show error alert: {alert_error}")
                
                # 不重新拋出異常，避免中斷 Bot 運行
                return None
        
        return wrapper
    return decorator


def track_performance(log_threshold: float = 1.0):
    """
    性能追蹤裝飾器
    
    Args:
        log_threshold: 記錄閾值（秒），超過此時間的操作會被記錄
    
    Usage:
        @track_performance(log_threshold=0.5)
        async def slow_operation():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start
                
                if duration >= log_threshold:
                    logger.info(
                        f"{func.__name__} took {duration:.2f}s",
                        extra={
                            "function": func.__name__,
                            "duration": duration,
                            "threshold": log_threshold
                        }
                    )
                
                return result
            except Exception as e:
                duration = time.time() - start
                logger.error(
                    f"{func.__name__} failed after {duration:.2f}s: {e}",
                    exc_info=True,
                    extra={
                        "function": func.__name__,
                        "duration": duration,
                        "error": str(e)
                    }
                )
                raise
        
        return wrapper
    return decorator


def require_user(func: Callable) -> Callable:
    """
    要求用戶已註冊的裝飾器
    
    Usage:
        @require_user
        async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # 這裡可以安全地使用 context.user_data['db_user']
            ...
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        from shared.database.connection import get_db
        from shared.database.models import User
        
        user = update.effective_user
        if not user:
            if update.callback_query:
                await update.callback_query.answer("無法獲取用戶信息", show_alert=True)
            return None
        
        # 檢查緩存
        if 'db_user' not in context.user_data:
            with get_db() as db:
                db_user = db.query(User).filter(User.tg_id == user.id).first()
                if not db_user:
                    if update.callback_query:
                        await update.callback_query.answer(
                            "請先使用 /start 註冊",
                            show_alert=True
                        )
                    elif update.message:
                        await update.message.reply_text("請先使用 /start 註冊")
                    return None
                context.user_data['db_user'] = db_user
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper
