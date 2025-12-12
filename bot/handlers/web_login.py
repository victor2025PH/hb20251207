"""
Web 登入處理器

實現 /web_login 命令
生成一次性 Magic Link 讓用戶在瀏覽器中登入
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from sqlalchemy import select
from loguru import logger

from shared.database.connection import AsyncSessionLocal
from shared.database.models import User, MagicLinkToken
from shared.config.settings import get_settings

settings = get_settings()

# ==================== 配置 ====================

# Magic Link 有效期（分鐘）
MAGIC_LINK_EXPIRE_MINUTES = 5

# Web 域名（從設置中獲取或使用默認值）
WEB_DOMAIN = getattr(settings, 'WEB_DOMAIN', None) or getattr(settings, 'MINIAPP_DOMAIN', 'app.yoursite.com')


# ==================== 處理函數 ====================

async def web_login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    處理 /web_login 命令
    
    為用戶生成一次性登入連結，用於在瀏覽器中訪問 H5 版本
    """
    user = update.effective_user
    if not user:
        return
    
    tg_id = user.id
    
    async with AsyncSessionLocal() as db:
        # 查找用戶
        result = await db.execute(
            select(User).where(User.tg_id == tg_id)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            from bot.utils.i18n import t
            await update.message.reply_text(
                t('not_registered_yet', user=None) if t('not_registered_yet', user=None) != 'not_registered_yet' else "❌ 您還沒有註冊，請先使用機器人的其他功能完成註冊。"
            )
            return
        
        if db_user.is_banned:
            from bot.utils.i18n import t
            await update.message.reply_text(
                t('account_banned', user=db_user)
            )
            return
        
        # 生成安全令牌
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=MAGIC_LINK_EXPIRE_MINUTES)
        
        # 存儲令牌
        magic_link = MagicLinkToken(
            user_id=db_user.id,
            tg_id=tg_id,
            token=token,
            expires_at=expires_at,
        )
        db.add(magic_link)
        await db.commit()
        
        # 構建登入連結
        login_url = f"https://{WEB_DOMAIN}/auth/magic?token={token}"
        
        logger.info(f"Magic link generated for user {tg_id}")
        
        # 發送訊息
        from bot.utils.i18n import t
        login_now_button = t('login_now_button', user=db_user)
        copy_link_button = t('copy_link_button', user=db_user)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(login_now_button, url=login_url)],
            [InlineKeyboardButton(copy_link_button, callback_data=f"copy_link:{token[:10]}")],
        ])
        
        message_text = (
            "🔐 **網頁版登入連結**\n\n"
            f"點擊下方按鈕在瀏覽器中登入：\n\n"
            f"⏱ 有效期：**{MAGIC_LINK_EXPIRE_MINUTES} 分鐘**\n"
            f"🔒 此連結只能使用一次\n\n"
            "💡 **提示：**\n"
            "• 在網頁版中您可以進行充值、提現等操作\n"
            "• 您的餘額會自動同步\n"
            "• 連結失效後可再次使用 /web\\_login 獲取新連結"
        )
        
        await update.message.reply_text(
            message_text,
            parse_mode="Markdown",
            reply_markup=keyboard,
        )


async def web_login_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    處理 Magic Link 相關的回調
    """
    query = update.callback_query
    if not query:
        return
    
    data = query.data
    
    if data.startswith("copy_link:"):
        # 提示用戶如何複製連結
        await query.answer(
            "請長按上方的「立即登入」按鈕來複製連結",
            show_alert=True
        )


async def web_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    處理 /web 命令（/web_login 的簡短版本）
    """
    await web_login_command(update, context)


# ==================== 輔助命令 ====================

async def sync_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    處理 /sync 命令
    
    顯示帳戶同步狀態和說明
    """
    user = update.effective_user
    if not user:
        return
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.tg_id == user.id)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            await update.message.reply_text(
                "❌ 找不到您的帳戶信息。"
            )
            return
        
        # 構建同步狀態訊息
        from bot.utils.i18n import t
        account_sync_status = t('account_sync_status', user=db_user)
        user_id_label_sync = t('user_id_label_sync', user=db_user, tg_id=db_user.tg_id)
        usdt_balance_label_sync = t('usdt_balance_label_sync', user=db_user, balance=float(db_user.balance_usdt or 0))
        ton_balance_label_sync = t('ton_balance_label_sync', user=db_user, balance=float(db_user.balance_ton or 0))
        stars_balance_label_sync = t('stars_balance_label_sync', user=db_user, balance=db_user.balance_stars or 0)
        points_balance_label_sync = t('points_balance_label_sync', user=db_user, balance=db_user.balance_points or 0)
        account_auto_sync = t('account_auto_sync', user=db_user)
        use_web_login_hint = t('use_web_login_hint', user=db_user)
        
        message_text = (
            f"{account_sync_status}\n\n"
            f"{user_id_label_sync}\n"
            f"{usdt_balance_label_sync}\n"
            f"{ton_balance_label_sync}\n"
            f"{stars_balance_label_sync}\n"
            f"{points_balance_label_sync}\n\n"
            f"{account_auto_sync}\n\n"
            f"{use_web_login_hint}"
        )
        
        await update.message.reply_text(
            message_text,
            parse_mode="Markdown",
        )


# ==================== 處理器註冊 ====================

def get_handlers():
    """
    獲取所有處理器
    
    Returns:
        list: 處理器列表
    """
    return [
        CommandHandler("web_login", web_login_command),
        CommandHandler("web", web_command),
        CommandHandler("sync", sync_command),
    ]


# 用於直接導入的處理器
web_login_handler = CommandHandler("web_login", web_login_command)
web_handler = CommandHandler("web", web_command)
sync_handler = CommandHandler("sync", sync_command)
