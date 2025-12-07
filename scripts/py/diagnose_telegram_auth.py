#!/usr/bin/env python3
"""
诊断 Telegram 认证问题
检查 BOT_TOKEN 配置、数据库连接、以及最近的认证日志
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from shared.config.settings import get_settings
from loguru import logger
import asyncio
from shared.database.connection import AsyncSessionLocal
from sqlalchemy import text

async def check_bot_token():
    """检查 BOT_TOKEN 配置"""
    print("\n" + "="*60)
    print("1. 检查 BOT_TOKEN 配置")
    print("="*60)
    
    settings = get_settings()
    bot_token = settings.BOT_TOKEN
    
    if not bot_token:
        print("❌ BOT_TOKEN 未配置")
        print("   这会导致 initData hash 验证被跳过（仅开发环境）")
        print("   生产环境应该配置 BOT_TOKEN 以确保安全性")
        return False
    else:
        print(f"✅ BOT_TOKEN 已配置 (长度: {len(bot_token)})")
        print(f"   Token 前缀: {bot_token[:10]}...")
        return True

async def check_database():
    """检查数据库连接"""
    print("\n" + "="*60)
    print("2. 检查数据库连接")
    print("="*60)
    
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"✅ 数据库连接正常")
            print(f"   用户总数: {count}")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

async def check_recent_users():
    """检查最近的 Telegram 用户"""
    print("\n" + "="*60)
    print("3. 检查最近的 Telegram 用户")
    print("="*60)
    
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                text("""
                    SELECT id, tg_id, username, first_name, created_at 
                    FROM users 
                    WHERE tg_id IS NOT NULL 
                    ORDER BY created_at DESC 
                    LIMIT 5
                """)
            )
            users = result.fetchall()
            
            if users:
                print(f"✅ 找到 {len(users)} 个最近的 Telegram 用户:")
                for user in users:
                    print(f"   - ID: {user[0]}, tg_id: {user[1]}, username: {user[2]}, name: {user[3]}, 创建时间: {user[4]}")
            else:
                print("⚠️  没有找到 Telegram 用户")
            return True
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return False

def check_env_file():
    """检查 .env 文件"""
    print("\n" + "="*60)
    print("4. 检查 .env 文件")
    print("="*60)
    
    env_file = project_root / ".env"
    if not env_file.exists():
        print("❌ .env 文件不存在")
        return False
    
    print(f"✅ .env 文件存在: {env_file}")
    
    # 检查 BOT_TOKEN 是否在 .env 中
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'BOT_TOKEN' in content:
            # 检查是否有值
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith('BOT_TOKEN'):
                    if '=' in line and line.split('=', 1)[1].strip():
                        print("✅ BOT_TOKEN 在 .env 中有配置")
                        return True
                    else:
                        print("⚠️  BOT_TOKEN 在 .env 中但值为空")
                        return False
        else:
            print("⚠️  BOT_TOKEN 不在 .env 中")
            return False

async def main():
    """主函数"""
    print("\n" + "="*60)
    print("Telegram 认证诊断工具")
    print("="*60)
    
    results = []
    
    # 检查 BOT_TOKEN
    results.append(await check_bot_token())
    
    # 检查数据库
    results.append(await check_database())
    
    # 检查最近的用户
    results.append(await check_recent_users())
    
    # 检查 .env 文件
    results.append(check_env_file())
    
    # 总结
    print("\n" + "="*60)
    print("诊断总结")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    
    if not results[0]:  # BOT_TOKEN 未配置
        print("\n⚠️  建议:")
        print("   1. 在 .env 文件中配置 BOT_TOKEN")
        print("   2. 重启 API 服务: sudo systemctl restart luckyred-api")
        print("   3. 查看 API 日志: sudo journalctl -u luckyred-api -f")
    
    print("\n📋 下一步:")
    print("   1. 在 Telegram MiniApp 中打开应用")
    print("   2. 查看浏览器控制台（F12）中的日志")
    print("   3. 查看 API 日志: sudo journalctl -u luckyred-api -f --since '5 minutes ago'")
    print("   4. 检查是否有 'Telegram 用戶認證成功' 或相关错误信息")

if __name__ == "__main__":
    asyncio.run(main())

