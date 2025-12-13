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
    from bot.utils.i18n import t
    from bot.utils.user_helpers import get_user_id_from_update
    
    # 獲取用戶 ID（不返回 ORM 對象）
    user_id = update.effective_user.id if update.effective_user else None
    tg_id = await get_user_id_from_update(update, context)
    if not tg_id:
        await update.message.reply_text(t('please_register_first', user_id=user_id))
        return
    
    # 在會話內查詢用戶並獲取數據
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == user_id).first()
        if not user:
            await update.message.reply_text(t('error_occurred', user_id=tg_id))
            return
        
        usdt = float(user.balance_usdt or 0)
        ton = float(user.balance_ton or 0)
        stars = user.balance_stars or 0
        points = user.balance_points or 0
        level = user.level
        xp = user.xp or 0
    
    # 使用 user_id 獲取翻譯
    my_wallet_text = t('my_wallet', user_id=tg_id)
    balance_colon = t('balance_colon', user_id=tg_id)
    level_colon = t('level_colon', user_id=tg_id)
    xp_colon = t('xp_colon', user_id=tg_id)
    energy_colon = t('energy_colon', user_id=tg_id)
    select_operation = t('select_operation', user_id=tg_id)
    
    text = f"""
{my_wallet_text}

{balance_colon}
• USDT: `{usdt:.4f}`
• TON: `{ton:.4f}`
• Stars: `{stars}`
• {energy_colon} `{points}`

{level_colon} Lv.{level}
{xp_colon} {xp} XP

{select_operation}:
"""
    
    from bot.keyboards import get_wallet_menu
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_wallet_menu(),
    )


async def wallet_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理錢包回調"""
    from bot.utils.user_helpers import get_user_id_from_update
    
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    
    # 獲取用戶 ID（不返回 ORM 對象）
    user_id = update.effective_user.id if update.effective_user else None
    tg_id = await get_user_id_from_update(update, context)
    if not tg_id:
        await query.message.reply_text("請先使用 /start 註冊")
        return
    
    if action == "deposit":
        await show_deposit_menu(query, tg_id)
    elif action == "withdraw":
        await show_withdraw_menu(query, tg_id)
    elif action == "history":
        await show_transaction_history(query, tg_id)
    elif action == "exchange":
        await show_exchange_menu(query, tg_id)
    elif action.startswith("deposit_"):
        currency = action.split("_")[1]
        await handle_deposit(query, tg_id, currency, context)
    elif action.startswith("withdraw_"):
        currency = action.split("_")[1]
        await handle_withdraw_input(query, tg_id, currency, context)
    elif action.startswith("exchange_"):
        pair = action.split("_", 1)[1]
        await handle_exchange_input(query, tg_id, pair, context)


async def show_deposit_menu(query, tg_id: int):
    """顯示充值菜單（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    deposit_title = t('deposit_title', user_id=tg_id)
    select_deposit_currency = t('select_deposit_currency', user_id=tg_id)
    usdt_trc20 = t('usdt_trc20', user_id=tg_id)
    ton_network = t('ton_network', user_id=tg_id)
    min_deposit_amount = t('min_deposit_amount', user_id=tg_id)
    
    text = f"""
{deposit_title}

{select_deposit_currency}
{usdt_trc20}
{ton_network}

{min_deposit_amount}
"""
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_currency_selection("wallet:deposit"),
    )


async def handle_deposit(query, tg_id: int, currency: str, context):
    """處理充值（只接受 tg_id，不接受 ORM 對象）"""
    currency_upper = currency.upper()
    
    # 在會話內查詢用戶獲取餘額
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        balance = float(getattr(user, f"balance_{currency}", 0) or 0)
    
    from bot.utils.i18n import t
    deposit_currency_title = t('deposit_currency_title', user_id=tg_id, currency=currency_upper)
    current_balance = t('current_balance', user_id=tg_id)
    deposit_instructions = t('deposit_instructions', user_id=tg_id)
    deposit_step1 = t('deposit_step1', user_id=tg_id, currency=currency_upper)
    deposit_step2 = t('deposit_step2', user_id=tg_id)
    deposit_step3 = t('deposit_step3', user_id=tg_id)
    deposit_address_label = t('deposit_address_label', user_id=tg_id)
    deposit_address_placeholder = t('deposit_address_placeholder', user_id=tg_id)
    deposit_miniapp_hint = t('deposit_miniapp_hint', user_id=tg_id)
    open_miniapp_deposit = t('open_miniapp_deposit', user_id=tg_id)
    return_wallet = t('return_wallet', user_id=tg_id)
    
    text = f"""
{deposit_currency_title}

{current_balance} `{balance:.4f}` {currency_upper}

{deposit_instructions}
{deposit_step1}
{deposit_step2}
{deposit_step3}

{deposit_address_label}
{deposit_address_placeholder}

{deposit_miniapp_hint}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                open_miniapp_deposit,
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/recharge")
            ),
        ],
        [
            InlineKeyboardButton(return_wallet, callback_data="menu:wallet"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_withdraw_menu(query, tg_id: int):
    """顯示提現菜單（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    withdraw_title = t('withdraw_title', user_id=tg_id)
    select_withdraw_currency = t('select_withdraw_currency', user_id=tg_id)
    usdt_trc20 = t('usdt_trc20', user_id=tg_id)
    ton_network = t('ton_network', user_id=tg_id)
    min_withdraw_amount = t('min_withdraw_amount', user_id=tg_id)
    withdraw_fee = t('withdraw_fee', user_id=tg_id)
    
    text = f"""
{withdraw_title}

{select_withdraw_currency}
{usdt_trc20}
{ton_network}

{min_withdraw_amount}
{withdraw_fee}
"""
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_currency_selection("wallet:withdraw"),
    )


