# Lucky Red - 功能对齐分析文档

## 概述

本文档详细分析了**红包游戏（Telegram MiniApp）**和**后台管理系统（Admin Dashboard）**之间的功能对齐情况，帮助其他AI理解系统架构和数据流。

---

## 系统架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                     Telegram MiniApp                         │
│  (前端: frontend/src/)                                        │
│  - 钱包页面 (WalletPage)                                      │
│  - 红包页面 (PacketsPage)                                    │
│  - 发送红包 (SendRedPacket)                                  │
│  - 任务页面 (TasksPage)                                      │
│  - 个人中心 (ProfilePage)                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ API 请求 (JWT/Telegram initData)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                            │
│  (后端: api/routers/)                                        │
│  - /api/v1/users/*        (用户相关)                         │
│  - /api/v1/redpackets/*  (红包相关)                         │
│  - /api/v1/wallet/*      (钱包相关)                          │
│  - /api/v1/tasks/*       (任务相关)                          │
│  - /api/v1/admin/*       (管理后台)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ 数据库操作
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              PostgreSQL + Redis                              │
│  - Users, RedPackets, Transactions, Ledger                   │
│  - Redis: 高并发抢红包缓存                                   │
└─────────────────────────────────────────────────────────────┘
                       │
                       │ 管理操作
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Admin Dashboard                                 │
│  (前端: admin/frontend/src/)                                 │
│  - 用户管理 (UserManagement)                                │
│  - 红包管理 (RedPacketManagement)                           │
│  - 交易管理 (TransactionManagement)                          │
│  - 邀请管理 (InviteManagement)                              │
│  - 仪表盘 (Dashboard)                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 功能模块对齐分析

### 1. 用户认证与身份管理

#### 1.1 游戏端（MiniApp）

**前端组件**: 
- `frontend/src/utils/auth/useAuth.ts` - 认证Hook
- `frontend/src/utils/auth/AuthGuard.tsx` - 路由守卫
- `frontend/src/components/WebLoginScreen.tsx` - 登录页面

**支持的登录方式**:
- ✅ Telegram MiniApp 自动登录（initData）
- ✅ Google OAuth 登录
- ✅ JWT Token 登录（Web环境）

**API端点**:
- `POST /api/v1/auth/web/google` - Google登录
- `GET /api/v1/users/me` - 获取当前用户信息

#### 1.2 后台管理端

**前端组件**:
- `admin/frontend/src/pages/Login.tsx` - 管理员登录

**API端点**:
- `POST /api/v1/admin/auth/login` - 管理员登录
- `GET /api/v1/admin/auth/me` - 获取当前管理员信息

**对齐状态**: ✅ **完全对齐**
- 游戏端使用 Telegram/Google 认证
- 后台使用独立的用户名/密码认证
- 两者共享同一个 User 表，但权限分离

---

### 2. 用户管理

#### 2.1 游戏端功能

**用户信息显示**:
- 用户资料（ProfilePage）
- 余额显示（WalletPage）
- 等级和XP（WalletPage）

**API端点**:
- `GET /api/v1/users/me` - 获取当前用户信息
- `GET /api/v1/users/me/balance` - 获取余额
- `GET /api/v1/users/me/referral/stats` - 推荐统计

#### 2.2 后台管理功能

**管理功能**:
- 用户列表（UserManagement.tsx）
- 用户详情（UserDetail.tsx）
- 余额调整（admin_users.py）
- 批量操作（admin_users.py）

**API端点**:
- `GET /api/v1/admin/users/list` - 用户列表
- `GET /api/v1/admin/users/{id}/detail` - 用户详情
- `POST /api/v1/admin/users/adjust-balance` - 调整余额
- `POST /api/v1/admin/users/batch-operation` - 批量操作

**对齐状态**: ✅ **完全对齐**
- 游戏端：用户查看自己的信息
- 后台：管理员查看和管理所有用户
- 数据源：共享 `users` 表

---

### 3. 红包系统

#### 3.1 游戏端功能

**红包功能**:
- 发送红包（SendRedPacket.tsx）
- 查看红包列表（PacketsPage.tsx）
- 抢红包（PacketsPage.tsx）
- 红包详情

**API端点**:
- `POST /api/v1/redpackets/create` - 创建红包
- `GET /api/v1/redpackets/list` - 红包列表
- `POST /api/v1/redpackets/{uuid}/claim` - 抢红包
- `GET /api/v1/redpackets/recommended` - 推荐红包

**红包类型**:
- 随机红包（random）
- 固定金额红包（fixed/equal）
- 专属红包（exclusive）

#### 3.2 后台管理功能

**管理功能**:
- 红包列表（RedPacketManagement.tsx）
- 红包详情（RedPacketDetail.tsx）
- 手动退款（admin_redpackets.py）
- 延长过期时间（admin_redpackets.py）
- 完成红包（admin_redpackets.py）
- 删除红包（admin_redpackets.py）
- **新增**: 红包雨调度（Phase 3）

**API端点**:
- `GET /api/v1/admin/redpackets/list` - 红包列表
- `GET /api/v1/admin/redpackets/{id}` - 红包详情
- `POST /api/v1/admin/redpackets/{id}/refund` - 退款
- `POST /api/v1/admin/redpackets/{id}/extend` - 延长
- `POST /api/v1/admin/redpackets/{id}/complete` - 完成
- `DELETE /api/v1/admin/redpackets/{id}` - 删除
- `POST /api/v1/admin/redpackets/schedule-rain` - 调度红包雨（新增）

**对齐状态**: ✅ **完全对齐 + 增强**
- 游戏端：用户创建和抢红包
- 后台：管理员监控、管理和控制红包
- 数据源：共享 `red_packets` 和 `red_packet_claims` 表
- **新增功能**: 后台可以调度红包雨（游戏端暂不支持）

---

### 4. 钱包与交易

#### 4.1 游戏端功能

**钱包功能**:
- 余额显示（WalletPage.tsx）
- 充值（Recharge.tsx）
- 提现（Withdraw.tsx）
- 交易记录（WalletPage.tsx）
- 兑换（ExchangePage.tsx）

**API端点**:
- `GET /api/v1/wallet/balance` - 获取余额
- `GET /api/v1/wallet/transactions` - 交易记录
- `POST /api/v1/wallet/deposit` - 充值
- `POST /api/v1/wallet/withdraw` - 提现
- `POST /api/exchange/exchange` - 兑换

**余额类型**:
- USDT（真实余额）
- TON（真实余额）
- Stars（游戏币）
- Points（积分）

#### 4.2 后台管理功能

**管理功能**:
- 交易列表（TransactionManagement.tsx）
- 交易详情（TransactionDetail.tsx）
- 交易统计（TransactionManagement.tsx）
- **新增**: Real vs Bonus 余额显示（Phase 2）

**API端点**:
- `GET /api/v1/admin/transactions/list` - 交易列表
- `GET /api/v1/admin/transactions/{id}` - 交易详情
- `GET /api/v1/admin/transactions/stats/overview` - 统计概览
- `GET /api/v1/admin/transactions/stats/trend` - 趋势分析

**对齐状态**: ✅ **完全对齐 + 增强**
- 游戏端：用户查看自己的余额和交易
- 后台：管理员查看所有用户的交易
- 数据源：共享 `transactions` 表
- **新增功能**: 后台显示 Real vs Bonus 余额分类（游戏端暂不支持）

---

### 5. 推荐系统

#### 5.1 游戏端功能

**推荐功能**:
- 邀请码显示（ProfilePage.tsx）
- 推荐统计（ProfilePage.tsx）
- 推荐关系树（ProfilePage.tsx）

**API端点**:
- `GET /api/v1/users/me/referral/stats` - 推荐统计
- `GET /api/v1/users/me/referral/tree` - 推荐关系树

#### 5.2 后台管理功能

**管理功能**:
- 邀请关系列表（InviteManagement.tsx）
- 邀请关系树（InviteManagement.tsx）
- 邀请统计（InviteManagement.tsx）
- **新增**: 佣金配置管理（Phase 3）

**API端点**:
- `GET /api/v1/admin/invite/list` - 邀请关系列表
- `GET /api/v1/admin/invite/tree/{user_id}` - 邀请关系树
- `GET /api/v1/admin/invite/stats` - 邀请统计
- `GET /api/v1/admin/invite/trend` - 趋势分析
- `GET /api/v1/admin/invite/commission-config` - 获取佣金配置（新增）
- `POST /api/v1/admin/invite/commission-config` - 更新佣金配置（新增）

**对齐状态**: ✅ **完全对齐 + 增强**
- 游戏端：用户查看自己的推荐数据
- 后台：管理员查看所有用户的推荐关系
- 数据源：共享 `users` 表（invited_by, invite_code, invite_count）
- **新增功能**: 后台可以配置3层推荐佣金（游戏端只显示，不配置）

---

### 6. 任务系统

#### 6.1 游戏端功能

**任务功能**:
- 任务列表（TasksPage.tsx）
- 任务完成（TasksPage.tsx）
- 任务奖励领取（TasksPage.tsx）

**API端点**:
- `GET /api/v1/tasks/status` - 任务状态
- `POST /api/v1/tasks/{task_type}/claim` - 领取奖励
- `POST /api/v1/tasks/{task_type}/complete` - 完成任务

**任务类型**:
- 签到任务（checkin）
- 邀请任务（invite）
- 分享任务（share）
- 抢红包任务（claim）
- 发红包任务（send）

#### 6.2 后台管理功能

**管理功能**:
- ❌ **暂未实现**（未来可添加任务管理功能）

**对齐状态**: ⚠️ **部分对齐**
- 游戏端：完整的任务系统
- 后台：暂无任务管理功能
- **建议**: 添加任务配置、任务统计等功能

---

### 7. 签到系统

#### 7.1 游戏端功能

**签到功能**:
- 每日签到（EarnPage.tsx 或 WalletPage.tsx）
- 连续签到奖励

**API端点**:
- `POST /api/v1/checkin` - 执行签到
- `GET /api/v1/checkin/status` - 签到状态

#### 7.2 后台管理功能

**管理功能**:
- 签到记录列表（CheckinManagement.tsx）
- 签到统计（CheckinManagement.tsx）

**API端点**:
- `GET /api/v1/admin/checkin/list` - 签到记录列表
- `GET /api/v1/admin/checkin/stats` - 签到统计
- `GET /api/v1/admin/checkin/trend` - 趋势分析

**对齐状态**: ✅ **完全对齐**
- 游戏端：用户执行签到
- 后台：管理员查看签到记录和统计
- 数据源：共享 `checkin_records` 表

---

### 8. 数据统计与分析

#### 8.1 游戏端功能

**统计功能**:
- 个人统计（ProfilePage.tsx）
- 推荐统计（ProfilePage.tsx）

#### 8.2 后台管理功能

**统计功能**:
- 仪表盘（Dashboard.tsx）
  - 用户统计
  - 红包统计
  - 交易统计
  - 趋势图表
- 报表管理（ReportManagement.tsx）
  - 生成报表
  - 导出Excel

**API端点**:
- `GET /api/v1/admin/dashboard/stats` - 仪表盘统计
- `GET /api/v1/admin/dashboard/trends` - 趋势数据
- `GET /api/v1/admin/dashboard/distribution` - 分布数据
- `POST /api/v1/admin/reports/generate` - 生成报表
- `GET /api/v1/admin/reports/{id}/download` - 下载报表

**对齐状态**: ✅ **完全对齐**
- 游戏端：个人数据统计
- 后台：全局数据统计和分析
- 数据源：共享所有业务表

---

## 数据流分析

### 红包创建流程

```
游戏端 (SendRedPacket)
  ↓ POST /api/v1/redpackets/create
后端 API (redpackets.py)
  ↓ 验证余额 (LedgerService)
  ↓ 创建红包记录 (RedPacket)
  ↓ 初始化 Redis (RedisClaimService)
  ↓ 发送到 Telegram 群组
  ↓ 返回红包信息
游戏端 (显示红包已创建)
  ↓
后台管理 (RedPacketManagement)
  ↓ GET /api/v1/admin/redpackets/list
后端 API (admin_redpackets.py)
  ↓ 查询红包列表
  ↓ 返回给后台
后台管理 (显示红包列表)
```

### 红包退款流程

```
后台管理 (RedPacketManagement)
  ↓ POST /api/v1/admin/redpackets/{id}/refund
后端 API (admin_redpackets.py)
  ↓ 验证红包状态
  ↓ 计算剩余金额
  ↓ 使用 LedgerService 退款
  ↓ 更新红包状态
  ↓ 清理 Redis
  ↓ 返回退款结果
后台管理 (显示退款成功)
  ↓
游戏端 (PacketsPage)
  ↓ GET /api/v1/redpackets/list
后端 API (redpackets.py)
  ↓ 查询红包列表（状态已更新为 REFUNDED）
  ↓ 返回给游戏端
游戏端 (显示红包已退款)
```

### 推荐佣金计算流程

```
游戏端 (用户完成充值/发红包)
  ↓ 触发推荐奖励计算
后端 API (推荐服务)
  ↓ 查找推荐关系（3层）
  ↓ 读取佣金配置 (SystemConfig)
  ↓ 计算佣金（Tier1, Tier2, Tier3）
  ↓ 使用 LedgerService 发放奖励
  ↓ 更新用户 invite_earnings
  ↓
后台管理 (InviteManagement)
  ↓ GET /api/v1/admin/invite/list
后端 API (admin_invite.py)
  ↓ 查询推荐关系和收益
  ↓ 返回给后台
后台管理 (显示推荐数据)
```

---

## 数据库表对齐

### 核心业务表

| 表名 | 游戏端使用 | 后台管理使用 | 对齐状态 |
|------|-----------|-------------|---------|
| `users` | ✅ 读取/更新自己的数据 | ✅ 读取/更新所有用户 | ✅ 完全对齐 |
| `red_packets` | ✅ 创建/读取 | ✅ 读取/管理 | ✅ 完全对齐 |
| `red_packet_claims` | ✅ 创建（抢红包） | ✅ 读取 | ✅ 完全对齐 |
| `transactions` | ✅ 读取自己的交易 | ✅ 读取所有交易 | ✅ 完全对齐 |
| `ledger_entries` | ✅ 间接使用（余额） | ✅ 间接使用（余额分类） | ✅ 完全对齐 |
| `checkin_records` | ✅ 创建（签到） | ✅ 读取 | ✅ 完全对齐 |
| `tasks` | ✅ 读取/更新 | ❌ 暂未使用 | ⚠️ 部分对齐 |
| `system_configs` | ✅ 读取配置 | ✅ 读取/更新配置 | ✅ 完全对齐 |

### 管理专用表

| 表名 | 用途 | 对齐状态 |
|------|------|---------|
| `admin_users` | 管理员账户 | ✅ 后台专用 |
| `scheduled_redpacket_rains` | 红包雨调度 | ✅ 后台专用（Phase 3新增） |
| `telegram_groups` | Telegram群组管理 | ✅ 后台专用 |
| `telegram_messages` | 消息记录 | ✅ 后台专用 |

---

## API端点对齐

### 游戏端API（/api/v1/）

| 端点 | 方法 | 游戏端使用 | 后台管理使用 | 对齐状态 |
|------|------|-----------|-------------|---------|
| `/users/me` | GET | ✅ | ❌ | ✅ 游戏端专用 |
| `/users/me/balance` | GET | ✅ | ❌ | ✅ 游戏端专用 |
| `/redpackets/create` | POST | ✅ | ❌ | ✅ 游戏端专用 |
| `/redpackets/list` | GET | ✅ | ❌ | ✅ 游戏端专用 |
| `/redpackets/{uuid}/claim` | POST | ✅ | ❌ | ✅ 游戏端专用 |
| `/wallet/balance` | GET | ✅ | ❌ | ✅ 游戏端专用 |
| `/wallet/deposit` | POST | ✅ | ❌ | ✅ 游戏端专用 |
| `/wallet/withdraw` | POST | ✅ | ❌ | ✅ 游戏端专用 |
| `/checkin` | POST | ✅ | ❌ | ✅ 游戏端专用 |
| `/tasks/status` | GET | ✅ | ❌ | ✅ 游戏端专用 |

### 后台管理API（/api/v1/admin/）

| 端点 | 方法 | 游戏端使用 | 后台管理使用 | 对齐状态 |
|------|------|-----------|-------------|---------|
| `/users/list` | GET | ❌ | ✅ | ✅ 后台专用 |
| `/users/{id}/detail` | GET | ❌ | ✅ | ✅ 后台专用 |
| `/users/adjust-balance` | POST | ❌ | ✅ | ✅ 后台专用 |
| `/redpackets/list` | GET | ❌ | ✅ | ✅ 后台专用 |
| `/redpackets/{id}/refund` | POST | ❌ | ✅ | ✅ 后台专用 |
| `/redpackets/schedule-rain` | POST | ❌ | ✅ | ✅ 后台专用（Phase 3） |
| `/transactions/list` | GET | ❌ | ✅ | ✅ 后台专用 |
| `/invite/list` | GET | ❌ | ✅ | ✅ 后台专用 |
| `/invite/commission-config` | GET/POST | ❌ | ✅ | ✅ 后台专用（Phase 3） |
| `/checkin/list` | GET | ❌ | ✅ | ✅ 后台专用 |
| `/dashboard/stats` | GET | ❌ | ✅ | ✅ 后台专用 |

---

## 功能缺失分析

### 游戏端缺失的功能

1. ❌ **红包雨调度** - 只能由后台管理员调度
2. ❌ **推荐佣金配置** - 只能由后台管理员配置
3. ❌ **余额分类显示** - 游戏端只显示总余额，不区分 Real/Bonus

### 后台管理缺失的功能

1. ❌ **任务管理** - 无法配置任务、查看任务完成情况
2. ❌ **实时通知** - 无法向用户发送实时通知
3. ❌ **批量操作** - 部分功能缺少批量操作支持

---

## 数据一致性保证

### 1. 余额一致性

- **游戏端**: 使用 `LedgerService` 管理余额，确保账本一致性
- **后台管理**: 同样使用 `LedgerService` 调整余额，保持一致性
- **数据源**: `ledger_entries` 表是唯一真实数据源

### 2. 红包状态一致性

- **游戏端**: 创建红包时，同时写入数据库和 Redis
- **后台管理**: 退款/完成红包时，同时更新数据库和清理 Redis
- **数据源**: `red_packets` 表是主数据源，Redis 是缓存

### 3. 推荐关系一致性

- **游戏端**: 用户注册时，自动建立推荐关系
- **后台管理**: 可以查看和统计推荐关系，但不能修改
- **数据源**: `users` 表的 `invited_by` 字段

---

## 安全与权限

### 游戏端权限

- ✅ 用户只能操作自己的数据
- ✅ 使用 JWT Token 或 Telegram initData 认证
- ✅ API 端点有权限验证（`get_current_user_from_token`）

### 后台管理权限

- ✅ 管理员需要登录认证
- ✅ 所有管理API都需要管理员权限（`get_current_admin`）
- ✅ 敏感操作（退款、余额调整）记录操作日志

---

## 总结

### 对齐状态

- ✅ **用户管理**: 完全对齐
- ✅ **红包系统**: 完全对齐 + 增强（后台可调度红包雨）
- ✅ **钱包交易**: 完全对齐 + 增强（后台显示余额分类）
- ✅ **推荐系统**: 完全对齐 + 增强（后台可配置佣金）
- ✅ **签到系统**: 完全对齐
- ⚠️ **任务系统**: 部分对齐（后台缺少任务管理）
- ✅ **数据统计**: 完全对齐

### 数据流

- ✅ 游戏端和后台共享同一数据库
- ✅ 使用 `LedgerService` 确保余额一致性
- ✅ Redis 用于高并发场景（抢红包）
- ✅ 所有关键操作都有日志记录

### 扩展性

- ✅ 系统设计支持水平扩展
- ✅ API 设计遵循 RESTful 规范
- ✅ 前后端分离，易于维护和升级

---

**文档版本**: v1.0  
**最后更新**: 2025-01-XX  
**维护者**: Lead Full-Stack Architect

