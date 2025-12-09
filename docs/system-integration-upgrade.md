# Lucky Red - 系统集成与推广升级文档

## 概述

本文档详细说明了3阶段系统集成与推广升级计划的完整实现方案，包括：
- Phase 1: 基础设施修复（Nginx路由）
- Phase 2: 游戏-后台数据同步（红包控制、财务监控）
- Phase 3: 病毒式增长引擎（3层推荐系统、红包雨调度器）

---

## Phase 1: 基础设施修复（Nginx路由）

### 1.1 修复后的 Nginx 配置

**文件位置**: `deploy/nginx/admin.usdt2026.cc.conf`

```nginx
# Admin 後台 - HTTP 重定向到 HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name admin.usdt2026.cc;
    
    # 強制重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

# Admin 後台 - HTTPS 主配置
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name admin.usdt2026.cc;

    # SSL 證書配置（由 certbot 管理）
    ssl_certificate /etc/letsencrypt/live/admin.usdt2026.cc/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.usdt2026.cc/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # 管理後台靜態文件根目錄（嚴格指向 admin frontend）
    root /home/ubuntu/hbgm001/admin/frontend/dist;
    index index.html;

    # 日誌配置
    access_log /var/log/nginx/admin.usdt2026.cc.access.log;
    error_log /var/log/nginx/admin.usdt2026.cc.error.log;

    # API 代理 - 處理所有 /api/ 請求
    location /api/ {
        proxy_pass http://127.0.0.1:8080/api/;
        proxy_http_version 1.1;
        
        # 基本代理頭
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # CORS 支持
        add_header Access-Control-Allow-Origin $http_origin always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Telegram-Init-Data" always;
        add_header Access-Control-Allow-Credentials true always;
        
        # 處理 OPTIONS 預檢請求
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin $http_origin always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Telegram-Init-Data" always;
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type 'text/plain charset=UTF-8';
            add_header Content-Length 0;
            return 204;
        }
        
        # 超時設置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 緩衝區設置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # 前端靜態資源（JS, CSS, 圖片等）- 長期緩存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|map)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
        try_files $uri =404;
    }

    # 前端路由 (SPA) - 必須放在最後，處理所有其他請求
    location / {
        # SPA 路由支持：嘗試文件，如果不存在則返回 index.html
        try_files $uri $uri/ /index.html;
        
        # 禁用 HTML 緩存（確保 SPA 更新）
        add_header Cache-Control "no-cache, no-store, must-revalidate, max-age=0" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
        
        # 內容類型
        default_type text/html;
    }

    # 安全頭
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # 禁止訪問隱藏文件
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

### 1.2 部署步骤

```bash
# 1. 复制配置文件到服务器
sudo cp deploy/nginx/admin.usdt2026.cc.conf /etc/nginx/sites-available/admin.usdt2026.cc.conf

# 2. 创建软链接（如果不存在）
sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/admin.usdt2026.cc.conf

# 3. 测试配置
sudo nginx -t

# 4. 重新加载 Nginx
sudo systemctl reload nginx

