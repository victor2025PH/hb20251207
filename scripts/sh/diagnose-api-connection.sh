#!/bin/bash
# 🔍 API 连接诊断脚本
# 用于诊断 API 服务连接问题

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

echo "=========================================="
echo -e "${CYAN}  🔍 API 连接诊断${NC}"
echo "=========================================="
echo ""

# 1. 检查服务状态
log_step "1. 检查服务状态..."
if systemctl is-active --quiet luckyred-api 2>/dev/null; then
    log_info "✅ API 服务正在运行"
    systemctl status luckyred-api --no-pager | head -5
else
    log_error "❌ API 服务未运行"
    echo "尝试启动服务..."
    sudo systemctl start luckyred-api
    sleep 3
fi
echo ""

# 2. 检查端口监听
log_step "2. 检查端口监听..."
if command -v ss >/dev/null 2>&1; then
    PORT_CHECK="ss -tlnp"
else
    PORT_CHECK="netstat -tlnp"
fi

if $PORT_CHECK 2>/dev/null | grep -q ":8080"; then
    log_info "✅ 端口 8080 正在监听"
    $PORT_CHECK 2>/dev/null | grep ":8080"
else
    log_error "❌ 端口 8080 未监听"
    log_warn "服务可能还在启动中，请等待几秒后重试"
fi
echo ""

# 3. 检查进程
log_step "3. 检查进程..."
if pgrep -f "uvicorn.*main:app" >/dev/null; then
    log_info "✅ uvicorn 进程正在运行"
    ps aux | grep "uvicorn.*main:app" | grep -v grep
else
    log_error "❌ uvicorn 进程未运行"
fi
echo ""

# 4. 测试连接
log_step "4. 测试连接..."
for i in {1..5}; do
    if curl -s http://localhost:8080/health >/dev/null 2>&1; then
        log_info "✅ API 连接成功"
        curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8080/health
        break
    else
        if [ $i -lt 5 ]; then
            log_warn "⚠️  连接失败，等待 ${i} 秒后重试..."
            sleep $i
        else
            log_error "❌ API 连接失败（已重试 5 次）"
        fi
    fi
done
echo ""

# 5. 检查日志
log_step "5. 检查最近日志..."
log_info "最近 20 行日志："
sudo journalctl -u luckyred-api -n 20 --no-pager 2>/dev/null || log_warn "无法查看日志（需要 sudo 权限）"
echo ""

# 6. 检查错误
log_step "6. 检查错误日志..."
ERROR_COUNT=$(sudo journalctl -u luckyred-api --no-pager 2>/dev/null | grep -i error | wc -l)
if [ "$ERROR_COUNT" -gt 0 ]; then
    log_warn "⚠️  发现 $ERROR_COUNT 个错误日志"
    sudo journalctl -u luckyred-api --no-pager 2>/dev/null | grep -i error | tail -5
else
    log_info "✅ 没有发现错误日志"
fi
echo ""

# 7. 检查配置文件
log_step "7. 检查配置文件..."
if [ -f "/opt/luckyred/.env" ]; then
    log_info "✅ .env 文件存在"
    if grep -q "DATABASE_URL" /opt/luckyred/.env 2>/dev/null; then
        log_info "✅ DATABASE_URL 已配置"
    else
        log_warn "⚠️  DATABASE_URL 未配置"
    fi
else
    log_error "❌ .env 文件不存在"
fi
echo ""

# 8. 检查数据库连接
log_step "8. 检查数据库连接..."
if command -v psql >/dev/null 2>&1; then
    if sudo -u postgres psql -d luckyred -c "SELECT 1;" >/dev/null 2>&1; then
        log_info "✅ 数据库连接正常"
    else
        log_error "❌ 数据库连接失败"
    fi
else
    log_warn "⚠️  psql 未安装，跳过数据库检查"
fi
echo ""

# 总结
echo "=========================================="
echo -e "${CYAN}  诊断完成${NC}"
echo "=========================================="
echo ""
log_info "如果 API 连接仍然失败，请："
echo "  1. 查看详细日志: sudo journalctl -u luckyred-api -f"
echo "  2. 手动启动测试: cd /opt/luckyred/api && source .venv/bin/activate && uvicorn main:app --host 127.0.0.1 --port 8080"
echo "  3. 检查配置文件: cat /opt/luckyred/.env"
echo ""

