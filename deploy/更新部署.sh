#!/bin/bash
# ===========================================
# hbgm001 更新部署脚本
# 用于更新代码和重启服务
# ===========================================

set -e

# 配置
PROJECT_DIR="/home/ubuntu/hbgm001"
SERVICE_NAME="hbgm001-backend"

echo "=========================================="
echo "  更新部署 hbgm001"
echo "=========================================="
echo

# 进入项目目录
cd $PROJECT_DIR

# 拉取最新代码
echo "📥 拉取最新代码..."
git fetch origin
git pull origin main

# 激活虚拟环境并更新依赖
echo "📦 更新 Python 依赖..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "⚠️  虚拟环境不存在，创建新的虚拟环境..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# 运行数据库迁移（如果有）
if [ -d "migrations" ]; then
    echo "🗄️  检查数据库迁移..."
    echo "提示: 如有迁移文件，请手动运行"
fi

# 重启服务
echo "🔄 重启服务..."
sudo systemctl restart $SERVICE_NAME

# 等待服务启动
sleep 3

# 检查服务状态
echo "✅ 检查服务状态..."
sudo systemctl status $SERVICE_NAME --no-pager -l || true

echo
echo "=========================================="
echo "  更新完成！"
echo "=========================================="

