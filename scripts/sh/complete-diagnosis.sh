#!/bin/bash
# 全面诊断 502 错误

set -e

echo "=========================================="
echo "  全面诊断 502 Bad Gateway 错误"
echo "=========================================="

APP_DIR="/opt/luckyred"

# 1. 检查后端服务状态
echo ""
echo "[1/8] 检查后端服务状态..."
if systemctl is-active --quiet luckyred-api; then
    echo "✅ 后端服务正在运行"
    systemctl status luckyred-api --no-pager | head -10
else
    echo "❌ 后端服务未运行"
    echo "尝试启动服务..."
    sudo systemctl start luckyred-api
    sleep 2
    if systemctl is-active --quiet luckyred-api; then
        echo "✅ 后端服务已启动"
    else
        echo "❌ 后端服务启动失败"
        echo "查看错误日志:"
        sudo journalctl -u luckyred-api -n 30 --no-pager | tail -20
    fi
fi

# 2. 检查端口监听
echo ""
echo "[2/8] 检查端口监听..."
if sudo netstat -tlnp 2>/dev/null | grep -q ":8080"; then
    echo "✅ 端口 8080 正在监听"
    sudo netstat -tlnp | grep 8080
else
    echo "❌ 端口 8080 未监听"
    echo "这可能是 502 错误的根本原因！"
fi

# 3. 测试后端 API 连接
echo ""
echo "[3/8] 测试后端 API 连接..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/api/v1/admin/auth/login || echo "000")
if [ "$HTTP_CODE" = "405" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "422" ]; then
    echo "✅ 后端 API 可访问 (HTTP $HTTP_CODE - 这是正常的，因为需要 POST 请求)"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "❌ 无法连接到后端 API"
else
    echo "⚠️  后端 API 返回 HTTP $HTTP_CODE"
fi

# 4. 检查静态文件
echo ""
echo "[4/8] 检查静态文件..."
STATIC_DIR="$APP_DIR/admin/frontend/dist"
if [ -d "$STATIC_DIR" ]; then
    echo "✅ 静态文件目录存在: $STATIC_DIR"
    if [ -f "$STATIC_DIR/index.html" ]; then
        echo "✅ index.html 存在"
        ls -lh "$STATIC_DIR/index.html"
    else
        echo "❌ index.html 不存在"
    fi
else
    echo "❌ 静态文件目录不存在: $STATIC_DIR"
    echo "需要重新构建前端..."
fi

# 5. 检查 Nginx 配置
echo ""
echo "[5/8] 检查 Nginx 配置..."
NGINX_CONF="/etc/nginx/sites-available/admin.usdt2026.cc.conf"
if [ -f "$NGINX_CONF" ]; then
    echo "✅ Nginx 配置文件存在"
    echo "Root 路径:"
    grep "root" "$NGINX_CONF" | head -1
    echo "Proxy 配置:"
    grep "proxy_pass" "$NGINX_CONF" | head -1
else
    echo "❌ Nginx 配置文件不存在"
fi

# 6. 检查 Nginx 是否启用该站点
echo ""
echo "[6/8] 检查 Nginx 站点启用状态..."
if [ -L "/etc/nginx/sites-enabled/admin.usdt2026.cc.conf" ]; then
    echo "✅ 站点已启用"
else
    echo "❌ 站点未启用"
    echo "创建符号链接..."
    sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/admin.usdt2026.cc.conf
    sudo nginx -t && sudo systemctl reload nginx
fi

# 7. 检查 Nginx 错误日志
echo ""
echo "[7/8] 检查 Nginx 错误日志（最近 20 行）..."
if [ -f "/var/log/nginx/error.log" ]; then
    echo "最近的错误:"
    sudo tail -20 /var/log/nginx/error.log | grep -i "502\|error\|failed" || echo "未发现相关错误"
else
    echo "⚠️  无法读取错误日志"
fi

# 8. 测试完整请求流程
echo ""
echo "[8/8] 测试完整请求流程..."
echo "测试静态文件访问:"
STATIC_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/ || echo "000")
if [ "$STATIC_TEST" = "200" ] || [ "$STATIC_TEST" = "304" ]; then
    echo "✅ 静态文件可访问 (HTTP $STATIC_TEST)"
else
    echo "⚠️  静态文件访问返回 HTTP $STATIC_TEST"
fi

echo ""
echo "=========================================="
echo "  诊断完成"
echo "=========================================="
echo ""
echo "如果问题仍然存在，请检查:"
echo "  1. 后端服务日志: sudo journalctl -u luckyred-api -n 50"
echo "  2. Nginx 访问日志: sudo tail -50 /var/log/nginx/access.log"
echo "  3. Nginx 错误日志: sudo tail -50 /var/log/nginx/error.log"
echo "  4. 手动测试后端: curl -v http://127.0.0.1:8080/api/v1/admin/auth/login"

