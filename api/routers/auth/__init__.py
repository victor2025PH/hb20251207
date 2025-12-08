"""
认证路由模块
"""

# 注意：为了避免循环导入，这里需要特殊处理
# 当 api.routers.__init__.py 执行 `from api.routers import auth` 时
# Python 会优先导入这个 __init__.py（因为存在 auth/ 目录）
# 但我们需要导出 auth.py 文件中的 router

# 导出子路由（这些是包内的模块，可以安全导入）
from api.routers.auth import web, link

# 对于主 router，我们需要从父目录的 auth.py 文件导入
# 使用相对导入路径来避免循环
import sys
from pathlib import Path

# 添加项目根目录到路径
_project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_project_root))

# 直接导入 auth.py 模块（使用绝对导入，避免包导入）
_auth_module = None
try:
    # 使用 importlib 直接加载 auth.py 文件
    import importlib.util

    _auth_file = Path(__file__).parent.parent / "auth.py"
    if _auth_file.exists():
        spec = importlib.util.spec_from_file_location(
            "api.routers.auth_file", _auth_file, submodule_search_locations=[]
        )
        _auth_module = importlib.util.module_from_spec(spec)
        sys.modules["api.routers.auth_file"] = _auth_module
        spec.loader.exec_module(_auth_module)
        router = _auth_module.router
        get_current_user_from_token = _auth_module.get_current_user_from_token
        decode_jwt_token = _auth_module.decode_jwt_token
    else:
        raise ImportError(f"auth.py not found at {_auth_file}")
except Exception as e:
    # 如果上述方法失败，尝试直接导入（可能会循环导入，但至少能工作）
    try:
        # 临时移除这个模块，避免循环导入检测
        _temp = sys.modules.get("api.routers.auth")
        if "api.routers.auth" in sys.modules:
            del sys.modules["api.routers.auth"]
        # 现在导入 auth.py 文件
        from api.routers import auth as _auth_file_module

        router = _auth_file_module.router
        get_current_user_from_token = _auth_file_module.get_current_user_from_token
        decode_jwt_token = _auth_file_module.decode_jwt_token
        _auth_module = _auth_file_module
        # 恢复模块
        if _temp:
            sys.modules["api.routers.auth"] = _temp
    except Exception as e2:
        raise ImportError(f"Cannot import from auth.py: {e}, {e2}")

__all__ = ["web", "link", "router", "get_current_user_from_token", "decode_jwt_token"]
