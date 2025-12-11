"""
Lucky Red - Bot 端多語言支持
對應 miniapp 的 I18nProvider
"""
from typing import Dict, Optional
from shared.database.connection import get_db
from shared.database.models import User
from loguru import logger

# 翻譯文本
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "zh-TW": {
        # 通用
        "welcome": "歡迎來到 Lucky Red！",
        "select_operation": "請選擇操作：",
        "return_main": "◀️ 返回主菜單",
        "cancel": "◀️ 取消",
        "confirm": "✅ 確認",
        "error": "發生錯誤，請稍後再試",
        "unrecognized": "未識別的操作，已返回主菜單：",
        "restart": "發生錯誤，請使用 /start 重新開始",
        
        # 模式選擇
        "select_mode": "請選擇您喜歡的交互方式：",
        "mode_keyboard": "⌨️ 底部鍵盤",
        "mode_inline": "🔘 內聯按鈕",
        "mode_miniapp": "📱 MiniApp",
        "mode_auto": "🔄 自動",
        "mode_keyboard_desc": "傳統 bot 體驗，在群組中也能使用",
        "mode_inline_desc": "流暢交互，點擊消息中的按鈕",
        "mode_miniapp_desc": "最豐富的功能，最佳體驗（僅私聊）",
        "mode_auto_desc": "根據上下文自動選擇最佳模式",
        "switch_mode": "🔄 切換模式",
        "mode_set": "✅ 已設置為 {mode}",
        "mode_switched": "✅ 已切換到 {mode}",
        "you_can_switch_mode": "💡 您可以隨時在主菜單中切換模式",
        "miniapp_not_available_in_group": "⚠️ 注意：MiniApp 模式在群組中不可用",
        
        # 紅包
        "packets_center": "🧧 紅包中心",
        "view_packets": "📋 查看紅包",
        "view_packets_desc": "瀏覽可搶的紅包",
        "send_packet": "➕ 發紅包",
        "send_packet_desc": "在群組中發送紅包",
        "my_packets": "🎁 我的紅包",
        "my_packets_desc": "查看我發送的紅包",
        "packets_list": "📋 可搶紅包列表",
        "no_packets_available": "目前沒有可搶的紅包",
        "packets_list_hint": "💡 提示：在群組中發送紅包，其他用戶就可以搶了",
        "view_full_list": "📱 查看完整列表",
        "remaining": "份剩餘",
        "send_packet_title": "➕ 發紅包",
        "current_balance": "當前餘額：",
        "select_currency": "請選擇紅包幣種：",
        "select_type": "請選擇類型：",
        "select_amount": "请选择或输入红包总金额：",
        "custom_amount": "📝 自定义金额",
        "enter_amount": "请输入红包总金额（数字）：\n\n例如：100",
        "invalid_amount": "请输入有效的数字，例如：100",
        "amount_must_positive": "金额必须大于0，请重新输入：",
        "random_amount": "手气最佳",
        "fixed_amount": "红包炸弹",
        "select_count": "请选择或输入数量：",
        "custom_count": "📝 自定义数量",
        "enter_count": "请输入红包数量（数字）：\n\n例如：20",
        "invalid_count": "请输入有效的数字，例如：20",
        "count_must_positive": "数量必须大于0，请重新输入：",
        "count_exceeded": "數量不能超過 {max}，請重新輸入：",
        "select_group": "輸入群組 ID 或鏈接：",
        "enter_group": "請輸入群組 ID 或鏈接：\n\n例如：-1001234567890\n或：https://t.me/groupname",
        "confirm_send": "✅ 確認發送",
        "packet_sent": "✅ 紅包發送成功！",
        "packet_failed": "❌ 發送失敗",
        "insufficient_balance": "❌ 餘額不足",
        "balance_warning": "⚠️ 注意：您的 {currency} 餘額為 `{balance:.4f}`，發送前請先充值！",
        
        # 語言
        "language": "🌐 語言",
        "switch_language": "切換語言",
        "lang_zh_tw": "繁體中文",
        "lang_zh_cn": "簡體中文",
        "lang_en": "English",
        "lang_changed": "✅ 語言已切換為 {lang}",
        # 主菜單
        "menu_wallet": "💰 錢包",
        "menu_packets": "🧧 紅包",
        "menu_earn": "📈 賺取",
        "menu_game": "🎮 遊戲",
        "menu_profile": "👤 我的",
        "menu_switch_mode": "🔄 切換模式",
        # 主菜單文本
        "lucky_red_red_packet": "🧧 Lucky Red 搶紅包",
        "total_assets": "💰 總資產",
        "energy": "能量",
        # 模式設置消息
        "mode_set_to": "✅ 已設置為 {mode}",
        "please_use_bottom_keyboard": "請使用底部鍵盤進行操作。",
        "you_can_switch_mode_in_main_menu": "您可以隨時在主菜單中切換模式。",
        "please_use_bottom_keyboard_colon": "⌨️ 請使用底部鍵盤進行操作：",
        "setting_mode": "正在設置模式...",
        "mode_set_failed": "❌ 設置模式失敗，請稍後再試\n\n如果問題持續，請聯繫管理員。",
        "miniapp_not_available_in_group_auto_switch": "⚠️ MiniApp 模式在群組中不可用，已自動切換到內聯按鈕模式。",
        "choose_your_preferred_interaction": "💡 選擇您喜歡的交互方式：",
        "using_inline_buttons": "使用內聯按鈕進行操作 👇",
        "select_function_or_command": "選擇功能或輸入命令...",
        "select_packet_operation": "選擇紅包操作...",
    },
    "zh-CN": {
        # 通用
        "welcome": "欢迎来到 Lucky Red！",
        "select_operation": "请选择操作：",
        "return_main": "◀️ 返回主菜单",
        "cancel": "◀️ 取消",
        "confirm": "✅ 确认",
        "error": "发生错误，请稍后重试",
        "unrecognized": "未识别的操作，已返回主菜单：",
        "restart": "发生错误，请使用 /start 重新开始",
        
        # 模式选择
        "select_mode": "请选择您喜欢的交互方式：",
        "mode_keyboard": "⌨️ 底部键盘",
        "mode_inline": "🔘 内联按钮",
        "mode_miniapp": "📱 MiniApp",
        "mode_auto": "🔄 自动",
        "switch_mode": "🔄 切换模式",
        "mode_set": "✅ 已设置为 {mode}",
        "mode_switched": "✅ 已切换到 {mode}",
        
        # 红包
        "packets_center": "🧧 红包中心",
        "view_packets": "📋 查看红包",
        "view_packets_desc": "浏览可抢的红包",
        "send_packet": "➕ 发红包",
        "send_packet_desc": "在群组中发送红包",
        "my_packets": "🎁 我的红包",
        "my_packets_desc": "查看我发送的红包",
        "send_packet_title": "➕ 发红包",
        "current_balance": "当前余额：",
        "select_currency": "请选择红包币种：",
        "select_type": "请选择类型：",
        "select_amount": "请选择或输入红包总金额：",
        "custom_amount": "📝 自定义金额",
        "enter_amount": "请输入红包总金额（数字）：\n\n例如：100",
        "invalid_amount": "请输入有效的数字，例如：100",
        "amount_must_positive": "金额必须大于0，请重新输入：",
        "select_count": "请选择或输入数量：",
        "custom_count": "📝 自定义数量",
        "enter_count": "请输入红包数量（数字）：\n\n例如：20",
        "invalid_count": "请输入有效的数字，例如：20",
        "count_must_positive": "数量必须大于0，请重新输入：",
        "count_exceeded": "数量不能超过 {max}，请重新输入：",
        "select_group": "输入群组 ID 或链接：",
        "enter_group": "请输入群组 ID 或链接：\n\n例如：-1001234567890\n或：https://t.me/groupname",
        "confirm_send": "✅ 确认发送",
        "packet_sent": "✅ 红包发送成功！",
        "packet_failed": "❌ 发送失败",
        "insufficient_balance": "❌ 余额不足",
        "balance_warning": "⚠️ 注意：您的 {currency} 余额为 `{balance:.4f}`，发送前请先充值！",
        
        # 语言
        "language": "🌐 语言",
        "switch_language": "切换语言",
        "lang_zh_tw": "繁體中文",
        "lang_zh_cn": "简体中文",
        "lang_en": "English",
        "lang_changed": "✅ 语言已切换为 {lang}",
        # 初始设置
        "welcome_to_lucky_red": "🧧 歡迎來到 Lucky Red！",
        "please_select_language_first": "請先選擇您的語言，然後選擇您喜歡的交互方式：",
        "language_selection": "🌐 語言選擇",
        "please_select_interface_language": "請選擇界面語言：",
        "interaction_method": "⌨️ 交互方式",
        "you_can_switch_language_mode": "💡 您可以隨時在主菜單中切換語言和模式",
        "setting_language": "正在設置語言...",
    },
    "en": {
        # 通用
        "welcome": "Welcome to Lucky Red!",
        "select_operation": "Please select an operation:",
        "return_main": "◀️ Return to Main Menu",
        "cancel": "◀️ Cancel",
        "confirm": "✅ Confirm",
        "error": "An error occurred, please try again later",
        "unrecognized": "Unrecognized operation, returned to main menu:",
        "restart": "An error occurred, please use /start to restart",
        
        # 模式选择
        "select_mode": "Please choose your preferred interaction method:",
        "mode_keyboard": "⌨️ Bottom Keyboard",
        "mode_inline": "🔘 Inline Buttons",
        "mode_miniapp": "📱 MiniApp",
        "mode_auto": "🔄 Auto",
        "mode_keyboard_desc": "Traditional bot experience, can also be used in groups",
        "mode_inline_desc": "Smooth interaction, click buttons in messages",
        "mode_miniapp_desc": "Richest features, best experience (private chat only)",
        "mode_auto_desc": "Automatically select the best mode based on context",
        "switch_mode": "🔄 Switch Mode",
        "mode_set": "✅ Set to {mode}",
        "mode_switched": "✅ Switched to {mode}",
        "you_can_switch_mode": "💡 You can switch modes anytime in the main menu",
        "miniapp_not_available_in_group": "⚠️ Note: MiniApp mode is not available in groups",
        
        # 红包
        "packets_center": "🧧 Red Packet Center",
        "view_packets": "📋 View Red Packets",
        "view_packets_desc": "Browse available red packets",
        "send_packet": "➕ Send Red Packet",
        "send_packet_desc": "Send red packets in groups",
        "my_packets": "🎁 My Red Packets",
        "my_packets_desc": "View red packets I sent",
        "packets_list": "📋 Available Red Packets",
        "no_packets_available": "Currently, there are no red packets available to grab",
        "packets_list_hint": "💡 Tip: Send red packets in a group, and other users can grab them",
        "view_full_list": "📱 View Full List",
        "remaining": "remaining",
        "send_packet_title": "➕ Send Red Packet",
        "current_balance": "Current Balance:",
        "select_currency": "Please select red packet currency:",
        "select_type": "Please select type:",
        "select_amount": "Please select or enter the total amount:",
        "custom_amount": "📝 Custom Amount",
        "enter_amount": "Please enter the total amount (number):\n\nExample: 100",
        "invalid_amount": "Please enter a valid number, e.g., 100",
        "amount_must_positive": "Amount must be greater than 0, please re-enter:",
        "random_amount": "Best Luck",
        "fixed_amount": "Red Packet Bomb",
        "select_count": "Please select or enter quantity:",
        "custom_count": "📝 Custom Quantity",
        "enter_count": "Please enter the quantity (number):\n\nExample: 20",
        "invalid_count": "Please enter a valid number, e.g., 20",
        "count_must_positive": "Quantity must be greater than 0, please re-enter:",
        "count_exceeded": "Quantity cannot exceed {max}, please re-enter:",
        "select_group": "Enter group ID or link:",
        "enter_group": "Please enter group ID or link:\n\nExample: -1001234567890\nOr: https://t.me/groupname",
        "confirm_send": "✅ Confirm Send",
        "packet_sent": "✅ Red packet sent successfully!",
        "packet_failed": "❌ Send failed",
        "insufficient_balance": "❌ Insufficient balance",
        "balance_warning": "⚠️ Note: Your {currency} balance is `{balance:.4f}`, please recharge before sending!",
        
        # 语言
        "language": "🌐 Language",
        "switch_language": "Switch Language",
        "lang_zh_tw": "繁體中文",
        "lang_zh_cn": "简体中文",
        "lang_en": "English",
        "lang_changed": "✅ Language changed to {lang}",
        # 主菜单
        "menu_wallet": "💰 Wallet",
        "menu_packets": "🧧 Red Packet",
        "menu_earn": "📈 Earn",
        "menu_game": "🎮 Game",
        "menu_profile": "👤 My",
        "menu_switch_mode": "🔄 Switch Mode",
        # 主菜单文本
        "lucky_red_red_packet": "🧧 Lucky Red Red Packet",
        "total_assets": "💰 Total Assets",
        "energy": "Energy",
        # 模式设置消息
        "mode_set_to": "✅ Set to {mode}",
        "please_use_bottom_keyboard": "Please use the bottom keyboard to operate.",
        "you_can_switch_mode_in_main_menu": "You can switch modes anytime in the main menu.",
        "please_use_bottom_keyboard_colon": "⌨️ Please use the bottom keyboard to operate:",
        "setting_mode": "Setting mode...",
        "mode_set_failed": "❌ Failed to set mode, please try again later\n\nIf the problem persists, please contact the administrator.",
        "miniapp_not_available_in_group_auto_switch": "⚠️ MiniApp mode is not available in groups, automatically switched to inline button mode.",
        "choose_your_preferred_interaction": "💡 Choose your preferred interaction method:",
        "using_inline_buttons": "Using inline buttons 👇",
        "select_function_or_command": "Select function or enter command...",
        "select_packet_operation": "Select red packet operation...",
        # 初始设置
        "welcome_to_lucky_red": "🧧 Welcome to Lucky Red!",
        "please_select_language_first": "Please select your language first, then choose your preferred interaction method:",
        "language_selection": "🌐 Language Selection",
        "please_select_interface_language": "Please select interface language:",
        "interaction_method": "⌨️ Interaction Method",
        "you_can_switch_language_mode": "💡 You can switch language and mode anytime in the main menu",
        "setting_language": "Setting language...",
    },
}


