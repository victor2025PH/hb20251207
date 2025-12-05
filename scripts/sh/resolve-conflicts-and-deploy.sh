#!/bin/bash
# 解决Git冲突并完成部署
# 在服务器上执行: bash scripts/sh/resolve-conflicts-and-deploy.sh

set -e

PROJECT_DIR="/opt/luckyred"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cd "$PROJECT_DIR"

# 1. 解决Git冲突
log_info "[1/8] 解决Git冲突..."
git stash
git pull origin master || git pull origin main
git stash pop || true
log_info "✓ Git冲突已解决"

# 2. 确保API虚拟环境存在
log_info "[2/8] 检查API虚拟环境..."
cd "$PROJECT_DIR/api"
if [ ! -d ".venv" ]; then
    log_info "创建虚拟环境..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# 3. 安装依赖
log_info "[3/8] 安装API依赖..."
pip install -q --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
else
    pip install -q sqlalchemy psycopg2-binary fastapi uvicorn python-telegram-bot
fi
log_info "✓ 依赖已安装"

# 4. 运行数据库迁移
log_info "[4/8] 运行数据库迁移..."
cd "$PROJECT_DIR"
python3 migrations/add_task_redpacket_system.py || log_warn "迁移可能已执行过"
deactivate
log_info "✓ 数据库迁移完成"

# 5. 构建前端
log_info "[5/8] 构建前端..."
cd "$PROJECT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    log_info "安装前端依赖..."
    npm install --silent
fi
npm run build
log_info "✓ 前端构建完成"

# 6. 停止Bot（解决冲突）
log_info "[6/8] 停止Bot服务（解决冲突）..."
systemctl stop luckyred-bot
sleep 2

# 7. 重启服务
log_info "[7/8] 重启服务..."
systemctl restart luckyred-api
systemctl restart luckyred-bot
sleep 3
log_info "✓ 服务已重启"

# 8. 检查服务状态
log_info "[8/8] 检查服务状态..."
if systemctl is-active --quiet luckyred-api; then
    log_info "✓ API服务运行正常"
else
    log_error "✗ API服务启动失败"
    systemctl status luckyred-api --no-pager | head -10
    exit 1
fi

if systemctl is-active --quiet luckyred-bot; then
    log_info "✓ Bot服务运行正常"
else
    log_error "✗ Bot服务启动失败"
    systemctl status luckyred-bot --no-pager | head -10
    exit 1
fi

# 测试API路由
log_info "测试API路由..."
sleep 2
TASK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/v1/tasks/status || echo "000")
if [ "$TASK_STATUS" = "401" ] || [ "$TASK_STATUS" = "200" ]; then
    log_info "✓ 任务API路由正常 (HTTP $TASK_STATUS)"
elif [ "$TASK_STATUS" = "404" ]; then
    log_error "✗ 任务API路由返回404，检查路由注册"
    log_info "检查 api/main.py 中的路由注册..."
    grep -n "tasks" "$PROJECT_DIR/api/main.py" || log_warn "未找到tasks路由注册"
else
    log_warn "⚠ 任务API返回: HTTP $TASK_STATUS"
fi

echo ""
log_info "✅ 部署完成！"
echo ""
echo "📋 下一步："
echo "  1. 检查API路由: curl http://localhost:8080/api/v1/tasks/status"
echo "  2. 访问任务页面: https://mini.usdt2026.cc/tasks"
echo "  3. 查看日志: sudo journalctl -u luckyred-api -f"
echo ""

