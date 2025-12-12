"""
Lucky Red - 語言切換處理器
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger

from bot.utils.user_helpers import get_user_from_update
from bot.utils.i18n import t, update_user_language, get_user_language


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理語言切換回調"""
    query = update.callback_query
    if not query:
        return
    
    user_id = update.effective_user.id if update.effective_user else None
    logger.info(f"[LANGUAGE] Received callback: '{query.data}' from user {user_id}")
    
    try:
        await query.answer()
    except Exception as e:
        logger.error(f"[LANGUAGE] Error answering query: {e}")
    
    # 解析語言代碼
    if not query.data or not query.data.startswith("language:"):
        return
    
    lang_code = query.data.split(":")[1]
    
    # 獲取用戶
    db_user = await get_user_from_update(update, context)
    if not db_user:
        from bot.utils.i18n import t
        await query.message.reply_text(t('please_register_first', user=None) if t('please_register_first', user=None) != 'please_register_first' else "請先使用 /start 註冊")
        return
    
    # 更新用戶語言
    logger.info(f"[LANGUAGE] Updating language for user {user_id} to {lang_code}")
    success = await update_user_language(user_id, lang_code)
    
    if not success:
        logger.error(f"[LANGUAGE] Failed to update language for user {user_id} to {lang_code}")
        try:
            from bot.utils.i18n import t
            await query.message.reply_text(t('language_set_failed', user=db_user) if t('language_set_failed', user=db_user) != 'language_set_failed' else "❌ 設置語言失敗，請稍後再試")
        except Exception as reply_error:
            logger.error(f"[LANGUAGE] Failed to send error message: {reply_error}")
        return
    
    # 獲取新語言名稱
    lang_names = {
        "zh-TW": t("lang_zh_tw", user=db_user),
        "zh-CN": t("lang_zh_cn", user=db_user),
        "en": t("lang_en", user=db_user),
    }
    lang_name = lang_names.get(lang_code, lang_code)
    
    # 重新獲取用戶以獲取新語言
    from shared.database.connection import get_db
    from shared.database.models import User
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == user_id).first()
        if user:
            db_user = user
    
    # 顯示確認消息
    try:
        await query.edit_message_text(
            t("lang_changed", user=db_user, lang=lang_name),
            parse_mode="Markdown",
            reply_markup=get_language_selection_keyboard(db_user)
        )
        logger.info(f"[LANGUAGE] Successfully updated language display for user {user_id}")
    except Exception as edit_error:
        logger.error(f"[LANGUAGE] Failed to edit message for user {user_id}: {edit_error}")
        # 如果编辑消息失败，尝试发送新消息
        try:
            await query.message.reply_text(
                t("lang_changed", user=db_user, lang=lang_name),
                parse_mode="Markdown",
                reply_markup=get_language_selection_keyboard(db_user)
            )
        except Exception as reply_error:
            logger.error(f"[LANGUAGE] Failed to send reply message: {reply_error}")


async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """顯示語言選擇界面"""
    query = update.callback_query if update.callback_query else None
    message = update.message if update.message else (query.message if query else None)
    
    if not message:
        return
    
    db_user = await get_user_from_update(update, context)
    if not db_user:
        if message:
            await message.reply_text("請先使用 /start 註冊")
        return
    
    text = f"""
🌐 *{t('switch_language', user=db_user)}*

{t('select_operation', user=db_user)}
"""
    
    keyboard = get_language_selection_keyboard(db_user)
    
    if query:
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        await message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )


def get_language_selection_keyboard(user):
    """獲取語言選擇鍵盤"""
    current_lang = get_user_language(user=user)
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅' if current_lang == 'zh-TW' else ''} {t('lang_zh_tw', user=user)}",
                callback_data="language:zh-TW"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if current_lang == 'zh-CN' else ''} {t('lang_zh_cn', user=user)}",
                callback_data="language:zh-CN"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if current_lang == 'en' else ''} {t('lang_en', user=user)}",
                callback_data="language:en"
            ),
        ],
        [
            InlineKeyboardButton(t("return_main", user=user), callback_data="menu:main"),
        ],
    ]
    
    return InlineKeyboardMarkup(keyboard)
