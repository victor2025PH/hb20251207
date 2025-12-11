"""
Lucky Red - 统一键盘生成器
支持三种交互模式：底部键盘、内联按钮、MiniApp
"""
from telegram import (
    ReplyKeyboardMarkup, InlineKeyboardMarkup, 
    KeyboardButton, InlineKeyboardButton, WebAppInfo
)
from shared.config.settings import get_settings

settings = get_settings()


# 菜单定义（使用函数获取翻译后的文本）
def get_menu_definitions(user=None):
    """获取翻译后的菜单定义"""
    from bot.utils.i18n import t
    
    return {
        "main": [
            (t("menu_wallet", user=user), "wallet", f"{settings.MINIAPP_URL}/wallet"),
            (t("menu_packets", user=user), "packets", f"{settings.MINIAPP_URL}/packets"),
            (t("menu_earn", user=user), "earn", f"{settings.MINIAPP_URL}/earn"),
            (t("menu_game", user=user), "game", f"{settings.MINIAPP_URL}/game"),
            (t("menu_profile", user=user), "profile", f"{settings.MINIAPP_URL}/profile"),
        ],
        "wallet": [
            (t("recharge", user=user) if t("recharge", user=user) != "recharge" else "💵 充值", "recharge", f"{settings.MINIAPP_URL}/recharge"),
            (t("withdraw", user=user) if t("withdraw", user=user) != "withdraw" else "💸 提現", "withdraw", f"{settings.MINIAPP_URL}/withdraw"),
            (t("transaction_records", user=user) if t("transaction_records", user=user) != "transaction_records" else "📜 交易記錄", "records", f"{settings.MINIAPP_URL}/wallet?tab=records"),
            (t("exchange", user=user) if t("exchange", user=user) != "exchange" else "🔄 兌換", "exchange", f"{settings.MINIAPP_URL}/exchange"),
            (t("return_main", user=user), "main", f"{settings.MINIAPP_URL}"),
        ],
        "packets": [
            (t("view_packets", user=user), "list", f"{settings.MINIAPP_URL}/packets"),
            (t("send_packet", user=user), "send", f"{settings.MINIAPP_URL}/send-red-packet"),
            (t("my_packets", user=user), "my", f"{settings.MINIAPP_URL}/packets?tab=my"),
            (t("return_main", user=user), "main", f"{settings.MINIAPP_URL}"),
        ],
        "earn": [
            (t("daily_checkin", user=user) if t("daily_checkin", user=user) != "daily_checkin" else "📅 每日簽到", "checkin", f"{settings.MINIAPP_URL}/earn?tab=checkin"),
            (t("invite_friends", user=user) if t("invite_friends", user=user) != "invite_friends" else "👥 邀請好友", "invite", f"{settings.MINIAPP_URL}/earn?tab=invite"),
            (t("task_center", user=user) if t("task_center", user=user) != "task_center" else "🎯 任務中心", "tasks", f"{settings.MINIAPP_URL}/earn?tab=tasks"),
            (t("lucky_wheel", user=user) if t("lucky_wheel", user=user) != "lucky_wheel" else "🎰 幸運轉盤", "wheel", f"{settings.MINIAPP_URL}/lucky-wheel"),
            (t("return_main", user=user), "main", f"{settings.MINIAPP_URL}"),
        ],
        "game": [
            (t("gold_game", user=user) if t("gold_game", user=user) != "gold_game" else "🎰 金運局", "gold", f"{settings.MINIAPP_URL}/game"),
            (t("lucky_wheel", user=user) if t("lucky_wheel", user=user) != "lucky_wheel" else "🎡 幸運轉盤", "wheel", f"{settings.MINIAPP_URL}/lucky-wheel"),
            (t("return_main", user=user), "main", f"{settings.MINIAPP_URL}"),
        ],
        "profile": [
            (t("my_profile", user=user) if t("my_profile", user=user) != "my_profile" else "📊 我的資料", "info", f"{settings.MINIAPP_URL}/profile"),
            (t("statistics", user=user) if t("statistics", user=user) != "statistics" else "📈 統計數據", "stats", f"{settings.MINIAPP_URL}/profile?tab=stats"),
            (t("settings", user=user), "settings", f"{settings.MINIAPP_URL}/profile?tab=settings"),
            (t("return_main", user=user), "main", f"{settings.MINIAPP_URL}"),
        ],
    }


