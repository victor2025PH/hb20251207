#!/bin/bash
# 在服务器上拉取最新代码并设置脚本权限

set -e  # 遇到错误立即退出

echo "=========================================="
echo "拉取最新代码并设置脚本权限"
echo "=========================================="

# 项目根目录
PROJECT_ROOT="/opt/luckyred"
cd "$PROJECT_ROOT" || exit 1

echo ""
echo "步骤 1: 拉取最新代码"
echo "=========================================="
git pull origin main

echo ""
echo "步骤 2: 设置脚本执行权限"
echo "=========================================="
chmod +x scripts/sh/*.sh

echo ""
echo "步骤 3: 列出所有脚本文件"
echo "=========================================="
ls -lh scripts/sh/*.sh

echo ""
echo "=========================================="
echo "✅ 完成！"
echo "=========================================="
echo ""
echo "现在可以使用以下命令监控日志："
echo "  /opt/luckyred/scripts/sh/monitor-redpacket-send.sh"
echo ""
echo "或者直接使用："
echo "  sudo journalctl -u luckyred-api -f | grep -E 'chat_id|群組|發送|紅包|minihb2|TelegramError|Exception|錯誤|失敗|成功'"
echo ""

