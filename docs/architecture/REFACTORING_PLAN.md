# 🏗️ Global Social-Fi Platform - 完整重构计划

## 📋 执行摘要

将当前Telegram红包游戏重构为支持多平台、多支付方式的全球Social-Fi平台。

**核心原则**：
- **链下优先**：所有游戏操作在链下完成，只有存取款上链
- **平台适配**：根据平台（iOS/Android/Web）动态调整UI
- **统一身份**：一个用户可以在多个平台使用同一账户
- **高并发**：支持10k+并发抢红包操作

---

## 🎯 Pillar 1: Universal Identity System

### 1.1 数据库Schema重构

```sql
-- 用户主表（统一身份）
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    username VARCHAR(100),
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- 链下余额（游戏币）
    balance_usdt DECIMAL(20, 8) DEFAULT 0,
    balance_ton DECIMAL(20, 8) DEFAULT 0,
    balance_stars DECIMAL(20, 8) DEFAULT 0,
    balance_points DECIMAL(20, 8) DEFAULT 0,
    
    -- 链上地址（可选）
    wallet_address VARCHAR(255),
    wallet_network VARCHAR(50), -- 'TON', 'ETH', 'BSC'
    
    -- 推荐系统
    referrer_id INTEGER REFERENCES users(id),
    referral_code VARCHAR(20) UNIQUE,
    total_referrals INTEGER DEFAULT 0,
    tier1_commission DECIMAL(5, 2) DEFAULT 0, -- 一级佣金率
    tier2_commission DECIMAL(5, 2) DEFAULT 0,  -- 二级佣金率
    
    -- 平台标识
    primary_platform VARCHAR(20), -- 'telegram', 'web', 'mobile'
    last_active_at TIMESTAMP,
    
    -- 合规标志
    kyc_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'verified', 'rejected'
    kyc_verified_at TIMESTAMP
);

-- 身份提供者关联表（多对多）
CREATE TABLE user_identities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL, -- 'telegram', 'google', 'wallet', 'email'
    provider_user_id VARCHAR(255) NOT NULL, -- Telegram ID, Google ID, Wallet Address
    provider_data JSONB, -- 存储provider特定的数据
    is_primary BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(provider, provider_user_id)
);

-- 账户链接表（Magic Link）
CREATE TABLE account_links (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    link_token VARCHAR(64) UNIQUE NOT NULL,
    link_type VARCHAR(20) NOT NULL, -- 'magic_login', 'wallet_link', 'cross_platform'
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_user_identities_user_id ON user_identities(user_id);
CREATE INDEX idx_user_identities_provider ON user_identities(provider, provider_user_id);
CREATE INDEX idx_users_referral_code ON users(referral_code);
CREATE INDEX idx_account_links_token ON account_links(link_token);
```

### 1.2 API路由结构

```
/api/v1/
├── auth/
│   ├── telegram/          # Telegram认证（现有）
│   │   └── POST /init     # 使用initData登录
│   ├── web/               # Web认证
│   │   ├── POST /google   # Google OAuth登录
│   │   ├── POST /wallet   # Wallet连接（签名验证）
│   │   └── POST /email    # Email/Password登录
│   └── link/              # 账户链接
│       ├── POST /magic-link/generate  # 生成Magic Link
│       ├── POST /magic-link/verify    # 验证Magic Link
│       └── POST /wallet/link          # 链接钱包地址
│
├── users/
│   ├── GET /me            # 获取当前用户（自动识别平台）
│   ├── PUT /me            # 更新用户信息
│   ├── GET /me/identities # 获取所有关联身份
│   └── POST /me/identities/link # 链接新身份
│
└── platform/
    ├── GET /detect        # 检测当前平台
    └── GET /rules        # 获取平台规则（UI配置）
```

### 1.3 前端AuthGuard实现

