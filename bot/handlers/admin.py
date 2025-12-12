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
    
    if not is_admin(user.id):
        await update.message.reply_text(t('no_admin_permission', user=None) if t('no_admin_permission', user=None) != 'no_admin_permission' else "⛔ 你沒有管理員權限")
        return
    admin_panel_title = t('admin_panel_title', user=user) if t('admin_panel_title', user=user) != 'admin_panel_title' else "⚙️ *管理員面板*"
    available_commands_label = t('available_commands_label', user=user) if t('available_commands_label', user=user) != 'available_commands_label' else "*可用命令：*"
    adjust_command_usage = t('adjust_command_usage', user=user) if t('adjust_command_usage', user=user) != 'adjust_command_usage' else "/adjust <@用戶名或ID> <金額> - 調整餘額"
    broadcast_command_usage = t('broadcast_command_usage', user=user) if t('broadcast_command_usage', user=user) != 'broadcast_command_usage' else "/broadcast <消息> - 群發消息"
    stats_command_usage = t('stats_command_usage', user=user) if t('stats_command_usage', user=user) != 'stats_command_usage' else "/stats - 查看統計"
    admin_backend_label = t('admin_backend_label', user=user) if t('admin_backend_label', user=user) != 'admin_backend_label' else "*管理後台：*"
    
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
    
    if not is_admin(admin_user.id):
        from bot.utils.i18n import t
        await update.message.reply_text(t('no_admin_permission', user=None) if t('no_admin_permission', user=None) != 'no_admin_permission' else "⛔ 你沒有管理員權限")
        return
    
    args = context.args
    if len(args) < 2:
        from bot.utils.i18n import t
        adjust_usage = t('adjust_usage', user=admin_user) if t('adjust_usage', user=admin_user) != 'adjust_usage' else "用法: /adjust <@用戶名或ID> <金額>\n例如: /adjust @username 100\n或: /adjust 123456789 -50"
        await update.message.reply_text(adjust_usage)
        return
    
    target = args[0].lstrip("@")
    try:
        amount = Decimal(args[1])
    except:
        from bot.utils.i18n import t
        await update.message.reply_text(t('invalid_amount_format', user=admin_user) if t('invalid_amount_format', user=admin_user) != 'invalid_amount_format' else "金額格式錯誤")
        return
    
    with get_db() as db:
        # 查找用戶
        if target.isdigit():
            db_user = db.query(User).filter(User.tg_id == int(target)).first()
        else:
            db_user = db.query(User).filter(User.username == target).first()
        
        if not db_user:
            from bot.utils.i18n import t
            await update.message.reply_text(t('user_not_found', user=admin_user, target=target) if t('user_not_found', user=admin_user) != 'user_not_found' else f"找不到用戶: {target}")
            return
        
        old_balance = db_user.balance_usdt or Decimal(0)
        db_user.balance_usdt = old_balance + amount
        new_balance = db_user.balance_usdt
        
        db.commit()
    
    from bot.utils.i18n import t
    balance_adjusted_success = t('balance_adjusted_success', user=admin_user)
    user_label = t('user_label', user=admin_user, username=db_user.username or db_user.tg_id)
    change_label = t('change_label', user=admin_user, amount=f"{'+' if amount >= 0 else ''}{amount}")
    old_balance_label = t('old_balance_label', user=admin_user, old_balance=old_balance)
    new_balance_label = t('new_balance_label', user=admin_user, new_balance=new_balance)
    
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
    
    if not is_admin(admin_user.id):
        from bot.utils.i18n import t
        await update.message.reply_text(t('no_admin_permission', user=None) if t('no_admin_permission', user=None) != 'no_admin_permission' else "⛔ 你沒有管理員權限")
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

