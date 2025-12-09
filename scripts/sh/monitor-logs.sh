#!/bin/bash
# 监控所有服务日志的脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  日志监控工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查参数
if [ "$1" == "api" ]; then
    SERVICE_NAME="hbgm001-backend"
    echo -e "${GREEN}监控 API 服务日志...${NC}"
elif [ "$1" == "bot" ]; then
    SERVICE_NAME="hbgm001-bot"
    echo -e "${GREEN}监控 Bot 服务日志...${NC}"
elif [ "$1" == "all" ] || [ -z "$1" ]; then
    SERVICE_MODE="all"
    echo -e "${GREEN}监控所有服务日志...${NC}"
else
    echo -e "${RED}用法: $0 [api|bot|all]${NC}"
    echo "  api  - 只监控 API 服务"
    echo "  bot  - 只监控 Bot 服务"
    echo "  all  - 监控所有服务（默认）"
    exit 1
fi

# 过滤关键词（可选）
FILTER="${2:-}"

if [ "$SERVICE_MODE" == "all" ]; then
    # 监控所有服务
    echo -e "${YELLOW}按 Ctrl+C 停止监控${NC}"
    echo ""
    if [ -z "$FILTER" ]; then
        journalctl -u hbgm001-backend -u hbgm001-bot -f --no-pager
    else
        journalctl -u hbgm001-backend -u hbgm001-bot -f --no-pager | grep --color=always -i "$FILTER"
    fi
else
    # 监控单个服务
    echo -e "${YELLOW}按 Ctrl+C 停止监控${NC}"
    echo ""
    if [ -z "$FILTER" ]; then
        journalctl -u "$SERVICE_NAME" -f --no-pager
    else
        journalctl -u "$SERVICE_NAME" -f --no-pager | grep --color=always -i "$FILTER"
    fi
fi

