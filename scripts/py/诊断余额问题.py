"""
诊断余额不同步问题
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from shared.database.connection import get_db, sync_engine
from shared.database.models import User
from shared.config.settings import get_settings
from sqlalchemy import text

settings = get_settings()

def diagnose_balance_issue():
    """诊断余额问题"""
    print("=" * 70)
    print("诊断余额不同步问题")
    print("=" * 70)
    print()
    
    print("1. 检查数据库配置")
    print("-" * 70)
    print(f"DATABASE_URL: {settings.DATABASE_URL}")
    db_type = "SQLite" if "sqlite" in settings.DATABASE_URL.lower() else "PostgreSQL"
    print(f"数据库类型: {db_type}")
    print()
    
    print("2. 检查数据库中的用户")
    print("-" * 70)
    try:
        with get_db() as db:
            # 获取所有用户
            users = db.query(User).all()
            print(f"找到 {len(users)} 个用户")
            print()
            
            if not users:
                print("⚠️  数据库中没有用户")
                return
            
            # 查找目标用户（从图片看是 @aixinwww）
            target_username = "aixinwww"
            target_user = None
            
            for user in users:
                print(f"用户: @{user.username or '未设置'} (TG ID: {user.tg_id}, DB ID: {user.id})")
                
                # 在会话内读取余额
                usdt = float(user.balance_usdt or 0)
                ton = float(user.balance_ton or 0)
                stars = user.balance_stars or 0
                points = user.balance_points or 0
                
                print(f"  余额: USDT={usdt:.4f}, TON={ton:.4f}, Stars={stars}, 能量={points}")
                
                if user.username == target_username:
                    target_user = user
                    print(f"  ⭐ 这是目标用户")
                
                print()
            
            print("3. 检查目标用户详情")
            print("-" * 70)
            
            if target_user:
                # 重新查询确保数据最新
                fresh_user = db.query(User).filter(User.id == target_user.id).first()
                
                usdt = float(fresh_user.balance_usdt or 0)
                ton = float(fresh_user.balance_ton or 0)
                stars = fresh_user.balance_stars or 0
                points = fresh_user.balance_points or 0
                
                print(f"用户: @{fresh_user.username}")
                print(f"TG ID: {fresh_user.tg_id}")
                print(f"数据库ID: {fresh_user.id}")
                print()
                print("当前余额（Bot读取）:")
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
                    print("  2. 数据库连接配置不同（.env vs settings.py）")
                    print("  3. 用户ID不匹配（不同的用户记录）")
                    print("  4. 余额字段类型问题（Numeric vs Float）")
                    print()
                    print("建议检查：")
                    print("  1. 检查 .env 文件中的 DATABASE_URL")
                    print("  2. 检查 API 的数据库配置")
                    print("  3. 确认Bot和API使用同一个数据库")
                    print("  4. 检查是否有多个用户记录（相同的tg_id）")
                    
                    # 检查是否有重复用户
                    print()
                    print("4. 检查重复用户")
                    print("-" * 70)
                    duplicate_users = db.query(User).filter(User.tg_id == fresh_user.tg_id).all()
                    if len(duplicate_users) > 1:
                        print(f"⚠️  发现 {len(duplicate_users)} 个相同TG ID的用户记录！")
                        for idx, dup_user in enumerate(duplicate_users, 1):
                            print(f"  记录 {idx}: DB ID={dup_user.id}, USDT={float(dup_user.balance_usdt or 0):.4f}")
                    else:
                        print("✅ 没有重复用户记录")
                    
                    # 检查数据库文件位置
                    if db_type == "SQLite":
                        print()
                        print("5. 检查SQLite数据库文件")
                        print("-" * 70)
                        db_path = settings.DATABASE_URL.replace("sqlite:///", "").replace("sqlite:///./", "")
                        from pathlib import Path
                        db_file = Path(db_path)
                        if db_file.exists():
                            print(f"✅ 数据库文件存在: {db_file.absolute()}")
                            print(f"   文件大小: {db_file.stat().st_size / 1024:.2f} KB")
                        else:
                            print(f"❌ 数据库文件不存在: {db_file.absolute()}")
                            # 尝试查找
                            possible_paths = [
                                Path.cwd() / db_path,
                                Path(__file__).parent / db_path,
                            ]
                            for p in possible_paths:
                                if p.exists():
                                    print(f"   找到可能的文件: {p.absolute()}")
                else:
                    print("✅ 余额匹配")
            else:
                print(f"⚠️  未找到用户 @{target_username}")
                print("  请检查用户名是否正确，或提供TG ID")
                
    except Exception as e:
        print(f"❌ 诊断失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_balance_issue()
