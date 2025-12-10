#!/bin/bash
# 检查 API 服务日志的多种方法

echo "=========================================="
echo "检查 API 服务日志"
echo "=========================================="
echo ""

# 1. 检查服务状态
echo "步骤 1: 检查服务状态"
echo "=========================================="
sudo systemctl status luckyred-api --no-pager -l | head -20
echo ""

# 2. 检查服务是否存在
echo "步骤 2: 检查服务是否存在"
echo "=========================================="
if systemctl list-unit-files | grep -q "luckyred-api.service"; then
    echo "✅ 服务存在"
else
    echo "❌ 服务不存在，可能服务名不对"
    echo ""
    echo "可用的服务："
    systemctl list-unit-files | grep -E "luckyred|hbgm001" || echo "未找到相关服务"
fi
echo ""

# 3. 尝试不同的服务名
echo "步骤 3: 尝试查找所有相关服务"
echo "=========================================="
echo "查找包含 'luckyred' 或 'api' 的服务："
systemctl list-units --type=service --all | grep -E "luckyred|api" || echo "未找到"
echo ""

# 4. 检查进程
echo "步骤 4: 检查 API 进程"
echo "=========================================="
ps aux | grep -E "uvicorn|main:app" | grep -v grep || echo "未找到 API 进程"
echo ""

# 5. 检查日志文件（如果存在）
echo "步骤 5: 检查日志文件"
echo "=========================================="
if [ -d "/opt/luckyred/api/logs" ]; then
    echo "找到日志目录，最新日志："
    ls -lht /opt/luckyred/api/logs/ | head -5
elif [ -f "/opt/luckyred/api/app.log" ]; then
    echo "找到日志文件："
    tail -20 /opt/luckyred/api/app.log
else
    echo "未找到日志文件"
fi
echo ""

# 6. 尝试使用 SyslogIdentifier 查找
echo "步骤 6: 使用 SyslogIdentifier 查找日志"
echo "=========================================="
sudo journalctl _SYSTEMD_UNIT=luckyred-api.service -n 20 --no-pager || echo "未找到日志"
echo ""

# 7. 查看所有 systemd 日志（最近）
echo "步骤 7: 查看所有 systemd 日志（最近 50 行）"
echo "=========================================="
sudo journalctl -n 50 --no-pager | grep -iE "luckyred|api|uvicorn" | tail -20 || echo "未找到相关日志"
echo ""

echo "=========================================="
echo "检查完成"
echo "=========================================="

