"""
Lucky Red (搶紅包) - 全局配置
"""
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """應用配置"""
    
    # 項目信息
    APP_NAME: str = "Lucky Red"
    APP_NAME_ZH: str = "搶紅包"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Telegram Bot
    BOT_TOKEN: str = ""
    BOT_USERNAME: str = ""
    
    # 管理員
    ADMIN_IDS: str = ""
    
    @property
    def admin_id_list(self) -> List[int]:
        """解析管理員 ID 列表"""
        if not self.ADMIN_IDS:
            return []
        return [int(x.strip()) for x in self.ADMIN_IDS.split(",") if x.strip().isdigit()]
    
    # 數據庫
    DATABASE_URL: str = "postgresql://localhost/luckyred"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8080
    
    # JWT
    JWT_SECRET: str = "change-this-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    
    # 域名
    BOT_DOMAIN: str = "bot.usdt2026.cc"
    ADMIN_DOMAIN: str = "admin.usdt2026.cc"
    MINIAPP_DOMAIN: str = "mini.usdt2026.cc"
    MINIAPP_URL: str = "https://mini.usdt2026.cc"
    
    # 遊戲
    GAME_URL: str = ""
    
    # 日誌
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """獲取配置單例"""
    return Settings()


# 項目根目錄
BASE_DIR = Path(__file__).resolve().parent.parent.parent

