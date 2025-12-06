"""检查数据库schema"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from shared.database.connection import sync_engine
from sqlalchemy import inspect, text

inspector = inspect(sync_engine)

try:
    # 检查表是否存在
    tables = inspector.get_table_names()
    print(f"数据库中的表: {', '.join(tables)}")
    
    if 'red_packets' in tables:
        # 获取列信息
        columns = inspector.get_columns('red_packets')
        column_names = [col['name'] for col in columns]
        print(f"\nred_packets 表的列 ({len(column_names)} 个):")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        print(f"\nbomb_number 字段存在: {'bomb_number' in column_names}")
        
        if 'bomb_number' not in column_names:
            print("\n需要运行迁移: python migrations/add_bomb_number.py")
    else:
        print("\nred_packets 表不存在！")
        
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
