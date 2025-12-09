@echo off
chcp 65001 >nul
title Update Deployment

set SERVER=ubuntu@165.154.254.99
set PASSWORD=Along2025!!!
set PROJECT_DIR=/home/ubuntu/hbgm001

echo Connecting to server...
echo y | plink -ssh -pw %PASSWORD% %SERVER% "cd %PROJECT_DIR% && git pull origin main && chmod +x deploy/update-deploy.sh && bash deploy/update-deploy.sh"

pause

