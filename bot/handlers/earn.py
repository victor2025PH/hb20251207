"""
Lucky Red - 賺取處理器（擴展版）
處理簽到、邀請、任務等功能
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from loguru import logger
from datetime import datetime, timedelta

from shared.config.settings import get_settings
from shared.database.connection import get_db
from shared.database.models import User, CheckinRecord
from bot.keyboards import get_earn_menu, get_back_to_main

settings = get_settings()


async def earn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理賺取菜單回調"""
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
    
    if action == "checkin":
        from bot.handlers.checkin import do_checkin
        from shared.database.connection import get_db
        with get_db() as db:
            result = await do_checkin(db_user, db, return_result=True)
        await handle_checkin_result(query, result)
    elif action == "invite":
        await show_invite_info(query, db_user)
    elif action == "tasks":
        await show_tasks(query, db_user)


async def handle_checkin_result(query, result):
    """處理簽到結果"""
    from bot.utils.i18n import t
    daily_checkin_title = t('daily_checkin_title', user=query.from_user)
    checkin_success_checkmark = t('checkin_success_checkmark', user=query.from_user)
    reward_earned_label = t('reward_earned_label', user=query.from_user)
    energy_reward = t('energy_reward', user=query.from_user, points=result['points'])
    consecutive_checkin_label = t('consecutive_checkin_label', user=query.from_user, days=result.get('consecutive', 0))
    checkin_7day_bonus_hint = t('checkin_7day_bonus_hint', user=query.from_user)
    unknown_error = t('unknown_error', user=query.from_user)
    return_main = t('return_main', user=query.from_user)
    
    if result["success"]:
        text = f"""
{daily_checkin_title}

{checkin_success_checkmark}

{reward_earned_label}
{energy_reward}

{consecutive_checkin_label}

{checkin_7day_bonus_hint}
"""
    else:
        text = f"""
{daily_checkin_title}

{result.get('message', unknown_error)}

{consecutive_checkin_label}

{checkin_7day_bonus_hint}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(return_main, callback_data="menu:earn"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_invite_info(query, db_user):
    """顯示邀請信息"""
    # 在會話內重新查詢用戶以確保數據最新
    from shared.database.connection import get_db
    from shared.database.models import User
    
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        invite_count = user.invite_count or 0
        invite_earnings = float(user.invite_earnings or 0)
        
        # 生成邀請碼（如果沒有）
        if not user.invite_code:
            import secrets
            user.invite_code = secrets.token_urlsafe(8)
            db.commit()
            # 清除緩存
            from bot.utils.cache import UserCache
            UserCache.invalidate(user.tg_id)
        
        invite_code = user.invite_code
    
    invite_link = f"https://t.me/{settings.BOT_USERNAME}?start={invite_code}"
    
    from bot.utils.i18n import t
    invite_info_title = t('invite_info_title', user=user)
    invite_statistics_label = t('invite_statistics_label', user=user)
    invited_count = t('invited_count', user=user, count=invite_count)
    total_earnings = t('total_earnings', user=user, earnings=invite_earnings)
    invite_rules_title = t('invite_rules_title', user=user)
    invite_rules_description = t('invite_rules_description', user=user)
    invite_link_label = t('invite_link', user=user)
    click_to_share = t('click_to_share', user=user) if t('click_to_share', user=user) != 'click_to_share' else "點擊下方按鈕分享給好友："
    share_invite_link = t('share_invite_link', user=user)
    invite_share_text = t('invite_share_text', user=user) if t('invite_share_text', user=user) != 'invite_share_text' else "快來玩搶紅包遊戲！"
    return_main = t('return_main', user=user)
    
    text = f"""
{invite_info_title}

{invite_statistics_label}
{invited_count}
{total_earnings}

{invite_rules_title}
{invite_rules_description}

{invite_link_label}
`{invite_link}`

{click_to_share}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                share_invite_link,
                url=f"https://t.me/share/url?url={invite_link}&text={invite_share_text}"
            ),
        ],
        [
            InlineKeyboardButton(return_main, callback_data="menu:earn"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_tasks(query, db_user):
    """顯示任務中心（優化查詢）"""
    from shared.database.models import RedPacket, RedPacketClaim, Transaction, User
    from sqlalchemy import func
    
    with get_db() as db:
        # 在會話內重新查詢用戶
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        # 獲取任務進度
        today = datetime.utcnow().date()
        checked_today = user.last_checkin and user.last_checkin.date() == today
        today_start = datetime.combine(today, datetime.min.time())
        
        # 使用單一查詢獲取所有統計（優化性能）
        stats = db.query(
            func.count(RedPacketClaim.id).filter(
                RedPacketClaim.user_id == user.id,
                RedPacketClaim.created_at >= today_start
            ).label('today_claimed'),
            func.count(RedPacket.id).filter(
                RedPacket.sender_id == user.id,
                RedPacket.created_at >= today_start
            ).label('today_sent'),
            func.count(Transaction.id).filter(
                Transaction.user_id == user.id,
                Transaction.type == "deposit",
                Transaction.status == "completed"
            ).label('has_deposit')
        ).first()
        
        today_claimed = stats.today_claimed or 0
        today_sent = stats.today_sent or 0
        has_deposit = (stats.has_deposit or 0) > 0
        
        # 統計總數（從用戶對象獲取，避免額外查詢）
        total_claimed = db_user.claimed_packets_count or 0
        total_sent = db_user.sent_packets_count or 0
        total_invites = db_user.invite_count or 0
    
    from bot.constants import TaskConstants
    
    text = f"""
🎯 *任務中心*

*每日任務：*
{"✅" if checked_today else "⏳"} 📅 每日簽到 - {checked_today and "已完成" or "未完成"} +{TaskConstants.DAILY_CHECKIN_REWARD} 能量
{"✅" if today_claimed > 0 else "⏳"} 🎁 搶紅包 - 今日已搶 {today_claimed} 個 +{TaskConstants.DAILY_CLAIM_REWARD} 能量/個
{"✅" if today_sent > 0 else "⏳"} 💰 發紅包 - 今日已發 {today_sent} 個 +{TaskConstants.DAILY_SEND_REWARD} 能量/個

*成就任務：*
{"✅" if has_deposit else "⏳"} 🏆 首次充值 - {has_deposit and "已完成" or "未完成"} +{TaskConstants.ACHIEVEMENT_FIRST_DEPOSIT} 能量
{"✅" if total_invites >= TaskConstants.INVITE_MASTER_TARGET else "⏳"} 👥 邀請達人 - {total_invites}/{TaskConstants.INVITE_MASTER_TARGET} 人 {total_invites >= TaskConstants.INVITE_MASTER_TARGET and "已完成" or f"還需{TaskConstants.INVITE_MASTER_TARGET-total_invites}人"} +{TaskConstants.ACHIEVEMENT_INVITE_MASTER} 能量
{"✅" if total_sent >= TaskConstants.PACKET_MASTER_TARGET else "⏳"} 🎊 紅包大師 - {total_sent}/{TaskConstants.PACKET_MASTER_TARGET} 個 {total_sent >= TaskConstants.PACKET_MASTER_TARGET and "已完成" or f"還需{TaskConstants.PACKET_MASTER_TARGET-total_sent}個"} +{TaskConstants.ACHIEVEMENT_PACKET_MASTER} 能量

*我的統計：*
• 已搶紅包：{total_claimed} 個
• 已發紅包：{total_sent} 個
• 邀請人數：{total_invites} 人
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📅 去簽到", callback_data="earn:checkin"),
        ],
        [
            InlineKeyboardButton("◀️ 返回", callback_data="menu:earn"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
