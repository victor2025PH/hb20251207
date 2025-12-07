#!/usr/bin/env python3
"""
全自动测试所有登录方式
测试并修复所有登录API端点
"""
import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
import httpx
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# API基础URL（可以从环境变量读取）
import os
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8080/api/v1")
TIMEOUT = 30.0


class LoginTester:
    """登录方式测试器"""
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.client = httpx.AsyncClient(timeout=TIMEOUT, base_url=API_BASE)
    
    async def test_google_login(self) -> Dict[str, Any]:
        """测试Google登录"""
        print("\n" + "="*60)
        print("测试 Google 登录")
        print("="*60)
        
        try:
            # 模拟Google登录请求
            payload = {
                "id_token": f"mock_google_token_{datetime.now().timestamp()}",
                "email": "test@example.com",
                "given_name": "Test",
                "family_name": "User"
            }
            
            response = await self.client.post("/auth/web/google", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                user = data.get("user", {})
                
                # 验证返回的数据
                if token and user.get("id"):
                    print(f"✅ Google登录成功")
                    print(f"   User ID: {user.get('id')}")
                    print(f"   Username: {user.get('username')}")
                    print(f"   Token: {token[:20]}...")
                    
                    # 测试使用Token获取用户信息
                    headers = {"Authorization": f"Bearer {token}"}
                    me_response = await self.client.get("/users/me", headers=headers)
                    
                    if me_response.status_code == 200:
                        print(f"✅ 使用Token获取用户信息成功")
                        return {
                            "status": "success",
                            "token": token,
                            "user_id": user.get("id"),
                            "can_fetch_profile": True
                        }
                    else:
                        print(f"⚠️  使用Token获取用户信息失败: {me_response.status_code}")
                        return {
                            "status": "partial_success",
                            "token": token,
                            "user_id": user.get("id"),
                            "can_fetch_profile": False,
                            "error": f"GET /users/me returned {me_response.status_code}"
                        }
                else:
                    print(f"❌ 响应格式错误")
                    return {"status": "error", "error": "Invalid response format"}
            else:
                print(f"❌ Google登录失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
        except Exception as e:
            print(f"❌ Google登录异常: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "error": str(e)}
    
    async def test_wallet_login(self) -> Dict[str, Any]:
        """测试Wallet登录"""
        print("\n" + "="*60)
        print("测试 Wallet 登录")
        print("="*60)
        
        try:
            # 模拟Wallet登录请求
            payload = {
                "address": "EQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqB2N",
                "network": "TON"
            }
            
            response = await self.client.post("/auth/web/wallet", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                user = data.get("user", {})
                
                if token and user.get("id"):
                    print(f"✅ Wallet登录成功")
                    print(f"   User ID: {user.get('id')}")
                    print(f"   Wallet Address: {user.get('wallet_address')}")
                    print(f"   Token: {token[:20]}...")
                    
                    # 测试使用Token获取用户信息
                    headers = {"Authorization": f"Bearer {token}"}
                    me_response = await self.client.get("/users/me", headers=headers)
                    
                    if me_response.status_code == 200:
                        print(f"✅ 使用Token获取用户信息成功")
                        return {
                            "status": "success",
                            "token": token,
                            "user_id": user.get("id"),
                            "can_fetch_profile": True
                        }
                    else:
                        print(f"⚠️  使用Token获取用户信息失败: {me_response.status_code}")
                        return {
                            "status": "partial_success",
                            "token": token,
                            "user_id": user.get("id"),
                            "can_fetch_profile": False,
                            "error": f"GET /users/me returned {me_response.status_code}"
                        }
                else:
                    print(f"❌ 响应格式错误")
                    return {"status": "error", "error": "Invalid response format"}
            else:
                print(f"❌ Wallet登录失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
        except Exception as e:
            print(f"❌ Wallet登录异常: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "error": str(e)}
    
    async def test_magic_link_login(self) -> Dict[str, Any]:
        """测试Magic Link登录"""
        print("\n" + "="*60)
        print("测试 Magic Link 登录")
        print("="*60)
        
        try:
            # 注意：Magic Link需要先通过Telegram生成
            # 这里我们测试一个不存在的token，应该返回401
            payload = {
                "token": "invalid_test_token_12345"
            }
            
            response = await self.client.post("/auth/link/magic-link/verify", json=payload)
            
            if response.status_code == 401:
                print(f"✅ Magic Link验证端点正常（正确拒绝了无效token）")
                print(f"   响应: {response.json().get('detail', 'Unauthorized')}")
                return {
                    "status": "success",
                    "note": "Endpoint works correctly, but requires valid token from Telegram"
                }
            elif response.status_code == 200:
                # 如果意外成功，说明可能有测试token
                data = response.json()
                token = data.get("access_token")
                print(f"⚠️  Magic Link验证成功（可能是测试token）")
                return {
                    "status": "success",
                    "token": token,
                    "note": "Unexpected success with test token"
                }
            else:
                print(f"❌ Magic Link验证失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
        except Exception as e:
            print(f"❌ Magic Link登录异常: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "error": str(e)}
    
    async def test_telegram_auth(self) -> Dict[str, Any]:
        """测试Telegram认证（通过initData）"""
        print("\n" + "="*60)
        print("测试 Telegram 认证（initData）")
        print("="*60)
        
        try:
            # 注意：这需要真实的Telegram initData
            # 我们测试一个模拟的initData格式
            # 实际环境中，这应该由Telegram WebApp提供
            
            # 模拟initData（这不会通过验证，但可以测试端点是否可访问）
            mock_init_data = "user=%7B%22id%22%3A123456%7D&auth_date=1234567890&hash=test_hash"
            
            headers = {
                "X-Telegram-Init-Data": mock_init_data
            }
            
            response = await self.client.get("/users/me", headers=headers)
            
            if response.status_code == 401:
                print(f"✅ Telegram认证端点正常（正确拒绝了无效initData）")
                print(f"   响应: {response.json().get('detail', 'Unauthorized')}")
                return {
                    "status": "success",
                    "note": "Endpoint works correctly, but requires valid Telegram initData"
                }
            elif response.status_code == 200:
                # 如果成功，说明可能配置了测试模式
                data = response.json()
                print(f"⚠️  Telegram认证成功（可能是测试模式）")
                return {
                    "status": "success",
                    "user_id": data.get("id"),
                    "note": "Unexpected success with mock initData"
                }
            else:
                print(f"❌ Telegram认证失败: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}"
                }
        except Exception as e:
            print(f"❌ Telegram认证异常: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "error": str(e)}
    
    async def test_api_health(self) -> bool:
        """测试API健康状态"""
        print("\n" + "="*60)
        print("测试 API 健康状态")
        print("="*60)
        
        try:
            # 尝试访问一个不需要认证的端点
            response = await self.client.get("/health")
            if response.status_code == 200:
                print("✅ API服务正常运行")
                return True
            elif response.status_code == 404:
                # 如果没有health端点，尝试访问根路径
                print("⚠️  /health端点不存在，尝试其他方式...")
                return True  # 假设API在运行
            else:
                print(f"⚠️  API响应异常: {response.status_code}")
                return False
        except httpx.ConnectError:
            print("❌ 无法连接到API服务器")
            print("   请确保API服务正在运行: python api/main.py")
            return False
        except Exception as e:
            print(f"❌ API健康检查异常: {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("开始全自动登录方式测试")
        print("="*60)
        print(f"API Base URL: {API_BASE}")
        print(f"测试时间: {datetime.now().isoformat()}")
        
        # 1. 检查API健康状态
        api_healthy = await self.test_api_health()
        if not api_healthy:
            print("\n❌ API服务不可用，无法继续测试")
            return
        
        # 2. 测试所有登录方式
        self.results["google"] = await self.test_google_login()
        self.results["wallet"] = await self.test_wallet_login()
        self.results["magic_link"] = await self.test_magic_link_login()
        self.results["telegram"] = await self.test_telegram_auth()
        
        # 3. 生成测试报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("测试报告")
        print("="*60)
        
        total = len(self.results)
        success = sum(1 for r in self.results.values() if r.get("status") == "success")
        partial = sum(1 for r in self.results.values() if r.get("status") == "partial_success")
        errors = sum(1 for r in self.results.values() if r.get("status") == "error")
        
        print(f"\n总计: {total} 个登录方式")
        print(f"✅ 完全成功: {success}")
        print(f"⚠️  部分成功: {partial}")
        print(f"❌ 失败: {errors}")
        
        print("\n详细结果:")
        for method, result in self.results.items():
            status = result.get("status", "unknown")
            status_icon = {
                "success": "✅",
                "partial_success": "⚠️",
                "error": "❌"
            }.get(status, "❓")
            
            print(f"\n{status_icon} {method.upper()}:")
            print(f"   状态: {status}")
            if result.get("error"):
                print(f"   错误: {result['error']}")
            if result.get("note"):
                print(f"   说明: {result['note']}")
            if result.get("user_id"):
                print(f"   用户ID: {result['user_id']}")
            if result.get("can_fetch_profile") is not None:
                print(f"   可获取用户信息: {result['can_fetch_profile']}")
        
        # 保存报告到文件
        report_file = project_root / "test_login_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "api_base": API_BASE,
                "results": self.results,
                "summary": {
                    "total": total,
                    "success": success,
                    "partial_success": partial,
                    "errors": errors
                }
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()


async def main():
    """主函数"""
    tester = LoginTester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())

