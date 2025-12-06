# 🤖 Lucky Red 紅包遊戲 - AI 系統對接指南

> **發送給：** AI 聊天控制後台開發者  
> **來自：** 紅包遊戲後端開發者  
> **日期：** 2025-12-02  
> **API 版本：** v2.0

---

## 📋 概述

本文檔說明如何將您的 **AI 聊天系統** 與我們的 **紅包遊戲平台** 對接。

對接後，您的 AI 可以代替 Telegram 用戶執行以下操作：
- ✅ 查詢用戶餘額
- ✅ 獲取用戶資料
- ✅ 發送紅包
- ✅ 領取紅包
- ✅ 內部轉帳
- ✅ 查詢紅包詳情

---

## 🔐 認證方式

### API Key 認證

每次請求需要以下 HTTP Headers：

```http
Authorization: Bearer <API_KEY>
X-Telegram-User-Id: <用戶的 Telegram ID>
X-AI-System-Id: <您的 AI 系統標識>（可選）
Content-Type: application/json
```

| Header | 必填 | 說明 |
|--------|------|------|
| `Authorization` | ✅ | 格式：`Bearer your-api-key` |
| `X-Telegram-User-Id` | ✅ | 代表執行操作的用戶 Telegram ID |
| `X-AI-System-Id` | ❌ | 您的 AI 系統名稱（用於日誌追蹤） |

### 獲取 API Key

請聯繫我們獲取您的 API Key：
- **測試環境：** 開發模式下可使用任意 Key
- **生產環境：** 需要申請正式 API Key

---

## 🌐 API 基礎信息

| 環境 | Base URL |
|------|----------|
| 測試環境 | `http://localhost:8080` |
| 生產環境 | `https://api.usdt2026.cc` |

---

## 📡 API 端點詳細說明

### 1️⃣ 健康檢查

檢查 API 是否正常運行。

```http
GET /api/v2/ai/status
```

**請求範例：**
```bash
curl -X GET "http://localhost:8080/api/v2/ai/status"
```

**響應：**
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "version": "2.0",
    "endpoints": [
      "GET /api/v2/ai/status",
      "GET /api/v2/ai/wallet/balance",
      "GET /api/v2/ai/user/profile",
      "POST /api/v2/ai/packets/send",
      "POST /api/v2/ai/packets/claim",
      "POST /api/v2/ai/wallet/transfer"
    ]
  },
  "meta": {
    "timestamp": "2025-12-02T10:00:00"
  }
}
```

---

### 2️⃣ 查詢用戶餘額

獲取指定用戶的所有幣種餘額。

```http
GET /api/v2/ai/wallet/balance
```

**請求範例：**
```bash
curl -X GET "http://localhost:8080/api/v2/ai/wallet/balance" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "X-Telegram-User-Id: 123456789"
```

**響應：**
```json
{
  "success": true,
  "data": {
    "user_id": 123456789,
    "balances": {
      "usdt": 100.0,
      "ton": 5.0,
      "stars": 1000,
      "points": 500
    },
    "total_usdt_equivalent": 125.0
  },
  "meta": {
    "timestamp": "2025-12-02T10:00:00"
  }
}
```

---

### 3️⃣ 獲取用戶資料

獲取用戶的詳細資料和統計信息。

```http
GET /api/v2/ai/user/profile
```

**請求範例：**
```bash
curl -X GET "http://localhost:8080/api/v2/ai/user/profile" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "X-Telegram-User-Id: 123456789"
```

**響應：**
```json
{
  "success": true,
  "data": {
    "user_id": 123456789,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "level": 5,
    "xp": 1000,
    "invite_code": "ABC123",
    "invite_count": 10,
    "packets_sent": 50,
    "packets_claimed": 200,
    "total_sent_amount": 500.0,
    "total_claimed_amount": 300.0,
    "created_at": "2025-01-01T00:00:00"
  }
}
```

---

### 4️⃣ 發送紅包 ⭐ 核心功能

代替用戶發送紅包。

```http
POST /api/v2/ai/packets/send
```

**請求參數：**

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `currency` | string | ❌ | 幣種：`usdt`(默認), `ton`, `stars`, `points` |
| `packet_type` | string | ❌ | 類型：`random`(手氣,默認), `equal`(炸彈) |
| `total_amount` | float | ✅ | 紅包總金額 |
| `total_count` | int | ✅ | 紅包份數（1-100） |
| `message` | string | ❌ | 祝福語（默認："🤖 AI 紅包"） |
| `chat_id` | int | ❌ | 目標群組 ID（可選） |
| `bomb_number` | int | ❌ | 炸彈數字 0-9（炸彈紅包必填） |

**請求範例 - 手氣紅包：**
```bash
curl -X POST "http://localhost:8080/api/v2/ai/packets/send" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "X-Telegram-User-Id: 123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "usdt",
    "packet_type": "random",
    "total_amount": 10.0,
    "total_count": 5,
    "message": "🤖 AI 送你紅包！恭喜發財！"
  }'
