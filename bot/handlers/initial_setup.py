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
    
    # 使用i18n获取文本
    text = f"""
*{t('welcome_to_lucky_red', user=db_user)}*

Hi {user.first_name}！

{t('please_select_language_first', user=db_user)}

*{t('language_selection', user=db_user)}*
{t('please_select_interface_language', user=db_user)}

*{t('interaction_method', user=db_user)}*
• {t('mode_keyboard', user=db_user)} - {t('mode_keyboard_desc', user=db_user)}
• {t('mode_inline', user=db_user)} - {t('mode_inline_desc', user=db_user)}
• {t('mode_miniapp', user=db_user)} - {t('mode_miniapp_desc', user=db_user)}
• {t('mode_auto', user=db_user)} - {t('mode_auto_desc', user=db_user)}

{t('you_can_switch_language_mode', user=db_user)}
"""
    
    # 如果在群组中，提示 MiniApp 不可用
    if chat_type in ["group", "supergroup"]:
        text += f"\n{t('miniapp_not_available_in_group', user=db_user)}"
    
    keyboard = get_initial_setup_keyboard(current_lang)
    
    try:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
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
        
        # 显示键盘模式选择
        await show_mode_selection_after_lang(query, user, update.effective_chat.type)


async def show_mode_selection_after_lang(query, db_user, chat_type: str):
    """在语言选择后显示键盘模式选择"""
    lang_names = {
        "zh-TW": "繁體中文",
        "zh-CN": "简体中文",
        "en": "English",
    }
    current_lang = get_user_language(user=db_user)
    lang_name = lang_names.get(current_lang, "繁體中文")
    
    # 使用i18n获取文本
    text = f"""
✅ *{t('lang_changed', user=db_user, lang=lang_name)}*

{t('select_operation', user=db_user)}

*{t('mode_keyboard', user=db_user)}* - {t('mode_keyboard_desc', user=db_user)}
*{t('mode_inline', user=db_user)}* - {t('mode_inline_desc', user=db_user)}
*{t('mode_miniapp', user=db_user)}* - {t('mode_miniapp_desc', user=db_user)}
*{t('mode_auto', user=db_user)}* - {t('mode_auto_desc', user=db_user)}

{t('you_can_switch_mode', user=db_user)}
"""
    
    # 如果在群组中，提示 MiniApp 不可用
    if chat_type in ["group", "supergroup"]:
        text += f"\n{t('miniapp_not_available_in_group', user=db_user)}"
    
    keyboard = get_mode_selection_keyboard(db_user)
    
    try:
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Error editing message: {e}", exc_info=True)
        try:
            await query.message.reply_text(
                text,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e2:
            logger.error(f"Error sending new message: {e2}", exc_info=True)


def get_mode_selection_keyboard(db_user=None):
    """获取键盘模式选择键盘"""
    from bot.keyboards.unified import get_mode_selection_keyboard as get_unified_mode_keyboard
    from bot.utils.i18n import t
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    if db_user:
        # 使用i18n获取按钮文本
        keyboard = [
            [
                InlineKeyboardButton(t('mode_keyboard', user=db_user), callback_data="set_mode:keyboard"),
                InlineKeyboardButton(t('mode_inline', user=db_user), callback_data="set_mode:inline"),
            ],
            [
                InlineKeyboardButton(t('mode_miniapp', user=db_user), callback_data="set_mode:miniapp"),
                InlineKeyboardButton(t('mode_auto', user=db_user), callback_data="set_mode:auto"),
            ],
        ]
        return InlineKeyboardMarkup(keyboard)
    else:
        # 回退到旧的实现
        keyboard = get_unified_mode_keyboard()
        return keyboard
