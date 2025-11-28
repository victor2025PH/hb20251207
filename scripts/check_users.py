#!/usr/bin/env python3
"""
检查数据库中的用户数据
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from shared.database.connection import AsyncSessionLocal
from shared.database.models import User
from sqlalchemy import select, func

async def check_users():
    async with AsyncSessionLocal() as db:
        # 获取总用户数
        total_result = await db.execute(select(func.count(User.id)))
        total = total_result.scalar() or 0
        print(f"总用户数: {total}")
        print()
        
        if total == 0:
            print("❌ 数据库中没有用户数据！")
            print("   可能的原因：")
            print("   1. miniapp 用户还没有登录/注册")
            print("   2. 用户创建逻辑有问题")
            print("   3. 数据库连接有问题")
            return
        
        # 获取前10个用户
        users_result = await db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(10)
        )
        users = users_result.scalars().all()
        
        print("最近10个用户：")
        print("-" * 80)
        for u in users:
            print(f"ID: {u.id:4d} | TG_ID: {u.tg_id:12d} | Username: {u.username or '(无)':20s} | Name: {u.first_name or '(无)':15s} | Created: {u.created_at}")
        print("-" * 80)
        print()
        
        # 测试搜索功能
        print("测试搜索功能：")
        test_searches = []
        if users:
            # 测试搜索第一个用户的 tg_id
            if users[0].tg_id:
                test_searches.append(str(users[0].tg_id))
            # 测试搜索第一个用户的 username
            if users[0].username:
                test_searches.append(users[0].username)
            # 测试搜索第一个用户的 first_name
            if users[0].first_name:
                test_searches.append(users[0].first_name)
        
        for search_term in test_searches[:3]:
            query = select(User)
            try:
                search_int = int(search_term)
                from sqlalchemy import or_
                query = query.where(or_(
                    User.tg_id == search_int,
                    User.username.ilike(f"%{search_term}%"),
                    User.first_name.ilike(f"%{search_term}%")
                ))
            except ValueError:
                from sqlalchemy import or_
                query = query.where(or_(
                    User.username.ilike(f"%{search_term}%"),
                    User.first_name.ilike(f"%{search_term}%")
                ))
            
            result = await db.execute(query)
            found_users = result.scalars().all()
            print(f"  搜索 '{search_term}': 找到 {len(found_users)} 个用户")
            if found_users:
                for u in found_users[:3]:
                    print(f"    - ID: {u.id}, TG_ID: {u.tg_id}, Username: {u.username}, Name: {u.first_name}")

if __name__ == "__main__":
    asyncio.run(check_users())

