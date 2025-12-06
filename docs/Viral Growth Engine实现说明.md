# 🚀 Viral Growth Engine 实现说明

## ✅ 已实现功能

### 1. Deep Linking系统

#### 功能
- ✅ 智能链接生成（红包、邀请、Magic Link）
- ✅ 平台自动检测（Telegram, WhatsApp, Facebook, X, Web）
- ✅ 自动重定向到对应平台

#### 实现文件
- `api/services/deep_link_service.py` - Deep Linking服务
- `api/routers/deep_link.py` - Deep Link路由

#### 使用示例

**生成红包链接：**
```python
from api.services.deep_link_service import DeepLinkService

links = DeepLinkService.generate_packet_link("packet-uuid-123")
# 返回：
# {
#   'telegram': 'https://t.me/bot?start=packet_packet-uuid-123',
#   'web': 'https://mini.usdt2026.cc/packets/packet-uuid-123',
#   'universal': 'https://mini.usdt2026.cc/packet/packet-uuid-123'
# }
```

**生成邀请链接：**
```python
links = DeepLinkService.generate_invite_link("REF123")
# 返回：
# {
#   'telegram': 'https://t.me/bot?start=ref_REF123',
#   'web': 'https://mini.usdt2026.cc/invite/REF123',
#   'universal': 'https://mini.usdt2026.cc/invite/REF123'
# }
```

**智能重定向：**
```
GET /api/v1/link/packet/{packet_uuid}
- 如果User-Agent包含"Telegram" → 重定向到Telegram MiniApp
- 否则 → 重定向到Web版本
```

---

### 2. Tier 1 & Tier 2推荐佣金系统

#### 功能
- ✅ Tier 1推荐奖励（10%）
- ✅ Tier 2推荐奖励（5%）
- ✅ 自动发放推荐奖励
- ✅ 推荐统计查询

#### 实现文件
- `api/services/referral_service.py` - 推荐系统服务

#### 佣金比例
- **Tier 1（直接推荐）**: 10%
- **Tier 2（二级推荐）**: 5%

#### 触发场景
推荐奖励在以下场景自动触发：
1. **充值奖励** - 用户充值法币时
2. **红包奖励** - 用户领取红包时
3. **游戏奖励** - 用户游戏获胜时（待实现）

#### 使用示例

**处理推荐奖励：**
```python
from api.services.referral_service import ReferralService

# 用户领取红包时自动触发
await ReferralService.process_referral_reward(
    db=db,
    user_id=123,
    amount=Decimal('100'),
    currency='USDT',
    reward_type='redpacket',
    metadata={'packet_id': 456}
)
```

**获取推荐统计：**
```python
stats = await ReferralService.get_referral_stats(db, user_id=123)
# 返回：
# {
#   'tier1_count': 10,
#   'tier2_count': 25,
#   'total_referrals': 35,
#   'total_reward': '150.00',
#   'reward_count': 50,
#   'tier1_reward': '100.00',
#   'tier2_reward': '50.00'
# }
```

---

## 🔗 集成点

### 1. 红包领取时触发推荐奖励
**文件**: `api/routers/redpackets.py`

在用户领取红包后，自动处理推荐奖励：
```python
# 处理推荐奖励（Tier 1 & Tier 2）
await ReferralService.process_referral_reward(
    db=db,
    user_id=claimer.id,
    amount=amount,
    currency=packet.currency.value.upper(),
    reward_type='redpacket',
    metadata={'packet_id': packet.id}
)
```

### 2. 充值成功时触发推荐奖励
**文件**: `api/routers/payment.py`

在用户充值成功后，自动处理推荐奖励：
```python
# 处理推荐奖励（Tier 1 & Tier 2）
await ReferralService.process_referral_reward(
    db=db,
    user_id=user.id,
    amount=virtual_usdt,
    currency='USDT',
    reward_type='deposit',
    metadata={'transaction_id': transaction_id}
)
```

### 3. API端点
**文件**: `api/routers/users.py`

新增推荐统计API：
```
GET /api/v1/users/me/referral/stats
```

---

## 📊 推荐树结构

### 数据结构
```
User A (referrer_id: null)
├── User B (referrer_id: A.id) - Tier 1
│   ├── User D (referrer_id: B.id) - Tier 2 (对A)
│   └── User E (referrer_id: B.id) - Tier 2 (对A)
└── User C (referrer_id: A.id) - Tier 1
    └── User F (referrer_id: C.id) - Tier 2 (对A)
```

### 奖励计算示例

**场景**: User B 领取了 100 USDT 红包

1. **Tier 1奖励**: User A 获得 10 USDT (100 * 10%)
2. **Tier 2奖励**: User A 的推荐人（如果有）获得 5 USDT (100 * 5%)

---

## 🎯 下一步

### 待实现功能
1. **游戏奖励触发** - 在游戏获胜时触发推荐奖励
2. **推荐树可视化** - 前端显示推荐树结构
3. **推荐排行榜** - 显示推荐人数和奖励排行榜
4. **推荐活动** - 限时推荐活动（如双倍奖励）

### 优化建议
1. **批量处理** - 对于大量推荐奖励，使用队列异步处理
2. **缓存优化** - 缓存推荐统计数据
3. **防刷机制** - 防止推荐奖励被恶意刷取

---

## 📝 API文档

### Deep Link API

#### 红包链接重定向
```
GET /api/v1/link/packet/{packet_uuid}
```
根据User-Agent自动重定向到Telegram MiniApp或Web版本

#### 邀请链接重定向
```
GET /api/v1/link/invite/{referral_code}
```
根据User-Agent自动重定向到Telegram MiniApp或Web版本

#### Magic Link重定向
```
GET /api/v1/link/magic-link?token={token}
```
重定向到Web版本的Magic Link登录页面

### 推荐系统API

#### 获取推荐统计
```
GET /api/v1/users/me/referral/stats
```

**响应示例：**
```json
{
  "tier1_count": 10,
  "tier2_count": 25,
  "total_referrals": 35,
  "total_reward": "150.00",
  "reward_count": 50,
  "tier1_reward": "100.00",
  "tier2_reward": "50.00"
}
```

---

## ✅ 测试建议

1. **Deep Link测试**
   - 在不同平台（Telegram, WhatsApp, Web）打开链接
   - 验证重定向是否正确

2. **推荐奖励测试**
   - 创建推荐关系（User A -> User B -> User C）
   - User C 领取红包，验证 User A 和 User B 是否收到奖励
   - 验证奖励金额是否正确（Tier 1: 10%, Tier 2: 5%）

3. **推荐统计测试**
   - 查询推荐统计
   - 验证数据准确性

---

## 🎉 总结

**Viral Growth Engine核心功能已实现！**

- ✅ Deep Linking系统 - 完成
- ✅ Tier 1 & Tier 2推荐佣金 - 完成
- ✅ 自动奖励发放 - 完成
- ✅ 推荐统计查询 - 完成

**系统现在具备了完整的病毒式增长引擎！** 🚀

