"""
Lucky Red - 错误处理辅助函数
统一处理错误消息和按钮保留
"""
import traceback
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from bot.utils.i18n import t
from bot.keyboards import get_main_menu


async def handle_error_with_ui(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    error: Exception,
    error_context: str = "",
    user_id: Optional[int] = None,
    show_main_menu_button: bool = True
):
    """
    统一的错误处理函数，确保：
    1. 打印完整的 traceback
    2. 如果是 CallbackQuery，使用 query.answer
    3. 如果必须发送消息，确保带返回主菜单按钮
    
    Args:
        update: Telegram Update 对象
        context: Context 对象
        error: 捕获的异常
        error_context: 错误上下文描述（用于日志）
        user_id: 用户 ID（如果为 None，会从 update 中获取）
        show_main_menu_button: 是否显示主菜单按钮
    """
    import traceback
    
    # 获取用户 ID
    if user_id is None:
        if update.effective_user:
            user_id = update.effective_user.id
        else:
            user_id = None
    
    # 打印完整的错误信息和堆栈
    error_msg = str(error)
    error_type = type(error).__name__
    
    logger.error(
        f"【严重错误】{error_context} | "
        f"类型: {error_type} | "
        f"消息: {error_msg} | "
        f"用户ID: {user_id}"
    )
    
    # 打印完整的 traceback
    logger.error("=" * 80)
    logger.error(f"完整堆栈信息 ({error_context}):")
    traceback.print_exc()
    logger.error("=" * 80)
    
    # 处理 CallbackQuery
    if update.callback_query:
        query = update.callback_query
        try:
            # 优先使用 query.answer 显示错误提示
            error_text = t('error_occurred', user_id=user_id)
            await query.answer(error_text, show_alert=True)
            
            # 如果必须编辑消息，确保带按钮
            if show_main_menu_button:
                try:
                    await query.edit_message_text(
                        error_text,
                        reply_markup=get_main_menu(user_id=user_id)
                    )
                except Exception as edit_e:
                    # 如果编辑失败，尝试发送新消息
                    if query.message:
                        try:
                            await query.message.reply_text(
                                error_text,
                                reply_markup=get_main_menu(user_id=user_id)
                            )
                        except Exception as reply_e:
                            logger.error(f"发送错误消息也失败: {reply_e}", exc_info=True)
        except Exception as alert_error:
            logger.error(f"显示错误提示失败: {alert_error}", exc_info=True)
            # 最后的尝试：至少发送一个带按钮的消息
            if query.message and show_main_menu_button:
                try:
                    await query.message.reply_text(
                        t('error_occurred', user_id=user_id),
                        reply_markup=get_main_menu(user_id=user_id)
                    )
                except:
                    pass
    
    # 处理 Message
    elif update.message:
        try:
            error_text = t('error_occurred', user_id=user_id)
            if show_main_menu_button:
                # 发送错误消息，带返回主菜单按钮
                await update.message.reply_text(
                    error_text,
                    reply_markup=get_main_menu(user_id=user_id)
                )
            else:
                # 不带按钮的情况（很少见）
                await update.message.reply_text(error_text)
        except Exception as msg_error:
            logger.error(f"发送错误消息失败: {msg_error}", exc_info=True)

