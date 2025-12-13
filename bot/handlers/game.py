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
        from bot.utils.i18n import t
        await query.message.reply_text(t('please_register_first', user=None) if t('please_register_first', user=None) != 'please_register_first' else "請先使用 /start 註冊")
        return
    
    if action == "list":
        await show_games_list(query, db_user)
    elif action == "gold_fortune":
        await show_gold_fortune_info(query, db_user)
    elif action == "lucky_wheel":
        await show_lucky_wheel_info(query, db_user)


async def show_games_list(query, tg_id: int):
    """顯示遊戲列表（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if user:
            # 使用 user_id 獲取翻譯
            game_center_title = t('game_center_title', user_id=tg_id)
            available_games_label = t('available_games_label', user_id=tg_id)
            gold_fortune_bureau = t('gold_fortune_bureau', user_id=tg_id)
            gold_fortune_description = t('gold_fortune_description', user_id=tg_id)
            slot_machine = t('slot_machine', user_id=tg_id)
            live_games = t('live_games', user_id=tg_id)
            sports_betting = t('sports_betting', user_id=tg_id)
            poker_games = t('poker_games', user_id=tg_id)
            lottery_games = t('lottery_games', user_id=tg_id)
            fishing_games = t('fishing_games', user_id=tg_id)
            lucky_wheel_title = t('lucky_wheel_title', user_id=tg_id)
            lucky_wheel_description = t('lucky_wheel_description', user_id=tg_id)
            daily_free_chances = t('daily_free_chances', user_id=tg_id)
            rich_prizes = t('rich_prizes', user_id=tg_id)
            easy_to_play = t('easy_to_play', user_id=tg_id)
            select_game_to_start = t('select_game_to_start', user_id=tg_id)
            gold_fortune_button = t('gold_fortune_button', user_id=tg_id)
            lucky_wheel_button = t('lucky_wheel_button', user_id=tg_id)
            return_main_menu = t('return_main_menu', user_id=tg_id)
        else:
            # 如果用戶不存在，使用默認值
            game_center_title = "🎮 *遊戲中心*"
            available_games_label = "*可用遊戲：*"
            gold_fortune_bureau = "🎰 *金運局 (Gold Fortune Bureau)*"
            gold_fortune_description = "多種遊戲類型，豐富獎勵"
            slot_machine = "• 老虎機 🎰"
            live_games = "• 真人遊戲 🎭"
            sports_betting = "• 體育投注 ⚽"
            poker_games = "• 撲克遊戲 🃏"
            lottery_games = "• 彩票遊戲 🎱"
            fishing_games = "• 捕魚遊戲 🐟"
            lucky_wheel_title = "🎡 *幸運轉盤*"
            lucky_wheel_description = "每日免費轉盤，贏取能量和幸運值"
            daily_free_chances = "• 每日 3 次免費機會"
            rich_prizes = "• 豐富獎品等你來拿"
            easy_to_play = "• 簡單易玩"
            select_game_to_start = "選擇一個遊戲開始："
            gold_fortune_button = "🎰 金運局"
            lucky_wheel_button = "🎡 幸運轉盤"
            return_main_menu = "◀️ 返回主菜單"
    
    text = f"""
{game_center_title}

{available_games_label}

{gold_fortune_bureau}
{gold_fortune_description}
{slot_machine}
{live_games}
{sports_betting}
{poker_games}
{lottery_games}
{fishing_games}

{lucky_wheel_title}
{lucky_wheel_description}
{daily_free_chances}
{rich_prizes}
{easy_to_play}

