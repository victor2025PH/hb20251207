"""
监控中间件
用于记录请求日志和性能指标
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from loguru import logger
from typing import Callable


class MonitoringMiddleware(BaseHTTPMiddleware):
    """监控中间件 - 记录请求日志和性能指标"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        # 跳过健康检查端点的详细日志（避免日志过多）
        skip_logging = path in ["/health", "/health/", "/health/detailed", "/health/metrics"]
        
        if not skip_logging:
            logger.info(f"📥 {method} {path} from {client_ip}")
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录响应信息
            status_code = response.status_code
            
            if not skip_logging:
                # 根据状态码选择日志级别
                if status_code >= 500:
                    logger.error(f"❌ {method} {path} - {status_code} - {process_time:.3f}s")
                elif status_code >= 400:
                    logger.warning(f"⚠️  {method} {path} - {status_code} - {process_time:.3f}s")
                else:
                    logger.info(f"✅ {method} {path} - {status_code} - {process_time:.3f}s")
            
            # 添加性能指标到响应头
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            logger.error(f"💥 {method} {path} - Exception: {str(e)} - {process_time:.3f}s")
            raise

