#!/usr/bin/env python3
"""
验证部署状态和功能
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from shared.database.connection import get_async_db
from loguru import logger


async def verify_deployment():
    """验证部署状态"""
    async with get_async_db() as db:
        try:
            # 1. 检查 scheduled_redpacket_rains 表
            result = await db.execute(
                text("SELECT COUNT(*) FROM scheduled_redpacket_rains")
            )
            count = result.scalar_one()
            logger.info(f"✅ scheduled_redpacket_rains 表存在，记录数: {count}")
            
            # 2. 检查 system_config 表（如果存在）
            try:
                result = await db.execute(
                    text("SELECT COUNT(*) FROM system_config WHERE key LIKE '%commission%' OR key LIKE '%invite%'")
                )
                config_count = result.scalar_one()
                logger.info(f"✅ 推荐系统配置项数: {config_count}")
            except Exception:
                logger.warning("⚠️  system_config 表不存在（可能需要运行数据库迁移）")
            
            # 3. 检查测试用户
            result = await db.execute(
                text("SELECT username, referrer_id FROM users WHERE username LIKE 'test_%' ORDER BY username")
            )
            test_users = result.fetchall()
            logger.info(f"✅ 测试用户数: {len(test_users)}")
            if test_users:
                logger.info("测试用户列表:")
                for row in test_users:
                    logger.info(f"  - {row[0]} (邀请人ID: {row[1]})")
            
            # 4. 检查用户表结构
            result = await db.execute(
                text("SELECT COUNT(*) FROM users")
            )
            user_count = result.scalar_one()
            logger.info(f"✅ 用户总数: {user_count}")
            
            logger.info("\n✅ 部署验证完成！")
            
        except Exception as e:
            logger.error(f"❌ 验证失败: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    asyncio.run(verify_deployment())

