"""
Lucky Red - 模式切换处理器
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from bot.utils.mode_helper import (
    get_effective_mode, 
    update_user_mode, 
    get_mode_name,
    get_mode_description
)
from bot.utils.user_helpers import get_user_id_from_update
from bot.keyboards.unified import get_unified_keyboard, get_mode_selection_keyboard


async def switch_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理模式切换回调 - 显示三种模式选择菜单"""
    query = update.callback_query
    if not query:
        return
    
    try:
        await query.answer()
    except Exception as e:
        logger.error(f"Error answering query: {e}")
    
    from bot.utils.i18n import t
    user_id = update.effective_user.id if update.effective_user else None
    if not user_id:
        return
    
    # 获取用户 ID（不返回 ORM 对象）
    tg_id = await get_user_id_from_update(update, context)
    if not tg_id:
        await query.message.reply_text(t('please_register_first', user_id=user_id))
        return
    
    # 显示模式选择界面（三种模式：内联按钮、底部键盘、MiniApp）
    await show_mode_selection_from_keyboard(update, context, tg_id)


async def set_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理设置模式回调（首次设置）"""
    query = update.callback_query
    if not query:
        logger.error("set_mode_callback called but no callback_query")
        return
    
    user_id = update.effective_user.id if update.effective_user else None
    logger.info(f"[SET_MODE] User {user_id} selecting mode, callback_data: {query.data}")
    
    if not user_id:
        return
    
    # 获取用户 ID
    tg_id = await get_user_id_from_update(update, context)
    if not tg_id:
        from bot.utils.i18n import t
        await query.message.reply_text(t("please_register_first", user_id=user_id))
        return
    
    from bot.utils.i18n import t
    
    try:
        await query.answer(t("setting_mode", user_id=tg_id))
    except Exception as e:
        logger.error(f"Error answering query: {e}")
    
    # 解析模式
    if not query.data or not query.data.startswith("set_mode:"):
        logger.error(f"Invalid callback_data: {query.data}")
        return
    
    mode = query.data.split(":")[1]
    chat_type = update.effective_chat.type
    
    logger.info(f"[SET_MODE] User {user_id} selected mode: {mode}, chat_type: {chat_type}")
    
    # 检查模式是否可用
    if mode == "miniapp" and chat_type in ["group", "supergroup"]:
        await query.message.reply_text(
            t("miniapp_not_available_in_group_auto_switch", user_id=tg_id)
        )
        mode = "inline"
    
    # 更新用户偏好
    logger.info(f"[SET_MODE] Updating user {user_id} mode to {mode}")
    success = await update_user_mode(user_id, mode, update_last=True)
    
    if not success:
        logger.error(f"[SET_MODE] Failed to update user {user_id} mode")
        try:
            await query.message.reply_text(
                t("mode_set_failed", user_id=tg_id)
            )
        except Exception as e:
            logger.error(f"Error sending error message: {e}")
        return
    
    logger.info(f"[SET_MODE] Successfully updated user {user_id} mode to {mode}")
    
    # 获取模式名称和描述（使用i18n，使用用户选择的语言）
    mode_name = t(f"mode_{mode}", user_id=tg_id) if mode in ["keyboard", "inline", "miniapp", "auto"] else get_mode_name(mode)
    mode_desc = t(f"mode_{mode}_desc", user_id=tg_id) if mode in ["keyboard", "inline", "miniapp", "auto"] else get_mode_description(mode)
    
    # 选择模式后，显示主菜单（使用用户选择的语言）
    from bot.handlers.menu import show_main_menu
    
    try:
        # 直接显示主菜单（使用用户选择的语言），不先显示确认消息
        # 这样可以避免多次编辑消息导致的问题
        await show_main_menu(query, tg_id)
        logger.info(f"[SET_MODE] Successfully showed main menu for user {user_id} after setting mode to {mode}")
        
    except Exception as e:
        logger.error(f"Error showing main menu: {e}", exc_info=True)
        try:
            # 如果显示主菜单失败，尝试显示确认消息和主菜单按钮
            from bot.keyboards import get_main_menu
            mode_set_text = t("mode_set_to", user_id=tg_id, mode=mode_name)
            try:
                await query.edit_message_text(
                    mode_set_text,
                    parse_mode=None,
                    reply_markup=get_main_menu(user_id=tg_id)
                )
            except Exception as edit_e:
                error_msg = str(edit_e)
                if "Message is not modified" in error_msg or "message is not modified" in error_msg.lower():
                    # 消息未修改，只显示提示，不报错
                    await query.answer(t('displayed', user_id=tg_id), show_alert=False)
                    logger.debug(f"Message not modified in set_mode_callback, user {tg_id}")
                else:
                    # 如果编辑失败，发送新消息
                    if query.message:
                        await query.message.reply_text(
                            mode_set_text,
                            parse_mode=None,
                            reply_markup=get_main_menu(user_id=tg_id)
                        )
        except Exception as e2:
            import traceback
            logger.error(f"【严重错误】[SET_MODE_CALLBACK] 发送回退消息时")
            traceback.print_exc()
            # 使用统一的错误处理
            from bot.utils.error_helpers import handle_error_with_ui
            from telegram import Update
            class MockUpdate:
                def __init__(self, callback_query):
                    self.callback_query = callback_query
                    self.effective_user = callback_query.from_user if callback_query else None
            mock_update = MockUpdate(query)
            await handle_error_with_ui(
                update=mock_update,
                context=context,
                error=e2,
                error_context="[SET_MODE_CALLBACK] 发送回退消息时",
                user_id=tg_id,
                show_main_menu_button=True
            )


async def show_mode_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示模式选择界面（首次使用）"""
    user = update.effective_user
    if not user:
        return
    
    chat_type = update.effective_chat.type
    user_id = user.id
    
    from bot.utils.i18n import t
    from bot.utils.user_helpers import get_user_id_from_update
    
    # 获取用户 ID
    tg_id = await get_user_id_from_update(update, context)
    if not tg_id:
        tg_id = user_id  # 如果获取失败，使用 Telegram user ID
    
    welcome_title = t('welcome_to_lucky_red', user_id=tg_id)
    hi_greeting = t('hi_greeting', user_id=tg_id, name=user.first_name or 'User')
    select_interaction_mode = t('select_interaction_mode', user_id=tg_id)
    keyboard_mode_desc = t('keyboard_mode_welcome_desc', user_id=tg_id)
    inline_mode_desc = t('inline_mode_welcome_desc', user_id=tg_id)
    miniapp_mode_desc = t('miniapp_mode_welcome_desc', user_id=tg_id)
    auto_mode_desc = t('auto_mode_welcome_desc', user_id=tg_id)
    can_switch_mode_hint = t('can_switch_mode_hint', user_id=tg_id)
    miniapp_not_available_in_group_note = t('miniapp_not_available_in_group_note', user_id=tg_id)
    
    text = f"""
{welcome_title}

{hi_greeting}

{select_interaction_mode}

{keyboard_mode_desc}
{inline_mode_desc}
{miniapp_mode_desc}
{auto_mode_desc}

{can_switch_mode_hint}
"""
    
    # 如果在群组中，提示 MiniApp 不可用
    if chat_type in ["group", "supergroup"]:
        text += miniapp_not_available_in_group_note
    
    try:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_mode_selection_keyboard(user_id=tg_id)
        )
    except Exception as e:
        logger.error(f"Error sending mode selection: {e}", exc_info=True)


