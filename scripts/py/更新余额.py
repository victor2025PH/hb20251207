"""
更新用户余额（从MiniApp的值同步到Bot数据库）
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from shared.database.connection import get_db
from shared.database.models import User
from decimal import Decimal

def update_balance():
    """更新用户余额"""
    print("=" * 70)
    print("更新用户余额")
    print("=" * 70)
    print()
    
    # 目标用户信息（从图片和日志中获取）
    target_tg_id = 6359371231
    target_username = "aixinwww"
    
    # MiniApp显示的余额
    miniapp_balances = {
        'usdt': 10463.46,
        'ton': 1000.00,
        'stars': 1999,
        'points': 0  # 图片中没有显示，保持原值
    }
    
    try:
        with get_db() as db:
            # 查找用户
            user = db.query(User).filter(User.tg_id == target_tg_id).first()
            
            if not user:
                print(f"❌ 未找到用户 (TG ID: {target_tg_id})")
                print()
                print("数据库中的所有用户：")
                all_users = db.query(User).all()
                for u in all_users:
                    print(f"  - @{u.username or '未设置'} (TG ID: {u.tg_id}, DB ID: {u.id})")
                return
            
            print(f"找到用户: @{user.username or '未设置'} (TG ID: {user.tg_id})")
            print()
            
            # 显示当前余额
            current_usdt = float(user.balance_usdt or 0)
            current_ton = float(user.balance_ton or 0)
            current_stars = user.balance_stars or 0
            current_points = user.balance_points or 0
            
            print("当前余额:")
            print(f"  USDT: {current_usdt:.4f}")
            print(f"  TON: {current_ton:.4f}")
            print(f"  Stars: {current_stars}")
            print(f"  能量: {current_points}")
            print()
            
            # 更新余额
            print("更新为MiniApp的值:")
            print(f"  USDT: {miniapp_balances['usdt']:.4f}")
            print(f"  TON: {miniapp_balances['ton']:.4f}")
            print(f"  Stars: {miniapp_balances['stars']}")
            print()
            
            user.balance_usdt = Decimal(str(miniapp_balances['usdt']))
            user.balance_ton = Decimal(str(miniapp_balances['ton']))
            user.balance_stars = miniapp_balances['stars']
            # points 保持原值，因为图片中没有显示
            
            db.commit()
            
            # 验证
            db.refresh(user)
            updated_usdt = float(user.balance_usdt or 0)
            updated_ton = float(user.balance_ton or 0)
            updated_stars = user.balance_stars or 0
            
            print("✅ 余额已更新！")
            print()
            print("更新后的余额:")
            print(f"  USDT: {updated_usdt:.4f}")
            print(f"  TON: {updated_ton:.4f}")
            print(f"  Stars: {updated_stars}")
            print()
            print("现在Bot应该显示正确的余额了！")
            
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_balance()
