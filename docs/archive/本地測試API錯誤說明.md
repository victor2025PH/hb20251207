# 本地測試 API 錯誤說明

## ✅ 已修復的問題

### 1. 422 錯誤：`/api/v1/users/me` 路由衝突
**問題：** 前端調用 `/api/v1/users/me`，但後端只有 `/{user_id}` 路由，FastAPI 將 "me" 當作 `user_id` 參數，但期望整數，導致 422 錯誤。

**修復：**
- ✅ 添加了 `/me` 端點來獲取當前用戶資料
- ✅ 將管理後台的 `/{user_id}` 改為 `/detail/{user_id}` 以避免路由衝突

**結果：** 現在 `/api/v1/users/me` 可以正常工作，不再出現 422 錯誤。

## ⚠️ 正常的錯誤（無需修復）

### 1. 401 Unauthorized 錯誤
**錯誤信息：**
```
GET http://localhost:3001/api/v1/messages/unread-count 401 (Unauthorized)
GET http://localhost:3001/api/v1/users/me/balance 401 (Unauthorized)
'Telegram user ID is required'
```

**原因：** 本地測試時，瀏覽器沒有 Telegram MiniApp 環境，無法提供有效的 Telegram 認證數據（`X-Telegram-Init-Data` header）。

**解決方案：**
- 這是**正常現象**，不影響前端 UI 的測試
- 要測試完整功能，需要在 Telegram MiniApp 環境中運行
- 或者可以暫時修改 API 代碼，在開發環境中跳過認證（不推薦用於生產環境）

### 2. WebSocket 連接失敗
**錯誤信息：**
```
WebSocket Disconnected
WebSocket Reconnecting in 1000ms (attempt 1)
[NotificationManager] Failed to initialize: Connection failed
```

**原因：** WebSocket 連接也需要 Telegram 認證，本地測試時無法提供。

**解決方案：**
- 這是**正常現象**，不影響主要功能測試
- 消息通知功能需要在 Telegram MiniApp 環境中測試

## 🧪 測試建議

### 可以測試的功能（無需認證）
- ✅ 前端 UI 界面
- ✅ 頁面導航
- ✅ 遊戲規則彈窗
- ✅ 按鈕樣式和特效
- ✅ 表單驗證
- ✅ 本地存儲（localStorage）

### 需要認證的功能（本地測試會失敗）
- ❌ 獲取用戶資料
- ❌ 獲取餘額
- ❌ 發送紅包
- ❌ 領取紅包
- ❌ 消息通知
- ❌ WebSocket 連接

## 🔧 如何測試完整功能

### 方法 1：在 Telegram MiniApp 中測試（推薦）
1. 部署前端到服務器
2. 在 Telegram Bot 中打開 MiniApp
3. 這樣就有完整的 Telegram 認證數據

### 方法 2：模擬認證數據（僅開發測試）
可以在開發環境中暫時跳過認證，但**不要**用於生產環境。

## 📊 當前狀態

### 前端服務器
- ✅ 運行正常：http://localhost:3001
- ✅ UI 可以正常顯示
- ✅ 路由正常工作

### API 服務器
- ✅ 運行正常：http://localhost:8080
- ✅ `/api/v1/users/me` 端點已添加
- ⚠️ 需要 Telegram 認證才能獲取數據

### 控制台錯誤
- ✅ 422 錯誤已修復
- ⚠️ 401 錯誤是正常的（缺少認證）
- ⚠️ WebSocket 錯誤是正常的（缺少認證）

## 🎯 測試重點

現在可以重點測試：
1. **遊戲規則彈窗** - 應該可以正常顯示
2. **按鈕特效** - 發光效果應該正常
3. **「以後不再彈出」功能** - localStorage 應該正常工作
4. **頁面導航** - 所有頁面應該可以正常切換

API 相關的錯誤可以暫時忽略，因為這些是認證問題，不是代碼問題。
