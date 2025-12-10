#!/bin/bash
# 自动修复语言设置问题的脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  语言设置自动修复工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 检查服务状态
echo -e "${YELLOW}[1] 检查 Bot 服务状态...${NC}"
if sudo systemctl is-active --quiet luckyred-bot; then
    echo -e "${GREEN}✓ Bot 服务正在运行${NC}"
else
    echo -e "${RED}✗ Bot 服务未运行，正在启动...${NC}"
    sudo systemctl start luckyred-bot
    sleep 2
    if sudo systemctl is-active --quiet luckyred-bot; then
        echo -e "${GREEN}✓ Bot 服务已启动${NC}"
    else
        echo -e "${RED}✗ Bot 服务启动失败${NC}"
        sudo systemctl status luckyred-bot --no-pager -l | head -20
        exit 1
    fi
fi
echo ""

# 2. 检查最近的错误
echo -e "${YELLOW}[2] 检查最近的错误...${NC}"
RECENT_ERRORS=$(sudo journalctl -u luckyred-bot --since "5 minutes ago" --no-pager | grep -i "I18N.*error\|language.*failed\|設置語言失敗" | wc -l)

if [ "$RECENT_ERRORS" -gt 0 ]; then
    echo -e "${YELLOW}发现 $RECENT_ERRORS 个语言设置相关的错误${NC}"
    echo "最近的错误:"
    sudo journalctl -u luckyred-bot --since "5 minutes ago" --no-pager | grep -i "I18N.*error\|language.*failed\|設置語言失敗" | tail -5
else
    echo -e "${GREEN}✓ 未发现最近的错误${NC}"
fi
echo ""

# 3. 重启服务（如果需要）
echo -e "${YELLOW}[3] 检查是否需要重启服务...${NC}"
LAST_RESTART=$(sudo systemctl show luckyred-bot --property=ActiveEnterTimestamp --value)
echo "服务最后启动时间: $LAST_RESTART"

# 如果服务运行时间超过 24 小时，建议重启
UPTIME_HOURS=$(systemctl show luckyred-bot --property=ActiveEnterTimestamp --value | xargs -I {} date -d {} +%s 2>/dev/null || echo 0)
CURRENT_TIME=$(date +%s)
if [ "$UPTIME_HOURS" -gt 0 ]; then
    UPTIME_SECONDS=$((CURRENT_TIME - UPTIME_HOURS))
    UPTIME_HOURS=$((UPTIME_SECONDS / 3600))
    if [ "$UPTIME_HOURS" -gt 24 ]; then
        echo -e "${YELLOW}服务已运行超过 24 小时，建议重启${NC}"
        read -p "是否重启服务? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "正在重启服务..."
            sudo systemctl restart luckyred-bot
            sleep 3
            if sudo systemctl is-active --quiet luckyred-bot; then
                echo -e "${GREEN}✓ 服务重启成功${NC}"
            else
                echo -e "${RED}✗ 服务重启失败${NC}"
                exit 1
            fi
        fi
    else
        echo -e "${GREEN}✓ 服务运行时间正常${NC}"
    fi
fi
echo ""

# 4. 显示实时监控命令
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  修复完成${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}建议的监控命令:${NC}"
echo "  1. 实时监控语言设置日志:"
echo "     ${CYAN}sudo journalctl -u luckyred-bot -f --no-pager | grep -i I18N${NC}"
echo ""
echo "  2. 查看最近的错误:"
echo "     ${CYAN}sudo journalctl -u luckyred-bot --since '10 minutes ago' --no-pager | grep -i error${NC}"
echo ""
echo "  3. 运行错误检测:"
echo "     ${CYAN}./scripts/sh/check-language-errors.sh${NC}"
echo ""

