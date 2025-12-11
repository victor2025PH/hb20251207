#!/bin/bash
# 诊断 502 Bad Gateway 错误

set -e

echo "=========================================="
echo "  诊断 502 Bad Gateway 错误"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查服务状态
echo -e "${YELLOW}[1/6] 检查 systemd 服务状态...${NC}"
if sudo systemctl list-units --all | grep -q "luckyred-api"; then
    SERVICE_STATUS=$(sudo systemctl is-active luckyred-api 2>/dev/null || echo "inactive")
    if [ "$SERVICE_STATUS" = "active" ]; then
        echo -e "${GREEN}✅ 服务正在运行${NC}"
    else
        echo -e "${RED}❌ 服务未运行 (状态: $SERVICE_STATUS)${NC}"
        echo "最近的服务日志:"
        sudo journalctl -u luckyred-api -n 10 --no-pager | tail -5
    fi
else
    echo -e "${RED}❌ 服务文件不存在${NC}"
fi
echo ""

# 2. 检查端口监听
echo -e "${YELLOW}[2/6] 检查端口 8080 是否被监听...${NC}"
if sudo ss -tlnp | grep -q ":8080"; then
    echo -e "${GREEN}✅ 端口 8080 正在监听${NC}"
    sudo ss -tlnp | grep ":8080"
else
    echo -e "${RED}❌ 端口 8080 未被监听${NC}"
fi
echo ""

# 3. 检查进程
echo -e "${YELLOW}[3/6] 检查 API 进程...${NC}"
API_PROCESS=$(ps aux | grep -E "uvicorn.*main:app|uvicorn.*api.main" | grep -v grep || true)
if [ -n "$API_PROCESS" ]; then
    echo -e "${GREEN}✅ 找到 API 进程:${NC}"
    echo "$API_PROCESS"
else
    echo -e "${RED}❌ 没有找到 API 进程${NC}"
fi
echo ""

# 4. 检查服务日志
echo -e "${YELLOW}[4/6] 检查服务日志（最近 20 行）...${NC}"
if sudo systemctl list-units --all | grep -q "luckyred-api"; then
    sudo journalctl -u luckyred-api -n 20 --no-pager | tail -15
else
    echo "服务文件不存在，无法查看日志"
fi
echo ""

# 5. 测试本地连接
echo -e "${YELLOW}[5/6] 测试本地 API 连接...${NC}"
if curl -s -f -m 5 http://127.0.0.1:8080/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 本地 API 连接成功${NC}"
    curl -s http://127.0.0.1:8080/api/v1/health | head -3
else
    echo -e "${RED}❌ 本地 API 连接失败${NC}"
    echo "尝试连接时出错"
fi
echo ""

# 6. 检查 Nginx 错误日志
echo -e "${YELLOW}[6/6] 检查 Nginx 错误日志（最近 10 行）...${NC}"
if [ -f /var/log/nginx/error.log ]; then
    sudo tail -10 /var/log/nginx/error.log | grep -i "502\|upstream\|connect" || echo "没有找到相关错误"
else
    echo "Nginx 错误日志文件不存在"
fi
echo ""

# 总结和建议
echo "=========================================="
echo "  诊断总结"
echo "=========================================="

# 检查所有条件
ISSUES=0

if ! sudo systemctl is-active luckyred-api > /dev/null 2>&1; then
    echo -e "${RED}❌ 后端服务未运行${NC}"
    ISSUES=$((ISSUES + 1))
fi

if ! sudo ss -tlnp | grep -q ":8080"; then
    echo -e "${RED}❌ 端口 8080 未被监听${NC}"
    ISSUES=$((ISSUES + 1))
fi

if ! curl -s -f -m 5 http://127.0.0.1:8080/api/v1/health > /dev/null 2>&1; then
    echo -e "${RED}❌ 本地 API 无法连接${NC}"
    ISSUES=$((ISSUES + 1))
fi

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过，问题可能在 Nginx 配置${NC}"
    echo "建议: 检查 Nginx 配置并重启"
    echo "  sudo nginx -t"
    echo "  sudo systemctl reload nginx"
else
    echo -e "${RED}发现 $ISSUES 个问题${NC}"
    echo ""
    echo "建议修复步骤:"
    echo "  1. 重启后端服务: sudo systemctl restart luckyred-api"
    echo "  2. 如果服务不存在，检查服务文件: sudo cat /etc/systemd/system/luckyred-api.service"
    echo "  3. 查看详细日志: sudo journalctl -u luckyred-api -n 50"
fi

echo ""
echo "=========================================="
