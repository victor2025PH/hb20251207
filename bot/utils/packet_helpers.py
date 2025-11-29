"""
Lucky Red - 紅包輔助工具
提供紅包相關的輔助函數，消除代碼重複
"""
from typing import Dict, Any, Optional, List
from decimal import Decimal
from bot.constants import PacketConstants


def extract_packet_data(parts: List[str]) -> Dict[str, Any]:
    """
    從回調數據中提取紅包數據
    
    Args:
        parts: 回調數據分割後的列表
    
    Returns:
        紅包數據字典
    """
    return {
        'currency': parts[3] if len(parts) > 3 else "usdt",
        'packet_type': parts[4] if len(parts) > 4 else "random",
        'amount': parts[5] if len(parts) > 5 else None,
        'count': int(parts[6]) if len(parts) > 6 and parts[6].isdigit() else None,
        'bomb_number': int(parts[7]) if len(parts) > 7 and parts[7].isdigit() else None,
        'message': parts[8] if len(parts) > 8 and parts[8] != "default" else PacketConstants.DEFAULT_MESSAGE,
    }


def build_packet_callback_data(
    action: str,
    currency: str,
    packet_type: str,
    amount: Optional[str] = None,
    count: Optional[int] = None,
    bomb_number: Optional[int] = None,
    message: Optional[str] = None,
    chat_id: Optional[int] = None
) -> str:
    """
    構建紅包回調數據
    
    Args:
        action: 動作（如 "send:amount", "send:count"）
        currency: 貨幣類型
        packet_type: 紅包類型
        amount: 金額（可選）
        count: 數量（可選）
        bomb_number: 炸彈數字（可選）
        message: 祝福語（可選）
        chat_id: 群組 ID（可選）
    
    Returns:
        回調數據字符串
    """
    parts = ["packets", "send", action, currency, packet_type]
    
    if amount is not None:
        parts.append(str(amount))
    if count is not None:
        parts.append(str(count))
    if bomb_number is not None:
        parts.append(str(bomb_number))
    if message is not None and message != "default":
        parts.append(message)
    if chat_id is not None:
        parts.append(str(chat_id))
    
    return ":".join(parts)


def format_packet_info(
    currency: str,
    packet_type: str,
    amount: Decimal,
    count: int,
    bomb_number: Optional[int] = None,
    message: Optional[str] = None
) -> str:
    """
    格式化紅包信息文本
    
    Args:
        currency: 貨幣類型
        packet_type: 紅包類型
        amount: 金額
        count: 數量
        bomb_number: 炸彈數字（可選）
        message: 祝福語（可選）
    
    Returns:
        格式化的文本
    """
    currency_upper = currency.upper()
    type_text = "手氣最佳" if packet_type == "random" else "紅包炸彈"
    
    lines = [
        f"*幣種：* {currency_upper}",
        f"*類型：* {type_text}",
        f"*金額：* `{float(amount):.2f}` {currency_upper}",
        f"*數量：* `{count}` 份",
    ]
    
    if bomb_number is not None:
        lines.append(f"*炸彈數字：* `{bomb_number}`")
    
    if message:
        lines.append(f"*祝福語：* {message}")
    
    return "\n".join(lines)


def get_packet_type_text(packet_type: str) -> str:
    """
    獲取紅包類型文本
    
    Args:
        packet_type: 紅包類型（random 或 equal）
    
    Returns:
        類型文本
    """
    return "手氣最佳" if packet_type == "random" else "紅包炸彈"


def get_thunder_type(count: int) -> str:
    """
    獲取雷類型文本（用於紅包炸彈）
    
    Args:
        count: 紅包數量
    
    Returns:
        雷類型文本（單雷或雙雷）
    """
    return "單雷" if count == 10 else "雙雷"
