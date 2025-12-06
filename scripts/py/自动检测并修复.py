"""
自动检测并修复所有常见错误
包括数据库字段缺失、代码问题等
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from shared.database.connection import get_db, sync_engine
from sqlalchemy import text, inspect
from shared.database.models import RedPacket, User, RedPacketClaim
from shared.config.settings import get_settings
import subprocess
import traceback

settings = get_settings()

def is_sqlite():
    """检查是否使用 SQLite"""
    return settings.DATABASE_URL.startswith("sqlite")

def check_column_exists(engine, table_name, column_name):
    """检查列是否存在"""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        return column_name in columns
    except Exception as e:
        return False

def test_database_queries():
    """测试常见的数据库查询，检测错误"""
    print("=" * 70)
    print("测试数据库查询（检测常见错误）")
    print("=" * 70)
    
    errors = []
    
    try:
        with get_db() as db:
            # 测试1: 查询用户
            try:
                user = db.query(User).first()
                if user:
                    print("  ✅ 用户查询正常")
                else:
                    print("  ⚠️  没有用户数据（这是正常的，如果数据库是新的）")
            except Exception as e:
                errors.append(f"用户查询失败: {e}")
                print(f"  ❌ 用户查询失败: {e}")
            
            # 测试2: 查询RedPacket（会触发bomb_number和deleted_at检查）
            try:
                packet_count = db.query(RedPacket).count()
                print(f"  ✅ RedPacket查询正常 (共 {packet_count} 条记录)")
            except Exception as e:
                error_msg = str(e)
                if "bomb_number" in error_msg:
                    errors.append("bomb_number字段缺失")
                    print(f"  ❌ RedPacket查询失败: bomb_number字段缺失")
                elif "deleted_at" in error_msg:
                    errors.append("deleted_at字段缺失")
                    print(f"  ❌ RedPacket查询失败: deleted_at字段缺失")
                else:
                    errors.append(f"RedPacket查询失败: {e}")
                    print(f"  ❌ RedPacket查询失败: {e}")
            
            # 测试3: 统计查询（show_profile_menu中使用的）
            try:
                if user:
                    sent_count = db.query(RedPacket).filter(RedPacket.sender_id == user.id).count()
                    claimed_count = db.query(RedPacketClaim).filter(RedPacketClaim.user_id == user.id).count()
                    print(f"  ✅ 统计查询正常 (已发: {sent_count}, 已抢: {claimed_count})")
            except Exception as e:
                error_msg = str(e)
                if "bomb_number" in error_msg:
                    errors.append("bomb_number字段缺失（统计查询）")
                    print(f"  ❌ 统计查询失败: bomb_number字段缺失")
                elif "deleted_at" in error_msg:
                    errors.append("deleted_at字段缺失（统计查询）")
                    print(f"  ❌ 统计查询失败: deleted_at字段缺失")
                elif "is_bomb" in error_msg:
                    errors.append("is_bomb字段缺失（统计查询）")
                    print(f"  ❌ 统计查询失败: is_bomb字段缺失")
                elif "penalty_amount" in error_msg:
                    errors.append("penalty_amount字段缺失（统计查询）")
                    print(f"  ❌ 统计查询失败: penalty_amount字段缺失")
                else:
                    errors.append(f"统计查询失败: {e}")
                    print(f"  ❌ 统计查询失败: {e}")
            
            # 测试4: 检查所有必需的字段
            print()
            print("检查必需的数据库字段:")
            required_fields = [
                ('red_packets', 'bomb_number', 'INTEGER NULL'),
                ('red_packets', 'deleted_at', 'DATETIME NULL'),
                ('red_packet_claims', 'is_bomb', 'INTEGER NULL'),
                ('red_packet_claims', 'penalty_amount', 'NUMERIC(20, 8) NULL'),
            ]
            
            for table, column, sql_type in required_fields:
                exists = check_column_exists(sync_engine, table, column)
                if exists:
                    print(f"  ✅ {table}.{column} 存在")
                else:
                    errors.append(f"{table}.{column}字段缺失")
                    print(f"  ❌ {table}.{column} 缺失")
    
    except Exception as e:
        errors.append(f"数据库连接失败: {e}")
        print(f"  ❌ 数据库连接失败: {e}")
    
    print()
    return errors

def fix_database_fields():
    """修复所有缺失的数据库字段"""
    print("=" * 70)
    print("修复数据库字段")
    print("=" * 70)
    
    engine = sync_engine
    is_sqlite_db = is_sqlite()
    
    columns_to_add = [
        {
            'table': 'red_packets',
            'column': 'bomb_number',
            'type_sqlite': 'INTEGER NULL',
            'type_postgres': 'INTEGER NULL',
        },
        {
            'table': 'red_packets',
            'column': 'deleted_at',
            'type_sqlite': 'DATETIME NULL',
            'type_postgres': 'TIMESTAMP NULL',
        },
        {
            'table': 'red_packet_claims',
            'column': 'is_bomb',
            'type_sqlite': 'INTEGER NULL',  # SQLite使用INTEGER表示BOOLEAN
            'type_postgres': 'BOOLEAN NULL',
        },
        {
            'table': 'red_packet_claims',
            'column': 'penalty_amount',
            'type_sqlite': 'NUMERIC(20, 8) NULL',
            'type_postgres': 'NUMERIC(20, 8) NULL',
        }
    ]
    
    fixed = []
    failed = []
    
    try:
        with get_db() as db:
            for col_info in columns_to_add:
                table_name = col_info['table']
                column_name = col_info['column']
                
                # 检查是否已存在
                if check_column_exists(engine, table_name, column_name):
                    continue
                
                # 添加字段
                try:
                    if is_sqlite_db:
                        sql_type = col_info['type_sqlite']
                    else:
                        sql_type = col_info['type_postgres']
                    
                    db.execute(text(f"""
                        ALTER TABLE {table_name} 
                        ADD COLUMN {column_name} {sql_type}
                    """))
                    db.commit()
                    
                    # 验证
                    if check_column_exists(engine, table_name, column_name):
                        fixed.append(f"{table_name}.{column_name}")
                        print(f"  ✅ 已添加 {table_name}.{column_name}")
                    else:
                        failed.append(f"{table_name}.{column_name}")
                        print(f"  ❌ 添加 {table_name}.{column_name} 后验证失败")
                except Exception as e:
                    failed.append(f"{table_name}.{column_name}: {e}")
                    print(f"  ❌ 添加 {table_name}.{column_name} 失败: {e}")
                    db.rollback()
    except Exception as e:
        print(f"  ❌ 修复过程出错: {e}")
        return False
    
    print()
    return len(failed) == 0

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
    
    errors = []
    for file_path in files_to_check:
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"  ✅ {file_path}")
            else:
                errors.append(f"{file_path}: {result.stderr}")
                print(f"  ❌ {file_path}")
        except Exception as e:
            errors.append(f"{file_path}: {e}")
            print(f"  ❌ {file_path}: {e}")
    
    print()
    return errors

def main():
    """主函数 - 自动检测并修复"""
    print()
    print("=" * 70)
    print("自动检测并修复系统")
    print("=" * 70)
    print()
    
    all_fixed = True
    
    # 步骤1: 测试数据库查询，检测错误
    errors = test_database_queries()
    
    # 步骤2: 如果有错误，自动修复
    if errors:
        print("=" * 70)
        print("发现错误，开始自动修复...")
        print("=" * 70)
        print()
        
        # 修复数据库字段
        if any("bomb_number" in e or "deleted_at" in e or "is_bomb" in e or "penalty_amount" in e for e in errors):
            if not fix_database_fields():
                all_fixed = False
        
        # 重新测试
        print()
        print("=" * 70)
        print("重新测试数据库查询")
        print("=" * 70)
        errors_after_fix = test_database_queries()
        
        if errors_after_fix:
            print("❌ 修复后仍有错误:")
            for e in errors_after_fix:
                print(f"  - {e}")
            all_fixed = False
        else:
            print("✅ 所有数据库错误已修复！")
    else:
        print("✅ 未发现数据库错误")
    
    # 步骤3: 验证代码语法
    code_errors = verify_code_syntax()
    if code_errors:
        print("❌ 发现代码语法错误:")
        for e in code_errors:
            print(f"  - {e}")
        all_fixed = False
    else:
        print("✅ 代码语法检查通过")
    
    # 总结
    print()
    print("=" * 70)
    print("检测和修复总结")
    print("=" * 70)
    
    if all_fixed and not errors and not code_errors:
        print("✅ 所有检查通过，没有发现错误！")
        print()
        print("Bot应该可以正常运行。如果还有问题，请查看Bot日志。")
        return 0
    else:
        print("⚠️  发现一些问题，已尝试修复")
        if errors:
            print(f"  - 数据库错误: {len(errors)} 个")
        if code_errors:
            print(f"  - 代码错误: {len(code_errors)} 个")
        print()
        print("建议：")
        print("  1. 重新运行此脚本: python 自动检测并修复.py")
        print("  2. 如果问题持续，请查看Bot日志获取详细错误信息")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
        traceback.print_exc()
        sys.exit(1)
