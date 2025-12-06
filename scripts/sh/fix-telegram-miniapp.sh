#!/bin/bash
# 修復 Telegram MiniApp 無法加載的問題
# 在服務器上執行此腳本

echo "🔧 修復 Telegram MiniApp 加載問題..."

# 備份現有配置
echo "📁 備份現有配置..."
sudo cp /etc/nginx/sites-available/mini.usdt2026.cc.conf /etc/nginx/sites-available/mini.usdt2026.cc.conf.bak 2>/dev/null || true

# 查找並修改配置文件
CONFIG_FILE="/etc/nginx/sites-available/mini.usdt2026.cc.conf"

# 檢查是否存在 X-Frame-Options 配置
if grep -q "X-Frame-Options" "$CONFIG_FILE"; then
    echo "🔄 移除 X-Frame-Options 限制..."
    
    # 註釋掉 X-Frame-Options 行
    sudo sed -i 's/add_header X-Frame-Options "SAMEORIGIN" always;/# add_header X-Frame-Options "SAMEORIGIN" always; # 已禁用 - Telegram MiniApp 需要/g' "$CONFIG_FILE"
    
    # 如果沒有 CSP frame-ancestors，添加它
    if ! grep -q "frame-ancestors" "$CONFIG_FILE"; then
        echo "➕ 添加 Content-Security-Policy..."
        sudo sed -i '/X-Content-Type-Options/i\    add_header Content-Security-Policy "frame-ancestors '\''self'\'' https://web.telegram.org https://*.telegram.org" always;' "$CONFIG_FILE"
    fi
    
    echo "✅ 配置已更新"
else
    echo "ℹ️  未找到 X-Frame-Options，可能已經修復"
fi

# 測試 nginx 配置
echo "🔍 測試 Nginx 配置..."
if sudo nginx -t; then
    echo "✅ Nginx 配置正確"
    
    # 重載 nginx
    echo "🔄 重載 Nginx..."
    sudo systemctl reload nginx
    
    echo ""
    echo "=========================================="
    echo "  ✅ 修復完成！"
    echo "=========================================="
    echo ""
    echo "現在可以在 Telegram 中測試 MiniApp 了"
else
    echo "❌ Nginx 配置有誤，正在恢復備份..."
    sudo cp /etc/nginx/sites-available/mini.usdt2026.cc.conf.bak /etc/nginx/sites-available/mini.usdt2026.cc.conf
    echo "已恢復備份配置"
fi

