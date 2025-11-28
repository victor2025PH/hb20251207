#!/usr/bin/env python3
"""
测试发送消息功能
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

def test_send_message(token, chat_id=5433982810, text="测试消息"):
    """测试发送消息功能"""
    url = f"{BASE_URL}/v1/admin/telegram/send-message"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "chat_id": chat_id,
        "text": text,
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, verify=False)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"\n✅ 消息发送成功！")
                print(f"消息ID: {result.get('message_id')}")
                print(f"聊天ID: {result.get('chat_id')}")
                return True
            else:
                print(f"\n❌ 消息发送失败: {result.get('error')}")
                return False
        else:
            print(f"\n❌ 请求失败")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  测试发送消息功能")
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
    
    # 测试发送消息
    print("[2/2] 测试发送消息...")
    test_send_message(token, chat_id=5433982810, text="这是一条测试消息 🎉")
    print()
    
    print("=" * 60)
    print("  测试完成！")
    print("=" * 60)

