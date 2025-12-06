"""
认证工具函数
用于避免循环导入
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from shared.config.settings import get_settings
from pydantic import BaseModel

settings = get_settings()


def create_access_token(user_id: int) -> str:
    """創建 JWT Token"""
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


class TokenResponse(BaseModel):
    """Token 響應"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """用戶響應"""
    id: int
    tg_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    level: int
    balance_usdt: float
    balance_ton: float
    balance_stars: int
    balance_points: int
    
    class Config:
        from_attributes = True