```

**請求範例 - 炸彈紅包：**
```bash
curl -X POST "http://localhost:8080/api/v2/ai/packets/send" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "X-Telegram-User-Id: 123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "usdt",
    "packet_type": "equal",
    "total_amount": 10.0,
    "total_count": 10,
    "message": "💣 炸彈紅包來了！",
    "bomb_number": 7
  }'
```

**響應：**
```json
{
  "success": true,
  "data": {
    "packet_id": "abc-123-def-456",
    "packet_type": "random",
    "total_amount": 10.0,
    "total_count": 5,
    "currency": "usdt",
    "share_url": "https://t.me/your_bot/app?startapp=p_abc-123-def-456",
    "deep_link": "https://mini.usdt2026.cc/packets/abc-123-def-456",
    "remaining_balance": 90.0,
    "expires_at": "2025-12-03T10:00:00"
  }
}
```

**⚠️ 炸彈紅包規則：**
- `total_count` 必須是 `5`（雙雷）或 `10`（單雷）
- 必須提供 `bomb_number`（0-9）
- 領取金額尾數等於 `bomb_number` 時踩雷，需賠付

---

### 5️⃣ 領取紅包 ⭐ 核心功能

代替用戶領取紅包。

```http
POST /api/v2/ai/packets/claim
```

**請求參數：**

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `packet_uuid` | string | ✅ | 紅包 UUID |

**請求範例：**
```bash
curl -X POST "http://localhost:8080/api/v2/ai/packets/claim" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "X-Telegram-User-Id: 987654321" \
  -H "Content-Type: application/json" \
  -d '{
    "packet_uuid": "abc-123-def-456"
  }'
```

**響應 - 正常領取：**
```json
{
  "success": true,
  "data": {
    "packet_uuid": "abc-123-def-456",
    "claimed_amount": 2.5,
    "actual_amount": 2.5,
    "is_luckiest": false,
    "is_bomb": false,
    "penalty_amount": 0,
    "new_balance": 102.5,
    "packet_remaining_count": 4,
    "packet_status": "active",
    "message": "恭喜獲得 2.5 USDT"
  }
}
```

**響應 - 踩雷：**
```json
{
  "success": true,
  "data": {
    "packet_uuid": "abc-123-def-456",
    "claimed_amount": 1.07,
    "actual_amount": -0.07,
    "is_luckiest": false,
    "is_bomb": true,
    "penalty_amount": 1.07,
    "new_balance": 98.93,
    "packet_remaining_count": 4,
    "packet_status": "active",
    "message": "💣 踩雷！賠付 1.07"
  }
}
```

---

### 6️⃣ 內部轉帳

用戶之間零手續費轉帳。

```http
POST /api/v2/ai/wallet/transfer
```

**請求參數：**

| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `to_user_id` | int | ✅ | 接收者 Telegram ID |
| `currency` | string | ❌ | 幣種（默認：usdt） |
| `amount` | float | ✅ | 轉帳金額 |
| `note` | string | ❌ | 備註 |

**請求範例：**
```bash
curl -X POST "http://localhost:8080/api/v2/ai/wallet/transfer" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "X-Telegram-User-Id: 123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "to_user_id": 987654321,
    "currency": "usdt",
    "amount": 10.0,
    "note": "AI 機器人轉帳"
  }'
```

**響應：**
```json
{
  "success": true,
  "data": {
    "transaction_id": "tx-uuid-xxx",
    "from_user_id": 123456789,
    "to_user_id": 987654321,
    "currency": "usdt",
    "amount": 10.0,
    "from_balance_after": 90.0,
    "to_balance_after": 110.0,
    "message": "成功轉帳 10 USDT"
  }
}
```

---

### 7️⃣ 獲取紅包詳情

查詢紅包的詳細信息。

```http
GET /api/v2/ai/packets/{packet_uuid}
```

**請求範例：**
```bash
curl -X GET "http://localhost:8080/api/v2/ai/packets/abc-123-def-456" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "X-Telegram-User-Id: 123456789"
```

**響應：**
```json
{
  "success": true,
  "data": {
    "packet_uuid": "abc-123-def-456",
    "sender": {
      "tg_id": 123456789,
      "username": "john_doe",
      "first_name": "John"
    },
    "currency": "usdt",
    "packet_type": "random",
    "total_amount": 10.0,
    "total_count": 5,
    "claimed_amount": 5.0,
    "claimed_count": 2,
    "remaining_amount": 5.0,
    "remaining_count": 3,
    "message": "恭喜發財！",
    "bomb_number": null,
    "status": "active",
    "created_at": "2025-12-02T10:00:00",
    "expires_at": "2025-12-03T10:00:00",
    "claims_count": 2
  }
}
```

---

## ❌ 錯誤處理

### 錯誤響應格式

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "錯誤描述"
  }
}
```

