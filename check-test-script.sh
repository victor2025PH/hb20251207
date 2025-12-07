#!/bin/bash
# 检查测试脚本是否存在并运行

set -e

echo "=========================================="
echo "检查测试脚本"
echo "=========================================="

cd /opt/luckyred

# 1. 检查是否在正确的目录
echo "当前目录: $(pwd)"

# 2. 拉取最新代码
echo ""
echo "步骤 1: 拉取最新代码..."
git pull origin master

# 3. 检查文件是否存在
echo ""
echo "步骤 2: 检查测试脚本..."
if [ -f "scripts/py/test_all_login_methods.py" ]; then
    echo "✅ 测试脚本存在: scripts/py/test_all_login_methods.py"
    ls -lh scripts/py/test_all_login_methods.py
else
    echo "❌ 测试脚本不存在"
    echo "检查 scripts/py 目录内容:"
    ls -la scripts/py/ | head -20
    exit 1
fi

# 4. 检查 Python 依赖
echo ""
echo "步骤 3: 检查 Python 依赖..."
python3 -c "import httpx" 2>/dev/null || {
    echo "⚠️  httpx 未安装，正在安装..."
    pip3 install httpx
}

# 5. 运行测试
echo ""
echo "步骤 4: 运行测试脚本..."
python3 scripts/py/test_all_login_methods.py

