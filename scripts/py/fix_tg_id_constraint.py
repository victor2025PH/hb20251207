#!/usr/bin/env python3
"""
修复数据库 tg_id 列的 NOT NULL 约束
确保 tg_id 可以为 NULL（支持非 Telegram 用户）
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

def fix_tg_id_constraint():
    """修复 tg_id 列的约束"""
    logger.info("检查并修复 tg_id 列的约束...")
    
    with sync_engine.connect() as conn:
        if settings.DATABASE_URL.startswith("postgresql"):
            # PostgreSQL: 检查并修改列约束
            try:
                # 检查当前约束
                check_query = text("""
                    SELECT 
                        column_name, 
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'tg_id'
                """)
                result = conn.execute(check_query)
                row = result.fetchone()
                
                if row:
                    is_nullable = row[1]
                    logger.info(f"当前 tg_id 列约束: is_nullable={is_nullable}")
                    
                    if is_nullable == 'NO':
                        logger.info("修改 tg_id 列为可空...")
                        alter_query = text("ALTER TABLE users ALTER COLUMN tg_id DROP NOT NULL")
                        conn.execute(alter_query)
                        conn.commit()
                        logger.info("✅ tg_id 列已修改为可空")
                    else:
                        logger.info("✅ tg_id 列已经是可空的，无需修改")
                else:
                    logger.warning("未找到 tg_id 列")
                    
            except Exception as e:
                logger.error(f"修复 tg_id 约束失败: {e}", exc_info=True)
                try:
                    conn.rollback()
                except:
                    pass
        else:
            # SQLite: 不支持直接修改列约束，需要重建表
            logger.warning("SQLite 不支持直接修改列约束")
            logger.info("使用 init_db() 重建表...")
            from shared.database.connection import init_db
            init_db()
            logger.info("✅ SQLite 表已重建")

if __name__ == "__main__":
    try:
        fix_tg_id_constraint()
        print("✅ 约束修复完成！")
    except Exception as e:
        logger.error(f"修复失败: {e}", exc_info=True)
        sys.exit(1)

