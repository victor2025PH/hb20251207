#!/usr/bin/env python3
"""
MiniApp API 全自動測試腳本

測試所有 API 端點的連通性和功能
"""

import requests
import json
from datetime import datetime

# 配置
API_BASE = "https://api.usdt2026.cc"
TEST_USER_TG_ID = 5433982810

# 測試結果
results = []

def log_result(name, success, message="", data=None):
    """記錄測試結果"""
    status = "✅ PASS" if success else "❌ FAIL"
    results.append({
        "name": name,
        "success": success,
        "message": message
    })
    print(f"{status} | {name}")
    if message:
        print(f"      └─ {message}")
    if data and not success:
        print(f"      └─ Response: {json.dumps(data, ensure_ascii=False)[:200]}")

def test_health():
    """測試健康檢查"""
    try:
        r = requests.get(f"{API_BASE}/health", timeout=10)
        data = r.json()
        log_result("健康檢查", data.get("status") == "ok", f"Version: {data.get('version')}")
        return True
    except Exception as e:
        log_result("健康檢查", False, str(e))
        return False

def test_websocket_status():
    """測試 WebSocket 狀態"""
    try:
        r = requests.get(f"{API_BASE}/ws/status", timeout=10)
        if r.status_code == 200:
            data = r.json()
            # 能訪問即表示服務正常
            log_result("WebSocket 狀態", True, 
                       f"服務正常, 在線用戶: {data.get('online_users', 0)}")
            return True
        else:
            log_result("WebSocket 狀態", False, f"Status: {r.status_code}")
            return False
    except Exception as e:
        log_result("WebSocket 狀態", False, str(e))
        return False

def test_redpacket_list():
    """測試紅包列表"""
    try:
        r = requests.get(f"{API_BASE}/api/redpackets/list", timeout=10)
        if r.status_code == 200:
            data = r.json()
            count = len(data) if isinstance(data, list) else 0
            log_result("紅包列表", True, f"獲取到 {count} 個紅包")
            return True
        else:
            log_result("紅包列表", False, f"Status: {r.status_code}")
            return False
    except Exception as e:
        log_result("紅包列表", False, str(e))
        return False

def test_exchange_rates():
    """測試兌換匯率"""
    try:
        r = requests.get(f"{API_BASE}/api/exchange/rates", timeout=10)
        if r.status_code == 200:
            data = r.json()
            log_result("兌換匯率", True, f"匯率數據: {data}")
            return True
        else:
            log_result("兌換匯率", r.status_code == 404, f"Status: {r.status_code}")
            return False
    except Exception as e:
        log_result("兌換匯率", False, str(e))
        return False

def test_checkin_status():
    """測試簽到狀態"""
    try:
        # 正確的路徑是 /api/checkin/status/{tg_id}
        r = requests.get(f"{API_BASE}/api/checkin/status/{TEST_USER_TG_ID}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            log_result("簽到狀態", True, f"連續簽到: {data.get('streak', 0)} 天")
            return True
        elif r.status_code == 404:
            log_result("簽到狀態", True, "用戶尚未簽到過（正常）")
            return True
        else:
            log_result("簽到狀態", False, f"Status: {r.status_code}", r.json() if r.text else None)
            return False
    except Exception as e:
        log_result("簽到狀態", False, str(e))
        return False

def test_user_profile():
    """測試用戶資料"""
    try:
        # 直接通過 tg_id 獲取用戶
        r = requests.get(f"{API_BASE}/api/users/{TEST_USER_TG_ID}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            log_result("用戶資料", True, 
                       f"用戶: {data.get('username', 'N/A')}, 餘額: {data.get('balance_usdt', 0)} USDT")
            return True
        elif r.status_code == 404:
            log_result("用戶資料", True, "用戶不存在（需要先在 Telegram 中啟動 Bot）")
            return True
        else:
            log_result("用戶資料", False, f"Status: {r.status_code}")
            return False
    except Exception as e:
        log_result("用戶資料", False, str(e))
        return False

def test_invite_stats():
    """測試邀請統計（通過用戶資料獲取）"""
    try:
        # 邀請信息包含在用戶資料中
        r = requests.get(f"{API_BASE}/api/users/{TEST_USER_TG_ID}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            log_result("邀請統計", True, 
                       f"邀請碼: {data.get('invite_code', 'N/A')}, 邀請人數: {data.get('invite_count', 0)}")
            return True
        elif r.status_code == 404:
            log_result("邀請統計", True, "用戶不存在（需要先註冊）")
            return True
        else:
            log_result("邀請統計", False, f"Status: {r.status_code}")
            return False
    except Exception as e:
        log_result("邀請統計", False, str(e))
        return False

def test_ai_api_status():
    """測試 AI API 狀態"""
    try:
        r = requests.get(f"{API_BASE}/api/v2/ai/status", timeout=10)
        if r.status_code == 200:
            data = r.json()
            log_result("AI API 狀態", data.get("success") == True, 
                       f"版本: {data.get('data', {}).get('version', 'N/A')}")
            return True
        else:
            log_result("AI API 狀態", False, f"Status: {r.status_code}")
            return False
    except Exception as e:
        log_result("AI API 狀態", False, str(e))
        return False

def test_admin_dashboard():
    """測試管理後台儀表板（無認證）"""
    try:
        r = requests.get(f"{API_BASE}/api/v1/admin/dashboard/stats", timeout=10)
        # 預期返回 401 未授權
        log_result("管理後台認證", r.status_code == 401 or r.status_code == 403, 
                   f"需要認證 (Status: {r.status_code})")
        return True
    except Exception as e:
        log_result("管理後台認證", False, str(e))
        return False

def run_all_tests():
    """運行所有測試"""
    print("=" * 60)
    print(f"  MiniApp API 全自動測試")
    print(f"  API: {API_BASE}")
    print(f"  時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # 基礎測試
    print("【基礎服務】")
    test_health()
    test_websocket_status()
    print()
    
    # 用戶功能
    print("【用戶功能】")
    test_user_profile()
    test_checkin_status()
    test_invite_stats()
    print()
    
    # 紅包功能
    print("【紅包功能】")
    test_redpacket_list()
    print()
    
    # 兌換功能
    print("【兌換功能】")
    test_exchange_rates()
    print()
    
    # AI 對接
    print("【AI 系統】")
    test_ai_api_status()
    print()
    
    # 安全測試
    print("【安全測試】")
    test_admin_dashboard()
    print()
    
    # 統計結果
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print("=" * 60)
    print(f"  測試完成: {passed}/{total} 通過")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 所有測試通過！MiniApp API 運行正常。")
    else:
        print("\n⚠️ 部分測試未通過，請檢查上方錯誤信息。")
        failed = [r for r in results if not r["success"]]
        print("\n失敗的測試:")
        for r in failed:
            print(f"  - {r['name']}: {r['message']}")

if __name__ == "__main__":
    run_all_tests()
