"""
Lucky Red - 權限檢查工具
提供用戶權限、餘額檢查等功能
"""
from decimal import Decimal
from typing import Optional
from loguru import logger
from shared.database.models import User


def check_user_permission(
    db_user: User,
    required_balance: Optional[Decimal] = None,
    currency: str = "usdt"
) -> tuple[bool, str]:
    """
    檢查用戶權限和餘額
    
    Args:
        db_user: 用戶對象
        required_balance: 所需餘額（可選）
        currency: 貨幣類型（usdt, ton, points）
    
    Returns:
        (是否有權限, 錯誤消息)
    """
    # 檢查是否被封禁
    if db_user.is_banned:
        logger.warning(f"Banned user {db_user.tg_id} attempted action")
        return False, "您的賬號已被封禁，無法執行此操作"
    
    # 檢查餘額（如果提供了所需餘額）
    if required_balance is not None:
        balance_field = f"balance_{currency}"
        current_balance = getattr(db_user, balance_field, 0) or Decimal(0)
        
        if current_balance < required_balance:
            logger.info(
                f"User {db_user.tg_id} insufficient balance: "
                f"{current_balance} < {required_balance} ({currency})"
            )
            return False, f"餘額不足，當前 {currency.upper()} 餘額: {float(current_balance):.4f}"
    
    return True, ""


def check_balance(
    db_user: User,
    amount: Decimal,
    currency: str = "usdt"
) -> tuple[bool, str]:
    """
    檢查用戶餘額是否足夠
    
    Args:
        db_user: 用戶對象
        amount: 所需金額
        currency: 貨幣類型
    
    Returns:
        (餘額是否足夠, 錯誤消息)
    """
    return check_user_permission(db_user, required_balance=amount, currency=currency)


def check_admin_permission(db_user: User) -> bool:
    """
    檢查是否為管理員
    
    Args:
        db_user: 用戶對象
    
    Returns:
        是否為管理員
    """
    return db_user.is_admin if db_user else False


def check_premium_permission(db_user: User) -> bool:
    """
    檢查是否為高級用戶（如果系統有高級功能）
    
    Args:
        db_user: 用戶對象
    
    Returns:
        是否為高級用戶
    """
    # 如果 User 模型有 is_premium 字段
    return getattr(db_user, 'is_premium', False) if db_user else False
