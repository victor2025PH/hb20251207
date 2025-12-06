#!/bin/bash
# ============================================
# 停止遠程服務器上的 Bot
# ============================================

echo ""
echo "停止遠程 Bot..."
echo ""

# 停止 systemd 服務
if systemctl is-active --quiet luckyred-bot 2>/dev/null; then
    echo "停止 systemd 服務..."
    sudo systemctl stop luckyred-bot
    echo "✓ Bot 服務已停止"
fi

# 停止所有 Bot 相關進程
BOT_PIDS=$(ps aux | grep -E "bot.*main\.py|python.*bot" | grep -v grep | awk '{print $2}')
if [ -n "$BOT_PIDS" ]; then
    echo "停止 Bot 進程..."
    for PID in $BOT_PIDS; do
        kill -9 $PID 2>/dev/null
        echo "  ✓ 已停止 PID: $PID"
    done
fi

# 等待進程完全停止
sleep 2

echo ""
echo "✓ 遠程 Bot 已完全停止"
echo ""
echo "現在可以在本地啟動 Bot 了"
echo ""
