#!/bin/bash

# 快速修复认证问题并部署
set -e

echo "🔧 快速修复认证问题..."
echo ""

PROJECT_DIR="/opt/luckyred"
cd "$PROJECT_DIR"

# 1. 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin master

# 2. 确保数据库表存在
echo "🗄️  检查数据库表..."
cd api
source .venv/bin/activate

python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/luckyred')

from shared.database.connection import init_db
print("正在创建/更新数据库表...")
init_db()
print("✅ 数据库表已创建/更新")
EOF

# 3. 重新构建前端
echo "🔨 重新构建前端..."
cd ../frontend
npm run build

# 4. 重启服务
echo "🔄 重启服务..."
sudo systemctl restart luckyred-api
sleep 2

# 5. 检查服务状态
if systemctl is-active --quiet luckyred-api; then
    echo "✅ API 服务运行正常"
else
    echo "❌ API 服务启动失败"
    sudo journalctl -u luckyred-api -n 30 --no-pager
    exit 1
fi

# 6. 重新加载 Nginx
sudo systemctl reload nginx

# 7. 测试 API
echo "🧪 测试 API..."
sleep 1
if curl -s http://localhost:8080/health | grep -q "ok"; then
    echo "✅ API 健康检查通过"
else
    echo "⚠️  API 健康检查失败"
fi

echo ""
echo "✅ 修复完成！"
echo ""
echo "请清除浏览器缓存并刷新页面测试登录功能"

