# 🔧 Bot 衝突錯誤修復指南

## 錯誤信息
```
telegram.error.Conflict: Conflict: terminated by other getUpdates request; 
make sure that only one bot instance is running
```

## 問題原因

Telegram Bot API 不允許同一個 Bot Token 同時有多個 `getUpdates` 請求。這通常發生在：
1. 有多個 Bot 實例正在運行
2. 之前的 Bot 實例沒有正確關閉
3. 在另一個終端或進程中啟動了 Bot

## 快速解決方案

### 方案 1: 使用停止腳本（推薦）

```powershell
.\stop-bot.ps1
```

這會自動：
- 查找所有正在運行的 Bot 實例
- 停止它們
- 等待進程完全終止

然後重新啟動 Bot：
```powershell
cd bot
.venv\Scripts\Activate.ps1
python main.py
```

### 方案 2: 手動停止所有 Python 進程

```powershell
# 查看所有 Python 進程
Get-Process python

# 停止特定進程（替換 PID）
Stop-Process -Id <PID> -Force

# 或停止所有 Python 進程（謹慎使用）
Get-Process python | Stop-Process -Force
```

### 方案 3: 使用任務管理器

1. 按 `Ctrl + Shift + Esc` 打開任務管理器
2. 找到所有 `python.exe` 進程
3. 右鍵點擊 → 結束任務
4. 重新啟動 Bot

## 已實施的修復

### 1. 添加了錯誤處理器

`bot/main.py` 現在包含：
- 全局錯誤處理器
- 衝突錯誤的特殊處理
- 更好的錯誤日誌

### 2. 更新了啟動腳本

`start-services.ps1` 和 `setup-and-deploy-fixed.ps1` 現在會：
- 在啟動前自動檢查舊實例
- 自動停止舊實例
- 等待進程完全終止後再啟動

### 3. 改進了 Bot 啟動配置

- 添加了 `drop_pending_updates=True` 來避免啟動時的衝突
- 添加了更好的異常處理

## 預防措施

### 1. 使用停止腳本

在啟動新實例前，總是先運行：
```powershell
.\stop-bot.ps1
```

### 2. 檢查進程

啟動前檢查：
```powershell
Get-Process python | Where-Object { $_.Path -like "*bot*" }
```

### 3. 使用單一啟動點

總是使用 `start-services.ps1` 來啟動服務，它會自動處理衝突。

## 驗證修復

修復後，Bot 應該：
1. 正常啟動，沒有衝突錯誤
2. 能夠接收和處理消息
3. 日誌中沒有 "Conflict" 錯誤

測試：
- 在 Telegram 中發送 `/start` 給 Bot
- 檢查 Bot 是否正常響應
- 查看日誌確認沒有錯誤

## 如果問題持續

1. **檢查是否有其他設備/服務器在運行 Bot**
   - 如果有，停止它們

2. **檢查 Bot Token 是否被多處使用**
   - 確保只有一個地方在使用這個 Token

3. **等待幾分鐘後重試**
   - Telegram API 可能需要時間來釋放連接

4. **使用 Webhook 模式代替 Polling**
   - 如果持續有衝突，考慮使用 Webhook 模式

## 相關文件

- `stop-bot.ps1` - 停止所有 Bot 實例的腳本
- `bot/main.py` - 已添加錯誤處理
- `start-services.ps1` - 已更新，自動處理衝突