async def show_mode_selection_from_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, tg_id: int):
    """从键盘模式显示模式选择界面（三种模式：内联按钮、底部键盘、MiniApp）（只接受 user_id，不接受 ORM 对象）"""
    chat_type = update.effective_chat.type
    
    # 获取用户语言（使用 user_id）
    from bot.utils.i18n import t
    
    text = f"""
🔄 *{t('switch_mode', user_id=tg_id)}*

{t('select_operation', user_id=tg_id)}

*{t('mode_inline', user_id=tg_id)}* - {t('mode_inline_desc', user_id=tg_id)}
*{t('mode_keyboard', user_id=tg_id)}* - {t('mode_keyboard_desc', user_id=tg_id)}
*{t('mode_miniapp', user_id=tg_id)}* - {t('mode_miniapp_desc', user_id=tg_id)}

{t('choose_your_preferred_interaction', user_id=tg_id)}
"""
    
    # 如果在群组中，提示 MiniApp 不可用
    if chat_type in ["group", "supergroup"]:
        text += f"\n{t('miniapp_not_available_in_group', user_id=tg_id)}"
    
    # 创建三种模式选择键盘（只显示三种主要模式，不包括auto）- 按钮中包含图标
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [
        [
            InlineKeyboardButton(f"🔘 {t('mode_inline', user_id=tg_id)}", callback_data="set_mode:inline"),
        ],
        [
            InlineKeyboardButton(f"⌨️ {t('mode_keyboard', user_id=tg_id)}", callback_data="set_mode:keyboard"),
        ],
        [
            InlineKeyboardButton(f"📱 {t('mode_miniapp', user_id=tg_id)}", callback_data="set_mode:miniapp"),
        ],
    ]
    
    try:
        # 如果是 callback_query，编辑消息；否则发送新消息
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        logger.error(f"Error sending mode selection from keyboard: {e}", exc_info=True)
        # 如果编辑失败，尝试发送新消息
        try:
            if update.callback_query:
                await update.callback_query.message.reply_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except Exception as e2:
            logger.error(f"Error sending fallback message: {e2}", exc_info=True)
