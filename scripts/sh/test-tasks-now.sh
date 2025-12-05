#!/bin/bash
# 立即测试任务功能
# 在服务器上执行: bash scripts/sh/test-tasks-now.sh

set -e

PROJECT_DIR="/opt/luckyred"
API_URL="http://localhost:8080"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_test() { echo -e "${BLUE}[TEST]${NC} $1"; }

echo "========================================"
echo "   任务红包系统 - 功能测试"
echo "========================================"
echo ""

# 测试1: API服务状态
log_test "[1/6] 检查API服务状态..."
if systemctl is-active --quiet luckyred-api; then
    log_info "✓ API服务运行正常"
else
    log_error "✗ API服务未运行"
    exit 1
fi

# 测试2: 任务API路由
log_test "[2/6] 测试任务API路由..."
TASK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/tasks/status" || echo "000")
if [ "$TASK_STATUS" = "401" ]; then
    log_info "✓ 任务API路由正常 (HTTP 401 - 需要认证，这是正常的)"
elif [ "$TASK_STATUS" = "200" ]; then
    log_info "✓ 任务API路由正常 (HTTP 200)"
elif [ "$TASK_STATUS" = "405" ]; then
    log_info "✓ 任务API路由存在 (HTTP 405 - 方法不允许)"
else
    log_error "✗ 任务API返回: HTTP $TASK_STATUS"
fi

# 测试3: 检查API日志中的错误
log_test "[3/6] 检查API启动日志..."
RECENT_ERRORS=$(journalctl -u luckyred-api -n 50 --no-pager 2>/dev/null | grep -i "error\|exception\|traceback" | grep -v "WebSocket router not available" | grep -v "SyntaxWarning" || echo "")
if [ -z "$RECENT_ERRORS" ]; then
    log_info "✓ API启动无严重错误"
else
    log_warn "⚠ 发现错误日志:"
    echo "$RECENT_ERRORS" | head -3
fi

# 测试4: 检查数据库表
log_test "[4/6] 检查数据库表..."
cd "$PROJECT_DIR/api"
source .venv/bin/activate
cd "$PROJECT_DIR"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from sqlalchemy import inspect
from shared.database.connection import sync_engine

try:
    inspector = inspect(sync_engine)
    tables = inspector.get_table_names()
    
    required_tables = ['task_completions', 'red_packets', 'users']
    all_exist = True
    
    for table in required_tables:
        if table in tables:
            print(f"✓ 表 {table} 存在")
        else:
            print(f"✗ 表 {table} 不存在")
            all_exist = False
    
    # 检查字段
    if 'red_packets' in tables:
        columns = [col['name'] for col in inspector.get_columns('red_packets')]
        fields = ['visibility', 'source_type', 'task_type']
        for field in fields:
            if field in columns:
                print(f"✓ red_packets.{field} 字段存在")
            else:
                print(f"✗ red_packets.{field} 字段不存在")
                all_exist = False
    
    if 'users' in tables:
        columns = [col['name'] for col in inspector.get_columns('users')]
        if 'share_count' in columns:
            print(f"✓ users.share_count 字段存在")
        else:
            print(f"✗ users.share_count 字段不存在")
            all_exist = False
    
    if not all_exist:
        sys.exit(1)
except Exception as e:
    print(f"✗ 数据库检查失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    log_info "✓ 数据库表检查通过"
else
    log_error "✗ 数据库表检查失败"
fi
deactivate

# 测试5: 测试模块导入
log_test "[5/6] 测试模块导入..."
cd "$PROJECT_DIR/api"
source .venv/bin/activate
cd "$PROJECT_DIR"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    from api.routers import tasks, share
    print("✓ tasks模块导入成功")
    print("✓ share模块导入成功")
    
    # 检查任务配置
    print(f"  每日任务: {len(tasks.DAILY_TASKS)} 个")
    print(f"  成就任务: {len(tasks.ACHIEVEMENT_TASKS)} 个")
except Exception as e:
    print(f"✗ 模块导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF

if [ $? -eq 0 ]; then
    log_info "✓ 模块导入测试通过"
else
    log_error "✗ 模块导入测试失败"
fi
deactivate

# 测试6: 检查前端文件
log_test "[6/6] 检查前端文件..."
if [ -f "$PROJECT_DIR/frontend/dist/index.html" ]; then
    log_info "✓ 前端index.html存在"
    if [ -f "$PROJECT_DIR/frontend/src/pages/TasksPage.tsx" ]; then
        log_info "✓ TasksPage.tsx存在"
    else
        log_warn "⚠ TasksPage.tsx不存在"
    fi
else
    log_warn "⚠ 前端文件不存在，需要构建"
fi

echo ""
echo "========================================"
log_info "✅ 测试完成！"
echo "========================================"
echo ""
echo "📋 下一步测试："
echo "  1. 访问 https://mini.usdt2026.cc/tasks 查看任务页面"
echo "  2. 测试签到功能，检查是否出错"
echo "  3. 检查任务列表是否显示"
echo "  4. 完成签到后，检查任务是否自动完成"
echo ""
echo "🔍 如果任务不显示，查看API日志："
echo "  sudo journalctl -u luckyred-api -f"
echo ""

