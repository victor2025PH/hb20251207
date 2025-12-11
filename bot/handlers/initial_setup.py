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
    user = update.effective_user
    chat_type = update.effective_chat.type
    
    # 获取用户当前语言（如果有）
    with get_db() as db:
        db_user = db.query(User).filter(User.tg_id == user.id).first()
        if not db_user:
            await update.message.reply_text("發生錯誤，請稍後再試")
            return
        
        current_lang = get_user_language(user=db_user)
        
        # 在会话内预先加载所有需要的属性
        _ = db_user.id
        _ = db_user.tg_id
        _ = db_user.language_code
        
        # 在会话内获取所有翻译文本
        welcome_to_lucky_red_text = t('welcome_to_lucky_red', user=db_user)
        please_select_language_first_text = t('please_select_language_first', user=db_user)
        language_selection_text = t('language_selection', user=db_user)
        please_select_interface_language_text = t('please_select_interface_language', user=db_user)
        interaction_method_text = t('interaction_method', user=db_user)
        mode_keyboard_text = t('mode_keyboard', user=db_user)
        mode_keyboard_desc_text = t('mode_keyboard_desc', user=db_user)
        mode_inline_text = t('mode_inline', user=db_user)
        mode_inline_desc_text = t('mode_inline_desc', user=db_user)
        mode_miniapp_text = t('mode_miniapp', user=db_user)
        mode_miniapp_desc_text = t('mode_miniapp_desc', user=db_user)
        mode_auto_text = t('mode_auto', user=db_user)
        mode_auto_desc_text = t('mode_auto_desc', user=db_user)
        you_can_switch_language_mode_text = t('you_can_switch_language_mode', user=db_user)
        miniapp_not_available_text = t('miniapp_not_available_in_group', user=db_user)
        
        keyboard = get_initial_setup_keyboard(current_lang)
    
    # 在会话外构建文本（使用预先获取的翻译）
    text = f"""
{welcome_to_lucky_red_text}

Hi {user.first_name}！

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
        logger.error(f"Error sending initial setup: {e}", exc_info=True)


def get_initial_setup_keyboard(current_lang: str = "zh-TW"):
    """获取初始设置键盘（语言选择）"""
    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅' if current_lang == 'zh-TW' else ''} 繁體中文",
                callback_data="setup:lang:zh-TW"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if current_lang == 'zh-CN' else ''} 简体中文",
                callback_data="setup:lang:zh-CN"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if current_lang == 'en' else ''} English",
                callback_data="setup:lang:en"
            ),
        ],
    ]
    
    return InlineKeyboardMarkup(keyboard)


async def setup_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理语言选择回调"""
    query = update.callback_query
    if not query:
        return
    
    user_id = update.effective_user.id if update.effective_user else None
    logger.info(f"[SETUP] User {user_id} selecting language, callback_data: {query.data}")
    
    # 获取用户以使用正确的语言
    with get_db() as db:
        temp_user = db.query(User).filter(User.tg_id == user_id).first()
        if temp_user:
            answer_text = t('setting_language', user=temp_user)
        else:
            answer_text = "正在設置語言..."
    
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
            await query.message.reply_text("❌ 設置語言失敗，請稍後再試")
        except Exception as reply_error:
            logger.error(f"[SETUP] Failed to send error message: {reply_error}")
        return
    
    # 重新获取用户以获取新语言
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == user_id).first()
        if not user:
            await query.message.reply_text("發生錯誤，請稍後再試")
            return
        
        # 在会话内预先加载所有需要的属性，并获取语言相关的文本
        # 这样即使会话关闭，我们也能使用这些值
        current_lang = get_user_language(user=user)
        lang_names = {
            "zh-TW": "繁體中文",
            "zh-CN": "简体中文",
            "en": "English",
        }
        lang_name = lang_names.get(current_lang, "繁體中文")
        
        # 在会话内获取所有需要的翻译文本
        lang_changed_text = t('lang_changed', user=user, lang=lang_name)
        select_operation_text = t('select_operation', user=user)
        mode_keyboard_text = t('mode_keyboard', user=user)
        mode_keyboard_desc_text = t('mode_keyboard_desc', user=user)
        mode_inline_text = t('mode_inline', user=user)
        mode_inline_desc_text = t('mode_inline_desc', user=user)
        mode_miniapp_text = t('mode_miniapp', user=user)
        mode_miniapp_desc_text = t('mode_miniapp_desc', user=user)
        mode_auto_text = t('mode_auto', user=user)
        mode_auto_desc_text = t('mode_auto_desc', user=user)
        you_can_switch_mode_text = t('you_can_switch_mode', user=user)
        miniapp_not_available_text = t('miniapp_not_available_in_group', user=user)
        
        # 预先访问用户属性，确保它们被加载
        _ = user.id
        _ = user.tg_id
        _ = user.language_code
        
        # 创建键盘（在会话内）
        keyboard = get_mode_selection_keyboard(user)
    
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
    except Exception as e:
        logger.error(f"Error editing message: {e}", exc_info=True)
        try:
            await query.message.reply_text(
                text,
                parse_mode=None,  # 不使用 Markdown，避免解析错误
                reply_markup=keyboard
            )
        except Exception as e2:
            logger.error(f"Error sending new message: {e2}", exc_info=True)


# 这个函数已经被移除，逻辑移到了 setup_language_callback 中


def get_mode_selection_keyboard(db_user=None):
    """获取键盘模式选择键盘"""
    from bot.keyboards.unified import get_mode_selection_keyboard as get_unified_mode_keyboard
    from bot.utils.i18n import t
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    if db_user:
        # 注意：这个函数应该在会话内调用，或者 db_user 的属性已经被预先加载
        # 使用i18n获取按钮文本
        try:
            mode_keyboard_text = t('mode_keyboard', user=db_user)
            mode_inline_text = t('mode_inline', user=db_user)
            mode_miniapp_text = t('mode_miniapp', user=db_user)
            mode_auto_text = t('mode_auto', user=db_user)
        except Exception as e:
            logger.warning(f"Error getting translations for keyboard, using fallback: {e}")
            # 回退到默认文本
            mode_keyboard_text = "⌨️ 底部键盘"
            mode_inline_text = "🔘 内联按钮"
            mode_miniapp_text = "📱 MiniApp"
            mode_auto_text = "🔄 自动"
        
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
    else:
        # 回退到旧的实现
        keyboard = get_unified_mode_keyboard()
        return keyboard
