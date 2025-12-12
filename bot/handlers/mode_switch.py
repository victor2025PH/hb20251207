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
from bot.utils.user_helpers import get_user_from_update
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
    
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # 获取用户
    user = await get_user_from_update(update, context)
    if not user:
        from bot.utils.i18n import t
        await query.message.reply_text(t('please_register_first', user=None) if t('please_register_first', user=None) != 'please_register_first' else "請先使用 /start 註冊")
        return
    
    # 显示模式选择界面（三种模式：内联按钮、底部键盘、MiniApp）
    await show_mode_selection_from_keyboard(update, context, user)


async def set_mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理设置模式回调（首次设置）"""
    query = update.callback_query
    if not query:
        logger.error("set_mode_callback called but no callback_query")
        return
    
    user_id = update.effective_user.id if update.effective_user else None
    logger.info(f"[SET_MODE] User {user_id} selecting mode, callback_data: {query.data}")
    
    # 获取用户以使用正确的语言
    from bot.utils.user_helpers import get_or_create_user
    from bot.utils.i18n import t
    db_user = await get_or_create_user(
        tg_id=user_id,
        username=update.effective_user.username if update.effective_user else None,
        first_name=update.effective_user.first_name if update.effective_user else None,
    )
    
    try:
        await query.answer(t("setting_mode", user=db_user))
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
            t("miniapp_not_available_in_group_auto_switch", user=db_user)
        )
        mode = "inline"
    
    # 更新用户偏好
    logger.info(f"[SET_MODE] Updating user {user_id} mode to {mode}")
    success = await update_user_mode(user_id, mode, update_last=True)
    
    if not success:
        logger.error(f"[SET_MODE] Failed to update user {user_id} mode")
        try:
            await query.message.reply_text(
                t("mode_set_failed", user=db_user)
            )
        except Exception as e:
            logger.error(f"Error sending error message: {e}")
        return
    
    logger.info(f"[SET_MODE] Successfully updated user {user_id} mode to {mode}")
    
    # 获取模式名称和描述（使用i18n）
    from bot.utils.i18n import t
    mode_name = t(f"mode_{mode}", user=db_user) if mode in ["keyboard", "inline", "miniapp", "auto"] else get_mode_name(mode)
    mode_desc = t(f"mode_{mode}_desc", user=db_user) if mode in ["keyboard", "inline", "miniapp", "auto"] else get_mode_description(mode)
    
    # 更新消息
    try:
        keyboard = get_unified_keyboard(mode, "main", chat_type, user=db_user)
        
        # 根据键盘类型处理
        from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup
        
        if isinstance(keyboard, ReplyKeyboardMarkup):
            # 底部键盘模式：先编辑消息显示确认（不带键盘），然后发送新消息带键盘
            try:
                await query.edit_message_text(
                    t("mode_set_to", user=db_user, mode=mode_name) + "\n\n"
                    f"💡 {mode_desc}\n\n"
                    + t("please_use_bottom_keyboard", user=db_user) + "\n"
                    + t("you_can_switch_mode_in_main_menu", user=db_user)
                )
            except Exception as edit_e:
                logger.warning(f"Could not edit message: {edit_e}, sending new message")
            
            # 发送新消息带回复键盘（不能编辑消息添加 ReplyKeyboardMarkup）
            await query.message.reply_text(
                t("please_use_bottom_keyboard_colon", user=db_user),
                reply_markup=keyboard
            )
            logger.info(f"[SET_MODE] Sent ReplyKeyboardMarkup for user {user_id}")
            
        elif isinstance(keyboard, InlineKeyboardMarkup):
            # 内联按钮模式：静默移除底部键盘，不显示提示消息
            from telegram import ReplyKeyboardRemove
            try:
                # 静默移除底部键盘，不显示提示消息
                # 直接移除键盘，不发送提示消息
                # 通过编辑当前消息来移除键盘（如果消息有回复标记）
                try:
                    # 尝试编辑消息移除键盘
                    await query.edit_message_reply_markup(reply_markup=None)
                except:
                    # 如果编辑失败，说明当前消息没有键盘，不需要移除
                    pass
            except Exception as remove_e:
                logger.warning(f"Could not remove keyboard: {remove_e}")
            
            # 然后编辑消息显示确认
            await query.edit_message_text(
                t("mode_set_to", user=db_user, mode=mode_name) + "\n\n"
                f"💡 {mode_desc}\n\n"
                + t("you_can_switch_mode_in_main_menu", user=db_user),
                reply_markup=keyboard
            )
            logger.info(f"[SET_MODE] Updated message with InlineKeyboardMarkup for user {user_id}")
        else:
            # 其他情况：尝试编辑消息
            await query.edit_message_text(
                t("mode_set_to", user=db_user, mode=mode_name) + "\n\n"
                f"💡 {mode_desc}",
                reply_markup=keyboard
            )
        
        logger.info(f"[SET_MODE] Successfully updated message for user {user_id}")
    except Exception as e:
        logger.error(f"Error updating message: {e}", exc_info=True)
        try:
            # 如果编辑失败，发送新消息
            keyboard = get_unified_keyboard(mode, "main", chat_type, user=db_user)
            from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup
            
            if isinstance(keyboard, ReplyKeyboardMarkup):
                await query.message.reply_text(
                    t("mode_set_to", user=db_user, mode=mode_name) + "\n\n"
                    f"💡 {mode_desc}\n\n"
                    + t("please_use_bottom_keyboard_colon", user=db_user),
                    reply_markup=keyboard
                )
            else:
                await query.message.reply_text(
                    t("mode_set_to", user=db_user, mode=mode_name) + "\n\n"
                    f"💡 {mode_desc}",
                    reply_markup=keyboard
                )
        except Exception as e2:
            logger.error(f"Error sending fallback message: {e2}", exc_info=True)
            await query.message.reply_text(t("mode_set_to", user=db_user, mode=mode_name))


async def show_mode_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示模式选择界面（首次使用）"""
    user = update.effective_user
    chat_type = update.effective_chat.type
    
    from bot.utils.i18n import t
    from bot.utils.user_helpers import get_user_from_update
    db_user = await get_user_from_update(update, context)
    if not db_user:
        db_user = user
    
    welcome_title = t('welcome_to_lucky_red', user=db_user) if t('welcome_to_lucky_red', user=db_user) != 'welcome_to_lucky_red' else f"🧧 *歡迎來到 Lucky Red！*"
    hi_greeting = t('hi_greeting', user=db_user, name=user.first_name) if t('hi_greeting', user=db_user) != 'hi_greeting' else f"Hi {user.first_name}！"
    select_interaction_mode = t('select_interaction_mode', user=db_user) if t('select_interaction_mode', user=db_user) != 'select_interaction_mode' else "請選擇您喜歡的交互方式："
    keyboard_mode_desc = t('keyboard_mode_welcome_desc', user=db_user) if t('keyboard_mode_welcome_desc', user=db_user) != 'keyboard_mode_welcome_desc' else "*⌨️ 底部鍵盤* - 傳統 bot 體驗，在群組中也能使用"
    inline_mode_desc = t('inline_mode_welcome_desc', user=db_user) if t('inline_mode_welcome_desc', user=db_user) != 'inline_mode_welcome_desc' else "*🔘 內聯按鈕* - 流暢交互，點擊消息中的按鈕"
    miniapp_mode_desc = t('miniapp_mode_welcome_desc', user=db_user) if t('miniapp_mode_welcome_desc', user=db_user) != 'miniapp_mode_welcome_desc' else "*📱 MiniApp* - 最豐富的功能，最佳體驗（僅私聊）"
    auto_mode_desc = t('auto_mode_welcome_desc', user=db_user) if t('auto_mode_welcome_desc', user=db_user) != 'auto_mode_welcome_desc' else "*🔄 自動* - 根據上下文自動選擇最佳模式"
    can_switch_mode_hint = t('can_switch_mode_hint', user=db_user) if t('can_switch_mode_hint', user=db_user) != 'can_switch_mode_hint' else "💡 您可以隨時使用「🔄 切換模式」按鈕切換"
    miniapp_not_available_in_group_note = t('miniapp_not_available_in_group_note', user=db_user) if t('miniapp_not_available_in_group_note', user=db_user) != 'miniapp_not_available_in_group_note' else "\n⚠️ 注意：MiniApp 模式在群組中不可用"
    
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
            reply_markup=get_mode_selection_keyboard()
        )
    except Exception as e:
        logger.error(f"Error sending mode selection: {e}", exc_info=True)


