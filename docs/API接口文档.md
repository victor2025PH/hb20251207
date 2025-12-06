# 📡 Lucky Red API 接口文档

## 🌐 基础信息

- **Base URL**: `https://api.usdt2026.cc` (生产环境)
- **API Version**: v1
- **认证方式**: 
  - Telegram: `X-Telegram-Init-Data` Header
  - Web: JWT Token (Bearer)

---

## 🔐 认证

### Telegram 认证

```http
X-Telegram-Init-Data: <telegram_init_data>
```

### Web JWT 认证

```http
Authorization: Bearer <jwt_token>
```

---

## 📋 API 端点

### 健康检查

#### GET /health

基础健康检查

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-06T12:00:00",
  "service": "luckyred-api",
  "version": "1.0.0"
}
```

#### GET /health/detailed

详细健康检查（包括数据库和 Redis）

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-06T12:00:00",
  "service": "luckyred-api",
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful"
    }
  }
}
```

#### GET /health/metrics

获取系统指标

**响应**:
```json
{
  "timestamp": "2025-12-06T12:00:00",
  "service": "luckyred-api",
  "version": "1.0.0",
  "database": {
    "users": 1000,
    "red_packets": 5000
  },
  "redis": {
    "connected_clients": 10,
    "used_memory": "50M",
    "keyspace": {}
  }
}
```

---

### 用户相关

#### GET /api/v1/users/me

获取当前用户信息

**认证**: 必需

**响应**:
```json
{
  "id": 1,
  "tg_id": 123456789,
  "username": "user123",
  "balance_usdt": "100.00",
  "balance_ton": "50.00",
  "balance_stars": "1000",
  "energy_balance": 100
}
```

#### GET /api/v1/users/me/referral/stats

获取推荐统计

**认证**: 必需

**响应**:
```json
{
  "tier1_count": 10,
  "tier2_count": 50,
  "tier1_rewards": "100.00",
  "tier2_rewards": "50.00",
  "next_milestone": {
    "count": 20,
    "reward": "200.00"
  }
}
```

#### GET /api/v1/users/me/referral/tree

获取推荐树

**认证**: 必需

**响应**:
```json
{
  "user_id": 1,
  "username": "user123",
  "tier1": [
    {
      "user_id": 2,
      "username": "user456",
      "tier1_count": 5,
      "tier2_count": 10,
      "tier1_rewards": "50.00",
      "tier2_rewards": "25.00"
    }
  ]
}
```

---

### 红包相关

#### GET /api/v1/redpackets

获取红包列表

**查询参数**:
- `page`: 页码（默认: 1）
- `limit`: 每页数量（默认: 20）
- `status`: 状态（active, completed, expired）

