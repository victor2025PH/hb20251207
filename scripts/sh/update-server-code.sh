#!/bin/bash
# 手动更新服务器代码并重启服务

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_DIR="/home/ubuntu/hbgm001"
SERVICE_NAME="hbgm001-backend"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  更新服务器代码并重启服务${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 进入项目目录
echo -e "${GREEN}[1] 进入项目目录...${NC}"
cd "$PROJECT_DIR" || {
    echo -e "${RED}❌ 无法进入项目目录: $PROJECT_DIR${NC}"
    exit 1
}
echo -e "✅ 当前目录: $(pwd)"
echo ""

# 2. 拉取最新代码
echo -e "${GREEN}[2] 拉取最新代码...${NC}"
git fetch origin main || {
    echo -e "${RED}❌ Git fetch 失败${NC}"
    exit 1
}
git reset --hard origin/main || {
    echo -e "${RED}❌ Git reset 失败${NC}"
    exit 1
}
echo -e "✅ 代码更新成功"
echo ""

# 3. 检查最新提交
echo -e "${GREEN}[3] 检查最新提交...${NC}"
LATEST_COMMIT=$(git log -1 --oneline)
echo -e "✅ 最新提交: $LATEST_COMMIT"
echo ""

# 4. 检查关键文件是否已更新
echo -e "${GREEN}[4] 检查关键文件...${NC}"
if grep -q "\[CREATE_RED_PACKET\]" "$PROJECT_DIR/api/routers/redpackets.py"; then
    echo -e "✅ 新日志标记已存在"
else
    echo -e "${RED}❌ 新日志标记不存在，代码可能未更新${NC}"
    exit 1
fi
echo ""

# 5. 重启服务
echo -e "${GREEN}[5] 重启服务...${NC}"
sudo systemctl restart "$SERVICE_NAME" && echo -e "✅ 服务重启成功" || {
    echo -e "${YELLOW}⚠️ 服务重启失败，请手动检查${NC}"
    exit 1
}
echo ""

# 6. 检查服务状态
echo -e "${GREEN}[6] 检查服务状态...${NC}"
sleep 2
if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "✅ 服务正在运行"
else
    echo -e "${RED}❌ 服务未运行${NC}"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l | head -20
    exit 1
fi
echo ""

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  ✅ 更新完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "现在可以查看日志："
echo -e "  sudo journalctl -u $SERVICE_NAME -f | grep -E 'CREATE_RED_PACKET|SEND_TO_GROUP|SEND_CHECK'"
echo ""

