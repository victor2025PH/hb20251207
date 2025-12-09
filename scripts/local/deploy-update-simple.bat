@echo off
chcp 65001 >nul
title Update Deployment

echo ==========================================
echo   Update Deployment
echo ==========================================
echo.
echo Server: ubuntu@165.154.254.99
echo Project: /home/ubuntu/hbgm001
echo.
echo Please enter password when prompted: Along2025!!!
echo.

ssh ubuntu@165.154.254.99 "cd /home/ubuntu/hbgm001 && git pull origin main && chmod +x deploy/update-deploy.sh && bash deploy/update-deploy.sh"

pause

