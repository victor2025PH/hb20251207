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
    from bot.utils.i18n import t  # 在函数开头导入，确保始终可用
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    
    # 獲取用戶 ID（不返回 ORM 對象）
    from bot.utils.user_helpers import get_user_id_from_update
    user_id = user.id if user else None
    tg_id = await get_user_id_from_update(update, context)
    if not tg_id:
        await query.message.reply_text(t('please_register_first', user_id=user_id))
        return
    
    if action == "info":
        await show_profile_info(query, tg_id)
    elif action == "stats":
        await show_profile_stats(query, tg_id)
    elif action == "settings":
        await show_profile_settings(query, tg_id)


async def show_profile_info(query, tg_id: int):
    """顯示個人資料（只接受 tg_id，不接受 ORM 對象）"""
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            from bot.utils.i18n import t
            await query.edit_message_text(t('error_occurred', user_id=tg_id))
            return
        
        from bot.utils.i18n import t
        username = user.username or t('not_set', user_id=tg_id)
        first_name = user.first_name or ''
        last_name = user.last_name or ''
        user_tg_id = user.tg_id
        level = user.level
        xp = user.xp or 0
        created_at = user.created_at.strftime('%Y-%m-%d') if user.created_at else t('unknown', user_id=tg_id)
        balance_usdt = float(user.balance_usdt or 0)
        balance_ton = float(user.balance_ton or 0)
        balance_points = user.balance_points or 0
        
        # 在會話內使用 user_id 獲取翻譯
        my_profile_title = t('my_profile_title', user_id=tg_id)
        basic_info_label = t('basic_info_label', user_id=tg_id)
        username_label = t('username_label', user_id=tg_id, username=username)
        name_label = t('name_label', user_id=tg_id, first_name=first_name, last_name=last_name)
        user_id_label = t('user_id_label', user_id=tg_id, tg_id=user_tg_id)
        account_info_label = t('account_info_label', user_id=tg_id)
        level_label = t('level_label', user_id=tg_id, level=level)
        xp_label = t('xp_label', user_id=tg_id, xp=xp)
        registration_date_label = t('registration_date_label', user_id=tg_id, created_at=created_at)
        balance_label_profile = t('balance_label_profile', user_id=tg_id)
        energy_colon = t('energy_colon', user_id=tg_id)
        return_main = t('return_main', user_id=tg_id)
    
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


async def show_profile_stats(query, tg_id: int):
    """顯示統計數據（只接受 tg_id，不接受 ORM 對象）"""
    from shared.database.connection import get_db
    from shared.database.models import User, RedPacket, RedPacketClaim
    from sqlalchemy import func
    
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            from bot.utils.i18n import t
            await query.edit_message_text(t('error_occurred', user_id=tg_id))
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
    # 使用 user_id 獲取翻譯
    stats_title = t('stats_title', user_id=tg_id)
    red_packet_stats_label = t('red_packet_stats_label', user_id=tg_id)
    sent_packets_count = t('sent_packets_count', user_id=tg_id, count=sent_count)
    claimed_packets_count = t('claimed_packets_count', user_id=tg_id, count=claimed_count)
    total_sent_amount = t('total_sent_amount', user_id=tg_id, amount=total_sent)
    total_claimed_amount = t('total_claimed_amount', user_id=tg_id, amount=total_claimed)
    invite_stats_label = t('invite_stats_label', user_id=tg_id)
    invited_people_count = t('invited_people_count', user_id=tg_id, count=invite_count)
    invite_earnings_amount = t('invite_earnings_amount', user_id=tg_id, earnings=invite_earnings)
    checkin_stats_label = t('checkin_stats_label', user_id=tg_id)
    consecutive_checkin_days_label = t('consecutive_checkin_days_label', user_id=tg_id, days=consecutive_days)
    total_checkin_count = t('total_checkin_count', user_id=tg_id, count=total_checkin)
    more_stats_hint = t('more_stats_hint', user_id=tg_id)
    open_miniapp_view_details = t('open_miniapp_view_details', user_id=tg_id)
    return_main = t('return_main', user_id=tg_id)
    
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


async def show_profile_settings(query, tg_id: int):
    """顯示設置（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if user:
            # 使用 user_id 獲取翻譯
            settings_title = t('settings_title', user_id=tg_id)
            account_settings_label = t('account_settings_label', user_id=tg_id)
            notification_settings = t('notification_settings', user_id=tg_id)
            language_settings = t('language_settings', user_id=tg_id)
            privacy_settings = t('privacy_settings', user_id=tg_id)
            full_settings_hint = t('full_settings_hint', user_id=tg_id)
            open_miniapp_settings = t('open_miniapp_settings', user_id=tg_id)
            return_main = t('return_main', user_id=tg_id)
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
