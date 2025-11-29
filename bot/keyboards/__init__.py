"""
Lucky Red - 鍵盤生成器
統一管理所有機器人按鈕和菜單
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from shared.config.settings import get_settings

settings = get_settings()


def get_main_menu():
    """主菜單 - 對應 miniapp 底部導航"""
    keyboard = [
        [
            InlineKeyboardButton("💰 錢包", callback_data="menu:wallet"),
            InlineKeyboardButton("🧧 紅包", callback_data="menu:packets"),
        ],
        [
            InlineKeyboardButton("📈 賺取", callback_data="menu:earn"),
            InlineKeyboardButton("🎮 遊戲", callback_data="menu:game"),
        ],
        [
            InlineKeyboardButton("👤 我的", callback_data="menu:profile"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_wallet_menu():
    """錢包子菜單"""
    keyboard = [
        [
            InlineKeyboardButton("💵 充值", callback_data="wallet:deposit"),
            InlineKeyboardButton("💸 提現", callback_data="wallet:withdraw"),
        ],
        [
            InlineKeyboardButton("📜 交易記錄", callback_data="wallet:history"),
            InlineKeyboardButton("🔄 兌換", callback_data="wallet:exchange"),
        ],
        [
            InlineKeyboardButton("◀️ 返回主菜單", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_packets_menu():
    """紅包子菜單"""
    keyboard = [
        [
            InlineKeyboardButton("📋 查看紅包", callback_data="packets:list"),
            InlineKeyboardButton("➕ 發紅包", callback_data="packets:send"),
        ],
        [
            InlineKeyboardButton("🎁 我的紅包", callback_data="packets:my"),
        ],
        [
            InlineKeyboardButton("◀️ 返回主菜單", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_earn_menu():
    """賺取子菜單"""
    keyboard = [
        [
            InlineKeyboardButton("📅 每日簽到", callback_data="earn:checkin"),
            InlineKeyboardButton("👥 邀請好友", callback_data="earn:invite"),
        ],
        [
            InlineKeyboardButton("🎯 任務中心", callback_data="earn:tasks"),
            InlineKeyboardButton("🎰 幸運轉盤", web_app=WebAppInfo(url=f"{settings.MINIAPP_URL}/lucky-wheel")),
        ],
        [
            InlineKeyboardButton("◀️ 返回主菜單", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_profile_menu():
    """個人資料子菜單"""
    keyboard = [
        [
            InlineKeyboardButton("📊 我的資料", callback_data="profile:info"),
            InlineKeyboardButton("📈 統計數據", callback_data="profile:stats"),
        ],
        [
            InlineKeyboardButton("⚙️ 設置", callback_data="profile:settings"),
        ],
        [
            InlineKeyboardButton("◀️ 返回主菜單", callback_data="menu:main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_exchange_menu():
    """兌換子菜單"""
    keyboard = [
        [
            InlineKeyboardButton("USDT → TON", callback_data="exchange:usdt_ton"),
            InlineKeyboardButton("TON → USDT", callback_data="exchange:ton_usdt"),
        ],
        [
            InlineKeyboardButton("USDT → 能量", callback_data="exchange:usdt_points"),
            InlineKeyboardButton("能量 → USDT", callback_data="exchange:points_usdt"),
        ],
        [
            InlineKeyboardButton("TON → 能量", callback_data="exchange:ton_points"),
            InlineKeyboardButton("能量 → TON", callback_data="exchange:points_ton"),
        ],
        [
            InlineKeyboardButton("◀️ 返回錢包", callback_data="menu:wallet"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_wallet():
    """返回錢包菜單"""
    keyboard = [
        [InlineKeyboardButton("◀️ 返回錢包", callback_data="menu:wallet")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_main():
    """返回主菜單"""
    keyboard = [
        [InlineKeyboardButton("◀️ 返回主菜單", callback_data="menu:main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_currency_selection(action_prefix: str):
    """貨幣選擇按鈕（用於充值/提現）"""
    keyboard = [
        [
            InlineKeyboardButton("USDT", callback_data=f"{action_prefix}:usdt"),
            InlineKeyboardButton("TON", callback_data=f"{action_prefix}:ton"),
        ],
        [
            InlineKeyboardButton("◀️ 返回", callback_data="menu:wallet"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirm_cancel(confirm_data: str, cancel_data: str = "menu:main"):
    """確認/取消按鈕"""
    keyboard = [
        [
            InlineKeyboardButton("✅ 確認", callback_data=confirm_data),
            InlineKeyboardButton("❌ 取消", callback_data=cancel_data),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
