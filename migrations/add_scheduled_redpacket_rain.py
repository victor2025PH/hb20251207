#!/usr/bin/env python3
"""
添加 scheduled_redpacket_rains 表
用于红包雨调度功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from shared.database.connection import get_async_db
from loguru import logger


async def upgrade():
    """执行迁移"""
    async with get_async_db() as db:
        try:
            # 创建 scheduled_redpacket_rains 表
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS scheduled_redpacket_rains (
                    id SERIAL PRIMARY KEY,
                    start_time TIMESTAMP NOT NULL,
                    total_amount NUMERIC(20, 8) NOT NULL,
                    currency VARCHAR(32) NOT NULL,
                    packet_count INTEGER NOT NULL,
                    target_chat_id BIGINT,
                    message TEXT,
                    packet_type VARCHAR(32),
                    status VARCHAR(32) DEFAULT 'scheduled',
                    created_by INTEGER REFERENCES admin_users(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    executed_at TIMESTAMP
                )
            """))
            
            # 创建索引
            await db.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_scheduled_rain_start_time 
                ON scheduled_redpacket_rains(start_time)
            """))
            
            await db.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_scheduled_rain_status 
                ON scheduled_redpacket_rains(status)
            """))
            
            await db.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_scheduled_redpacket_rains_target_chat_id 
                ON scheduled_redpacket_rains(target_chat_id)
            """))
            
            await db.commit()
            logger.info("✅ scheduled_redpacket_rains 表创建成功")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ 迁移失败: {e}")
            raise


async def downgrade():
    """回滚迁移"""
    async with get_async_db() as db:
        try:
            # 删除索引
            await db.execute(text("DROP INDEX IF EXISTS ix_scheduled_redpacket_rains_target_chat_id"))
            await db.execute(text("DROP INDEX IF EXISTS ix_scheduled_rain_status"))
            await db.execute(text("DROP INDEX IF EXISTS ix_scheduled_rain_start_time"))
            
            # 删除表
            await db.execute(text("DROP TABLE IF EXISTS scheduled_redpacket_rains"))
            
            await db.commit()
            logger.info("✅ scheduled_redpacket_rains 表已删除")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ 回滚失败: {e}")
            raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "down":
        asyncio.run(downgrade())
    else:
        asyncio.run(upgrade())

