#!/bin/bash
# 一键修复 admin.usdt2026.cc 502 错误

set -e

echo "=========================================="
echo "  一键修复 admin.usdt2026.cc 502 错误"
echo "=========================================="

APP_DIR="/opt/luckyred"
DOMAIN="admin.usdt2026.cc"
EMAIL="admin@usdt2026.cc"

# 进入项目目录
cd $APP_DIR || { echo "❌ 无法进入 $APP_DIR"; exit 1; }

# 1. 更新代码
echo ""
echo "[1/7] 更新代码..."
git pull origin master || echo "⚠️  git pull 失败，继续执行..."

# 2. 检查后端服务
echo ""
echo "[2/7] 检查后端服务..."
if ! systemctl is-active --quiet luckyred-api; then
    echo "⚠️  后端服务未运行，启动服务..."
    sudo systemctl start luckyred-api
    sleep 3
fi
if systemctl is-active --quiet luckyred-api; then
    echo "✅ 后端服务运行中"
else
    echo "❌ 后端服务启动失败，查看日志："
    sudo journalctl -u luckyred-api -n 10 --no-pager
    exit 1
fi

# 3. 检查端口监听
echo ""
echo "[3/7] 检查端口监听..."
if sudo netstat -tlnp 2>/dev/null | grep -q ":8080"; then
    echo "✅ 端口 8080 正在监听"
else
    echo "❌ 端口 8080 未监听，重启后端服务..."
    sudo systemctl restart luckyred-api
    sleep 3
    if ! sudo netstat -tlnp 2>/dev/null | grep -q ":8080"; then
        echo "❌ 端口仍未监听"
        exit 1
    fi
fi

# 4. 检查静态文件
echo ""
echo "[4/7] 检查静态文件..."
STATIC_DIR="$APP_DIR/admin/frontend/dist"
if [ ! -d "$STATIC_DIR" ] || [ ! -f "$STATIC_DIR/index.html" ]; then
    echo "⚠️  静态文件不存在，重新构建..."
    cd $APP_DIR/admin/frontend
    npm install --silent
    npm run build
    cd $APP_DIR
fi
if [ -f "$STATIC_DIR/index.html" ]; then
    echo "✅ 静态文件存在"
else
    echo "❌ 静态文件构建失败"
    exit 1
fi

# 5. 更新 Nginx 配置
echo ""
echo "[5/7] 更新 Nginx 配置..."
NGINX_CONF="/etc/nginx/sites-available/$DOMAIN"
sudo cp $APP_DIR/deploy/nginx/$DOMAIN.conf $NGINX_CONF
sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/$DOMAIN.conf

# 6. 检查并获取 SSL 证书
echo ""
echo "[6/7] 检查 SSL 证书..."
if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "✅ SSL 证书已存在"
    # 确保 HTTPS 配置正确
    if ! sudo nginx -T 2>/dev/null | grep -A 10 "server_name $DOMAIN" | grep -q "listen 443"; then
        echo "添加 HTTPS 配置..."
        sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL --redirect --quiet || echo "⚠️  certbot 配置失败"
    fi
else
    echo "获取 SSL 证书..."
    # 先确保 HTTP 配置正确
    sudo nginx -t && sudo systemctl reload nginx
    # 获取证书
    if sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL --redirect --quiet 2>&1; then
        echo "✅ SSL 证书获取成功"
    else
        echo "⚠️  SSL 证书获取失败，使用 HTTP 配置"
    fi
fi

# 7. 测试并重新加载 Nginx
echo ""
echo "[7/7] 测试并重新加载 Nginx..."
if sudo nginx -t; then
    sudo systemctl reload nginx
    echo "✅ Nginx 配置已更新"
else
    echo "❌ Nginx 配置测试失败"
    exit 1
fi

# 验证
echo ""
echo "=========================================="
echo "  验证结果"
echo "=========================================="

echo ""
echo "后端服务状态:"
systemctl is-active luckyred-api && echo "✅ 运行中" || echo "❌ 未运行"

echo ""
echo "端口监听:"
sudo netstat -tlnp 2>/dev/null | grep 8080 && echo "✅ 端口 8080 监听中" || echo "❌ 端口未监听"

echo ""
echo "静态文件:"
[ -f "$STATIC_DIR/index.html" ] && echo "✅ index.html 存在" || echo "❌ index.html 不存在"

echo ""
echo "SSL 配置:"
if sudo nginx -T 2>/dev/null | grep -A 5 "server_name $DOMAIN" | grep -q "listen 443"; then
    echo "✅ HTTPS 已配置"
    echo "访问：https://$DOMAIN"
else
    echo "⚠️  只有 HTTP 配置"
    echo "访问：http://$DOMAIN"
fi

echo ""
echo "=========================================="
echo "  ✅ 修复完成！"
echo "=========================================="
echo ""
echo "如果仍有问题，请检查："
echo "  sudo tail -30 /var/log/nginx/error.log"
echo "  sudo journalctl -u luckyred-api -n 30"

