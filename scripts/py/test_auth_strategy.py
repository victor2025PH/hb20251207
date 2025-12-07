"""
测试认证策略选择功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import Request
from api.utils.auth_strategy import get_auth_strategy, should_allow_telegram_auth, should_allow_jwt_auth


def create_mock_request(host: str, referer: str = "") -> Request:
    """创建模拟请求对象"""
    from unittest.mock import Mock
    
    mock_request = Mock(spec=Request)
    mock_request.headers = {
        "host": host,
        "referer": referer
    }
    return mock_request


def test_auth_strategies():
    """测试认证策略选择"""
    print("=" * 60)
    print("测试认证策略选择功能")
    print("=" * 60)
    
    test_cases = [
        # (host, referer, expected_strategy, description)
        ("mini.usdt2026.cc", "", "telegram_first", "MiniApp 域名"),
        ("mini.usdt2026.cc:443", "", "telegram_first", "MiniApp 域名（带端口）"),
        ("admin.usdt2026.cc", "", "jwt_only", "Admin 域名"),
        ("admin.usdt2026.cc:443", "", "jwt_only", "Admin 域名（带端口）"),
        ("localhost:5173", "", "telegram_first", "开发环境 MiniApp"),
        ("localhost:5174", "", "jwt_only", "开发环境 Admin"),
        ("example.com", "", "both", "未知域名（默认策略）"),
        ("mini.usdt2026.cc", "https://admin.usdt2026.cc", "telegram_first", "MiniApp host，Admin referer"),
    ]
    
    passed = 0
    failed = 0
    
    for host, referer, expected_strategy, description in test_cases:
        request = create_mock_request(host, referer)
        strategy = get_auth_strategy(request)
        
        status = "✓" if strategy == expected_strategy else "✗"
        if strategy == expected_strategy:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {description}")
        print(f"    Host: {host}")
        print(f"    Referer: {referer or '(empty)'}")
        print(f"    预期策略: {expected_strategy}")
        print(f"    实际策略: {strategy}")
        print()
    
    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


def test_auth_permissions():
    """测试认证权限检查"""
    print("\n" + "=" * 60)
    print("测试认证权限检查")
    print("=" * 60)
    
    test_cases = [
        # (host, allow_telegram, allow_jwt, description)
        ("mini.usdt2026.cc", True, True, "MiniApp 允许 Telegram 和 JWT"),
        ("admin.usdt2026.cc", False, True, "Admin 只允许 JWT"),
        ("example.com", True, True, "未知域名允许两种方式"),
    ]
    
    passed = 0
    failed = 0
    
    for host, expected_telegram, expected_jwt, description in test_cases:
        request = create_mock_request(host)
        allow_telegram = should_allow_telegram_auth(request)
        allow_jwt = should_allow_jwt_auth(request)
        
        telegram_ok = allow_telegram == expected_telegram
        jwt_ok = allow_jwt == expected_jwt
        
        status = "✓" if telegram_ok and jwt_ok else "✗"
        if telegram_ok and jwt_ok:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {description}")
        print(f"    Host: {host}")
        print(f"    Telegram 认证: {allow_telegram} (预期: {expected_telegram})")
        print(f"    JWT 认证: {allow_jwt} (预期: {expected_jwt})")
        print()
    
    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    print("\n开始测试认证策略功能...\n")
    
    strategy_ok = test_auth_strategies()
    permission_ok = test_auth_permissions()
    
    if strategy_ok and permission_ok:
        print("\n✓ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n✗ 部分测试失败！")
        sys.exit(1)

