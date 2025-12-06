"""
直接运行数据库迁移（带详细输出）
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("=" * 60)
print("数据库迁移 - 添加交互模式字段")
print("=" * 60)
print()

try:
    from migrations.add_interaction_mode import upgrade
    
    print("正在运行迁移...")
    print()
    upgrade()
    print()
    print("=" * 60)
    print("迁移完成！")
    print("=" * 60)
    print()
    
    # 验证字段
    print("正在验证字段...")
    print()
    from 检查数据库字段 import *
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
