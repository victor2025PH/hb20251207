#!/bin/bash
# 查找红包相关日志的脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  红包日志查找工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 时间范围（默认最近1小时）
SINCE="${1:-1 hour ago}"

echo -e "${GREEN}查找时间范围: ${SINCE} 到现在${NC}"
echo -e "${YELLOW}查找关键词: 红包、發送、群組、send、redpacket${NC}"
echo ""

# 查找红包相关日志
journalctl -u hbgm001-backend -u hbgm001-bot \
    --since "$SINCE" \
    --no-pager \
    | grep --color=always -iE "(红包|發送|群組|send|redpacket|claim|領取|chat_id|bot|機器人|✅|❌|⚠️)" \
    | tail -100

echo ""
echo -e "${GREEN}查找完成！${NC}"
echo -e "${YELLOW}提示: 使用 'journalctl -u hbgm001-backend --since '1 hour ago' | grep '红包' | tail -50' 查看更多${NC}"

