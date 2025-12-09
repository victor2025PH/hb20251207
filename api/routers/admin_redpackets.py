"""
红包管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timedelta
from decimal import Decimal

from shared.database.connection import get_db_session
from shared.database.models import RedPacket, RedPacketClaim, User, RedPacketStatus, RedPacketType, CurrencyType, Transaction, ScheduledRedPacketRain
from api.utils.auth import get_current_admin
from api.services.cache_service import get_cache_service
from pydantic import BaseModel, Field
from loguru import logger

router = APIRouter(prefix="/api/v1/admin/redpackets", tags=["管理后台-红包管理"])


# Pydantic 模型
class RedPacketListItem(BaseModel):
    id: int
    uuid: str
    sender_id: int
    sender_tg_id: Optional[int] = None
    sender_username: Optional[str] = None
    sender_name: Optional[str] = None
    chat_id: Optional[int] = None
    chat_title: Optional[str] = None
    currency: str
    packet_type: str
    total_amount: Decimal
    total_count: int
    claimed_amount: Decimal
    claimed_count: int
    status: str
    message: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RedPacketDetail(RedPacketListItem):
    claims: List[dict] = []


class RedPacketClaimItem(BaseModel):
    id: int
    user_id: int
    user_tg_id: Optional[int] = None
    user_username: Optional[str] = None
    user_name: Optional[str] = None
    amount: Decimal
    is_luckiest: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RedPacketStats(BaseModel):
    total_count: int
    total_amount: Decimal
    claimed_amount: Decimal
    average_amount: Decimal
    claim_rate: float
    active_count: int
    completed_count: int
    expired_count: int
    refunded_count: int


@router.get("/list", response_model=dict)
async def list_redpackets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    packet_type: Optional[str] = Query(None),
    sender_id: Optional[int] = Query(None),
    chat_id: Optional[int] = Query(None),
    uuid: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_amount: Optional[Decimal] = Query(None),
    max_amount: Optional[Decimal] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
    """获取红包列表（带缓存和预加载优化）"""
    # 生成缓存键
    cache = get_cache_service()
    cache_key = cache._make_key(
        "admin:redpackets:list",
        page=page,
        page_size=page_size,
        status=status,
        currency=currency,
        packet_type=packet_type,
        sender_id=sender_id,
        chat_id=chat_id,
        uuid=uuid,
        start_date=str(start_date) if start_date else None,
        end_date=str(end_date) if end_date else None,
        min_amount=str(min_amount) if min_amount else None,
        max_amount=str(max_amount) if max_amount else None
    )
    
    # 尝试从缓存获取
    cached_result = await cache.get(cache_key)
    if cached_result is not None:
        logger.debug(f"红包列表缓存命中: {cache_key}")
        return cached_result
    
    # 使用 selectinload 预加载关联数据，避免 N+1 查询
    query = select(RedPacket).options(selectinload(RedPacket.sender))
    
    # 構建篩選條件（排除已軟刪除的）
    conditions = [RedPacket.deleted_at.is_(None)]
    
    if status:
        try:
            status_enum = RedPacketStatus(status)
            conditions.append(RedPacket.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的状态: {status}")
    
    if currency:
        try:
            currency_enum = CurrencyType(currency)
            conditions.append(RedPacket.currency == currency_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的币种: {currency}")
    
    if packet_type:
        try:
            type_enum = RedPacketType(packet_type)
            conditions.append(RedPacket.packet_type == type_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的红包类型: {packet_type}")
    
    if sender_id:
        conditions.append(RedPacket.sender_id == sender_id)
    
    if chat_id:
        conditions.append(RedPacket.chat_id == chat_id)
    
    if uuid:
        conditions.append(RedPacket.uuid.contains(uuid))
    
    if start_date:
        conditions.append(RedPacket.created_at >= start_date)
    
    if end_date:
        conditions.append(RedPacket.created_at <= end_date)
    
    if min_amount:
        conditions.append(RedPacket.total_amount >= min_amount)
    
    if max_amount:
        conditions.append(RedPacket.total_amount <= max_amount)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # 获取总数
    count_query = select(func.count()).select_from(RedPacket)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total = await db.scalar(count_query)
    
    # 分页查询
    query = query.order_by(RedPacket.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    redpackets = result.scalars().all()
    
    # 构建响应数据
    items = []
    for rp in redpackets:
        sender = rp.sender
        items.append(RedPacketListItem(
            id=rp.id,
            uuid=rp.uuid,
            sender_id=rp.sender_id,
            sender_tg_id=sender.tg_id if sender else None,
            sender_username=sender.username if sender else None,
            sender_name=f"{sender.first_name or ''} {sender.last_name or ''}".strip() if sender else None,
            chat_id=rp.chat_id,
            chat_title=rp.chat_title,
            currency=rp.currency.value,
            packet_type=rp.packet_type.value,
            total_amount=rp.total_amount,
            total_count=rp.total_count,
            claimed_amount=rp.claimed_amount,
            claimed_count=rp.claimed_count,
            status=rp.status.value,
            message=rp.message,
            expires_at=rp.expires_at,
            created_at=rp.created_at,
            completed_at=rp.completed_at,
        ))
    
    result = {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }
    
    # 缓存结果（60秒，红包列表更新频率较低）
    await cache.set(cache_key, result, expire=60)
    logger.debug(f"红包列表缓存设置: {cache_key}")
    
    return result


@router.get("/{redpacket_id}", response_model=RedPacketDetail)
async def get_redpacket_detail(
    redpacket_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
    """获取红包详情"""
    query = select(RedPacket).options(
        selectinload(RedPacket.sender),
        selectinload(RedPacket.claims).selectinload(RedPacketClaim.user)
    ).where(RedPacket.id == redpacket_id)
    
    result = await db.execute(query)
    redpacket = result.scalar_one_or_none()
    
    if not redpacket:
        raise HTTPException(status_code=404, detail="红包不存在")
    
    sender = redpacket.sender
    claims = []
    for claim in redpacket.claims:
        user = claim.user
        claims.append({
            "id": claim.id,
            "user_id": claim.user_id,
            "user_tg_id": user.tg_id if user else None,
            "user_username": user.username if user else None,
            "user_name": f"{user.first_name or ''} {user.last_name or ''}".strip() if user else None,
            "amount": float(claim.amount),
            "is_luckiest": claim.is_luckiest,
            "created_at": claim.claimed_at.isoformat() if hasattr(claim, 'claimed_at') and claim.claimed_at else None,
        })
    
    return RedPacketDetail(
        id=redpacket.id,
        uuid=redpacket.uuid,
        sender_id=redpacket.sender_id,
        sender_tg_id=sender.tg_id if sender else None,
        sender_username=sender.username if sender else None,
        sender_name=f"{sender.first_name or ''} {sender.last_name or ''}".strip() if sender else None,
        chat_id=redpacket.chat_id,
        chat_title=redpacket.chat_title,
        currency=redpacket.currency.value,
        packet_type=redpacket.packet_type.value,
        total_amount=redpacket.total_amount,
        total_count=redpacket.total_count,
        claimed_amount=redpacket.claimed_amount,
        claimed_count=redpacket.claimed_count,
        status=redpacket.status.value,
        message=redpacket.message,
        expires_at=redpacket.expires_at,
        created_at=redpacket.created_at,
        completed_at=redpacket.completed_at,
        claims=claims,
    )


@router.post("/{redpacket_id}/refund")
async def refund_redpacket(
    redpacket_id: int,
    reason: Optional[str] = Query(None, description="退款原因"),
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
    """手动退款红包（使用 LedgerService）"""
    # 清除红包列表缓存
    cache = get_cache_service()
    await cache.delete_pattern("admin:redpackets:list:*")
    
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
    # 如果紅包已被領取，只退還剩餘金額；如果未被領取，退還全部金額
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


@router.post("/{redpacket_id}/extend")
async def extend_redpacket(
    redpacket_id: int,
    hours: int = Query(24, ge=1, le=720),
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
    # 清除红包列表缓存
    cache = get_cache_service()
    await cache.delete_pattern("admin:redpackets:list:*")
    """延长红包过期时间"""
    query = select(RedPacket).where(RedPacket.id == redpacket_id)
    result = await db.execute(query)
    redpacket = result.scalar_one_or_none()
    
    if not redpacket:
        raise HTTPException(status_code=404, detail="红包不存在")
    
    if redpacket.status != RedPacketStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="只能延长进行中的红包")
    
    if redpacket.expires_at:
        redpacket.expires_at = redpacket.expires_at + timedelta(hours=hours)
    else:
        redpacket.expires_at = datetime.utcnow() + timedelta(hours=hours)
    
    await db.commit()
    await db.refresh(redpacket)
    
    return {"success": True, "message": f"已延长 {hours} 小时", "new_expires_at": redpacket.expires_at}


@router.post("/{redpacket_id}/complete")
async def complete_redpacket(
    redpacket_id: int,
    refund_remaining: bool = Query(True, description="是否退還剩餘金額"),
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
    # 清除红包列表缓存
    cache = get_cache_service()
    await cache.delete_pattern("admin:redpackets:list:*")
    """強制完成紅包"""
    query = select(RedPacket).where(RedPacket.id == redpacket_id)
    result = await db.execute(query)
    redpacket = result.scalar_one_or_none()
    
    if not redpacket:
        raise HTTPException(status_code=404, detail="紅包不存在")
    
    if redpacket.status != RedPacketStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="只能完成進行中的紅包")
    
    redpacket.status = RedPacketStatus.COMPLETED
    redpacket.completed_at = datetime.utcnow()
    
    # 如果未領取完且需要退還，退還剩餘金額給發送者
    remaining_amount = redpacket.total_amount - redpacket.claimed_amount
    refunded = False
    
    if refund_remaining and remaining_amount > 0:
        # 查找發送者
        sender_result = await db.execute(select(User).where(User.id == redpacket.sender_id))
        sender = sender_result.scalar_one_or_none()
        
        if sender:
            balance_field = f"balance_{redpacket.currency.value}"
            current_balance = getattr(sender, balance_field, 0) or Decimal(0)
            new_balance = current_balance + remaining_amount
            setattr(sender, balance_field, new_balance)
            
            # 創建退款交易記錄
            refund_transaction = Transaction(
                user_id=sender.id,
                type="refund",
                currency=redpacket.currency,
                amount=remaining_amount,
                balance_before=current_balance,
                balance_after=new_balance,
                ref_id=f"redpacket_{redpacket.id}",
                note=f"紅包強制完成退款: 紅包ID {redpacket.id}, 退還剩餘金額 {remaining_amount} {redpacket.currency.value.upper()}",
                status="completed"
            )
            db.add(refund_transaction)
            refunded = True
            
            logger.info(
                f"Red packet completed with refund: redpacket_id={redpacket_id}, "
                f"sender_id={sender.id}, refund_amount={remaining_amount}, "
                f"currency={redpacket.currency.value}, admin_id={current_admin.get('id')}"
            )
    
    await db.commit()
    await db.refresh(redpacket)
    
    return {
        "success": True,
        "message": "紅包已強制完成",
        "refunded": refunded,
        "refunded_amount": float(remaining_amount) if refunded else 0,
        "currency": redpacket.currency.value if refunded else None
    }


@router.delete("/{redpacket_id}")
async def delete_redpacket(
    redpacket_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
    # 清除红包列表缓存
    cache = get_cache_service()
    await cache.delete_pattern("admin:redpackets:list:*")
    """刪除紅包（軟刪除）"""
    query = select(RedPacket).where(RedPacket.id == redpacket_id)
    result = await db.execute(query)
    redpacket = result.scalar_one_or_none()
    
    if not redpacket:
        raise HTTPException(status_code=404, detail="紅包不存在")
    
    if redpacket.deleted_at:
        raise HTTPException(status_code=400, detail="紅包已被刪除")
    
    # 軟刪除：標記刪除時間
    redpacket.deleted_at = datetime.utcnow()
    
    logger.info(
        f"Red packet soft deleted: redpacket_id={redpacket_id}, "
        f"admin_id={current_admin.get('id')}"
    )
    
    await db.commit()
    await db.refresh(redpacket)
    
    return {"success": True, "message": "紅包已刪除", "deleted_at": redpacket.deleted_at}


@router.get("/stats/overview", response_model=RedPacketStats)
async def get_redpacket_stats(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
    """获取红包统计概览"""
    query = select(RedPacket)
    
    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(RedPacket.created_at >= start_date)
        if end_date:
            conditions.append(RedPacket.created_at <= end_date)
        query = query.where(and_(*conditions))
    
    result = await db.execute(query)
    redpackets = result.scalars().all()
    
    total_count = len(redpackets)
    total_amount = sum(float(rp.total_amount) for rp in redpackets)
    claimed_amount = sum(float(rp.claimed_amount) for rp in redpackets)
    average_amount = total_amount / total_count if total_count > 0 else 0
    claim_rate = (claimed_amount / total_amount * 100) if total_amount > 0 else 0
    
    active_count = sum(1 for rp in redpackets if rp.status == RedPacketStatus.ACTIVE)
    completed_count = sum(1 for rp in redpackets if rp.status == RedPacketStatus.COMPLETED)
    expired_count = sum(1 for rp in redpackets if rp.status == RedPacketStatus.EXPIRED)
    refunded_count = sum(1 for rp in redpackets if rp.status == RedPacketStatus.REFUNDED)
    
    return RedPacketStats(
        total_count=total_count,
        total_amount=Decimal(str(total_amount)),
        claimed_amount=Decimal(str(claimed_amount)),
        average_amount=Decimal(str(average_amount)),
        claim_rate=round(claim_rate, 2),
        active_count=active_count,
        completed_count=completed_count,
        expired_count=expired_count,
        refunded_count=refunded_count,
    )


@router.get("/stats/trend")
async def get_redpacket_trend(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
    """获取红包趋势数据"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # 按日期分组统计
    query = select(
        func.date(RedPacket.created_at).label('date'),
        func.count(RedPacket.id).label('count'),
        func.sum(RedPacket.total_amount).label('total_amount'),
        func.sum(RedPacket.claimed_amount).label('claimed_amount'),
    ).where(
        RedPacket.created_at >= start_date,
        RedPacket.created_at <= end_date,
    ).group_by(
        func.date(RedPacket.created_at)
    ).order_by(
        func.date(RedPacket.created_at)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    dates = []
    counts = []
    amounts = []
    claimed_amounts = []
    
    for row in rows:
        dates.append(row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date))
        counts.append(row.count)
        amounts.append(float(row.total_amount) if row.total_amount else 0)
        claimed_amounts.append(float(row.claimed_amount) if row.claimed_amount else 0)
    
    return {
        "dates": dates,
        "counts": counts,
        "amounts": amounts,
        "claimed_amounts": claimed_amounts,
    }


# 红包雨调度
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

    class Config:
        from_attributes = True


@router.post("/schedule-rain", response_model=ScheduleRainResponse)
async def schedule_rain(
    request: ScheduleRainRequest,
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
    """调度红包雨"""
    import json
    
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
            host=getattr(settings, 'REDIS_HOST', 'localhost'),
            port=getattr(settings, 'REDIS_PORT', 6379),
            db=getattr(settings, 'REDIS_DB', 0),
            decode_responses=True
        )
        
        # 计算延迟时间（秒）
        delay_seconds = int((request.start_time - datetime.utcnow()).total_seconds())
        
        # 使用 Redis 的延迟队列
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

