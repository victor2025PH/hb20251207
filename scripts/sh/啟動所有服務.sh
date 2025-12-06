#!/bin/bash
# 啟動服務器上的所有服務

echo "=========================================="
echo "  啟動 LuckyRed 所有服務"
echo "=========================================="
echo ""

# 1. 啟動後端 API
echo "[1/4] 啟動後端 API..."
sudo systemctl start luckyred-api
sleep 2
if sudo systemctl is-active --quiet luckyred-api; then
    echo "  ✓ API 服務已啟動"
else
    echo "  ✗ API 服務啟動失敗"
    sudo systemctl status luckyred-api --no-pager | head -10
fi

# 2. 啟動 Telegram Bot
echo "[2/4] 啟動 Telegram Bot..."
sudo systemctl start luckyred-bot
sleep 2
if sudo systemctl is-active --quiet luckyred-bot; then
    echo "  ✓ Bot 服務已啟動"
else
    echo "  ✗ Bot 服務啟動失敗"
    sudo systemctl status luckyred-bot --no-pager | head -10
fi

# 3. 啟動 Nginx
echo "[3/4] 檢查 Nginx..."
if sudo systemctl is-active --quiet nginx; then
    echo "  ✓ Nginx 已在運行"
else
    echo "  → 啟動 Nginx..."
    sudo systemctl start nginx
    sleep 1
    if sudo systemctl is-active --quiet nginx; then
        echo "  ✓ Nginx 已啟動"
    else
        echo "  ✗ Nginx 啟動失敗"
    fi
fi

# 4. 設置開機自啟
echo "[4/4] 設置開機自啟..."
sudo systemctl enable luckyred-api luckyred-bot nginx
echo "  ✓ 服務已設置為開機自啟"

echo ""
echo "=========================================="
echo "  服務狀態"
echo "=========================================="
echo ""
echo "API 服務:"
sudo systemctl is-active luckyred-api && echo "  ✓ 運行中" || echo "  ✗ 未運行"
echo ""
echo "Bot 服務:"
sudo systemctl is-active luckyred-bot && echo "  ✓ 運行中" || echo "  ✗ 未運行"
echo ""
echo "Nginx:"
sudo systemctl is-active nginx && echo "  ✓ 運行中" || echo "  ✗ 未運行"
echo ""

# 顯示進程
echo "運行中的進程:"
ps aux | grep -E 'python.*api|python.*bot|uvicorn|nginx' | grep -v grep | head -5
echo ""

# 顯示最近日誌
echo "API 最近日誌:"
sudo journalctl -u luckyred-api -n 5 --no-pager | tail -3
echo ""
echo "Bot 最近日誌:"
sudo journalctl -u luckyred-bot -n 5 --no-pager | tail -3
echo ""

echo "=========================================="
echo "  ✅ 啟動完成！"
echo "=========================================="
echo ""
echo "查看完整狀態:"
echo "  sudo systemctl status luckyred-api luckyred-bot"
echo ""
echo "查看實時日誌:"
echo "  sudo journalctl -u luckyred-api -f"
echo "  sudo journalctl -u luckyred-bot -f"
echo ""
