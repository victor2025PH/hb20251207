"""
Lucky Red - 共享配置
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """應用配置"""
    
    # Telegram Bot
    bot_token: str = ""
    bot_username: str = "LuckyRedBot"
    
    # 管理員
    admin_ids: str = ""
    
    # 數據庫
    database_url: str = "postgresql://localhost/luckyred"
    
    # URLs
    miniapp_url: str = "https://mini.usdt2026.cc"
    api_url: str = "https://mini.usdt2026.cc/api"
    admin_url: str = "https://admin.usdt2026.cc"
    
    # 安全
    secret_key: str = "change-this-secret-key"
    
    # 環境
    environment: str = "development"
    log_level: str = "INFO"
    
    @property
    def admin_id_list(self) -> list[int]:
        """獲取管理員 ID 列表"""
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """獲取配置單例"""
    return Settings()


settings = get_settings()

