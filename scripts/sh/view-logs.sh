#!/bin/bash
# 查看服务日志的脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  日志查看工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查参数
SERVICE="${1:-all}"
LINES="${2:-100}"
FILTER="${3:-}"

if [ "$SERVICE" == "api" ]; then
    SERVICE_NAME="hbgm001-backend"
elif [ "$SERVICE" == "bot" ]; then
    SERVICE_NAME="hbgm001-bot"
elif [ "$SERVICE" == "all" ]; then
    SERVICE_NAME=""
else
    echo -e "${RED}错误: 无效的服务名称 '$SERVICE'${NC}"
    echo -e "${YELLOW}用法: $0 [api|bot|all] [行数] [过滤关键词]${NC}"
    exit 1
fi
else
    echo -e "${RED}用法: $0 [api|bot|all] [行数] [过滤关键词]${NC}"
    echo "  示例:"
    echo "    $0 api 100              # 查看 API 最近 100 行日志"
    echo "    $0 bot 50 红包          # 查看 Bot 最近 50 行包含'红包'的日志"
    echo "    $0 all 200 错误         # 查看所有服务最近 200 行包含'错误'的日志"
    exit 1
fi

echo -e "${GREEN}查看最近 ${LINES} 行日志${NC}"
if [ -n "$FILTER" ]; then
    echo -e "${YELLOW}过滤关键词: ${FILTER}${NC}"
fi
echo ""

if [ -z "$SERVICE_NAME" ]; then
    # 查看所有服务
    if [ -z "$FILTER" ]; then
        journalctl -u hbgm001-backend -u hbgm001-bot -n "$LINES" --no-pager
    else
        journalctl -u hbgm001-backend -u hbgm001-bot -n "$LINES" --no-pager | grep --color=always -i "$FILTER"
    fi
else
    # 查看单个服务
    if [ -z "$FILTER" ]; then
        journalctl -u "$SERVICE_NAME" -n "$LINES" --no-pager
    else
        journalctl -u "$SERVICE_NAME" -n "$LINES" --no-pager | grep --color=always -i "$FILTER"
    fi
fi

