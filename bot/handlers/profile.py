"""
Lucky Red - 個人資料處理器
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from loguru import logger

from shared.config.settings import get_settings
from shared.database.connection import get_db
from shared.database.models import User
from bot.keyboards import get_profile_menu, get_back_to_main

settings = get_settings()


async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理個人資料回調"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    
    # 獲取用戶（帶緩存）
    from bot.utils.user_helpers import get_user_from_update
    db_user = await get_user_from_update(update, context)
    if not db_user:
        from bot.utils.i18n import t
        await query.message.reply_text(t('please_register_first', user=None) if t('please_register_first', user=None) != 'please_register_first' else "請先使用 /start 註冊")
        return
    
    if action == "info":
        await show_profile_info(query, db_user)
    elif action == "stats":
        await show_profile_stats(query, db_user)
    elif action == "settings":
        await show_profile_settings(query, db_user)


async def show_profile_info(query, db_user):
    """顯示個人資料"""
    # 在會話內重新查詢用戶以確保數據最新
    from shared.database.connection import get_db
    from shared.database.models import User
    
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            from bot.utils.i18n import t
            await query.edit_message_text(t('error_occurred', user=user))
            return
        
        from bot.utils.i18n import t
        username = user.username or t('not_set', user=user)
        first_name = user.first_name or ''
        last_name = user.last_name or ''
        tg_id = user.tg_id
        level = user.level
        xp = user.xp or 0
        created_at = user.created_at.strftime('%Y-%m-%d') if user.created_at else t('unknown', user=user)
        balance_usdt = float(user.balance_usdt or 0)
        balance_ton = float(user.balance_ton or 0)
        balance_points = user.balance_points or 0
        
        my_profile_title = t('my_profile_title', user=user)
        basic_info_label = t('basic_info_label', user=user)
        username_label = t('username_label', user=user, username=username)
        name_label = t('name_label', user=user, first_name=first_name, last_name=last_name)
        user_id_label = t('user_id_label', user=user, tg_id=tg_id)
        account_info_label = t('account_info_label', user=user)
        level_label = t('level_label', user=user, level=level)
        xp_label = t('xp_label', user=user, xp=xp)
        registration_date_label = t('registration_date_label', user=user, created_at=created_at)
        balance_label_profile = t('balance_label_profile', user=user)
        energy_colon = t('energy_colon', user=user)
        return_main = t('return_main', user=user)
    
    text = f"""
{my_profile_title}

{basic_info_label}
{username_label}
{name_label}
{user_id_label}

{account_info_label}
{level_label}
{xp_label}
{registration_date_label}

{balance_label_profile}
• USDT: `{balance_usdt:.4f}`
• TON: `{balance_ton:.4f}`
• {energy_colon} `{balance_points}`
"""
    
    keyboard = [
        [
            InlineKeyboardButton(return_main, callback_data="menu:profile"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_profile_stats(query, db_user):
    """顯示統計數據"""
    # 在會話內重新查詢用戶以確保數據最新
    from shared.database.connection import get_db
    from shared.database.models import User, RedPacket, RedPacketClaim
    from sqlalchemy import func
    
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            from bot.utils.i18n import t
            await query.edit_message_text(t('error_occurred', user=user))
            return
        
        # 使用关系查询统计（在会话内）
        sent_count = db.query(RedPacket).filter(RedPacket.sender_id == user.id).count()
        claimed_count = db.query(RedPacketClaim).filter(RedPacketClaim.user_id == user.id).count()
        
        # 计算总发送和总领取金额
        total_sent_result = db.query(func.sum(RedPacket.total_amount)).filter(RedPacket.sender_id == user.id).scalar()
        total_sent = float(total_sent_result or 0)
        
        total_claimed_result = db.query(func.sum(RedPacketClaim.amount)).filter(RedPacketClaim.user_id == user.id).scalar()
        total_claimed = float(total_claimed_result or 0)
        
        invite_count = user.invite_count or 0
        invite_earnings = float(user.invite_earnings or 0)
        consecutive_days = user.checkin_streak or 0  # 使用 checkin_streak 代替 consecutive_checkin_days
        
        # 计算总签到次数（如果有签到记录表，否则使用 checkin_streak）
        total_checkin = user.checkin_streak or 0
    
    from bot.utils.i18n import t
    stats_title = t('stats_title', user=user)
    red_packet_stats_label = t('red_packet_stats_label', user=user)
    sent_packets_count = t('sent_packets_count', user=user, count=sent_count)
    claimed_packets_count = t('claimed_packets_count', user=user, count=claimed_count)
    total_sent_amount = t('total_sent_amount', user=user, amount=total_sent)
    total_claimed_amount = t('total_claimed_amount', user=user, amount=total_claimed)
    invite_stats_label = t('invite_stats_label', user=user)
    invited_people_count = t('invited_people_count', user=user, count=invite_count)
    invite_earnings_amount = t('invite_earnings_amount', user=user, earnings=invite_earnings)
    checkin_stats_label = t('checkin_stats_label', user=user)
    consecutive_checkin_days_label = t('consecutive_checkin_days_label', user=user, days=consecutive_days)
    total_checkin_count = t('total_checkin_count', user=user, count=total_checkin)
    more_stats_hint = t('more_stats_hint', user=user)
    open_miniapp_view_details = t('open_miniapp_view_details', user=user)
    return_main = t('return_main', user=user)
    
    text = f"""
{stats_title}

{red_packet_stats_label}
{sent_packets_count}
{claimed_packets_count}
{total_sent_amount}
{total_claimed_amount}

{invite_stats_label}
{invited_people_count}
{invite_earnings_amount}

{checkin_stats_label}
{consecutive_checkin_days_label}
{total_checkin_count}

{more_stats_hint}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                open_miniapp_view_details,
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/profile")
            ),
        ],
        [
            InlineKeyboardButton(return_main, callback_data="menu:profile"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_profile_settings(query, db_user):
    """顯示設置"""
    from bot.utils.i18n import t
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if user:
            settings_title = t('settings_title', user=user)
            account_settings_label = t('account_settings_label', user=user)
            notification_settings = t('notification_settings', user=user)
            language_settings = t('language_settings', user=user)
            privacy_settings = t('privacy_settings', user=user)
            full_settings_hint = t('full_settings_hint', user=user)
            open_miniapp_settings = t('open_miniapp_settings', user=user)
            return_main = t('return_main', user=user)
        else:
            settings_title = "⚙️ *設置*"
            account_settings_label = "*賬戶設置：*"
            notification_settings = "• 通知設置"
            language_settings = "• 語言設置"
            privacy_settings = "• 隱私設置"
            full_settings_hint = "💡 提示：完整的設置功能請在 miniapp 中使用"
            open_miniapp_settings = "📱 打開 miniapp 設置"
            return_main = "◀️ 返回"
    
    text = f"""
{settings_title}

{account_settings_label}
{notification_settings}
{language_settings}
{privacy_settings}

{full_settings_hint}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                open_miniapp_settings,
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/profile")
            ),
        ],
        [
            InlineKeyboardButton(return_main, callback_data="menu:profile"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
