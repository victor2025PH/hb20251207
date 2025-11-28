#!/bin/bash
# 管理后台快速部署脚本 - 在服务器上执行

set -e

echo "=========================================="
echo "  管理后台快速部署"
echo "=========================================="

APP_DIR="/opt/luckyred"

# 1. 更新代码
echo "[1/6] 更新代码..."
cd $APP_DIR
git fetch origin
git reset --hard origin/master

# 2. 安装/更新后端依赖
echo "[2/6] 安装后端依赖..."
cd $APP_DIR/api
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# 3. 安装/更新管理后台前端依赖
echo "[3/6] 安装管理后台前端依赖..."
cd $APP_DIR/admin/frontend
if [ ! -d "node_modules" ]; then
    npm install
else
    npm install
fi

# 4. 构建管理后台前端
echo "[4/6] 构建管理后台前端..."
npm run build

# 5. 重启后端服务
echo "[5/6] 重启后端服务..."
sudo systemctl restart luckyred-api

# 6. 重新加载 Nginx
echo "[6/6] 重新加载 Nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "=========================================="
echo "  ✅ 部署完成！"
echo "=========================================="
echo "管理后台: https://admin.usdt2026.cc"
echo ""
echo "检查服务状态:"
sudo systemctl status luckyred-api --no-pager | head -10