```typescript
// frontend/src/utils/auth/AuthGuard.tsx
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getTelegram, isTelegramEnv } from '../telegram'
import { detectPlatform, Platform } from '../platform'

interface AuthState {
  user: User | null
  loading: boolean
  platform: Platform
}

export function useAuth(): AuthState {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    loading: true,
    platform: detectPlatform()
  })

  useEffect(() => {
    initAuth()
  }, [])

  const initAuth = async () => {
    const platform = detectPlatform()
    
    if (platform === 'telegram') {
      // Telegram环境：自动登录
      await loginWithTelegram()
    } else if (platform === 'web') {
      // Web环境：检查本地token或显示登录按钮
      await checkWebAuth()
    }
  }

  const loginWithTelegram = async () => {
    const telegram = getTelegram()
    if (!telegram?.initData) {
      setAuthState({ user: null, loading: false, platform: 'telegram' })
      return
    }

    try {
      const response = await fetch('/api/v1/auth/telegram/init', {
        method: 'POST',
        headers: {
          'X-Telegram-Init-Data': telegram.initData
        }
      })
      const user = await response.json()
      setAuthState({ user, loading: false, platform: 'telegram' })
    } catch (error) {
      console.error('Telegram auth failed:', error)
      setAuthState({ user: null, loading: false, platform: 'telegram' })
    }
  }

  const checkWebAuth = async () => {
    const token = localStorage.getItem('auth_token')
    if (!token) {
      setAuthState({ user: null, loading: false, platform: 'web' })
      return
    }

    try {
      const response = await fetch('/api/v1/users/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const user = await response.json()
        setAuthState({ user, loading: false, platform: 'web' })
      } else {
        localStorage.removeItem('auth_token')
        setAuthState({ user: null, loading: false, platform: 'web' })
      }
    } catch (error) {
      setAuthState({ user: null, loading: false, platform: 'web' })
    }
  }

  return authState
}

// AuthGuard组件
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading, platform } = useAuth()
  const navigate = useNavigate()

  if (loading) {
    return <LoadingScreen />
  }

  if (!user && platform === 'web') {
    return <WebLoginScreen />
  }

  if (!user && platform === 'telegram') {
    return <div>Telegram环境需要initData</div>
  }

  return <>{children}</>
}
```

---

## 💰 Pillar 2: Off-Chain Ledger System

### 2.1 账本表结构

```sql
-- 账本条目表（复式记账）
CREATE TABLE ledger_entries (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    
    -- 金额信息
    amount DECIMAL(20, 8) NOT NULL,
    currency VARCHAR(10) NOT NULL, -- 'USDT', 'TON', 'STARS', 'POINTS'
    type VARCHAR(50) NOT NULL, -- 'DEPOSIT', 'WITHDRAW', 'GAME_WIN', 'GAME_LOSS', 'REDPACKET_SEND', 'REDPACKET_CLAIM', 'COMMISSION'
    
    -- 关联信息
    related_type VARCHAR(50), -- 'red_packet', 'game_bet', 'payment', 'referral'
    related_id BIGINT,
    
    -- 余额快照
    balance_before DECIMAL(20, 8) NOT NULL,
    balance_after DECIMAL(20, 8) NOT NULL,
    
    -- 元数据
    metadata JSONB,
    description TEXT,
    
    -- 审计字段
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(50), -- 'system', 'user', 'payment_gateway'
    
    -- 索引
    INDEX idx_ledger_user_id (user_id),
    INDEX idx_ledger_type (type),
    INDEX idx_ledger_related (related_type, related_id),
    INDEX idx_ledger_created_at (created_at)
);

-- 余额快照表（用于快速查询）
CREATE TABLE user_balances (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    usdt_balance DECIMAL(20, 8) DEFAULT 0,
    ton_balance DECIMAL(20, 8) DEFAULT 0,
    stars_balance DECIMAL(20, 8) DEFAULT 0,
    points_balance DECIMAL(20, 8) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Redis缓存键：user:balance:{user_id}
);
```

### 2.2 Redis + Lua脚本（高并发抢红包）

