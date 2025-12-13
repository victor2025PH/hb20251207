"""
Lucky Red - 緩存工具
提供用戶數據緩存功能（只緩存純數據，不緩存 ORM 對象）
"""
import time
from typing import Optional, Dict, Any
from loguru import logger


class UserCache:
    """用戶數據緩存（只緩存純數據字典，不緩存 ORM 對象）"""
    _cache: Dict[str, Dict[str, Any]] = {}
    _cache_ttl: int = 300  # 5分鐘
    
    @classmethod
    def get_user_data(cls, tg_id: int, db) -> Optional[Dict[str, Any]]:
        """
        獲取用戶數據（帶緩存）
        
        Args:
            tg_id: Telegram 用戶 ID
            db: 數據庫會話
        
        Returns:
            用戶數據字典或 None
        """
        from shared.database.models import User
        
        cache_key = f"user_{tg_id}"
        cached = cls._cache.get(cache_key)
        
        # 檢查緩存是否有效
        if cached and (time.time() - cached['time']) < cls._cache_ttl:
            logger.debug(f"Cache hit for user {tg_id}")
            return cached['data']
        
        # 緩存未命中，從數據庫查詢
        logger.debug(f"Cache miss for user {tg_id}, querying database")
        user = db.query(User).filter(User.tg_id == tg_id).first()
        
        if user:
            # 在會話內提取所有需要的數據為純字典
            user_data = {
                'id': user.id,
                'tg_id': user.tg_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'level': user.level,
                'xp': user.xp,
                'balance_usdt': float(user.balance_usdt or 0),
                'balance_ton': float(user.balance_ton or 0),
                'balance_stars': user.balance_stars or 0,
                'balance_points': user.balance_points or 0,
                'language_code': getattr(user, 'language_code', None) or 'zh-TW',
                'interaction_mode': getattr(user, 'interaction_mode', None) or 'auto',
                'last_interaction_mode': getattr(user, 'last_interaction_mode', None),
                'invited_by': user.invited_by,
                'invite_code': user.invite_code,
                'invite_count': user.invite_count or 0,
                'invite_earnings': float(user.invite_earnings or 0),
                'is_banned': getattr(user, 'is_banned', False),
            }
            
            cls._cache[cache_key] = {
                'data': user_data,
                'time': time.time()
            }
            
            return user_data
        
        return None
    
    @classmethod
    def invalidate(cls, tg_id: int):
        """
        清除用戶緩存
        
        Args:
            tg_id: Telegram 用戶 ID
        """
        cache_key = f"user_{tg_id}"
        if cache_key in cls._cache:
            del cls._cache[cache_key]
            logger.debug(f"Cache invalidated for user {tg_id}")
    
    @classmethod
    def clear_all(cls):
        """清除所有緩存"""
        cls._cache.clear()
        logger.info("All user cache cleared")
    
    @classmethod
    def set_ttl(cls, ttl: int):
        """
        設置緩存 TTL（秒）
        
        Args:
            ttl: 緩存生存時間（秒）
        """
        cls._cache_ttl = ttl
        logger.info(f"Cache TTL set to {ttl} seconds")
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """
        獲取緩存統計信息
        
        Returns:
            緩存統計字典
        """
        now = time.time()
        valid_entries = sum(
            1 for cached in cls._cache.values()
            if (now - cached['time']) < cls._cache_ttl
        )
        
        return {
            'total_entries': len(cls._cache),
            'valid_entries': valid_entries,
            'expired_entries': len(cls._cache) - valid_entries,
            'ttl': cls._cache_ttl
        }
    
    @classmethod
    def cleanup_expired(cls):
        """清理過期的緩存條目"""
        now = time.time()
        expired_keys = [
            key for key, cached in cls._cache.items()
            if (now - cached['time']) >= cls._cache_ttl
        ]
        
        for key in expired_keys:
            del cls._cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
