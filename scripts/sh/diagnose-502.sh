#!/bin/bash
# 诊断 502 Bad Gateway 错误

set -e

echo "=========================================="
echo "  诊断 502 Bad Gateway 错误"
echo "=========================================="

APP_DIR="/opt/luckyred"

# 1. 检查后端服务状态
echo ""
echo "[1/6] 检查后端服务状态..."
systemctl status luckyred-api --no-pager | head -20 || echo "⚠️  服务状态检查失败"

# 2. 检查后端服务是否在监听端口
echo ""
echo "[2/6] 检查后端服务端口监听..."
netstat -tlnp | grep 8080 || echo "⚠️  端口 8080 未监听"

# 3. 检查静态文件是否存在
echo ""
echo "[3/6] 检查静态文件..."
STATIC_DIR="$APP_DIR/admin/frontend/dist"
if [ -d "$STATIC_DIR" ]; then
    echo "✅ 静态文件目录存在: $STATIC_DIR"
    ls -lah "$STATIC_DIR" | head -10
    if [ -f "$STATIC_DIR/index.html" ]; then
        echo "✅ index.html 存在"
    else
        echo "❌ index.html 不存在"
    fi
else
    echo "❌ 静态文件目录不存在: $STATIC_DIR"
fi

# 4. 检查 Nginx 配置
echo ""
echo "[4/6] 检查 Nginx 配置..."
if [ -f "/etc/nginx/sites-available/admin.usdt2026.cc.conf" ]; then
    echo "✅ Nginx 配置文件存在"
    echo "配置内容:"
    grep -A 3 "root" /etc/nginx/sites-available/admin.usdt2026.cc.conf || echo "⚠️  未找到 root 配置"
else
    echo "❌ Nginx 配置文件不存在"
fi

# 5. 检查 Nginx 错误日志
echo ""
echo "[5/6] 检查 Nginx 错误日志（最近 20 行）..."
sudo tail -20 /var/log/nginx/error.log || echo "⚠️  无法读取错误日志"

# 6. 测试后端 API
echo ""
echo "[6/6] 测试后端 API..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://127.0.0.1:8080/api/v1/admin/auth/login || echo "❌ 无法连接到后端 API"

echo ""
echo "=========================================="
echo "  诊断完成"
echo "=========================================="