async def handle_withdraw_input(query, tg_id: int, currency: str, context):
    """處理提現輸入（只接受 tg_id，不接受 ORM 對象）"""
    currency_upper = currency.upper()
    
    # 在會話內查詢用戶獲取餘額
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        balance = float(getattr(user, f"balance_{currency}", 0) or 0)
    
    from bot.utils.i18n import t
    withdraw_currency_title = t('withdraw_currency_title', user_id=tg_id, currency=currency_upper)
    current_balance = t('current_balance', user_id=tg_id)
    min_withdraw_label = t('min_withdraw_label', user_id=tg_id)
    withdraw_fee_label = t('withdraw_fee_label', user_id=tg_id)
    enter_withdraw_amount_address = t('enter_withdraw_amount_address', user_id=tg_id)
    withdraw_format = t('withdraw_format', user_id=tg_id)
    withdraw_example = t('withdraw_example', user_id=tg_id)
    withdraw_miniapp_hint = t('withdraw_miniapp_hint', user_id=tg_id)
    open_miniapp_withdraw = t('open_miniapp_withdraw', user_id=tg_id)
    return_wallet = t('return_wallet', user_id=tg_id)
    
    text = f"""
{withdraw_currency_title}

{current_balance} `{balance:.4f}` {currency_upper}
{min_withdraw_label} 10 {currency_upper}
{withdraw_fee_label} 1%

{enter_withdraw_amount_address}
{withdraw_format}

{withdraw_example}

{withdraw_miniapp_hint}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                open_miniapp_withdraw,
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/withdraw")
            ),
        ],
        [
            InlineKeyboardButton(return_wallet, callback_data="menu:wallet"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_transaction_history(query, tg_id: int):
    """顯示交易記錄（只接受 tg_id，不接受 ORM 對象）"""
    # 在會話內查詢用戶和交易記錄
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id
        ).order_by(Transaction.created_at.desc()).limit(10).all()
    
    from bot.utils.i18n import t
    transaction_history = t('transaction_history', user_id=tg_id)
    no_transactions = t('no_transactions', user_id=tg_id)
    recent_transactions = t('recent_transactions', user_id=tg_id)
    
    if not transactions:
        text = f"""
{transaction_history}

{no_transactions}
"""
    else:
        text = f"{recent_transactions}\n\n"
        for tx in transactions:
            amount = float(tx.amount)
            sign = "+" if amount > 0 else ""
            status_emoji = "✅" if tx.status == "completed" else "⏳" if tx.status == "pending" else "❌"
            text += f"{status_emoji} {tx.type.upper()} {sign}{amount:.4f} {tx.currency.value.upper()}\n"
            text += f"   {tx.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    view_full_history_text = t('view_full_history', user_id=tg_id)
    keyboard = [
        [
            InlineKeyboardButton(
                view_full_history_text,
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/")
            ),
        ],
        [
            InlineKeyboardButton(t('return_wallet', user_id=tg_id), callback_data="menu:wallet"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_exchange_menu(query, tg_id: int):
    """顯示兌換菜單（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    exchange_title = t('exchange_title', user_id=tg_id)
    supported_exchanges = t('supported_exchanges', user_id=tg_id)
    usdt_ton_exchange = t('usdt_ton_exchange', user_id=tg_id)
    usdt_energy_exchange = t('usdt_energy_exchange', user_id=tg_id)
    ton_energy_exchange = t('ton_energy_exchange', user_id=tg_id)
    select_exchange_type = t('select_exchange_type', user_id=tg_id)
    
    text = f"""
{exchange_title}

{supported_exchanges}
{usdt_ton_exchange}
{usdt_energy_exchange}
{ton_energy_exchange}

{select_exchange_type}:
"""
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_exchange_menu(),
    )


async def handle_exchange_input(query, tg_id: int, pair: str, context):
    """處理兌換輸入（只接受 tg_id，不接受 ORM 對象）"""
    from_currency, to_currency = pair.split("_")
    
    # 在會話內查詢用戶獲取餘額
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        from_balance = float(getattr(user, f"balance_{from_currency}", 0) or 0)
    
    from bot.utils.i18n import t
    exchange_pair_title = t('exchange_pair_title', user_id=tg_id, from_currency=from_currency.upper(), to_currency=to_currency.upper())
    current_balance_label = t('current_balance_label', user_id=tg_id, currency=from_currency.upper())
    enter_exchange_amount = t('enter_exchange_amount', user_id=tg_id)
    exchange_format = t('exchange_format', user_id=tg_id)
    exchange_example = t('exchange_example', user_id=tg_id)
    exchange_miniapp_hint = t('exchange_miniapp_hint', user_id=tg_id)
    open_miniapp_exchange = t('open_miniapp_exchange', user_id=tg_id)
    return_wallet = t('return_wallet', user_id=tg_id)
    
    text = f"""
{exchange_pair_title}

{current_balance_label} `{from_balance:.4f}`

{enter_exchange_amount}
{exchange_format}

{exchange_example}

{exchange_miniapp_hint}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                open_miniapp_exchange,
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/exchange")
            ),
        ],
        [
            InlineKeyboardButton(return_wallet, callback_data="menu:wallet"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

