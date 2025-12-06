#!/usr/bin/env python3
"""
測試 Bot 連接和消息接收
"""
import sys
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent))

from shared.config.settings import get_settings
from telegram import Bot
import asyncio

async def test_bot():
    settings = get_settings()
    print(f"BOT_TOKEN exists: {bool(settings.BOT_TOKEN)}")
    print(f"BOT_TOKEN length: {len(settings.BOT_TOKEN) if settings.BOT_TOKEN else 0}")
    
    if not settings.BOT_TOKEN:
        print("ERROR: BOT_TOKEN is empty!")
        return
    
    try:
        bot = Bot(token=settings.BOT_TOKEN)
        me = await bot.get_me()
        print(f"✓ Bot connected: @{me.username} (ID: {me.id})")
        
        # 測試獲取更新
        updates = await bot.get_updates(limit=1)
        print(f"✓ Can get updates: {len(updates)} pending updates")
        
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bot())
