"""
同步余额：从API数据库同步到Bot数据库
或者检查两个数据库的余额差异
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from shared.database.connection import get_db, sync_engine
from shared.database.models import User
from shared.config.settings import get_settings
from sqlalchemy import create_engine, text

settings = get_settings()

def check_and_sync_balance():
    """检查并同步余额"""
    print("=" * 70)
    print("检查余额同步")
    print("=" * 70)
    print()
    
    print("1. 检查当前数据库配置")
    print("-" * 70)
    current_db_url = str(sync_engine.url)
    print(f"Bot使用的数据库: {current_db_url}")
    print()
    
    # 检查数据库中的用户余额
    print("2. 检查数据库中的用户余额")
    print("-" * 70)
    
    try:
        with get_db() as db:
            # 查找目标用户
            target_username = "aixinwww"
            target_tg_id = 6359371231  # 从日志中看到的用户ID
            
            # 按用户名查找
            user_by_username = db.query(User).filter(User.username == target_username).first()
            # 按TG ID查找
            user_by_tg_id = db.query(User).filter(User.tg_id == target_tg_id).first()
            
            if user_by_username:
                user = user_by_username
                print(f"找到用户（按用户名）: @{user.username} (TG ID: {user.tg_id})")
            elif user_by_tg_id:
                user = user_by_tg_id
                print(f"找到用户（按TG ID）: TG ID {user.tg_id} (@{user.username or '未设置'})")
            else:
                print(f"⚠️  未找到用户 @{target_username} 或 TG ID {target_tg_id}")
                print()
                print("数据库中的所有用户：")
                all_users = db.query(User).all()
                for u in all_users:
                    print(f"  - @{u.username or '未设置'} (TG ID: {u.tg_id}, DB ID: {u.id})")
                return
            
            # 读取余额
            usdt = float(user.balance_usdt or 0)
            ton = float(user.balance_ton or 0)
            stars = user.balance_stars or 0
            points = user.balance_points or 0
            
            print()
            print("当前余额（Bot数据库）:")
            print(f"  USDT: {usdt:.4f}")
            print(f"  TON: {ton:.4f}")
            print(f"  Stars: {stars}")
            print(f"  能量: {points}")
            print()
            print("MiniApp显示的余额:")
            print(f"  USDT: 10463.46")
            print(f"  TON: 1000.00")
            print(f"  Stars: 1999")
            print()
            
            if usdt < 10000 or ton < 1000 or stars < 1000:
                print("❌ 余额不匹配！")
                print()
                print("可能的原因：")
                print("  1. Bot和MiniApp使用不同的数据库")
                print("  2. 数据库连接配置不同")
                print("  3. 需要同步余额")
                print()
                
                # 询问是否同步
                print("=" * 70)
                print("余额同步选项")
                print("=" * 70)
                print()
                print("如果MiniApp使用的是PostgreSQL数据库，而Bot使用SQLite，")
                print("需要手动同步余额。")
                print()
                print("选项1: 手动更新余额（从MiniApp的值）")
                print("选项2: 检查是否有其他数据库文件")
                print("选项3: 检查API的数据库配置")
                print()
                
                # 提供手动更新脚本
                print("如果要手动更新余额，可以运行：")
                print()
                print("python -c \"")
                print("from shared.database.connection import get_db;")
                print("from shared.database.models import User;")
                print("with get_db() as db:")
                print("    user = db.query(User).filter(User.tg_id == 6359371231).first()")
                print("    if user:")
                print("        user.balance_usdt = 10463.46")
                print("        user.balance_ton = 1000.00")
                print("        user.balance_stars = 1999")
                print("        db.commit()")
                print("        print('✅ 余额已更新')")
                print("\"")
            else:
                print("✅ 余额匹配")
                
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_and_sync_balance()
