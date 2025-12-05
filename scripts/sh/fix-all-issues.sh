#!/bin/bash
# 修复所有问题：权限、构建、重启服务
# 在服务器上执行: bash scripts/sh/fix-all-issues.sh

set -e

PROJECT_DIR="/opt/luckyred"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "========================================"
echo "   修复所有问题"
echo "========================================"
echo ""

# 1. 拉取最新代码
log_info "[1/6] 拉取最新代码..."
cd "$PROJECT_DIR"
git pull origin master || log_warn "Git pull失败，继续执行..."

# 2. 修复前端目录权限
log_info "[2/6] 修复前端目录权限..."
sudo chown -R $USER:$USER "$PROJECT_DIR/frontend"
sudo chmod -R 755 "$PROJECT_DIR/frontend"
if [ -d "$PROJECT_DIR/frontend/dist" ]; then
    sudo chown -R $USER:$USER "$PROJECT_DIR/frontend/dist"
    sudo chmod -R 755 "$PROJECT_DIR/frontend/dist"
    log_info "✓ 权限已修复"
else
    log_info "✓ dist目录不存在，将创建"
fi

# 3. 重新构建前端
log_info "[3/6] 重新构建前端..."
cd "$PROJECT_DIR/frontend"
npm run build
if [ $? -eq 0 ]; then
    log_info "✓ 前端构建成功"
else
    log_error "✗ 前端构建失败"
    exit 1
fi

# 4. 检查API依赖
log_info "[4/6] 检查API依赖..."
cd "$PROJECT_DIR/api"
if [ ! -d ".venv" ]; then
    log_warn "⚠ 虚拟环境不存在，创建中..."
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt || log_warn "依赖安装可能有问题"
deactivate

# 5. 重启API服务
log_info "[5/6] 重启API服务..."
sudo systemctl restart luckyred-api
sleep 3
if systemctl is-active --quiet luckyred-api; then
    log_info "✓ API服务已重启"
else
    log_error "✗ API服务启动失败"
    sudo systemctl status luckyred-api
    exit 1
fi

# 6. 测试API
log_info "[6/6] 测试API..."
sleep 2
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/v1/tasks/status || echo "000")
if [ "$API_STATUS" = "401" ] || [ "$API_STATUS" = "200" ]; then
    log_info "✓ API正常 (HTTP $API_STATUS)"
else
    log_warn "⚠ API返回: HTTP $API_STATUS"
fi

echo ""
echo "========================================"
log_info "修复完成！"
echo "========================================"
echo ""
echo "📋 下一步："
echo "  1. 在Telegram中打开MiniApp"
echo "  2. 访问 https://mini.usdt2026.cc/debug 查看调试信息"
echo "  3. 或使用 #debug=1 启用调试面板"
echo ""

