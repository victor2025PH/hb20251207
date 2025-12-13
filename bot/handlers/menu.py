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
    from bot.utils.i18n import t  # 在函数开头导入，确保始终可用
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
        # 获取 Telegram ID（用于查询和翻译）
        tg_id = update.effective_user.id if update.effective_user else None
        if not tg_id:
            await query.message.reply_text(t('please_register_first', user_id=None))
            return
        
        # 验证用户是否存在（但不使用返回的数据库ID）
        from bot.utils.user_helpers import get_user_id_from_update
        db_user_id = await get_user_id_from_update(update, context)
        if not db_user_id:
            await query.message.reply_text(t('please_register_first', user_id=tg_id))
            return
        
        # 如果是键盘模式，尝试恢复底部键盘
        from bot.utils.mode_helper import get_effective_mode
        effective_mode = get_effective_mode(tg_id, update.effective_chat.type)
        
        if effective_mode == "keyboard":
            from bot.keyboards.reply_keyboards import get_main_reply_keyboard, get_profile_reply_keyboard
            
            reply_keyboard = None
            keyboard_message = ""
            
            if action == "main":
                reply_keyboard = get_main_reply_keyboard(user_id=tg_id)
                keyboard_message = t("main_menu", user_id=tg_id)
            elif action == "profile":
                reply_keyboard = get_profile_reply_keyboard()
                keyboard_message = t("profile_center", user_id=tg_id)
            
            if reply_keyboard and query.message:
                try:
                    await query.message.reply_text(
                        keyboard_message,
                        reply_markup=reply_keyboard,
                    )
                except Exception as e:
                    logger.debug(f"Error restoring reply keyboard: {e}")
        
        if action == "main":
            await show_main_menu(query, tg_id)
        elif action == "wallet":
            await show_wallet_menu(query, tg_id)
        elif action == "packets":
            await show_packets_menu(query, tg_id)
        elif action == "earn":
            await show_earn_menu(query, tg_id)
        elif action == "game":
            await show_game_menu(query, tg_id)
        elif action == "profile":
            await show_profile_menu(query, tg_id)
        elif action == "language":
            from bot.handlers.language import show_language_selection
            await show_language_selection(update, context)
        else:
            logger.warning(f"[MENU_CALLBACK] Unknown action: {action}")
            try:
                if query.message:
                    await query.message.reply_text(f"{t('unknown_action', user_id=tg_id)}: {action}")
            except:
                pass
    except Exception as e:
        # 使用统一的错误处理函数
        from bot.utils.error_helpers import handle_error_with_ui
        await handle_error_with_ui(
            update=update,
            context=context,
            error=e,
            error_context=f"[MENU_CALLBACK] 处理菜单操作 '{action}' 时",
            show_main_menu_button=True
        )


async def show_main_menu(query, tg_id: int):
    """顯示主菜單（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    try:
        # 在會話內查詢用戶並完成所有操作
        with get_db() as db:
            user = db.query(User).filter(User.tg_id == tg_id).first()
            if not user:
                import traceback
                logger.error(f"【严重错误】[SHOW_MAIN_MENU] 用户 {tg_id} 未找到")
                traceback.print_exc()
                await query.answer(t('error_occurred', user_id=tg_id), show_alert=True)
                try:
                    await query.edit_message_text(
                        t('error_occurred', user_id=tg_id),
                        reply_markup=get_main_menu(user_id=tg_id)
                    )
                except:
                    if hasattr(query, 'message') and query.message:
                        await query.message.reply_text(
                            t('error_occurred', user_id=tg_id),
                            reply_markup=get_main_menu(user_id=tg_id)
                        )
                return
            
            # 在会话内访问所有需要的属性
            usdt = float(user.balance_usdt or 0)
            ton = float(user.balance_ton or 0)
            points = user.balance_points or 0
            
            # 在会话内获取翻译文本（使用 user_id）
            select_operation = t('select_operation', user_id=tg_id)
            lucky_red_text = t('lucky_red_red_packet', user_id=tg_id)
            total_assets_text = t('total_assets', user_id=tg_id)
            energy_text = t('energy', user_id=tg_id)
            
            text = f"""
{lucky_red_text}

{total_assets_text}
• USDT: `{usdt:.4f}`
• TON: `{ton:.4f}`
• {energy_text}: `{points}`

