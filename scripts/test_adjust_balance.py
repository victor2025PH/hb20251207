#!/usr/bin/env python3
"""
测试充值功能
"""
import requests
import json
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BASE_URL = "https://admin.usdt2026.cc/api"
USERNAME = "admin"
PASSWORD = "123456"

def get_token():
    """获取登录 token"""
    url = f"{BASE_URL}/v1/admin/auth/login"
    data = {"username": USERNAME, "password": PASSWORD}
    
    try:
        response = requests.post(url, json=data, verify=False)
        if response.status_code == 200:
            result = response.json()
            return result.get("token")
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录请求失败: {str(e)}")
        return None

def test_adjust_balance(token, user_id=4, currency="usdt", amount=100.0):
    """测试充值功能"""
    url = f"{BASE_URL}/v1/admin/users/adjust-balance"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "user_id": user_id,
        "currency": currency,
        "amount": amount,
        "reason": "测试充值"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, verify=False)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 充值成功！")
            print(f"用户ID: {result.get('data', {}).get('user_id')}")
            print(f"货币: {result.get('data', {}).get('currency')}")
            print(f"金额: {result.get('data', {}).get('amount')}")
            print(f"旧余额: {result.get('data', {}).get('old_balance')}")
            print(f"新余额: {result.get('data', {}).get('new_balance')}")
            return True
        else:
            print(f"\n❌ 充值失败")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  测试充值功能")
    print("=" * 60)
    print()
    
    # 登录获取 token
    print("[1/2] 登录...")
    token = get_token()
    if not token:
        print("❌ 无法获取 token，测试终止")
        exit(1)
    print(f"✅ 登录成功")
    print()
    
    # 测试充值
    print("[2/2] 测试充值...")
    test_adjust_balance(token, user_id=4, currency="usdt", amount=100.0)
    print()
    
    print("=" * 60)
    print("  测试完成！")
    print("=" * 60)

