#!/bin/bash
# 检查 Nginx 路由配置

set -e

echo "=========================================="
echo "  检查 Nginx 路由配置"
echo "=========================================="

# 1. 检查启用的站点
echo ""
echo "[1/5] 检查启用的站点..."
echo "启用的站点配置:"
sudo ls -la /etc/nginx/sites-enabled/ | grep -v "^d" | grep -v "^total"

# 2. 检查默认服务器
echo ""
echo "[2/5] 检查默认服务器配置..."
DEFAULT_SERVER=$(sudo nginx -T 2>/dev/null | grep -i "default_server" || echo "未找到默认服务器")
echo "$DEFAULT_SERVER"

# 3. 检查 admin.usdt2026.cc 配置
echo ""
echo "[3/5] 检查 admin.usdt2026.cc 配置..."
echo "完整的 server 块:"
sudo nginx -T 2>/dev/null | grep -A 30 "server_name.*admin.usdt2026.cc" || echo "未找到 admin.usdt2026.cc 配置"

# 4. 检查所有 server_name
echo ""
echo "[4/5] 检查所有 server_name..."
echo "所有 server_name 配置:"
sudo nginx -T 2>/dev/null | grep "server_name" | grep -v "^#" | head -20

# 5. 检查 bot.usdt2026.cc 配置
echo ""
echo "[5/5] 检查 bot.usdt2026.cc 配置..."
echo "bot.usdt2026.cc server 块:"
sudo nginx -T 2>/dev/null | grep -A 20 "server_name.*bot.usdt2026.cc" || echo "未找到 bot.usdt2026.cc 配置"

echo ""
echo "=========================================="
echo "  检查完成"
echo "=========================================="
echo ""
echo "如果发现配置冲突，请："
echo "  1. 确保 admin.usdt2026.cc 配置正确"
echo "  2. 检查是否有默认服务器导致路由错误"
echo "  3. 确保 server_name 匹配正确"

