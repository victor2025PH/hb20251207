#!/usr/bin/env python3
"""
生成推荐关系树测试数据
用于测试邀请管理功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from shared.database.connection import get_async_db
from shared.config.settings import get_settings
from loguru import logger

settings = get_settings()


async def seed_referral_tree():
    """生成推荐关系树测试数据"""
    async with get_async_db() as db:
        try:
            # 创建测试用户（3层推荐关系）
            # 第1层：root_user
            # 第2层：user_1, user_2 (邀请人: root_user)
            # 第3层：user_1_1, user_1_2 (邀请人: user_1), user_2_1 (邀请人: user_2)
            
            logger.info("开始生成推荐关系树测试数据...")
            
            # 检查 root_user 是否已存在
            result = await db.execute(
                text("SELECT id FROM users WHERE username = 'test_root_user'")
            )
            root_user = result.scalar_one_or_none()
            
            if root_user:
                logger.info("测试用户已存在，跳过创建")
                return
            
            # 创建 root_user (第1层)
            await db.execute(text("""
                INSERT INTO users (
                    username, first_name, last_name, invite_code, 
                    balance_usdt, balance_ton, balance_stars, balance_points,
                    level, xp, created_at
                ) VALUES (
                    'test_root_user', 'Root', 'User', 'ROOT001',
                    1000.0, 100.0, 5000, 10000,
                    5, 500, CURRENT_TIMESTAMP
                ) RETURNING id
            """))
            root_result = await db.execute(
                text("SELECT id FROM users WHERE username = 'test_root_user'")
            )
            root_user_id = root_result.scalar_one()
            logger.info(f"✅ 创建 root_user (id: {root_user_id})")
            
            # 创建第2层用户
            await db.execute(text("""
                INSERT INTO users (
                    username, first_name, last_name, invite_code, 
                    balance_usdt, balance_ton, balance_stars, balance_points,
                    level, xp, created_at, referrer_id
                ) VALUES 
                ('test_user_1', 'User', 'One', 'USER001', 500.0, 50.0, 2500, 5000, 3, 300, CURRENT_TIMESTAMP, :root_id),
                ('test_user_2', 'User', 'Two', 'USER002', 500.0, 50.0, 2500, 5000, 3, 300, CURRENT_TIMESTAMP, :root_id)
            """), {"root_id": root_user_id})
            
            # 获取第2层用户ID
            user1_result = await db.execute(
                text("SELECT id FROM users WHERE username = 'test_user_1'")
            )
            user1_id = user1_result.scalar_one()
            
            user2_result = await db.execute(
                text("SELECT id FROM users WHERE username = 'test_user_2'")
            )
            user2_id = user2_result.scalar_one()
            logger.info(f"✅ 创建第2层用户: user_1 (id: {user1_id}), user_2 (id: {user2_id})")
            
            # 创建第3层用户
            await db.execute(text("""
                INSERT INTO users (
                    username, first_name, last_name, invite_code, 
                    balance_usdt, balance_ton, balance_stars, balance_points,
                    level, xp, created_at, referrer_id
                ) VALUES 
                ('test_user_1_1', 'User', 'One-One', 'U1_1001', 200.0, 20.0, 1000, 2000, 2, 200, CURRENT_TIMESTAMP, :user1_id),
                ('test_user_1_2', 'User', 'One-Two', 'U1_1002', 200.0, 20.0, 1000, 2000, 2, 200, CURRENT_TIMESTAMP, :user1_id),
                ('test_user_2_1', 'User', 'Two-One', 'U2_2001', 200.0, 20.0, 1000, 2000, 2, 200, CURRENT_TIMESTAMP, :user2_id)
            """), {"user1_id": user1_id, "user2_id": user2_id})
            
            # 获取第3层用户ID
            user1_1_result = await db.execute(
                text("SELECT id FROM users WHERE username = 'test_user_1_1'")
            )
            user1_1_id = user1_1_result.scalar_one()
            
            user1_2_result = await db.execute(
                text("SELECT id FROM users WHERE username = 'test_user_1_2'")
            )
            user1_2_id = user1_2_result.scalar_one()
            
            user2_1_result = await db.execute(
                text("SELECT id FROM users WHERE username = 'test_user_2_1'")
            )
            user2_1_id = user2_1_result.scalar_one()
            logger.info(f"✅ 创建第3层用户: user_1_1 (id: {user1_1_id}), user_1_2 (id: {user1_2_id}), user_2_1 (id: {user2_1_id})")
            
            # 更新 invited_by 字段（兼容旧字段）
            await db.execute(text("""
                UPDATE users 
                SET invited_by = referrer_id 
                WHERE referrer_id IS NOT NULL AND invited_by IS NULL
            """))
            
            await db.commit()
            logger.info("✅ 推荐关系树测试数据生成完成！")
            logger.info("")
            logger.info("推荐关系结构：")
            logger.info("  test_root_user (id: {})".format(root_user_id))
            logger.info("    ├── test_user_1 (id: {})".format(user1_id))
            logger.info("    │   ├── test_user_1_1 (id: {})".format(user1_1_id))
            logger.info("    │   └── test_user_1_2 (id: {})".format(user1_2_id))
            logger.info("    └── test_user_2 (id: {})".format(user2_id))
            logger.info("        └── test_user_2_1 (id: {})".format(user2_1_id))
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ 生成测试数据失败: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    asyncio.run(seed_referral_tree())
