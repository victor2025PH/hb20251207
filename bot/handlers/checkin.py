"""
Lucky Red - 簽到處理器
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta

from shared.database.connection import get_db
from shared.database.models import User, CheckinRecord
from bot.constants import CheckinConstants
from bot.utils.logging_helpers import log_user_action
from bot.utils.cache import UserCache

# 簽到獎勵（使用常量）
REWARDS = CheckinConstants.REWARDS


async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /checkin 命令"""
    await do_checkin_with_message(update.effective_user, update.message)


async def checkin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理簽到回調"""
    query = update.callback_query
    await query.answer()
    await do_checkin_with_message(query.from_user, query.message, is_callback=True)


async def do_checkin(db_user, db=None, return_result=False):
    """執行簽到
    
    Args:
        db_user: User 對象
        db: 數據庫會話（如果提供則使用，否則創建新的）
        return_result: 如果為 True，返回結果字典而不是發送消息
    
    Returns:
        如果 return_result=True，返回 {"success": bool, "points": int, "consecutive": int, "message": str}
    """
    if db is None:
        with get_db() as db:
            return await do_checkin(db_user, db, return_result)
    
    today = datetime.utcnow().date()
    
    # 檢查是否已簽到
    if db_user.last_checkin and db_user.last_checkin.date() == today:
        streak = db_user.checkin_streak or 1
        if return_result:
            return {
                "success": False,
                "message": f"您今天已經簽到了！連續簽到: {streak} 天",  # 这个会在 do_checkin_with_message 中翻译
                "points": 0,
                "consecutive": streak
            }
        return {
            "success": False,
            "message": f"您今天已經簽到了！連續簽到: {streak} 天",
            "points": 0,
            "consecutive": streak
        }
    
    # 計算連續簽到
    if db_user.last_checkin:
        yesterday = today - timedelta(days=1)
        if db_user.last_checkin.date() == yesterday:
            new_streak = ((db_user.checkin_streak or 0) % 7) + 1
        else:
            new_streak = 1
    else:
        new_streak = 1
    
    reward = REWARDS.get(new_streak, 10)
    
    # 更新用戶
    db_user.last_checkin = datetime.utcnow()
    db_user.checkin_streak = new_streak
    db_user.balance_points = (db_user.balance_points or 0) + reward
    db_user.xp = (db_user.xp or 0) + reward
    db_user.consecutive_checkin_days = new_streak
    db_user.total_checkin_count = (db_user.total_checkin_count or 0) + 1
    
    # 創建記錄
    record = CheckinRecord(
        user_id=db_user.id,
        checkin_date=datetime.utcnow(),
        day_of_streak=new_streak,
        reward_points=reward,
        points_earned=reward,
    )
    db.add(record)
    db.commit()
    
    # 清除用戶緩存（因為餘額和統計已更新）
    UserCache.invalidate(db_user.tg_id)
    
    # 記錄操作
    log_user_action(db_user.tg_id, "checkin", {
        "streak": new_streak,
        "reward": reward
    })
    
    if return_result:
        return {
            "success": True,
            "points": reward,
            "consecutive": new_streak,
            "message": f"簽到成功！獲得 {reward} 能量"  # 这个会在 do_checkin_with_message 中翻译
        }
    
    return {
        "success": True,
        "points": reward,
        "consecutive": new_streak,
        "message": f"簽到成功！獲得 {reward} 能量"
    }


async def do_checkin_with_message(user, message, is_callback=False):
    """執行簽到並發送消息（保持向後兼容）"""
    with get_db() as db:
        db_user = db.query(User).filter(User.tg_id == user.id).first()
        
        if not db_user:
            from bot.utils.i18n import t
            text = t('please_register_first', user=None) if t('please_register_first', user=None) != 'please_register_first' else "請先使用 /start 註冊"
            if is_callback:
                await message.reply_text(text)
            else:
                await message.reply_text(text)
            return
        
        today = datetime.utcnow().date()
        
        # 檢查是否已簽到
        if db_user.last_checkin and db_user.last_checkin.date() == today:
            from bot.utils.i18n import t
            streak = db_user.checkin_streak or 1
            checkin_already_title = t('checkin_already_title', user=db_user)
            consecutive_checkin_days = t('consecutive_checkin_days', user=db_user, streak=streak)
            remember_tomorrow = t('remember_tomorrow', user=db_user)
            text = f"""
{checkin_already_title}

{consecutive_checkin_days}
{remember_tomorrow}
"""
            if is_callback:
                await message.edit_text(text, parse_mode="Markdown")
            else:
                await message.reply_text(text, parse_mode="Markdown")
            return
        
        result = await do_checkin(db_user, db, return_result=True)
        
        from bot.utils.i18n import t
        if result["success"]:
            checkin_success_title = t('checkin_success_title', user=db_user)
            checkin_day_label = t('checkin_day_label', user=db_user, day=result['consecutive'])
            checkin_reward_energy = t('checkin_reward_energy', user=db_user, points=result['points'])
            checkin_7day_bonus = t('checkin_7day_bonus', user=db_user)
            text = f"""
{checkin_success_title}

{checkin_day_label}
{checkin_reward_energy}

{checkin_7day_bonus}
"""
        else:
            checkin_already_title = t('checkin_already_title', user=db_user)
            consecutive_checkin_days = t('consecutive_checkin_days', user=db_user, streak=result.get('consecutive', 1))
            text = f"{checkin_already_title}\n\n{consecutive_checkin_days}"
        
        view_wallet_button = t('view_wallet_button', user=db_user)
        keyboard = [[InlineKeyboardButton(view_wallet_button, callback_data="wallet:view")]]
        
        if is_callback:
            await message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

