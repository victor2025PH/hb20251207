"""
Lucky Red - 管理員處理器
"""
from telegram import Update
from telegram.ext import ContextTypes
from decimal import Decimal

from shared.config.settings import get_settings
from shared.database.connection import get_db
from shared.database.models import User

settings = get_settings()


def is_admin(user_id: int) -> bool:
    """檢查是否為管理員"""
    return user_id in settings.admin_id_list


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /admin 命令"""
    from bot.utils.i18n import t  # 在函数开头导入，确保始终可用
    user = update.effective_user
    
    user_id = user.id if user else None
    if not is_admin(user_id):
        await update.message.reply_text(t('no_admin_permission', user_id=user_id))
        return
    
    admin_panel_title = t('admin_panel_title', user_id=user_id)
    available_commands_label = t('available_commands_label', user_id=user_id)
    adjust_command_usage = t('adjust_command_usage', user_id=user_id)
    broadcast_command_usage = t('broadcast_command_usage', user_id=user_id)
    stats_command_usage = t('stats_command_usage', user_id=user_id)
    admin_backend_label = t('admin_backend_label', user_id=user_id)
    
    text = f"""
{admin_panel_title}

{available_commands_label}
{adjust_command_usage}
{broadcast_command_usage}
{stats_command_usage}

{admin_backend_label}
https://admin.usdt2026.cc
"""
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def adjust_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /adjust 命令 - 調整用戶餘額"""
    admin_user = update.effective_user
    
    admin_user_id = admin_user.id if admin_user else None
    if not is_admin(admin_user_id):
        from bot.utils.i18n import t
        await update.message.reply_text(t('no_admin_permission', user_id=admin_user_id))
        return
    
    args = context.args
    if len(args) < 2:
        from bot.utils.i18n import t
        adjust_usage = t('adjust_usage', user_id=admin_user_id)
        await update.message.reply_text(adjust_usage)
        return
    
    target = args[0].lstrip("@")
    try:
        amount = Decimal(args[1])
    except:
        from bot.utils.i18n import t
        await update.message.reply_text(t('invalid_amount_format', user_id=admin_user_id))
        return
    
    with get_db() as db:
        # 查找用戶
        if target.isdigit():
            db_user = db.query(User).filter(User.tg_id == int(target)).first()
        else:
            db_user = db.query(User).filter(User.username == target).first()
        
        if not db_user:
            from bot.utils.i18n import t
            await update.message.reply_text(t('user_not_found', user_id=admin_user_id, target=target))
            return
        
        old_balance = db_user.balance_usdt or Decimal(0)
        db_user.balance_usdt = old_balance + amount
        new_balance = db_user.balance_usdt
        
        db.commit()
    
    from bot.utils.i18n import t
    balance_adjusted_success = t('balance_adjusted_success', user_id=admin_user_id)
    user_label = t('user_label', user_id=admin_user_id, username=db_user.username or db_user.tg_id)
    change_label = t('change_label', user_id=admin_user_id, amount=f"{'+' if amount >= 0 else ''}{amount}")
    old_balance_label = t('old_balance_label', user_id=admin_user_id, old_balance=old_balance)
    new_balance_label = t('new_balance_label', user_id=admin_user_id, new_balance=new_balance)
    
    await update.message.reply_text(
        f"{balance_adjusted_success}\n\n"
        f"{user_label}\n"
        f"{change_label}\n"
        f"{old_balance_label}\n"
        f"{new_balance_label}"
    )


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /broadcast 命令 - 群發消息"""
    admin_user = update.effective_user
    
    admin_user_id = admin_user.id if admin_user else None
    if not is_admin(admin_user_id):
        from bot.utils.i18n import t
        await update.message.reply_text(t('no_admin_permission', user_id=admin_user_id))
        return
    
    if not context.args:
        await update.message.reply_text("用法: /broadcast <消息內容>")
        return
    
    message = " ".join(context.args)
    
    with get_db() as db:
        users = db.query(User).filter(User.is_banned == False).all()
        user_ids = [u.tg_id for u in users]
    
    success = 0
    failed = 0
    
    for user_id in user_ids:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 *公告*\n\n{message}",
                parse_mode="Markdown",
            )
            success += 1
        except:
            failed += 1
    
    await update.message.reply_text(
        f"✅ 群發完成\n\n成功: {success}\n失敗: {failed}"
    )

