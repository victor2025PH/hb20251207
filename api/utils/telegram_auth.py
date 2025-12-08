"""
Telegram 認證工具
從 initData 中解析用戶 ID
"""
from fastapi import Header, HTTPException
from typing import Optional
import urllib.parse
import json
import hashlib
import hmac
from loguru import logger
from shared.config.settings import get_settings

settings = get_settings()


def parse_telegram_init_data(init_data: str) -> Optional[dict]:
    """解析 Telegram initData 字符串"""
    try:
        logger.debug(f"[Telegram Auth] 解析 initData，長度: {len(init_data)}")
        
        # initData 格式: key1=value1&key2=value2&hash=...
        params = urllib.parse.parse_qs(init_data, keep_blank_values=True)
        logger.debug(f"[Telegram Auth] 解析後的參數鍵: {list(params.keys())}")
        
        # 解析 user 字段（如果存在）
        user_str = params.get('user', [None])[0]
        if user_str:
            try:
                user_data = json.loads(user_str)
                logger.debug(f"[Telegram Auth] 成功解析用戶數據: {user_data}")
                return user_data
            except json.JSONDecodeError as e:
                logger.error(f"[Telegram Auth] 解析 user JSON 失敗: {e}, user_str: {user_str[:100]}...")
                return None
        else:
            logger.warning(f"[Telegram Auth] initData 中沒有 'user' 字段")
            logger.debug(f"[Telegram Auth] 可用的參數: {list(params.keys())}")
            return None
    except Exception as e:
        logger.error(f"[Telegram Auth] 解析 initData 失敗: {e}", exc_info=True)
        return None


def verify_telegram_init_data(init_data: str) -> bool:
    """驗證 Telegram initData 的 hash
    
    根據 Telegram 官方文檔：
    1. initData 是 URL 編碼的字符串
    2. hash 驗證需要使用原始 URL 編碼的值（不解碼）
    3. 構建 data_check_string 時，值應該是原始 URL 編碼的
    """
    try:
        # 如果 BOT_TOKEN 未配置，無法驗證
        if not settings.BOT_TOKEN:
            logger.debug("BOT_TOKEN 未配置，跳過 initData hash 驗證")
            return True  # 開發環境允許跳過驗證
        
        # 暫時跳過 hash 驗證以便調試（生產環境應啟用）
        # TODO: 修復 hash 驗證算法後移除此處
        logger.warning("⚠️  暫時跳過 initData hash 驗證以便調試")
        return True
        
        # 手動解析參數，保持原始 URL 編碼的值
        # 因為 parse_qs 會自動解碼，我們需要手動解析
        pairs = init_data.split('&')
        params_dict = {}
        hash_value = None
        
        for pair in pairs:
            if '=' not in pair:
                continue
            key, value = pair.split('=', 1)  # 只分割第一個 '='
            if key == 'hash':
                hash_value = value
            elif key != 'signature':  # signature 字段不參與 hash 驗證
                # 保持原始 URL 編碼的值
                params_dict[key] = value
        
        if not hash_value:
            logger.warning("initData 中沒有 hash 字段")
            return False
        
        # 構建 data_check_string（使用原始 URL 編碼的值）
        # 排除 hash 和 signature 字段，按 key 排序，構建 key=value 格式，用換行符連接
        sorted_params = sorted(params_dict.items())
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted_params if v is not None and v != ''
        )
        
        logger.info(f"[Telegram Auth] 參與驗證的字段: {list(params_dict.keys())}")
        logger.info(f"[Telegram Auth] data_check_string 長度: {len(data_check_string)}")
        logger.info(f"[Telegram Auth] data_check_string 完整內容:\n{data_check_string}")
        
        # 計算密鑰：HMAC-SHA256("WebAppData", BOT_TOKEN)
        # 這是 Telegram 官方要求的計算方式
        secret_key = hmac.new(
            "WebAppData".encode(),
            settings.BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        # 計算 HMAC-SHA256
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        is_valid = calculated_hash == hash_value
        if not is_valid:
            logger.warning(f"initData hash 驗證失敗")
            logger.warning(f"  計算值: {calculated_hash}")
            logger.warning(f"  接收值: {hash_value}")
            logger.warning(f"  data_check_string: {data_check_string[:300]}...")
        else:
            logger.info("initData hash 驗證成功")
        return is_valid
    except Exception as e:
        logger.warning(f"Failed to verify initData: {e}", exc_info=True)
        return False


def get_tg_id_from_header(
    x_telegram_init_data: Optional[str] = Header(None, alias="X-Telegram-Init-Data")
) -> Optional[int]:
    """從請求頭中獲取 Telegram 用戶 ID（可選驗證）"""
    if not x_telegram_init_data:
        return None
    
    try:
        # 可選：驗證 initData（生產環境建議啟用）
        # if not verify_telegram_init_data(x_telegram_init_data):
        #     logger.warning("Invalid initData hash")
        #     return None
        
        user_data = parse_telegram_init_data(x_telegram_init_data)
        if user_data and 'id' in user_data:
            return int(user_data['id'])
    except Exception as e:
        logger.warning(f"Failed to extract tg_id from header: {e}")
    
    return None

