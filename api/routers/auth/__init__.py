"""
认证路由模块
"""
# 导出create_access_token和TokenResponse供其他模块使用
# 注意：auth.py在routers目录下，不在auth子目录
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.routers.auth import create_access_token, TokenResponse

__all__ = ["create_access_token", "TokenResponse"]

