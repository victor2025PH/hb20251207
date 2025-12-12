"""
Lucky Red - 開始/幫助處理器
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from loguru import logger

from shared.config.settings import get_settings
from shared.database.connection import get_db
from shared.database.models import User, Transaction, CurrencyType
from bot.utils.user_helpers import get_or_create_user
from bot.utils.logging_helpers import log_user_action
from bot.constants import InviteConstants
from decimal import Decimal

settings = get_settings()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /start 命令"""
    from bot.utils.i18n import t  # 在函数开头导入，确保始终可用
    user = update.effective_user
    
    # 處理邀請碼
    invite_code = None
    if context.args and len(context.args) > 0:
        invite_code = context.args[0]
    
    # 使用統一的用戶獲取函數
    db_user = await get_or_create_user(
        tg_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        use_cache=False  # 註冊時不使用緩存，確保數據最新
    )
    
    # 在會話內獲取 invited_by 狀態（避免會話分離錯誤）
    with get_db() as db:
        # 重新查詢用戶以確保在會話內
        db_user_refreshed = db.query(User).filter(User.tg_id == user.id).first()
        if not db_user_refreshed:
            logger.error(f"User {user.id} not found after creation")
            await update.message.reply_text(t('error_occurred', user=db_user_refreshed))
            return
        
        is_new_user = not db_user_refreshed.invited_by
        
        # 處理邀請關係
        if invite_code and not db_user_refreshed.invited_by:
            inviter = db.query(User).filter(User.invite_code == invite_code).first()
            if inviter and inviter.tg_id != user.id:
                db_user_refreshed.invited_by = inviter.tg_id
                inviter.invite_count = (inviter.invite_count or 0) + 1
                
                # 發放邀請獎勵
                if InviteConstants.ENABLED:
                    # 邀請人獎勵
                    inviter_reward = InviteConstants.INVITER_REWARD
                    inviter.balance_usdt = (inviter.balance_usdt or Decimal(0)) + inviter_reward
                    inviter.invite_earnings = (inviter.invite_earnings or Decimal(0)) + inviter_reward
                    
                    # 被邀請人獎勵
                    invitee_reward = InviteConstants.INVITEE_REWARD
                    db_user_refreshed.balance_usdt = (db_user_refreshed.balance_usdt or Decimal(0)) + invitee_reward
                    
                    # 記錄交易
                    inviter_tx = Transaction(
                        user_id=inviter.id,
                        type="invite_bonus",
                        currency=CurrencyType.USDT,
                        amount=inviter_reward,
                        balance_before=inviter.balance_usdt - inviter_reward,
                        balance_after=inviter.balance_usdt,
                        note=f"邀請獎勵 - 邀請用戶 {user.id}",
                        status="completed"
                    )
                    invitee_tx = Transaction(
                        user_id=db_user_refreshed.id,
                        type="invite_bonus",
                        currency=CurrencyType.USDT,
                        amount=invitee_reward,
                        balance_before=Decimal(0),
                        balance_after=invitee_reward,
                        note=f"新用戶獎勵 - 由 {inviter.tg_id} 邀請",
                        status="completed"
                    )
                    db.add(inviter_tx)
                    db.add(invitee_tx)
                    
                    # 檢查里程碑獎勵
                    new_invite_count = inviter.invite_count
                    if new_invite_count in InviteConstants.MILESTONES:
                        milestone_reward = InviteConstants.MILESTONES[new_invite_count]
                        inviter.balance_usdt = inviter.balance_usdt + milestone_reward
                        inviter.invite_earnings = inviter.invite_earnings + milestone_reward
                        milestone_tx = Transaction(
                            user_id=inviter.id,
                            type="invite_milestone",
                            currency=CurrencyType.USDT,
                            amount=milestone_reward,
                            balance_before=inviter.balance_usdt - milestone_reward,
                            balance_after=inviter.balance_usdt,
                            note=f"邀請里程碑獎勵 - 達成 {new_invite_count} 人",
                            status="completed"
                        )
                        db.add(milestone_tx)
                        logger.info(f"User {inviter.tg_id} reached invite milestone {new_invite_count}, reward: {milestone_reward}")
                    
                    logger.info(f"Invite rewards: inviter {inviter.tg_id} +{inviter_reward}, invitee {user.id} +{invitee_reward}")
                
                db.commit()
                # 清除緩存
                from bot.utils.cache import UserCache
                UserCache.invalidate(inviter.tg_id)
                UserCache.invalidate(user.id)
                logger.info(f"User {user.id} invited by {inviter.tg_id}")
                log_user_action(user.id, "invited", {"inviter_id": inviter.tg_id, "invite_code": invite_code})
                is_new_user = False  # 更新狀態
                
                # 融合任務系統：標記邀請任務完成（異步調用API）
                try:
                    import aiohttp
                    import asyncio
                    
                    # 獲取API URL（從MINIAPP_URL推導或使用默認值）
                    api_url = getattr(settings, 'API_URL', None) or settings.MINIAPP_URL.replace('/frontend', '').replace('/dist', '')
                    if not api_url.startswith('http'):
                        api_url = f"http://127.0.0.1:8080"
                    
                    async def mark_invite_task_complete():
                        try:
                            url = f"{api_url}/api/v1/tasks/invite_friend/complete"
                            headers = {"Content-Type": "application/json"}
                            async with aiohttp.ClientSession() as session:
                                async with session.post(
                                    url,
                                    headers=headers,
                                    json={"tg_id": inviter.tg_id},
                                    timeout=aiohttp.ClientTimeout(total=5)
                                ) as resp:
                                    if resp.status == 200:
                                        logger.info(f"Marked invite task complete for user {inviter.tg_id}")
                                    else:
                                        logger.warning(f"Failed to mark invite task: {resp.status}")
                        except Exception as e:
                            logger.warning(f"Failed to mark invite task complete: {e}")
                    
                    # 異步執行，不阻塞
                    asyncio.create_task(mark_invite_task_complete())
                    
                    # 檢查成就任務（邀請5人、10人等）
                    invite_count = inviter.invite_count
                    if invite_count == 5:
                        async def mark_achievement_task(task_type):
                            try:
                                url = f"{api_url}/api/v1/tasks/{task_type}/complete"
                                headers = {"Content-Type": "application/json"}
                                async with aiohttp.ClientSession() as session:
                                    async with session.post(
                                        url,
                                        headers=headers,
                                        json={"tg_id": inviter.tg_id},
                                        timeout=aiohttp.ClientTimeout(total=5)
                                    ) as resp:
                                        if resp.status == 200:
                                            logger.info(f"Marked {task_type} achievement for user {inviter.tg_id}")
                            except Exception as e:
                                logger.warning(f"Failed to mark {task_type} achievement: {e}")
                        
                        asyncio.create_task(mark_achievement_task("invite_5"))
                    elif invite_count == 10:
                        async def mark_achievement_task(task_type):
                            try:
                                url = f"{api_url}/api/v1/tasks/{task_type}/complete"
                                headers = {"Content-Type": "application/json"}
                                async with aiohttp.ClientSession() as session:
                                    async with session.post(
                                        url,
                                        headers=headers,
                                        json={"tg_id": inviter.tg_id},
                                        timeout=aiohttp.ClientTimeout(total=5)
                                    ) as resp:
                                        if resp.status == 200:
                                            logger.info(f"Marked {task_type} achievement for user {inviter.tg_id}")
                            except Exception as e:
                                logger.warning(f"Failed to mark {task_type} achievement: {e}")
                        
                        asyncio.create_task(mark_achievement_task("invite_10"))
                except Exception as e:
                    logger.warning(f"Failed to mark invite task: {e}")
        
        # 記錄用戶操作（在會話內完成）
        log_user_action(user.id, "start", {"is_new": is_new_user})
    logger.info(f"User {user.id} ({user.username}) sent /start command")
    
    # 检查用户是否已设置交互模式
    with get_db() as db:
        db_user_refreshed = db.query(User).filter(User.tg_id == user.id).first()
        if not db_user_refreshed:
            logger.error(f"User {user.id} not found after creation")
            await update.message.reply_text(t('error_occurred', user=db_user_refreshed))
            return
        
        # 检查是否有 reset 参数（用于重新设置）
        should_reset = context.args and len(context.args) > 0 and context.args[0].lower() == "reset"
        
        # 检查用户是否已设置过模式（排除 "auto" 和 None）
        has_set_mode = db_user_refreshed.interaction_mode and db_user_refreshed.interaction_mode != "auto"
        
        # 如果是新用户、未设置模式、用户明确要求重置，或者用户删除机器人后重新启动（已设置过模式但没有邀请码参数），显示初始设置
        if should_reset or not db_user_refreshed.interaction_mode or db_user_refreshed.interaction_mode == "auto" or (has_set_mode and not invite_code):
            # 如果用户要求重置或重新启动（已设置过模式但没有邀请码），先清除现有设置
            if should_reset or (has_set_mode and not invite_code):
                old_mode = db_user_refreshed.interaction_mode
                db_user_refreshed.interaction_mode = None
                db.commit()
                if should_reset:
                    logger.info(f"User {user.id} requested reset, cleared interaction_mode")
                else:
                    logger.info(f"User {user.id} restarted bot (had mode {old_mode}), resetting to show initial setup")
            
            # 在会话内预先加载用户属性，确保后续访问不会出错
            _ = db_user_refreshed.id
            _ = db_user_refreshed.tg_id
            _ = db_user_refreshed.language_code
            _ = db_user_refreshed.interaction_mode
        
        # 会话在这里结束，但我们已经预先加载了需要的属性
        # 现在可以安全地调用 show_initial_setup
        if should_reset or not db_user_refreshed.interaction_mode or db_user_refreshed.interaction_mode == "auto" or (has_set_mode and not invite_code):
            from bot.handlers.initial_setup import show_initial_setup
            await show_initial_setup(update, context)
            return
        
        # 在会话内预先加载所有需要的属性，并获取翻译文本
        _ = db_user_refreshed.id
        _ = db_user_refreshed.tg_id
        _ = db_user_refreshed.language_code
        _ = db_user_refreshed.interaction_mode
        
        # 在会话内获取翻译文本（t 已在函数开头导入）
        welcome_msg = t('welcome', user=db_user_refreshed)
        
        # 獲取所有歡迎消息的翻譯文本
        welcome_greeting = t('welcome_greeting', user=db_user_refreshed, name=user.first_name or 'User')
        welcome_description = t('welcome_description', user=db_user_refreshed)
        welcome_feature_send = t('welcome_feature_send', user=db_user_refreshed)
        welcome_feature_claim = t('welcome_feature_claim', user=db_user_refreshed)
        welcome_feature_checkin = t('welcome_feature_checkin', user=db_user_refreshed)
        welcome_feature_invite = t('welcome_feature_invite', user=db_user_refreshed)
        welcome_call_to_action = t('welcome_call_to_action', user=db_user_refreshed)
        
        welcome_text = f"""
🧧 {welcome_msg}

{welcome_greeting}

{welcome_description}
{welcome_feature_send}
{welcome_feature_claim}
{welcome_feature_checkin}
{welcome_feature_invite}

{welcome_call_to_action}
"""
        
        # 获取用户的有效模式（在会话内）
        from bot.utils.mode_helper import get_effective_mode
        from bot.keyboards.unified import get_unified_keyboard
        
        effective_mode = get_effective_mode(db_user_refreshed, update.effective_chat.type)
        chat_type = update.effective_chat.type
        
        # 根据用户选择的模式决定显示方式
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
        
        # 创建内联按钮（主菜单 + 切换模式）- 使用翻译（t 已在函数开头导入）
        inline_keyboard = [
            [
                InlineKeyboardButton(t("menu_wallet", user=db_user_refreshed), callback_data="menu:wallet"),
                InlineKeyboardButton(t("menu_packets", user=db_user_refreshed), callback_data="menu:packets"),
            ],
            [
                InlineKeyboardButton(t("menu_earn", user=db_user_refreshed), callback_data="menu:earn"),
                InlineKeyboardButton(t("menu_game", user=db_user_refreshed), callback_data="menu:game"),
            ],
            [
                InlineKeyboardButton(t("menu_profile", user=db_user_refreshed), callback_data="menu:profile"),
            ],
            [
                InlineKeyboardButton(t("menu_switch_mode", user=db_user_refreshed), callback_data="switch_mode"),
            ],
        ]
        
        try:
            # 根据模式决定是否显示底部键盘
            if effective_mode == "keyboard":
                # 键盘模式：显示底部键盘和内联按钮
                reply_keyboard = [
                    [
                        KeyboardButton(t("menu_wallet", user=db_user_refreshed)),
                        KeyboardButton(t("menu_packets", user=db_user_refreshed)),
                    ],
                    [
                        KeyboardButton(t("menu_earn", user=db_user_refreshed)),
                        KeyboardButton(t("menu_game", user=db_user_refreshed)),
                    ],
                    [
                        KeyboardButton(t("menu_profile", user=db_user_refreshed)),
                    ],
                ]
                
                # 发送欢迎消息（带内联按钮）
                result = await update.message.reply_text(
                    welcome_text,
                    parse_mode=None,  # 不使用 Markdown，避免解析错误
                    reply_markup=InlineKeyboardMarkup(inline_keyboard),
                )
                logger.info(f"✓ Inline keyboard sent successfully to user {user.id}")
                
                # 发送底部键盘
                await update.message.reply_text(
                    t("please_use_bottom_keyboard", user=db_user_refreshed),
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
                )
            else:
                # 内联按钮模式或 MiniApp 模式：只显示内联按钮，不显示底部键盘
                result = await update.message.reply_text(
                    welcome_text,
                    parse_mode=None,  # 不使用 Markdown，避免解析错误
                    reply_markup=InlineKeyboardMarkup(inline_keyboard),
                )
                logger.info(f"✓ Inline keyboard sent successfully to user {user.id} (inline mode, no bottom keyboard)")
        except Exception as e:
            logger.error(f"✗ Error sending keyboard to user {user.id}: {e}", exc_info=True)
            await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def open_miniapp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理打開 miniapp 的命令"""
    from shared.config.settings import get_settings
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
    
    settings = get_settings()
    command = update.message.text.split()[0].replace("/", "").lower()
    
    # 根據命令映射到對應的 miniapp 頁面
    url_map = {
        "wallet": f"{settings.MINIAPP_URL}/wallet",
        "packets": f"{settings.MINIAPP_URL}/packets",
        "earn": f"{settings.MINIAPP_URL}/earn",
        "game": f"{settings.MINIAPP_URL}/game",
        "profile": f"{settings.MINIAPP_URL}/profile",
    }
    
    url = url_map.get(command, settings.MINIAPP_URL)
    
    keyboard = [[
        InlineKeyboardButton(
            "🚀 打開應用",
            web_app=WebAppInfo(url=url)
        )
    ]]
    
    # 獲取用戶以使用翻譯
    from bot.utils.user_helpers import get_user_from_update
    from bot.utils.i18n import t
    db_user = await get_user_from_update(update, context)
    if db_user:
        open_app_message = t('open_app_message', user=db_user, page=command)
        open_app_button = t('open_app_button', user=db_user)
        keyboard = [[
            InlineKeyboardButton(
                open_app_button,
                web_app=WebAppInfo(url=url)
            )
        ]]
    else:
        open_app_message = f"點擊按鈕打開 {command} 頁面："
        open_app_button = "🚀 打開應用"
    
    await update.message.reply_text(
        open_app_message,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /help 命令"""
    from bot.utils.user_helpers import get_user_from_update
    from bot.utils.i18n import t
    
    db_user = await get_user_from_update(update, context)
    if not db_user:
        db_user = await get_user_from_update(update, context, use_cache=False)
    
    if db_user:
        help_title = t('help_title', user=db_user)
        help_basic_commands = t('help_basic_commands', user=db_user)
        help_command_start = t('help_command_start', user=db_user)
        help_command_wallet = t('help_command_wallet', user=db_user)
        help_command_packets = t('help_command_packets', user=db_user)
        help_command_earn = t('help_command_earn', user=db_user)
        help_command_game = t('help_command_game', user=db_user)
        help_command_profile = t('help_command_profile', user=db_user)
        help_command_send = t('help_command_send', user=db_user)
        help_command_checkin = t('help_command_checkin', user=db_user)
        help_command_invite = t('help_command_invite', user=db_user)
        help_how_to_send = t('help_how_to_send', user=db_user)
        help_send_step1 = t('help_send_step1', user=db_user)
        help_send_step2 = t('help_send_step2', user=db_user)
        help_send_step3 = t('help_send_step3', user=db_user)
        help_how_to_claim = t('help_how_to_claim', user=db_user)
        help_claim_description = t('help_claim_description', user=db_user)
        help_daily_checkin = t('help_daily_checkin', user=db_user)
        help_checkin_description = t('help_checkin_description', user=db_user)
        help_invite_rebate = t('help_invite_rebate', user=db_user)
        help_invite_description = t('help_invite_description', user=db_user)
        help_contact = t('help_contact', user=db_user)
    else:
        # 默認中文
        help_title = "🧧 *Lucky Red 使用指南*"
        help_basic_commands = "*基本命令：*"
        help_command_start = "/start - 開始使用"
        help_command_wallet = "/wallet - 打開錢包"
        help_command_packets = "/packets - 打開紅包"
        help_command_earn = "/earn - 打開賺取"
        help_command_game = "/game - 打開遊戲"
        help_command_profile = "/profile - 打開我的"
        help_command_send = "/send - 發送紅包"
        help_command_checkin = "/checkin - 每日簽到"
        help_command_invite = "/invite - 邀請好友"
        help_how_to_send = "*如何發紅包：*"
        help_send_step1 = "1. 在群組中輸入 /send"
        help_send_step2 = "2. 選擇金額和數量"
        help_send_step3 = "3. 發送紅包給群友"
        help_how_to_claim = "*如何搶紅包：*"
        help_claim_description = "點擊群組中的紅包消息即可搶"
        help_daily_checkin = "*每日簽到：*"
        help_checkin_description = "連續簽到7天可獲得額外獎勵！"
        help_invite_rebate = "*邀請返佣：*"
        help_invite_description = "邀請好友可獲得其交易的10%返佣！"
        help_contact = "有問題？聯繫客服 @support"
    
    help_text = f"""
{help_title}

{help_basic_commands}
{help_command_start}
{help_command_wallet}
{help_command_packets}
{help_command_earn}
{help_command_game}
{help_command_profile}
{help_command_send}
{help_command_checkin}
{help_command_invite}

{help_how_to_send}
{help_send_step1}
{help_send_step2}
{help_send_step3}

{help_how_to_claim}
{help_claim_description}

{help_daily_checkin}
{help_checkin_description}

{help_invite_rebate}
{help_invite_description}

{help_contact}
"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /invite 命令"""
    from bot.utils.user_helpers import get_user_from_update
    from bot.utils.logging_helpers import log_user_action
    
    # 獲取用戶（帶緩存）
    db_user = await get_user_from_update(update, context)
    if not db_user:
        from bot.utils.i18n import t
        # 嘗試獲取用戶以使用翻譯，如果失敗則使用默認值
        try:
            with get_db() as db:
                temp_user = db.query(User).filter(User.tg_id == update.effective_user.id).first()
                if temp_user:
                    await update.message.reply_text(t('please_register_first', user=temp_user))
                else:
                    await update.message.reply_text("請先使用 /start 註冊")
        except:
            await update.message.reply_text("請先使用 /start 註冊")
        return
    
    # 在會話內處理邀請碼和獲取統計信息
    with get_db() as db:
        user = db.query(User).filter(User.tg_id == db_user.tg_id).first()
        if not user:
            from bot.utils.i18n import t
            await update.message.reply_text(t('error_occurred', user=db_user))
            return
        
        # 生成邀請碼（如果沒有）
        if not user.invite_code:
            import secrets
            user.invite_code = secrets.token_urlsafe(8)
            db.commit()
            # 清除緩存
            from bot.utils.cache import UserCache
            UserCache.invalidate(user.tg_id)
        
        invite_code = user.invite_code
        invite_count = user.invite_count or 0
        invite_earnings = float(user.invite_earnings or 0)
    
    # 記錄操作
    log_user_action(db_user.tg_id, "invite_view")
    
    invite_link = f"https://t.me/{settings.BOT_USERNAME}?start={invite_code}"
    
    # 使用翻譯文本
    from bot.utils.i18n import t
    invite_title = t('invite_title', user=user)
    invite_your_link = t('invite_your_link', user=user)
    invite_statistics = t('invite_statistics', user=user)
    invite_count_text = t('invite_count', user=user, count=invite_count)
    invite_earnings_text = t('invite_earnings', user=user, earnings=invite_earnings)
    invite_rules = t('invite_rules', user=user)
    invite_rules_description = t('invite_rules_description', user=user)
    invite_share_button = t('invite_share_button', user=user)
    invite_share_text = t('invite_share_text', user=user)
    
    invite_text = f"""
{invite_title}

{invite_your_link}
`{invite_link}`

{invite_statistics}
{invite_count_text}
{invite_earnings_text}

{invite_rules}
{invite_rules_description}
"""
    
    keyboard = [
        [InlineKeyboardButton(invite_share_button, url=f"https://t.me/share/url?url={invite_link}&text={invite_share_text}")],
    ]
    
    await update.message.reply_text(
        invite_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

