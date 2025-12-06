"""
Universal Identity Service - 多平台身份认证服务
支持 Telegram, Google, Wallet 等多种身份提供者
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta
import uuid as uuid_lib
import secrets
from loguru import logger

from shared.database.models import User, UserIdentity, AccountLink
from shared.config.settings import get_settings

settings = get_settings()


class IdentityService:
    """统一身份认证服务"""
    
    @staticmethod
    async def get_or_create_user_by_identity(
        db: AsyncSession,
        provider: str,
        provider_user_id: str,
        provider_data: Optional[Dict[str, Any]] = None,
        auto_link: bool = True
    ) -> User:
        """
        通过身份提供者获取或创建用户
        
        Args:
            db: 数据库会话
            provider: 身份提供者 ('telegram', 'google', 'wallet', 'email')
            provider_user_id: 提供者的用户ID
            provider_data: 提供者的额外数据
            auto_link: 是否自动链接到现有账户
        
        Returns:
            User对象
        """
        # 查找现有身份
        result = await db.execute(
            select(UserIdentity).where(
                and_(
                    UserIdentity.provider == provider,
                    UserIdentity.provider_user_id == str(provider_user_id)
                )
            )
        )
        identity = result.scalar_one_or_none()
        
        if identity:
            # 身份存在，返回关联的用户
            result = await db.execute(select(User).where(User.id == identity.user_id))
            user = result.scalar_one()
            
            # 更新身份数据
            if provider_data:
                identity.provider_data = provider_data
                identity.verified_at = datetime.utcnow()
                await db.commit()
            
            logger.info(f"Found existing identity: {provider}:{provider_user_id} -> user_id={user.id}")
            return user
        
        # 身份不存在，创建新用户和身份
        # 生成UUID（如果还没有）
        user_uuid = str(uuid_lib.uuid4())
        
        # 创建用户
        user = User(
            uuid=user_uuid,
            primary_platform=provider,
            last_active_at=datetime.utcnow()
        )
        
        # 根据provider设置用户信息
        if provider == 'telegram':
            if provider_data:
                user.tg_id = int(provider_user_id)
                user.username = provider_data.get('username')
                user.first_name = provider_data.get('first_name')
                user.last_name = provider_data.get('last_name')
                user.language_code = provider_data.get('language_code', 'zh-TW')
        elif provider == 'google':
            if provider_data:
                # Google用户不需要tg_id，可以为None
                user.tg_id = None  # 明确设置为None
                user.username = provider_data.get('email', '').split('@')[0]
                user.first_name = provider_data.get('given_name')
                user.last_name = provider_data.get('family_name')
        elif provider == 'wallet':
            if provider_data:
                # Wallet用户不需要tg_id，可以为None
                user.tg_id = None  # 明确设置为None
                user.wallet_address = provider_user_id
                user.wallet_network = provider_data.get('network', 'TON')
        
        db.add(user)
        await db.flush()
        
        # 创建身份记录
        identity = UserIdentity(
            user_id=user.id,
            provider=provider,
            provider_user_id=str(provider_user_id),
            provider_data=provider_data,
            is_primary=True,  # 第一个身份是主要身份
            verified_at=datetime.utcnow()
        )
        db.add(identity)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Created new user with identity: {provider}:{provider_user_id} -> user_id={user.id}")
        return user
    
    @staticmethod
    async def link_identity(
        db: AsyncSession,
        user_id: int,
        provider: str,
        provider_user_id: str,
        provider_data: Optional[Dict[str, Any]] = None
    ) -> UserIdentity:
        """
        链接新身份到现有用户
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            provider: 身份提供者
            provider_user_id: 提供者的用户ID
            provider_data: 提供者的额外数据
        
        Returns:
            UserIdentity对象
        
        Raises:
            ValueError: 如果身份已存在或用户不存在
        """
        # 检查用户是否存在
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # 检查身份是否已存在
        result = await db.execute(
            select(UserIdentity).where(
                and_(
                    UserIdentity.provider == provider,
                    UserIdentity.provider_user_id == str(provider_user_id)
                )
            )
        )
        existing_identity = result.scalar_one_or_none()
        if existing_identity:
            if existing_identity.user_id == user_id:
                # 已链接到同一用户，更新数据
                if provider_data:
                    existing_identity.provider_data = provider_data
                    existing_identity.verified_at = datetime.utcnow()
                    await db.commit()
                return existing_identity
            else:
                raise ValueError(f"Identity {provider}:{provider_user_id} already linked to another user")
        
        # 创建新身份链接
        identity = UserIdentity(
            user_id=user_id,
            provider=provider,
            provider_user_id=str(provider_user_id),
            provider_data=provider_data,
            is_primary=False,  # 非主要身份
            verified_at=datetime.utcnow()
        )
        db.add(identity)
        await db.commit()
        await db.refresh(identity)
        
        logger.info(f"Linked identity: {provider}:{provider_user_id} -> user_id={user_id}")
        return identity
    
    @staticmethod
    async def generate_magic_link(
        db: AsyncSession,
        user_id: int,
        link_type: str = 'magic_login',
        expires_in_hours: int = 24,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成Magic Link
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            link_type: 链接类型 ('magic_login', 'wallet_link', 'cross_platform')
            expires_in_hours: 过期时间（小时）
            metadata: 额外元数据
        
        Returns:
            Magic Link Token
        """
        # 生成唯一token
        token = secrets.token_urlsafe(32)
        
        # 创建链接记录
        link = AccountLink(
            user_id=user_id,
            link_token=token,
            link_type=link_type,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours),
            link_metadata=metadata
        )
        db.add(link)
        await db.commit()
        
        logger.info(f"Generated magic link: user_id={user_id}, token={token[:8]}...")
        return token
    
    @staticmethod
    async def verify_magic_link(
        db: AsyncSession,
        token: str,
        mark_used: bool = True
    ) -> Optional[User]:
        """
        验证Magic Link并返回用户
        
        Args:
            db: 数据库会话
            token: Magic Link Token
            mark_used: 是否标记为已使用
        
        Returns:
            User对象，如果token无效则返回None
        """
        result = await db.execute(
            select(AccountLink).where(AccountLink.link_token == token)
        )
        link = result.scalar_one_or_none()
        
        if not link:
            logger.warning(f"Magic link not found: {token[:8]}...")
            return None
        
        # 检查是否已使用
        if link.used_at:
            logger.warning(f"Magic link already used: {token[:8]}...")
            return None
        
        # 检查是否过期
        if link.expires_at < datetime.utcnow():
            logger.warning(f"Magic link expired: {token[:8]}...")
            return None
        
        # 获取用户
        result = await db.execute(select(User).where(User.id == link.user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.error(f"User not found for magic link: user_id={link.user_id}")
            return None
        
        # 标记为已使用
        if mark_used:
            link.used_at = datetime.utcnow()
            await db.commit()
        
        logger.info(f"Magic link verified: token={token[:8]}... -> user_id={user.id}")
        return user
    
    @staticmethod
    async def get_user_identities(
        db: AsyncSession,
        user_id: int
    ) -> List[UserIdentity]:
        """
        获取用户的所有身份
        
        Args:
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            身份列表
        """
        result = await db.execute(
            select(UserIdentity).where(UserIdentity.user_id == user_id)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_user_by_telegram_id(
        db: AsyncSession,
        tg_id: int
    ) -> Optional[User]:
        """
        通过Telegram ID获取用户（兼容旧代码）
        
        Args:
            db: 数据库会话
            tg_id: Telegram用户ID
        
        Returns:
            User对象或None
        """
        # 先尝试通过tg_id直接查找（旧方式）
        result = await db.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()
        
        if user:
            return user
        
        # 尝试通过UserIdentity查找
        result = await db.execute(
            select(UserIdentity).where(
                and_(
                    UserIdentity.provider == 'telegram',
                    UserIdentity.provider_user_id == str(tg_id)
                )
            )
        )
        identity = result.scalar_one_or_none()
        
        if identity:
            result = await db.execute(select(User).where(User.id == identity.user_id))
            return result.scalar_one_or_none()
        
        return None

