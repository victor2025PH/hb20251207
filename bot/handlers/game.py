"""
Lucky Red - 遊戲處理器
處理遊戲相關功能
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from loguru import logger

from shared.config.settings import get_settings
from shared.database.connection import get_db
from shared.database.models import User
from bot.keyboards import get_back_to_main

settings = get_settings()


async def game_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理遊戲菜單回調"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    parts = query.data.split(":")
    action = parts[1] if len(parts) > 1 else ""
    
    # 獲取用戶（帶緩存）
    from bot.utils.user_helpers import get_user_from_update
    db_user = await get_user_from_update(update, context)
    if not db_user:
        await query.message.reply_text("請先使用 /start 註冊")
        return
    
    if action == "list":
        await show_games_list(query, db_user)
    elif action == "gold_fortune":
        await show_gold_fortune_info(query, db_user)
    elif action == "lucky_wheel":
        await show_lucky_wheel_info(query, db_user)


async def show_games_list(query, db_user):
    """顯示遊戲列表"""
    text = """
🎮 *遊戲中心*

*可用遊戲：*

🎰 *金運局 (Gold Fortune Bureau)*
多種遊戲類型，豐富獎勵
• 老虎機 🎰
• 真人遊戲 🎭
• 體育投注 ⚽
• 撲克遊戲 🃏
• 彩票遊戲 🎱
• 捕魚遊戲 🐟

🎡 *幸運轉盤*
每日免費轉盤，贏取能量和幸運值
• 每日 3 次免費機會
• 豐富獎品等你來拿
• 簡單易玩

選擇一個遊戲開始：
"""
    
    keyboard = [
        [
            InlineKeyboardButton("🎰 金運局", callback_data="game:gold_fortune"),
        ],
        [
            InlineKeyboardButton("🎡 幸運轉盤", callback_data="game:lucky_wheel"),
        ],
        [
            InlineKeyboardButton("◀️ 返回主菜單", callback_data="menu:main"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_gold_fortune_info(query, db_user):
    """顯示金運局遊戲介紹"""
    text = """
🎰 *金運局 (Gold Fortune Bureau)*

*遊戲介紹：*
金運局是一個綜合性遊戲平台，提供多種精彩遊戲體驗。

*遊戲類型：*
• 🎰 老虎機 - 經典老虎機遊戲，簡單刺激
• 🎭 真人遊戲 - 真人荷官，真實體驗
• ⚽ 體育投注 - 支持多種體育賽事投注
• 🃏 撲克遊戲 - 多種撲克玩法
• 🎱 彩票遊戲 - 多種彩票玩法
• 🐟 捕魚遊戲 - 經典捕魚遊戲

*特色優勢：*
• 🛡️ 安全可靠 - 多重安全保障
• 💎 VIP 特權 - 專屬 VIP 福利
• ⚡ 快速提現 - 快速到賬服務

*優惠活動：*
• 🎁 首充優惠 - 最高獎勵
• 📅 每日返水 - 無限返水
• 👑 VIP 特權 - 專屬優惠

*開始遊戲：*
點擊下方按鈕進入遊戲平台
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                "🎮 開始遊戲",
                url="https://8887893.com"
            ),
        ],
        [
            InlineKeyboardButton(
                "📱 在 miniapp 中打開",
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/game")
            ),
        ],
        [
            InlineKeyboardButton("◀️ 返回遊戲列表", callback_data="game:list"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_lucky_wheel_info(query, db_user):
    """顯示幸運轉盤遊戲介紹"""
    text = """
🎡 *幸運轉盤*

*遊戲介紹：*
幸運轉盤是一個簡單有趣的轉盤遊戲，每天都有免費機會贏取豐富獎品！

*遊戲規則：*
• 每天有 3 次免費轉盤機會
• 長按按鈕蓄力，鬆開後轉盤開始旋轉
• 轉盤停止後，根據指針位置獲得對應獎品

*獎品類型：*
• ⚡ 能量 - 用於各種功能
• 🍀 幸運值 - 提升運氣
• 💰 其他驚喜獎品

*遊戲技巧：*
• 長按時間越長，轉盤速度越快
• 掌握好時機，獲得最佳獎品
• 每天記得來轉轉，不要錯過免費機會

*開始遊戲：*
點擊下方按鈕進入幸運轉盤
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                "🎡 開始轉盤",
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/lucky-wheel")
            ),
        ],
        [
            InlineKeyboardButton("◀️ 返回遊戲列表", callback_data="game:list"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
