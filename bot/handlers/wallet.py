"""
Lucky Red - 錢包處理器
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from shared.database.connection import get_db
from shared.database.models import User


async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /wallet 命令"""
    user = update.effective_user
    
    with get_db() as db:
        db_user = db.query(User).filter(User.tg_id == user.id).first()
        
        if not db_user:
            await update.message.reply_text("請先使用 /start 註冊")
            return
        
        usdt = float(db_user.balance_usdt or 0)
        ton = float(db_user.balance_ton or 0)
        stars = db_user.balance_stars or 0
        points = db_user.balance_points or 0
    
    text = f"""
💰 *我的錢包*

*餘額：*
• USDT: `{usdt:.4f}`
• TON: `{ton:.4f}`
• Stars: `{stars}`
• 積分: `{points}`

*等級：* Lv.{db_user.level}
*經驗：* {db_user.xp or 0} XP
"""
    
    keyboard = [
        [
            InlineKeyboardButton("💵 充值", callback_data="wallet:deposit"),
            InlineKeyboardButton("💸 提現", callback_data="wallet:withdraw"),
        ],
        [
            InlineKeyboardButton("📜 交易記錄", callback_data="wallet:history"),
        ],
    ]
    
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def wallet_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理錢包回調"""
    query = update.callback_query
    action = query.data.split(":")[1]
    
    await query.answer()
    
    if action == "view":
        await query.message.reply_text("請使用 /wallet 查看錢包")
    elif action == "deposit":
        await query.message.reply_text(
            "💵 *充值說明*\n\n"
            "請將 USDT (TRC20) 轉入以下地址：\n"
            "`TBD`\n\n"
            "轉賬後請聯繫客服確認",
            parse_mode="Markdown",
        )
    elif action == "withdraw":
        await query.message.reply_text(
            "💸 *提現說明*\n\n"
            "最低提現: 10 USDT\n"
            "請使用: /withdraw <金額> <地址>\n\n"
            "例如: /withdraw 10 TRC20地址",
            parse_mode="Markdown",
        )
    elif action == "history":
        await query.message.reply_text("📜 交易記錄功能開發中...")

