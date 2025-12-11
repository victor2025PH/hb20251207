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
            await query.message.reply_text("請先使用 /start 註冊")
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
                keyboard_message = "個人中心"
            
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
                    await query.message.reply_text(f"未知操作: {action}")
            except:
                pass
    except Exception as e:
        logger.error(f"[MENU_CALLBACK] Error processing action '{action}': {e}", exc_info=True)
        try:
            if query.message:
                await query.message.reply_text("發生錯誤，請稍後再試")
        except:
            pass


async def show_main_menu(query, db_user):
    """顯示主菜單"""
    try:
        from bot.utils.i18n import t
        # 在會話內重新查詢用戶以確保數據最新，並在會話內完成所有操作
        with get_db() as db:
            user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
            if not user:
                try:
                    await query.edit_message_text(t("error", user=db_user))
                except:
                    if hasattr(query, 'message') and query.message:
                        await query.message.reply_text("發生錯誤，請稍後再試")
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
            await query.edit_message_text("發生錯誤，請稍後再試")
        except:
            try:
                if query.message:
                    await query.message.reply_text("發生錯誤，請稍後再試")
            except:
                pass


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
                    await query.message.reply_text("發生錯誤，請稍後再試")
            return
        
        # 在会话内访问所有需要的属性
        _ = user.id
        _ = user.tg_id
        _ = user.language
        _ = user.interaction_mode
        
        # 在会话内获取翻译文本
        packets_center_text = t('packets_center', user=user)
        view_packets_text = t('view_packets', user=user)
        send_packet_text = t('send_packet', user=user)
        my_packets_text = t('my_packets', user=user)
        select_operation_text = t('select_operation', user=user)
        
        # 获取功能描述
        view_packets_desc = t('view_packets_desc', user=user)
        send_packet_desc = t('send_packet_desc', user=user)
        my_packets_desc = t('my_packets_desc', user=user)
        
        # 在会话内生成键盘（get_packets_menu 内部会调用 t()，需要访问 user 属性）
        reply_markup = get_packets_menu(user=user)
        
        text = f"""
🧧 *{packets_center_text}*

*功能：*
• 📋 {view_packets_text} - {view_packets_desc}
• ➕ {send_packet_text} - {send_packet_desc}
• 🎁 {my_packets_text} - {my_packets_desc}

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
    text = """
📈 *賺取中心*

*功能：*
• 📅 每日簽到 - 每天簽到領取積分
• 👥 邀請好友 - 邀請好友獲得返佣
• 🎯 任務中心 - 完成任務獲得獎勵
• 🎰 幸運轉盤 - 轉盤抽獎贏大獎

請選擇操作：
"""
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_earn_menu(),
    )


async def show_game_menu(query, db_user):
    """顯示遊戲菜單"""
    text = """
🎮 *遊戲中心*

*功能：*
• 🎰 金運局 - 經典紅包遊戲
• 🎡 幸運轉盤 - 轉盤抽獎

請選擇操作：
"""
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_profile_menu(),
    )


async def show_profile_menu(query, db_user):
    """顯示個人資料菜單"""
    text = """
👤 *個人資料*

*功能：*
• 📊 我的資料 - 查看個人信息
• 📈 統計數據 - 查看統計數據
• ⚙️ 設置 - 個人設置

請選擇操作：
"""
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=get_profile_menu(),
    )
