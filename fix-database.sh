#!/bin/bash

# 快速修复数据库表结构问题
# 在项目根目录运行：bash fix-database.sh

set -e

echo "🔧 开始修复数据库表结构..."
echo ""

# 检测项目目录
if [ -d "/opt/luckyred" ]; then
    PROJECT_DIR="/opt/luckyred"
elif [ -d "$HOME/luckyred" ]; then
    PROJECT_DIR="$HOME/luckyred"
else
    echo "❌ 未找到项目目录，请在项目根目录运行此脚本"
    exit 1
fi

cd "$PROJECT_DIR"
echo "项目目录: $PROJECT_DIR"

# 1. 拉取最新代码
echo ""
echo "📥 拉取最新代码..."
git pull origin master || echo "⚠️  Git pull 失败，继续..."

# 2. 运行数据库迁移
echo ""
echo "🗄️  运行数据库迁移..."
cd api
source .venv/bin/activate

# 运行迁移脚本
python3 ../scripts/py/migrate_add_uuid_column.py

# 如果迁移脚本不存在，使用 init_db
if [ $? -ne 0 ]; then
    echo "使用 init_db() 创建/更新表..."
    python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/luckyred')

from shared.database.connection import init_db
print("正在创建/更新数据库表...")
init_db()
print("✅ 数据库表已创建/更新")
EOF
fi

# 3. 重新构建前端
echo ""
echo "🔨 重新构建前端..."
cd ../frontend
npm run build

# 4. 重启服务
echo ""
echo "🔄 重启服务..."
sudo systemctl restart luckyred-api
sleep 2

# 5. 检查服务状态
if systemctl is-active --quiet luckyred-api; then
    echo "✅ API 服务运行正常"
else
    echo "❌ API 服务启动失败"
    echo "查看日志:"
    sudo journalctl -u luckyred-api -n 30 --no-pager
    exit 1
fi

# 6. 重新加载 Nginx
sudo systemctl reload nginx

echo ""
echo "✅ 修复完成！"
echo ""
echo "请清除浏览器缓存并刷新页面测试登录功能"

