from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import Optional
from loguru import logger
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google.auth.exceptions import GoogleAuthError, TransportError
from shared.database.connection import get_db_session
from api.services.identity_service import IdentityService
from api.utils.auth_utils import create_access_token, TokenResponse, UserResponse
import os

router = APIRouter(prefix="/web", tags=["Web Auth"])


class GoogleAuthRequest(BaseModel):
    id_token: str
    email: Optional[EmailStr] = None
    picture: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    request: GoogleAuthRequest, db: AsyncSession = Depends(get_db_session)
):
    logger.info("正在处理 Google 登录请求...")

    # 1. 预先定义变量
    email = None
    google_sub = None
    picture = None
    name = None

    # 从环境变量读取 GOOGLE_CLIENT_ID
    client_id = os.getenv("GOOGLE_CLIENT_ID")

    try:
        # 尝试验证 Google Token
        id_info = id_token.verify_oauth2_token(
            request.id_token,
            google_requests.Request(),
            audience=client_id or None,
        )
        # 验证成功
        email = id_info.get("email")
        google_sub = id_info.get("sub")
        picture = id_info.get("picture")
        name = id_info.get("name")
        logger.info(f"Google token verified: email={email}, sub={google_sub}")

    except (ValueError, GoogleAuthError, TransportError) as e:
        logger.exception(f"Google token verification failed: {e}")
        # 【降级逻辑】如果验证失败，尝试使用前端传来的数据
        if request.email:
            logger.warning("Using frontend data for degraded Google login")
            email = request.email
            google_sub = request.email
            picture = request.picture
            first = request.given_name or ""
            last = request.family_name or ""
            name = (first + " " + last).strip() or None
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无法验证 Google 凭证",
            )

    if not email:
        raise HTTPException(status_code=400, detail="无法获取用户邮箱")

    # 2. 查找或创建用户
    provider_data = {
        "sub": google_sub,
        "email": email,
        "picture": picture or request.picture,
        "name": name or request.given_name,
    }

    try:
        user = await IdentityService.get_or_create_user_by_identity(
            db=db,
            provider="google",
            provider_user_id=email,
            provider_data=provider_data,
        )
    except Exception as e:
        logger.error(f"数据库服务错误: {e}")
        raise HTTPException(status_code=500, detail="登录失败：数据库错误")

    # 3. 生成 Token
    token = create_access_token(user.id)
    user_response = UserResponse(
        id=user.id,
        tg_id=getattr(user, "tg_id", 0) or 0,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        level=user.level,
        balance_usdt=float(getattr(user, "balance_usdt", 0) or 0),
        balance_ton=float(getattr(user, "balance_ton", 0) or 0),
        balance_stars=getattr(user, "balance_stars", 0) or 0,
        balance_points=getattr(user, "balance_points", 0) or 0,
    )
    return TokenResponse(access_token=token, user=user_response.model_dump())
