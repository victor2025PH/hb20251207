"""
Lucky Red - 開始/幫助處理器
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes
from loguru import logger

from shared.config.settings import get_settings
from shared.database.connection import get_db
from shared.database.models import User

settings = get_settings()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /start 命令"""
    user = update.effective_user
    
    # 創建或更新用戶
    with get_db() as db:
        db_user = db.query(User).filter(User.tg_id == user.id).first()
        
        if not db_user:
            # 處理邀請碼
            invite_code = None
            if context.args and len(context.args) > 0:
                invite_code = context.args[0]
            
            db_user = User(
                tg_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
            )
            
            # 處理邀請關係
            if invite_code:
                inviter = db.query(User).filter(User.invite_code == invite_code).first()
                if inviter and inviter.tg_id != user.id:
                    db_user.invited_by = inviter.tg_id
                    inviter.invite_count = (inviter.invite_count or 0) + 1
                    logger.info(f"User {user.id} invited by {inviter.tg_id}")
            
            db.add(db_user)
            db.commit()
            logger.info(f"New user registered: {user.id}")
        else:
            db_user.username = user.username
            db_user.first_name = user.first_name
            db_user.last_name = user.last_name
            db.commit()
    
    # 構建歡迎消息
    welcome_text = f"""
🧧 *歡迎來到 Lucky Red 搶紅包！*

Hi {user.first_name}！

這裡是最有趣的紅包遊戲平台：
• 💰 發紅包給群友
• 🎁 搶紅包贏大獎
• 📅 每日簽到領積分
• 👥 邀請好友得返佣

快來試試吧！👇
"""
    
    # 構建按鈕
    keyboard = [
        [InlineKeyboardButton("🎮 打開遊戲", web_app=WebAppInfo(url=settings.MINIAPP_URL))],
        [
            InlineKeyboardButton("💰 我的錢包", callback_data="wallet:view"),
            InlineKeyboardButton("📅 每日簽到", callback_data="checkin:do"),
        ],
        [
            InlineKeyboardButton("👥 邀請好友", callback_data="invite:share"),
            InlineKeyboardButton("❓ 幫助", callback_data="help:main"),
        ],
    ]
    
    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /help 命令"""
    help_text = """
🧧 *Lucky Red 使用指南*

*基本命令：*
/start - 開始使用
/wallet - 查看錢包餘額
/send - 發送紅包
/checkin - 每日簽到
/invite - 邀請好友

*如何發紅包：*
1. 在群組中輸入 /send
2. 選擇金額和數量
3. 發送紅包給群友

*如何搶紅包：*
點擊群組中的紅包消息即可搶

*每日簽到：*
連續簽到7天可獲得額外獎勵！

*邀請返佣：*
邀請好友可獲得其交易的10%返佣！

有問題？聯繫客服 @support
"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def invite_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /invite 命令"""
    user = update.effective_user
    
    with get_db() as db:
        db_user = db.query(User).filter(User.tg_id == user.id).first()
        
        if not db_user:
            await update.message.reply_text("請先使用 /start 註冊")
            return
        
        # 生成邀請碼
        if not db_user.invite_code:
            import secrets
            db_user.invite_code = secrets.token_urlsafe(8)
            db.commit()
        
        invite_link = f"https://t.me/{settings.BOT_USERNAME}?start={db_user.invite_code}"
    
    invite_text = f"""
👥 *邀請好友*

你的專屬邀請鏈接：
`{invite_link}`

📊 邀請統計：
• 已邀請：{db_user.invite_count or 0} 人
• 累計收益：{float(db_user.invite_earnings or 0):.2f} USDT

💡 邀請規則：
好友通過你的鏈接註冊後，你將獲得其所有交易的 10% 返佣！
"""
    
    keyboard = [
        [InlineKeyboardButton("📤 分享給好友", url=f"https://t.me/share/url?url={invite_link}&text=快來玩搶紅包遊戲！")],
    ]
    
    await update.message.reply_text(
        invite_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

