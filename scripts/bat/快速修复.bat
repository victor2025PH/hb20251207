@echo off
chcp 65001 >nul
echo 快速修复 MiniApp URL
echo.

set SERVER=ubuntu@165.154.254.99

echo 执行修复命令...
ssh %SERVER% "cd /opt/luckyred && grep -v '^MINIAPP_URL=' .env > .env.new && echo 'MINIAPP_URL=https://mini.usdt2026.cc' >> .env.new && mv .env.new .env && grep MINIAPP_URL .env"

echo.
echo 重启 Bot...
ssh %SERVER% "sudo systemctl restart luckyred-bot"

echo.
echo 完成！
pause