**响应**:
```json
{
  "items": [
    {
      "id": "uuid-123",
      "sender_name": "用户A",
      "sender_id": 1,
      "message": "恭喜发财",
      "amount": "100.00",
      "currency": "usdt",
      "quantity": 10,
      "remaining": 5,
      "status": "active",
      "created_at": "2025-12-06T12:00:00"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

#### POST /api/v1/redpackets

发送红包

**认证**: 必需

**请求体**:
```json
{
  "amount": "100.00",
  "currency": "usdt",
  "quantity": 10,
  "type": "random",
  "message": "恭喜发财",
  "chat_id": 123456789,
  "send_to_public": false
}
```

**响应**:
```json
{
  "id": "uuid-123",
  "status": "active",
  "message": "红包发送成功"
}
```

#### POST /api/v1/redpackets/{packet_id}/claim

领取红包

**认证**: 必需

**响应**:
```json
{
  "amount": "10.00",
  "currency": "usdt",
  "message": "领取成功"
}
```

---

### 钱包相关

#### GET /api/v1/wallet/balance

获取余额

**认证**: 必需

**响应**:
```json
{
  "usdt": "100.00",
  "ton": "50.00",
  "stars": "1000",
  "points": 100
}
```

#### GET /api/v1/wallet/transactions

获取交易记录

**认证**: 必需

**查询参数**:
- `limit`: 数量（默认: 50）

**响应**:
```json
{
  "items": [
    {
      "id": 1,
      "type": "deposit",
      "amount": "100.00",
      "currency": "usdt",
      "status": "completed",
      "created_at": "2025-12-06T12:00:00"
    }
  ]
}
```

#### POST /api/v1/wallet/deposit

创建充值订单

**认证**: 必需

**请求体**:
```json
{
  "amount": 100.00,
  "currency": "usdt"
}
```

**响应**:
```json
{
  "order_id": "order-123",
  "payment_url": "https://payment.example.com/pay/order-123",
  "status": "pending"
}
```

#### POST /api/v1/wallet/withdraw

创建提现订单

**认证**: 必需

**请求体**:
```json
{
  "amount": 100.00,
  "currency": "usdt",
  "address": "0x..."
}
```

**响应**:
```json
{
  "order_id": "order-123",
  "status": "pending",
  "message": "提现申请已提交"
}
```

---

### 签到相关

#### POST /api/v1/checkin

每日签到

**认证**: 必需

**响应**:
```json
{
  "reward": 10,
  "streak": 5,
  "message": "签到成功"
}
```

#### GET /api/v1/checkin/status

获取签到状态

**认证**: 必需

**响应**:
```json
{
  "checked_in": true,
  "streak": 5,
  "last_checkin": "2025-12-06T00:00:00"
}
```

---

### 任务相关

#### GET /api/v1/tasks/status

获取任务状态

**认证**: 必需

**响应**:
```json
{
  "daily_tasks": [
    {
      "id": "checkin",
      "name": "每日签到",
      "completed": true,
      "claimed": false,
      "reward": 10
    }
  ],
  "achievement_tasks": [
    {
      "id": "invite_master",
      "name": "邀请大师",
      "completed": false,
      "progress": 5,
      "target": 10,
      "reward": 100
    }
  ]
}
```

#### POST /api/v1/tasks/{task_id}/claim

领取任务奖励

**认证**: 必需

**响应**:
```json
{
  "reward": 10,
  "message": "奖励领取成功"
}
```

---

### 兑换相关

#### GET /api/exchange/rate

获取汇率

**查询参数**:
- `from_currency`: 源币种（usdt, ton, points）
- `to_currency`: 目标币种（usdt, ton, points）

**响应**:
```json
{
  "from_currency": "usdt",
  "to_currency": "ton",
  "rate": "2.5",
  "timestamp": "2025-12-06T12:00:00"
}
```

#### POST /api/exchange

兑换币种

**认证**: 必需

**请求体**:
```json
{
  "from_currency": "usdt",
  "to_currency": "ton",
  "amount": "100.00"
}
```

**响应**:
```json
{
  "from_amount": "100.00",
  "to_amount": "250.00",
  "rate": "2.5",
  "message": "兑换成功"
}
```

---

## 🔄 Webhook

### 支付 Webhook

#### POST /api/v1/webhook/alchemy-pay

Alchemy Pay 支付回调

**请求体**:
```json
{
  "order_id": "order-123",
  "status": "paid",
  "amount": "100.00",
  "currency": "usdt"
}
```

---

## ⚠️ 错误响应

所有错误响应格式：

```json
{
  "detail": "错误描述"
}
```

**HTTP 状态码**:
- `200`: 成功
- `400`: 请求错误
- `401`: 未认证
- `403`: 无权限
- `404`: 资源不存在
- `500`: 服务器错误

---

## 📝 注意事项

1. **速率限制**: API 有速率限制，请合理使用
2. **时间格式**: 所有时间使用 ISO 8601 格式（UTC）
3. **金额格式**: 金额使用字符串格式，保留小数点后2位
4. **认证**: 大部分端点需要认证，请确保提供正确的认证信息

---

## 🔗 相关链接

- [健康检查端点](#健康检查)
- [用户端点](#用户相关)
- [红包端点](#红包相关)
- [钱包端点](#钱包相关)

