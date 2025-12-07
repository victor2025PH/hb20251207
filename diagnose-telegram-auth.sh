#!/bin/bash
# 诊断 Telegram 认证问题

set -e

echo "=========================================="
echo "Telegram 认证诊断工具"
echo "=========================================="

# 确保在项目根目录
cd "$(dirname "$0")"

# 检查 Python 环境
if [ -f "api/.venv/bin/python" ]; then
  PYTHON_EXEC="api/.venv/bin/python"
  echo "使用 API 虚拟环境"
else
  PYTHON_EXEC="python3"
  echo "使用系统 Python"
fi

# 运行诊断脚本
echo ""
echo "运行诊断脚本..."
$PYTHON_EXEC scripts/py/diagnose_telegram_auth.py

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="

