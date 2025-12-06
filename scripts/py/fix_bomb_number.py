"""
快速修复：添加 bomb_number 字段到 red_packets 表
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from shared.database.connection import get_db, sync_engine
from sqlalchemy import text, inspect
from shared.config.settings import get_settings

settings = get_settings()

def is_sqlite():
    """检查是否使用 SQLite"""
    database_url = settings.DATABASE_URL
    return database_url.startswith("sqlite")

def check_column_exists(engine, table_name, column_name):
    """检查列是否存在"""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception as e:
        print(f"检查列时出错: {e}")
        return False

def fix():
    """执行修复"""
    engine = sync_engine
    is_sqlite_db = is_sqlite()
    
    print(f"数据库类型: {'SQLite' if is_sqlite_db else 'PostgreSQL'}")
    
    try:
        # 检查列是否存在
        if check_column_exists(engine, 'red_packets', 'bomb_number'):
            print("✅ bomb_number 列已存在，无需修复")
            return
        
        print("开始添加 bomb_number 列...")
        
        with get_db() as db:
            if is_sqlite_db:
                db.execute(text("""
                    ALTER TABLE red_packets 
                    ADD COLUMN bomb_number INTEGER NULL
                """))
            else:  # PostgreSQL
                db.execute(text("""
                    ALTER TABLE red_packets 
                    ADD COLUMN bomb_number INTEGER NULL
                """))
            db.commit()
        
        # 再次检查
        if check_column_exists(engine, 'red_packets', 'bomb_number'):
            print("✅ 成功添加 bomb_number 列到 red_packets 表")
        else:
            print("❌ 添加列后检查失败，请手动检查")
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("=" * 50)
    print("修复 bomb_number 字段")
    print("=" * 50)
    fix()
    print("=" * 50)
