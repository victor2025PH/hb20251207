#!/bin/bash
# 服务器部署脚本 - 认证修复
# Deployment script for authentication fixes

set -e  # 遇到错误立即退出

echo "=========================================="
echo "开始部署最新代码"
echo "Starting deployment..."
echo "=========================================="

# 1. 进入项目目录
cd /opt/luckyred

# 2. 拉取最新代码
echo ""
echo "步骤 1: 拉取最新代码..."
echo "Step 1: Pulling latest code..."
git pull origin master
echo "✓ 代码拉取完成"
echo "✓ Code pulled successfully"

# 3. 进入前端目录并构建
echo ""
echo "步骤 2: 构建前端..."
echo "Step 2: Building frontend..."
cd frontend
npm run build
echo "✓ 前端构建完成"
echo "✓ Frontend built successfully"

# 4. 重启 Nginx
echo ""
echo "步骤 3: 重启 Nginx..."
echo "Step 3: Restarting Nginx..."
sudo systemctl restart nginx
echo "✓ Nginx 已重启"
echo "✓ Nginx restarted"

# 5. 检查服务状态
echo ""
echo "步骤 4: 检查服务状态..."
echo "Step 4: Checking service status..."
echo "--- Nginx 状态 ---"
echo "--- Nginx Status ---"
sudo systemctl status nginx --no-pager -l | head -n 5

echo ""
echo "--- API 服务状态 ---"
echo "--- API Service Status ---"
sudo systemctl status luckyred-api --no-pager -l | head -n 5

echo ""
echo "=========================================="
echo "部署完成！"
echo "Deployment completed!"
echo "=========================================="
echo ""
echo "请清除浏览器缓存并重新访问 https://mini.usdt2026.cc"
echo "Please clear browser cache and visit https://mini.usdt2026.cc"
echo ""

