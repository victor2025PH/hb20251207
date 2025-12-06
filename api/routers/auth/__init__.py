"""
认证路由模块
"""
# 注意：为了避免循环导入，这里需要特殊处理
# api.routers.__init__.py 会导入 auth，这会导入这个 __init__.py
# 但我们需要导出 auth.py 文件中的 router

# 导出子路由（这些是包内的模块，可以安全导入）
from api.routers.auth import web, link

# 对于主 router，我们需要导入 auth.py 文件中的 router
# 使用 importlib 来避免循环导入
import sys
from pathlib import Path
import importlib.util

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 直接导入 auth.py 文件（不是包）
_auth_file_path = Path(__file__).parent.parent / "auth.py"
if _auth_file_path.exists():
    spec = importlib.util.spec_from_file_location("api.routers.auth_module", _auth_file_path)
    auth_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auth_module)
    router = auth_module.router
else:
    # 如果文件不存在，尝试从模块导入
    try:
        import api.routers.auth as auth_module
        router = auth_module.router
    except (ImportError, AttributeError):
        raise ImportError("Cannot import router from api.routers.auth")

__all__ = ["web", "link", "router"]

