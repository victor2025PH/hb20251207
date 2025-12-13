"""
Lucky Red - 權限檢查工具
提供用戶權限、餘額檢查等功能（只接受 user_id，不接受 ORM 對象）
"""
from decimal import Decimal
from typing import Optional, Tuple
from loguru import logger
from shared.database.connection import get_db
from shared.database.models import User


def check_user_permission(
    user_id: int,
    required_balance: Optional[Decimal] = None,
    currency: str = "usdt"
) -> Tuple[bool, str]:
    """
    檢查用戶權限和餘額（只接受 user_id，不接受 ORM 對象）
    
    Args:
        user_id: Telegram 用戶 ID
        required_balance: 所需餘額（可選）
        currency: 貨幣類型（usdt, ton, points）
    
    Returns:
        (是否有權限, 錯誤消息)
    """
    with get_db() as db:
        db_user = db.query(User).filter(User.tg_id == user_id).first()
        if not db_user:
            return False, "用戶不存在"
        
        # 檢查是否被封禁
        if getattr(db_user, 'is_banned', False):
            logger.warning(f"Banned user {user_id} attempted action")
            return False, "您的賬號已被封禁，無法執行此操作"
        
        # 檢查餘額（如果提供了所需餘額）
        if required_balance is not None:
            balance_field = f"balance_{currency}"
            current_balance = getattr(db_user, balance_field, 0) or Decimal(0)
            
            if current_balance < required_balance:
                logger.info(
                    f"User {user_id} insufficient balance: "
                    f"{current_balance} < {required_balance} ({currency})"
                )
                return False, f"餘額不足，當前 {currency.upper()} 餘額: {float(current_balance):.4f}"
    
    return True, ""


def check_balance(
    user_id: int,
    amount: Decimal,
    currency: str = "usdt"
) -> Tuple[bool, str]:
    """
    檢查用戶餘額是否足夠（只接受 user_id，不接受 ORM 對象）
    
    Args:
        user_id: Telegram 用戶 ID
        amount: 所需金額
        currency: 貨幣類型
    
    Returns:
        (餘額是否足夠, 錯誤消息)
    """
    return check_user_permission(user_id, required_balance=amount, currency=currency)


def check_admin_permission(user_id: int) -> bool:
    """
    檢查是否為管理員（只接受 user_id，不接受 ORM 對象）
    
    Args:
        user_id: Telegram 用戶 ID
    
    Returns:
        是否為管理員
    """
    with get_db() as db:
        db_user = db.query(User).filter(User.tg_id == user_id).first()
        if not db_user:
            return False
        return getattr(db_user, 'is_admin', False)


def check_premium_permission(user_id: int) -> bool:
    """
    檢查是否為高級用戶（只接受 user_id，不接受 ORM 對象）
    
    Args:
        user_id: Telegram 用戶 ID
    
    Returns:
        是否為高級用戶
    """
    with get_db() as db:
        db_user = db.query(User).filter(User.tg_id == user_id).first()
        if not db_user:
            return False
        return getattr(db_user, 'is_premium', False)
