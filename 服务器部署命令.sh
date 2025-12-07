#!/bin/bash
# 服务器部署脚本 - 认证修复

set -e  # 遇到错误立即退出

echo "=========================================="
echo "开始部署最新代码"
echo "=========================================="

# 1. 进入项目目录
cd /opt/luckyred

# 2. 拉取最新代码
echo ""
echo "步骤 1: 拉取最新代码..."
git pull origin master
echo "✓ 代码拉取完成"

# 3. 进入前端目录并构建
echo ""
echo "步骤 2: 构建前端..."
cd frontend
npm run build
echo "✓ 前端构建完成"

# 4. 重启 Nginx
echo ""
echo "步骤 3: 重启 Nginx..."
sudo systemctl restart nginx
echo "✓ Nginx 已重启"

# 5. 检查服务状态
echo ""
echo "步骤 4: 检查服务状态..."
echo "--- Nginx 状态 ---"
sudo systemctl status nginx --no-pager -l | head -n 5

echo ""
echo "--- API 服务状态 ---"
sudo systemctl status luckyred-api --no-pager -l | head -n 5

echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "请清除浏览器缓存并重新访问 https://mini.usdt2026.cc"
echo ""

