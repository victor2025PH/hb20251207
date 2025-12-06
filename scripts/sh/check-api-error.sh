#!/bin/bash
# 检查API启动错误
# 在服务器上执行: bash scripts/sh/check-api-error.sh

set -e

PROJECT_DIR="/opt/luckyred"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "========================================"
echo "   检查API启动错误"
echo "========================================"
echo ""

cd "$PROJECT_DIR"

# 1. 检查服务状态
log_info "[1/5] 检查服务状态..."
sudo systemctl status luckyred-api --no-pager -l | tail -20

# 2. 查看最近的错误日志
log_info "[2/5] 查看最近的错误日志..."
sudo journalctl -u luckyred-api -n 50 --no-pager | tail -30

# 3. 尝试手动启动（查看详细错误）
log_info "[3/5] 尝试手动启动（查看详细错误）..."
cd "$PROJECT_DIR/api"
source .venv/bin/activate
cd "$PROJECT_DIR"

# 检查Python语法
log_info "[4/5] 检查Python语法..."
python3 -m py_compile api/routers/checkin.py 2>&1 || log_error "语法错误！"
python3 -m py_compile api/main.py 2>&1 || log_error "语法错误！"

# 检查导入
log_info "[5/5] 检查模块导入..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/opt/luckyred')
try:
    from api.routers import checkin
    print("✓ checkin模块导入成功")
    
    from api.main import app
    print("✓ main模块导入成功")
    
    # 检查路由
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    checkin_routes = [r for r in routes if 'checkin' in r]
    print(f"✓ 找到checkin路由: {checkin_routes}")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

echo ""
echo "========================================"
log_info "检查完成！"
echo "========================================"
echo ""
echo "如果看到错误，请把错误信息发给我"
echo ""

