#!/bin/bash
# 设置 Systemd 服务脚本
# 使用方法: sudo bash setup-systemd-service.sh

set -e

echo "=========================================="
echo "设置 LuckyRed Systemd 服务"
echo "=========================================="

# 配置
PROJECT_DIR="/home/ubuntu/hbgm001"
SERVICE_NAME="luckyred-api"
SERVICE_FILE="deploy/systemd/${SERVICE_NAME}.service"
SYSTEMD_DIR="/etc/systemd/system"

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 项目目录不存在: $PROJECT_DIR"
    exit 1
fi

# 检查服务文件
if [ ! -f "$PROJECT_DIR/$SERVICE_FILE" ]; then
    echo "❌ 服务文件不存在: $PROJECT_DIR/$SERVICE_FILE"
    exit 1
fi

# 复制服务文件
echo "📋 复制服务文件..."
cp "$PROJECT_DIR/$SERVICE_FILE" "$SYSTEMD_DIR/${SERVICE_NAME}.service"

# 确保 .env 文件存在
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "⚠️  .env 文件不存在，请创建: $PROJECT_DIR/.env"
    echo "   可以使用 env-template.txt 作为模板"
fi

# 确保虚拟环境存在
if [ ! -d "$PROJECT_DIR/api/.venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv "$PROJECT_DIR/api/.venv"
    source "$PROJECT_DIR/api/.venv/bin/activate"
    pip install --upgrade pip
    pip install -r "$PROJECT_DIR/api/requirements.txt"
fi

# 确保工作目录权限正确
echo "🔐 设置目录权限..."
chown -R www-data:www-data "$PROJECT_DIR/api"
chmod -R 755 "$PROJECT_DIR/api"

# 重新加载 systemd
echo "🔄 重新加载 systemd..."
systemctl daemon-reload

# 启用服务（开机自启）
echo "✅ 启用服务..."
systemctl enable ${SERVICE_NAME}.service

# 启动服务
echo "🚀 启动服务..."
systemctl start ${SERVICE_NAME}.service

# 等待服务启动
sleep 2

# 检查服务状态
echo "📊 服务状态:"
systemctl status ${SERVICE_NAME}.service --no-pager -l || true

echo ""
echo "=========================================="
echo "服务设置完成！"
echo "=========================================="
echo ""
echo "常用命令："
echo "  查看状态: sudo systemctl status ${SERVICE_NAME}"
echo "  查看日志: sudo journalctl -u ${SERVICE_NAME} -f"
echo "  重启服务: sudo systemctl restart ${SERVICE_NAME}"
echo "  停止服务: sudo systemctl stop ${SERVICE_NAME}"
echo ""

