"""
健康检查和监控端点
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any
import redis
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.database.connection import get_db_session
from shared.config.settings import get_settings
from loguru import logger

router = APIRouter(prefix="/health", tags=["健康检查"])

settings = get_settings()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """基础健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "luckyred-api",
        "version": settings.APP_VERSION
    }


@router.get("/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """详细健康检查（包括数据库连接）"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "luckyred-api",
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    # 检查数据库连接
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": str(e)
        }
        logger.error(f"Database health check failed: {e}")
    
    # 检查Redis连接（如果配置了）
    if settings.REDIS_URL:
        try:
            r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            r.ping()
            health_status["checks"]["redis"] = {
                "status": "healthy",
                "message": "Redis connection successful"
            }
        except Exception as e:
            health_status["checks"]["redis"] = {
                "status": "unhealthy",
                "message": str(e)
            }
            logger.warning(f"Redis health check failed: {e}")
    else:
        health_status["checks"]["redis"] = {
            "status": "not_configured",
            "message": "Redis not configured"
        }
    
    return health_status


@router.get("/metrics")
async def get_metrics(
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """获取系统指标"""
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": "luckyred-api",
        "version": settings.APP_VERSION
    }
    
    # 数据库指标
    try:
        # 获取用户总数
        user_count_result = await db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = user_count_result.scalar() or 0
        
        # 获取红包总数
        packet_count_result = await db.execute(text("SELECT COUNT(*) FROM red_packets"))
        packet_count = packet_count_result.scalar() or 0
        
        metrics["database"] = {
            "users": user_count,
            "red_packets": packet_count
        }
    except Exception as e:
        logger.error(f"Failed to get database metrics: {e}")
        metrics["database"] = {"error": str(e)}
    
    # Redis指标（如果配置了）
    if settings.REDIS_URL:
        try:
            r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            info = r.info()
            metrics["redis"] = {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "N/A"),
                "keyspace": info.get("db0", {})
            }
        except Exception as e:
            logger.warning(f"Failed to get Redis metrics: {e}")
            metrics["redis"] = {"error": str(e)}
    
    return metrics

