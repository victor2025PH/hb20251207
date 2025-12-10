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
        "switch_mode": "🔄 切換模式",
        "mode_set": "✅ 已設置為 {mode}",
        "mode_switched": "✅ 已切換到 {mode}",
        
        # 紅包
        "packets_center": "🧧 紅包中心",
        "view_packets": "📋 查看紅包",
        "send_packet": "➕ 發紅包",
        "my_packets": "🎁 我的紅包",
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
        "send_packet": "➕ 发红包",
        "my_packets": "🎁 我的红包",
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
        "switch_mode": "🔄 Switch Mode",
        "mode_set": "✅ Set to {mode}",
        "mode_switched": "✅ Switched to {mode}",
        
        # 红包
        "packets_center": "🧧 Red Packet Center",
        "view_packets": "📋 View Red Packets",
        "send_packet": "➕ Send Red Packet",
        "my_packets": "🎁 My Red Packets",
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
        
        with get_db() as db:
            user = db.query(User).filter(User.tg_id == user_id).first()
            if not user:
                logger.error(f"[I18N] User {user_id} not found in database")
                return False
            
            logger.debug(f"[I18N] Found user {user_id}, current language: {getattr(user, 'language_code', None)}")
            
            # 更新語言
            user.language_code = language
            db.commit()
            
            logger.info(f"[I18N] Successfully updated user {user_id} language to {language}")
            
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
        logger.error(f"[I18N] Error updating user {user_id} language to {language}: {e}", exc_info=True)
        return False
