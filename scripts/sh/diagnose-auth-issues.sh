#!/bin/bash

# 认证问题诊断脚本
# 检查数据库表、API端点、服务状态

set -e

echo "🔍 开始诊断认证问题..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查数据库表
echo "📊 检查数据库表..."
cd /opt/luckyred/api
source .venv/bin/activate

python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/luckyred')

from sqlalchemy import inspect, create_engine
from shared.config.settings import get_settings
from shared.database.models import Base

settings = get_settings()
engine = create_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://") if settings.DATABASE_URL.startswith("postgresql") else settings.DATABASE_URL)

inspector = inspect(engine)
tables = inspector.get_table_names()

required_tables = ['users', 'user_identities', 'account_links']
missing_tables = [t for t in required_tables if t not in tables]

if missing_tables:
    print(f"❌ 缺少表: {', '.join(missing_tables)}")
    print("   运行以下命令创建表:")
    print("   cd /opt/luckyred/api")
    print("   source .venv/bin/activate")
    print("   python3 -c 'from shared.database.connection import init_db; init_db()'")
    sys.exit(1)
else:
    print("✅ 所有必需的表都存在")
    
    # 检查表结构
    for table in required_tables:
        columns = [col['name'] for col in inspector.get_columns(table)]
        print(f"   {table}: {len(columns)} 列")
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 数据库检查失败${NC}"
    exit 1
fi

echo ""

# 2. 检查 API 服务状态
echo "🔍 检查 API 服务状态..."
if systemctl is-active --quiet luckyred-api; then
    echo -e "${GREEN}✓ API 服务运行中${NC}"
else
    echo -e "${RED}❌ API 服务未运行${NC}"
    echo "   运行: sudo systemctl start luckyred-api"
    exit 1
fi

echo ""

# 3. 检查最近的错误日志
echo "📋 检查最近的错误日志..."
echo "--- Google 认证相关错误 ---"
sudo journalctl -u luckyred-api -n 100 --no-pager | grep -i "google\|identity\|error" | tail -10 || echo "   没有找到相关错误"

echo ""
echo "--- 所有错误 ---"
sudo journalctl -u luckyred-api -n 50 --no-pager | grep -i "error\|exception\|traceback" | tail -10 || echo "   没有找到错误"

echo ""

# 4. 测试 API 端点
echo "🧪 测试 API 端点..."
API_URL="http://localhost:8080"

# 测试健康检查
if curl -s -f "${API_URL}/health" > /dev/null; then
    echo -e "${GREEN}✓ 健康检查通过${NC}"
else
    echo -e "${RED}❌ 健康检查失败${NC}"
    exit 1
fi

# 测试 Google 认证端点（应该返回 422 或 401，不应该返回 500）
echo "测试 Google 认证端点..."
response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}/api/v1/auth/web/google" \
    -H "Content-Type: application/json" \
    -d '{"id_token": "test"}' 2>&1)
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "422" ] || [ "$http_code" = "401" ]; then
    echo -e "${GREEN}✓ Google 认证端点响应正常 (HTTP $http_code)${NC}"
elif [ "$http_code" = "500" ]; then
    echo -e "${RED}❌ Google 认证端点返回 500 错误${NC}"
    echo "   响应: $body"
    exit 1
else
    echo -e "${YELLOW}⚠ Google 认证端点返回 HTTP $http_code${NC}"
    echo "   响应: $body"
fi

echo ""

# 5. 检查 Python 依赖
echo "📦 检查 Python 依赖..."
if python3 -c "from api.services.identity_service import IdentityService" 2>/dev/null; then
    echo -e "${GREEN}✓ IdentityService 可以导入${NC}"
else
    echo -e "${RED}❌ IdentityService 导入失败${NC}"
    python3 -c "from api.services.identity_service import IdentityService" 2>&1
    exit 1
fi

echo ""

# 6. 检查数据库连接
echo "🔌 检查数据库连接..."
python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/luckyred')

from shared.database.connection import get_async_db
from shared.database.models import User, UserIdentity
import asyncio

async def test_db():
    try:
        async for db in get_async_db():
            # 测试查询
            from sqlalchemy import select
            result = await db.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
            print("✅ 数据库连接正常")
            
            # 检查 UserIdentity 表
            result = await db.execute(select(UserIdentity).limit(1))
            print("✅ UserIdentity 表可访问")
            return
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

asyncio.run(test_db())
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 数据库连接测试失败${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ 诊断完成！${NC}"
echo ""
echo "如果问题仍然存在，请检查："
echo "1. 数据库表是否正确创建"
echo "2. API 服务日志: sudo journalctl -u luckyred-api -f"
echo "3. 数据库迁移是否完成"