def get_user_language(user: Optional[User] = None, user_id: Optional[int] = None) -> str:
    """獲取用戶語言"""
    if user:
        try:
            # 尝试安全地访问language_code属性
            # 如果user对象已脱离会话，使用getattr应该仍然可以工作
            # 但如果属性需要延迟加载，可能会失败，所以使用try-except
            lang = getattr(user, 'language_code', None) or "zh-TW"
        except Exception as e:
            # 如果访问失败（例如对象已脱离会话），使用user_id重新查询
            logger.debug(f"Error accessing user.language_code, falling back to user_id: {e}")
            if hasattr(user, 'tg_id'):
                try:
                    with get_db() as db:
                        db_user = db.query(User).filter(User.tg_id == user.tg_id).first()
                        if db_user:
                            lang = getattr(db_user, 'language_code', None) or "zh-TW"
                        else:
                            lang = "zh-TW"
                except Exception as e2:
                    logger.error(f"Error getting user language from database: {e2}")
                    lang = "zh-TW"
            else:
                lang = "zh-TW"
    elif user_id:
        try:
            with get_db() as db:
                db_user = db.query(User).filter(User.tg_id == user_id).first()
                if db_user:
                    lang = getattr(db_user, 'language_code', None) or "zh-TW"
                else:
                    lang = "zh-TW"
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
            lang = "zh-TW"
    else:
        lang = "zh-TW"
    
    # 確保語言代碼有效
    if lang not in TRANSLATIONS:
        lang = "zh-TW"
    
    return lang