### 常見錯誤碼

| HTTP 狀態碼 | 錯誤類型 | 說明 | 處理建議 |
|------------|---------|------|---------|
| 401 | `Unauthorized` | API Key 無效 | 檢查 Authorization header |
| 403 | `Forbidden` | 用戶被封禁 | 聯繫管理員 |
| 404 | `Not Found` | 用戶/紅包不存在 | 檢查 ID 是否正確 |
| 400 | `Bad Request` | 參數錯誤 | 檢查請求參數 |
| 400 | `Insufficient balance` | 餘額不足 | 提示用戶充值 |
| 400 | `Already claimed` | 已經領取過 | 提示用戶已領取 |
| 400 | `Packet is empty` | 紅包已領完 | 提示紅包已空 |
| 400 | `Packet expired` | 紅包已過期 | 提示已過期 |
| 429 | `Too Many Requests` | 請求過於頻繁 | 降低請求頻率 |

---

## 💻 Python SDK 範例代碼

以下是可以直接使用的 Python SDK：

```python
"""
Lucky Red AI API Client
複製此文件到您的項目中使用
"""
import httpx
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class APIResponse:
    success: bool
    data: Optional[Dict[str, Any]]
    error: Optional[Dict[str, Any]]


class LuckyRedAIClient:
    """Lucky Red 紅包遊戲 AI API 客戶端"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8080",
        ai_system_id: str = "ai-chat-system",
        timeout: float = 30.0
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.ai_system_id = ai_system_id
        self.timeout = timeout
    
    def _get_headers(self, telegram_user_id: int) -> Dict[str, str]:
        """生成請求 headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-Telegram-User-Id": str(telegram_user_id),
            "X-AI-System-Id": self.ai_system_id,
            "Content-Type": "application/json"
        }
    
    def _handle_response(self, response: httpx.Response) -> APIResponse:
        """處理 API 響應"""
        data = response.json()
        return APIResponse(
            success=data.get("success", False),
            data=data.get("data"),
            error=data.get("error")
        )
    
    # ========== 同步方法 ==========
    
    def get_balance(self, telegram_user_id: int) -> APIResponse:
        """查詢用戶餘額"""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/api/v2/ai/wallet/balance",
                headers=self._get_headers(telegram_user_id)
            )
            return self._handle_response(response)
    
    def get_profile(self, telegram_user_id: int) -> APIResponse:
        """獲取用戶資料"""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/api/v2/ai/user/profile",
                headers=self._get_headers(telegram_user_id)
            )
            return self._handle_response(response)
    
    def send_packet(
        self,
        telegram_user_id: int,
        total_amount: float,
        total_count: int,
        currency: str = "usdt",
        packet_type: str = "random",
        message: str = "🤖 AI 紅包",
        chat_id: Optional[int] = None,
        bomb_number: Optional[int] = None
    ) -> APIResponse:
        """發送紅包"""
        payload = {
            "currency": currency,
            "packet_type": packet_type,
            "total_amount": total_amount,
            "total_count": total_count,
            "message": message
        }
        if chat_id:
            payload["chat_id"] = chat_id
        if bomb_number is not None:
            payload["bomb_number"] = bomb_number
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/api/v2/ai/packets/send",
                headers=self._get_headers(telegram_user_id),
                json=payload
            )
            return self._handle_response(response)
    
    def claim_packet(
        self,
        telegram_user_id: int,
        packet_uuid: str
    ) -> APIResponse:
        """領取紅包"""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/api/v2/ai/packets/claim",
                headers=self._get_headers(telegram_user_id),
                json={"packet_uuid": packet_uuid}
            )
            return self._handle_response(response)
    
    def transfer(
        self,
        from_user_id: int,
        to_user_id: int,
        amount: float,
        currency: str = "usdt",
        note: str = ""
    ) -> APIResponse:
        """內部轉帳"""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/api/v2/ai/wallet/transfer",
                headers=self._get_headers(from_user_id),
                json={
                    "to_user_id": to_user_id,
                    "currency": currency,
                    "amount": amount,
                    "note": note
                }
            )
            return self._handle_response(response)
    
    def get_packet_info(
        self,
        telegram_user_id: int,
        packet_uuid: str
    ) -> APIResponse:
        """獲取紅包詳情"""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(
                f"{self.base_url}/api/v2/ai/packets/{packet_uuid}",
                headers=self._get_headers(telegram_user_id)
            )
            return self._handle_response(response)
    
    # ========== 異步方法 ==========
    
    async def async_get_balance(self, telegram_user_id: int) -> APIResponse:
        """異步查詢用戶餘額"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v2/ai/wallet/balance",
                headers=self._get_headers(telegram_user_id)
            )
            return self._handle_response(response)
    
    async def async_send_packet(
        self,
        telegram_user_id: int,
        total_amount: float,
        total_count: int,
        **kwargs
    ) -> APIResponse:
        """異步發送紅包"""
        payload = {
            "currency": kwargs.get("currency", "usdt"),
            "packet_type": kwargs.get("packet_type", "random"),
            "total_amount": total_amount,
            "total_count": total_count,
            "message": kwargs.get("message", "🤖 AI 紅包")
        }
        if kwargs.get("chat_id"):
            payload["chat_id"] = kwargs["chat_id"]
        if kwargs.get("bomb_number") is not None:
            payload["bomb_number"] = kwargs["bomb_number"]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v2/ai/packets/send",
                headers=self._get_headers(telegram_user_id),
                json=payload
            )
            return self._handle_response(response)
    
    async def async_claim_packet(
        self,
        telegram_user_id: int,
        packet_uuid: str
    ) -> APIResponse:
        """異步領取紅包"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/v2/ai/packets/claim",
                headers=self._get_headers(telegram_user_id),
                json={"packet_uuid": packet_uuid}
            )
            return self._handle_response(response)


# ========== 使用範例 ==========

if __name__ == "__main__":
    # 初始化客戶端
    client = LuckyRedAIClient(
        api_key="your-api-key-here",
        base_url="http://localhost:8080",
        ai_system_id="my-ai-chat-bot"
    )
    
    # 範例 1: 查詢餘額
    result = client.get_balance(telegram_user_id=123456789)
    if result.success:
        print(f"USDT 餘額: {result.data['balances']['usdt']}")
    else:
        print(f"錯誤: {result.error}")
    
    # 範例 2: 發送紅包
    result = client.send_packet(
        telegram_user_id=123456789,
        total_amount=10.0,
        total_count=5,
        message="AI 祝你好運！🎉"
    )
    if result.success:
        packet_id = result.data['packet_id']
        share_url = result.data['share_url']
        print(f"紅包已發送！ID: {packet_id}")
        print(f"分享連結: {share_url}")
    
    # 範例 3: 領取紅包
    result = client.claim_packet(
        telegram_user_id=987654321,
        packet_uuid="abc-123-def-456"
    )
    if result.success:
        amount = result.data['claimed_amount']
        print(f"成功領取 {amount} USDT！")
        if result.data['is_bomb']:
            print(f"💣 踩雷了！賠付 {result.data['penalty_amount']}")
```

