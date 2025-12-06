# ============================================
# Update Bot Menu Button
# ============================================

Write-Host ""
Write-Host "Updating Bot menu button..." -ForegroundColor Cyan
Write-Host ""

cd bot
.venv\Scripts\Activate.ps1

Write-Host "Running menu update script..." -ForegroundColor Yellow
python -c @"
import asyncio
from telegram import Bot, BotCommand
from shared.config.settings import get_settings

async def update_menu():
    settings = get_settings()
    bot = Bot(token=settings.BOT_TOKEN)
    
    try:
        # Update commands
        commands = [
            BotCommand('start', '開始使用'),
            BotCommand('wallet', '我的錢包'),
            BotCommand('send', '發紅包'),
            BotCommand('checkin', '每日簽到'),
            BotCommand('invite', '邀請好友'),
            BotCommand('help', '幫助說明'),
        ]
        await bot.set_my_commands(commands)
        print('✓ Commands updated successfully')
        
        # Try to set menu button
        try:
            from telegram import MenuButtonCommands
            menu_button = MenuButtonCommands()
            await bot.set_chat_menu_button(menu_button=menu_button)
            print('✓ Menu button updated successfully')
        except (ImportError, AttributeError):
            try:
                # Try using dict format
                await bot.set_chat_menu_button(menu_button={'type': 'commands'})
                print('✓ Menu button updated successfully (using dict)')
            except Exception as e2:
                print(f'⚠ Menu button not available: {e2}')
                print('  (Commands are still updated)')
        
    except Exception as e:
        print(f'✗ Error: {e}')
    finally:
        await bot.close()

asyncio.run(update_menu())
"@

deactivate
cd ..

Write-Host ""
Write-Host "Menu button update complete!" -ForegroundColor Green
Write-Host ""
