@echo off
chcp 65001 >nul
echo ========================================
echo 全自动测试并修复所有错误
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

echo [2/5] 修复数据库字段...
cd /d "%~dp0"
python fix_all_db_columns.py
if errorlevel 1 (
    echo ❌ 数据库修复失败
    pause
    exit /b 1
)
echo ✅ 数据库修复完成
echo.

echo [3/5] 验证数据库schema...
python -c "from shared.database.connection import get_db; from sqlalchemy import text; with get_db() as db: result = db.execute(text('PRAGMA table_info(red_packets)')); cols = [row[1] for row in result.fetchall()]; print('red_packets 表的列:', ', '.join(cols)); print('bomb_number 存在:', 'bomb_number' in cols); print('deleted_at 存在:', 'deleted_at' in cols)"
echo.

echo [4/5] 检查代码语法...
python -m py_compile bot/handlers/packets.py bot/handlers/keyboard.py bot/handlers/menu.py bot/utils/i18n.py 2>nul
if errorlevel 1 (
    echo ❌ 代码语法错误
    pause
    exit /b 1
)
echo ✅ 代码语法检查通过
echo.

echo [5/5] 启动Bot进行测试...
echo.
echo ========================================
echo 测试清单
echo ========================================
echo.
echo 请在Telegram中测试以下功能：
echo.
echo 1. /start
echo    ✅ 应该显示内联按钮和底部键盘
echo.
echo 2. 点击"👤 我的"
echo    ✅ 应该显示个人资料（不再出错）
echo.
echo 3. 点击"🧧 紅包" → "➕ 發紅包"
echo    ✅ 应该显示发红包菜单（不再出错）
echo.
echo 4. 点击"🎁 我的紅包"
echo    ✅ 应该显示我的红包列表（不再出错）
echo.
echo 5. 测试所有其他按钮
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
