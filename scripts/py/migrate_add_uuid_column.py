#!/usr/bin/env python3
"""
数据库迁移脚本：添加所有缺失的列到 users 表
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text, inspect
from shared.database.connection import sync_engine
from shared.config.settings import get_settings
from loguru import logger

settings = get_settings()

def column_exists(conn, table_name, column_name):
    """检查列是否存在"""
    if settings.DATABASE_URL.startswith("postgresql"):
        query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name=:table_name AND column_name=:column_name
        """)
        result = conn.execute(query, {"table_name": table_name, "column_name": column_name})
        return result.fetchone() is not None
    else:
        # SQLite
        query = text("SELECT name FROM pragma_table_info(:table_name) WHERE name=:column_name")
        result = conn.execute(query, {"table_name": table_name, "column_name": column_name})
        return result.fetchone() is not None

def add_column_if_not_exists(conn, column_name, column_def, is_unique=False):
    """添加列（如果不存在）"""
    if column_exists(conn, "users", column_name):
        logger.info(f"  ✓ {column_name} 列已存在，跳过")
        return False
    
    logger.info(f"  添加 {column_name} 列...")
    try:
        if settings.DATABASE_URL.startswith("postgresql"):
            if is_unique:
                # PostgreSQL: 先添加列，再添加唯一约束
                alter_query = text(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                conn.execute(alter_query)
                # 对于可空列，创建部分唯一索引
                if "NULL" in column_def.upper() or "NULLABLE" in column_def.upper():
                    index_query = text(f"CREATE UNIQUE INDEX IF NOT EXISTS ix_users_{column_name} ON users({column_name}) WHERE {column_name} IS NOT NULL")
                else:
                    index_query = text(f"CREATE UNIQUE INDEX IF NOT EXISTS ix_users_{column_name} ON users({column_name})")
                conn.execute(index_query)
            else:
                alter_query = text(f"ALTER TABLE users ADD COLUMN {column_name} {column_def}")
                conn.execute(alter_query)
        else:
            # SQLite 不支持直接添加列，需要重建表
            logger.warning("SQLite 不支持直接添加列，将使用 init_db() 重建表")
            from shared.database.connection import init_db
            init_db()
            logger.info("✅ SQLite 表已重建")
            return True
        conn.commit()
        logger.info(f"  ✅ {column_name} 列添加成功")
        return True
    except Exception as e:
        logger.warning(f"  ⚠️ 添加 {column_name} 列时出错（可能已存在）: {e}")
        try:
            conn.rollback()
        except:
            pass
        return False

def migrate():
    """添加所有缺失的列到 users 表"""
    logger.info("开始数据库迁移：添加缺失的列...")
    
    with sync_engine.connect() as conn:
        # 需要添加的列定义
        columns_to_add = [
            ("uuid", "VARCHAR(36)", True),  # unique
            ("wallet_address", "VARCHAR(255)", False),
            ("wallet_network", "VARCHAR(50)", False),
            ("referrer_id", "INTEGER", False),
            ("referral_code", "VARCHAR(20)", True),  # unique
            ("total_referrals", "INTEGER DEFAULT 0", False),
            ("tier1_commission", "NUMERIC(5,2) DEFAULT 0.10", False),
            ("tier2_commission", "NUMERIC(5,2) DEFAULT 0.05", False),
            ("primary_platform", "VARCHAR(20)", False),
            ("last_active_at", "TIMESTAMP", False),
            ("kyc_status", "VARCHAR(20) DEFAULT 'pending'", False),
            ("kyc_verified_at", "TIMESTAMP", False),
        ]
        
        added_count = 0
        for column_name, column_def, is_unique in columns_to_add:
            if add_column_if_not_exists(conn, column_name, column_def, is_unique):
                added_count += 1
        
        # 添加外键约束（如果使用 PostgreSQL）
        if settings.DATABASE_URL.startswith("postgresql") and not column_exists(conn, "users", "referrer_id"):
            try:
                # 检查外键是否已存在
                fk_query = text("""
                    SELECT constraint_name 
                    FROM information_schema.table_constraints 
                    WHERE table_name='users' 
                    AND constraint_type='FOREIGN KEY'
                    AND constraint_name LIKE '%referrer%'
                """)
                result = conn.execute(fk_query)
                if not result.fetchone():
                    logger.info("  添加 referrer_id 外键约束...")
                    fk_query = text("""
                        ALTER TABLE users 
                        ADD CONSTRAINT fk_users_referrer_id 
                        FOREIGN KEY (referrer_id) REFERENCES users(id)
                    """)
                    conn.execute(fk_query)
                    conn.commit()
                    logger.info("  ✅ referrer_id 外键约束添加成功")
            except Exception as e:
                logger.warning(f"  ⚠️ 添加外键约束时出错（可能已存在）: {e}")
                try:
                    conn.rollback()
                except:
                    pass
        
        # 创建索引
        indexes_to_create = [
            ("ix_users_referral_code", "referral_code", True),
        ]
        
        if settings.DATABASE_URL.startswith("postgresql"):
            for index_name, column_name, is_unique in indexes_to_create:
                if not column_exists(conn, "users", column_name):
                    continue
                try:
                    if is_unique:
                        index_query = text(f"CREATE UNIQUE INDEX IF NOT EXISTS {index_name} ON users({column_name}) WHERE {column_name} IS NOT NULL")
                    else:
                        index_query = text(f"CREATE INDEX IF NOT EXISTS {index_name} ON users({column_name})")
                    conn.execute(index_query)
                    conn.commit()
                    logger.info(f"  ✅ 索引 {index_name} 创建成功")
                except Exception as e:
                    logger.warning(f"  ⚠️ 创建索引 {index_name} 时出错（可能已存在）: {e}")
        
        logger.info(f"✅ 迁移完成！共添加 {added_count} 个列")

if __name__ == "__main__":
    try:
        migrate()
        print("✅ 迁移完成！")
    except Exception as e:
        logger.error(f"迁移失败: {e}", exc_info=True)
        sys.exit(1)

