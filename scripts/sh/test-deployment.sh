#!/bin/bash
# 🧪 部署测试脚本
# 用于验证服务器部署流程是否正常

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
log_test() { echo -e "${CYAN}[TEST]${NC} $1"; }

echo "=========================================="
echo -e "${CYAN}  🧪 部署测试脚本${NC}"
echo "=========================================="
echo ""

# 检测项目目录
PROJECT_DIR=""
if [ -n "$1" ]; then
    PROJECT_DIR="$1"
elif [ -n "$LUCKYRED_DIR" ]; then
    PROJECT_DIR="$LUCKYRED_DIR"
elif [ -d "/opt/luckyred" ]; then
    PROJECT_DIR="/opt/luckyred"
else
    log_error "无法确定项目目录"
    exit 1
fi

log_info "项目目录: $PROJECT_DIR"
cd "$PROJECT_DIR"

# 测试结果
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
test_check() {
    local test_name="$1"
    local command="$2"
    
    log_test "测试: $test_name"
    if eval "$command" >/dev/null 2>&1; then
        log_info "✅ $test_name - 通过"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "❌ $test_name - 失败"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# 1. Git 仓库测试
log_step "1. Git 仓库测试"
test_check "Git 仓库存在" "[ -d .git ]"
test_check "远程仓库配置" "git remote -v | grep -q origin"
test_check "当前分支" "git branch --show-current"

# 2. 目录结构测试
log_step "2. 目录结构测试"
test_check "API 目录存在" "[ -d api ]"
test_check "Bot 目录存在" "[ -d bot ]"
test_check "Frontend 目录存在" "[ -d frontend ]"
test_check "部署脚本存在" "[ -f scripts/sh/pull-and-deploy.sh ]"

# 3. 依赖文件测试
log_step "3. 依赖文件测试"
test_check "API requirements.txt" "[ -f api/requirements.txt ]"
test_check "Bot requirements.txt" "[ -f bot/requirements.txt ]"
test_check "Frontend package.json" "[ -f frontend/package.json ]"

# 4. 虚拟环境测试
log_step "4. 虚拟环境测试"
if [ -d "api/.venv" ]; then
    test_check "API 虚拟环境存在" "[ -f api/.venv/bin/activate ]"
else
    log_warn "API 虚拟环境不存在（将在部署时创建）"
fi

if [ -d "bot/.venv" ]; then
    test_check "Bot 虚拟环境存在" "[ -f bot/.venv/bin/activate ]"
else
    log_warn "Bot 虚拟环境不存在（将在部署时创建）"
fi

# 5. 前端构建测试
log_step "5. 前端构建测试"
if [ -d "frontend/dist" ]; then
    test_check "前端构建目录存在" "[ -d frontend/dist ]"
    test_check "前端构建文件存在" "[ -f frontend/dist/index.html ]"
else
    log_warn "前端未构建（将在部署时构建）"
fi

# 6. 服务状态测试
log_step "6. 服务状态测试"
if [ "$EUID" -eq 0 ]; then
    # 检测服务名称
    API_SERVICE=""
    BOT_SERVICE=""
    
    for service in luckyred-api api-luckyred luckyred-api.service; do
        if systemctl list-units --all --type=service 2>/dev/null | grep -q "$service"; then
            API_SERVICE="$service"
            break
        fi
    done
    
    for service in luckyred-bot bot-luckyred luckyred-bot.service; do
        if systemctl list-units --all --type=service 2>/dev/null | grep -q "$service"; then
            BOT_SERVICE="$service"
            break
        fi
    done
    
    if [ -n "$API_SERVICE" ]; then
        if systemctl is-active --quiet "$API_SERVICE" 2>/dev/null; then
            log_info "✅ API 服务运行中: $API_SERVICE"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            log_warn "⚠️  API 服务未运行: $API_SERVICE"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        log_warn "⚠️  未找到 API 服务"
    fi
    
    if [ -n "$BOT_SERVICE" ]; then
        if systemctl is-active --quiet "$BOT_SERVICE" 2>/dev/null; then
            log_info "✅ Bot 服务运行中: $BOT_SERVICE"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            log_warn "⚠️  Bot 服务未运行: $BOT_SERVICE"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        log_warn "⚠️  未找到 Bot 服务"
    fi
    
    if systemctl is-active --quiet nginx 2>/dev/null; then
        log_info "✅ Nginx 运行中"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_warn "⚠️  Nginx 未运行"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    log_warn "需要 root 权限来检查服务状态"
fi

# 7. API 健康检查
log_step "7. API 健康检查"
if [ -n "$API_SERVICE" ] && systemctl is-active --quiet "$API_SERVICE" 2>/dev/null; then
    if curl -s http://localhost:8080/health >/dev/null 2>&1; then
        log_info "✅ API 健康检查通过"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_warn "⚠️  API 健康检查失败"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    log_warn "⚠️  跳过 API 健康检查（服务未运行）"
fi

# 8. 端口测试
log_step "8. 端口测试"
if command -v netstat >/dev/null 2>&1 || command -v ss >/dev/null 2>&1; then
    if command -v ss >/dev/null 2>&1; then
        PORT_CHECK="ss -tlnp | grep"
    else
        PORT_CHECK="netstat -tlnp | grep"
    fi
    
    if eval "$PORT_CHECK :8080" >/dev/null 2>&1; then
        log_info "✅ 端口 8080 已监听"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_warn "⚠️  端口 8080 未监听"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    log_warn "⚠️  无法检查端口（netstat/ss 未安装）"
fi

# 9. 环境变量测试
log_step "9. 环境变量测试"
if [ -f ".env" ]; then
    log_info "✅ .env 文件存在"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    
    # 检查关键环境变量
    if grep -q "DATABASE_URL" .env 2>/dev/null; then
        log_info "✅ DATABASE_URL 已配置"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_warn "⚠️  DATABASE_URL 未配置"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    
    if grep -q "BOT_TOKEN" .env 2>/dev/null; then
        log_info "✅ BOT_TOKEN 已配置"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_warn "⚠️  BOT_TOKEN 未配置"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
else
    log_warn "⚠️  .env 文件不存在"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# 10. 权限测试
log_step "10. 权限测试"
if [ -w "$PROJECT_DIR" ]; then
    log_info "✅ 项目目录可写"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    log_warn "⚠️  项目目录不可写"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# 总结
echo ""
echo "=========================================="
echo -e "${CYAN}  测试总结${NC}"
echo "=========================================="
echo -e "${GREEN}通过: $TESTS_PASSED${NC}"
echo -e "${RED}失败: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    log_info "🎉 所有测试通过！"
    exit 0
else
    log_warn "⚠️  有 $TESTS_FAILED 个测试失败"
    exit 1
fi

