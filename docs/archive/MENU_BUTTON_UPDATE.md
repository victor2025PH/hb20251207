# 📱 Bot 菜單按鈕更新指南

## 什麼是菜單按鈕？

菜單按鈕是顯示在 Telegram 輸入框旁邊的按鈕，點擊後可以快速訪問 Bot 的命令列表。

## 已實施的功能

### 1. 自動設置（Bot 啟動時）

Bot 啟動時會自動：
- 設置命令列表
- 設置菜單按鈕（如果支持）

### 2. 命令列表

當前設置的命令：
- `/start` - 開始使用
- `/wallet` - 我的錢包
- `/send` - 發紅包
- `/checkin` - 每日簽到
- `/invite` - 邀請好友
- `/help` - 幫助說明

## 更新菜單按鈕

### 方法 1: 重啟 Bot（推薦）

這是最簡單的方法，Bot 會自動設置菜單按鈕：

```powershell
# 1. 停止當前 Bot（在 Bot 終端窗口按 Ctrl+C）

# 2. 重新啟動
cd bot
.venv\Scripts\Activate.ps1
python main.py
```

### 方法 2: 使用更新腳本

無需重啟 Bot，直接更新：

```powershell
cd bot
.venv\Scripts\Activate.ps1
python ..\update-menu.py
```

### 方法 3: 使用 PowerShell 腳本

```powershell
.\update-bot-menu.ps1
```

## 驗證更新

更新後，在 Telegram 中：
1. 打開與 Bot 的對話
2. 查看輸入框旁邊是否有菜單按鈕（☰ 圖標）
3. 點擊按鈕應該顯示命令列表

## 如果菜單按鈕不顯示

可能的原因：
1. **Telegram 客戶端版本過舊**
   - 更新 Telegram 到最新版本

2. **Bot API 版本不支持**
   - 某些版本的 `python-telegram-bot` 可能不支持
   - 命令仍然可以通過 `/` 使用

3. **需要等待幾分鐘**
   - Telegram 可能需要一些時間來更新

## 手動測試命令

即使菜單按鈕不顯示，命令仍然可用：

```
/start
/wallet
/send
/checkin
/invite
/help
```

## 技術說明

菜單按鈕使用 Telegram Bot API 的 `setChatMenuButton` 方法：
- 類型：`commands`（顯示命令列表）
- 設置時機：Bot 啟動時（`post_init`）
- 兼容性：自動檢測並使用可用的 API

## 相關文件

- `bot/main.py` - Bot 主文件（包含菜單按鈕設置）
- `update-menu.py` - 手動更新腳本
- `update-bot-menu.ps1` - PowerShell 更新腳本
