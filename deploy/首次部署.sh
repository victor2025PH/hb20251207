#!/bin/bash
# ===========================================
# hbgm001 首次部署脚本
# 在服务器上执行此脚本进行首次部署
# ===========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
PROJECT_DIR="/home/ubuntu/hbgm001"
GIT_REPO="https://github.com/victor2025PH/hb20251207.git"
SERVICE_NAME="hbgm001-backend"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=========================================="
echo "  hbgm001 首次部署"
echo "=========================================="
echo

# 1. 检查是否为 root 或 sudo
if [ "$EUID" -ne 0 ]; then
    log_warn "需要 sudo 权限，某些操作可能需要输入密码"
fi

# 2. 更新系统
log_info "更新系统包..."
sudo apt update
sudo apt upgrade -y

# 3. 安装基础依赖
log_info "安装基础依赖..."
sudo apt install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    curl \
    wget

# 4. 创建项目目录
log_info "创建项目目录: $PROJECT_DIR"
sudo mkdir -p $PROJECT_DIR
sudo chown -R ubuntu:ubuntu $PROJECT_DIR

# 5. 克隆代码（如果目录为空）
if [ ! -d "$PROJECT_DIR/.git" ]; then
    log_info "克隆代码仓库..."
    cd /home/ubuntu
    git clone $GIT_REPO hbgm001
else
    log_info "代码已存在，跳过克隆"
fi

# 6. 创建虚拟环境
log_info "创建 Python 虚拟环境..."
cd $PROJECT_DIR
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    log_info "虚拟环境已创建"
else
    log_info "虚拟环境已存在"
fi

# 7. 激活虚拟环境并安装依赖
log_info "安装 Python 依赖..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 8. 创建 .env 文件（如果不存在）
if [ ! -f "$PROJECT_DIR/.env" ]; then
    log_warn ".env 文件不存在，请手动创建并配置"
    log_info "可以从 env-template.txt 复制模板"
    if [ -f "$PROJECT_DIR/env-template.txt" ]; then
        cp $PROJECT_DIR/env-template.txt $PROJECT_DIR/.env
        log_info "已从模板创建 .env 文件，请编辑配置"
    fi
else
    log_info ".env 文件已存在"
fi

# 9. 创建 systemd 服务文件
log_info "创建 systemd 服务..."
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=hbgm001 Backend API Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=$PROJECT_DIR"
EnvironmentFile=$PROJECT_DIR/.env

# 启动命令
ExecStart=$PROJECT_DIR/.venv/bin/uvicorn api.main:app --host 127.0.0.1 --port 8080 --workers 4

# 重启策略
Restart=always
RestartSec=5
StartLimitInterval=200
StartLimitBurst=5

# 日志配置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# 安全配置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR

[Install]
WantedBy=multi-user.target
EOF

# 10. 重新加载 systemd
log_info "重新加载 systemd..."
sudo systemctl daemon-reload

# 11. 启用服务（开机自启）
log_info "启用服务..."
sudo systemctl enable ${SERVICE_NAME}.service

# 12. 启动服务
log_info "启动服务..."
sudo systemctl start ${SERVICE_NAME}.service

# 13. 等待服务启动
sleep 3

# 14. 检查服务状态
log_info "检查服务状态..."
sudo systemctl status ${SERVICE_NAME}.service --no-pager -l || true

echo
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo
echo "常用命令："
echo "  查看状态: sudo systemctl status $SERVICE_NAME"
echo "  查看日志: sudo journalctl -u $SERVICE_NAME -f"
echo "  重启服务: sudo systemctl restart $SERVICE_NAME"
echo "  停止服务: sudo systemctl stop $SERVICE_NAME"
echo
echo "重要：请确保已配置 .env 文件！"
echo

