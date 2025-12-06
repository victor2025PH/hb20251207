#!/bin/bash
# 診斷並修復 Bot 問題

echo "=========================================="
echo "  診斷並修復 Bot 問題"
echo "=========================================="
echo ""

cd /opt/luckyred

# 1. 檢查文件
echo "[1/6] 檢查關鍵文件..."
if [ -f "bot/handlers/keyboard.py" ]; then
    echo "  ✓ keyboard.py 存在 ($(wc -l < bot/handlers/keyboard.py) 行)"
else
    echo "  ✗ keyboard.py 缺失！"
fi

if [ -f "bot/handlers/menu.py" ]; then
    echo "  ✓ menu.py 存在 ($(wc -l < bot/handlers/menu.py) 行)"
else
    echo "  ✗ menu.py 缺失！"
fi

echo ""
echo "所有 handlers 文件："
ls -1 bot/handlers/*.py | wc -l | xargs echo "  共"
ls -1 bot/handlers/*.py
echo ""

# 2. 更新 Git
echo "[2/6] 更新 Git 代碼..."
git fetch origin
git reset --hard origin/master
echo "  ✓ Git 已更新到最新版本"
echo ""

# 3. 檢查導入
echo "[3/6] 檢查 Python 導入..."
python3 -c "import sys; sys.path.insert(0, '.'); from bot.handlers import keyboard, menu; print('  ✓ keyboard 和 menu 可以導入')" 2>&1
echo ""

# 4. 檢查語法
echo "[4/6] 檢查語法..."
python3 -m py_compile bot/main.py 2>&1 && echo "  ✓ 語法檢查通過" || echo "  ✗ 語法錯誤"
echo ""

# 5. 停止並重啟 Bot
echo "[5/6] 重啟 Bot 服務..."
sudo systemctl stop luckyred-bot
sleep 2
sudo systemctl start luckyred-bot
sleep 5

if sudo systemctl is-active --quiet luckyred-bot; then
    echo "  ✓ Bot 服務運行中"
else
    echo "  ✗ Bot 服務未運行"
    echo "  錯誤信息："
    sudo systemctl status luckyred-bot --no-pager | head -15
fi
echo ""

# 6. 顯示最近日誌
echo "[6/6] 最近日誌："
sudo journalctl -u luckyred-bot -n 20 --no-pager | tail -10
echo ""

echo "=========================================="
echo "  ✅ 診斷完成！"
echo "=========================================="
echo ""
echo "請在 Telegram 中測試按鈕，然後查看實時日誌："
echo "  sudo journalctl -u luckyred-bot -f"
echo ""