{select_operation}:
"""
            
            # 在会话内完成所有操作后再发送消息
            # 检查消息是否需要更新，避免"Message is not modified"错误
            try:
                await query.edit_message_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=get_main_menu(user_id=tg_id),
                )
            except Exception as edit_e:
                error_msg = str(edit_e)
                if "Message is not modified" in error_msg or "message is not modified" in error_msg.lower():
                    # 消息未修改，只显示提示，不报错
                    await query.answer(t('displayed', user_id=tg_id), show_alert=False)
                    logger.debug(f"Message not modified in show_main_menu, user {tg_id}")
                else:
                    # 其他错误，尝试发送新消息
                    logger.error(f"Error editing message in show_main_menu: {edit_e}", exc_info=True)
                    try:
                        if query.message:
                            await query.message.reply_text(
                                text,
                                parse_mode="Markdown",
                                reply_markup=get_main_menu(user_id=tg_id),
                            )
                    except Exception as reply_e:
                        logger.error(f"Error sending new message in show_main_menu: {reply_e}", exc_info=True)
                        raise
    except Exception as e:
        # 使用统一的错误处理函数
        from bot.utils.error_helpers import handle_error_with_ui
        from telegram import Update
        from telegram.ext import ContextTypes
        
        # 创建一个模拟的 update 对象用于错误处理
        class MockUpdate:
            def __init__(self, callback_query):
                self.callback_query = callback_query
                self.effective_user = callback_query.from_user if callback_query else None
        
        mock_update = MockUpdate(query)
        await handle_error_with_ui(
            update=mock_update,
            context=None,
            error=e,
            error_context="[SHOW_MAIN_MENU] 显示主菜单时",
            user_id=tg_id,
            show_main_menu_button=True
        )


async def show_wallet_menu(query, tg_id: int):
    """顯示錢包菜單（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    # 在會話內查詢用戶並獲取所有數據
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            import traceback
            logger.error(f"【严重错误】[SHOW_WALLET_MENU] 用户 {tg_id} 未找到")
            traceback.print_exc()
            await query.answer(t('error_occurred', user_id=tg_id), show_alert=True)
            await query.edit_message_text(
                t('error_occurred', user_id=tg_id),
                reply_markup=get_main_menu(user_id=tg_id)
            )
            return
        
        usdt = float(user.balance_usdt or 0)
        ton = float(user.balance_ton or 0)
        stars = user.balance_stars or 0
        points = user.balance_points or 0
        level = user.level
        xp = user.xp or 0
        
        # 在会话内获取所有翻译文本（使用 user_id）
        my_wallet_text = t('my_wallet', user_id=tg_id)
        balance_colon = t('balance_colon', user_id=tg_id)
        level_colon = t('level_colon', user_id=tg_id)
        xp_colon = t('xp_colon', user_id=tg_id)
        energy_colon = t('energy_colon', user_id=tg_id)
        select_operation = t('select_operation', user_id=tg_id)
    
    # 会话外使用预先获取的翻译文本
    
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
    
    try:
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_wallet_menu(),
        )
    except Exception as e:
        error_msg = str(e)
        if "Message is not modified" in error_msg or "message is not modified" in error_msg.lower():
            await query.answer(t('displayed', user_id=tg_id), show_alert=False)
            logger.debug(f"Message not modified in show_wallet_menu, user {tg_id}")
        else:
            logger.error(f"Error editing message in show_wallet_menu: {e}", exc_info=True)
            try:
                if query.message:
                    await query.message.reply_text(
                        text,
                        parse_mode="Markdown",
                        reply_markup=get_wallet_menu(),
                    )
            except Exception as reply_e:
                logger.error(f"Error sending new message in show_wallet_menu: {reply_e}", exc_info=True)
                # 最后的错误处理：至少显示错误消息和按钮
                try:
                    await query.message.reply_text(
                        t('error_occurred', user_id=tg_id),
                        reply_markup=get_wallet_menu()
                    )
                except:
                    pass


