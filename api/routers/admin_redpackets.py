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
from shared.database.models import RedPacket, RedPacketClaim, User, RedPacketStatus, RedPacketType, CurrencyType, Transaction
from api.utils.auth import get_current_admin
from pydantic import BaseModel
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
    """获取红包列表"""
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
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


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
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
    """手动退款红包"""
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
    
    balance_field = f"balance_{redpacket.currency.value}"
    current_balance = getattr(sender, balance_field, 0) or Decimal(0)
    
    # 計算需要退還的金額
    # 如果紅包已被領取，只退還剩餘金額；如果未被領取，退還全部金額
    remaining_amount = redpacket.total_amount - redpacket.claimed_amount
    
    if remaining_amount > 0:
        # 退還剩餘金額給發送者
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
            note=f"紅包退款: 紅包ID {redpacket.id}, 退還金額 {remaining_amount} {redpacket.currency.value.upper()}",
            status="completed"
        )
        db.add(refund_transaction)
        
        logger.info(
            f"Red packet refunded: redpacket_id={redpacket_id}, sender_id={sender.id}, "
            f"amount={remaining_amount}, currency={redpacket.currency.value}, "
            f"admin_id={current_admin.get('id')}"
        )
    
    # 更新紅包狀態
    redpacket.status = RedPacketStatus.REFUNDED
    
    await db.commit()
    await db.refresh(redpacket)
    
    return {
        "success": True,
        "message": "退款成功",
        "refunded_amount": float(remaining_amount),
        "currency": redpacket.currency.value
    }


@router.post("/{redpacket_id}/extend")
async def extend_redpacket(
    redpacket_id: int,
    hours: int = Query(24, ge=1, le=720),
    db: AsyncSession = Depends(get_db_session),
    current_admin: dict = Depends(get_current_admin),
):
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

