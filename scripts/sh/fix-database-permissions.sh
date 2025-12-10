#!/bin/bash
# 修复数据库权限问题的脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  数据库权限修复工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检测数据库文件位置
echo -e "${CYAN}[1] 检测数据库文件位置...${NC}"
echo "----------------------------------------"

# 检查可能的数据库位置
DB_PATHS=(
    "/opt/luckyred/data/database.db"
    "/opt/luckyred/database.db"
    "/home/ubuntu/hbgm001/data/database.db"
    "/home/ubuntu/hbgm001/database.db"
    "/opt/luckyred/bot/data/database.db"
)

DB_FILE=""
for path in "${DB_PATHS[@]}"; do
    if [ -f "$path" ]; then
        DB_FILE="$path"
        echo -e "${GREEN}✓ 找到数据库文件: $DB_FILE${NC}"
        break
    fi
done

if [ -z "$DB_FILE" ]; then
    echo -e "${YELLOW}⚠ 未找到数据库文件，尝试搜索...${NC}"
    DB_FILE=$(find /opt/luckyred /home/ubuntu/hbgm001 -name "*.db" -type f 2>/dev/null | head -1)
    if [ -n "$DB_FILE" ]; then
        echo -e "${GREEN}✓ 找到数据库文件: $DB_FILE${NC}"
    else
        echo -e "${RED}✗ 未找到数据库文件${NC}"
        echo "请手动指定数据库文件路径"
        exit 1
    fi
fi

# 检查当前权限
echo ""
echo -e "${CYAN}[2] 检查当前权限...${NC}"
echo "----------------------------------------"
ls -la "$DB_FILE"
DB_DIR=$(dirname "$DB_FILE")
echo ""
echo "数据库目录: $DB_DIR"
ls -ld "$DB_DIR"
echo ""

# 获取运行 Bot 服务的用户
echo -e "${CYAN}[3] 检测 Bot 服务运行用户...${NC}"
echo "----------------------------------------"
BOT_USER=$(ps aux | grep "bot/main.py" | grep -v grep | awk '{print $1}' | head -1)
if [ -z "$BOT_USER" ]; then
    BOT_USER="ubuntu"
    echo -e "${YELLOW}⚠ 无法检测 Bot 用户，使用默认用户: $BOT_USER${NC}"
else
    echo -e "${GREEN}✓ Bot 服务运行用户: $BOT_USER${NC}"
fi
echo ""

# 修复权限
echo -e "${CYAN}[4] 修复数据库文件权限...${NC}"
echo "----------------------------------------"

# 修复数据库文件权限
echo "正在修复数据库文件权限..."
sudo chown "$BOT_USER:$BOT_USER" "$DB_FILE"
sudo chmod 664 "$DB_FILE"
echo -e "${GREEN}✓ 数据库文件权限已修复${NC}"

# 修复数据库目录权限
echo "正在修复数据库目录权限..."
sudo chown -R "$BOT_USER:$BOT_USER" "$DB_DIR"
sudo chmod 755 "$DB_DIR"
echo -e "${GREEN}✓ 数据库目录权限已修复${NC}"

# 验证权限
echo ""
echo -e "${CYAN}[5] 验证权限...${NC}"
echo "----------------------------------------"
ls -la "$DB_FILE"
ls -ld "$DB_DIR"
echo ""

# 测试写入权限
echo -e "${CYAN}[6] 测试数据库写入权限...${NC}"
echo "----------------------------------------"
if sudo -u "$BOT_USER" test -w "$DB_FILE"; then
    echo -e "${GREEN}✓ 数据库文件可写${NC}"
else
    echo -e "${RED}✗ 数据库文件仍不可写${NC}"
    echo "尝试使用更宽松的权限..."
    sudo chmod 666 "$DB_FILE"
    if sudo -u "$BOT_USER" test -w "$DB_FILE"; then
        echo -e "${GREEN}✓ 数据库文件现在可写${NC}"
    else
        echo -e "${RED}✗ 权限修复失败，请手动检查${NC}"
        exit 1
    fi
fi
echo ""

# 重启 Bot 服务
echo -e "${CYAN}[7] 重启 Bot 服务...${NC}"
echo "----------------------------------------"
read -p "是否重启 Bot 服务以应用修复? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在重启 Bot 服务..."
    sudo systemctl restart luckyred-bot
    sleep 3
    if sudo systemctl is-active --quiet luckyred-bot; then
        echo -e "${GREEN}✓ Bot 服务重启成功${NC}"
    else
        echo -e "${RED}✗ Bot 服务重启失败${NC}"
        sudo systemctl status luckyred-bot --no-pager -l | head -20
    fi
else
    echo -e "${YELLOW}⚠ 跳过服务重启，请稍后手动重启${NC}"
fi
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  修复完成${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}建议:${NC}"
echo "  1. 测试语言设置功能"
echo "  2. 监控日志: sudo journalctl -u luckyred-bot -f --no-pager | grep -i I18N"
echo "  3. 如果问题仍然存在，检查 SELinux 或其他安全策略"
echo ""

