"""
Lucky Red - 數據庫連接
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

from .config import settings

# 創建引擎
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Session 工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 模型基類
Base = declarative_base()


def get_db():
    """FastAPI 依賴注入用"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_session():
    """上下文管理器方式獲取 session"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """初始化數據庫表"""
    from . import models  # noqa
    Base.metadata.create_all(bind=engine)

