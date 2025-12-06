"""
全自动修复：添加所有缺失的数据库字段
修复 bomb_number 和 deleted_at 字段
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

def fix_all_columns():
    """执行修复 - 添加所有缺失的字段"""
    engine = sync_engine
    is_sqlite_db = is_sqlite()
    
    print(f"数据库类型: {'SQLite' if is_sqlite_db else 'PostgreSQL'}")
    print("=" * 60)
    
    # 需要添加的字段列表
    columns_to_add = [
        {
            'table': 'red_packets',
            'column': 'bomb_number',
            'type_sqlite': 'INTEGER NULL',
            'type_postgres': 'INTEGER NULL',
            'description': '炸彈數字（0-9），用於紅包炸彈遊戲'
        },
        {
            'table': 'red_packets',
            'column': 'deleted_at',
            'type_sqlite': 'DATETIME NULL',
            'type_postgres': 'TIMESTAMP NULL',
            'description': '軟刪除時間戳'
        }
    ]
    
    fixed_count = 0
    skipped_count = 0
    
    try:
        with get_db() as db:
            for col_info in columns_to_add:
                table_name = col_info['table']
                column_name = col_info['column']
                
                # 检查表是否存在
                if is_sqlite_db:
                    result = db.execute(text(f"""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='{table_name}'
                    """))
                else:
                    result = db.execute(text("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = :table_name
                    """), {"table_name": table_name})
                
                table_exists = result.fetchone() is not None
                
                if not table_exists:
                    print(f"⚠️  表 {table_name} 不存在，跳过")
                    continue
                
                # 检查列是否已存在
                if check_column_exists(engine, table_name, column_name):
                    print(f"✅ {table_name}.{column_name} 已存在，跳过")
                    skipped_count += 1
                    continue
                
                # 添加列
                print(f"🔧 正在添加 {table_name}.{column_name}...")
                
                if is_sqlite_db:
                    sql_type = col_info['type_sqlite']
                else:
                    sql_type = col_info['type_postgres']
                
                try:
                    db.execute(text(f"""
                        ALTER TABLE {table_name} 
                        ADD COLUMN {column_name} {sql_type}
                    """))
                    db.commit()
                    
                    # 验证
                    if check_column_exists(engine, table_name, column_name):
                        print(f"✅ 成功添加 {table_name}.{column_name} ({col_info['description']})")
                        fixed_count += 1
                    else:
                        print(f"❌ 添加 {table_name}.{column_name} 后验证失败")
                except Exception as e:
                    print(f"❌ 添加 {table_name}.{column_name} 失败: {e}")
                    db.rollback()
        
        print("=" * 60)
        print(f"修复完成！")
        print(f"  ✅ 已添加: {fixed_count} 个字段")
        print(f"  ⏭️  已跳过: {skipped_count} 个字段（已存在）")
        
        # 最终验证
        print("\n最终验证:")
        for col_info in columns_to_add:
            table_name = col_info['table']
            column_name = col_info['column']
            exists = check_column_exists(engine, table_name, column_name)
            status = "✅" if exists else "❌"
            print(f"  {status} {table_name}.{column_name}: {'存在' if exists else '缺失'}")
            
    except Exception as e:
        print(f"❌ 修复过程出错: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("全自动修复数据库字段")
    print("=" * 60)
    print()
    fix_all_columns()
    print()
    print("=" * 60)
