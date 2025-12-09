#!/usr/bin/env python3
"""
测试后台管理登录
"""
import requests
import json
import sys

def test_login(username: str, password: str):
    """测试登录"""
    url = "https://admin.usdt2026.cc/api/v1/admin/auth/login"
    
    try:
        response = requests.post(
            url,
            json={"username": username, "password": password},
            verify=False,  # 忽略 SSL 证书验证（仅用于测试）
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            data = response.json()
            print(f"Response JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if response.status_code == 200 and data.get("success"):
                print("\n✅ 登录成功！")
                print(f"Token: {data.get('token', '')[:50]}...")
                return True
            else:
                print(f"\n❌ 登录失败: {data.get('detail', 'Unknown error')}")
                return False
        except Exception as e:
            print(f"Response Text: {response.text}")
            print(f"JSON Parse Error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    password = sys.argv[2] if len(sys.argv) > 2 else "123456"
    
    print(f"测试登录: username={username}, password={password}")
    print("=" * 50)
    
    success = test_login(username, password)
    sys.exit(0 if success else 1)

