@echo off
chcp 65001 >nul
echo ========================================
echo 全自动测试修复脚本
echo ========================================
echo.

echo [1/5] 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)
echo ✅ Python环境正常
echo.

echo [2/5] 检查代码语法...
cd /d "%~dp0"
python -m py_compile bot/handlers/packets.py bot/handlers/keyboard.py bot/handlers/menu.py bot/utils/i18n.py 2>nul
if errorlevel 1 (
    echo ❌ 代码语法错误
    pause
    exit /b 1
)
echo ✅ 代码语法检查通过
echo.

echo [3/5] 检查数据库连接...
python -c "from shared.database.connection import get_db; db = next(get_db()); print('✅ 数据库连接正常')" 2>nul
if errorlevel 1 (
    echo ⚠️  数据库连接检查失败，但继续执行...
)
echo.

echo [4/5] 启动Bot进行测试...
echo.
echo ========================================
echo 测试清单
echo ========================================
echo.
echo 请在Telegram中测试以下功能：
echo.
echo 1. /start
echo    ✅ 应该显示内联按钮和底部键盘
echo    ✅ 图标不重复
echo.
echo 2. 点击"🧧 紅包"
echo    ✅ 应该显示红包菜单（不再出错）
echo.
echo 3. 点击"➕ 發紅包"
echo    ✅ 应该显示发红包菜单（不再出错）
echo.
echo 4. 点击"USDT"
echo    ✅ 应该显示红包类型选择（不再出错）
echo.
echo 5. 点击"👤 我的"
echo    ✅ 应该显示个人资料（不再出错）
echo.
echo 6. 点击"◀️ 返回主菜單"
echo    ✅ 应该返回主菜单（不再打开miniapp）
echo.
echo 7. 点击"🔄 切換模式"
echo    ✅ 应该显示模式选择菜单（图标不重复）
echo.
echo 8. 点击"💰 錢包"、"📈 賺取"、"🎮 遊戲"
echo    ✅ 所有按钮都应该正常工作
echo.
echo ========================================
echo.

echo 正在启动Bot...
echo 如果所有功能正常，按 Ctrl+C 停止Bot
echo.

call "一键启动测试.bat"

echo.
echo ========================================
echo 测试完成
echo ========================================
pause
