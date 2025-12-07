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
        # initData 格式: key1=value1&key2=value2&hash=...
        params = urllib.parse.parse_qs(init_data, keep_blank_values=True)
        
        # 解析 user 字段（如果存在）
        user_str = params.get('user', [None])[0]
        if user_str:
            user_data = json.loads(user_str)
            return user_data
        return None
    except Exception as e:
        logger.warning(f"Failed to parse initData: {e}")
        return None


def verify_telegram_init_data(init_data: str) -> bool:
    """驗證 Telegram initData 的 hash"""
    try:
        # 解析參數
        params = urllib.parse.parse_qs(init_data, keep_blank_values=True)
        
        # 獲取 hash
        hash_value = params.get('hash', [None])[0]
        if not hash_value:
            return False
        
        # 移除 hash 並構建數據字符串
        data_dict = {k: v[0] if v else '' for k, v in params.items() if k != 'hash'}
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(data_dict.items()) if v is not None
        )
        
        # 計算密鑰
        secret_key = hashlib.sha256(settings.BOT_TOKEN.encode()).digest()
        
        # 計算 HMAC
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return calculated_hash == hash_value
    except Exception as e:
        logger.warning(f"Failed to verify initData: {e}")
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

