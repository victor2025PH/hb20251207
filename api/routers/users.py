"""
Lucky Red - 用戶路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from shared.database.connection import get_db_session
from shared.database.models import User

router = APIRouter()


class UserProfile(BaseModel):
    """用戶資料"""
    id: int
    tg_id: int
    username: Optional[str]
    first_name: Optional[str]
    level: int
    xp: int
    invite_code: Optional[str]
    invite_count: int
    
    class Config:
        from_attributes = True


class UserBalance(BaseModel):
    """用戶餘額"""
    usdt: float
    ton: float
    stars: int
    points: int


@router.get("/profile/{tg_id}", response_model=UserProfile)
async def get_user_profile(
    tg_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """獲取用戶資料"""
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.get("/balance/{tg_id}", response_model=UserBalance)
async def get_user_balance(
    tg_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """獲取用戶餘額"""
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserBalance(
        usdt=float(user.balance_usdt or 0),
        ton=float(user.balance_ton or 0),
        stars=user.balance_stars or 0,
        points=user.balance_points or 0,
    )

