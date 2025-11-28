#!/usr/bin/env python3
"""
测试服务器登录 API
"""
import requests
import json
import sys

def test_login():
    url = "https://admin.usdt2026.cc/api/v1/admin/auth/login"
    data = {
        "username": "admin",
        "password": "123456"
    }
    
    try:
        response = requests.post(url, json=data, verify=False)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 登录成功！")
            print(f"Success: {result.get('success')}")
            print(f"Token: {result.get('token', '')[:50]}...")
            print(f"Admin: {result.get('admin')}")
            return True
        else:
            print(f"\n❌ 登录失败")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_login()

