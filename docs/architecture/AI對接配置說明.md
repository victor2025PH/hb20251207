# 🤖 AI 系統對接配置說明

**文件路徑：** `c:\hbgm001\docs\architecture\AI對接配置說明.md`

---

## 配置步驟

### 1. 環境變數配置

在 `.env` 文件中添加：

```env
# AI 系統對接配置
AI_API_KEY=your-secret-api-key-here  # 設定 AI 系統的 API 金鑰
AI_API_RATE_LIMIT=100                 # 每分鐘請求限制
```

> **注意：** 如果 `AI_API_KEY` 留空，開發模式下允許任意金鑰

---

## API 使用範例

### 認證方式

所有 AI API 請求需要以下 Headers：

```http
Authorization: Bearer <AI_API_KEY>
X-Telegram-User-Id: <代表的用戶 Telegram ID>
X-AI-System-Id: <AI 系統標識（可選）>
```

### 範例：查詢用戶餘額

```bash
curl -X GET "http://localhost:8080/api/v2/ai/wallet/balance" \
  -H "Authorization: Bearer your-secret-api-key-here" \
  -H "X-Telegram-User-Id: 123456789" \
  -H "X-AI-System-Id: my-ai-bot"
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

### 範例：發送紅包

```bash
curl -X POST "http://localhost:8080/api/v2/ai/packets/send" \
  -H "Authorization: Bearer your-secret-api-key-here" \
  -H "X-Telegram-User-Id: 123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "usdt",
    "packet_type": "random",
    "total_amount": 10.0,
    "total_count": 5,
    "message": "🤖 AI 發的紅包！"
  }'
```

**響應：**
```json
{
  "success": true,
  "data": {
    "packet_id": "abc-123-def",
    "packet_type": "random",
    "total_amount": 10.0,
    "total_count": 5,
    "currency": "usdt",
    "share_url": "https://t.me/your_bot/app?startapp=p_abc-123-def",
    "deep_link": "https://mini.usdt2026.cc/packets/abc-123-def",
    "remaining_balance": 90.0,
    "expires_at": "2025-12-03T10:00:00"
  }
}
```

### 範例：領取紅包

```bash
curl -X POST "http://localhost:8080/api/v2/ai/packets/claim" \
  -H "Authorization: Bearer your-secret-api-key-here" \
  -H "X-Telegram-User-Id: 987654321" \
  -H "Content-Type: application/json" \
  -d '{
    "packet_uuid": "abc-123-def"
  }'
```

### 範例：內部轉帳

```bash
curl -X POST "http://localhost:8080/api/v2/ai/wallet/transfer" \
  -H "Authorization: Bearer your-secret-api-key-here" \
  -H "X-Telegram-User-Id: 123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "to_user_id": 987654321,
    "currency": "usdt",
    "amount": 10.0,
    "note": "AI 機器人轉帳"
  }'
```

---

## API 端點清單

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/v2/ai/status` | GET | 健康檢查 |
| `/api/v2/ai/wallet/balance` | GET | 查詢餘額 |
| `/api/v2/ai/user/profile` | GET | 獲取用戶資料 |
| `/api/v2/ai/packets/send` | POST | 發送紅包 |
| `/api/v2/ai/packets/claim` | POST | 領取紅包 |
| `/api/v2/ai/packets/{uuid}` | GET | 獲取紅包詳情 |
| `/api/v2/ai/wallet/transfer` | POST | 內部轉帳 |

---

## 錯誤碼

| HTTP 狀態碼 | 錯誤類型 | 說明 |
|------------|---------|------|
| 401 | Unauthorized | API Key 無效 |
| 403 | Forbidden | 用戶被封禁 |
| 404 | Not Found | 用戶/紅包不存在 |
| 400 | Bad Request | 參數錯誤或餘額不足 |
| 429 | Too Many Requests | 超過速率限制 |

---

## Python SDK 範例

```python
import httpx
from typing import Optional

class LuckyRedAIClient:
    """Lucky Red AI API 客戶端"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8080",
        ai_system_id: str = "my-ai-bot"
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.ai_system_id = ai_system_id
    
    def _get_headers(self, telegram_user_id: int) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-Telegram-User-Id": str(telegram_user_id),
            "X-AI-System-Id": self.ai_system_id,
            "Content-Type": "application/json"
        }
    
    async def get_balance(self, telegram_user_id: int) -> dict:
        """獲取用戶餘額"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v2/ai/wallet/balance",
                headers=self._get_headers(telegram_user_id)
            )
            response.raise_for_status()
            return response.json()
    
    async def send_packet(
        self,
        telegram_user_id: int,
        total_amount: float,
        total_count: int,
        currency: str = "usdt",
        packet_type: str = "random",
        message: str = "🤖 AI 紅包",
        bomb_number: Optional[int] = None
    ) -> dict:
        """發送紅包"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v2/ai/packets/send",
                headers=self._get_headers(telegram_user_id),
                json={
                    "currency": currency,
                    "packet_type": packet_type,
                    "total_amount": total_amount,
                    "total_count": total_count,
                    "message": message,
                    "bomb_number": bomb_number
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def claim_packet(
        self,
        telegram_user_id: int,
        packet_uuid: str
    ) -> dict:
        """領取紅包"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v2/ai/packets/claim",
                headers=self._get_headers(telegram_user_id),
                json={"packet_uuid": packet_uuid}
            )
            response.raise_for_status()
            return response.json()
    
    async def transfer(
        self,
        from_user_id: int,
        to_user_id: int,
        amount: float,
        currency: str = "usdt",
        note: str = ""
    ) -> dict:
        """內部轉帳"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v2/ai/wallet/transfer",
                headers=self._get_headers(from_user_id),
                json={
                    "to_user_id": to_user_id,
                    "currency": currency,
                    "amount": amount,
                    "note": note
                }
            )
            response.raise_for_status()
            return response.json()


# 使用範例
async def main():
    client = LuckyRedAIClient(
        api_key="your-secret-api-key",
        base_url="https://your-api.com"
    )
    
    # 查詢餘額
    balance = await client.get_balance(telegram_user_id=123456789)
    print(f"餘額: {balance}")
    
    # 發送紅包
    packet = await client.send_packet(
        telegram_user_id=123456789,
        total_amount=10.0,
        total_count=5,
        message="AI 送你紅包！"
    )
    print(f"紅包已發送: {packet['data']['packet_id']}")
    
    # 領取紅包
    claim = await client.claim_packet(
        telegram_user_id=987654321,
        packet_uuid=packet['data']['packet_id']
    )
    print(f"領取結果: {claim['data']['message']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## 文件結構

```
c:\hbgm001\
├── api\
│   └── routers\
│       └── ai_api.py              # AI 對接 API 實現
├── shared\
│   └── config\
│       └── settings.py            # 添加了 AI_API_KEY 配置
└── docs\
    └── architecture\
        ├── 現有系統分析與AI對接方案.md  # 完整分析文檔
        └── AI對接配置說明.md           # 本文件
```
