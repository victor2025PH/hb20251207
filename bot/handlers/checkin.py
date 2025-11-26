"""
Lucky Red - 簽到處理器
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta

from shared.database.connection import get_db
from shared.database.models import User, CheckinRecord

# 簽到獎勵
REWARDS = {1: 10, 2: 20, 3: 30, 4: 40, 5: 50, 6: 60, 7: 100}


async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /checkin 命令"""
    await do_checkin(update.effective_user, update.message)


async def checkin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理簽到回調"""
    query = update.callback_query
    await query.answer()
    await do_checkin(query.from_user, query.message, is_callback=True)


async def do_checkin(user, message, is_callback=False):
    """執行簽到"""
    with get_db() as db:
        db_user = db.query(User).filter(User.tg_id == user.id).first()
        
        if not db_user:
            text = "請先使用 /start 註冊"
            if is_callback:
                await message.reply_text(text)
            else:
                await message.reply_text(text)
            return
        
        today = datetime.utcnow().date()
        
        # 檢查是否已簽到
        if db_user.last_checkin and db_user.last_checkin.date() == today:
            streak = db_user.checkin_streak or 1
            text = f"""
📅 *今日已簽到*

連續簽到: {streak} 天
明天記得來哦！
"""
            if is_callback:
                await message.edit_text(text, parse_mode="Markdown")
            else:
                await message.reply_text(text, parse_mode="Markdown")
            return
        
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
        
        # 創建記錄
        record = CheckinRecord(
            user_id=db_user.id,
            checkin_date=datetime.utcnow(),
            day_of_streak=new_streak,
            reward_points=reward,
        )
        db.add(record)
        db.commit()
    
    text = f"""
🎉 *簽到成功！*

📅 第 {new_streak} 天
🎁 獲得 {reward} 積分

連續簽到7天可獲得額外獎勵！
"""
    
    keyboard = [[InlineKeyboardButton("💰 查看錢包", callback_data="wallet:view")]]
    
    if is_callback:
        await message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

