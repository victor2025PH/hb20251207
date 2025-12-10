#!/bin/bash
# 检测语言设置错误的脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  语言设置错误检测工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Bot 服务中与语言设置相关的错误
echo -e "${CYAN}[1] 检查 Bot 服务中的语言设置错误${NC}"
echo "----------------------------------------"
LANGUAGE_ERRORS=$(sudo journalctl -u luckyred-bot --since "1 hour ago" --no-pager | grep -i "I18N\|language\|設置語言\|update.*language" | tail -20)

if [ -z "$LANGUAGE_ERRORS" ]; then
    echo -e "${GREEN}✓ 未发现语言设置相关的错误${NC}"
else
    echo -e "${RED}发现语言设置相关的日志:${NC}"
    echo "$LANGUAGE_ERRORS"
fi
echo ""

# 检查最近的错误日志
echo -e "${CYAN}[2] 检查最近的错误日志${NC}"
echo "----------------------------------------"
RECENT_ERRORS=$(sudo journalctl -u luckyred-bot --since "10 minutes ago" --no-pager | grep -i "error\|exception\|failed\|traceback" | tail -10)

if [ -z "$RECENT_ERRORS" ]; then
    echo -e "${GREEN}✓ 最近 10 分钟内未发现错误${NC}"
else
    echo -e "${YELLOW}最近的错误:${NC}"
    echo "$RECENT_ERRORS"
fi
echo ""

# 检查数据库连接
echo -e "${CYAN}[3] 检查数据库连接相关错误${NC}"
echo "----------------------------------------"
DB_ERRORS=$(sudo journalctl -u luckyred-bot --since "1 hour ago" --no-pager | grep -i "database\|db\|connection\|sqlalchemy" | grep -i "error\|failed\|exception" | tail -10)

if [ -z "$DB_ERRORS" ]; then
    echo -e "${GREEN}✓ 未发现数据库连接错误${NC}"
else
    echo -e "${RED}发现数据库相关错误:${NC}"
    echo "$DB_ERRORS"
fi
echo ""

# 显示详细的 I18N 日志
echo -e "${CYAN}[4] 显示详细的 I18N 日志（最近 50 条）${NC}"
echo "----------------------------------------"
sudo journalctl -u luckyred-bot --since "1 hour ago" --no-pager | grep -i "\[I18N\]\|\[SETUP\]\|\[LANGUAGE\]" | tail -50
echo ""

# 检查服务状态
echo -e "${CYAN}[5] Bot 服务状态${NC}"
echo "----------------------------------------"
sudo systemctl status luckyred-bot --no-pager -l | head -15
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  检测完成${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}提示:${NC}"
echo "  实时监控语言设置日志: sudo journalctl -u luckyred-bot -f --no-pager | grep -i I18N"
echo "  查看所有 Bot 日志: sudo journalctl -u luckyred-bot -n 100 --no-pager"
echo ""

