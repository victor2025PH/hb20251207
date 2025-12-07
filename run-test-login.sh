#!/bin/bash
# 运行登录方式测试脚本（包含依赖安装）

set -e

echo "=========================================="
echo "运行登录方式测试"
echo "=========================================="

# 在服务器 ubuntu@10-11-156-159 上执行：

# 方案一：一键化指令（使用 API 虚拟环境）
cd /opt/luckyred && git pull origin master && \
if [ -f "api/.venv/bin/pip" ]; then \
  api/.venv/bin/pip install httpx && \
  api/.venv/bin/python scripts/py/test_all_login_methods.py; \
else \
  python3 -m pip install --user httpx && \
  python3 scripts/py/test_all_login_methods.py; \
fi

# 如果上述命令失败，使用以下分步执行：
# 步骤 1: 进入项目目录
# cd /opt/luckyred
# 步骤 2: 拉取最新代码
# git pull origin master
# 步骤 3: 检查并使用虚拟环境或用户安装
# if [ -f "api/.venv/bin/pip" ]; then
#   api/.venv/bin/pip install httpx
#   api/.venv/bin/python scripts/py/test_all_login_methods.py
# else
#   python3 -m pip install --user httpx
#   python3 scripts/py/test_all_login_methods.py
# fi

