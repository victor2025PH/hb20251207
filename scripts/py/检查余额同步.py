"""
检查Bot和MiniApp的余额是否同步
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from shared.database.connection import get_db
from shared.database.models import User
from shared.config.settings import get_settings

settings = get_settings()

def check_balance_sync():
    """检查余额同步情况"""
    print("=" * 70)
    print("检查余额同步")
    print("=" * 70)
    print()
    
    try:
        with get_db() as db:
            # 获取所有用户
            users = db.query(User).all()
            
            if not users:
                print("⚠️  数据库中没有用户")
                return
            
            print(f"找到 {len(users)} 个用户")
            print()
            
            for user in users:
                print(f"用户: @{user.username or '未设置'} (ID: {user.tg_id})")
                print(f"  数据库ID: {user.id}")
                
                # 读取余额（确保在会话内）
                usdt = float(user.balance_usdt or 0)
                ton = float(user.balance_ton or 0)
                stars = user.balance_stars or 0
                points = user.balance_points or 0
                
                print(f"  USDT: {usdt:.4f}")
                print(f"  TON: {ton:.4f}")
                print(f"  Stars: {stars}")
                print(f"  能量: {points}")
                
                if usdt == 0 and ton == 0 and stars == 0:
                    print("  ⚠️  所有余额为0")
                else:
                    print("  ✅ 有余额")
                
                print()
            
            # 检查特定用户（如果提供了）
            print("=" * 70)
            print("检查特定用户（从图片看是 @aixinwww）")
            print("=" * 70)
            print()
            
            target_user = db.query(User).filter(User.username == "aixinwww").first()
            if target_user:
                print(f"找到目标用户: @{target_user.username} (TG ID: {target_user.tg_id})")
                
                # 重新查询确保数据最新
                fresh_user = db.query(User).filter(User.id == target_user.id).first()
                usdt = float(fresh_user.balance_usdt or 0)
                ton = float(fresh_user.balance_ton or 0)
                stars = fresh_user.balance_stars or 0
                points = fresh_user.balance_points or 0
                
                print(f"  USDT: {usdt:.4f} (MiniApp显示: 10463.46)")
                print(f"  TON: {ton:.4f} (MiniApp显示: 1000.00)")
                print(f"  Stars: {stars} (MiniApp显示: 1999)")
                
                if usdt < 10000 or ton < 1000 or stars < 1000:
                    print()
                    print("❌ 余额不匹配！")
                    print("  可能的原因：")
                    print("  1. Bot和MiniApp使用不同的数据库")
                    print("  2. 数据库连接配置不同")
                    print("  3. 用户ID不匹配")
                    print()
                    print("建议检查：")
                    print("  1. .env 文件中的 DATABASE_URL")
                    print("  2. API 的数据库配置")
                    print("  3. 确认Bot和API使用同一个数据库")
                else:
                    print()
                    print("✅ 余额匹配")
            else:
                print("⚠️  未找到用户 @aixinwww")
                print("  请检查用户名是否正确")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_balance_sync()