async def show_packets_menu(query, tg_id: int):
    """顯示紅包菜單（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    
    # 在会话内查询用户并完成所有操作
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            try:
                await query.edit_message_text(t("error", user_id=tg_id))
            except:
                if hasattr(query, 'message') and query.message:
                    await query.message.reply_text(t('error_occurred', user_id=tg_id))
            return
        
        # 在会话内获取翻译文本（使用 user_id）
        packets_center_text = t('packets_center', user_id=tg_id)
        view_packets_text = t('view_packets', user_id=tg_id)
        send_packet_text = t('send_packet', user_id=tg_id)
        my_packets_text = t('my_packets', user_id=tg_id)
        select_operation_text = t('select_operation', user_id=tg_id)
        
        # 获取功能描述
        view_packets_desc = t('view_packets_desc', user_id=tg_id)
        send_packet_desc = t('send_packet_desc', user_id=tg_id)
        my_packets_desc = t('my_packets_desc', user_id=tg_id)
        functions_label = t('functions', user_id=tg_id)
        
        # 在会话内生成键盘（使用 user_id）
        reply_markup = get_packets_menu(user_id=tg_id)
        
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
    try:
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    except Exception as e:
        error_msg = str(e)
        if "Message is not modified" in error_msg or "message is not modified" in error_msg.lower():
            await query.answer(t('displayed', user_id=tg_id), show_alert=False)
            logger.debug(f"Message not modified in show_packets_menu, user {tg_id}")
        else:
            logger.error(f"Error editing message in show_packets_menu: {e}", exc_info=True)
            try:
                if query.message:
                    await query.message.reply_text(
                        text,
                        parse_mode="Markdown",
                        reply_markup=reply_markup,
                    )
            except Exception as reply_e:
                logger.error(f"Error sending new message in show_packets_menu: {reply_e}", exc_info=True)
                # 最后的错误处理：至少显示错误消息和按钮
                try:
                    await query.message.reply_text(
                        t('error_occurred', user_id=tg_id),
                        reply_markup=reply_markup
                    )
                except:
                    pass


async def show_earn_menu(query, tg_id: int):
    """顯示賺取菜單（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    
    # 在会话内查询用户并获取翻译文本
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            try:
                await query.edit_message_text(t("error", user_id=tg_id))
            except:
                if hasattr(query, 'message') and query.message:
                    await query.message.reply_text(t('error_occurred', user_id=tg_id))
            return
        
        # 在会话内获取翻译文本（使用 user_id）
        earn_center = t('earn_center', user_id=tg_id)
        functions_label = t('functions', user_id=tg_id)
        daily_checkin = t('daily_checkin', user_id=tg_id)
        daily_checkin_desc = t('daily_checkin_desc', user_id=tg_id)
        invite_friends = t('invite_friends', user_id=tg_id)
        invite_friends_desc = t('invite_friends_desc', user_id=tg_id)
        task_center = t('task_center', user_id=tg_id)
        task_center_desc = t('task_center_desc', user_id=tg_id)
        lucky_wheel = t('lucky_wheel', user_id=tg_id)
        lucky_wheel_desc = t('lucky_wheel_desc', user_id=tg_id)
        select_operation = t('select_operation', user_id=tg_id)
    
    text = f"""
{earn_center}

*{functions_label}*
• {daily_checkin} - {daily_checkin_desc}
• {invite_friends} - {invite_friends_desc}
• {task_center} - {task_center_desc}
• {lucky_wheel} - {lucky_wheel_desc}

{select_operation}:
"""
    
    try:
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_earn_menu(),
        )
    except Exception as e:
        error_msg = str(e)
        if "Message is not modified" in error_msg or "message is not modified" in error_msg.lower():
            await query.answer(t('displayed', user_id=tg_id), show_alert=False)
            logger.debug(f"Message not modified in show_earn_menu, user {tg_id}")
        else:
            logger.error(f"Error editing message in show_earn_menu: {e}", exc_info=True)
            try:
                if query.message:
                    await query.message.reply_text(
                        text,
                        parse_mode="Markdown",
                        reply_markup=get_earn_menu(),
                    )
            except Exception as reply_e:
                logger.error(f"Error sending new message in show_earn_menu: {reply_e}", exc_info=True)
                # 最后的错误处理：至少显示错误消息和按钮
                try:
                    await query.message.reply_text(
                        t('error_occurred', user_id=tg_id),
                        reply_markup=get_earn_menu()
                    )
                except:
                    pass


