#!/bin/bash
# 快速修复 502 Bad Gateway 错误

set -e

echo "=========================================="
echo "  修复 502 Bad Gateway 错误"
echo "=========================================="

APP_DIR="/opt/luckyred"

# 1. 检查并修复静态文件路径
echo ""
echo "[1/5] 检查静态文件..."
STATIC_DIR="$APP_DIR/admin/frontend/dist"
if [ ! -d "$STATIC_DIR" ]; then
    echo "❌ 静态文件目录不存在，重新构建前端..."
    cd $APP_DIR/admin/frontend
    npm run build
else
    echo "✅ 静态文件目录存在"
fi

# 2. 检查并修复 Nginx 配置
echo ""
echo "[2/5] 检查并修复 Nginx 配置..."
NGINX_CONF="/etc/nginx/sites-available/admin.usdt2026.cc.conf"
if [ -f "$NGINX_CONF" ]; then
    # 确保配置指向正确的路径
    if ! grep -q "root /opt/luckyred/admin/frontend/dist" "$NGINX_CONF"; then
        echo "修复 Nginx 配置路径..."
        sudo sed -i 's|root /opt/luckyred/admin/dist|root /opt/luckyred/admin/frontend/dist|g' "$NGINX_CONF"
    fi
    echo "✅ Nginx 配置已检查"
else
    echo "❌ Nginx 配置文件不存在，复制配置..."
    sudo cp $APP_DIR/deploy/nginx/admin.usdt2026.cc.conf /etc/nginx/sites-available/admin.usdt2026.cc.conf
    sudo ln -sf /etc/nginx/sites-available/admin.usdt2026.cc.conf /etc/nginx/sites-enabled/admin.usdt2026.cc.conf
fi

# 3. 检查后端服务
echo ""
echo "[3/5] 检查后端服务..."
if systemctl is-active --quiet luckyred-api; then
    echo "✅ 后端服务正在运行"
else
    echo "⚠️  后端服务未运行，尝试启动..."
    sudo systemctl start luckyred-api
    sleep 2
    if systemctl is-active --quiet luckyred-api; then
        echo "✅ 后端服务已启动"
    else
        echo "❌ 后端服务启动失败，查看日志:"
        sudo journalctl -u luckyred-api -n 20 --no-pager
    fi
fi

# 4. 检查端口监听
echo ""
echo "[4/5] 检查端口监听..."
if netstat -tlnp 2>/dev/null | grep -q ":8080"; then
    echo "✅ 端口 8080 正在监听"
else
    echo "❌ 端口 8080 未监听，重启后端服务..."
    sudo systemctl restart luckyred-api
    sleep 3
    if netstat -tlnp 2>/dev/null | grep -q ":8080"; then
        echo "✅ 端口 8080 现在正在监听"
    else
        echo "❌ 端口仍未监听，查看服务日志:"
        sudo journalctl -u luckyred-api -n 30 --no-pager
    fi
fi

# 5. 重新加载 Nginx
echo ""
echo "[5/5] 测试并重新加载 Nginx..."
sudo nginx -t && sudo systemctl reload nginx
echo "✅ Nginx 已重新加载"

echo ""
echo "=========================================="
echo "  ✅ 修复完成！"
echo "=========================================="
echo ""
echo "检查服务状态:"
systemctl status luckyred-api --no-pager | head -10
echo ""
echo "检查端口:"
netstat -tlnp | grep 8080 || echo "⚠️  端口未监听"
echo ""
echo "检查静态文件:"
ls -lah $STATIC_DIR/index.html 2>/dev/null && echo "✅ index.html 存在" || echo "❌ index.html 不存在"
echo ""
echo "如果问题仍然存在，请查看:"
echo "  sudo journalctl -u luckyred-api -n 50"
echo "  sudo tail -50 /var/log/nginx/error.log"

