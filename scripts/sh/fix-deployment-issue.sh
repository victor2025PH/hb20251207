#!/bin/bash
# 修復部署問題腳本

set -e

PROJECT_DIR="/opt/luckyred"

echo "=========================================="
echo "  修復部署問題"
echo "=========================================="
echo ""

echo "[1/5] 確認代碼版本..."
cd "$PROJECT_DIR"
git fetch origin
git log --oneline -3

echo ""
echo "[2/5] 強制更新代碼..."
git reset --hard origin/master
git clean -fd

echo ""
echo "[3/5] 清除前端構建緩存..."
cd "$PROJECT_DIR/frontend"
rm -rf node_modules/.vite
rm -rf dist

echo ""
echo "[4/5] 重新構建前端..."
npm install
npm run build

echo ""
echo "[5/5] 重啟服務..."
sudo systemctl restart luckyred-api luckyred-bot luckyred-admin
sudo systemctl reload nginx

echo ""
echo "=========================================="
echo "  修復完成！"
echo "=========================================="
echo ""
echo "請清除瀏覽器緩存後重新訪問："
echo "  - Chrome/Edge: Ctrl+Shift+Delete"
echo "  - 或使用無痕模式訪問"
echo ""
