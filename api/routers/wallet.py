"""
Lucky Red - 錢包路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from shared.database.connection import get_db_session
from shared.database.models import User, Transaction, CurrencyType

router = APIRouter()


class BalanceResponse(BaseModel):
    """餘額響應"""
    usdt: float
    ton: float
    stars: int
    points: int
    total_usdt: float  # 折算成 USDT 的總值


class TransactionResponse(BaseModel):
    """交易記錄響應"""
    id: int
    type: str
    currency: str
    amount: float
    note: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DepositRequest(BaseModel):
    """充值請求"""
    currency: CurrencyType
    amount: float = Field(..., gt=0)
    tx_hash: Optional[str] = None


class WithdrawRequest(BaseModel):
    """提現請求"""
    currency: CurrencyType
    amount: float = Field(..., gt=0)
    address: str


@router.get("/balance/{tg_id}", response_model=BalanceResponse)
async def get_balance(
    tg_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """獲取餘額"""
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    usdt = float(user.balance_usdt or 0)
    ton = float(user.balance_ton or 0)
    stars = user.balance_stars or 0
    points = user.balance_points or 0
    
    # 簡單折算 (實際應該使用匯率 API)
    total_usdt = usdt + ton * 5.0 + stars * 0.01 + points * 0.001
    
    return BalanceResponse(
        usdt=usdt,
        ton=ton,
        stars=stars,
        points=points,
        total_usdt=round(total_usdt, 2),
    )


@router.get("/transactions/{tg_id}", response_model=List[TransactionResponse])
async def get_transactions(
    tg_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session)
):
    """獲取交易記錄"""
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
    )
    transactions = result.scalars().all()
    
    return transactions


@router.post("/deposit")
async def deposit(
    request: DepositRequest,
    tg_id: int,  # TODO: 從 JWT 獲取
    db: AsyncSession = Depends(get_db_session)
):
    """充值 (需要管理員審核)"""
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # TODO: 實現充值邏輯
    # 這裡應該創建一個待審核的充值訂單
    
    return {"message": "Deposit request submitted", "status": "pending"}


@router.post("/withdraw")
async def withdraw(
    request: WithdrawRequest,
    tg_id: int,  # TODO: 從 JWT 獲取
    db: AsyncSession = Depends(get_db_session)
):
    """提現"""
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 檢查餘額
    balance_field = f"balance_{request.currency.value}"
    current_balance = getattr(user, balance_field, 0) or Decimal(0)
    
    if current_balance < Decimal(str(request.amount)):
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # TODO: 實現提現邏輯
    # 這裡應該創建一個待處理的提現訂單
    
    return {"message": "Withdraw request submitted", "status": "pending"}

