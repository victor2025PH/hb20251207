@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   三合一切换方案 - 快速测试脚本
echo ========================================
echo.

cd /d C:\hbgm001

echo [1/3] 检查数据库迁移...
python migrations/add_interaction_mode.py
if errorlevel 1 (
    echo ❌ 数据库迁移失败
    pause
    exit /b 1
)
echo ✅ 数据库迁移成功
echo.

echo [2/3] 检查环境配置...
if not exist .env (
    echo ❌ .env 文件不存在
    pause
    exit /b 1
)
echo ✅ .env 文件存在
echo.

echo [3/3] 检查 Bot 代码...
if not exist "bot\keyboards\unified.py" (
    echo ❌ 统一键盘生成器不存在
    pause
    exit /b 1
)
if not exist "bot\handlers\mode_switch.py" (
    echo ❌ 模式切换处理器不存在
    pause
    exit /b 1
)
if not exist "bot\utils\mode_helper.py" (
    echo ❌ 模式辅助函数不存在
    pause
    exit /b 1
)
echo ✅ 所有文件存在
echo.

echo ========================================
echo   准备完成！
echo ========================================
echo.
echo 下一步：
echo   1. 启动 Bot（运行：启动机器人-详细.bat）
echo   2. 在 Telegram 中与 bot 私聊
echo   3. 发送 /start 命令
echo   4. 按照测试指南进行测试
echo.
echo 测试指南：本地测试指南-三合一切换.md
echo.
pause
