"""
Lucky Red - 主菜單處理器
處理所有菜單導航和功能入口
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from shared.database.connection import get_db
from shared.database.models import User
from bot.keyboards import (
    get_main_menu, get_wallet_menu, get_packets_menu,
    get_earn_menu, get_profile_menu, get_exchange_menu
)


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理菜單回調"""
    from bot.utils.decorators import handle_errors
    from bot.utils.user_helpers import get_user_from_update
    
    query = update.callback_query
    await query.answer()
    
    action = query.data.split(":")[1]
    
    # 獲取用戶（帶緩存）
    db_user = await get_user_from_update(update, context)
    if not db_user:
        await query.message.reply_text("請先使用 /start 註冊")
        return
    
    if action == "main":
        await show_main_menu(query, db_user)
    elif action == "wallet":
        await show_wallet_menu(query, db_user)
    elif action == "packets":
        await show_packets_menu(query, db_user)
    elif action == "earn":
        await show_earn_menu(query, db_user)
    elif action == "game":
        await show_game_menu(query, db_user)
    elif action == "profile":
        await show_profile_menu(query, db_user)


async def show_main_menu(query, db_user):
    """顯示主菜單"""
    # 在會話內重新查詢用戶以確保數據最新
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        usdt = float(user.balance_usdt or 0)
        ton = float(user.balance_ton or 0)
        points = user.balance_points or 0
    
    text = f"""
🧧 *Lucky Red 搶紅包*

💰 *總資產*
• USDT: `{usdt:.4f}`
• TON: `{ton:.4f}`
• 能量: `{points}`

請選擇功能：
"""
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_main_menu(),
    )


async def show_wallet_menu(query, db_user):
    """顯示錢包菜單"""
    # 在會話內重新查詢用戶以確保數據最新
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
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
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_wallet_menu(),
    )


async def show_packets_menu(query, db_user):
    """顯示紅包菜單"""
    text = """
🧧 *紅包中心*

*功能：*
• 📋 查看紅包 - 瀏覽可搶的紅包
• ➕ 發紅包 - 在群組中發送紅包
• 🎁 我的紅包 - 查看我發送的紅包

請選擇操作：
"""
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_packets_menu(),
    )


async def show_earn_menu(query, db_user):
    """顯示賺取菜單"""
    # 在會話內重新查詢用戶以確保數據最新
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        invite_count = user.invite_count or 0
        invite_earnings = float(user.invite_earnings or 0)
    
    text = f"""
📈 *賺取中心*

*我的收益：*
• 已邀請：{invite_count} 人
• 邀請返佣：{invite_earnings:.4f} USDT

*功能：*
• 📅 每日簽到 - 領取每日獎勵
• 👥 邀請好友 - 獲得永久返佣
• 🎯 任務中心 - 完成任務賺積分
• 🎰 幸運轉盤 - 抽獎贏大獎

請選擇操作：
"""
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_earn_menu(),
    )


async def show_game_menu(query, db_user):
    """顯示遊戲菜單"""
    from bot.handlers import game
    await game.show_games_list(query, db_user)


async def show_profile_menu(query, db_user):
    """顯示個人資料菜單"""
    # 在會話內重新查詢用戶以確保數據最新
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            await query.edit_message_text("發生錯誤，請稍後再試")
            return
        
        username = user.username or '未設置'
        level = user.level
        xp = user.xp or 0
        sent_count = user.sent_packets_count or 0
        claimed_count = user.claimed_packets_count or 0
        invite_count = user.invite_count or 0
    
    text = f"""
👤 *我的資料*

*基本信息：*
• 用戶名：@{username}
• 等級：Lv.{level}
• 經驗：{xp} XP

*統計：*
• 已發紅包：{sent_count} 個
• 已搶紅包：{claimed_count} 個
• 邀請人數：{invite_count} 人

請選擇操作：
"""
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_profile_menu(),
    )