```lua
-- scripts/redis/claim_redpacket.lua
-- KEYS[1] = redpacket:{id}:claims
-- KEYS[2] = redpacket:{id}:amount
-- ARGV[1] = user_id
-- ARGV[2] = claim_amount

local claims = redis.call('GET', KEYS[1])
local total_amount = redis.call('GET', KEYS[2])

if not claims then
    return {err = 'REDPACKET_NOT_FOUND'}
end

if tonumber(claims) <= 0 then
    return {err = 'REDPACKET_EXHAUSTED'}
end

if tonumber(total_amount) < tonumber(ARGV[2]) then
    return {err = 'INSUFFICIENT_AMOUNT'}
end

-- 原子操作：减少剩余数量和总金额
local new_claims = redis.call('DECR', KEYS[1])
local new_amount = redis.call('DECRBY', KEYS[2], ARGV[2])

-- 记录用户已抢
redis.call('SADD', 'redpacket:' .. ARGV[1] .. ':claimed', ARGV[1])

return {
    success = true,
    remaining_claims = new_claims,
    remaining_amount = new_amount,
    claim_amount = ARGV[2]
}
```

### 2.3 LedgerService实现

```python
# api/services/ledger_service.py
from decimal import Decimal
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import json

from shared.database.models import User, LedgerEntry, UserBalance
from shared.database.connection import get_db_session

class LedgerService:
    """链下账本服务 - 复式记账"""
    
    @staticmethod
    async def create_entry(
        db: AsyncSession,
        user_id: int,
        amount: Decimal,
        currency: str,
        entry_type: str,
        related_type: Optional[str] = None,
        related_id: Optional[int] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LedgerEntry:
        """创建账本条目并更新余额"""
        
        # 获取当前余额
        result = await db.execute(
            select(UserBalance).where(UserBalance.user_id == user_id)
        )
        balance = result.scalar_one_or_none()
        
        if not balance:
            # 初始化余额
            balance = UserBalance(user_id=user_id)
            db.add(balance)
        
        # 计算新余额
        balance_before = getattr(balance, f'{currency.lower()}_balance', Decimal('0'))
        balance_after = balance_before + amount
        
        # 更新余额
        setattr(balance, f'{currency.lower()}_balance', balance_after)
        balance.updated_at = datetime.utcnow()
        
        # 创建账本条目
        entry = LedgerEntry(
            user_id=user_id,
            amount=amount,
            currency=currency.upper(),
            type=entry_type,
            related_type=related_type,
            related_id=related_id,
            balance_before=balance_before,
            balance_after=balance_after,
            description=description,
            metadata=json.dumps(metadata) if metadata else None,
            created_at=datetime.utcnow()
        )
        
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        
        # 更新Redis缓存
        await LedgerService._update_redis_balance(user_id, currency, balance_after)
        
        return entry
    
    @staticmethod
    async def _update_redis_balance(user_id: int, currency: str, balance: Decimal):
        """更新Redis余额缓存"""
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        key = f"user:balance:{user_id}:{currency.lower()}"
        r.setex(key, 3600, str(balance))  # 1小时过期
    
    @staticmethod
    async def get_balance(
        db: AsyncSession,
        user_id: int,
        currency: str = 'USDT'
    ) -> Decimal:
        """获取用户余额（优先从Redis）"""
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        cache_key = f"user:balance:{user_id}:{currency.lower()}"
        
        # 尝试从Redis获取
        cached = r.get(cache_key)
        if cached:
            return Decimal(cached.decode())
        
        # 从数据库获取
        result = await db.execute(
            select(UserBalance).where(UserBalance.user_id == user_id)
        )
        balance = result.scalar_one_or_none()
        
        if not balance:
            return Decimal('0')
        
        amount = getattr(balance, f'{currency.lower()}_balance', Decimal('0'))
        
        # 更新Redis缓存
        r.setex(cache_key, 3600, str(amount))
        
        return amount
```

---

## 💳 Pillar 3: Smart Payment Gateway

### 3.1 支付服务抽象层

