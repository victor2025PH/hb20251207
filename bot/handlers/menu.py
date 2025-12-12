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
    if not query:
        return
    
    try:
        await query.answer()
    except Exception as e:
        logger.error(f"Error answering query: {e}")
    
    # 解析操作类型
    if not query.data or not query.data.startswith("menu:"):
        logger.warning(f"Invalid menu callback_data: {query.data}")
        return
    
    action = query.data.split(":")[1]
    logger.info(f"[MENU_CALLBACK] Action: {action}, User: {update.effective_user.id if update.effective_user else None}")
    
    try:
        # 获取用户
        db_user = await get_user_from_update(update, context)
        if not db_user:
            from bot.utils.i18n import t
            await query.message.reply_text(t('please_register_first', user=None) if t('please_register_first', user=None) != 'please_register_first' else "請先使用 /start 註冊")
            return
        
        # 如果是键盘模式，尝试恢复底部键盘
        from bot.utils.mode_helper import get_effective_mode
        effective_mode = get_effective_mode(db_user, update.effective_chat.type)
        
        if effective_mode == "keyboard":
            from bot.keyboards.reply_keyboards import get_main_reply_keyboard, get_profile_reply_keyboard
            from bot.utils.i18n import t
            
            reply_keyboard = None
            keyboard_message = ""
            
            if action == "main":
                reply_keyboard = get_main_reply_keyboard(user=db_user)
                keyboard_message = t("main_menu", user=db_user) if t("main_menu", user=db_user) != "main_menu" else "主菜單"
            elif action == "profile":
                reply_keyboard = get_profile_reply_keyboard()
                keyboard_message = t("profile_center", user=db_user)
            
            if reply_keyboard and query.message:
                try:
                    await query.message.reply_text(
                        keyboard_message,
                        reply_markup=reply_keyboard,
                    )
                except Exception as e:
                    logger.debug(f"Error restoring reply keyboard: {e}")
        
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
        elif action == "language":
            from bot.handlers.language import show_language_selection
            await show_language_selection(update, context)
        else:
            logger.warning(f"[MENU_CALLBACK] Unknown action: {action}")
            try:
                if query.message:
                    from bot.utils.i18n import t
                    await query.message.reply_text(f"{t('unknown_action', user=db_user)}: {action}")
            except:
                pass
    except Exception as e:
        logger.error(f"[MENU_CALLBACK] Error processing action '{action}': {e}", exc_info=True)
        try:
            if query.message:
                from bot.utils.i18n import t
                await query.message.reply_text(t('error_occurred', user=db_user))
        except:
            pass


async def show_main_menu(query, db_user):
    """顯示主菜單"""
    from bot.utils.i18n import t  # 在函数开头导入，确保始终可用
    try:
        # 在會話內重新查詢用戶以確保數據最新，並在會話內完成所有操作
        with get_db() as db:
            user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
            if not user:
                try:
                    await query.edit_message_text(t("error", user=db_user))
                except:
                    if hasattr(query, 'message') and query.message:
                        from bot.utils.i18n import t
                await query.message.reply_text(t('error_occurred', user=db_user))
                return
            
            # 在会话内访问所有需要的属性
            usdt = float(user.balance_usdt or 0)
            ton = float(user.balance_ton or 0)
            points = user.balance_points or 0
            
            # 在会话内获取翻译文本
            select_operation = t('select_operation', user=user)
            
            # 在会话内获取更多翻译文本
            lucky_red_text = t('lucky_red_red_packet', user=user)
            total_assets_text = t('total_assets', user=user)
            energy_text = t('energy', user=user)
            
            text = f"""
{lucky_red_text}

{total_assets_text}
• USDT: `{usdt:.4f}`
• TON: `{ton:.4f}`
• {energy_text}: `{points}`

{select_operation}:
"""
            
            # 在会话内完成所有操作后再发送消息
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=get_main_menu(user=user),
            )
    except Exception as e:
        logger.error(f"Error in show_main_menu: {e}", exc_info=True)
        try:
            from bot.utils.i18n import t
            await query.edit_message_text(t('error_occurred', user=db_user))
        except:
            try:
                if query.message:
                    from bot.utils.i18n import t
                await query.message.reply_text(t('error_occurred', user=db_user))
            except:
                pass


