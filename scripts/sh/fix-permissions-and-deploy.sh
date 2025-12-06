#!/bin/bash
# 修复权限并部署管理后台

set -e

echo "=========================================="
echo "  修复权限并部署管理后台"
echo "=========================================="

APP_DIR="/opt/luckyred"

# 1. 修复目录权限
echo "[1/7] 修复目录权限..."
sudo chown -R ubuntu:ubuntu $APP_DIR
sudo chmod -R 755 $APP_DIR

# 2. 配置 git 安全目录（如果需要）
echo "[2/7] 配置 git..."
cd $APP_DIR
git config --global --add safe.directory $APP_DIR || true

# 3. 更新代码
echo "[3/7] 更新代码..."
git fetch origin
git reset --hard origin/master

# 4. 安装/更新后端依赖
echo "[4/7] 安装后端依赖..."
cd $APP_DIR/api
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
deactivate

# 5. 安装/更新管理后台前端依赖
echo "[5/7] 安装管理后台前端依赖..."
cd $APP_DIR/admin/frontend
if [ ! -d "node_modules" ]; then
    npm install
else
    npm install
fi

# 6. 构建管理后台前端
echo "[6/7] 构建管理后台前端..."
npm run build

# 7. 重启服务
echo "[7/7] 重启服务..."
sudo systemctl restart luckyred-api
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "=========================================="
echo "  ✅ 部署完成！"
echo "=========================================="
echo "管理后台: https://admin.usdt2026.cc"
echo ""
echo "检查服务状态:"
sudo systemctl status luckyred-api --no-pager | head -10