async def show_mode_selection_from_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, db_user):
    """从键盘模式显示模式选择界面（三种模式：内联按钮、底部键盘、MiniApp）"""
    chat_type = update.effective_chat.type
    
    # 获取用户语言
    from bot.utils.i18n import t, get_user_language
    current_lang = get_user_language(user=db_user)
    
    text = f"""
🔄 *{t('switch_mode', user=db_user)}*

{t('select_operation', user=db_user)}

*{t('mode_inline', user=db_user)}* - {t('mode_inline_desc', user=db_user)}
*{t('mode_keyboard', user=db_user)}* - {t('mode_keyboard_desc', user=db_user)}
*{t('mode_miniapp', user=db_user)}* - {t('mode_miniapp_desc', user=db_user)}

{t('choose_your_preferred_interaction', user=db_user)}
"""
    
    # 如果在群组中，提示 MiniApp 不可用
    if chat_type in ["group", "supergroup"]:
        text += f"\n{t('miniapp_not_available_in_group', user=db_user)}"
    
    # 创建三种模式选择键盘（只显示三种主要模式，不包括auto）- 按钮中包含图标
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [
        [
            InlineKeyboardButton(f"🔘 {t('mode_inline', user=db_user)}", callback_data="set_mode:inline"),
        ],
        [
            InlineKeyboardButton(f"⌨️ {t('mode_keyboard', user=db_user)}", callback_data="set_mode:keyboard"),
        ],
        [
            InlineKeyboardButton(f"📱 {t('mode_miniapp', user=db_user)}", callback_data="set_mode:miniapp"),
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
