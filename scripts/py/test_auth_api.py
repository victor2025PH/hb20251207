"""
测试Auth API功能
需要先启动API服务
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8080/api/v1/auth"


def test_google_auth():
    """测试Google OAuth登录"""
    print("\n[测试] Google OAuth登录")
    url = f"{API_BASE}/web/google"
    data = {
        "id_token": "mock_google_id_token",
        "email": "test@example.com",
        "given_name": "Test",
        "family_name": "User",
        "picture": "https://example.com/avatar.jpg"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Google登录成功")
            print(f"   access_token: {result.get('access_token', '')[:20]}...")
            print(f"   user_id: {result.get('user', {}).get('id')}")
            return result.get('access_token')
        else:
            print(f"❌ Google登录失败: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    return None


def test_wallet_auth():
    """测试Wallet连接"""
    print("\n[测试] Wallet连接")
    url = f"{API_BASE}/web/wallet"
    data = {
        "address": "0x1234567890abcdef",
        "network": "TON",
        "signature": "mock_signature",
        "message": "mock_message"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Wallet连接成功")
            print(f"   access_token: {result.get('access_token', '')[:20]}...")
            print(f"   wallet_address: {result.get('user', {}).get('wallet_address')}")
            return result.get('access_token')
        else:
            print(f"❌ Wallet连接失败: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    return None


def test_magic_link_generate():
    """测试生成Magic Link（需要Telegram认证）"""
    print("\n[测试] 生成Magic Link")
    print("⚠️  需要Telegram认证，跳过此测试")
    return None


def test_magic_link_verify(token: str):
    """测试验证Magic Link"""
    if not token:
        print("\n[测试] 验证Magic Link - 跳过（需要有效的token）")
        return None
    
    print("\n[测试] 验证Magic Link")
    url = f"{API_BASE}/link/magic-link/verify"
    data = {"token": token}
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Magic Link验证成功")
            print(f"   access_token: {result.get('access_token', '')[:20]}...")
            return result.get('access_token')
        else:
            print(f"❌ Magic Link验证失败: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    return None


def main():
    """主函数"""
    print("=" * 60)
    print("测试 Auth API")
    print("=" * 60)
    print("\n⚠️  注意: 需要先启动API服务 (uvicorn api.main:app --reload)")
    print("⚠️  注意: Google OAuth和Wallet验证目前是Mock版本")
    
    # 测试Google登录
    google_token = test_google_auth()
    
    # 测试Wallet连接
    wallet_token = test_wallet_auth()
    
    # 测试Magic Link（需要Telegram认证，跳过）
    test_magic_link_generate()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()

