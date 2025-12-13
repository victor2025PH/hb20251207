"""
Lucky Red - 初始设置处理器
处理新用户的语言和键盘模式选择
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger

from shared.database.connection import get_db
from shared.database.models import User
from bot.utils.i18n import t, update_user_language, get_user_language
from bot.utils.mode_helper import update_user_mode, get_mode_name, get_mode_description
from bot.keyboards.unified import get_unified_keyboard


async def show_initial_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """显示初始设置界面（语言 + 键盘模式）"""
    from bot.utils.i18n import t  # 在函数开头导入，确保始终可用
    user = update.effective_user
    chat_type = update.effective_chat.type
    
    user_id = user.id if user else None
    
    # 获取用户当前语言（如果有）
    with get_db() as db:
        db_user = db.query(User).filter(User.tg_id == user_id).first()
        if not db_user:
            import traceback
            logger.error(f"【严重错误】[SHOW_INITIAL_SETUP] 用户 {user_id} 未找到")
            traceback.print_exc()
            from bot.keyboards import get_main_menu
            await update.message.reply_text(
                t('error_occurred', user_id=user_id),
                reply_markup=get_main_menu(user_id=user_id)
            )
            return
        
        current_lang = get_user_language(user_id=user_id)
        
        # 在会话内获取所有翻译文本（使用 user_id）
        welcome_to_lucky_red_text = t('welcome_to_lucky_red', user_id=user_id)
        please_select_language_first_text = t('please_select_language_first', user_id=user_id)
        language_selection_text = t('language_selection', user_id=user_id)
        please_select_interface_language_text = t('please_select_interface_language', user_id=user_id)
        interaction_method_text = t('interaction_method', user_id=user_id)
        mode_keyboard_text = t('mode_keyboard', user_id=user_id)
        mode_keyboard_desc_text = t('mode_keyboard_desc', user_id=user_id)
        mode_inline_text = t('mode_inline', user_id=user_id)
        mode_inline_desc_text = t('mode_inline_desc', user_id=user_id)
        mode_miniapp_text = t('mode_miniapp', user_id=user_id)
        mode_miniapp_desc_text = t('mode_miniapp_desc', user_id=user_id)
        mode_auto_text = t('mode_auto', user_id=user_id)
        mode_auto_desc_text = t('mode_auto_desc', user_id=user_id)
        you_can_switch_language_mode_text = t('you_can_switch_language_mode', user_id=user_id)
        miniapp_not_available_text = t('miniapp_not_available_in_group', user_id=user_id)
        hi_greeting_text = t('hi_greeting', user_id=user_id, name=user.first_name or 'User')
        
        keyboard = get_initial_setup_keyboard(current_lang, user_id=user_id)
    
    # 在会话外构建文本（使用预先获取的翻译）
    text = f"""
{welcome_to_lucky_red_text}

{hi_greeting_text}

{please_select_language_first_text}

{language_selection_text}
{please_select_interface_language_text}

{interaction_method_text}
• {mode_keyboard_text} - {mode_keyboard_desc_text}
• {mode_inline_text} - {mode_inline_desc_text}
• {mode_miniapp_text} - {mode_miniapp_desc_text}
• {mode_auto_text} - {mode_auto_desc_text}

