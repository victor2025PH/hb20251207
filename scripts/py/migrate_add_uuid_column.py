#!/usr/bin/env python3
"""
数据库迁移脚本：添加 uuid 列到 users 表
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from shared.database.connection import sync_engine
from shared.config.settings import get_settings
from loguru import logger

settings = get_settings()

def migrate():
    """添加 uuid 列到 users 表"""
    logger.info("开始数据库迁移：添加 uuid 列...")
    
    with sync_engine.connect() as conn:
        # 检查列是否已存在
        if settings.DATABASE_URL.startswith("postgresql"):
            # PostgreSQL
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name='uuid'
            """)
        else:
            # SQLite
            check_query = text("""
                SELECT name 
                FROM pragma_table_info('users') 
                WHERE name='uuid'
            """)
        
        result = conn.execute(check_query)
        if result.fetchone():
            logger.info("✅ uuid 列已存在，跳过迁移")
            return
        
        # 添加 uuid 列
        logger.info("添加 uuid 列...")
        if settings.DATABASE_URL.startswith("postgresql"):
            # PostgreSQL
            alter_query = text("""
                ALTER TABLE users 
                ADD COLUMN uuid VARCHAR(36) UNIQUE
            """)
        else:
            # SQLite (需要重建表)
            logger.warning("SQLite 不支持直接添加 UNIQUE 列，将使用 init_db() 重建表")
            from shared.database.connection import init_db
            init_db()
            logger.info("✅ SQLite 表已重建")
            return
        
        try:
            conn.execute(alter_query)
            conn.commit()
            logger.info("✅ uuid 列添加成功")
        except Exception as e:
            logger.error(f"❌ 添加 uuid 列失败: {e}")
            # 如果列已存在但检查失败，尝试创建索引
            try:
                if settings.DATABASE_URL.startswith("postgresql"):
                    index_query = text("CREATE INDEX IF NOT EXISTS ix_users_uuid ON users(uuid)")
                    conn.execute(index_query)
                    conn.commit()
                    logger.info("✅ uuid 索引创建成功")
            except Exception as e2:
                logger.warning(f"创建索引失败（可能已存在）: {e2}")

if __name__ == "__main__":
    try:
        migrate()
        print("✅ 迁移完成！")
    except Exception as e:
        logger.error(f"迁移失败: {e}", exc_info=True)
        sys.exit(1)

