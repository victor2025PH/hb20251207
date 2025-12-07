"""
認證策略選擇器
根據請求來源（host/port）選擇不同的認證方式
"""
from fastapi import Request
from typing import Optional, Literal
from loguru import logger
from shared.config.settings import get_settings

settings = get_settings()

AuthStrategy = Literal["telegram_first", "jwt_only", "both"]


def get_auth_strategy(request: Request) -> AuthStrategy:
    """
    根據請求來源選擇認證策略
    
    Args:
        request: FastAPI Request 對象
        
    Returns:
        AuthStrategy: 認證策略
        - "telegram_first": 優先使用 Telegram 認證（MiniApp 環境）
        - "jwt_only": 只使用 JWT Token 認證（Web 環境）
        - "both": 同時支持兩種認證方式（默認）
    """
    host = request.headers.get("host", "").lower()
    referer = request.headers.get("referer", "").lower()
    
    # MiniApp 域名：優先使用 Telegram 認證
    miniapp_hosts = [
        "mini.usdt2026.cc",
        "localhost:5173",  # 開發環境
        "localhost:3000",  # 開發環境
    ]
    
    # Admin/Web 域名：只使用 JWT Token 認證
    web_hosts = [
        "admin.usdt2026.cc",
        "localhost:5174",  # 開發環境
        "localhost:3001",  # 開發環境
    ]
    
    # 檢查 host
    if any(miniapp_host in host for miniapp_host in miniapp_hosts):
        logger.debug(f"[Auth Strategy] MiniApp host detected: {host}, using telegram_first")
        return "telegram_first"
    
    if any(web_host in host for web_host in web_hosts):
        logger.debug(f"[Auth Strategy] Web host detected: {host}, using jwt_only")
        return "jwt_only"
    
    # 檢查 referer（如果 host 不匹配）
    if referer:
        if any(miniapp_host in referer for miniapp_host in miniapp_hosts):
            logger.debug(f"[Auth Strategy] MiniApp referer detected: {referer}, using telegram_first")
            return "telegram_first"
        
        if any(web_host in referer for web_host in web_hosts):
            logger.debug(f"[Auth Strategy] Web referer detected: {referer}, using jwt_only")
            return "jwt_only"
    
    # 默認：同時支持兩種認證方式
    logger.debug(f"[Auth Strategy] Default strategy for host: {host}")
    return "both"


def should_allow_telegram_auth(request: Request) -> bool:
    """檢查是否允許 Telegram 認證"""
    strategy = get_auth_strategy(request)
    return strategy in ["telegram_first", "both"]


def should_allow_jwt_auth(request: Request) -> bool:
    """檢查是否允許 JWT Token 認證"""
    strategy = get_auth_strategy(request)
    return strategy in ["jwt_only", "both"]

