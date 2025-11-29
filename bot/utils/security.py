"""
Lucky Red - 安全工具
提供輸入驗證、清理等功能
"""
import re
from typing import Optional
from decimal import Decimal, InvalidOperation
from loguru import logger


def sanitize_message(message: str, max_length: int = 256) -> str:
    """
    清理用戶輸入的消息
    
    Args:
        message: 原始消息
        max_length: 最大長度
    
    Returns:
        清理後的消息
    """
    if not message:
        return ""
    
    # 移除危險字符（HTML 標籤等）
    message = re.sub(r'[<>]', '', message)
    
    # 移除控制字符（保留換行符和製表符）
    message = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', message)
    
    # 限制長度
    if len(message) > max_length:
        message = message[:max_length]
        logger.warning(f"Message truncated to {max_length} characters")
    
    return message.strip()


def validate_chat_id(chat_id: str) -> Optional[int]:
    """
    驗證群組 ID 格式
    
    Args:
        chat_id: 群組 ID 字符串
    
    Returns:
        有效的群組 ID（整數），如果無效則返回 None
    """
    if not chat_id:
        return None
    
    try:
        id_int = int(chat_id)
        # 群組 ID 通常是負數（Telegram 群組 ID 格式）
        # 但也接受正數（用戶 ID）
        return id_int
    except ValueError:
        logger.warning(f"Invalid chat_id format: {chat_id}")
        return None


def validate_amount(
    amount: str,
    currency: str,
    balance: Decimal,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None
) -> tuple[bool, str]:
    """
    驗證金額輸入
    
    Args:
        amount: 金額字符串
        currency: 貨幣類型
        balance: 當前餘額
        min_amount: 最小金額（可選）
        max_amount: 最大金額（可選）
    
    Returns:
        (是否有效, 錯誤消息)
    """
    if not amount:
        return False, "金額不能為空"
    
    try:
        amount_decimal = Decimal(str(amount))
    except (ValueError, InvalidOperation):
        return False, "金額格式錯誤，請輸入有效的數字"
    
    # 檢查是否為正數
    if amount_decimal <= 0:
        return False, "金額必須大於0"
    
    # 檢查最小金額
    if min_amount is not None and amount_decimal < min_amount:
        return False, f"金額不能小於 {float(min_amount):.2f}"
    
    # 檢查最大金額
    if max_amount is not None and amount_decimal > max_amount:
        return False, f"金額不能大於 {float(max_amount):.2f}"
    
    # 檢查餘額
    if amount_decimal > balance:
        return False, f"餘額不足，當前 {currency.upper()} 餘額: {float(balance):.4f}"
    
    return True, ""


def validate_packet_count(count: int, packet_type: str = "random") -> tuple[bool, str]:
    """
    驗證紅包數量
    
    Args:
        count: 紅包數量
        packet_type: 紅包類型（random 或 equal）
    
    Returns:
        (是否有效, 錯誤消息)
    """
    if count <= 0:
        return False, "數量必須大於0"
    
    if count > 100:
        return False, "每個紅包最多100份"
    
    # 紅包炸彈只能選擇 5 或 10
    if packet_type == "equal" and count not in [5, 10]:
        return False, "紅包炸彈只能選擇 5 份（雙雷）或 10 份（單雷）"
    
    return True, ""


def validate_bomb_number(bomb_number: int) -> tuple[bool, str]:
    """
    驗證炸彈數字
    
    Args:
        bomb_number: 炸彈數字（0-9）
    
    Returns:
        (是否有效, 錯誤消息)
    """
    if bomb_number < 0 or bomb_number > 9:
        return False, "炸彈數字必須在 0-9 之間"
    
    return True, ""


def sanitize_username(username: Optional[str]) -> str:
    """
    清理用戶名
    
    Args:
        username: 原始用戶名
    
    Returns:
        清理後的用戶名
    """
    if not username:
        return ""
    
    # 移除 @ 符號
    username = username.lstrip('@')
    
    # 只保留字母、數字、下劃線
    username = re.sub(r'[^a-zA-Z0-9_]', '', username)
    
    # 限制長度
    return username[:64]


def validate_telegram_init_data(init_data: str) -> bool:
    """
    驗證 Telegram initData 格式（簡化版）
    
    注意：生產環境應使用完整的 Telegram 驗證機制
    
    Args:
        init_data: initData 字符串
    
    Returns:
        是否有效
    """
    if not init_data:
        return False
    
    # 簡化驗證：檢查是否包含 user 字段
    if 'user=' not in init_data:
        return False
    
    # 可以添加更多驗證邏輯
    return True
