#!/bin/bash
# 快速更新腳本 - 拉取代碼並重啟服務

set -e

APP_DIR="/opt/luckyred"

echo "=== 拉取最新代碼 ==="
cd $APP_DIR
git pull

echo "=== 構建前端 ==="
cd $APP_DIR/frontend
npm install
npm run build

echo "=== 重啟服務 ==="
systemctl restart luckyred-api luckyred-bot luckyred-admin

echo "=== 檢查狀態 ==="
systemctl status luckyred-api --no-pager
systemctl status luckyred-bot --no-pager
systemctl status luckyred-admin --no-pager

echo "=== 更新完成 ==="

