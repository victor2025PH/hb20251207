@echo off
chcp 65001 >nul
title 部署程序到服务器

REM ==========================================
REM 部署脚本 - 在本地 Windows 执行
REM 自动连接服务器并执行部署
REM ==========================================

REM 服务器配置
set SERVER_HOST=165.154.254.99
set SERVER_USER=ubuntu
set SERVER_PASSWORD=Along2025!!!
set PROJECT_DIR=/home/ubuntu/hbgm001

echo ==========================================
echo   部署程序到服务器
echo ==========================================
echo.
echo [信息] 服务器: %SERVER_USER%@%SERVER_HOST%
echo [信息] 项目目录: %PROJECT_DIR%
echo.

REM 检查 plink 是否可用
where plink >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 plink.exe
    echo.
    echo 请先安装 PuTTY:
    echo https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html
    echo.
    pause
    exit /b 1
)

echo [步骤 1] 检查服务器连接...
echo y | plink -ssh -pw %SERVER_PASSWORD% %SERVER_USER%@%SERVER_HOST% "echo '连接成功'" >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 无法连接到服务器
    pause
    exit /b 1
)
echo [成功] 服务器连接正常
echo.

echo [步骤 2] 检查项目目录是否存在...
echo y | plink -ssh -pw %SERVER_PASSWORD% %SERVER_USER%@%SERVER_HOST% "test -d %PROJECT_DIR% && echo '存在' || echo '不存在'"
echo.

echo [步骤 3] 执行部署...
echo.
echo 请选择部署方式:
echo   1. 首次部署（完整安装）
echo   2. 更新部署（更新代码）
echo.
set /p choice=请输入选择 (1 或 2): 

if "%choice%"=="1" (
    echo.
    echo [执行] 首次部署...
    echo y | plink -ssh -pw %SERVER_PASSWORD% %SERVER_USER%@%SERVER_HOST% "cd /tmp && curl -o deploy.sh https://raw.githubusercontent.com/victor2025PH/hb20251207/main/deploy/首次部署.sh 2>nul || wget -O deploy.sh https://raw.githubusercontent.com/victor2025PH/hb20251207/main/deploy/首次部署.sh 2>nul || (echo '请手动上传部署脚本' && exit 1)" && echo y | plink -ssh -pw %SERVER_PASSWORD% %SERVER_USER%@%SERVER_HOST% "chmod +x /tmp/deploy.sh && bash /tmp/deploy.sh"
) else if "%choice%"=="2" (
    echo.
    echo [执行] 更新部署...
    echo y | plink -ssh -pw %SERVER_PASSWORD% %SERVER_USER%@%SERVER_HOST% "cd %PROJECT_DIR% && git pull origin main && source .venv/bin/activate && pip install -r requirements.txt && sudo systemctl restart hbgm001-backend && sleep 2 && sudo systemctl status hbgm001-backend --no-pager"
) else (
    echo [错误] 无效的选择
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   部署完成！
echo ==========================================
echo.
pause