```python
# api/services/payment_service.py
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any, Optional
from enum import Enum

class PaymentProvider(Enum):
    UNIONPAY = "unionpay"
    ALIPAY = "alipay"
    WECHAT = "wechat"
    VISA = "visa"
    MOCK = "mock"  # 测试用

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PaymentService(ABC):
    """支付服务抽象基类"""
    
    @abstractmethod
    async def create_order(
        self,
        user_id: int,
        amount: Decimal,
        currency: str,
        payment_method: str
    ) -> Dict[str, Any]:
        """创建支付订单"""
        pass
    
    @abstractmethod
    async def verify_payment(
        self,
        order_id: str,
        payment_data: Dict[str, Any]
    ) -> bool:
        """验证支付结果"""
        pass

class MockUnionPayService(PaymentService):
    """模拟UnionPay支付服务（用于开发测试）"""
    
    def __init__(self, exchange_rate_api_url: str):
        self.exchange_rate_api = exchange_rate_api_url
        self.profit_spread = Decimal('0.03')  # 3%利润
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """获取实时汇率"""
        # 实际实现：调用汇率API
        # 这里模拟返回
        if from_currency == 'CNY' and to_currency == 'USDT':
            # 模拟：1 CNY = 0.14 USDT (约7.1 CNY/USDT)
            return Decimal('0.14')
        return Decimal('1')
    
    async def calculate_internal_credit(
        self,
        fiat_amount: Decimal,
        fiat_currency: str
    ) -> Decimal:
        """计算内部信用额度（含利润）"""
        rate = await self.get_exchange_rate(fiat_currency, 'USDT')
        base_credit = fiat_amount * rate
        profit = base_credit * self.profit_spread
        return base_credit + profit
    
    async def create_order(
        self,
        user_id: int,
        amount: Decimal,
        currency: str,
        payment_method: str
    ) -> Dict[str, Any]:
        """创建支付订单"""
        # 计算内部信用
        internal_credit = await self.calculate_internal_credit(amount, currency)
        
        # 创建订单记录
        order = {
            'order_id': f"ORDER_{user_id}_{int(datetime.now().timestamp())}",
            'user_id': user_id,
            'fiat_amount': str(amount),
            'fiat_currency': currency,
            'internal_credit': str(internal_credit),
            'internal_currency': 'USDT',
            'status': 'pending',
            'payment_method': payment_method,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # 保存到数据库
        # await save_payment_order(order)
        
        return {
            'order_id': order['order_id'],
            'payment_url': f"/mock-payment/{order['order_id']}",  # 模拟支付URL
            'amount': str(amount),
            'currency': currency,
            'internal_credit': str(internal_credit),
            'internal_currency': 'USDT'
        }
    
    async def verify_payment(
        self,
        order_id: str,
        payment_data: Dict[str, Any]
    ) -> bool:
        """验证支付（模拟：总是返回成功）"""
        # 实际实现：调用UnionPay API验证
        return True

# 支付服务工厂
class PaymentServiceFactory:
    @staticmethod
    def create(provider: PaymentProvider) -> PaymentService:
        if provider == PaymentProvider.MOCK:
            return MockUnionPayService("https://api.exchangerate.host")
        elif provider == PaymentProvider.UNIONPAY:
            # 实际实现：返回真实的UnionPay服务
            pass
        else:
            raise ValueError(f"Unsupported provider: {provider}")
```

### 3.2 支付API路由

```python
# api/routers/payments.py
from fastapi import APIRouter, Depends, HTTPException
from decimal import Decimal
from api.services.payment_service import PaymentServiceFactory, PaymentProvider
from api.services.ledger_service import LedgerService

router = APIRouter()

@router.post("/deposit")
async def create_deposit(
    amount: Decimal,
    currency: str,  # 'CNY', 'USD', etc.
    payment_method: str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session)
):
    """创建充值订单"""
    payment_service = PaymentServiceFactory.create(PaymentProvider.MOCK)
    
    order = await payment_service.create_order(
        user_id=user_id,
        amount=amount,
        currency=currency,
        payment_method=payment_method
    )
    
    return order

@router.post("/deposit/callback")
async def deposit_callback(
    order_id: str,
    payment_data: dict,
    db: AsyncSession = Depends(get_db_session)
):
    """支付回调（由支付网关调用）"""
    payment_service = PaymentServiceFactory.create(PaymentProvider.MOCK)
    
    # 验证支付
    if not await payment_service.verify_payment(order_id, payment_data):
        raise HTTPException(status_code=400, detail="Payment verification failed")
    
    # 获取订单信息
    order = await get_payment_order(order_id)
    
    # 充值到账本
    await LedgerService.create_entry(
        db=db,
        user_id=order['user_id'],
        amount=Decimal(order['internal_credit']),
        currency=order['internal_currency'],
        entry_type='DEPOSIT',
        related_type='payment',
        related_id=order_id,
        description=f"Deposit {order['fiat_amount']} {order['fiat_currency']}"
    )
    
    return {"status": "success"}
```

