"""
检查数据库字段是否已添加
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from shared.database.connection import get_db
from sqlalchemy import text

try:
    with get_db() as db:
        # 获取 users 表的所有字段
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]
        
        print("=" * 50)
        print("Users 表的字段:")
        print("=" * 50)
        for col in columns:
            print(f"  - {col}")
        
        print("\n" + "=" * 50)
        print("检查必需字段:")
        print("=" * 50)
        
        required = ['interaction_mode', 'last_interaction_mode', 'seamless_switch_enabled']
        missing = []
        
        for col in required:
            if col in columns:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} (缺失)")
                missing.append(col)
        
        print("\n" + "=" * 50)
        if not missing:
            print("✅ 迁移成功！所有字段已添加")
        else:
            print(f"❌ 迁移失败，缺少字段: {', '.join(missing)}")
            print("\n请运行: python migrations/add_interaction_mode.py")
        print("=" * 50)
        
except Exception as e:
    print(f"❌ 检查失败: {e}")
    import traceback
    traceback.print_exc()
