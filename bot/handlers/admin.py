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
    user = update.effective_user
    
    if not is_admin(user.id):
        await update.message.reply_text("⛔ 你沒有管理員權限")
        return
    
    text = """
⚙️ *管理員面板*

*可用命令：*
/adjust <@用戶名或ID> <金額> - 調整餘額
/broadcast <消息> - 群發消息
/stats - 查看統計

*管理後台：*
https://admin.usdt2026.cc
"""
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def adjust_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /adjust 命令 - 調整用戶餘額"""
    admin_user = update.effective_user
    
    if not is_admin(admin_user.id):
        await update.message.reply_text("⛔ 你沒有管理員權限")
        return
    
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "用法: /adjust <@用戶名或ID> <金額>\n"
            "例如: /adjust @username 100\n"
            "或: /adjust 123456789 -50"
        )
        return
    
    target = args[0].lstrip("@")
    try:
        amount = Decimal(args[1])
    except:
        await update.message.reply_text("金額格式錯誤")
        return
    
    with get_db() as db:
        # 查找用戶
        if target.isdigit():
            db_user = db.query(User).filter(User.tg_id == int(target)).first()
        else:
            db_user = db.query(User).filter(User.username == target).first()
        
        if not db_user:
            await update.message.reply_text(f"找不到用戶: {target}")
            return
        
        old_balance = db_user.balance_usdt or Decimal(0)
        db_user.balance_usdt = old_balance + amount
        new_balance = db_user.balance_usdt
        
        db.commit()
    
    await update.message.reply_text(
        f"✅ 餘額調整成功\n\n"
        f"用戶: @{db_user.username or db_user.tg_id}\n"
        f"變動: {'+' if amount >= 0 else ''}{amount} USDT\n"
        f"原餘額: {old_balance} USDT\n"
        f"新餘額: {new_balance} USDT"
    )


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /broadcast 命令 - 群發消息"""
    admin_user = update.effective_user
    
    if not is_admin(admin_user.id):
        await update.message.reply_text("⛔ 你沒有管理員權限")
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