def get_mode_indicator(mode: str, user=None) -> str:
    """获取模式指示器文本"""
    from bot.utils.i18n import t
    indicators = {
        "keyboard": t("mode_keyboard", user=user),
        "inline": t("mode_inline", user=user),
        "miniapp": t("mode_miniapp", user=user),
        "auto": t("mode_auto", user=user)
    }
    return indicators.get(mode, t("mode_keyboard", user=user))


def get_unified_keyboard(
    mode: str, 
    menu_type: str = "main", 
    chat_type: str = "private",
    user=None
):
    """
    统一键盘生成器
    
    Args:
        mode: 交互模式 ("keyboard", "inline", "miniapp", "auto")
        menu_type: 菜单类型 ("main", "wallet", "packets", etc.)
        chat_type: 聊天类型 ("private", "group", "supergroup")
        user: 用户对象（用于获取翻译）
    
    Returns:
        根据模式返回不同的键盘对象
    """
    # 如果是 auto 模式，根据聊天类型智能选择
    if mode == "auto":
        if chat_type in ["group", "supergroup"]:
            mode = "inline"  # 群组中使用内联按钮
        else:
            mode = "keyboard"  # 私聊中默认使用键盘
    
    # 如果 miniapp 模式在群组中，回退到 inline
    if mode == "miniapp" and chat_type in ["group", "supergroup"]:
        mode = "inline"
    
    # 获取菜单项（使用翻译）
    menu_defs = get_menu_definitions(user=user)
    items = menu_defs.get(menu_type, menu_defs["main"])
    
    if mode == "keyboard":
        # 底部键盘模式：使用普通文本按钮
        keyboard = []
        for i in range(0, len(items), 2):
            row = [KeyboardButton(items[i][0])]
            if i + 1 < len(items):
                row.append(KeyboardButton(items[i+1][0]))
            keyboard.append(row)
        
        # 不添加切换按钮到底部键盘（避免重复，切换模式通过内联按钮实现）
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    elif mode == "inline":
        # 内联按钮模式：使用 callback_data
        keyboard = []
        for i in range(0, len(items), 2):
            row = [
                InlineKeyboardButton(
                    items[i][0], 
                    callback_data=f"menu:{items[i][1]}"
                )
            ]
            if i + 1 < len(items):
                row.append(
                    InlineKeyboardButton(
                        items[i+1][0], 
                        callback_data=f"menu:{items[i+1][1]}"
                    )
                )
            keyboard.append(row)
        
        # 添加切换按钮
        from bot.utils.i18n import t
        keyboard.append([
            InlineKeyboardButton(t("menu_switch_mode", user=user), callback_data="switch_mode")
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    elif mode == "miniapp":
        # MiniApp 模式：使用 web_app
        keyboard = []
        for i in range(0, len(items), 2):
            row = [
                KeyboardButton(
                    items[i][0], 
                    web_app=WebAppInfo(url=items[i][2])
                )
            ]
            if i + 1 < len(items):
                row.append(
                    KeyboardButton(
                        items[i+1][0], 
                        web_app=WebAppInfo(url=items[i+1][2])
                    )
                )
            keyboard.append(row)
        
        # 添加切换按钮（使用内联按钮，因为 web_app 按钮不能切换模式）
        from bot.utils.i18n import t
        inline_keyboard = [
            [InlineKeyboardButton(t("menu_switch_mode", user=user), callback_data="switch_mode")]
        ]
        
        return {
            "reply": ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
            "inline": InlineKeyboardMarkup(inline_keyboard)
        }
    
    # 默认返回键盘模式
    return get_unified_keyboard("keyboard", menu_type, chat_type, user=user)


def get_mode_selection_keyboard(user=None):
    """获取模式选择键盘（用于首次设置）"""
    from bot.utils.i18n import t
    keyboard = [
        [
            InlineKeyboardButton(t("mode_keyboard", user=user), callback_data="set_mode:keyboard"),
            InlineKeyboardButton(t("mode_inline", user=user), callback_data="set_mode:inline"),
        ],
        [
            InlineKeyboardButton(t("mode_miniapp", user=user), callback_data="set_mode:miniapp"),
            InlineKeyboardButton(t("mode_auto", user=user), callback_data="set_mode:auto"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
