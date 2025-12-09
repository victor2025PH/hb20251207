#!/usr/bin/env python3
"""
创建管理员用户
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from shared.database.connection import get_async_db
from loguru import logger
import hashlib


async def create_admin_user(username: str = "admin", password: str = "123456", email: str = None):
    """创建管理员用户"""
    async with get_async_db() as db:
        try:
            # 检查用户是否已存在
            result = await db.execute(
                text("SELECT id FROM admin_users WHERE username = :username"),
                {"username": username}
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.warning(f"管理员用户 '{username}' 已存在，跳过创建")
                return
            
            # 生成密码哈希（SHA256，用于测试环境）
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # 创建管理员用户
            await db.execute(text("""
                INSERT INTO admin_users (
                    username, password_hash, email, is_active, created_at, updated_at
                ) VALUES (
                    :username, :password_hash, :email, true, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            """), {
                "username": username,
                "password_hash": password_hash,
                "email": email
            })
            
            await db.commit()
            logger.info(f"✅ 管理员用户 '{username}' 创建成功")
            logger.info(f"   用户名: {username}")
            logger.info(f"   密码: {password}")
            logger.info(f"   邮箱: {email or '未设置'}")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ 创建管理员用户失败: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    import sys
    
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    password = sys.argv[2] if len(sys.argv) > 2 else "123456"
    email = sys.argv[3] if len(sys.argv) > 3 else None
    
    asyncio.run(create_admin_user(username, password, email))

