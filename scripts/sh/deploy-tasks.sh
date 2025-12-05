#!/bin/bash
# 部署任务红包系统更新

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

# 1. 更新代码
log_info "更新代码..."
git fetch origin
git pull origin master || git pull origin main

# 2. 运行数据库迁移
log_info "运行数据库迁移..."
python3 migrations/add_task_redpacket_system.py

# 3. 安装API依赖（如果有新依赖）
log_info "检查API依赖..."
cd "$PROJECT_DIR/api"
if [ -f "requirements.txt" ]; then
    source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate
    pip install -q -r requirements.txt
fi

# 4. 构建前端
log_info "构建前端..."
cd "$PROJECT_DIR/frontend"
npm install --silent
npm run build

# 5. 重启服务
log_info "重启服务..."
systemctl restart luckyred-api
systemctl restart luckyred-bot

# 6. 检查服务状态
log_info "检查服务状态..."
sleep 2
systemctl is-active --quiet luckyred-api && log_info "API服务运行正常" || log_error "API服务启动失败"
systemctl is-active --quiet luckyred-bot && log_info "Bot服务运行正常" || log_error "Bot服务启动失败"

log_info "部署完成！"

