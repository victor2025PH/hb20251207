"""
Lucky Red - 用戶路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from pydantic import BaseModel
from typing import Optional, List
from loguru import logger

from shared.database.connection import get_db_session
from shared.database.models import User
from api.utils.telegram_auth import get_tg_id_from_header
from api.routers.auth import get_current_user_from_token

router = APIRouter()


class UserProfile(BaseModel):
    """用戶資料"""
    id: int
    tg_id: Optional[int]  # 允许为 None（非 Telegram 用户）
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


@router.get("/me")
async def get_my_profile(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_from_token)
):
    """獲取當前用戶資料（從 JWT Token 或 Telegram initData 中獲取）
    
    返回完整的用戶信息，包括餘額等，用於前端認證狀態管理
    """
    try:
        from api.utils.auth_utils import UserResponse
        
        # 返回完整的 UserResponse 結構，與 /api/auth/me 保持一致
        return UserResponse(
            id=current_user.id,
            tg_id=current_user.tg_id or 0,  # 非 Telegram 用户时为 0
            username=current_user.username,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            level=current_user.level or 1,
            balance_usdt=float(current_user.balance_usdt or 0),
            balance_ton=float(current_user.balance_ton or 0),
            balance_stars=current_user.balance_stars or 0,
            balance_points=current_user.balance_points or 0,
        )
    except Exception as e:
        logger.error(f"获取用户资料失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user profile: {str(e)}"
        )


@router.get("/me/balance", response_model=UserBalance)
async def get_my_balance(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_from_token)
):
    """獲取當前用戶餘額（從 JWT Token 或 Telegram initData 中獲取）
    
    使用 LedgerService 獲取餘額，確保與發送紅包時的餘額檢查一致
    """
    # 優先使用 LedgerService 獲取餘額（與發送紅包時的檢查一致）
    try:
        from api.services.ledger_service import LedgerService
        from decimal import Decimal
        
        usdt = float(await LedgerService.get_balance(db, current_user.id, 'USDT') or Decimal('0'))
        ton = float(await LedgerService.get_balance(db, current_user.id, 'TON') or Decimal('0'))
        stars = int(await LedgerService.get_balance(db, current_user.id, 'STARS') or Decimal('0'))
        points = int(await LedgerService.get_balance(db, current_user.id, 'POINTS') or Decimal('0'))
    except Exception as e:
        # 如果 LedgerService 不可用，回退到 User 表餘額
        logger.warning(f"Failed to get balance from LedgerService, falling back to User table: {e}")
        usdt = float(current_user.balance_usdt or 0)
        ton = float(current_user.balance_ton or 0)
        stars = current_user.balance_stars or 0
        points = current_user.balance_points or 0
    
    return UserBalance(
        usdt=usdt,
        ton=ton,
        stars=stars,
        points=points,
    )


@router.get("/me/referral/stats")
async def get_referral_stats(
    tg_id: Optional[int] = Depends(get_tg_id_from_header),
    db: AsyncSession = Depends(get_db_session)
):
    """
    获取推荐统计（Tier 1 & Tier 2）
    """
    if not tg_id:
        raise HTTPException(status_code=401, detail="Telegram user ID is required")
    
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from api.services.referral_service import ReferralService
    stats = await ReferralService.get_referral_stats(db, user.id)
    
    return stats


@router.get("/me/referral/tree")
async def get_referral_tree(
    tg_id: Optional[int] = Depends(get_tg_id_from_header),
    db: AsyncSession = Depends(get_db_session),
    max_depth: int = Query(2, ge=1, le=3)
):
    """
    获取推荐树
    """
    if not tg_id:
        raise HTTPException(status_code=401, detail="Telegram user ID is required")
    
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from api.services.referral_service import ReferralService
    tree = await ReferralService.get_referral_tree(db, user.id, max_depth=max_depth)
    
    return tree


@router.get("/me/invite")
async def get_my_invite_stats(
    tg_id: Optional[int] = Depends(get_tg_id_from_header),
    db: AsyncSession = Depends(get_db_session)
):
    """
    获取当前用户的邀请统计信息
    包括邀请码、邀请链接、邀请人数、收益等
    """
    if not tg_id:
        raise HTTPException(status_code=401, detail="Telegram user ID is required")
    
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 生成邀请码（如果还没有）
    if not user.invite_code:
        import secrets
        user.invite_code = secrets.token_urlsafe(8)
        await db.commit()
        await db.refresh(user)
    
    # 生成邀请链接
    from shared.config.settings import get_settings
    settings = get_settings()
    invite_link = f"https://t.me/{settings.BOT_USERNAME}?start={user.invite_code}"
    
    # 获取被邀请人列表
    invitees_result = await db.execute(
        select(User).where(User.invited_by == tg_id).order_by(User.created_at.desc())
    )
    invitees = invitees_result.scalars().all()
    
    # 计算下一个里程碑
    invite_milestones = [
        {"target": 5, "reward": 5},
        {"target": 10, "reward": 15},
        {"target": 25, "reward": 50},
        {"target": 50, "reward": 150},
        {"target": 100, "reward": 500},
    ]
    
    invite_count = user.invite_count or 0
    next_milestone = None
    next_milestone_reward = None
    progress_to_next = 0
    
    for milestone in invite_milestones:
        if invite_count < milestone["target"]:
            next_milestone = milestone["target"]
            next_milestone_reward = milestone["reward"]
            progress_to_next = invite_count
            break
    
    # 构建被邀请人列表
    invitees_list = [
        {
            "tg_id": invitee.tg_id or 0,
            "username": invitee.username,
            "first_name": invitee.first_name,
            "joined_at": invitee.created_at.isoformat() if invitee.created_at else None,
        }
        for invitee in invitees
    ]
    
    return {
        "invite_code": user.invite_code,
        "invite_count": invite_count,
        "invite_earnings": float(user.invite_earnings or 0),
        "invite_link": invite_link,
        "next_milestone": next_milestone,
        "next_milestone_reward": next_milestone_reward,
        "progress_to_next": progress_to_next,
        "invitees": invitees_list,
    }


# 管理后台用户列表API
@router.get("/list")
async def list_users(
    search: Optional[str] = Query(None, description="搜索关键词（用户名、Telegram ID）"),
    level: Optional[int] = Query(None, description="等级筛选"),
    is_banned: Optional[bool] = Query(None, description="封禁状态筛选"),
    min_balance_usdt: Optional[float] = Query(None, description="最小USDT余额"),
    max_balance_usdt: Optional[float] = Query(None, description="最大USDT余额"),
    created_from: Optional[str] = Query(None, description="注册开始时间（ISO格式）"),
    created_to: Optional[str] = Query(None, description="注册结束时间（ISO格式）"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db_session)
):
    """获取用户列表（管理后台，支持高级筛选）"""
    query = select(User)
    
    # 搜索功能
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                User.username.ilike(search_term),
                User.first_name.ilike(search_term),
                User.tg_id.cast(str).ilike(search_term)
            )
        )
    
    # 高级筛选
    if level is not None:
        query = query.where(User.level == level)
    
    if is_banned is not None:
        query = query.where(User.is_banned == is_banned)
    
    if min_balance_usdt is not None:
        query = query.where(User.balance_usdt >= min_balance_usdt)
    
    if max_balance_usdt is not None:
        query = query.where(User.balance_usdt <= max_balance_usdt)
    
    if created_from:
        try:
            from_date = datetime.fromisoformat(created_from.replace('Z', '+00:00'))
            query = query.where(User.created_at >= from_date)
        except:
            pass
    
    if created_to:
        try:
            to_date = datetime.fromisoformat(created_to.replace('Z', '+00:00'))
            query = query.where(User.created_at <= to_date)
        except:
            pass
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # 获取用户列表
    query = query.order_by(User.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return {
        "success": True,
        "data": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "users": [
                {
                    "id": user.id,
                    "telegram_id": user.tg_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "balance_usdt": float(user.balance_usdt or 0),
                    "balance_ton": float(user.balance_ton or 0),
                    "balance_stars": user.balance_stars or 0,
                    "balance_points": user.balance_points or 0,
                    "level": user.level or 0,
                    "is_banned": user.is_banned or False,
                    "is_admin": user.is_admin or False,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                }
                for user in users
            ]
        }
    }


@router.get("/detail/{user_id}")
async def get_user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """获取用户详情（管理后台）"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "data": {
            "id": user.id,
            "telegram_id": user.tg_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "balance_usdt": float(user.balance_usdt or 0),
            "balance_ton": float(user.balance_ton or 0),
            "balance_stars": user.balance_stars or 0,
            "balance_points": user.balance_points or 0,
            "level": user.level or 0,
            "is_banned": user.is_banned or False,
            "is_admin": user.is_admin or False,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
    }

