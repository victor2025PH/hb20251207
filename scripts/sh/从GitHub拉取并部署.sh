#!/bin/bash
# 📥 从 GitHub 拉取代码并部署
# 使用方法: bash scripts/sh/从GitHub拉取并部署.sh [项目目录]

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
echo -e "${CYAN}  📥 从 GitHub 拉取代码并部署${NC}"
echo "=========================================="
echo ""

# 1. 检测项目目录
if [ -n "$1" ]; then
    PROJECT_DIR="$1"
elif [ -n "$LUCKYRED_DIR" ]; then
    PROJECT_DIR="$LUCKYRED_DIR"
elif [ -d "/opt/luckyred" ]; then
    PROJECT_DIR="/opt/luckyred"
elif [ -d "$HOME/luckyred" ]; then
    PROJECT_DIR="$HOME/luckyred"
else
    log_error "无法自动检测项目目录"
    echo "请使用以下方式之一："
    echo "  1. 传递目录参数: bash scripts/sh/从GitHub拉取并部署.sh /path/to/project"
    echo "  2. 设置环境变量: export LUCKYRED_DIR=/path/to/project"
    exit 1
fi

log_info "使用项目目录: $PROJECT_DIR"

if [ ! -d "$PROJECT_DIR" ]; then
    log_error "项目目录不存在: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR" || {
    log_error "无法进入项目目录: $PROJECT_DIR"
    exit 1
}

# 2. 检查 Git 仓库
log_step "检查 Git 仓库..."
if [ ! -d ".git" ]; then
    log_error "当前目录不是 Git 仓库"
    echo "请先克隆仓库："
    echo "  git clone https://github.com/victor2025PH/hoongbao1127.git $PROJECT_DIR"
    exit 1
fi

# 检查远程仓库
if ! git remote -v | grep -q "origin"; then
    log_error "未配置远程仓库"
    echo "请添加远程仓库："
    echo "  git remote add origin https://github.com/victor2025PH/hoongbao1127.git"
    exit 1
fi

# 3. 拉取最新代码
log_step "拉取最新代码..."
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "master")
log_info "当前分支: $CURRENT_BRANCH"

# 保存本地更改（如果有）
if ! git diff-index --quiet HEAD --; then
    log_warn "检测到未提交的更改，正在保存..."
    git stash save "自动保存于 $(date '+%Y-%m-%d %H:%M:%S')" || true
fi

# 拉取代码
if git pull origin "$CURRENT_BRANCH"; then
    log_info "代码拉取成功"
else
    log_error "代码拉取失败"
    exit 1
fi

# 4. 检查必要的工具
log_step "检查必要的工具..."
MISSING_TOOLS=()

command -v python3 >/dev/null 2>&1 || MISSING_TOOLS+=("python3")
command -v npm >/dev/null 2>&1 || MISSING_TOOLS+=("npm")

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    log_error "缺少必要的工具: ${MISSING_TOOLS[*]}"
    echo "请先安装这些工具"
    exit 1
fi

# 5. 安装/更新 API 依赖
log_step "安装 API 依赖..."
cd api
if [ ! -d ".venv" ]; then
    log_warn "虚拟环境不存在，正在创建..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
deactivate
log_info "API 依赖安装完成"
cd ..

# 6. 安装/更新 Bot 依赖
log_step "安装 Bot 依赖..."
cd bot
if [ ! -d ".venv" ]; then
    log_warn "虚拟环境不存在，正在创建..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
deactivate
log_info "Bot 依赖安装完成"
cd ..

# 7. 构建前端
log_step "构建前端..."
if [ ! -f "frontend/package.json" ]; then
    log_error "frontend/package.json 不存在"
    exit 1
fi

cd frontend
npm install --silent
npm run build
log_info "前端构建完成"
cd ..

# 8. 检测并重启服务
log_step "检测系统服务..."

# 检测服务名称
API_SERVICE=""
BOT_SERVICE=""

# 尝试常见的服务名称
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

# 重启服务（需要 root 权限）
if [ "$EUID" -eq 0 ]; then
    log_step "重启服务..."
    
    if [ -n "$API_SERVICE" ]; then
        if systemctl restart "$API_SERVICE" 2>/dev/null; then
            log_info "API 服务已重启: $API_SERVICE"
        else
            log_warn "API 服务重启失败: $API_SERVICE"
        fi
    else
        log_warn "未找到 API 服务"
    fi
    
    if [ -n "$BOT_SERVICE" ]; then
        if systemctl restart "$BOT_SERVICE" 2>/dev/null; then
            log_info "Bot 服务已重启: $BOT_SERVICE"
        else
            log_warn "Bot 服务重启失败: $BOT_SERVICE"
        fi
    else
        log_warn "未找到 Bot 服务"
    fi
    
    if systemctl is-active --quiet nginx 2>/dev/null; then
        systemctl reload nginx 2>/dev/null && log_info "Nginx 已重新加载" || log_warn "Nginx 重新加载失败"
    fi
else
    log_warn "当前用户没有 root 权限，无法重启服务"
    echo "请手动执行以下命令："
    if [ -n "$API_SERVICE" ]; then
        echo "  sudo systemctl restart $API_SERVICE"
    fi
    if [ -n "$BOT_SERVICE" ]; then
        echo "  sudo systemctl restart $BOT_SERVICE"
    fi
    echo "  sudo systemctl reload nginx"
fi

# 9. 检查服务状态
if [ "$EUID" -eq 0 ]; then
    log_step "检查服务状态..."
    echo ""
    if [ -n "$API_SERVICE" ]; then
        echo "--- API 服务状态 ---"
        systemctl status "$API_SERVICE" --no-pager | head -5 || true
        echo ""
    fi
    
    if [ -n "$BOT_SERVICE" ]; then
        echo "--- Bot 服务状态 ---"
        systemctl status "$BOT_SERVICE" --no-pager | head -5 || true
        echo ""
    fi
fi

echo "=========================================="
echo -e "${GREEN}  ✅ 部署完成！${NC}"
echo "=========================================="
echo ""
echo "📝 查看日志："
if [ -n "$API_SERVICE" ]; then
    echo "   API: sudo journalctl -u $API_SERVICE -f"
fi
if [ -n "$BOT_SERVICE" ]; then
    echo "   Bot: sudo journalctl -u $BOT_SERVICE -f"
fi
echo ""

