"""
Deep Linking服务
智能路由：根据平台自动打开Telegram MiniApp或Web版本
"""
from typing import Optional, Dict, Any
from urllib.parse import urlencode, quote
from loguru import logger
from shared.config.settings import get_settings

settings = get_settings()


class DeepLinkService:
    """Deep Linking服务"""
    
    @staticmethod
    def generate_packet_link(packet_uuid: str, platform: Optional[str] = None) -> Dict[str, str]:
        """
        生成红包Deep Link
        
        Args:
            packet_uuid: 红包UUID
            platform: 目标平台（telegram, web, auto）
        
        Returns:
            包含不同平台链接的字典
        """
        base_url = settings.MINIAPP_URL
        
        # Telegram MiniApp链接
        telegram_link = f"https://t.me/{settings.BOT_USERNAME}?start=packet_{packet_uuid}"
        
        # Web版本链接
        web_link = f"{base_url}/packets/{packet_uuid}"
        
        # 通用链接（自动检测平台）
        universal_link = f"{base_url}/packet/{packet_uuid}"
        
        return {
            'telegram': telegram_link,
            'web': web_link,
            'universal': universal_link,
            'packet_uuid': packet_uuid
        }
    
    @staticmethod
    def generate_invite_link(referral_code: str, platform: Optional[str] = None) -> Dict[str, str]:
        """
        生成邀请链接
        
        Args:
            referral_code: 推荐码
            platform: 目标平台（telegram, web, auto）
        
        Returns:
            包含不同平台链接的字典
        """
        base_url = settings.MINIAPP_URL
        
        # Telegram MiniApp链接
        telegram_link = f"https://t.me/{settings.BOT_USERNAME}?start=ref_{referral_code}"
        
        # Web版本链接
        web_link = f"{base_url}/invite/{referral_code}"
        
        # 通用链接（自动检测平台）
        universal_link = f"{base_url}/invite/{referral_code}"
        
        return {
            'telegram': telegram_link,
            'web': web_link,
            'universal': universal_link,
            'referral_code': referral_code
        }
    
    @staticmethod
    def generate_magic_link_link(token: str) -> str:
        """
        生成Magic Link（跨平台登录）
        
        Args:
            token: Magic Link Token
        
        Returns:
            Magic Link URL
        """
        base_url = settings.MINIAPP_URL
        return f"{base_url}/auth/magic-link?token={token}"
    
    @staticmethod
    def detect_platform_from_user_agent(user_agent: str) -> str:
        """
        从User-Agent检测平台
        
        Args:
            user_agent: HTTP User-Agent字符串
        
        Returns:
            平台类型（telegram, whatsapp, facebook, x, web）
        """
        ua_lower = user_agent.lower()
        
        if 'telegram' in ua_lower:
            return 'telegram'
        elif 'whatsapp' in ua_lower:
            return 'whatsapp'
        elif 'facebook' in ua_lower or 'fb' in ua_lower:
            return 'facebook'
        elif 'twitter' in ua_lower or 'x.com' in ua_lower:
            return 'x'
        else:
            return 'web'
    
    @staticmethod
    def get_redirect_url(link_type: str, identifier: str, user_agent: Optional[str] = None) -> str:
        """
        根据链接类型和平台智能重定向
        
        Args:
            link_type: 链接类型（packet, invite, magic-link）
            identifier: 标识符（packet_uuid, referral_code, token）
            user_agent: HTTP User-Agent（可选）
        
        Returns:
            重定向URL
        """
        platform = 'web'
        if user_agent:
            platform = DeepLinkService.detect_platform_from_user_agent(user_agent)
        
        if link_type == 'packet':
            links = DeepLinkService.generate_packet_link(identifier, platform)
            if platform == 'telegram':
                return links['telegram']
            else:
                return links['web']
        
        elif link_type == 'invite':
            links = DeepLinkService.generate_invite_link(identifier, platform)
            if platform == 'telegram':
                return links['telegram']
            else:
                return links['web']
        
        elif link_type == 'magic-link':
            return DeepLinkService.generate_magic_link_link(identifier)
        
        else:
            # 默认返回Web链接
            return f"{settings.MINIAPP_URL}/{link_type}/{identifier}"

