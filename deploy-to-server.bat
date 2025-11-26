@echo off
chcp 65001 >nul
echo ==========================================
echo   部署到服務器 165.154.254.99
echo ==========================================
echo.
echo 密碼: Along2025!!!
echo.
echo 請複製以下命令到 SSH 終端執行:
echo.
echo curl -fsSL https://raw.githubusercontent.com/victor2025PH/hoongbao1127/master/server-full-deploy.sh -o /tmp/deploy.sh ^&^& chmod +x /tmp/deploy.sh ^&^& sudo bash /tmp/deploy.sh
echo.
echo ==========================================
echo.
ssh ubuntu@165.154.254.99
pause