async def show_wallet_menu(query, db_user):
    """顯示錢包菜單"""
    from bot.utils.i18n import t  # 在函数开头导入，确保始终可用
    # 在會話內重新查詢用戶以確保數據最新
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
            if not user:
                await query.edit_message_text(t('error_occurred', user=db_user))
            return
        
        usdt = float(user.balance_usdt or 0)
        ton = float(user.balance_ton or 0)
        stars = user.balance_stars or 0
        points = user.balance_points or 0
        level = user.level
        xp = user.xp or 0
    
    my_wallet_text = t('my_wallet', user=user)
    balance_colon = t('balance_colon', user=user)
    level_colon = t('level_colon', user=user)
    xp_colon = t('xp_colon', user=user)
    energy_colon = t('energy_colon', user=user)
    select_operation = t('select_operation', user=user)
    
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
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_wallet_menu(),
    )


async def show_packets_menu(query, db_user):
    """顯示紅包菜單"""
    from bot.utils.i18n import t
    from shared.database.connection import get_db
    from shared.database.models import User
    
    # 在会话内重新查询用户以确保数据最新，并在会话内完成所有操作
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            try:
                await query.edit_message_text(t("error", user=db_user))
            except:
                if hasattr(query, 'message') and query.message:
                    from bot.utils.i18n import t
                await query.message.reply_text(t('error_occurred', user=db_user))
            return
        
        # 在会话内访问所有需要的属性
        _ = user.id
        _ = user.tg_id
        _ = user.language_code  # 注意：User 模型使用 language_code，不是 language
        _ = user.interaction_mode
        
        # 在会话内获取翻译文本
        packets_center_text = t('packets_center', user=user)
        view_packets_text = t('view_packets', user=user)
        send_packet_text = t('send_packet', user=user)
        my_packets_text = t('my_packets', user=user)
        select_operation_text = t('select_operation', user=user)
        
        # 获取功能描述（翻译文本中已包含图标，不需要重复添加）
        view_packets_desc = t('view_packets_desc', user=user)
        send_packet_desc = t('send_packet_desc', user=user)
        my_packets_desc = t('my_packets_desc', user=user)
        functions_label = t('functions', user=user)
        
        # 在会话内生成键盘（get_packets_menu 内部会调用 t()，需要访问 user 属性）
        reply_markup = get_packets_menu(user=user)
        
        # 移除翻译文本中的图标，只保留文本部分（避免重复显示图标）
        # 注意：view_packets_text, send_packet_text, my_packets_text 已经包含图标
        text = f"""
🧧 *{packets_center_text}*

*{functions_label}*
• {view_packets_text} - {view_packets_desc}
• {send_packet_text} - {send_packet_desc}
• {my_packets_text} - {my_packets_desc}

{select_operation_text}:
"""
    
    # 在会话外发送消息（reply_markup 已经在会话内生成）
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def show_earn_menu(query, db_user):
    """顯示賺取菜單"""
    from bot.utils.i18n import t
    from shared.database.connection import get_db
    from shared.database.models import User
    
    # 在会话内重新查询用户以确保数据最新
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            try:
                await query.edit_message_text(t("error", user=db_user))
            except:
                if hasattr(query, 'message') and query.message:
                    from bot.utils.i18n import t
                await query.message.reply_text(t('error_occurred', user=db_user))
            return
        
        # 在会话内获取翻译文本
        earn_center = t('earn_center', user=user) if t('earn_center', user=user) != 'earn_center' else "📈 賺取中心"
        functions_label = t('functions', user=user)
        daily_checkin = t('daily_checkin', user=user) if t('daily_checkin', user=user) != 'daily_checkin' else "📅 每日簽到"
        daily_checkin_desc = t('daily_checkin_desc', user=user) if t('daily_checkin_desc', user=user) != 'daily_checkin_desc' else "每天簽到領取積分"
        invite_friends = t('invite_friends', user=user) if t('invite_friends', user=user) != 'invite_friends' else "👥 邀請好友"
        invite_friends_desc = t('invite_friends_desc', user=user) if t('invite_friends_desc', user=user) != 'invite_friends_desc' else "邀請好友獲得返佣"
        task_center = t('task_center', user=user) if t('task_center', user=user) != 'task_center' else "🎯 任務中心"
        task_center_desc = t('task_center_desc', user=user) if t('task_center_desc', user=user) != 'task_center_desc' else "完成任務獲得獎勵"
        lucky_wheel = t('lucky_wheel', user=user) if t('lucky_wheel', user=user) != 'lucky_wheel' else "🎰 幸運轉盤"
        lucky_wheel_desc = t('lucky_wheel_desc', user=user) if t('lucky_wheel_desc', user=user) != 'lucky_wheel_desc' else "轉盤抽獎贏大獎"
        select_operation = t('select_operation', user=user)
    
    text = f"""
{earn_center}

*{functions_label}*
• {daily_checkin} - {daily_checkin_desc}
• {invite_friends} - {invite_friends_desc}
• {task_center} - {task_center_desc}
• {lucky_wheel} - {lucky_wheel_desc}

{select_operation}:
"""
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_earn_menu(),
    )


