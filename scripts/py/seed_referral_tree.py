#!/usr/bin/env python3
"""
生成测试推荐关系树数据
用于在后台管理面板中可视化推荐关系
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import datetime
import random
import string

from shared.database.models import User
from shared.config.settings import get_settings
from shared.database.connection import get_async_db

settings = get_settings()

# 创建数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


def generate_invite_code(length=8):
    """生成邀请码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


async def create_referral_tree(db: AsyncSession, depth=3, width=5, parent_tg_id=None, level=0):
    """递归创建推荐关系树"""
    if level >= depth:
        return []
    
    created_users = []
    
    for i in range(width):
        # 创建用户
        tg_id = random.randint(100000000, 999999999)
        invite_code = generate_invite_code()
        
        user = User(
            tg_id=tg_id,
            username=f"test_user_{tg_id}",
            first_name=f"Test{level}_{i}",
            last_name="User",
            invite_code=invite_code,
            invited_by=parent_tg_id,
            invite_count=0,
            invite_earnings=0,
            level=1,
            xp=0,
            balance_usdt=random.uniform(0, 1000),
            balance_ton=random.uniform(0, 100),
            balance_stars=random.randint(0, 10000),
            balance_points=random.randint(0, 50000),
            created_at=datetime.utcnow(),
        )
        
        db.add(user)
        await db.flush()
        
        created_users.append({
            'id': user.id,
            'tg_id': user.tg_id,
            'username': user.username,
            'invite_code': user.invite_code,
            'level': level,
        })
        
        # 递归创建子用户
        children = await create_referral_tree(db, depth, width, user.tg_id, level + 1)
        created_users.extend(children)
        
        # 更新父用户的邀请数
        if parent_tg_id:
            parent = await db.scalar(select(User).where(User.tg_id == parent_tg_id))
            if parent:
                parent.invite_count = (parent.invite_count or 0) + 1
    
    return created_users


async def main():
    """主函数"""
    print("=" * 60)
    print("生成测试推荐关系树数据")
    print("=" * 60)
    
    async with AsyncSessionLocal() as db:
        try:
            # 创建根用户（KOL）
            root_tg_id = random.randint(100000000, 999999999)
            root_user = User(
                tg_id=root_tg_id,
                username="KOL_Root",
                first_name="KOL",
                last_name="Root",
                invite_code=generate_invite_code(),
                invited_by=None,
                invite_count=0,
                invite_earnings=0,
                level=1,
                xp=0,
                balance_usdt=10000,
                balance_ton=1000,
                balance_stars=50000,
                balance_points=100000,
                created_at=datetime.utcnow(),
            )
            
            db.add(root_user)
            await db.flush()
            
            print(f"✅ 创建根用户（KOL）: {root_user.username} (TG ID: {root_user.tg_id})")
            
            # 创建推荐关系树（3层，每层5个用户）
            print("\n📊 开始创建推荐关系树...")
            created_users = await create_referral_tree(
                db, depth=3, width=5, parent_tg_id=root_tg_id, level=0
            )
            
            # 更新根用户的邀请数
            root_user.invite_count = len(created_users)
            
            await db.commit()
            
            print(f"✅ 成功创建 {len(created_users)} 个测试用户")
            print(f"✅ 根用户邀请数: {root_user.invite_count}")
            
            # 打印树结构预览
            print("\n📋 推荐关系树预览:")
            print(f"  KOL: {root_user.username} (TG: {root_user.tg_id})")
            print(f"    └─ 一级推荐: {len([u for u in created_users if u['level'] == 0])} 人")
            print(f"      └─ 二级推荐: {len([u for u in created_users if u['level'] == 1])} 人")
            print(f"        └─ 三级推荐: {len([u for u in created_users if u['level'] == 2])} 人")
            
            print("\n" + "=" * 60)
            print("✅ 测试数据生成完成！")
            print("=" * 60)
            print(f"\n💡 提示: 在后台管理面板的'邀请管理'页面中，")
            print(f"   可以查看用户 {root_user.tg_id} 的推荐关系树。")
            
        except Exception as e:
            await db.rollback()
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(main())