# 5. 验证访问
curl -I https://admin.usdt2026.cc
```

---

## Phase 2: 游戏-后台数据同步

### 2.1 增强红包退款功能（使用 LedgerService）

**文件位置**: `api/routers/admin_redpackets.py`

在现有的 `refund_redpacket` 函数中，需要更新为使用 `LedgerService`：

```python
@router.post("/{redpacket_id}/refund")
async def refund_redpacket(
    redpacket_id: int,
    reason: Optional[str] = Query(None, description="退款原因"),
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
    """手动退款红包（使用 LedgerService）"""
    query = select(RedPacket).where(RedPacket.id == redpacket_id)
    result = await db.execute(query)
    redpacket = result.scalar_one_or_none()
    
    if not redpacket:
        raise HTTPException(status_code=404, detail="紅包不存在")
    
    if redpacket.status == RedPacketStatus.REFUNDED:
        raise HTTPException(status_code=400, detail="紅包已退款")
    
    # 查找發送者
    sender_result = await db.execute(select(User).where(User.id == redpacket.sender_id))
    sender = sender_result.scalar_one_or_none()
    
    if not sender:
        raise HTTPException(status_code=404, detail="發送者不存在")
    
    # 計算需要退還的金額
    remaining_amount = redpacket.total_amount - redpacket.claimed_amount
    
    if remaining_amount <= 0:
        raise HTTPException(status_code=400, detail="沒有可退還的金額")
    
    # 使用 LedgerService 退款（確保賬本一致性）
    from api.services.ledger_service import LedgerService
    
    try:
        # 創建退款賬本條目
        await LedgerService.create_entry(
            db=db,
            user_id=sender.id,
            amount=remaining_amount,  # 正數表示增加餘額
            currency=redpacket.currency.value.upper(),
            entry_type='REFUND',
            related_type='red_packet',
            related_id=redpacket.id,
            description=f"紅包退款: 紅包ID {redpacket.id}, 原因: {reason or '管理員手動退款'}",
            created_by=f"admin_{current_admin.get('id')}"
        )
        
        logger.info(
            f"Red packet refunded via LedgerService: redpacket_id={redpacket_id}, "
            f"sender_id={sender.id}, amount={remaining_amount}, "
            f"currency={redpacket.currency.value}, admin_id={current_admin.get('id')}"
        )
    except ValueError as e:
        logger.error(f"LedgerService refund failed: {e}")
        raise HTTPException(status_code=500, detail=f"退款失敗: {str(e)}")
    
    # 更新紅包狀態
    redpacket.status = RedPacketStatus.REFUNDED
    
    # 如果紅包在 Redis 中，也需要清理
    try:
        from api.services.redis_claim_service import RedisClaimService
        await RedisClaimService.delete_packet(redpacket.uuid)
        logger.info(f"Redis packet deleted: {redpacket.uuid}")
    except Exception as e:
        logger.warning(f"Failed to delete Redis packet: {e}")
    
    await db.commit()
    await db.refresh(redpacket)
    
    return {
        "success": True,
        "message": "退款成功",
        "refunded_amount": float(remaining_amount),
        "currency": redpacket.currency.value,
        "reason": reason or "管理員手動退款"
    }
```

### 2.2 更新交易管理UI显示Real vs Bonus余额

**文件位置**: `admin/frontend/src/pages/TransactionManagement.tsx`

需要在交易列表中添加 Real vs Bonus 余额列：

```typescript
// 在 Transaction 接口中添加余额字段
interface Transaction {
  id: number
  user_id: number
  user_tg_id?: number
  user_username?: string
  user_name?: string
  type: string
  currency: string
  amount: number
  balance_before?: number
  balance_after?: number
  // 新增：余额分类
  balance_real?: number  // 真实余额（可提现）
  balance_bonus?: number  // 奖励余额（仅游戏）
  ref_id?: string
  note?: string
  created_at: string
}

// 在 columns 定义中添加余额列
const columns: ColumnsType<Transaction> = [
  // ... 现有列 ...
  {
    title: '余额分类',
    key: 'balance_breakdown',
    width: 180,
    render: (_, record) => {
      // 从后端获取用户余额详情（需要调用新API）
      const { data: userBalance } = useQuery({
        queryKey: ['user-balance', record.user_id],
        queryFn: async () => {
          const response = await userApi.detailFull(record.user_id)
          return response.data
        },
        enabled: !!record.user_id,
      })
      
      if (!userBalance) return '-'
      
      return (
        <div style={{ fontSize: '12px' }}>
          <div>
            <Tag color="green">真实: {userBalance.balance_real_usdt || 0} USDT</Tag>
          </div>
          <div style={{ marginTop: '4px' }}>
            <Tag color="orange">奖励: {userBalance.balance_bonus_usdt || 0} USDT</Tag>
          </div>
        </div>
      )
    },
  },
  // ... 其他列 ...
]
```

**后端API更新**: `api/routers/admin_transactions.py`

需要在交易列表响应中包含用户余额分类：

```python
# 在 list_transactions 函数中，获取用户余额详情
from api.services.ledger_service import LedgerService

# 构建响应数据
items = []
for tx in transactions:
    user = users.get(tx.user_id)
    
    # 获取用户余额分类（Real vs Bonus）
    balance_breakdown = {}
    if user:
        try:
            # 使用 LedgerService 获取余额分类
            real_balance = await LedgerService.get_balance(
                db=db,
                user_id=user.id,
                currency='USDT',
                source_filter='real_crypto'  # 只计算真实充值
            )
            bonus_balance = await LedgerService.get_balance(
                db=db,
                user_id=user.id,
                currency='USDT',
                source_filter='bonus'  # 只计算奖励
            )
            balance_breakdown = {
                'balance_real_usdt': float(real_balance),
                'balance_bonus_usdt': float(bonus_balance),
            }
        except Exception as e:
            logger.warning(f"Failed to get balance breakdown for user {user.id}: {e}")
    
    items.append(TransactionListItem(
        id=tx.id,
        user_id=tx.user_id,
        user_tg_id=user.tg_id if user else None,
        user_username=user.username if user else None,
        user_name=f"{user.first_name or ''} {user.last_name or ''}".strip() if user else None,
        type=tx.type,
        currency=tx.currency.value,
        amount=tx.amount,
        balance_before=tx.balance_before,
        balance_after=tx.balance_after,
        balance_real=balance_breakdown.get('balance_real_usdt'),
        balance_bonus=balance_breakdown.get('balance_bonus_usdt'),
        ref_id=tx.ref_id,
        note=tx.note,
        status=tx.status,
        created_at=tx.created_at,
    ))
```

---

## Phase 3: 病毒式增长引擎

### 3.1 3层推荐系统配置管理

#### 3.1.1 后端API：推荐系统配置

**文件位置**: `api/routers/admin_invite.py`

添加推荐系统配置管理端点：

```python
from shared.database.models import SystemConfig
from pydantic import BaseModel
from typing import Optional

class CommissionConfigRequest(BaseModel):
    """推荐佣金配置请求"""
    tier1_commission: float = Field(..., ge=0, le=100, description="一级佣金率（%）")
    tier2_commission: float = Field(..., ge=0, le=100, description="二级佣金率（%）")
    tier3_commission: float = Field(0.0, ge=0, le=100, description="三级佣金率（%）")
    agent_bonus_threshold: int = Field(..., ge=1, description="代理奖励阈值（邀请用户数）")
    agent_bonus_amount: float = Field(..., ge=0, description="代理奖励金额（USDT）")
    kol_bonus_threshold: int = Field(100, ge=1, description="KOL奖励阈值（邀请用户数）")
    kol_bonus_amount: float = Field(50.0, ge=0, description="KOL奖励金额（USDT）")

class CommissionConfigResponse(BaseModel):
    """推荐佣金配置响应"""
    tier1_commission: float
    tier2_commission: float
    tier3_commission: float
    agent_bonus_threshold: int
    agent_bonus_amount: float
    kol_bonus_threshold: int
    kol_bonus_amount: float
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

@router.get("/commission-config", response_model=CommissionConfigResponse)
async def get_commission_config(
    db: AsyncSession = Depends(get_db_session),
    admin: AdminUser = Depends(get_current_active_admin),
):
    """获取推荐佣金配置"""
    config = await db.scalar(
        select(SystemConfig).where(SystemConfig.key == "referral_commission_config")
    )
    
    if not config:
        # 返回默认配置
        return CommissionConfigResponse(
            tier1_commission=5.0,
            tier2_commission=2.0,
            tier3_commission=0.0,
            agent_bonus_threshold=100,
            agent_bonus_amount=50.0,
            kol_bonus_threshold=100,
            kol_bonus_amount=50.0,
        )
    
    config_data = config.value or {}
    return CommissionConfigResponse(
        tier1_commission=config_data.get("tier1_commission", 5.0),
        tier2_commission=config_data.get("tier2_commission", 2.0),
        tier3_commission=config_data.get("tier3_commission", 0.0),
        agent_bonus_threshold=config_data.get("agent_bonus_threshold", 100),
        agent_bonus_amount=config_data.get("agent_bonus_amount", 50.0),
        kol_bonus_threshold=config_data.get("kol_bonus_threshold", 100),
        kol_bonus_amount=config_data.get("kol_bonus_amount", 50.0),
        updated_at=config.updated_at,
        updated_by=config.updated_by,
    )

@router.post("/commission-config", response_model=CommissionConfigResponse)
async def update_commission_config(
    request: CommissionConfigRequest,
    db: AsyncSession = Depends(get_db_session),
    admin: AdminUser = Depends(get_current_active_admin),
):
    """更新推荐佣金配置"""
    config = await db.scalar(
        select(SystemConfig).where(SystemConfig.key == "referral_commission_config")
    )
    
    config_data = {
        "tier1_commission": request.tier1_commission,
        "tier2_commission": request.tier2_commission,
        "tier3_commission": request.tier3_commission,
        "agent_bonus_threshold": request.agent_bonus_threshold,
        "agent_bonus_amount": request.agent_bonus_amount,
        "kol_bonus_threshold": request.kol_bonus_threshold,
        "kol_bonus_amount": request.kol_bonus_amount,
    }
    
    if config:
        config.value = config_data
        config.updated_by = admin.id
        config.updated_at = datetime.utcnow()
    else:
        config = SystemConfig(
            key="referral_commission_config",
            value=config_data,
            description="推荐系统佣金配置（3层推荐系统）",
            updated_by=admin.id,
        )
        db.add(config)
    
    await db.commit()
    await db.refresh(config)
    
    logger.info(
        f"Commission config updated by admin {admin.id}: "
        f"Tier1={request.tier1_commission}%, Tier2={request.tier2_commission}%, "
        f"Tier3={request.tier3_commission}%"
    )
    
    return CommissionConfigResponse(
        tier1_commission=request.tier1_commission,
        tier2_commission=request.tier2_commission,
        tier3_commission=request.tier3_commission,
        agent_bonus_threshold=request.agent_bonus_threshold,
        agent_bonus_amount=request.agent_bonus_amount,
        kol_bonus_threshold=request.kol_bonus_threshold,
        kol_bonus_amount=request.kol_bonus_amount,
        updated_at=config.updated_at,
        updated_by=config.updated_by,
    )
```

#### 3.1.2 前端组件：推荐系统配置表单

**文件位置**: `admin/frontend/src/pages/InviteManagement.tsx`

在 `InviteManagement` 组件中添加"佣金配置"部分：

```typescript
import { Form, InputNumber, Button, Card, message, Divider } from 'antd'
import { SettingOutlined, SaveOutlined } from '@ant-design/icons'

// 在组件中添加状态
const [commissionConfig, setCommissionConfig] = useState({
  tier1_commission: 5.0,
  tier2_commission: 2.0,
  tier3_commission: 0.0,
  agent_bonus_threshold: 100,
  agent_bonus_amount: 50.0,
  kol_bonus_threshold: 100,
  kol_bonus_amount: 50.0,
})

const [configForm] = Form.useForm()

// 获取配置
const { data: configData, refetch: refetchConfig } = useQuery({
  queryKey: ['commission-config'],
  queryFn: async () => {
    const response = await inviteApi.getCommissionConfig()
    return response.data
  },
})

// 更新配置
const updateConfigMutation = useMutation({
  mutationFn: async (values: any) => {
    const response = await inviteApi.updateCommissionConfig(values)
    return response.data
  },
  onSuccess: () => {
    message.success('佣金配置更新成功')
    refetchConfig()
  },
  onError: (error: any) => {
    message.error(`更新失败: ${error.message}`)
  },
})

// 在 JSX 中添加配置表单
<Card
  title={
    <span>
      <SettingOutlined /> 佣金配置
    </span>
  }
  style={{ marginBottom: 24 }}
>
  <Form
    form={configForm}
    layout="vertical"
    initialValues={configData || commissionConfig}
    onFinish={(values) => {
      updateConfigMutation.mutate(values)
    }}
  >
    <Row gutter={16}>
      <Col span={8}>
        <Form.Item
          label="一级佣金率 (%)"
          name="tier1_commission"
          rules={[{ required: true, message: '请输入一级佣金率' }]}
        >
          <InputNumber
            min={0}
            max={100}
            step={0.1}
            style={{ width: '100%' }}
            addonAfter="%"
          />
        </Form.Item>
      </Col>
      <Col span={8}>
        <Form.Item
          label="二级佣金率 (%)"
          name="tier2_commission"
          rules={[{ required: true, message: '请输入二级佣金率' }]}
        >
          <InputNumber
            min={0}
            max={100}
            step={0.1}
            style={{ width: '100%' }}
            addonAfter="%"
          />
        </Form.Item>
      </Col>
      <Col span={8}>
        <Form.Item
          label="三级佣金率 (%)"
          name="tier3_commission"
        >
          <InputNumber
            min={0}
            max={100}
            step={0.1}
            style={{ width: '100%' }}
            addonAfter="%"
          />
        </Form.Item>
      </Col>
    </Row>
    
    <Divider>代理奖励配置</Divider>
    
    <Row gutter={16}>
      <Col span={12}>
        <Form.Item
          label="代理奖励阈值（邀请用户数）"
          name="agent_bonus_threshold"
          rules={[{ required: true, message: '请输入代理奖励阈值' }]}
        >
          <InputNumber
            min={1}
            style={{ width: '100%' }}
            addonAfter="人"
          />
        </Form.Item>
      </Col>
      <Col span={12}>
        <Form.Item
          label="代理奖励金额"
          name="agent_bonus_amount"
          rules={[{ required: true, message: '请输入代理奖励金额' }]}
        >
          <InputNumber
            min={0}
            step={0.01}
            style={{ width: '100%' }}
            addonAfter="USDT"
          />
        </Form.Item>
      </Col>
    </Row>
    
    <Divider>KOL奖励配置</Divider>
    
    <Row gutter={16}>
      <Col span={12}>
        <Form.Item
          label="KOL奖励阈值（邀请用户数）"
          name="kol_bonus_threshold"
          rules={[{ required: true, message: '请输入KOL奖励阈值' }]}
        >
          <InputNumber
            min={1}
            style={{ width: '100%' }}
            addonAfter="人"
          />
        </Form.Item>
      </Col>
      <Col span={12}>
        <Form.Item
          label="KOL奖励金额"
          name="kol_bonus_amount"
          rules={[{ required: true, message: '请输入KOL奖励金额' }]}
        >
          <InputNumber
            min={0}
            step={0.01}
            style={{ width: '100%' }}
            addonAfter="USDT"
          />
        </Form.Item>
      </Col>
    </Row>
    
    <Form.Item>
      <Button
        type="primary"
        htmlType="submit"
        icon={<SaveOutlined />}
        loading={updateConfigMutation.isPending}
      >
        保存配置
      </Button>
    </Form.Item>
  </Form>
</Card>
```

**更新 API 客户端**: `admin/frontend/src/utils/api.ts`

```typescript
export const inviteApi = {
  list: (params?: any) => api.get('/v1/admin/invite/list', { params }),
  getTree: (userId: number, depth?: number) => api.get(`/v1/admin/invite/tree/${userId}`, { params: { depth } }),
  getStats: () => api.get('/v1/admin/invite/stats'),
  getTrend: (params?: any) => api.get('/v1/admin/invite/trend', { params }),
  // 新增：佣金配置
  getCommissionConfig: () => api.get('/v1/admin/invite/commission-config'),
  updateCommissionConfig: (data: any) => api.post('/v1/admin/invite/commission-config', data),
}
```

### 3.2 红包雨调度器

#### 3.2.1 后端API：红包雨调度

**文件位置**: `api/routers/admin_redpackets.py`

添加红包雨调度端点：

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class ScheduleRainRequest(BaseModel):
    """红包雨调度请求"""
    start_time: datetime = Field(..., description="开始时间（ISO格式）")
    total_amount: Decimal = Field(..., gt=0, description="总金额")
    currency: CurrencyType = Field(CurrencyType.USDT, description="币种")
    packet_count: int = Field(..., ge=1, le=1000, description="红包数量")
    target_chat_id: Optional[int] = Field(None, description="目标群组ID（None表示公开红包）")
    message: Optional[str] = Field("红包雨来了！", description="红包消息")
    packet_type: RedPacketType = Field(RedPacketType.RANDOM, description="红包类型")

class ScheduleRainResponse(BaseModel):
    """红包雨调度响应"""
    schedule_id: int
    start_time: datetime
    total_amount: Decimal
    currency: str
    packet_count: int
    target_chat_id: Optional[int]
    status: str  # scheduled, executing, completed, cancelled
    created_at: datetime

@router.post("/schedule-rain", response_model=ScheduleRainResponse)
async def schedule_rain(
    request: ScheduleRainRequest,
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
    """调度红包雨"""
    from shared.database.models import ScheduledRedPacketRain
    
    # 验证开始时间（必须在未来）
    if request.start_time <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="开始时间必须在未来")
    
    # 创建调度记录
    schedule = ScheduledRedPacketRain(
        start_time=request.start_time,
        total_amount=request.total_amount,
        currency=request.currency,
        packet_count=request.packet_count,
        target_chat_id=request.target_chat_id,
        message=request.message,
        packet_type=request.packet_type,
        status="scheduled",
        created_by=current_admin.get('id'),
    )
    
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    
    # 将调度任务写入 Redis（用于定时触发）
    try:
        import redis
        from shared.config.settings import get_settings
        settings = get_settings()
        
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        
        # 计算延迟时间（秒）
        delay_seconds = int((request.start_time - datetime.utcnow()).total_seconds())
        
        # 使用 Redis 的延迟队列（或使用 celery/APScheduler）
        schedule_key = f"redpacket_rain:schedule:{schedule.id}"
        redis_client.setex(
            schedule_key,
            delay_seconds + 3600,  # 额外1小时过期时间
            json.dumps({
                "schedule_id": schedule.id,
                "start_time": request.start_time.isoformat(),
                "total_amount": str(request.total_amount),
                "currency": request.currency.value,
                "packet_count": request.packet_count,
                "target_chat_id": request.target_chat_id,
                "message": request.message,
                "packet_type": request.packet_type.value,
            })
        )
        
        logger.info(
            f"Red packet rain scheduled: schedule_id={schedule.id}, "
            f"start_time={request.start_time}, delay_seconds={delay_seconds}"
        )
    except Exception as e:
        logger.error(f"Failed to schedule red packet rain in Redis: {e}")
        # 不阻止创建，但记录错误
    
    return ScheduleRainResponse(
        schedule_id=schedule.id,
        start_time=schedule.start_time,
        total_amount=schedule.total_amount,
        currency=schedule.currency.value,
        packet_count=schedule.packet_count,
        target_chat_id=schedule.target_chat_id,
        status=schedule.status,
        created_at=schedule.created_at,
    )
```

**数据库模型**: `shared/database/models.py`

需要添加 `ScheduledRedPacketRain` 模型：

```python
class ScheduledRedPacketRain(Base):
    """红包雨调度表"""
    __tablename__ = "scheduled_redpacket_rains"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, nullable=False, index=True)
    total_amount = Column(Numeric(20, 8), nullable=False)
    currency = Column(Enum(CurrencyType), nullable=False)
    packet_count = Column(Integer, nullable=False)
    target_chat_id = Column(BigInteger, nullable=True, index=True)
    message = Column(Text, nullable=True)
    packet_type = Column(Enum(RedPacketType), default=RedPacketType.RANDOM)
    status = Column(String(32), default="scheduled", index=True)  # scheduled, executing, completed, cancelled
    created_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index("ix_scheduled_rain_start_time", "start_time"),
        Index("ix_scheduled_rain_status", "status"),
    )
```

#### 3.2.2 前端组件：红包雨调度表单

**文件位置**: `admin/frontend/src/pages/RedPacketManagement.tsx`

添加"调度红包雨"按钮和表单：

```typescript
import { Modal, Form, InputNumber, DatePicker, Select, Input, message } from 'antd'
import { ThunderboltOutlined } from '@ant-design/icons'
import dayjs, { Dayjs } from 'dayjs'

// 在组件中添加状态
const [scheduleRainVisible, setScheduleRainVisible] = useState(false)
const [scheduleForm] = Form.useForm()

// 调度红包雨
const scheduleRainMutation = useMutation({
  mutationFn: async (values: any) => {
    const response = await redpacketApi.scheduleRain({
      ...values,
      start_time: values.start_time.toISOString(),
    })
    return response.data
  },
  onSuccess: () => {
    message.success('红包雨调度成功')
    setScheduleRainVisible(false)
    scheduleForm.resetFields()
    queryClient.invalidateQueries({ queryKey: ['redpackets'] })
  },
  onError: (error: any) => {
    message.error(`调度失败: ${error.message}`)
  },
})

// 在 JSX 中添加按钮和表单
<Button
  type="primary"
  icon={<ThunderboltOutlined />}
  onClick={() => setScheduleRainVisible(true)}
  style={{ marginBottom: 16 }}
>
  调度红包雨
</Button>

<Modal
  title="调度红包雨"
  open={scheduleRainVisible}
  onCancel={() => {
    setScheduleRainVisible(false)
    scheduleForm.resetFields()
  }}
  onOk={() => scheduleForm.submit()}
  confirmLoading={scheduleRainMutation.isPending}
  width={600}
>
  <Form
    form={scheduleForm}
    layout="vertical"
    onFinish={(values) => scheduleRainMutation.mutate(values)}
    initialValues={{
      currency: 'USDT',
      packet_type: 'random',
      message: '红包雨来了！',
    }}
  >
    <Form.Item
      label="开始时间"
      name="start_time"
      rules={[{ required: true, message: '请选择开始时间' }]}
    >
      <DatePicker
        showTime
        format="YYYY-MM-DD HH:mm:ss"
        disabledDate={(current) => current && current < dayjs().startOf('day')}
        style={{ width: '100%' }}
      />
    </Form.Item>
    
    <Form.Item
      label="总金额"
      name="total_amount"
      rules={[{ required: true, message: '请输入总金额' }]}
    >
      <InputNumber
        min={0.01}
        step={0.01}
        style={{ width: '100%' }}
        addonAfter={
          <Form.Item name="currency" noStyle>
            <Select style={{ width: 80 }}>
              <Select.Option value="USDT">USDT</Select.Option>
              <Select.Option value="TON">TON</Select.Option>
            </Select>
          </Form.Item>
        }
      />
    </Form.Item>
    
    <Form.Item
      label="红包数量"
      name="packet_count"
      rules={[{ required: true, message: '请输入红包数量' }]}
    >
      <InputNumber
        min={1}
        max={1000}
        style={{ width: '100%' }}
        addonAfter="个"
      />
    </Form.Item>
    
    <Form.Item
      label="目标群组ID（可选，留空为公开红包）"
      name="target_chat_id"
    >
      <InputNumber
        style={{ width: '100%' }}
        placeholder="留空表示公开红包"
      />
    </Form.Item>
    
    <Form.Item
      label="红包类型"
      name="packet_type"
    >
      <Select>
        <Select.Option value="random">随机红包</Select.Option>
        <Select.Option value="equal">平分红包</Select.Option>
      </Select>
    </Form.Item>
    
    <Form.Item
      label="红包消息"
      name="message"
    >
      <Input.TextArea rows={3} placeholder="红包雨来了！" />
    </Form.Item>
  </Form>
</Modal>
```

**更新 API 客户端**: `admin/frontend/src/utils/api.ts`

```typescript
export const redpacketApi = {
  list: (params?: any) => api.get('/v1/admin/redpackets/list', { params }),
  detail: (id: number) => api.get(`/v1/admin/redpackets/${id}`),
  refund: (id: number) => api.post(`/v1/admin/redpackets/${id}/refund`),
  extend: (id: number, hours: number) => api.post(`/v1/admin/redpackets/${id}/extend`, null, { params: { hours } }),
  complete: (id: number) => api.post(`/v1/admin/redpackets/${id}/complete`),
  delete: (id: number) => api.delete(`/v1/admin/redpackets/${id}`),
  getStats: () => api.get('/v1/admin/redpackets/stats/overview'),
  getTrend: (params?: any) => api.get('/v1/admin/redpackets/stats/trend', { params }),
  // 新增：红包雨调度
  scheduleRain: (data: any) => api.post('/v1/admin/redpackets/schedule-rain', data),
}
```

### 3.3 测试数据脚本：推荐关系树

**文件位置**: `scripts/py/seed_referral_tree.py`

```python
#!/usr/bin/env python3
"""
生成测试推荐关系树数据
用于在后台管理面板中可视化推荐关系
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import datetime
import random
import string

from shared.database.models import User
from shared.config.settings import get_settings
from shared.database.connection import get_async_db

settings = get_settings()

# 创建数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


def generate_invite_code(length=8):
    """生成邀请码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


async def create_referral_tree(db: AsyncSession, depth=3, width=5, parent_tg_id=None, level=0):
    """递归创建推荐关系树"""
    if level >= depth:
        return []
    
    created_users = []
    
    for i in range(width):
        # 创建用户
        tg_id = random.randint(100000000, 999999999)
        invite_code = generate_invite_code()
        
        user = User(
            tg_id=tg_id,
            username=f"test_user_{tg_id}",
            first_name=f"Test{level}_{i}",
            last_name="User",
            invite_code=invite_code,
            invited_by=parent_tg_id,
            invite_count=0,
            invite_earnings=0,
            level=1,
            xp=0,
            balance_usdt=random.uniform(0, 1000),
            balance_ton=random.uniform(0, 100),
            balance_stars=random.randint(0, 10000),
            balance_points=random.randint(0, 50000),
            created_at=datetime.utcnow(),
        )
        
        db.add(user)
        await db.flush()
        
        created_users.append({
            'id': user.id,
            'tg_id': user.tg_id,
            'username': user.username,
            'invite_code': user.invite_code,
            'level': level,
        })
        
        # 递归创建子用户
        children = await create_referral_tree(db, depth, width, user.tg_id, level + 1)
        created_users.extend(children)
        
        # 更新父用户的邀请数
        if parent_tg_id:
            parent = await db.scalar(select(User).where(User.tg_id == parent_tg_id))
            if parent:
                parent.invite_count = (parent.invite_count or 0) + 1
    
    return created_users


async def main():
    """主函数"""
    print("=" * 60)
    print("生成测试推荐关系树数据")
    print("=" * 60)
    
    async with AsyncSessionLocal() as db:
        try:
            # 创建根用户（KOL）
            root_tg_id = random.randint(100000000, 999999999)
            root_user = User(
                tg_id=root_tg_id,
                username="KOL_Root",
                first_name="KOL",
                last_name="Root",
                invite_code=generate_invite_code(),
                invited_by=None,
                invite_count=0,
                invite_earnings=0,
                level=1,
                xp=0,
                balance_usdt=10000,
                balance_ton=1000,
                balance_stars=50000,
                balance_points=100000,
                created_at=datetime.utcnow(),
            )
            
            db.add(root_user)
            await db.flush()
            
            print(f"✅ 创建根用户（KOL）: {root_user.username} (TG ID: {root_user.tg_id})")
            
            # 创建推荐关系树（3层，每层5个用户）
            print("\n📊 开始创建推荐关系树...")
            created_users = await create_referral_tree(
                db, depth=3, width=5, parent_tg_id=root_tg_id, level=0
            )
            
            # 更新根用户的邀请数
            root_user.invite_count = len(created_users)
            
            await db.commit()
            
            print(f"✅ 成功创建 {len(created_users)} 个测试用户")
            print(f"✅ 根用户邀请数: {root_user.invite_count}")
            
            # 打印树结构预览
            print("\n📋 推荐关系树预览:")
            print(f"  KOL: {root_user.username} (TG: {root_user.tg_id})")
            print(f"    └─ 一级推荐: {len([u for u in created_users if u['level'] == 0])} 人")
            print(f"      └─ 二级推荐: {len([u for u in created_users if u['level'] == 1])} 人")
            print(f"        └─ 三级推荐: {len([u for u in created_users if u['level'] == 2])} 人")
            
            print("\n" + "=" * 60)
            print("✅ 测试数据生成完成！")
            print("=" * 60)
            print(f"\n💡 提示: 在后台管理面板的'邀请管理'页面中，")
            print(f"   可以查看用户 {root_user.tg_id} 的推荐关系树。")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 部署检查清单

### Phase 1 检查清单
- [ ] Nginx 配置文件已更新
- [ ] SSL 证书已配置（certbot）
- [ ] Nginx 配置测试通过 (`nginx -t`)
- [ ] Nginx 已重新加载 (`systemctl reload nginx`)
- [ ] 访问 `https://admin.usdt2026.cc` 显示后台登录页
- [ ] API 代理正常工作 (`/api/v1/admin/auth/login`)

### Phase 2 检查清单
- [ ] 红包退款功能已更新（使用 LedgerService）
- [ ] 交易管理UI已更新（显示 Real vs Bonus 余额）
- [ ] 后端API已更新（返回余额分类）
- [ ] 测试红包退款功能
- [ ] 测试交易列表显示余额分类

### Phase 3 检查清单
- [ ] 推荐系统配置API已实现
- [ ] 推荐系统配置前端表单已添加
- [ ] 红包雨调度API已实现
- [ ] 红包雨调度前端表单已添加
- [ ] 数据库迁移已执行（ScheduledRedPacketRain 表）
- [ ] 测试数据脚本已运行
- [ ] 推荐关系树可视化正常

---

## 数据库迁移

如果需要创建新表，请运行以下 Alembic 迁移：

```bash
# 创建迁移文件
alembic revision --autogenerate -m "add_scheduled_redpacket_rain_table"

# 执行迁移
alembic upgrade head
```

---

## 注意事项

1. **Redis 配置**: 红包雨调度器需要 Redis 支持，确保 Redis 服务正常运行
2. **时区问题**: 所有时间字段使用 UTC，前端显示时需要转换为用户时区
3. **权限控制**: 所有管理后台API都需要管理员认证
4. **日志记录**: 所有关键操作（退款、调度等）都需要记录日志
5. **错误处理**: 所有API都需要完善的错误处理和验证

---

## 后续优化建议

1. **红包雨执行器**: 实现后台任务（Celery/APScheduler）来执行调度的红包雨
2. **推荐佣金自动计算**: 实现自动计算和发放推荐佣金的后台任务
3. **实时监控**: 添加 WebSocket 推送，实时更新推荐关系树和红包雨状态
4. **批量操作**: 支持批量退款、批量调度等功能
5. **数据分析**: 添加推荐效果分析、红包雨效果分析等报表

---

**文档版本**: v1.0  
**最后更新**: 2025-01-XX  
**维护者**: Lead Full-Stack Architect

