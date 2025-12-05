#!/usr/bin/env python3
"""
任务红包系统API测试脚本
在服务器上执行: python3 scripts/py/test_tasks_api.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import asyncio
from sqlalchemy import select, func
from shared.database.connection import get_db_session
from shared.database.models import (
    User, RedPacket, TaskCompletion, DailyTask,
    RedPacketVisibility, RedPacketSource
)

async def test_database():
    """测试数据库"""
    print("=" * 50)
    print("数据库测试")
    print("=" * 50)
    
    async for db in get_db_session():
        try:
            # 检查表是否存在
            from sqlalchemy import inspect
            inspector = inspect(db.bind.sync_engine)
            tables = inspector.get_table_names()
            
            required_tables = ['task_completions', 'daily_tasks', 'red_packets', 'users']
            print("\n📊 检查数据库表:")
            for table in required_tables:
                if table in tables:
                    print(f"  ✓ {table} 表存在")
                else:
                    print(f"  ✗ {table} 表不存在")
            
            # 检查字段
            print("\n📋 检查字段:")
            if 'red_packets' in tables:
                columns = [col['name'] for col in inspector.get_columns('red_packets')]
                fields = ['visibility', 'source_type', 'task_type', 'task_requirement']
                for field in fields:
                    if field in columns:
                        print(f"  ✓ red_packets.{field} 存在")
                    else:
                        print(f"  ✗ red_packets.{field} 不存在")
            
            if 'users' in tables:
                columns = [col['name'] for col in inspector.get_columns('users')]
                if 'share_count' in columns:
                    print(f"  ✓ users.share_count 存在")
                else:
                    print(f"  ✗ users.share_count 不存在")
            
            # 统计数据
            print("\n📈 数据统计:")
            user_count = await db.execute(select(func.count(User.id)))
            print(f"  用户总数: {user_count.scalar()}")
            
            packet_count = await db.execute(select(func.count(RedPacket.id)))
            print(f"  红包总数: {packet_count.scalar()}")
            
            task_count = await db.execute(select(func.count(TaskCompletion.id)))
            print(f"  任务完成记录: {task_count.scalar()}")
            
            # 检查任务红包
            task_packet_count = await db.execute(
                select(func.count(RedPacket.id)).where(
                    RedPacket.source_type == RedPacketSource.TASK
                )
            )
            print(f"  任务红包数: {task_packet_count.scalar()}")
            
            print("\n✅ 数据库测试通过")
            return True
            
        except Exception as e:
            print(f"\n❌ 数据库测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

async def test_models():
    """测试模型"""
    print("\n" + "=" * 50)
    print("模型测试")
    print("=" * 50)
    
    try:
        # 测试枚举
        print("\n🔍 检查枚举:")
        print(f"  RedPacketVisibility: {[v.value for v in RedPacketVisibility]}")
        print(f"  RedPacketSource: {[s.value for s in RedPacketSource]}")
        
        # 测试导入
        from api.routers.tasks import DAILY_TASKS, ACHIEVEMENT_TASKS
        print(f"\n📋 任务配置:")
        print(f"  每日任务: {len(DAILY_TASKS)} 个")
        for task_type, config in DAILY_TASKS.items():
            print(f"    - {task_type}: {config['task_name']}")
        
        print(f"  成就任务: {len(ACHIEVEMENT_TASKS)} 个")
        for task_type, config in ACHIEVEMENT_TASKS.items():
            print(f"    - {task_type}: {config['task_name']}")
        
        print("\n✅ 模型测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("\n🧪 任务红包系统 - API测试")
    print("=" * 50)
    
    results = []
    
    # 测试数据库
    results.append(await test_database())
    
    # 测试模型
    results.append(await test_models())
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    if all(results):
        print("✅ 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