---

## 📱 Pillar 4: Compliance & Chameleon UI

### 4.1 平台检测工具

```typescript
// frontend/src/utils/platform.ts
export type Platform = 'ios' | 'android' | 'web' | 'telegram'

export interface PlatformRules {
  showDeposit: boolean
  showWithdraw: boolean
  showExchange: boolean
  showFiatPayment: boolean
  allowedCurrencies: string[]
  minWithdrawAmount: number
}

export function detectPlatform(): Platform {
  // Telegram环境
  if (window.Telegram?.WebApp) {
    return 'telegram'
  }
  
  // iOS检测
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1)
  
  if (isIOS) {
    return 'ios'
  }
  
  // Android检测
  if (/Android/.test(navigator.userAgent)) {
    return 'android'
  }
  
  return 'web'
}

export async function getPlatformRules(): Promise<PlatformRules> {
  const platform = detectPlatform()
  
  // 从API获取规则（可以动态配置）
  const response = await fetch(`/api/v1/platform/rules?platform=${platform}`)
  const rules = await response.json()
  
  return rules
}

// 默认规则
export const DEFAULT_RULES: Record<Platform, PlatformRules> = {
  ios: {
    showDeposit: false,
    showWithdraw: false,
    showExchange: false,
    showFiatPayment: false,
    allowedCurrencies: ['STARS', 'POINTS'],
    minWithdrawAmount: 0
  },
  android: {
    showDeposit: true,
    showWithdraw: true,
    showExchange: true,
    showFiatPayment: true,
    allowedCurrencies: ['USDT', 'TON', 'STARS', 'POINTS'],
    minWithdrawAmount: 10
  },
  web: {
    showDeposit: true,
    showWithdraw: true,
    showExchange: true,
    showFiatPayment: true,
    allowedCurrencies: ['USDT', 'TON', 'STARS', 'POINTS'],
    minWithdrawAmount: 10
  },
  telegram: {
    showDeposit: true,
    showWithdraw: true,
    showExchange: true,
    showFiatPayment: true,
    allowedCurrencies: ['USDT', 'TON', 'STARS', 'POINTS'],
    minWithdrawAmount: 10
  }
}
```

### 4.2 条件渲染组件

```typescript
// frontend/src/components/PlatformAware.tsx
import { usePlatformRules } from '../hooks/usePlatformRules'

export function DepositButton() {
  const { rules } = usePlatformRules()
  
  if (!rules.showDeposit) {
    return null  // iOS不显示
  }
  
  return <button>Deposit</button>
}

export function FinancialDashboard() {
  const { rules } = usePlatformRules()
  
  return (
    <div>
      {rules.showDeposit && <DepositButton />}
      {rules.showWithdraw && <WithdrawButton />}
      {rules.showExchange && <ExchangeButton />}
      {/* 始终显示 */}
      <GameButton />
      <RedPacketButton />
    </div>
  )
}
```

---

## 🚀 Pillar 5: Viral Growth Engine

### 5.1 深度链接系统