async def show_game_menu(query, db_user):
    """顯示遊戲菜單"""
    from bot.utils.i18n import t
    from shared.database.connection import get_db
    from shared.database.models import User
    
    # 在会话内重新查询用户以确保数据最新
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            try:
                await query.edit_message_text(t("error", user=db_user))
            except:
                if hasattr(query, 'message') and query.message:
                    from bot.utils.i18n import t
                await query.message.reply_text(t('error_occurred', user=db_user))
            return
        
        # 在会话内获取翻译文本
        game_center = t('game_center', user=user) if t('game_center', user=user) != 'game_center' else "🎮 遊戲中心"
        functions_label = t('functions', user=user)
        select_operation = t('select_operation', user=user)
        # 游戏相关的翻译文本（如果不存在，使用默认值）
        game_golden_luck = t('game_golden_luck', user=user) if t('game_golden_luck', user=user) != 'game_golden_luck' else "🎰 金運局"
        game_golden_luck_desc = t('game_golden_luck_desc', user=user) if t('game_golden_luck_desc', user=user) != 'game_golden_luck_desc' else "經典紅包遊戲"
        lucky_wheel = t('lucky_wheel', user=user) if t('lucky_wheel', user=user) != 'lucky_wheel' else "🎡 幸運轉盤"
        lucky_wheel_desc = t('lucky_wheel_desc', user=user) if t('lucky_wheel_desc', user=user) != 'lucky_wheel_desc' else "轉盤抽獎"
    
    text = f"""
{game_center}

*{functions_label}*
• {game_golden_luck} - {game_golden_luck_desc}
• {lucky_wheel} - {lucky_wheel_desc}

{select_operation}:
"""
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_profile_menu(),
    )


async def show_profile_menu(query, db_user):
    """顯示個人資料菜單"""
    from bot.utils.i18n import t
    from shared.database.connection import get_db
    from shared.database.models import User
    
    # 在会话内重新查询用户以确保数据最新
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            try:
                await query.edit_message_text(t("error", user=db_user))
            except:
                if hasattr(query, 'message') and query.message:
                    from bot.utils.i18n import t
                await query.message.reply_text(t('error_occurred', user=db_user))
            return
        
        # 在会话内获取翻译文本
        profile_center = t('profile_center', user=user) if t('profile_center', user=user) != 'profile_center' else "👤 個人資料"
        functions_label = t('functions', user=user)
        select_operation = t('select_operation', user=user)
        # 个人资料相关的翻译文本（如果不存在，使用默认值）
        my_profile = t('my_profile', user=user) if t('my_profile', user=user) != 'my_profile' else "📊 我的資料"
        my_profile_desc = t('my_profile_desc', user=user) if t('my_profile_desc', user=user) != 'my_profile_desc' else "查看個人信息"
    
        # 获取更多翻译文本
        stats = t('stats', user=user) if t('stats', user=user) != 'stats' else "📈 統計數據"
        stats_desc = t('stats_desc', user=user) if t('stats_desc', user=user) != 'stats_desc' else "查看統計數據"
        settings = t('settings', user=user) if t('settings', user=user) != 'settings' else "⚙️ 設置"
        settings_desc = t('settings_desc', user=user) if t('settings_desc', user=user) != 'settings_desc' else "個人設置"
    
    text = f"""
{profile_center}

*{functions_label}*
• {my_profile} - {my_profile_desc}
• {stats} - {stats_desc}
• {settings} - {settings_desc}

{select_operation}:
"""
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_profile_menu(),
    )
