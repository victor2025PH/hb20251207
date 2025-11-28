#!/bin/bash
# 修复 Nginx 配置并重新加载

set -e

echo "=========================================="
echo "  修复 Nginx 配置"
echo "=========================================="

APP_DIR="/opt/luckyred"

# 1. 更新代码（获取修复后的配置）
echo "[1/3] 更新代码..."
cd $APP_DIR
git pull origin master

# 2. 复制并应用 Nginx 配置
echo "[2/3] 应用 Nginx 配置..."
sudo cp $APP_DIR/deploy/nginx/admin.usdt2026.cc.conf /etc/nginx/sites-available/admin.usdt2026.cc.conf
sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/admin.usdt2026.cc.conf

# 3. 测试并重新加载 Nginx
echo "[3/3] 测试并重新加载 Nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo ""
echo "=========================================="
echo "  ✅ Nginx 配置已修复！"
echo "=========================================="
echo "管理后台: https://admin.usdt2026.cc"
echo ""
echo "检查配置:"
echo "  sudo nginx -T | grep -A 5 'admin.usdt2026.cc'"

