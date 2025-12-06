"""
Deep Link路由
处理智能链接重定向
"""
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import RedirectResponse
from loguru import logger
from api.services.deep_link_service import DeepLinkService

router = APIRouter(prefix="/link", tags=["Deep Link"])


@router.get("/packet/{packet_uuid}")
async def redirect_packet(
    packet_uuid: str,
    request: Request
):
    """
    红包Deep Link重定向
    
    根据User-Agent自动重定向到Telegram MiniApp或Web版本
    """
    user_agent = request.headers.get('user-agent', '')
    redirect_url = DeepLinkService.get_redirect_url('packet', packet_uuid, user_agent)
    
    logger.info(f"Deep link redirect: packet={packet_uuid}, platform={DeepLinkService.detect_platform_from_user_agent(user_agent)}, url={redirect_url}")
    
    return RedirectResponse(url=redirect_url, status_code=302)


@router.get("/invite/{referral_code}")
async def redirect_invite(
    referral_code: str,
    request: Request
):
    """
    邀请链接Deep Link重定向
    
    根据User-Agent自动重定向到Telegram MiniApp或Web版本
    """
    user_agent = request.headers.get('user-agent', '')
    redirect_url = DeepLinkService.get_redirect_url('invite', referral_code, user_agent)
    
    logger.info(f"Deep link redirect: invite={referral_code}, platform={DeepLinkService.detect_platform_from_user_agent(user_agent)}, url={redirect_url}")
    
    return RedirectResponse(url=redirect_url, status_code=302)


@router.get("/magic-link")
async def redirect_magic_link(
    token: str = Query(..., description="Magic Link Token"),
    request: Request = None
):
    """
    Magic Link重定向
    
    重定向到Web版本的Magic Link登录页面
    """
    redirect_url = DeepLinkService.get_redirect_url('magic-link', token)
    
    logger.info(f"Magic link redirect: token={token[:20]}...")
    
    return RedirectResponse(url=redirect_url, status_code=302)

