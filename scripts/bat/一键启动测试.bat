@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Lucky Red Bot - 一键启动测试
echo ========================================
echo.
echo 正在启动全自动测试环境...
echo.

cd /d C:\hbgm001

REM 在新窗口中启动全自动脚本
start "Lucky Red Bot - 测试环境" cmd /k "全自动启动测试.bat"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo Bot 已在新窗口中启动
echo.
echo 请查看新打开的窗口：
echo   • 窗口标题：Lucky Red Bot - 测试环境
echo   • 查看是否有 "Bot @username started!" 消息
echo   • 如果有错误，会显示在该窗口中
echo.
echo 然后在 Telegram 中：
echo   1. 与 bot 私聊
echo   2. 发送 /start 命令
echo   3. 按照测试指南进行测试
echo.
echo 测试指南：本地测试指南-三合一切换.md
echo.
pause
