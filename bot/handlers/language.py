"""
Lucky Red - 語言切換處理器
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger

from bot.utils.user_helpers import get_user_id_from_update
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
    
    # 獲取用戶 ID（不返回 ORM 對象）
    tg_id = await get_user_id_from_update(update, context)
    if not tg_id:
        await query.message.reply_text(t('please_register_first', user_id=user_id))
        return
    
    # 更新用戶語言
    logger.info(f"[LANGUAGE] Updating language for user {user_id} to {lang_code}")
    success = await update_user_language(user_id, lang_code)
    
    if not success:
        logger.error(f"[LANGUAGE] Failed to update language for user {user_id} to {lang_code}")
        try:
            await query.message.reply_text(t('language_set_failed', user_id=tg_id))
        except Exception as reply_error:
            logger.error(f"[LANGUAGE] Failed to send error message: {reply_error}")
        return
    
    # 獲取新語言名稱（使用臨時 lang_code 來獲取翻譯）
    lang_names = {
        "zh-TW": t("lang_zh_tw", user_id=user_id),
        "zh-CN": t("lang_zh_cn", user_id=user_id),
        "en": t("lang_en", user_id=user_id),
    }
    lang_name = lang_names.get(lang_code, lang_code)
    
    # 顯示確認消息（使用更新後的語言）
    try:
        # 清除緩存以確保使用新語言
        from bot.utils.cache import UserCache
        UserCache.invalidate(user_id)
        
        # 使用新語言獲取翻譯
        await query.edit_message_text(
            t("lang_changed", user_id=user_id, lang=lang_name),
            parse_mode="Markdown",
            reply_markup=get_language_selection_keyboard(user_id)
        )
        logger.info(f"[LANGUAGE] Successfully updated language display for user {user_id}")
    except Exception as edit_error:
        logger.error(f"[LANGUAGE] Failed to edit message for user {user_id}: {edit_error}")
        # 如果编辑消息失败，尝试发送新消息
        try:
            await query.message.reply_text(
                t("lang_changed", user_id=user_id, lang=lang_name),
                parse_mode="Markdown",
                reply_markup=get_language_selection_keyboard(user_id)
            )
        except Exception as reply_error:
            logger.error(f"[LANGUAGE] Failed to send reply message: {reply_error}")


async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """顯示語言選擇界面"""
    query = update.callback_query if update.callback_query else None
    message = update.message if update.message else (query.message if query else None)
    
    if not message:
        return
    
    user_id = update.effective_user.id if update.effective_user else None
    tg_id = await get_user_id_from_update(update, context)
    if not tg_id:
        if message:
            await message.reply_text("請先使用 /start 註冊")
        return
    
    text = f"""
🌐 *{t('switch_language', user_id=tg_id)}*

{t('select_operation', user_id=tg_id)}
"""
    
    keyboard = get_language_selection_keyboard(tg_id)
    
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


def get_language_selection_keyboard(user_id: int):
    """獲取語言選擇鍵盤（只接受 user_id，不接受 ORM 對象）"""
    current_lang = get_user_language(user_id=user_id)
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"{'✅' if current_lang == 'zh-TW' else ''} {t('lang_zh_tw', user_id=user_id)}",
                callback_data="language:zh-TW"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if current_lang == 'zh-CN' else ''} {t('lang_zh_cn', user_id=user_id)}",
                callback_data="language:zh-CN"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{'✅' if current_lang == 'en' else ''} {t('lang_en', user_id=user_id)}",
                callback_data="language:en"
            ),
        ],
        [
            InlineKeyboardButton(t("return_main", user_id=user_id), callback_data="menu:main"),
        ],
    ]
    
    return InlineKeyboardMarkup(keyboard)
