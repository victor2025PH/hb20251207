@echo off
chcp 65001 >nul
title 全自动修复并启动Bot测试
color 0A

echo.
echo ========================================
echo   全自动修复并启动Bot测试
echo ========================================
echo.

echo [步骤 1/3] 修复数据库字段并验证代码...
python 全自动修复并验证.py
if errorlevel 1 (
    echo.
    echo ❌ 修复失败，请查看上面的错误信息
    pause
    exit /b 1
)
echo.

echo [步骤 2/3] 启动Bot...
echo.
echo ========================================
echo   Bot 正在启动...
echo ========================================
echo.
echo 请在Telegram中测试以下功能：
echo.
echo ✅ 测试清单：
echo   1. 发送 /start
echo   2. 点击 "👤 我的" - 应该不再出错
echo   3. 点击 "🧧 紅包" → "➕ 發紅包" - 应该不再出错
echo   4. 点击 "🎁 我的紅包" - 应该不再出错
echo   5. 点击 "💰 錢包"、"📈 賺取"、"🎮 遊戲" - 所有按钮都应该正常工作
echo   6. 点击 "◀️ 返回主菜單" - 应该返回主菜单（不再打开miniapp）
echo   7. 点击 "🔄 切換模式" - 应该显示模式选择菜单
echo.
echo 如果看到 "Bot @username started!" 说明启动成功
echo 按 Ctrl+C 停止Bot
echo.
echo ========================================
echo.

call "一键启动测试.bat"

echo.
echo ========================================
echo   Bot 已停止
echo ========================================
pause
