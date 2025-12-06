@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   验证数据库迁移是否成功
echo ========================================
echo.

cd /d C:\hbgm001

echo 正在检查数据库字段...
echo.

python -c "from shared.database.connection import get_db; from sqlalchemy import text; db = next(get_db()); result = db.execute(text('PRAGMA table_info(users)')); columns = [row[1] for row in result.fetchall()]; print('Users 表的字段:'); [print(f'  - {col}') for col in columns]; print(''); required = ['interaction_mode', 'last_interaction_mode', 'seamless_switch_enabled']; missing = [col for col in required if col not in columns]; print('检查必需字段:'); [print(f'  ✅ {col}') for col in required if col in columns]; [print(f'  ❌ {col} (缺失)') for col in missing]; print(''); print('✅ 迁移成功！' if not missing else '❌ 迁移失败，缺少字段')"

echo.
pause
