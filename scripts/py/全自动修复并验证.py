"""
全自动修复并验证所有数据库字段和代码
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from shared.database.connection import get_db, sync_engine
from sqlalchemy import text, inspect
from shared.config.settings import get_settings
import subprocess

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
    
    print("=" * 70)
    print("全自动修复数据库字段")
    print("=" * 70)
    print(f"数据库类型: {'SQLite' if is_sqlite_db else 'PostgreSQL'}")
    print()
    
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
    error_count = 0
    
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
                    print(f"✅ {table_name}.{column_name} 已存在")
                    skipped_count += 1
                    continue
                
                # 添加列
                print(f"🔧 正在添加 {table_name}.{column_name}...", end=" ")
                
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
                        print(f"✅ 成功")
                        fixed_count += 1
                    else:
                        print(f"❌ 验证失败")
                        error_count += 1
                except Exception as e:
                    print(f"❌ 失败: {e}")
                    db.rollback()
                    error_count += 1
        
        print()
        print("=" * 70)
        print("修复结果")
        print("=" * 70)
        print(f"  ✅ 已添加: {fixed_count} 个字段")
        print(f"  ⏭️  已跳过: {skipped_count} 个字段（已存在）")
        if error_count > 0:
            print(f"  ❌ 失败: {error_count} 个字段")
        print()
        
        # 最终验证
        print("最终验证:")
        all_ok = True
        for col_info in columns_to_add:
            table_name = col_info['table']
            column_name = col_info['column']
            exists = check_column_exists(engine, table_name, column_name)
            status = "✅" if exists else "❌"
            print(f"  {status} {table_name}.{column_name}: {'存在' if exists else '缺失'}")
            if not exists:
                all_ok = False
        
        print()
        return all_ok
            
    except Exception as e:
        print(f"❌ 修复过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_code_syntax():
    """验证代码语法"""
    print("=" * 70)
    print("验证代码语法")
    print("=" * 70)
    
    files_to_check = [
        'bot/handlers/packets.py',
        'bot/handlers/keyboard.py',
        'bot/handlers/menu.py',
        'bot/utils/i18n.py',
        'bot/handlers/profile.py',
    ]
    
    all_ok = True
    for file_path in files_to_check:
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', file_path],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  ✅ {file_path}")
            else:
                print(f"  ❌ {file_path}: {result.stderr}")
                all_ok = False
        except Exception as e:
            print(f"  ❌ {file_path}: {e}")
            all_ok = False
    
    print()
    return all_ok

def main():
    """主函数"""
    print()
    print("=" * 70)
    print("全自动修复并验证")
    print("=" * 70)
    print()
    
    # 1. 修复数据库字段
    db_ok = fix_all_columns()
    
    # 2. 验证代码语法
    code_ok = verify_code_syntax()
    
    # 3. 总结
    print("=" * 70)
    print("修复和验证总结")
    print("=" * 70)
    
    if db_ok and code_ok:
        print("✅ 所有检查和修复完成！")
        print()
        print("现在可以启动Bot进行测试：")
        print("  .\\一键启动测试.bat")
        print()
        print("测试清单：")
        print("  1. 发送 /start")
        print("  2. 点击 '👤 我的' - 应该不再出错")
        print("  3. 点击 '🧧 紅包' → '➕ 發紅包' - 应该不再出错")
        print("  4. 点击 '🎁 我的紅包' - 应该不再出错")
        print("  5. 测试所有其他按钮")
        return 0
    else:
        print("❌ 部分检查失败，请查看上面的错误信息")
        if not db_ok:
            print("  - 数据库字段修复失败")
        if not code_ok:
            print("  - 代码语法检查失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
