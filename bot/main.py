"""
Lucky Red (搶紅包) - Telegram Bot 主入口
"""
import sys
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from loguru import logger
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from shared.config.settings import get_settings
from shared.database.connection import init_db
from bot.handlers import start, redpacket, wallet, checkin, admin

settings = get_settings()

# 配置日誌
logger.remove()
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)


async def setup_commands(app: Application):
    """設置 Bot 命令菜單"""
    commands = [
        BotCommand("start", "開始使用"),
        BotCommand("wallet", "我的錢包"),
        BotCommand("send", "發紅包"),
        BotCommand("checkin", "每日簽到"),
        BotCommand("invite", "邀請好友"),
        BotCommand("help", "幫助說明"),
    ]
    await app.bot.set_my_commands(commands)
    logger.info("Bot commands set up")


async def post_init(app: Application):
    """Bot 初始化後執行"""
    await setup_commands(app)
    logger.info(f"🤖 Bot @{app.bot.username} started!")


def main():
    """主函數"""
    logger.info(f"🚀 Starting {settings.APP_NAME} Bot")
    
    # 初始化數據庫
    init_db()
    logger.info("✅ Database initialized")
    
    # 創建 Bot 應用
    app = Application.builder().token(settings.BOT_TOKEN).post_init(post_init).build()
    
    # 註冊處理器
    # 命令處理
    app.add_handler(CommandHandler("start", start.start_command))
    app.add_handler(CommandHandler("help", start.help_command))
    app.add_handler(CommandHandler("wallet", wallet.wallet_command))
    app.add_handler(CommandHandler("send", redpacket.send_command))
    app.add_handler(CommandHandler("checkin", checkin.checkin_command))
    app.add_handler(CommandHandler("invite", start.invite_command))
    
    # 管理員命令
    app.add_handler(CommandHandler("admin", admin.admin_command))
    app.add_handler(CommandHandler("adjust", admin.adjust_command))
    app.add_handler(CommandHandler("broadcast", admin.broadcast_command))
    
    # 回調查詢處理
    app.add_handler(CallbackQueryHandler(redpacket.claim_callback, pattern=r"^claim:"))
    app.add_handler(CallbackQueryHandler(wallet.wallet_callback, pattern=r"^wallet:"))
    app.add_handler(CallbackQueryHandler(checkin.checkin_callback, pattern=r"^checkin:"))
    
    # 啟動 Bot
    logger.info("🤖 Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
