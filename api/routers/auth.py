"""
Lucky Red - 認證路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import hashlib
import hmac
from datetime import datetime, timedelta
from jose import jwt, JWTError
from loguru import logger

from shared.config.settings import get_settings
from shared.database.connection import get_db_session
from shared.database.models import User
from sqlalchemy import select
from api.utils.auth_utils import create_access_token, TokenResponse, UserResponse

router = APIRouter()
settings = get_settings()

# HTTP Bearer 認證（auto_error=False 允許可選認證，以便回退到 Telegram initData）
security = HTTPBearer(auto_error=False)


class TelegramAuthData(BaseModel):
    """Telegram 認證數據"""
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


# UserResponse 已移至 api.utils.auth_utils 以避免循环导入

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


# create_access_token 已移至 api.utils.auth_utils 以避免循环导入


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


async def get_current_user_from_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """從 JWT Token 或 Telegram initData 獲取當前用戶"""
    user = None
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 優先嘗試 JWT Token 認證
    if credentials:
        try:
            token = credentials.credentials
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id_str = payload.get("sub")
            if user_id_str is None:
                raise credentials_exception
            user_id: int = int(user_id_str)
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
        except (JWTError, ValueError, TypeError) as e:
            logger.warning(f"JWT 驗證失敗: {str(e)}")
            # 不立即拋出異常，允許回退到 Telegram 認證
            user = None

    # 如果沒有 JWT Token 或 JWT 認證失敗，嘗試使用 Telegram initData
    if not user and x_telegram_init_data:
        try:
            from api.utils.telegram_auth import parse_telegram_init_data
            from api.services.identity_service import IdentityService
            
            user_data = parse_telegram_init_data(x_telegram_init_data)
            
            if user_data and 'id' in user_data:
                tg_id = int(user_data['id'])
                
                # 查找或創建用戶
                user = await IdentityService.get_or_create_user_by_identity(
                    db=db,
                    provider='telegram',
                    provider_user_id=str(tg_id),
                    provider_data={
                        'id': tg_id,
                        'username': user_data.get('username'),
                        'first_name': user_data.get('first_name'),
                        'last_name': user_data.get('last_name'),
                        'language_code': user_data.get('language_code', 'zh-TW'),
                    }
                )
                # 如果是新创建的用户，可能需要刷新以获取所有字段
                await db.refresh(user)
                logger.info(f"Telegram 用戶認證成功: tg_id={tg_id}, user_id={user.id}")

        except Exception as e:
            logger.warning(f"Telegram initData 認證失敗: {e}", exc_info=True)
            user = None

    if not user:
        raise credentials_exception

    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is banned"
        )

    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db_session)
):
    """獲取當前用戶信息"""
    return UserResponse(
        id=current_user.id,
        tg_id=current_user.tg_id,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        level=current_user.level,
        balance_usdt=float(current_user.balance_usdt or 0),
        balance_ton=float(current_user.balance_ton or 0),
        balance_stars=current_user.balance_stars or 0,
        balance_points=current_user.balance_points or 0,
    )

