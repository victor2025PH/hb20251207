"""
Lucky Red (搶紅包) - 數據庫連接
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import contextmanager, asynccontextmanager
from typing import Generator, AsyncGenerator

from shared.config.settings import get_settings
from shared.database.models import Base

settings = get_settings()

# 同步引擎 (用於 Bot)
sync_engine = create_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)

# 異步引擎 (用於 API)
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def init_db():
    """初始化數據庫表"""
    Base.metadata.create_all(bind=sync_engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """獲取同步數據庫會話"""
    db = SyncSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """獲取異步數據庫會話"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依賴注入用"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

