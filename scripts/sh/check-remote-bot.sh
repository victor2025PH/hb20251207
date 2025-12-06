#!/bin/bash
# ============================================
# 檢查遠程服務器上的 Bot 狀態
# ============================================

echo ""
echo "========================================"
echo "  檢查遠程 Bot 狀態"
echo "========================================"
echo ""

# 1. 檢查 systemd 服務
echo "1. 檢查 systemd 服務狀態："
if systemctl is-active --quiet luckyred-bot; then
    echo "  ⚠ Bot 服務正在運行"
    systemctl status luckyred-bot --no-pager -l | head -n 10
    echo ""
    read -p "  是否停止 Bot 服務？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo systemctl stop luckyred-bot
        echo "  ✓ Bot 服務已停止"
    fi
else
    echo "  ✓ Bot 服務未運行"
fi

echo ""

# 2. 檢查 Python 進程
echo "2. 檢查 Python 進程："
BOT_PROCESSES=$(ps aux | grep -E "bot.*main\.py|python.*bot" | grep -v grep)
if [ -n "$BOT_PROCESSES" ]; then
    echo "  ⚠ 發現 Bot 相關進程："
    echo "$BOT_PROCESSES"
    echo ""
    read -p "  是否停止這些進程？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pkill -f "bot.*main.py"
        echo "  ✓ Bot 進程已停止"
    fi
else
    echo "  ✓ 沒有發現 Bot 進程"
fi

echo ""

# 3. 檢查 screen/tmux 會話
echo "3. 檢查 screen/tmux 會話："
SCREEN_SESSIONS=$(screen -ls 2>/dev/null | grep -i bot)
TMUX_SESSIONS=$(tmux ls 2>/dev/null | grep -i bot)

if [ -n "$SCREEN_SESSIONS" ]; then
    echo "  ⚠ 發現 screen 會話："
    echo "$SCREEN_SESSIONS"
fi

if [ -n "$TMUX_SESSIONS" ]; then
    echo "  ⚠ 發現 tmux 會話："
    echo "$TMUX_SESSIONS"
fi

if [ -z "$SCREEN_SESSIONS" ] && [ -z "$TMUX_SESSIONS" ]; then
    echo "  ✓ 沒有發現 screen/tmux 會話"
fi

echo ""
echo "========================================"
echo "  檢查完成"
echo "========================================"
echo ""
