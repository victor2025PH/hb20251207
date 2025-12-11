#!/bin/bash
# 虚拟环境诊断脚本
# 用于诊断服务器上的虚拟环境问题

set -e

PROJECT_DIR="/home/ubuntu/hbgm001"
VENV_DIR="/home/ubuntu/hbgm001/api/.venv"

echo "=========================================="
echo "虚拟环境诊断报告"
echo "=========================================="
echo ""

echo "📁 项目目录: $PROJECT_DIR"
echo "🐍 虚拟环境目录: $VENV_DIR"
echo "👤 当前用户: $(whoami)"
echo "📂 当前目录: $(pwd)"
echo ""

# 检查项目目录
echo "=========================================="
echo "1. 检查项目目录"
echo "=========================================="
if [ -d "$PROJECT_DIR" ]; then
    echo "✅ 项目目录存在"
    echo "   权限: $(ls -ld "$PROJECT_DIR" | awk '{print $1, $3, $4}')"
else
    echo "❌ 项目目录不存在"
fi
echo ""

# 检查 api 目录
echo "=========================================="
echo "2. 检查 api 目录"
echo "=========================================="
if [ -d "$PROJECT_DIR/api" ]; then
    echo "✅ api 目录存在"
    echo "   权限: $(ls -ld "$PROJECT_DIR/api" | awk '{print $1, $3, $4}')"
    echo "   内容:"
    ls -la "$PROJECT_DIR/api" | head -10 || echo "   无法列出内容"
else
    echo "❌ api 目录不存在"
fi
echo ""

# 检查虚拟环境目录
echo "=========================================="
echo "3. 检查虚拟环境目录"
echo "=========================================="
if [ -d "$VENV_DIR" ]; then
    echo "✅ 虚拟环境目录存在"
    echo "   权限: $(ls -ld "$VENV_DIR" | awk '{print $1, $3, $4}')"
    echo "   大小: $(du -sh "$VENV_DIR" 2>/dev/null | awk '{print $1}' || echo '无法获取')"
    echo "   内容:"
    ls -la "$VENV_DIR" | head -10 || echo "   无法列出内容"
else
    echo "❌ 虚拟环境目录不存在"
fi
echo ""

# 检查 bin 目录
echo "=========================================="
echo "4. 检查 bin 目录"
echo "=========================================="
if [ -d "$VENV_DIR/bin" ]; then
    echo "✅ bin 目录存在"
    echo "   权限: $(ls -ld "$VENV_DIR/bin" | awk '{print $1, $3, $4}')"
    echo "   内容:"
    ls -la "$VENV_DIR/bin" | head -10 || echo "   无法列出内容"
else
    echo "❌ bin 目录不存在"
fi
echo ""

# 检查 activate 文件
echo "=========================================="
echo "5. 检查 activate 文件"
echo "=========================================="
if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "✅ activate 文件存在"
    echo "   权限: $(ls -l "$VENV_DIR/bin/activate" | awk '{print $1, $9}')"
    echo "   大小: $(ls -lh "$VENV_DIR/bin/activate" | awk '{print $5}')"
    echo "   前5行内容:"
    head -n 5 "$VENV_DIR/bin/activate" || echo "   无法读取内容"
else
    echo "❌ activate 文件不存在"
    echo "   这是问题的根源！"
fi
echo ""

# 检查 Python3
echo "=========================================="
echo "6. 检查 Python3"
echo "=========================================="
if command -v python3 &> /dev/null; then
    echo "✅ Python3 已安装"
    echo "   路径: $(which python3)"
    echo "   版本: $(python3 --version)"
    
    # 检查 venv 模块
    if python3 -m venv --help >/dev/null 2>&1; then
        echo "✅ python3-venv 模块可用"
    else
        echo "❌ python3-venv 模块不可用"
        echo "   需要安装: sudo apt-get install -y python3-venv"
    fi
else
    echo "❌ Python3 未安装"
fi
echo ""

# 尝试激活虚拟环境
echo "=========================================="
echo "7. 尝试激活虚拟环境"
echo "=========================================="
if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "尝试 source $VENV_DIR/bin/activate"
    source "$VENV_DIR/bin/activate" 2>&1 && {
        echo "✅ 虚拟环境激活成功"
        echo "   Python 路径: $(which python)"
        echo "   Python 版本: $(python --version)"
        echo "   pip 路径: $(which pip)"
        echo "   pip 版本: $(pip --version)"
    } || {
        echo "❌ 虚拟环境激活失败"
        echo "   错误信息: $?"
    }
else
    echo "⚠️  跳过激活测试（activate 文件不存在）"
fi
echo ""

# 总结
echo "=========================================="
echo "诊断总结"
echo "=========================================="
if [ -f "$VENV_DIR/bin/activate" ]; then
    echo "✅ 虚拟环境看起来正常"
else
    echo "❌ 虚拟环境损坏或不存在"
    echo ""
    echo "建议操作:"
    echo "1. 删除损坏的虚拟环境:"
    echo "   sudo rm -rf $VENV_DIR"
    echo ""
    echo "2. 确保 python3-venv 已安装:"
    echo "   sudo apt-get update && sudo apt-get install -y python3-venv"
    echo ""
    echo "3. 重新创建虚拟环境:"
    echo "   python3 -m venv $VENV_DIR"
    echo ""
    echo "4. 修复权限:"
    echo "   sudo chown -R \$USER:\$USER $VENV_DIR"
fi
echo ""

