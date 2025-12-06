#!/bin/bash
# 为 admin.usdt2026.cc 添加 SSL 配置

set -e

echo "=========================================="
echo "  为 admin.usdt2026.cc 添加 SSL 配置"
echo "=========================================="

APP_DIR="/opt/luckyred"

# 1. 检查是否已有 SSL 证书
echo ""
echo "[1/3] 检查 SSL 证书..."
if [ -d "/etc/letsencrypt/live/admin.usdt2026.cc" ]; then
    echo "✅ SSL 证书已存在"
    CERT_PATH="/etc/letsencrypt/live/admin.usdt2026.cc"
else
    echo "⚠️  SSL 证书不存在"
    echo "将尝试获取 SSL 证书..."
    CERT_PATH=""
fi

# 2. 更新 Nginx 配置
echo ""
echo "[2/3] 更新 Nginx 配置..."
NGINX_CONF="/etc/nginx/sites-available/admin.usdt2026.cc.conf"

# 备份原配置
sudo cp "$NGINX_CONF" "$NGINX_CONF.backup"

# 如果有 SSL 证书，添加 HTTPS 配置
if [ -n "$CERT_PATH" ]; then
    echo "添加 HTTPS 配置..."
    sudo tee "$NGINX_CONF" > /dev/null <<EOF
# Admin 後台 (HTTPS)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name admin.usdt2026.cc;

    ssl_certificate $CERT_PATH/fullchain.pem;
    ssl_certificate_key $CERT_PATH/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # 管理後台靜態文件
    root /opt/luckyred/admin/frontend/dist;
    index index.html;

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8080/api/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 前端路由 (SPA)
    location / {
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
    
    # 避免对已存在的文件进行重定向
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # 安全頭
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name admin.usdt2026.cc;
    return 301 https://\$server_name\$request_uri;
}
EOF
else
    echo "保持 HTTP 配置，但确保正确路由..."
    # 确保 HTTP 配置正确
    sudo tee "$NGINX_CONF" > /dev/null <<EOF
# Admin 後台 (HTTP 版本，部署後使用 certbot 添加 SSL)
server {
    listen 80;
    listen [::]:80;
    server_name admin.usdt2026.cc;

    # 管理後台靜態文件
    root /opt/luckyred/admin/frontend/dist;
    index index.html;

    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:8080/api/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 前端路由 (SPA)
    location / {
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
    
    # 避免对已存在的文件进行重定向
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # 安全頭
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF
fi

# 3. 测试并重新加载 Nginx
echo ""
echo "[3/3] 测试并重新加载 Nginx..."
sudo nginx -t && sudo systemctl reload nginx
echo "✅ Nginx 配置已更新"

echo ""
echo "=========================================="
echo "  配置完成"
echo "=========================================="
echo ""
if [ -z "$CERT_PATH" ]; then
    echo "⚠️  未找到 SSL 证书"
    echo "如果需要 HTTPS，请执行："
    echo "  sudo certbot --nginx -d admin.usdt2026.cc"
    echo ""
    echo "或者通过 HTTP 访问："
    echo "  http://admin.usdt2026.cc"
else
    echo "✅ SSL 配置已添加"
    echo "访问：https://admin.usdt2026.cc"
fi