{you_can_switch_language_mode_text}
"""
    
    # 如果在群组中，提示 MiniApp 不可用
    if chat_type in ["group", "supergroup"]:
        text += f"\n{miniapp_not_available_text}"
    
    try:
        await update.message.reply_text(
            text,
            parse_mode=None,  # 不使用 Markdown，避免解析错误
            reply_markup=keyboard
        )
    except Exception as e:
        import traceback
        logger.error(f"【严重错误】[SHOW_INITIAL_SETUP] 发送初始设置消息时")
        traceback.print_exc()
        # 使用统一的错误处理
        from bot.utils.error_helpers import handle_error_with_ui
        await handle_error_with_ui(
            update=update,
            context=context,
            error=e,
            error_context="[SHOW_INITIAL_SETUP] 发送初始设置消息时",
            user_id=user_id,
            show_main_menu_button=True
        )


def get_initial_setup_keyboard(current_lang: str = "zh-TW", user_id: int = None):
    """获取初始设置键盘（语言选择）（只接受 user_id，不接受 ORM 对象）"""
    from bot.utils.i18n import t
    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅' if current_lang == 'zh-TW' else ''} {t('lang_zh_tw', user_id=user_id)}",
                callback_data="setup:lang:zh-TW"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if current_lang == 'zh-CN' else ''} {t('lang_zh_cn', user_id=user_id)}",
                callback_data="setup:lang:zh-CN"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if current_lang == 'en' else ''} {t('lang_en', user_id=user_id)}",
                callback_data="setup:lang:en"
            ),
        ],
    ]
    
    return InlineKeyboardMarkup(keyboard)


async def setup_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理语言选择回调"""
    from bot.utils.i18n import t  # 确保在函数内导入
    
    query = update.callback_query
    if not query:
        return
    
    user_id = update.effective_user.id if update.effective_user else None
    logger.info(f"[SETUP] User {user_id} selecting language, callback_data: {query.data}")
    
    # 使用 user_id 獲取翻譯
    answer_text = t('setting_language', user_id=user_id)
    
    try:
        await query.answer(answer_text)
    except Exception as e:
        logger.error(f"Error answering query: {e}")
    
    # 解析语言代码
    if not query.data or not query.data.startswith("setup:lang:"):
        logger.error(f"Invalid callback_data: {query.data}")
        return
    
    lang_code = query.data.split(":")[2]
    
    # 更新用户语言
    logger.info(f"[SETUP] Updating language for user {user_id} to {lang_code}")
    success = await update_user_language(user_id, lang_code)
    
    if not success:
        logger.error(f"[SETUP] Failed to update language for user {user_id} to {lang_code}")
        try:
            await query.message.reply_text(t('language_set_failed', user_id=user_id))
        except Exception as reply_error:
            logger.error(f"[SETUP] Failed to send error message: {reply_error}")
        return
    
    # 清除緩存以確保使用新語言
    from bot.utils.cache import UserCache
    UserCache.invalidate(user_id)
    
    # 使用 user_id 獲取翻譯（使用新語言）
    current_lang = get_user_language(user_id=user_id)
    lang_names = {
        "zh-TW": t('lang_zh_tw', user_id=user_id),
        "zh-CN": t('lang_zh_cn', user_id=user_id),
        "en": t('lang_en', user_id=user_id),
    }
    lang_name = lang_names.get(current_lang, t('lang_zh_tw', user_id=user_id))
    
    # 獲取所有需要的翻譯文本
    lang_changed_text = t('lang_changed', user_id=user_id, lang=lang_name)
    select_operation_text = t('select_operation', user_id=user_id)
    mode_keyboard_text = t('mode_keyboard', user_id=user_id)
    mode_keyboard_desc_text = t('mode_keyboard_desc', user_id=user_id)
    mode_inline_text = t('mode_inline', user_id=user_id)
    mode_inline_desc_text = t('mode_inline_desc', user_id=user_id)
    mode_miniapp_text = t('mode_miniapp', user_id=user_id)
    mode_miniapp_desc_text = t('mode_miniapp_desc', user_id=user_id)
    mode_auto_text = t('mode_auto', user_id=user_id)
    mode_auto_desc_text = t('mode_auto_desc', user_id=user_id)
    you_can_switch_mode_text = t('you_can_switch_mode', user_id=user_id)
    miniapp_not_available_text = t('miniapp_not_available_in_group', user_id=user_id)
    
    # 創建鍵盤（使用 user_id）
    keyboard = get_mode_selection_keyboard(user_id=user_id)
    
    # 在会话外构建文本（使用预先获取的翻译）
    text = f"""
✅ {lang_changed_text}

{select_operation_text}

{mode_keyboard_text} - {mode_keyboard_desc_text}
{mode_inline_text} - {mode_inline_desc_text}
{mode_miniapp_text} - {mode_miniapp_desc_text}
{mode_auto_text} - {mode_auto_desc_text}

{you_can_switch_mode_text}
"""
    
    # 如果在群组中，提示 MiniApp 不可用
    if update.effective_chat.type in ["group", "supergroup"]:
        text += f"\n{miniapp_not_available_text}"
    
    # 在会话外发送消息
    try:
        await query.edit_message_text(
            text,
            parse_mode=None,  # 不使用 Markdown，避免解析错误
            reply_markup=keyboard
        )
    except Exception as edit_e:
        error_msg = str(edit_e)
        if "Message is not modified" in error_msg or "message is not modified" in error_msg.lower():
            # 消息未修改，只显示提示，不报错
            await query.answer(t('displayed', user_id=user_id), show_alert=False)
            logger.debug(f"Message not modified in setup_language_callback, user {user_id}")
        else:
            logger.error(f"Error editing message: {edit_e}", exc_info=True)
            try:
                # 尝试发送新消息
                await query.message.reply_text(
                    text,
                    parse_mode=None,  # 不使用 Markdown，避免解析错误
                    reply_markup=keyboard
                )
            except Exception as reply_e:
                logger.error(f"Error sending new message: {reply_e}", exc_info=True)
                # 如果发送新消息也失败，至少发送错误消息
                try:
                    await query.message.reply_text(
                        t('error_occurred', user_id=user_id),
                        parse_mode=None
                    )
                except Exception as e3:
                    logger.error(f"Error sending error message: {e3}", exc_info=True)


# 这个函数已经被移除，逻辑移到了 setup_language_callback 中


def get_mode_selection_keyboard(user_id: int = None):
    """获取键盘模式选择键盘（只接受 user_id，不接受 ORM 对象）"""
    from bot.keyboards.unified import get_mode_selection_keyboard as get_unified_mode_keyboard
    from bot.utils.i18n import t
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    # 使用 user_id 獲取翻譯
    mode_keyboard_text = t('mode_keyboard', user_id=user_id)
    mode_inline_text = t('mode_inline', user_id=user_id)
    mode_miniapp_text = t('mode_miniapp', user_id=user_id)
    mode_auto_text = t('mode_auto', user_id=user_id)
    
    keyboard = [
        [
            InlineKeyboardButton(mode_keyboard_text, callback_data="set_mode:keyboard"),
            InlineKeyboardButton(mode_inline_text, callback_data="set_mode:inline"),
        ],
        [
            InlineKeyboardButton(mode_miniapp_text, callback_data="set_mode:miniapp"),
            InlineKeyboardButton(mode_auto_text, callback_data="set_mode:auto"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
