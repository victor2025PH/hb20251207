"""
Lucky Red - 數據模型
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, 
    Numeric, Boolean, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship

from .database import Base


class CurrencyType(str, Enum):
    """貨幣類型"""
    USDT = "usdt"
    TON = "ton"
    STARS = "stars"
    POINTS = "points"


class RedPacketType(str, Enum):
    """紅包類型"""
    RANDOM = "random"      # 隨機金額
    EQUAL = "equal"        # 平均分配
    LUCKY = "lucky"        # 手氣最佳


class RedPacketStatus(str, Enum):
    """紅包狀態"""
    ACTIVE = "active"      # 進行中
    COMPLETED = "completed"  # 已搶完
    EXPIRED = "expired"    # 已過期
    REFUNDED = "refunded"  # 已退款


class User(Base):
    """用戶表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(64), index=True)
    first_name = Column(String(64))
    last_name = Column(String(64))
    
    # 餘額
    balance_usdt = Column(Numeric(18, 6), default=Decimal("0"))
    balance_ton = Column(Numeric(18, 6), default=Decimal("0"))
    balance_stars = Column(BigInteger, default=0)
    balance_points = Column(BigInteger, default=0)
    
    # 統計
    total_sent = Column(Numeric(18, 6), default=Decimal("0"))
    total_received = Column(Numeric(18, 6), default=Decimal("0"))
    packets_sent = Column(Integer, default=0)
    packets_received = Column(Integer, default=0)
    
    # 等級和經驗
    level = Column(Integer, default=1)
    xp = Column(BigInteger, default=0)
    energy = Column(Integer, default=100)
    
    # 邀請
    invited_by = Column(BigInteger, ForeignKey("users.tg_id"), nullable=True)
    invite_code = Column(String(16), unique=True)
    invite_count = Column(Integer, default=0)
    invite_earnings = Column(Numeric(18, 6), default=Decimal("0"))
    
    # 簽到
    last_checkin = Column(DateTime, nullable=True)
    checkin_streak = Column(Integer, default=0)
    
    # 狀態
    is_banned = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # 時間
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 關係
    sent_packets = relationship("RedPacket", back_populates="sender", foreign_keys="RedPacket.sender_id")
    claims = relationship("RedPacketClaim", back_populates="user")
    
    __table_args__ = (
        Index("ix_users_username_lower", "username"),
    )


class RedPacket(Base):
    """紅包表"""
    __tablename__ = "red_packets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    
    # 發送者
    sender_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    sender = relationship("User", back_populates="sent_packets", foreign_keys=[sender_id])
    
    # 目標群組
    chat_id = Column(BigInteger, nullable=True, index=True)
    chat_title = Column(String(128))
    message_id = Column(BigInteger)
    
    # 紅包信息
    currency = Column(String(16), default=CurrencyType.USDT.value)
    packet_type = Column(String(16), default=RedPacketType.RANDOM.value)
    total_amount = Column(Numeric(18, 6), nullable=False)
    remaining_amount = Column(Numeric(18, 6), nullable=False)
    total_count = Column(Integer, nullable=False)
    remaining_count = Column(Integer, nullable=False)
    
    # 祝福語
    message = Column(Text, default="Best Wishes! 🧧")
    
    # 狀態
    status = Column(String(16), default=RedPacketStatus.ACTIVE.value)
    
    # 時間
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # 關係
    claims = relationship("RedPacketClaim", back_populates="red_packet")
    
    __table_args__ = (
        Index("ix_red_packets_chat_status", "chat_id", "status"),
        Index("ix_red_packets_sender_status", "sender_id", "status"),
    )


class RedPacketClaim(Base):
    """紅包領取記錄"""
    __tablename__ = "red_packet_claims"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 關聯
    packet_id = Column(Integer, ForeignKey("red_packets.id"), nullable=False)
    red_packet = relationship("RedPacket", back_populates="claims")
    
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    user = relationship("User", back_populates="claims")
    
    # 領取金額
    amount = Column(Numeric(18, 6), nullable=False)
    is_luckiest = Column(Boolean, default=False)  # 手氣最佳
    
    # 時間
    claimed_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_claims_packet_user", "packet_id", "user_id", unique=True),
    )


class Transaction(Base):
    """交易記錄"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    
    # 交易類型: recharge, withdraw, send, receive, invite_bonus, checkin, refund
    tx_type = Column(String(32), nullable=False)
    currency = Column(String(16), default=CurrencyType.USDT.value)
    amount = Column(Numeric(18, 6), nullable=False)
    
    # 餘額快照
    balance_before = Column(Numeric(18, 6))
    balance_after = Column(Numeric(18, 6))
    
    # 關聯ID（紅包ID、充值訂單ID等）
    ref_id = Column(String(64), nullable=True)
    
    # 備註
    note = Column(Text, nullable=True)
    
    # 狀態
    status = Column(String(16), default="completed")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_tx_user_type", "user_id", "tx_type"),
        Index("ix_tx_created", "created_at"),
    )


class DailyCheckin(Base):
    """每日簽到記錄"""
    __tablename__ = "daily_checkins"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    
    checkin_date = Column(DateTime, nullable=False)
    day_of_streak = Column(Integer, default=1)
    reward_points = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_checkin_user_date", "user_id", "checkin_date", unique=True),
    )