def t(key: str, user: Optional[User] = None, user_id: Optional[int] = None, **kwargs) -> str:
    """
    翻譯函數
    
    Args:
        key: 翻譯鍵
        user: 用戶對象（可選）
        user_id: 用戶 ID（可選）
        **kwargs: 格式化參數
    
    Returns:
        翻譯後的文本
    """
    lang = get_user_language(user, user_id)
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["zh-TW"])
    text = translations.get(key, key)
    
    # 格式化文本（如果提供了參數）
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            logger.warning(f"Missing format key in translation: {key}")
    
    return text


async def update_user_language(user_id: int, language: str) -> bool:
    """更新用戶語言"""
    try:
        logger.info(f"[I18N] Attempting to update language for user {user_id} to {language}")
        
        # 驗證語言代碼
        if language not in TRANSLATIONS:
            logger.warning(f"[I18N] Invalid language code '{language}', defaulting to 'zh-TW'")
            language = "zh-TW"
        
        try:
            with get_db() as db:
                user = db.query(User).filter(User.tg_id == user_id).first()
                if not user:
                    logger.error(f"[I18N] User {user_id} not found in database")
                    return False
                
                logger.debug(f"[I18N] Found user {user_id} (id={user.id}), current language: {getattr(user, 'language_code', None)}")
                
                # 更新語言
                old_language = getattr(user, 'language_code', None)
                user.language_code = language
                
                # 刷新对象以确保更改被跟踪
                db.flush()
                
                # 提交更改
                try:
                    db.commit()
                    logger.info(f"[I18N] Successfully committed language change for user {user_id}: {old_language} -> {language}")
                except Exception as commit_error:
                    logger.error(f"[I18N] Failed to commit language change for user {user_id}: {commit_error}", exc_info=True)
                    db.rollback()
                    return False
                
                # 验证更新是否成功
                db.refresh(user)
                if getattr(user, 'language_code', None) != language:
                    logger.error(f"[I18N] Language update verification failed for user {user_id}: expected {language}, got {getattr(user, 'language_code', None)}")
                    return False
                
                logger.info(f"[I18N] Successfully updated user {user_id} language to {language} (verified)")
        except Exception as db_error:
            logger.error(f"[I18N] Database error updating language for user {user_id}: {db_error}", exc_info=True)
            return False
        
        # 清除緩存
        try:
            from bot.utils.cache import UserCache
            UserCache.invalidate(user_id)
            logger.debug(f"[I18N] Cleared cache for user {user_id}")
        except Exception as cache_error:
            logger.warning(f"[I18N] Failed to clear cache for user {user_id}: {cache_error}")
            # 緩存清除失敗不應該影響語言更新
        
        return True
    except Exception as e:
        logger.error(f"[I18N] Unexpected error updating user {user_id} language to {language}: {e}", exc_info=True)
        return False
