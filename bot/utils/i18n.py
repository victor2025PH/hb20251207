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
        "selected": "已選擇",
        "displayed": "已顯示",
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
        "random_amount_desc": "隨機金額分配，領取完成後金額最大的用戶將被標記為\"最佳手氣\"",
        "fixed_amount": "红包炸弹",
        "fixed_amount_desc": "固定金額分配，如果領取金額的小數點後最後一位數字與炸彈數字相同，將觸發炸彈",
        "select_packet_count": "請選擇紅包數量：",
        "select_packet_count_range": "請選擇紅包數量（1-100）：",
        "bomb_count_restriction": "💣 紅包炸彈只能選擇 5 份（雙雷）或 10 份（單雷）",
        "double_thunder": "雙雷",
        "single_thunder": "單雷",
        "select_bomb_number": "請選擇炸彈數字（0-9）：",
        "bomb_number_hint": "如果領取金額的小數點後最後一位數字與炸彈數字相同，將觸發炸彈",
        "please_enter_amount_first": "請先輸入金額",
        "currency_label": "幣種：",
        "type_label": "類型：",
        "packet_info": "紅包信息：",
        "select_group": "請選擇群組：",
        "select_group_or_user": "請選擇群組或用戶：",
        "confirm_send_packet": "✅ 確認發送紅包",
        "please_confirm_send": "請確認是否發送：",
        "packet_sent_success": "✅ 紅包發送成功！",
        "packet_sent_to_group": "紅包已發送到群組！",
        "enter_group_id_or_username": "請輸入群組 ID 或群組用戶名：",
        "method_one": "方式一：",
        "method_two": "方式二：",
        "enter_group_id_numeric": "輸入群組 ID（數字）",
        "enter_group_username": "輸入群組用戶名（自動補全 @ 和 t.me/）",
        "group_id_example": "例如：`-1001234567890`",
        "group_username_example": "例如：`groupname` 或 `@groupname` 或 `https://t.me/groupname`",
        "no_groups_sent_packets": "暫無已發過紅包的群組，請輸入群組 ID 或鏈接。",
        "groups_sent_packets": "已發過紅包的群組：",
        "use_command_in_group": "在群組中使用命令",
        "use_command_in_target_group": "在目標群組中輸入：`/send <金額> <數量> [祝福語]`",
        "select_sent_packet_groups": "選擇已發過紅包的群組或用戶",
        "packet_ready": "✅ 紅包已準備好！",
        "select_or_enter_group": "請選擇或輸入群組：",
        "packet_ready": "✅ 紅包已準備好！",
        "select_or_enter_group": "請選擇或輸入群組：",
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
        "enter_blessing_optional": "請輸入祝福語（可選）：",
        "blessing_hint": "直接發送消息作為祝福語，或點擊使用默認祝福語",
        "use_default_blessing": "✅ 使用默認祝福語",
        "enter_blessing": "📝 輸入祝福語",
        "amount_label": "金額：",
        "quantity_label": "數量：",
        "bomb_number_label": "炸彈數字：",
        "blessing_label": "祝福語：",
        "group_id_label": "群組 ID：",
        "uuid_label": "UUID:",
        "shares": "份",
        # 群組消息
        "sent_red_packet": "{name} 發了一個紅包",
        "claim_red_packet": "🧧 搶紅包",
        "claim_red_packet_remaining": "🧧 搶紅包 ({remaining} 份剩餘)",
        "click_to_claim": "點擊下方按鈕搶紅包！",
        "claimed_red_packet": "已搶包：",
        "user_claimed": "{name} 搶到了紅包",
        "user_claimed_with_amount": "{name} 搶到了 {amount:.2f} {currency}！",
        "user_claimed_bomb": "{name} 搶到了 {amount:.2f} {currency}，💣 踩雷了！需賠付 {penalty:.2f} {currency}",
        "red_packet_completed": "✅ 紅包已搶完",
        "red_packet_leaderboard": "📊 搶包排行榜：",
        "best_luck": "🏆 {name} 是本次最佳手氣！",
        "best_luck_marker": "🏆 {name} (最佳手氣)",
        "bomb_number_display": "💣 炸彈數字: {number} | {thunder_type}",
        "total_amount_label": "💰 總金額：",
        "amount_label_short": "💰 金額：",
        "quantity_label_short": "👥 數量：",
        "sender_label": "👤 發送者：",
        "shares_label": "份",
        "random_packet_type": "🎲 手氣最佳",
        "bomb_packet_type": "💣 紅包炸彈",
        "double_thunder_text": "雙雷",
        "single_thunder_text": "單雷",
        "default_blessing": "恭喜發財",
        "enter_group_link_id": "📝 輸入群組鏈接/ID",
        "search_group": "🔍 查找群組",
        "group_hint_auto_complete": "可以直接輸入用戶名（如：`minihb2`），系統會自動補全",
        "group_hint_use_command": "也可以在目標群組中直接使用命令 `/send <金額> <數量> [祝福語]`",
        
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
        # 歡迎消息
        "welcome_greeting": "Hi {name}！",
        "welcome_description": "這裡是最有趣的紅包遊戲平台：",
        "welcome_feature_send": "• 💰 發紅包給群友",
        "welcome_feature_claim": "• 🎁 搶紅包贏大獎",
        "welcome_feature_checkin": "• 📅 每日簽到領積分",
        "welcome_feature_invite": "• 👥 邀請好友得返佣",
        "welcome_call_to_action": "快來試試吧！👇",
        # 幫助命令
        "help_title": "🧧 *Lucky Red 使用指南*",
        "help_basic_commands": "*基本命令：*",
        "help_command_start": "/start - 開始使用",
        "help_command_wallet": "/wallet - 打開錢包",
        "help_command_packets": "/packets - 打開紅包",
        "help_command_earn": "/earn - 打開賺取",
        "help_command_game": "/game - 打開遊戲",
        "help_command_profile": "/profile - 打開我的",
        "help_command_send": "/send - 發送紅包",
        "help_command_checkin": "/checkin - 每日簽到",
        "help_command_invite": "/invite - 邀請好友",
        "help_how_to_send": "*如何發紅包：*",
        "help_send_step1": "1. 在群組中輸入 /send",
        "help_send_step2": "2. 選擇金額和數量",
        "help_send_step3": "3. 發送紅包給群友",
        "help_how_to_claim": "*如何搶紅包：*",
        "help_claim_description": "點擊群組中的紅包消息即可搶",
        "help_daily_checkin": "*每日簽到：*",
        "help_checkin_description": "連續簽到7天可獲得額外獎勵！",
        "help_invite_rebate": "*邀請返佣：*",
        "help_invite_description": "邀請好友可獲得其交易的10%返佣！",
        "help_contact": "有問題？聯繫客服 @support",
        # 邀請命令
        "invite_title": "👥 *邀請好友*",
        "invite_your_link": "你的專屬邀請鏈接：",
        "invite_statistics": "📊 邀請統計：",
        "invite_count": "• 已邀請：{count} 人",
        "invite_earnings": "• 累計收益：{earnings:.2f} USDT",
        "invite_rules": "💡 邀請規則：",
        "invite_rules_description": "好友通過你的鏈接註冊後，你將獲得其所有交易的 10% 返佣！",
        "invite_share_button": "📤 分享給好友",
        "invite_share_text": "快來玩搶紅包遊戲！",
        # 打開應用命令
        "open_app_button": "🚀 打開應用",
        "open_app_message": "點擊按鈕打開 {page} 頁面：",
        # 錯誤消息
        "error_occurred": "發生錯誤，請稍後再試",
        "please_register_first": "請先使用 /start 註冊",
        # 發送紅包命令
        "send_command_group_only": "請在群組中使用此命令發送紅包",
        "send_command_usage": "用法: /send <金額> <數量> [祝福語]",
        "send_command_example": "例如: /send 10 5 恭喜發財",
        "send_command_invalid_params": "參數格式錯誤，請輸入正確的金額和數量",
        "send_command_amount_count_positive": "金額和數量必須大於0",
        "send_command_processing": "處理完成",
        # 搶紅包提示
        "claim_bomb_alert": "💣 踩雷了！需要賠付 {penalty:.2f} {currency}（{thunder_type}）",
        "claim_success_luckiest": "🎉 恭喜獲得 {amount:.2f} {currency}！\n🏆 你是最佳手氣！",
        "claim_success": "🎉 恭喜獲得 {amount:.2f} {currency}！",
        # 鍵盤處理器
        "select_operation_colon": "選擇操作：",
        "select_game": "選擇遊戲：",
        "select_view": "選擇查看：",
        "select_currency_colon": "選擇充值幣種：",
        "select_withdraw_currency": "選擇提現幣種：",
        "select_exchange_type": "選擇兌換類型：",
        "returned_to_main_menu": "已返回主菜單：",
        "returned_to_wallet": "已返回錢包：",
        "returned_to_packets": "已返回紅包菜單：",
        "open_app_prompt": "點擊按鈕打開應用：",
        "open_lucky_red": "🚀 打開 Lucky Red",
        "processing_error": "處理消息時發生錯誤，請稍後再試或使用/start 重新開始",
        "insufficient_balance_title": "❌ *餘額不足*",
        "please_recharge_first": "請先充值後再發紅包！",
        "packet_cancelled": "已取消發紅包",
        "bind_group_instruction": "請在目標群組中發送以下命令來綁定：\n\n`/bind`\n\n或者輸入群組 ID/鏈接：",
        "enter_group_id_button": "📝 輸入群組 ID",
        "enter_group_id_or_link": "請輸入群組 ID 或鏈接：\n\n例如：-1001234567890\n或：https://t.me/groupname\n或：@groupname",
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
        "functions": "功能：",
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
        "selected": "Selected",
        "displayed": "Displayed",
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
        "enter_blessing_optional": "Please enter a blessing (optional):",
        "blessing_hint": "Send a message directly as a blessing, or click to use the default blessing",
        "use_default_blessing": "✅ Use Default Blessing",
        "enter_blessing": "📝 Enter Blessing",
        "amount_label": "Amount:",
        "quantity_label": "Quantity:",
        "bomb_number_label": "Bomb Number:",
        "blessing_label": "Blessing:",
        "group_id_label": "Group ID:",
        "uuid_label": "UUID:",
        # Group messages
        "sent_red_packet": "{name} sent a red packet",
        "claim_red_packet": "🧧 Claim Red Packet",
        "claim_red_packet_remaining": "🧧 Claim Red Packet ({remaining} remaining)",
        "click_to_claim": "Click the button below to claim!",
        "claimed_red_packet": "Already claimed:",
        "user_claimed": "{name} claimed the red packet",
        "user_claimed_with_amount": "{name} claimed {amount:.2f} {currency}!",
        "user_claimed_bomb": "{name} claimed {amount:.2f} {currency}, 💣 hit the bomb! Need to pay {penalty:.2f} {currency}",
        "red_packet_completed": "✅ Red packet completed",
        "red_packet_leaderboard": "📊 Claim Leaderboard:",
        "best_luck": "🏆 {name} is the best luck!",
        "best_luck_marker": "🏆 {name} (Best Luck)",
        "bomb_number_display": "💣 Bomb Number: {number} | {thunder_type}",
        "total_amount_label": "💰 Total Amount:",
        "amount_label_short": "💰 Amount:",
        "quantity_label_short": "👥 Quantity:",
        "sender_label": "👤 Sender:",
        "shares_label": "shares",
        "default_blessing": "Best Wishes!",
        # Welcome messages
        "welcome_greeting": "Hi {name}!",
        "welcome_description": "This is the most interesting red packet game platform:",
        "welcome_feature_send": "• 💰 Send red packets to group members",
        "welcome_feature_claim": "• 🎁 Claim red packets and win prizes",
        "welcome_feature_checkin": "• 📅 Daily check-in to earn points",
        "welcome_feature_invite": "• 👥 Invite friends to get rebates",
        "welcome_call_to_action": "Come and try it! 👇",
        # Help command
        "help_title": "🧧 *Lucky Red User Guide*",
        "help_basic_commands": "*Basic Commands:*",
        "help_command_start": "/start - Start using",
        "help_command_wallet": "/wallet - Open wallet",
        "help_command_packets": "/packets - Open red packets",
        "help_command_earn": "/earn - Open earn",
        "help_command_game": "/game - Open game",
        "help_command_profile": "/profile - Open profile",
        "help_command_send": "/send - Send red packet",
        "help_command_checkin": "/checkin - Daily check-in",
        "help_command_invite": "/invite - Invite friends",
        "help_how_to_send": "*How to Send Red Packets:*",
        "help_send_step1": "1. Type /send in a group",
        "help_send_step2": "2. Select amount and quantity",
        "help_send_step3": "3. Send red packet to group members",
        "help_how_to_claim": "*How to Claim Red Packets:*",
        "help_claim_description": "Click the red packet message in the group to claim",
        "help_daily_checkin": "*Daily Check-in:*",
        "help_checkin_description": "Check in for 7 consecutive days to get extra rewards!",
        "help_invite_rebate": "*Invite Rebate:*",
        "help_invite_description": "Invite friends to get 10% rebate on all their transactions!",
        "help_contact": "Questions? Contact support @support",
        # Invite command
        "invite_title": "👥 *Invite Friends*",
        "invite_your_link": "Your exclusive invite link:",
        "invite_statistics": "📊 Invite Statistics:",
        "invite_count": "• Invited: {count} people",
        "invite_earnings": "• Total Earnings: {earnings:.2f} USDT",
        "invite_rules": "💡 Invite Rules:",
        "invite_rules_description": "After friends register through your link, you will get 10% rebate on all their transactions!",
        "invite_share_button": "📤 Share with Friends",
        "invite_share_text": "Come play the red packet game!",
        # Open app command
        "open_app_button": "🚀 Open App",
        "open_app_message": "Click the button to open the {page} page:",
        # Error messages
        "error_occurred": "An error occurred, please try again later",
        "please_register_first": "Please use /start to register first",
        # Send packet command
        "send_command_group_only": "Please use this command in a group to send red packets",
        "send_command_usage": "Usage: /send <amount> <quantity> [blessing]",
        "send_command_example": "Example: /send 10 5 Best Wishes",
        "send_command_invalid_params": "Invalid parameter format, please enter correct amount and quantity",
        "send_command_amount_count_positive": "Amount and quantity must be greater than 0",
        "send_command_processing": "Processing complete",
        # Claim red packet alerts
        "claim_bomb_alert": "💣 Hit the bomb! Need to pay {penalty:.2f} {currency} ({thunder_type})",
        "claim_success_luckiest": "🎉 Congratulations! You got {amount:.2f} {currency}!\n🏆 You are the best luck!",
        "claim_success": "🎉 Congratulations! You got {amount:.2f} {currency}!",
        # Keyboard handler
        "select_operation_colon": "Select operation:",
        "select_game": "Select game:",
        "select_view": "Select view:",
        "select_currency_colon": "Select deposit currency:",
        "select_withdraw_currency": "Select withdrawal currency:",
        "select_exchange_type": "Select exchange type:",
        "returned_to_main_menu": "Returned to main menu:",
        "returned_to_wallet": "Returned to wallet:",
        "returned_to_packets": "Returned to red packet menu:",
        "open_app_prompt": "Click the button to open the app:",
        "open_lucky_red": "🚀 Open Lucky Red",
        "processing_error": "An error occurred while processing the message, please try again later or use /start to restart",
        "insufficient_balance_title": "❌ *Insufficient Balance*",
        "please_recharge_first": "Please recharge before sending red packets!",
        "packet_cancelled": "Red packet sending cancelled",
        "bind_group_instruction": "Please send the following command in the target group to bind:\n\n`/bind`\n\nOr enter group ID/link:",
        "enter_group_id_button": "📝 Enter Group ID",
        "enter_group_id_or_link": "Please enter group ID or link:\n\nExample: -1001234567890\nOr: https://t.me/groupname\nOr: @groupname",
        "shares": "shares",
        "enter_group_link_id": "📝 Enter Group Link/ID",
        "search_group": "🔍 Search Group",
        "group_hint_auto_complete": "You can directly enter the username (e.g.: minihb2), the system will auto-complete",
        "group_hint_use_command": "You can also directly use the command `/send <amount> <quantity> [blessing]` in the target group",
        
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
        "functions": "Functions:",
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
