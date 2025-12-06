"""
修复account_links表，添加link_metadata列
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect, text
from shared.config.settings import get_settings

settings = get_settings()


def upgrade():
    """升级数据库"""
    # 创建同步引擎
    sync_engine = create_engine(settings.DATABASE_URL.replace('+asyncpg', '').replace('+aiosqlite', ''))
    
    with sync_engine.connect() as conn:
        # 检查数据库类型
        db_url = settings.DATABASE_URL
        is_sqlite_db = 'sqlite' in db_url.lower()
        
        inspector = inspect(sync_engine)
        
        # 检查account_links表是否存在
        if 'account_links' not in inspector.get_table_names():
            print("⚠️ account_links表不存在，请先运行add_universal_identity_system.py")
            return
        
        # 检查link_metadata列是否存在
        columns = inspector.get_columns('account_links')
        has_metadata = any(col['name'] == 'link_metadata' for col in columns)
        
        if has_metadata:
            print("✅ link_metadata列已存在，无需修改")
            return
        
        print("🔧 添加link_metadata列到account_links表...")
        
        if is_sqlite_db:
            # SQLite
            conn.execute(text("ALTER TABLE account_links ADD COLUMN link_metadata TEXT;"))
        else:
            # PostgreSQL
            conn.execute(text("ALTER TABLE account_links ADD COLUMN IF NOT EXISTS link_metadata JSONB;"))
        
        conn.commit()
        print("✅ link_metadata列已添加")


if __name__ == "__main__":
    upgrade()