{select_game_to_start}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(gold_fortune_button, callback_data="game:gold_fortune"),
        ],
        [
            InlineKeyboardButton(lucky_wheel_button, callback_data="game:lucky_wheel"),
        ],
        [
            InlineKeyboardButton(return_main_menu, callback_data="menu:main"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_gold_fortune_info(query, tg_id: int):
    """顯示金運局遊戲介紹（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if user:
            # 使用 user_id 獲取翻譯
            gold_fortune_info_title = t('gold_fortune_info_title', user_id=tg_id)
            game_introduction_label = t('game_introduction_label', user_id=tg_id)
            gold_fortune_intro = t('gold_fortune_intro', user_id=tg_id)
            game_types_label = t('game_types_label', user_id=tg_id)
            slot_machine_desc = t('slot_machine_desc', user_id=tg_id)
            live_games_desc = t('live_games_desc', user_id=tg_id)
            sports_betting_desc = t('sports_betting_desc', user_id=tg_id)
            poker_games_desc = t('poker_games_desc', user_id=tg_id)
            lottery_games_desc = t('lottery_games_desc', user_id=tg_id)
            fishing_games_desc = t('fishing_games_desc', user_id=tg_id)
            features_label = t('features_label', user_id=tg_id)
            security_feature = t('security_feature', user_id=tg_id)
            vip_privilege = t('vip_privilege', user_id=tg_id)
            fast_withdrawal = t('fast_withdrawal', user_id=tg_id)
            promotions_label = t('promotions_label', user_id=tg_id)
            first_deposit_bonus = t('first_deposit_bonus', user_id=tg_id)
            daily_rebate = t('daily_rebate', user_id=tg_id)
            vip_benefits = t('vip_benefits', user_id=tg_id)
            start_game_label = t('start_game_label', user_id=tg_id)
            click_to_enter_game = t('click_to_enter_game', user_id=tg_id)
            start_game_button = t('start_game_button', user_id=tg_id)
            open_in_miniapp = t('open_in_miniapp', user_id=tg_id)
            return_game_list = t('return_game_list', user_id=tg_id)
        else:
            gold_fortune_info_title = "🎰 *金運局 (Gold Fortune Bureau)*"
            game_introduction_label = "*遊戲介紹：*"
            gold_fortune_intro = "金運局是一個綜合性遊戲平台，提供多種精彩遊戲體驗。"
            game_types_label = "*遊戲類型：*"
            slot_machine_desc = "• 🎰 老虎機 - 經典老虎機遊戲，簡單刺激"
            live_games_desc = "• 🎭 真人遊戲 - 真人荷官，真實體驗"
            sports_betting_desc = "• ⚽ 體育投注 - 支持多種體育賽事投注"
            poker_games_desc = "• 🃏 撲克遊戲 - 多種撲克玩法"
            lottery_games_desc = "• 🎱 彩票遊戲 - 多種彩票玩法"
            fishing_games_desc = "• 🐟 捕魚遊戲 - 經典捕魚遊戲"
            features_label = "*特色優勢：*"
            security_feature = "• 🛡️ 安全可靠 - 多重安全保障"
            vip_privilege = "• 💎 VIP 特權 - 專屬 VIP 福利"
            fast_withdrawal = "• ⚡ 快速提現 - 快速到賬服務"
            promotions_label = "*優惠活動：*"
            first_deposit_bonus = "• 🎁 首充優惠 - 最高獎勵"
            daily_rebate = "• 📅 每日返水 - 無限返水"
            vip_benefits = "• 👑 VIP 特權 - 專屬優惠"
            start_game_label = "*開始遊戲：*"
            click_to_enter_game = "點擊下方按鈕進入遊戲平台"
            start_game_button = "🎮 開始遊戲"
            open_in_miniapp = "📱 在 miniapp 中打開"
            return_game_list = "◀️ 返回遊戲列表"
    
    text = f"""
{gold_fortune_info_title}

{game_introduction_label}
{gold_fortune_intro}

{game_types_label}
{slot_machine_desc}
{live_games_desc}
{sports_betting_desc}
{poker_games_desc}
{lottery_games_desc}
{fishing_games_desc}

{features_label}
{security_feature}
{vip_privilege}
{fast_withdrawal}

{promotions_label}
{first_deposit_bonus}
{daily_rebate}
{vip_benefits}

{start_game_label}
{click_to_enter_game}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                start_game_button,
                url="https://8887893.com"
            ),
        ],
        [
            InlineKeyboardButton(
                open_in_miniapp,
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/game")
            ),
        ],
        [
            InlineKeyboardButton(return_game_list, callback_data="game:list"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_lucky_wheel_info(query, tg_id: int):
    """顯示幸運轉盤遊戲介紹（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if user:
            # 使用 user_id 獲取翻譯
            lucky_wheel_info_title = t('lucky_wheel_info_title', user_id=tg_id)
            game_introduction_label = t('game_introduction_label', user_id=tg_id)
            lucky_wheel_intro = t('lucky_wheel_intro', user_id=tg_id)
            game_rules_label = t('game_rules_label', user_id=tg_id)
            daily_free_chances_rule = t('daily_free_chances_rule', user_id=tg_id)
            long_press_rule = t('long_press_rule', user_id=tg_id)
            spin_stop_rule = t('spin_stop_rule', user_id=tg_id)
            prize_types_label = t('prize_types_label', user_id=tg_id)
            energy_prize = t('energy_prize', user_id=tg_id)
            luck_value_prize = t('luck_value_prize', user_id=tg_id)
            other_prizes = t('other_prizes', user_id=tg_id)
            game_tips_label = t('game_tips_label', user_id=tg_id)
            long_press_tip = t('long_press_tip', user_id=tg_id)
            timing_tip = t('timing_tip', user_id=tg_id)
            daily_reminder_tip = t('daily_reminder_tip', user_id=tg_id)
            start_lucky_wheel_label = t('start_lucky_wheel_label', user_id=tg_id)
            click_to_start_wheel = t('click_to_start_wheel', user_id=tg_id)
            start_wheel_button = t('start_wheel_button', user_id=tg_id)
            return_game_list = t('return_game_list', user_id=tg_id)
        else:
            lucky_wheel_info_title = "🎡 *幸運轉盤*"
            game_introduction_label = "*遊戲介紹：*"
            lucky_wheel_intro = "幸運轉盤是一個簡單有趣的轉盤遊戲，每天都有免費機會贏取豐富獎品！"
            game_rules_label = "*遊戲規則：*"
            daily_free_chances_rule = "• 每天有 3 次免費轉盤機會"
            long_press_rule = "• 長按按鈕蓄力，鬆開後轉盤開始旋轉"
            spin_stop_rule = "• 轉盤停止後，根據指針位置獲得對應獎品"
            prize_types_label = "*獎品類型：*"
            energy_prize = "• ⚡ 能量 - 用於各種功能"
            luck_value_prize = "• 🍀 幸運值 - 提升運氣"
            other_prizes = "• 💰 其他驚喜獎品"
            game_tips_label = "*遊戲技巧：*"
            long_press_tip = "• 長按時間越長，轉盤速度越快"
            timing_tip = "• 掌握好時機，獲得最佳獎品"
            daily_reminder_tip = "• 每天記得來轉轉，不要錯過免費機會"
            start_lucky_wheel_label = "*開始遊戲：*"
            click_to_start_wheel = "點擊下方按鈕進入幸運轉盤"
            start_wheel_button = "🎡 開始轉盤"
            return_game_list = "◀️ 返回遊戲列表"
    
    text = f"""
{lucky_wheel_info_title}

{game_introduction_label}
{lucky_wheel_intro}

{game_rules_label}
{daily_free_chances_rule}
{long_press_rule}
{spin_stop_rule}

{prize_types_label}
{energy_prize}
{luck_value_prize}
{other_prizes}

{game_tips_label}
{long_press_tip}
{timing_tip}
{daily_reminder_tip}

{start_lucky_wheel_label}
{click_to_start_wheel}
"""
    
    keyboard = [
        [
            InlineKeyboardButton(
                start_wheel_button,
                web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/lucky-wheel")
            ),
        ],
        [
            InlineKeyboardButton(return_game_list, callback_data="game:list"),
        ],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
