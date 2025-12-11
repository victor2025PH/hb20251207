#!/bin/bash
# 🔧 更新 systemd 服务配置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

echo "=========================================="
echo -e "${BLUE}  🔧 更新 systemd 服务配置${NC}"
echo "=========================================="
echo ""

# 检查是否有 root 权限
if [ "$EUID" -ne 0 ]; then 
    log_error "请使用 sudo 运行此脚本"
    exit 1
fi

SERVICE_FILE="/etc/systemd/system/luckyred-api.service"
BACKUP_FILE="/etc/systemd/system/luckyred-api.service.backup.$(date +%Y%m%d_%H%M%S)"

log_step "1. 备份当前服务配置..."
if [ -f "$SERVICE_FILE" ]; then
    cp "$SERVICE_FILE" "$BACKUP_FILE"
    log_info "已备份到: $BACKUP_FILE"
else
    log_warn "服务文件不存在: $SERVICE_FILE"
fi
echo ""

log_step "2. 检查 PYTHONPATH 配置..."
if grep -q 'PYTHONPATH' "$SERVICE_FILE" 2>/dev/null; then
    log_info "PYTHONPATH 已配置"
else
    log_warn "PYTHONPATH 未配置，需要添加"
    
    # 检查是否有 Environment 行
    if grep -q '^Environment=' "$SERVICE_FILE"; then
        # 在第一个 Environment 行后添加 PYTHONPATH
        sed -i '/^Environment="PATH=/a Environment="PYTHONPATH=/home/ubuntu/hbgm001"' "$SERVICE_FILE"
    else
        # 在 WorkingDirectory 后添加
        sed -i '/^WorkingDirectory=/a Environment="PYTHONPATH=/home/ubuntu/hbgm001"' "$SERVICE_FILE"
    fi
    log_info "已添加 PYTHONPATH 配置"
fi
echo ""

log_step "3. 验证配置..."
if grep -q 'PYTHONPATH=/home/ubuntu/hbgm001' "$SERVICE_FILE"; then
    log_info "✅ PYTHONPATH 配置正确"
    echo ""
    echo "当前配置："
    grep -A 5 "\[Service\]" "$SERVICE_FILE" | grep -E "WorkingDirectory|Environment|ExecStart"
else
    log_error "❌ PYTHONPATH 配置失败"
    exit 1
fi
echo ""

log_step "4. 重新加载 systemd 配置..."
systemctl daemon-reload
log_info "✅ systemd 配置已重新加载"
echo ""

log_step "5. 重启服务..."
systemctl restart luckyred-api
log_info "✅ 服务已重启"
echo ""

log_step "6. 等待服务启动..."
sleep 5
echo ""

log_step "7. 检查服务状态..."
if systemctl is-active --quiet luckyred-api; then
    log_info "✅ 服务运行正常"
    systemctl status luckyred-api --no-pager | head -10
else
    log_error "❌ 服务启动失败"
    echo ""
    echo "查看错误日志："
    journalctl -u luckyred-api -n 30 --no-pager
    exit 1
fi
echo ""

log_step "8. 测试健康检查..."
if curl -s http://localhost:8080/health >/dev/null 2>&1; then
    log_info "✅ 健康检查通过"
    curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8080/health
else
    log_warn "⚠️  健康检查失败，服务可能还在启动中"
fi
echo ""

echo "=========================================="
log_info "✅ 更新完成！"
echo "=========================================="

