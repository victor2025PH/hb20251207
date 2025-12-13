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
    
    if action == "checkin":
        from bot.handlers.checkin import do_checkin
        from shared.database.connection import get_db
        with get_db() as db:
            db_user = db.query(User).filter(User.tg_id == tg_id).first()
            if db_user:
                result = await do_checkin(db_user, db, return_result=True)
                await handle_checkin_result(query, result, tg_id)
    elif action == "invite":
        await show_invite_info(query, tg_id)
    elif action == "tasks":
        await show_tasks(query, tg_id)


async def handle_checkin_result(query, result, tg_id: int):
    """處理簽到結果（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    user_id = query.from_user.id if query.from_user else tg_id
    daily_checkin_title = t('daily_checkin_title', user_id=user_id)
    checkin_success_checkmark = t('checkin_success_checkmark', user_id=user_id)
    reward_earned_label = t('reward_earned_label', user_id=user_id)
    energy_reward = t('energy_reward', user_id=user_id, points=result['points'])
    consecutive_checkin_label = t('consecutive_checkin_label', user_id=user_id, days=result.get('consecutive', 0))
    checkin_7day_bonus_hint = t('checkin_7day_bonus_hint', user_id=user_id)
    unknown_error = t('unknown_error', user_id=user_id)
    return_main = t('return_main', user_id=user_id)
    
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


async def show_invite_info(query, tg_id: int):
    """顯示邀請信息（只接受 tg_id，不接受 ORM 對象）"""
    # 在會話內查詢用戶以確保數據最新
    from shared.database.connection import get_db
    from shared.database.models import User
    
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
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
    
    # 在會話外使用 user_id 獲取翻譯
    from bot.utils.i18n import t
    invite_info_title = t('invite_info_title', user_id=tg_id)
    invite_statistics_label = t('invite_statistics_label', user_id=tg_id)
    invited_count_text = t('invited_count', user_id=tg_id, count=invite_count)
    total_earnings_text = t('total_earnings', user_id=tg_id, earnings=invite_earnings)
    invite_rules_title = t('invite_rules_title', user_id=tg_id)
    invite_rules_description = t('invite_rules_description', user_id=tg_id)
    invite_link_label = t('invite_link', user_id=tg_id)
    click_to_share = t('click_to_share', user_id=tg_id)
    share_invite_link = t('share_invite_link', user_id=tg_id)
    invite_share_text = t('invite_share_text', user_id=tg_id)
    return_main = t('return_main', user_id=tg_id)
    
    text = f"""
{invite_info_title}

{invite_statistics_label}
{invited_count_text}
{total_earnings_text}

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


async def show_tasks(query, tg_id: int):
    """顯示任務中心（只接受 tg_id，不接受 ORM 對象）"""
    from shared.database.models import RedPacket, RedPacketClaim, Transaction, User
    from sqlalchemy import func
    
    with get_db() as db:
        # 在會話內查詢用戶
        user = db.query(User).filter(User.tg_id == tg_id).first()
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
        
        # 統計總數（從用戶對象獲取）
        total_claimed = user.claimed_packets_count or 0
        total_sent = user.sent_packets_count or 0
        total_invites = user.invite_count or 0
    
    from bot.constants import TaskConstants
    from bot.utils.i18n import t
    
    # 使用 user_id 獲取翻譯
    tasks_title = t('tasks_title', user_id=tg_id)
    daily_tasks_label = t('daily_tasks_label', user_id=tg_id)
    achievement_tasks_label = t('achievement_tasks_label', user_id=tg_id)
    my_statistics_label = t('my_statistics_label', user_id=tg_id)
    
    # 每日任務
    daily_checkin_task = t('daily_checkin_task', user_id=tg_id)
    task_completed = t('task_completed', user_id=tg_id)
    task_not_completed = t('task_not_completed', user_id=tg_id)
    checkin_status = task_completed if checked_today else task_not_completed
    
    claim_red_packet_task = t('claim_red_packet_task', user_id=tg_id)
    today_claimed_count = t('today_claimed_count', user_id=tg_id, count=today_claimed)
    energy_per_item = t('energy_per_item', user_id=tg_id)
    
    send_red_packet_task = t('send_red_packet_task', user_id=tg_id)
    today_sent_count = t('today_sent_count', user_id=tg_id, count=today_sent)
    
    # 成就任務
    first_deposit_task = t('first_deposit_task', user_id=tg_id)
    first_deposit_status = task_completed if has_deposit else task_not_completed
    
    invite_master_task = t('invite_master_task', user_id=tg_id)
    invite_progress = f"{total_invites}/{TaskConstants.INVITE_MASTER_TARGET} 人"
    invite_status = task_completed if total_invites >= TaskConstants.INVITE_MASTER_TARGET else t('task_need_more', user_id=tg_id, count=TaskConstants.INVITE_MASTER_TARGET-total_invites)
    
    packet_master_task = t('packet_master_task', user_id=tg_id)
    packet_progress = f"{total_sent}/{TaskConstants.PACKET_MASTER_TARGET} 個"
    packet_status = task_completed if total_sent >= TaskConstants.PACKET_MASTER_TARGET else t('task_need_more_packets', user_id=tg_id, count=TaskConstants.PACKET_MASTER_TARGET-total_sent)
    
    # 統計
    claimed_packets_count_label = t('claimed_packets_count_label', user_id=tg_id, count=total_claimed)
    sent_packets_count_label = t('sent_packets_count_label', user_id=tg_id, count=total_sent)
    invited_people_count_label = t('invited_people_count_label', user_id=tg_id, count=total_invites)
    
    go_checkin_button = t('go_checkin_button', user_id=tg_id)
    return_main = t('return_main', user_id=tg_id)
    
    text = f"""
{tasks_title}

{daily_tasks_label}
{"✅" if checked_today else "⏳"} {daily_checkin_task} - {checkin_status} +{TaskConstants.DAILY_CHECKIN_REWARD} 能量
{"✅" if today_claimed > 0 else "⏳"} {claim_red_packet_task} - {today_claimed_count} +{TaskConstants.DAILY_CLAIM_REWARD} {energy_per_item}
{"✅" if today_sent > 0 else "⏳"} {send_red_packet_task} - {today_sent_count} +{TaskConstants.DAILY_SEND_REWARD} {energy_per_item}

{achievement_tasks_label}
{"✅" if has_deposit else "⏳"} {first_deposit_task} - {first_deposit_status} +{TaskConstants.ACHIEVEMENT_FIRST_DEPOSIT} 能量
{"✅" if total_invites >= TaskConstants.INVITE_MASTER_TARGET else "⏳"} {invite_master_task} - {invite_progress} {invite_status} +{TaskConstants.ACHIEVEMENT_INVITE_MASTER} 能量
{"✅" if total_sent >= TaskConstants.PACKET_MASTER_TARGET else "⏳"} {packet_master_task} - {packet_progress} {packet_status} +{TaskConstants.ACHIEVEMENT_PACKET_MASTER} 能量

{my_statistics_label}
{claimed_packets_count_label}
{sent_packets_count_label}
{invited_people_count_label}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(go_checkin_button, callback_data="earn:checkin"),
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