```python
# api/routers/deeplink.py
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import urllib.parse

router = APIRouter()

@router.get("/packet/{packet_id}")
async def smart_redirect(
    packet_id: str,
    request: Request
):
    """智能深度链接：根据来源平台跳转"""
    user_agent = request.headers.get('user-agent', '').lower()
    referer = request.headers.get('referer', '')
    
    # 检测来源
    if 'telegram' in user_agent or 't.me' in referer:
        # Telegram环境：打开MiniApp
        return RedirectResponse(
            url=f"https://t.me/your_bot/app?startapp=packet_{packet_id}"
        )
    elif 'whatsapp' in user_agent or 'wa.me' in referer:
        # WhatsApp：打开H5版本
        return RedirectResponse(
            url=f"https://mygame.com/web/packet/{packet_id}"
        )
    else:
        # 默认：Web版本
        return RedirectResponse(
            url=f"https://mygame.com/web/packet/{packet_id}"
        )
```

### 5.2 推荐系统实现

```python
# api/services/referral_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

class ReferralService:
    @staticmethod
    async def process_commission(
        db: AsyncSession,
        user_id: int,
        amount: Decimal,
        transaction_type: str
    ):
        """处理推荐佣金（递归计算Tier1和Tier2）"""
        user = await get_user(db, user_id)
        if not user or not user.referrer_id:
            return
        
        # Tier 1 佣金（直接推荐人）
        tier1_user = await get_user(db, user.referrer_id)
        if tier1_user:
            commission_rate = tier1_user.tier1_commission or Decimal('0.10')  # 10%
            commission = amount * commission_rate
            
            await LedgerService.create_entry(
                db=db,
                user_id=tier1_user.id,
                amount=commission,
                currency='USDT',
                entry_type='COMMISSION',
                related_type='referral',
                related_id=user_id,
                description=f"Tier 1 commission from {user.username}"
            )
            
            # Tier 2 佣金（推荐人的推荐人）
            if tier1_user.referrer_id:
                tier2_user = await get_user(db, tier1_user.referrer_id)
                if tier2_user:
                    commission_rate = tier2_user.tier2_commission or Decimal('0.05')  # 5%
                    commission = amount * commission_rate
                    
                    await LedgerService.create_entry(
                        db=db,
                        user_id=tier2_user.id,
                        amount=commission,
                        currency='USDT',
                        entry_type='COMMISSION',
                        related_type='referral',
                        related_id=user_id,
                        description=f"Tier 2 commission from {user.username}"
                    )
```

---

## 📝 实施检查清单

### Phase 1: 数据库重构（Week 1）
- [ ] 创建新的数据库迁移脚本
- [ ] 迁移现有用户数据到新schema
- [ ] 创建user_identities表
- [ ] 创建ledger_entries表
- [ ] 创建account_links表
- [ ] 添加推荐系统字段

### Phase 2: 身份系统（Week 2）
- [ ] 实现AuthGuard组件
- [ ] 实现Telegram认证（现有）
- [ ] 实现Google OAuth登录
- [ ] 实现Wallet连接
- [ ] 实现Magic Link生成和验证
- [ ] 实现账户链接API

### Phase 3: 账本系统（Week 3）
- [ ] 实现LedgerService
- [ ] 实现Redis余额缓存
- [ ] 实现高并发抢红包（Lua脚本）
- [ ] 实现BullMQ队列同步
- [ ] 添加账本审计日志

### Phase 4: 支付网关（Week 4）
- [ ] 实现PaymentService抽象层
- [ ] 实现MockUnionPayService
- [ ] 实现汇率API集成
- [ ] 实现自动转换逻辑
- [ ] 实现支付回调处理

### Phase 5: 平台适配（Week 5）
- [ ] 实现平台检测工具
- [ ] 实现PlatformRules API
- [ ] 更新前端组件（条件渲染）
- [ ] iOS版本测试
- [ ] Android版本测试

### Phase 6: 增长引擎（Week 6）
- [ ] 实现深度链接系统
- [ ] 实现推荐佣金系统
- [ ] 实现分享功能
- [ ] 实现跨平台分享
- [ ] 添加分析追踪

---

## 🎯 下一步行动

1. **立即开始**：创建数据库迁移脚本
2. **优先级**：先实现身份系统和账本系统（核心功能）
3. **测试**：每个Phase完成后进行完整测试
4. **部署**：分阶段部署，确保稳定性

需要我继续实现具体的代码吗？

