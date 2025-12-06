#!/bin/bash

# 完整部署和验证脚本
# 确保代码更新、构建成功、服务正常运行

set -e  # 遇到错误立即退出

echo "🚀 开始完整部署和验证流程..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检测项目目录
if [ -d "/opt/luckyred" ]; then
    PROJECT_DIR="/opt/luckyred"
elif [ -d "$HOME/luckyred" ]; then
    PROJECT_DIR="$HOME/luckyred"
else
    echo -e "${RED}❌ 未找到项目目录${NC}"
    exit 1
fi

cd "$PROJECT_DIR"
echo -e "${GREEN}✓ 项目目录: $PROJECT_DIR${NC}"

# 2. 拉取最新代码
echo ""
echo "📥 拉取最新代码..."
git fetch origin
if git diff HEAD origin/master --quiet; then
    echo -e "${YELLOW}⚠ 代码已是最新版本${NC}"
else
    echo "发现新版本，正在拉取..."
    git stash  # 保存本地更改
    git pull origin master
    echo -e "${GREEN}✓ 代码更新成功${NC}"
fi

# 3. 检查前端构建
echo ""
echo "🔨 检查前端构建..."
cd "$PROJECT_DIR/frontend"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 构建前端
echo "构建前端..."
if npm run build; then
    echo -e "${GREEN}✓ 前端构建成功${NC}"
else
    echo -e "${RED}❌ 前端构建失败${NC}"
    exit 1
fi

# 4. 检查后端依赖
echo ""
echo "🔍 检查后端依赖..."
cd "$PROJECT_DIR/api"

if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
fi

source .venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "安装/更新Python依赖..."
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ 后端依赖检查完成${NC}"
fi

# 5. 检查服务状态
echo ""
echo "🔍 检查服务状态..."

# 检查 API 服务
if systemctl is-active --quiet luckyred-api; then
    echo -e "${GREEN}✓ API 服务运行中${NC}"
else
    echo -e "${YELLOW}⚠ API 服务未运行，正在启动...${NC}"
    sudo systemctl start luckyred-api
    sleep 2
    if systemctl is-active --quiet luckyred-api; then
        echo -e "${GREEN}✓ API 服务已启动${NC}"
    else
        echo -e "${RED}❌ API 服务启动失败${NC}"
        sudo systemctl status luckyred-api --no-pager -l
        exit 1
    fi
fi

# 检查 Nginx
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx 运行中${NC}"
    sudo systemctl reload nginx
    echo -e "${GREEN}✓ Nginx 已重新加载${NC}"
else
    echo -e "${RED}❌ Nginx 未运行${NC}"
    exit 1
fi

# 6. 健康检查
echo ""
echo "🏥 执行健康检查..."

# API 健康检查
API_URL="http://localhost:8080/health"
if curl -s -f "$API_URL" > /dev/null; then
    echo -e "${GREEN}✓ API 健康检查通过${NC}"
    curl -s "$API_URL" | python3 -m json.tool 2>/dev/null || echo "健康检查响应: $(curl -s $API_URL)"
else
    echo -e "${RED}❌ API 健康检查失败${NC}"
    echo "尝试查看日志..."
    sudo journalctl -u luckyred-api -n 20 --no-pager
    exit 1
fi

# 7. 检查端口监听
echo ""
echo "🔌 检查端口监听..."
if netstat -tuln 2>/dev/null | grep -q ":8080"; then
    echo -e "${GREEN}✓ 端口 8080 正在监听${NC}"
elif ss -tuln 2>/dev/null | grep -q ":8080"; then
    echo -e "${GREEN}✓ 端口 8080 正在监听${NC}"
else
    echo -e "${YELLOW}⚠ 端口 8080 未监听（可能正在启动中）${NC}"
fi

# 8. 检查前端文件
echo ""
echo "📁 检查前端文件..."
if [ -d "$PROJECT_DIR/frontend/dist" ] && [ -f "$PROJECT_DIR/frontend/dist/index.html" ]; then
    echo -e "${GREEN}✓ 前端文件存在${NC}"
    echo "前端文件大小: $(du -sh $PROJECT_DIR/frontend/dist | cut -f1)"
else
    echo -e "${RED}❌ 前端文件不存在${NC}"
    exit 1
fi

# 9. 显示服务状态摘要
echo ""
echo "📊 服务状态摘要:"
echo "=================="
systemctl status luckyred-api --no-pager -l | head -10
echo ""
echo "=================="

# 10. 完成
echo ""
echo -e "${GREEN}✅ 部署和验证完成！${NC}"
echo ""
echo "🌐 访问地址: https://mini.usdt2026.cc"
echo "📝 查看日志: sudo journalctl -u luckyred-api -f"
echo "🔄 重启服务: sudo systemctl restart luckyred-api"

