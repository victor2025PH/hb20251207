#!/bin/bash
# 诊断任务显示问题
# 在服务器上执行: bash scripts/sh/diagnose-tasks-issue.sh

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
echo "   任务系统诊断"
echo "========================================"
echo ""

# 1. 检查API路由注册
log_test "[1/7] 检查API路由注册..."
if grep -q "tasks.router" "$PROJECT_DIR/api/main.py"; then
    log_info "✓ tasks路由已注册"
    grep -n "tasks.router" "$PROJECT_DIR/api/main.py"
else
    log_error "✗ tasks路由未注册"
fi

# 2. 测试API（使用GET方法）
log_test "[2/7] 测试任务API（GET方法）..."
TASK_RESPONSE=$(curl -s "$API_URL/api/v1/tasks/status" || echo "ERROR")
TASK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/v1/tasks/status" || echo "000")

if [ "$TASK_STATUS" = "401" ]; then
    log_info "✓ 任务API正常 (HTTP 401 - 需要认证，这是正常的)"
    log_info "  响应: $TASK_RESPONSE"
elif [ "$TASK_STATUS" = "200" ]; then
    log_info "✓ 任务API正常 (HTTP 200)"
    echo "$TASK_RESPONSE" | head -5
elif [ "$TASK_STATUS" = "404" ]; then
    log_error "✗ 任务API返回404 - 路由未找到"
    log_info "检查路由注册..."
    grep -n "tasks" "$PROJECT_DIR/api/main.py" || log_error "未找到tasks路由"
elif [ "$TASK_STATUS" = "405" ]; then
    log_warn "⚠ 返回405 - 可能是方法问题，测试GET方法..."
    TASK_RESPONSE2=$(curl -s -X GET "$API_URL/api/v1/tasks/status" || echo "ERROR")
    TASK_STATUS2=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$API_URL/api/v1/tasks/status" || echo "000")
    if [ "$TASK_STATUS2" = "401" ] || [ "$TASK_STATUS2" = "200" ]; then
        log_info "✓ GET方法正常 (HTTP $TASK_STATUS2)"
    else
        log_error "✗ GET方法也返回: HTTP $TASK_STATUS2"
    fi
else
    log_error "✗ 任务API返回: HTTP $TASK_STATUS"
    log_info "响应: $TASK_RESPONSE"
fi

# 3. 检查API服务状态
log_test "[3/7] 检查API服务状态..."
if systemctl is-active --quiet luckyred-api; then
    log_info "✓ API服务运行正常"
    PID=$(systemctl show -p MainPID --value luckyred-api)
    log_info "  PID: $PID"
else
    log_error "✗ API服务未运行"
    exit 1
fi

# 4. 检查API日志中的错误
log_test "[4/7] 检查API日志（最近50条）..."
RECENT_ERRORS=$(journalctl -u luckyred-api -n 50 --no-pager 2>/dev/null | grep -i "error\|exception\|traceback" | grep -v "WebSocket router not available" | grep -v "SyntaxWarning" || echo "")
if [ -z "$RECENT_ERRORS" ]; then
    log_info "✓ API日志无严重错误"
else
    log_warn "⚠ 发现错误日志:"
    echo "$RECENT_ERRORS" | head -5
fi

# 5. 检查数据库表
log_test "[5/7] 检查数据库表..."
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

# 6. 测试模块导入和路由
log_test "[6/7] 测试模块导入..."
cd "$PROJECT_DIR/api"
source .venv/bin/activate
cd "$PROJECT_DIR"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    from api.routers import tasks
    print("✓ tasks模块导入成功")
    
    # 检查路由
    routes = tasks.router.routes
    print(f"  路由数量: {len(routes)}")
    
    # 查找status路由
    status_route = None
    for route in routes:
        if hasattr(route, 'path') and 'status' in route.path:
            status_route = route
            methods = list(route.methods) if hasattr(route, 'methods') else []
            print(f"  ✓ 找到status路由: {route.path} (方法: {methods})")
            break
    
    if not status_route:
        print("  ✗ 未找到status路由")
        sys.exit(1)
        
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

# 7. 检查前端文件
log_test "[7/7] 检查前端文件..."
if [ -f "$PROJECT_DIR/frontend/dist/index.html" ]; then
    log_info "✓ 前端已构建"
    if [ -f "$PROJECT_DIR/frontend/src/pages/TasksPage.tsx" ]; then
        log_info "✓ TasksPage.tsx存在"
    else
        log_warn "⚠ TasksPage.tsx不存在"
    fi
else
    log_warn "⚠ 前端未构建，需要运行: cd frontend && npm run build"
fi

echo ""
echo "========================================"
log_info "诊断完成！"
echo "========================================"
echo ""
echo "📋 下一步："
echo "  1. 如果API返回401，说明API正常（需要认证）"
echo "  2. 访问 https://mini.usdt2026.cc/tasks"
echo "  3. 打开浏览器开发者工具（F12），查看Network标签"
echo "  4. 检查API请求URL和响应"
echo ""

