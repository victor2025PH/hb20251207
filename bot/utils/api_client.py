"""
Lucky Red - 統一的 API 客戶端
處理所有與後端 API 的通信
"""
import httpx
from typing import Optional, Dict, Any
from loguru import logger
from shared.config.settings import get_settings

settings = get_settings()


class APIClient:
    """統一的 API 客戶端"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        初始化 API 客戶端
        
        Args:
            base_url: API 基礎 URL，如果不提供則從配置讀取
        """
        self.base_url = base_url or settings.api_url
        self.client = httpx.AsyncClient(timeout=10.0)
        logger.debug(f"APIClient initialized with base_url: {self.base_url}")
    
    async def post(
        self,
        endpoint: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
        tg_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        發送 POST 請求
        
        Args:
            endpoint: API 端點（例如：/redpackets/create）
            data: 請求數據
            headers: 額外的請求頭
            tg_id: Telegram 用戶 ID（用於構建 initData）
        
        Returns:
            API 響應的 JSON 數據
        
        Raises:
            httpx.HTTPStatusError: HTTP 狀態錯誤
            httpx.RequestError: 請求錯誤
        """
        url = f"{self.base_url}{endpoint}"
        
        # 構建請求頭
        request_headers = headers or {}
        if tg_id:
            # 構建簡化的 initData（生產環境應使用完整的 Telegram 驗證）
            init_data = f'user={{"id":{tg_id}}}'
            request_headers["X-Telegram-Init-Data"] = init_data
        
        try:
            import time
            from bot.utils.logging_helpers import log_api_call
            
            start_time = time.time()
            logger.debug(f"POST {url} with data: {data}")
            response = await self.client.post(
                url,
                json=data,
                headers=request_headers
            )
            
            duration = time.time() - start_time
            # 記錄響應狀態
            logger.debug(f"Response status: {response.status_code}")
            
            # 檢查 HTTP 狀態
            response.raise_for_status()
            
            # 記錄 API 調用
            log_api_call(endpoint, "POST", response.status_code, duration)
            
            # 解析 JSON 響應
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                logger.warning(f"Non-JSON response: {response.text}")
                return {"success": False, "message": response.text}
                
        except httpx.HTTPStatusError as e:
            import time
            from bot.utils.logging_helpers import log_api_call
            
            duration = time.time() - start_time if 'start_time' in locals() else None
            error_detail = "未知錯誤"
            try:
                if e.response.headers.get('content-type', '').startswith('application/json'):
                    error_data = e.response.json()
                    error_detail = error_data.get('detail', e.response.text)
                else:
                    error_detail = e.response.text
            except Exception:
                error_detail = str(e)
            
            # 記錄 API 調用錯誤
            log_api_call(endpoint, "POST", e.response.status_code, duration, error_detail)
            
            logger.error(
                f"API HTTP error: {e.response.status_code} - {error_detail}",
                extra={
                    "url": url,
                    "status_code": e.response.status_code,
                    "response": error_detail
                }
            )
            raise
        
        except httpx.RequestError as e:
            logger.error(
                f"API request error: {e}",
                extra={"url": url, "error": str(e)}
            )
            raise
        
        except Exception as e:
            logger.error(
                f"Unexpected error in API call: {e}",
                exc_info=True,
                extra={"url": url}
            )
            raise
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        tg_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        發送 GET 請求
        
        Args:
            endpoint: API 端點
            params: 查詢參數
            headers: 額外的請求頭
            tg_id: Telegram 用戶 ID
        
        Returns:
            API 響應的 JSON 數據
        """
        url = f"{self.base_url}{endpoint}"
        
        request_headers = headers or {}
        if tg_id:
            init_data = f'user={{"id":{tg_id}}}'
            request_headers["X-Telegram-Init-Data"] = init_data
        
        try:
            logger.debug(f"GET {url} with params: {params}")
            response = await self.client.get(
                url,
                params=params,
                headers=request_headers
            )
            
            response.raise_for_status()
            
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                return {"success": False, "message": response.text}
                
        except httpx.HTTPStatusError as e:
            error_detail = "未知錯誤"
            try:
                if e.response.headers.get('content-type', '').startswith('application/json'):
                    error_data = e.response.json()
                    error_detail = error_data.get('detail', e.response.text)
                else:
                    error_detail = e.response.text
            except Exception:
                error_detail = str(e)
            
            logger.error(f"API GET error: {e.response.status_code} - {error_detail}")
            raise
        
        except httpx.RequestError as e:
            logger.error(f"API GET request error: {e}")
            raise
    
    async def close(self):
        """關閉 HTTP 客戶端"""
        await self.client.aclose()
    
    async def __aenter__(self):
        """異步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """異步上下文管理器出口"""
        await self.close()


# 全局 API 客戶端實例
_api_client: Optional[APIClient] = None


def get_api_client() -> APIClient:
    """獲取全局 API 客戶端實例"""
    global _api_client
    if _api_client is None:
        _api_client = APIClient()
    return _api_client