async def show_game_menu(query, tg_id: int):
    """顯示遊戲菜單（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    
    # 在会话内查询用户并获取翻译文本
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            try:
                await query.edit_message_text(t("error", user_id=tg_id))
            except:
                if hasattr(query, 'message') and query.message:
                    await query.message.reply_text(t('error_occurred', user_id=tg_id))
            return
        
        # 在会话内获取翻译文本（使用 user_id）
        game_center = t('game_center', user_id=tg_id)
        functions_label = t('functions', user_id=tg_id)
        select_operation = t('select_operation', user_id=tg_id)
        game_golden_luck = t('game_golden_luck', user_id=tg_id)
        game_golden_luck_desc = t('game_golden_luck_desc', user_id=tg_id)
        lucky_wheel = t('lucky_wheel', user_id=tg_id)
        lucky_wheel_desc = t('lucky_wheel_desc', user_id=tg_id)
    
    text = f"""
{game_center}

*{functions_label}*
• {game_golden_luck} - {game_golden_luck_desc}
• {lucky_wheel} - {lucky_wheel_desc}

{select_operation}:
"""
    
    try:
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_profile_menu(),
        )
    except Exception as e:
        error_msg = str(e)
        if "Message is not modified" in error_msg or "message is not modified" in error_msg.lower():
            await query.answer(t('displayed', user_id=tg_id), show_alert=False)
            logger.debug(f"Message not modified in show_game_menu, user {tg_id}")
        else:
            logger.error(f"Error editing message in show_game_menu: {e}", exc_info=True)
            try:
                if query.message:
                    await query.message.reply_text(
                        text,
                        parse_mode="Markdown",
                        reply_markup=get_profile_menu(),
                    )
            except Exception as reply_e:
                logger.error(f"Error sending new message in show_game_menu: {reply_e}", exc_info=True)
                # 最后的错误处理：至少显示错误消息和按钮
                try:
                    await query.message.reply_text(
                        t('error_occurred', user_id=tg_id),
                        reply_markup=get_profile_menu()
                    )
                except:
                    pass


async def show_profile_menu(query, tg_id: int):
    """顯示個人資料菜單（只接受 tg_id，不接受 ORM 對象）"""
    from bot.utils.i18n import t
    
    # 在会话内查询用户并获取翻译文本
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if not user:
            try:
                await query.edit_message_text(t("error", user_id=tg_id))
            except:
                if hasattr(query, 'message') and query.message:
                    await query.message.reply_text(t('error_occurred', user_id=tg_id))
            return
        
        # 在会话内获取翻译文本（使用 user_id）
        profile_center = t('profile_center', user_id=tg_id)
        functions_label = t('functions', user_id=tg_id)
        select_operation = t('select_operation', user_id=tg_id)
        my_profile = t('my_profile', user_id=tg_id)
        my_profile_desc = t('my_profile_desc', user_id=tg_id)
        stats = t('stats', user_id=tg_id)
        stats_desc = t('stats_desc', user_id=tg_id)
        settings = t('settings', user_id=tg_id)
        settings_desc = t('settings_desc', user_id=tg_id)
    
    text = f"""
{profile_center}

*{functions_label}*
• {my_profile} - {my_profile_desc}
• {stats} - {stats_desc}
• {settings} - {settings_desc}

{select_operation}:
"""
    
    try:
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=get_profile_menu(),
        )
    except Exception as e:
        error_msg = str(e)
        if "Message is not modified" in error_msg or "message is not modified" in error_msg.lower():
            await query.answer(t('displayed', user_id=tg_id), show_alert=False)
            logger.debug(f"Message not modified in show_profile_menu, user {tg_id}")
        else:
            logger.error(f"Error editing message in show_profile_menu: {e}", exc_info=True)
            try:
                if query.message:
                    await query.message.reply_text(
                        text,
                        parse_mode="Markdown",
                        reply_markup=get_profile_menu(),
                    )
            except Exception as reply_e:
                logger.error(f"Error sending new message in show_profile_menu: {reply_e}", exc_info=True)
                # 最后的错误处理：至少显示错误消息和按钮
                try:
                    await query.message.reply_text(
                        t('error_occurred', user_id=tg_id),
                        reply_markup=get_profile_menu()
                    )
                except:
                    pass
