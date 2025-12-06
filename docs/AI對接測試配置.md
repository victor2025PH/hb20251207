# 🔧 AI 對接測試配置

**回覆給：** AI 聊天控制後台開發者  
**日期：** 2025-12-02

---

## ✅ 配置信息回覆

### 1️⃣ 測試環境 API 地址

| 環境 | 地址 | 狀態 |
|------|------|------|
| **本地測試** | `http://localhost:8080` | 需要本地啟動 |
| **生產服務器** | `https://api.usdt2026.cc` 或 `http://165.154.254.99:8080` | ✅ 運行中 |

**建議：** 直接使用生產服務器進行測試，地址為：
```
http://165.154.254.99:8080
```

### 2️⃣ API Key

**測試階段配置：** 開發模式已開啟，可使用任意 API Key

```python
# 測試環境可用任意 key
API_KEY = "ai-chat-system-test-key"
```

**生產環境：** 待測試完成後會提供正式 API Key

### 3️⃣ 測試用戶配置

| 用戶 | Telegram ID | 初始餘額 | 用途 |
|------|-------------|----------|------|
| 真實用戶 | `5433982810` | 100 USDT | 用戶端測試 |
| AI 帳號 1 | `1000000001` | 50 USDT | AI 陪玩 |
| AI 帳號 2 | `1000000002` | 50 USDT | AI 陪玩 |
| AI 帳號 3 | `1000000003` | 50 USDT | AI 陪玩 |
| AI 帳號 4 | `1000000004` | 50 USDT | AI 陪玩 |
| AI 帳號 5 | `1000000005` | 50 USDT | AI 陪玩 |

**⚠️ 重要：** 
- 我需要您提供實際的 AI 帳號 Telegram ID
- 上面的 `1000000001` - `1000000005` 是示例 ID
- 請告訴我您的 AI Worker 實際使用的 Telegram ID

### 4️⃣ AI 帳號批量註冊

**方式 1：通過 API 自動創建**

當 AI 首次調用任何 API 時，如果用戶不存在會返回 404。
您需要讓 AI 帳號先在 Telegram Bot 中發送 `/start` 完成註冊。

**方式 2：直接數據庫創建（推薦）**

我可以直接在數據庫中創建 AI 帳號。請提供以下信息：

```json
{
  "ai_accounts": [
    {"tg_id": 實際ID1, "username": "ai_player_1"},
    {"tg_id": 實際ID2, "username": "ai_player_2"},
    ...
  ]
}
```

**方式 3：運行設置腳本**

我已創建腳本，只需修改 AI 帳號 ID 即可：

```bash
# 在服務器上運行
cd /opt/luckyred
python scripts/setup_ai_test_accounts.py
```

---

## 🧪 測試環境完整配置

```python
from lucky_red_ai_sdk import LuckyRedAIClient

# 初始化客戶端
client = LuckyRedAIClient(
    api_key="ai-chat-system-test-key",  # 測試環境可用任意 key
    base_url="http://165.154.254.99:8080",  # 生產服務器
    ai_system_id="ai-chat-backend"
)

# 測試用戶 ID
TEST_USER_ID = 5433982810

# AI 帳號 ID（請替換為實際 ID）
AI_ACCOUNT_IDS = [
    1000000001,
    1000000002,
    1000000003,
    1000000004,
    1000000005,
]
```

---

## 🔄 測試流程

### 測試 1：用戶發紅包 → AI 搶

```python
# 1. 用戶發紅包
result = client.send_packet(
    telegram_user_id=5433982810,  # 用戶
    total_amount=10.0,
    total_count=3,
    message="測試紅包"
)
packet_id = result.data['packet_id']
print(f"紅包已創建: {packet_id}")

# 2. AI 帳號搶紅包
for ai_id in [1000000001, 1000000002, 1000000003]:
    result = client.claim_packet(
        telegram_user_id=ai_id,
        packet_uuid=packet_id
    )
    print(f"AI {ai_id} 搶到: {result.data['claimed_amount']}")
```

### 測試 2：AI 發紅包 → 用戶搶

```python
# 1. AI 發紅包
result = client.send_packet(
    telegram_user_id=1000000001,  # AI 帳號
    total_amount=5.0,
    total_count=2,
    message="AI 紅包"
)
packet_id = result.data['packet_id']

# 2. 用戶搶紅包
result = client.claim_packet(
    telegram_user_id=5433982810,  # 用戶
    packet_uuid=packet_id
)
print(f"用戶搶到: {result.data['claimed_amount']}")
```

### 測試 3：炸彈紅包

```python
# 發送炸彈紅包（10份單雷，炸彈數字7）
result = client.send_bomb_packet(
    telegram_user_id=5433982810,
    total_amount=10.0,
    total_count=10,  # 單雷必須是10份
    bomb_number=7,   # 尾數是7踩雷
    message="💣 炸彈紅包"
)
packet_id = result.data['packet_id']

# AI 搶紅包（可能踩雷）
result = client.claim_packet(
    telegram_user_id=1000000001,
    packet_uuid=packet_id
)

if result.data['is_bomb']:
    print(f"💣 踩雷！賠付: {result.data['penalty_amount']}")
else:
    print(f"安全！獲得: {result.data['claimed_amount']}")
```

### 測試 4：多 AI 同時搶（並發測試）

```python
import asyncio

async def test_concurrent_claim():
    packet_id = "xxx"  # 先創建一個紅包
    
    # 並發搶紅包
    tasks = []
    for ai_id in AI_ACCOUNT_IDS:
        task = client.async_claim_packet(
            telegram_user_id=ai_id,
            packet_uuid=packet_id
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"AI {AI_ACCOUNT_IDS[i]} 錯誤: {result}")
        else:
            print(f"AI {AI_ACCOUNT_IDS[i]} 結果: {result.data}")

asyncio.run(test_concurrent_claim())
```

---

## ❓ 需要您確認的信息

1. **AI 帳號的實際 Telegram ID**
   - 請提供您 Worker 節點使用的 AI Telegram 帳號 ID
   - 我會為這些帳號創建用戶並充值

2. **AI 帳號數量**
   - 您計劃使用多少個 AI 帳號？
   - 每個帳號需要多少初始餘額？

3. **連接測試**
   - 請先運行以下命令確認 API 連通：
   ```bash
   curl http://165.154.254.99:8080/api/v2/ai/status
   ```

---

## 📞 下一步

1. **您回覆** AI 帳號的實際 Telegram ID 列表
2. **我執行** 帳號創建和充值
3. **您開始** 對接測試
4. **雙方確認** 測試結果

請提供 AI 帳號信息，我會立即配置！
