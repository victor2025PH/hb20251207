# 🚀 Lucky Red 優化路線圖

## 📋 目錄
1. [配置管理優化](#1-配置管理優化)
2. [錯誤處理增強](#2-錯誤處理增強)
3. [性能優化](#3-性能優化)
4. [代碼質量提升](#4-代碼質量提升)
5. [用戶體驗優化](#5-用戶體驗優化)
6. [安全性增強](#6-安全性增強)
7. [監控和日誌](#7-監控和日誌)
8. [測試覆蓋](#8-測試覆蓋)

---

## 1. 配置管理優化

### 🔴 高優先級
**問題：** 硬編碼的 API URL 在多處使用
- `bot/handlers/packets.py`: `http://localhost:8080/api/redpackets/create`
- `bot/handlers/wallet.py`: `http://localhost:8080/api`

**解決方案：**
```python
# shared/config/settings.py
class Settings(BaseSettings):
    # 添加 API 配置
    API_BASE_URL: str = "http://localhost:8080"
    
    @property
    def api_url(self) -> str:
        """獲取完整的 API URL"""
        return f"{self.API_BASE_URL}/api"
```

**優化點：**
- ✅ 統一配置管理
- ✅ 支持環境變量覆蓋
- ✅ 生產環境和開發環境分離

---

## 2. 錯誤處理增強

### 🔴 高優先級
**問題：** 錯誤處理不統一，缺少詳細日誌

**優化方向：**

#### 2.1 統一錯誤處理裝飾器
```python
# bot/utils/decorators.py
from functools import wraps
from loguru import logger
from telegram import Update

def handle_errors(func):
    """統一錯誤處理裝飾器"""
    @wraps(func)
    async def wrapper(update: Update, context, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            await update.callback_query.answer(
                "發生錯誤，請稍後再試",
                show_alert=True
            )
    return wrapper
```

#### 2.2 API 調用錯誤處理
```python
# bot/utils/api_client.py
class APIClient:
    """統一的 API 客戶端"""
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def post(self, endpoint: str, data: dict, headers: dict = None):
        """統一的 POST 請求處理"""
        try:
            response = await self.client.post(
                f"{self.base_url}{endpoint}",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise
```

**優化點：**
- ✅ 統一的錯誤處理邏輯
- ✅ 詳細的錯誤日誌
- ✅ 用戶友好的錯誤提示

---

## 3. 性能優化

### 🟡 中優先級

#### 3.1 數據庫查詢優化

**問題：** 多次查詢用戶數據，缺少緩存

**優化方案：**

```python
# bot/utils/cache.py
from functools import lru_cache
from typing import Optional
from shared.database.models import User

class UserCache:
    """用戶數據緩存"""
    _cache = {}
    _cache_ttl = 300  # 5分鐘
    
    @classmethod
    def get_user(cls, tg_id: int, db) -> Optional[User]:
        """獲取用戶（帶緩存）"""
        cache_key = f"user_{tg_id}"
        cached = cls._cache.get(cache_key)
        
        if cached and (time.time() - cached['time']) < cls._cache_ttl:
            return cached['user']
        
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if user:
            cls._cache[cache_key] = {
                'user': user,
                'time': time.time()
            }
        return user
    
    @classmethod
    def invalidate(cls, tg_id: int):
        """清除緩存"""
        cache_key = f"user_{tg_id}"
        cls._cache.pop(cache_key, None)
```

#### 3.2 數據庫索引優化

**建議添加的索引：**
```python
# shared/database/models.py
class RedPacket(Base):
    # ... 現有字段 ...
    
    __table_args__ = (
        Index("ix_red_packets_status_created", "status", "created_at"),
        Index("ix_red_packets_sender_created", "sender_id", "created_at"),
        Index("ix_red_packets_chat_status", "chat_id", "status"),
    )
```

#### 3.3 批量操作優化

**問題：** 任務中心統計查詢可能較慢

**優化方案：**
```python
# 使用單一查詢替代多次查詢
async def get_user_task_stats(db_user, db):
    """一次性獲取所有任務統計"""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    
    # 使用子查詢優化
    stats = db.query(
        func.count(RedPacketClaim.id).label('today_claimed'),
        func.count(RedPacket.id).label('today_sent'),
        # ... 其他統計
    ).filter(
        # ... 條件
    ).first()
    
    return stats
```

**優化點：**
- ✅ 減少數據庫查詢次數
- ✅ 添加適當的索引
- ✅ 使用緩存減少重複查詢

---

## 4. 代碼質量提升

### 🟡 中優先級

#### 4.1 代碼重複消除

**問題：** 發紅包流程中有重複的數據提取邏輯

**優化方案：**
```python
# bot/utils/packet_helpers.py
def extract_packet_data(context, parts: list) -> dict:
    """統一的紅包數據提取"""
    return {
        'currency': parts[3] if len(parts) > 3 else "usdt",
        'packet_type': parts[4] if len(parts) > 4 else "random",
        'amount': parts[5] if len(parts) > 5 else None,
        'count': int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else None,
        'bomb_number': int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else None,
        'message': parts[8] if len(parts) > 8 and parts[8] != "default" else "恭喜發財！🧧",
    }
```

#### 4.2 類型提示完善

**優化方案：**
```python
# 為所有函數添加完整的類型提示
from typing import Optional, Dict, Any

async def show_packet_type_selection(
    query: CallbackQuery,
    db_user: User,
    currency: str
) -> None:
    """顯示紅包類型選擇"""
    ...
```

#### 4.3 常量提取

**優化方案：**
```python
# bot/constants.py
class PacketConstants:
    """紅包相關常量"""
    MAX_COUNT = 100
    MIN_AMOUNT = Decimal("0.01")
    DEFAULT_MESSAGE = "恭喜發財！🧧"
    BOMB_COUNTS = [5, 10]  # 紅包炸彈允許的數量
```

**優化點：**
- ✅ 減少代碼重複
- ✅ 提高可維護性
- ✅ 增強類型安全

---

## 5. 用戶體驗優化

### 🟡 中優先級

#### 5.1 加載狀態提示

**優化方案：**
```python
async def show_loading(query, message: str = "處理中..."):
    """顯示加載狀態"""
    await query.answer(message, cache_time=0)
    # 可以添加加載動畫或狀態標記
```

#### 5.2 輸入驗證增強

**優化方案：**
```python
# bot/utils/validators.py
def validate_amount(amount: str, currency: str, balance: Decimal) -> tuple[bool, str]:
    """驗證金額輸入"""
    try:
        amount_decimal = Decimal(amount)
        if amount_decimal <= 0:
            return False, "金額必須大於0"
        if amount_decimal > balance:
            return False, f"餘額不足，當前餘額: {float(balance):.2f}"
        return True, ""
    except (ValueError, InvalidOperation):
        return False, "金額格式錯誤"
```

#### 5.3 操作確認機制

**優化方案：**
```python
# 對於重要操作（如發送大額紅包），添加確認步驟
async def confirm_large_packet(query, amount: Decimal, threshold: Decimal = 100):
    """大額紅包確認"""
    if amount >= threshold:
        # 顯示確認對話框
        ...
```

**優化點：**
- ✅ 更好的用戶反饋
- ✅ 防止誤操作
- ✅ 提升操作流暢度

---

## 6. 安全性增強

### 🔴 高優先級

#### 6.1 輸入驗證和清理

**優化方案：**
```python
# bot/utils/security.py
import re

def sanitize_message(message: str, max_length: int = 256) -> str:
    """清理用戶輸入的消息"""
    # 移除危險字符
    message = re.sub(r'[<>]', '', message)
    # 限制長度
    return message[:max_length]

def validate_chat_id(chat_id: str) -> Optional[int]:
    """驗證群組 ID 格式"""
    try:
        id_int = int(chat_id)
        # 群組 ID 通常是負數
        if id_int < 0:
            return id_int
    except ValueError:
        pass
    return None
```

#### 6.2 權限檢查

**優化方案：**
```python
# bot/utils/permissions.py
async def check_user_permission(db_user: User, required_balance: Decimal) -> bool:
    """檢查用戶權限和餘額"""
    if db_user.is_banned:
        return False
    if db_user.balance_usdt < required_balance:
        return False
    return True
```

#### 6.3 API 請求驗證

**優化方案：**
```python
# 在 API 調用中添加更完整的驗證
def build_init_data(tg_id: int, secret: str) -> str:
    """構建完整的 Telegram initData"""
    # 使用實際的 Telegram 驗證機制
    # 而不是簡化的 user={"id": tg_id}
    ...
```

**優化點：**
- ✅ 防止注入攻擊
- ✅ 輸入驗證
- ✅ 權限控制

---

## 7. 監控和日誌

### 🟢 低優先級

#### 7.1 結構化日誌

**優化方案：**
```python
# bot/utils/logging.py
from loguru import logger
import json

def log_user_action(user_id: int, action: str, details: dict = None):
    """記錄用戶操作"""
    logger.info(
        "User action",
        extra={
            "user_id": user_id,
            "action": action,
            "details": json.dumps(details or {})
        }
    )
```

#### 7.2 性能監控

**優化方案：**
```python
# bot/utils/metrics.py
import time
from functools import wraps

def track_performance(func):
    """性能追蹤裝飾器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start
            logger.info(f"{func.__name__} took {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    return wrapper
```

**優化點：**
- ✅ 更好的問題追蹤
- ✅ 性能瓶頸識別
- ✅ 運維監控

---

## 8. 測試覆蓋

### 🟢 低優先級

#### 8.1 單元測試

**優化方案：**
```python
# tests/test_packets.py
import pytest
from bot.handlers.packets import validate_packet_data

def test_validate_packet_data():
    """測試紅包數據驗證"""
    assert validate_packet_data({"amount": "10", "count": "5"}) == True
    assert validate_packet_data({"amount": "-10", "count": "5"}) == False
```

#### 8.2 集成測試

**優化方案：**
```python
# tests/test_api_integration.py
async def test_create_packet_api():
    """測試創建紅包 API"""
    # 模擬 API 調用
    ...
```

**優化點：**
- ✅ 提高代碼可靠性
- ✅ 防止回歸問題
- ✅ 文檔化功能

---

## 📊 優先級總結

### 🔴 高優先級（立即實施）
1. **配置管理優化** - 移除硬編碼 URL
2. **錯誤處理增強** - 統一錯誤處理機制
3. **安全性增強** - 輸入驗證和權限檢查

### 🟡 中優先級（近期實施）
4. **性能優化** - 數據庫查詢和緩存
5. **代碼質量提升** - 消除重複，完善類型
6. **用戶體驗優化** - 加載狀態，輸入驗證

### 🟢 低優先級（長期規劃）
7. **監控和日誌** - 結構化日誌，性能監控
8. **測試覆蓋** - 單元測試，集成測試

---

## 🎯 實施建議

### 第一階段（1-2週）
1. 配置管理優化
2. 統一錯誤處理
3. 基礎安全性增強

### 第二階段（2-4週）
4. 性能優化（緩存、索引）
5. 代碼重構（消除重複）
6. 用戶體驗改進

### 第三階段（長期）
7. 監控系統
8. 測試覆蓋
9. 文檔完善

---

## 📝 注意事項

- 每次優化後都要充分測試
- 保持向後兼容性
- 優先處理影響用戶體驗的問題
- 定期代碼審查和重構
