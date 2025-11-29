"""
Lucky Red - 日誌輔助工具
提供結構化日誌記錄功能
"""
import json
from typing import Optional, Dict, Any
from loguru import logger
from datetime import datetime


def log_user_action(
    user_id: int,
    action: str,
    details: Optional[Dict[str, Any]] = None,
    level: str = "info"
):
    """
    記錄用戶操作
    
    Args:
        user_id: 用戶 ID
        action: 操作名稱
        details: 操作詳情
        level: 日誌級別（info, warning, error）
    """
    log_data = {
        "user_id": user_id,
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details or {}
    }
    
    log_message = f"User action: {action} (user_id: {user_id})"
    
    if level == "error":
        logger.error(log_message, extra=log_data)
    elif level == "warning":
        logger.warning(log_message, extra=log_data)
    else:
        logger.info(log_message, extra=log_data)


def log_api_call(
    endpoint: str,
    method: str = "POST",
    status_code: Optional[int] = None,
    duration: Optional[float] = None,
    error: Optional[str] = None
):
    """
    記錄 API 調用
    
    Args:
        endpoint: API 端點
        method: HTTP 方法
        status_code: 狀態碼
        duration: 耗時（秒）
        error: 錯誤信息（如果有）
    """
    log_data = {
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "duration": duration,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if error:
        log_data["error"] = error
        logger.error(
            f"API call failed: {method} {endpoint}",
            extra=log_data
        )
    else:
        logger.info(
            f"API call: {method} {endpoint} ({status_code})",
            extra=log_data
        )


def log_packet_action(
    user_id: int,
    action: str,
    packet_id: Optional[int] = None,
    amount: Optional[float] = None,
    currency: Optional[str] = None,
    success: bool = True
):
    """
    記錄紅包操作
    
    Args:
        user_id: 用戶 ID
        action: 操作（create, claim, send）
        packet_id: 紅包 ID
        amount: 金額
        currency: 貨幣類型
        success: 是否成功
    """
    log_data = {
        "user_id": user_id,
        "action": action,
        "packet_id": packet_id,
        "amount": amount,
        "currency": currency,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    level = "info" if success else "error"
    logger.log(
        level.upper(),
        f"Packet {action}: user={user_id}, packet={packet_id}, amount={amount} {currency}",
        extra=log_data
    )


def log_transaction(
    user_id: int,
    transaction_type: str,
    amount: float,
    currency: str,
    status: str = "completed"
):
    """
    記錄交易
    
    Args:
        user_id: 用戶 ID
        transaction_type: 交易類型（deposit, withdraw, exchange）
        amount: 金額
        currency: 貨幣類型
        status: 狀態
    """
    log_data = {
        "user_id": user_id,
        "type": transaction_type,
        "amount": amount,
        "currency": currency,
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(
        f"Transaction: {transaction_type} {amount} {currency} (user: {user_id}, status: {status})",
        extra=log_data
    )
