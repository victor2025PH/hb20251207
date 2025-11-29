"""
Lucky Red - 錢包處理器
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from loguru import logger
from decimal import Decimal
from datetime import datetime, timedelta
import httpx

from shared.config.settings import get_settings
from shared.database.connection import get_db
from shared.database.models import User, Transaction, CurrencyType
from bot.keyboards import (
    get_wallet_menu, get_back_to_wallet, get_currency_selection,
    get_exchange_menu, get_confirm_cancel
)

settings = get_settings()
API_BASE = settings.api_url  # 從配置讀取 API URL


async def wallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /wallet 命令"""
    from bot.utils.user_helpers import get_user_from_update
    
    # 獲取用戶（帶緩存）
    db_user = await get_user_from_update(update, context)
    if not db_user:
        await update.message.reply_text("請先使用 /start 註冊")
        return
    
    # 重新查詢用戶以確保數據最新（特別是餘額）
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await update.message.reply_text("發生錯誤，請稍後再試")
            return
        
        usdt = float(user.balance_usdt or 0)
        ton = float(user.balance_ton or 0)
        stars = user.balance_stars or 0
        points = user.balance_points or 0
        level = user.level
        xp = user.xp or 0
    
    text = f"""
💰 *我的錢包*

*餘額：*
• USDT: `{usdt:.4f}`
• TON: `{ton:.4f}`
• Stars: `{stars}`
• 能量: `{points}`

*等級：* Lv.{level}
*經驗：* {xp} XP

請選擇操作：
"""
    
    from bot.keyboards import get_wallet_menu
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_wallet_menu(),
    )


async def wallet_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理錢包回調"""
    from bot.utils.user_helpers import get_user_from_update
    
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    
    # 獲取用戶（帶緩存）
    db_user = await get_user_from_update(update, context)
    if not db_user:
        await query.message.reply_text("請先使用 /start 註冊")
        return
    
    # 重新查詢用戶以確保數據最新（特別是餘額）
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
    
    if action == "deposit":
        await show_deposit_menu(query, user)
    elif action == "withdraw":
        await show_withdraw_menu(query, user)
    elif action == "history":
        await show_transaction_history(query, user)
    elif action == "exchange":
        await show_exchange_menu(query, user)
    elif action.startswith("deposit_"):
        currency = action.split("_")[1]
        await handle_deposit(query, user, currency, context)
    elif action.startswith("withdraw_"):
        currency = action.split("_")[1]
        await handle_withdraw_input(query, user, currency, context)
    elif action.startswith("exchange_"):
        pair = action.split("_", 1)[1]
        await handle_exchange_input(query, user, pair, context)


async def show_deposit_menu(query, db_user):
    """顯示充值菜單"""
    text = """
💵 *充值*

請選擇充值幣種：
• USDT - TRC20 網絡
• TON - TON 網絡

最低充值金額：10 USDT / 10 TON
"""
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_currency_selection("wallet:deposit"),
    )


async def handle_deposit(query, db_user, currency: str, context):
    """處理充值"""
    currency_upper = currency.upper()
    balance = float(getattr(db_user, f"balance_{currency}", 0) or 0)
    
    text = f"""
💵 *充值 {currency_upper}*

*當前餘額：* `{balance:.4f}` {currency_upper}

*充值說明：*
1. 請將 {currency_upper} 轉入以下地址
2. 轉賬後系統會自動到帳
3. 如有問題，請聯繫客服

*充值地址：*
`TBD - 請在 miniapp 中查看完整地址`

💡 提示：完整的充值功能（包括地址顯示）請在 miniapp 中使用
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                "📱 打開 miniapp 充值",
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/recharge")
            ),
        ],
        [
            InlineKeyboardButton("◀️ 返回錢包", callback_data="menu:wallet"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_withdraw_menu(query, db_user):
    """顯示提現菜單"""
    text = """
💸 *提現*

請選擇提現幣種：
• USDT - TRC20 網絡
• TON - TON 網絡

最低提現金額：10 USDT / 10 TON
手續費：1%
"""
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_currency_selection("wallet:withdraw"),
    )


async def handle_withdraw_input(query, db_user, currency: str, context):
    """處理提現輸入"""
    currency_upper = currency.upper()
    balance = float(getattr(db_user, f"balance_{currency}", 0) or 0)
    
    text = f"""
💸 *提現 {currency_upper}*

*當前餘額：* `{balance:.4f}` {currency_upper}
*最低提現：* 10 {currency_upper}
*手續費：* 1%

請輸入提現金額和地址：
格式：`金額 地址`

例如：`10 Txxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

💡 提示：完整的提現功能（包括地址驗證）請在 miniapp 中使用
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                "📱 打開 miniapp 提現",
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/withdraw")
            ),
        ],
        [
            InlineKeyboardButton("◀️ 返回錢包", callback_data="menu:wallet"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_transaction_history(query, db_user):
    """顯示交易記錄"""
    # 在會話內重新查詢用戶以確保數據最新
    with get_db() as db:
        from shared.database.models import User
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id
        ).order_by(Transaction.created_at.desc()).limit(10).all()
    
    if not transactions:
        text = """
📜 *交易記錄*

暫無交易記錄
"""
    else:
        text = "📜 *最近交易記錄*\n\n"
        for tx in transactions:
            amount = float(tx.amount)
            sign = "+" if amount > 0 else ""
            status_emoji = "✅" if tx.status == "completed" else "⏳" if tx.status == "pending" else "❌"
            text += f"{status_emoji} {tx.type.upper()} {sign}{amount:.4f} {tx.currency.value.upper()}\n"
            text += f"   {tx.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    keyboard = [
        [
            InlineKeyboardButton(
                "📱 查看完整記錄",
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/")
            ),
        ],
        [
            InlineKeyboardButton("◀️ 返回錢包", callback_data="menu:wallet"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_exchange_menu(query, db_user):
    """顯示兌換菜單"""
    text = """
🔄 *貨幣兌換*

支持兌換：
• USDT ↔ TON
• USDT ↔ 能量
• TON ↔ 能量

請選擇兌換類型：
"""
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_exchange_menu(),
    )


async def handle_exchange_input(query, db_user, pair: str, context):
    """處理兌換輸入"""
    from_currency, to_currency = pair.split("_")
    from_balance = float(getattr(db_user, f"balance_{from_currency}", 0) or 0)
    
    text = f"""
🔄 *兌換 {from_currency.upper()} → {to_currency.upper()}*

*當前 {from_currency.upper()} 餘額：* `{from_balance:.4f}`

請輸入兌換金額：
格式：`金額`

例如：`10`

💡 提示：完整的兌換功能（包括實時匯率）請在 miniapp 中使用
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                "📱 打開 miniapp 兌換",
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/exchange")
            ),
        ],
        [
            InlineKeyboardButton("◀️ 返回錢包", callback_data="menu:wallet"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

