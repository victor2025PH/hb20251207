#!/bin/bash

# 检查数据库表结构
# 在项目根目录运行：bash check-database.sh

set -e

echo "🔍 检查数据库表结构..."
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

cd "$PROJECT_DIR/api"
source .venv/bin/activate

python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/luckyred')

from sqlalchemy import inspect, create_engine, text
from shared.config.settings import get_settings

settings = get_settings()

# 创建引擎
if settings.DATABASE_URL.startswith("postgresql"):
    engine = create_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"))
else:
    engine = create_engine(settings.DATABASE_URL)

inspector = inspect(engine)

# 检查 users 表
if 'users' not in inspector.get_table_names():
    print("❌ users 表不存在")
    sys.exit(1)

print("✅ users 表存在")

# 检查列
columns = [col['name'] for col in inspector.get_columns('users')]
print(f"   列数: {len(columns)}")

# 检查必需的列
required_columns = [
    'id', 'uuid', 'wallet_address', 'wallet_network', 
    'primary_platform', 'referrer_id', 'referral_code',
    'total_referrals', 'tier1_commission', 'tier2_commission',
    'last_active_at', 'kyc_status', 'kyc_verified_at'
]
missing_columns = [col for col in required_columns if col not in columns]

if missing_columns:
    print(f"❌ 缺少列: {', '.join(missing_columns)}")
    print("   运行以下命令修复:")
    print("   bash fix-database.sh")
    sys.exit(1)
else:
    print("✅ 所有必需的列都存在")

# 检查 user_identities 表
if 'user_identities' not in inspector.get_table_names():
    print("❌ user_identities 表不存在")
    print("   运行以下命令修复:")
    print("   bash fix-database.sh")
    sys.exit(1)
else:
    print("✅ user_identities 表存在")

# 检查 account_links 表
if 'account_links' not in inspector.get_table_names():
    print("❌ account_links 表不存在")
    print("   运行以下命令修复:")
    print("   bash fix-database.sh")
    sys.exit(1)
else:
    print("✅ account_links 表存在")

print("")
print("✅ 数据库表结构检查通过！")
EOF

