"""
Lucky Red - 認證路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
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
from api.utils.auth_strategy import (
    get_auth_strategy,
    should_allow_telegram_auth,
    should_allow_jwt_auth,
)

router = APIRouter()
settings = get_settings()

# HTTP Bearer 認證（auto_error=False 允許可選認證，以便回退到 Telegram initData）
security = HTTPBearer(auto_error=False)


def decode_jwt_token(token: str) -> int:
    """
    解碼 JWT Token 並返回用戶 ID

    Returns:
        int: 用戶 ID

    Raises:
        JWTError: 如果 Token 無效或過期
        ValueError: 如果 'sub' claim 不存在或格式錯誤
    """
    payload = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise ValueError("'sub' claim is missing in token payload")
    return int(user_id_str)


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
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    return calculated_hash == check_hash


# create_access_token 已移至 api.utils.auth_utils 以避免循环导入


@router.post("/telegram", response_model=TokenResponse)
async def telegram_auth(
    auth_data: TelegramAuthData, db: AsyncSession = Depends(get_db_session)
):
    """Telegram 登錄/註冊"""

    # 驗證數據
    data_dict = auth_data.model_dump()
    if not verify_telegram_auth(data_dict.copy(), settings.BOT_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication data",
        )

    # 檢查時間 (5 分鐘內有效)
    if datetime.utcnow().timestamp() - auth_data.auth_date > 300:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication expired"
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
        },
    )


async def get_current_user_from_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    從 JWT Token 或 Telegram initData 獲取當前用戶
    優先使用 Telegram initData，如果沒有則回退到 JWT Token
    """
    user = None
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    has_initData = bool(x_telegram_init_data) and should_allow_telegram_auth(request)
    has_jwt_token = credentials is not None and credentials.credentials

    # Step 1: 嘗試 Telegram 認證（如果有 initData）
    if has_initData:
        logger.debug(
            f"[Auth] Attempting Telegram authentication - initData length: {len(x_telegram_init_data)}"
        )
        logger.debug(
            f"[Auth] initData 預覽: {x_telegram_init_data[:100]}..."
        )
        try:
            from api.utils.telegram_auth import (
                parse_telegram_init_data,
                verify_telegram_init_data,
            )
            from api.services.identity_service import IdentityService

            logger.debug(
                f"[Auth] 開始處理 Telegram initData，長度: {len(x_telegram_init_data)}"
            )

            # 驗證 initData 的 hash（如果 BOT_TOKEN 配置了則驗證）
            # 如果 BOT_TOKEN 未配置，跳過驗證（僅用於開發環境）
            should_verify = bool(settings.BOT_TOKEN)
            logger.debug(
                f"[Auth] BOT_TOKEN 配置狀態: {should_verify}, BOT_TOKEN 長度: {len(settings.BOT_TOKEN) if settings.BOT_TOKEN else 0}"
            )

            hash_valid = True  # 默認值：如果不需要驗證，則認為有效
            if should_verify:
                hash_valid = verify_telegram_init_data(x_telegram_init_data)
                if not hash_valid:
                    logger.warning(
                        f"[Auth] Telegram initData hash 驗證失敗 - initData可能無效或已過期"
                    )
                    logger.warning(f"[Auth] initData 預覽: {x_telegram_init_data[:200]}...")
                    logger.warning(
                        f"[Auth] 請檢查：1. BOT_TOKEN 是否正確 2. initData 是否已過期 3. initData 是否被篡改"
                    )
                    user = None
                else:
                    logger.debug(f"[Auth] Telegram initData hash 驗證成功")
            else:
                logger.debug(f"[Auth] 跳過 initData hash 驗證（BOT_TOKEN 未配置）- 僅用於開發環境")

            # 只有在 hash 驗證通過（或跳過驗證）時才解析用戶數據
            if hash_valid:
                user_data = parse_telegram_init_data(x_telegram_init_data)
                logger.debug(f"[Auth] 解析後的用戶數據: {user_data}")

                if user_data and "id" in user_data:
                    tg_id = int(user_data["id"])
                    logger.debug(f"[Auth] 從 initData 中提取到 tg_id: {tg_id}")

                    try:
                        user = await IdentityService.get_or_create_user_by_identity(
                            db=db,
                            provider="telegram",
                            provider_user_id=str(tg_id),
                            provider_data={
                                "id": tg_id,
                                "username": user_data.get("username"),
                                "first_name": user_data.get("first_name"),
                                "last_name": user_data.get("last_name"),
                                "language_code": user_data.get(
                                    "language_code", "zh-TW"
                                ),
                            },
                        )
                        try:
                            await db.refresh(user)
                        except Exception as refresh_error:
                            logger.warning(
                                f"[Auth] 刷新用户数据失败（不影响使用）: {refresh_error}"
                            )

                        logger.info(
                            f"[Auth] Telegram 用戶認證成功: tg_id={tg_id}, user_id={user.id}, username={user.username}"
                        )
                    except Exception as identity_error:
                        logger.error(
                            f"[Auth] IdentityService 創建/獲取用戶失敗: {identity_error}",
                            exc_info=True,
                        )
                        user = None
                else:
                    logger.warning(
                        f"[Auth] Telegram initData 中沒有用戶信息 - user_data: {user_data}"
                    )
                    user = None
            else:
                logger.warning(
                    f"[Auth] 由於 hash 驗證失敗，跳過用戶數據解析"
                )
        except Exception as e:
            logger.error(f"[Auth] Telegram initData 認證失敗: {e}", exc_info=True)
            user = None

        # 如果 Telegram 認證失敗，嘗試降級到 JWT（如果有 JWT token）
        if not user and has_jwt_token:
            logger.info(
                "[Auth] Telegram authentication failed, falling back to JWT token auth"
            )
            try:
                token = credentials.credentials
                user_id = decode_jwt_token(token)
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()
                if user:
                    logger.info(f"[Auth] JWT 用戶認證成功: user_id={user_id}")
                else:
                    logger.warning(f"[Auth] JWT 用戶認證失敗: user_id={user_id} 不存在")
                    user = None
            except JWTError as e:
                logger.error(f"[Auth] JWT token validation failed: {e}")
                user = None
            except (ValueError, TypeError) as e:
                logger.error(f"[Auth] JWT decode error: {e}")
                user = None

    # Step 2: 如果沒有 Telegram initData，嘗試 JWT Token
    elif has_jwt_token:
        logger.info("[Auth] No Telegram initData, falling back to JWT token auth")
        try:
            token = credentials.credentials
            user_id = decode_jwt_token(token)
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                logger.info(f"[Auth] JWT 用戶認證成功: user_id={user_id}")
            else:
                logger.warning(f"[Auth] JWT 用戶認證失敗: user_id={user_id} 不存在")
                raise credentials_exception
        except JWTError as e:
            logger.error(f"[Auth] JWT token validation failed: {e}")
            raise credentials_exception
        except (ValueError, TypeError) as e:
            logger.error(f"[Auth] JWT decode error: {e}")
            raise credentials_exception

    # 如果兩種認證方式都失敗，拋出異常
    if not user:
        logger.error("[Auth] Both Telegram and JWT authentication failed")
        raise credentials_exception

    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is banned"
        )

    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user_from_token),
    db: AsyncSession = Depends(get_db_session),
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
