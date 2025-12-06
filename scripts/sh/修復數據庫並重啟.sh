#!/bin/bash
# 修復數據庫並重啟 Bot

echo "=========================================="
echo "  修復數據庫並重啟 Bot"
echo "=========================================="
echo ""

# 1. 檢查並添加 deleted_at 字段
echo "[1/4] 檢查並添加 deleted_at 字段..."
sudo -u postgres psql -d luckyred <<EOF
-- 檢查 red_packets 表
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='red_packets' AND column_name='deleted_at'
    ) THEN
        ALTER TABLE red_packets ADD COLUMN deleted_at TIMESTAMP NULL;
        RAISE NOTICE '✓ red_packets.deleted_at 已添加';
    ELSE
        RAISE NOTICE '✓ red_packets.deleted_at 已存在';
    END IF;
    
    -- 檢查 messages 表
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name='messages' AND column_name='deleted_at'
    ) THEN
        ALTER TABLE messages ADD COLUMN deleted_at TIMESTAMP NULL;
        RAISE NOTICE '✓ messages.deleted_at 已添加';
    ELSE
        RAISE NOTICE '✓ messages.deleted_at 已存在';
    END IF;
END \$\$;
EOF

echo ""

# 2. 驗證字段
echo "[2/4] 驗證字段..."
if sudo -u postgres psql -d luckyred -t -c "SELECT column_name FROM information_schema.columns WHERE table_name='red_packets' AND column_name='deleted_at';" | grep -q deleted_at; then
    echo "  ✓ red_packets.deleted_at 字段存在"
else
    echo "  ✗ red_packets.deleted_at 字段不存在"
fi

echo ""

# 3. 重啟 Bot
echo "[3/4] 重啟 Bot 服務..."
sudo systemctl stop luckyred-bot
sleep 2
sudo systemctl start luckyred-bot
sleep 5

if sudo systemctl is-active --quiet luckyred-bot; then
    echo "  ✓ Bot 服務運行中"
else
    echo "  ✗ Bot 服務未運行"
    sudo systemctl status luckyred-bot --no-pager | head -15
fi

echo ""

# 4. 顯示最近日誌
echo "[4/4] 最近日誌："
sudo journalctl -u luckyred-bot -n 20 --no-pager | tail -10
echo ""

echo "=========================================="
echo "  ✅ 修復完成！"
echo "=========================================="
echo ""
echo "請在 Telegram 中測試："
echo "  1. 點擊「搶紅包」按鈕"
echo "  2. 點擊機器人菜單中的按鈕"
echo ""
echo "查看實時日誌："
echo "  sudo journalctl -u luckyred-bot -f"
echo ""
