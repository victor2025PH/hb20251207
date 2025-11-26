"""
Lucky Red - 認證路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import hashlib
import hmac
from datetime import datetime, timedelta
from jose import jwt
from loguru import logger

from shared.config.settings import get_settings
from shared.database.connection import get_db_session
from shared.database.models import User

router = APIRouter()
settings = get_settings()


class TelegramAuthData(BaseModel):
    """Telegram 認證數據"""
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class TokenResponse(BaseModel):
    """Token 響應"""
    access_token: str
    token_type: str = "bearer"
    user: dict


def verify_telegram_auth(data: dict, bot_token: str) -> bool:
    """驗證 Telegram 登錄數據"""
    check_hash = data.pop("hash", None)
    if not check_hash:
        return False
    
    # 構建數據字符串
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items()) if v is not None
    )
    
    # 計算密鑰
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    
    # 計算 HMAC
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return calculated_hash == check_hash


def create_access_token(user_id: int) -> str:
    """創建 JWT Token"""
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


@router.post("/telegram", response_model=TokenResponse)
async def telegram_auth(
    auth_data: TelegramAuthData,
    db: AsyncSession = Depends(get_db_session)
):
    """Telegram 登錄/註冊"""
    
    # 驗證數據
    data_dict = auth_data.model_dump()
    if not verify_telegram_auth(data_dict.copy(), settings.BOT_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication data"
        )
    
    # 檢查時間 (5 分鐘內有效)
    if datetime.utcnow().timestamp() - auth_data.auth_date > 300:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication expired"
        )
    
    # 查找或創建用戶
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.tg_id == auth_data.id))
    user = result.scalar_one_or_none()
    
    if not user:
        # 創建新用戶
        user = User(
            tg_id=auth_data.id,
            username=auth_data.username,
            first_name=auth_data.first_name,
            last_name=auth_data.last_name,
        )
        db.add(user)
        await db.flush()
        logger.info(f"New user registered: {auth_data.id}")
    else:
        # 更新用戶信息
        user.username = auth_data.username
        user.first_name = auth_data.first_name
        user.last_name = auth_data.last_name
        user.updated_at = datetime.utcnow()
    
    await db.commit()
    
    # 生成 Token
    token = create_access_token(user.id)
    
    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "tg_id": user.tg_id,
            "username": user.username,
            "first_name": user.first_name,
            "level": user.level,
        }
    )


@router.get("/me")
async def get_current_user():
    """獲取當前用戶信息 (需要實現 JWT 驗證中間件)"""
    # TODO: 實現 JWT 驗證
    pass

