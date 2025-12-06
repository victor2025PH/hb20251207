@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   Lucky Red - 检查Bot状态
echo ========================================
echo.

cd /d C:\hbgm001

echo [检查 1/3] 检查Python进程...
echo.
tasklist | findstr python.exe
if errorlevel 1 (
    echo ❌ 未找到Python进程，Bot可能未运行
) else (
    echo ✅ 找到Python进程
)
echo.

echo [检查 2/3] 检查端口占用...
echo.
netstat -ano | findstr :8080
if errorlevel 1 (
    echo ❌ 端口8080未被占用，API服务器可能未运行
) else (
    echo ✅ 端口8080已被占用（API服务器可能正在运行）
)
echo.

echo [检查 3/3] 检查.env文件...
echo.
if not exist .env (
    echo ❌ .env 文件不存在
    echo 请先创建 .env 文件并配置 BOT_TOKEN
) else (
    echo ✅ .env 文件存在
    echo.
    echo 检查BOT_TOKEN配置...
    findstr /C:"BOT_TOKEN" .env >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  .env 文件中未找到 BOT_TOKEN
    ) else (
        echo ✅ 找到 BOT_TOKEN 配置
    )
)
echo.

echo ========================================
echo   检查完成
echo ========================================
echo.
echo 如果Bot未运行，请执行：
echo   .\一键启动测试.bat
echo   或
echo   .\全自动启动测试.bat
echo.
pause