---

## 🔄 對接流程

### 步驟 1：獲取 API Key

聯繫紅包遊戲管理員獲取：
- 測試環境 API Key
- 生產環境 API Key

### 步驟 2：集成 SDK

1. 複製上方的 Python SDK 代碼
2. 安裝依賴：`pip install httpx`
3. 初始化客戶端

### 步驟 3：實現 AI 指令

在您的 AI 聊天系統中，當用戶說出相關指令時調用對應 API：

| 用戶指令範例 | 調用 API |
|-------------|---------|
| "查看我的餘額" | `get_balance()` |
| "發 10 USDT 紅包，5 個人分" | `send_packet(amount=10, count=5)` |
| "領取紅包 xxx" | `claim_packet(packet_uuid="xxx")` |
| "轉帳 5 USDT 給 @user" | `transfer(to_user_id=xxx, amount=5)` |

### 步驟 4：測試驗證

使用測試環境進行完整測試：
1. 創建測試用戶
2. 充值測試餘額
3. 測試所有 API 端點

---

## 📞 聯繫方式

如有問題，請聯繫：
- **技術對接：** [您的聯繫方式]
- **API 文檔：** 本文檔
- **問題反饋：** [Issue 追蹤地址]

---

## 📝 更新日誌

| 版本 | 日期 | 更新內容 |
|------|------|---------|
| v2.0 | 2025-12-02 | 初始版本，支持基礎紅包操作 |

---

**祝對接順利！🚀**
