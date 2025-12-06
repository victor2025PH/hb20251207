#!/bin/bash
# 強制更新服務器代碼並重新構建

set -e

PROJECT_DIR="/opt/luckyred"

echo "=========================================="
echo "  強制更新服務器代碼"
echo "=========================================="
echo ""

echo "[1/6] 檢查當前狀態..."
cd "$PROJECT_DIR"
echo "當前提交:"
git log --oneline -1
echo ""
echo "檢查文件修改時間:"
stat -c '%y' frontend/src/pages/SendRedPacket.tsx | cut -d' ' -f1-2
echo ""

echo "[2/6] 強制拉取最新代碼..."
git fetch origin
git reset --hard origin/master
echo "✓ 代碼已更新"
echo ""

echo "[3/6] 驗證文件內容..."
if grep -q "✨.*game_rules.*✨" frontend/src/pages/SendRedPacket.tsx; then
    echo "✓ 找到新代碼標記"
else
    echo "✗ 未找到新代碼，可能代碼未正確推送"
    exit 1
fi
echo ""

echo "[4/6] 清除構建緩存..."
cd frontend
rm -rf node_modules/.vite dist
echo "✓ 緩存已清除"
echo ""

echo "[5/6] 重新構建前端..."
npm install --silent
npm run build
echo "✓ 構建完成"
echo ""

echo "[6/6] 重啟服務..."
sudo systemctl restart luckyred-api luckyred-bot luckyred-admin
sudo systemctl reload nginx
echo "✓ 服務已重啟"
echo ""

echo "=========================================="
echo "  更新完成！"
echo "=========================================="
echo ""
echo "檢查構建文件:"
ls -lh dist/assets/*SendRedPacket*.js 2>/dev/null | head -1
echo ""
echo "服務狀態:"
sudo systemctl is-active luckyred-api && echo "API: ✓" || echo "API: ✗"
sudo systemctl is-active luckyred-bot && echo "Bot: ✓" || echo "Bot: ✗"
echo ""
