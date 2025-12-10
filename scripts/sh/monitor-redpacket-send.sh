#!/bin/bash
# 监控红包发送到群组的日志

echo "=========================================="
echo "监控红包发送日志"
echo "=========================================="
echo ""
echo "正在监控后端 API 日志..."
echo "按 Ctrl+C 停止监控"
echo ""

# 监控后端日志（过滤红包相关）
sudo journalctl -u luckyred-api -f --no-pager | grep -E "chat_id|群組|發送|紅包|minihb2|TelegramError|Exception|錯誤|失敗|成功" --color=always

