#!/bin/bash
# 🔍 检查 API 启动错误

echo "=========================================="
echo "  🔍 检查 API 启动错误"
echo "=========================================="
echo ""

# 查看最近 100 行日志
echo "📋 最近 100 行日志："
echo "----------------------------------------"
sudo journalctl -u luckyred-api -n 100 --no-pager | tail -50
echo ""

# 查看错误信息
echo "❌ 错误信息："
echo "----------------------------------------"
sudo journalctl -u luckyred-api --no-pager | grep -i "error\|exception\|traceback\|attributeerror\|importerror" | tail -30
echo ""

# 尝试手动导入测试
echo "🧪 尝试手动导入测试："
echo "----------------------------------------"
cd /opt/luckyred/api
source .venv/bin/activate
cd /opt/luckyred  # 从项目根目录测试
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from api.routers import auth
    print('✅ api.routers.auth 导入成功')
    print(f'   auth 类型: {type(auth)}')
    if hasattr(auth, 'router'):
        print('✅ auth.router 存在')
        print(f'   router 类型: {type(auth.router)}')
    else:
        print('❌ auth.router 不存在')
        print(f'   auth 的属性: {dir(auth)}')
except Exception as e:
    print(f'❌ 导入失败: {e}')
    import traceback
    traceback.print_exc()
" 2>&1

