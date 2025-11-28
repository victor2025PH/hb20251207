#!/usr/bin/env python3
"""
检查并修复数据库结构（添加新字段）
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database.connection import sync_engine, init_db
from shared.database.models import RedPacket, RedPacketClaim
from sqlalchemy import inspect, text
from loguru import logger

def check_and_fix_database():
    """检查数据库结构并添加缺失的字段"""
    inspector = inspect(sync_engine)
    
    # 检查 red_packets 表
    redpacket_cols = {c['name']: c for c in inspector.get_columns('red_packets')}
    logger.info(f"RedPacket columns: {list(redpacket_cols.keys())}")
    
    # 检查 red_packet_claims 表
    claim_cols = {c['name']: c for c in inspector.get_columns('red_packet_claims')}
    logger.info(f"RedPacketClaim columns: {list(claim_cols.keys())}")
    
    with sync_engine.connect() as conn:
        # 检查并添加 bomb_number 字段到 red_packets
        if 'bomb_number' not in redpacket_cols:
            logger.info("Adding bomb_number column to red_packets...")
            try:
                conn.execute(text("ALTER TABLE red_packets ADD COLUMN bomb_number INTEGER"))
                conn.commit()
                logger.info("✅ Added bomb_number column")
            except Exception as e:
                logger.error(f"Failed to add bomb_number: {e}")
                conn.rollback()
        else:
            logger.info("✅ bomb_number column already exists")
        
        # 检查并添加 is_bomb 字段到 red_packet_claims
        if 'is_bomb' not in claim_cols:
            logger.info("Adding is_bomb column to red_packet_claims...")
            try:
                conn.execute(text("ALTER TABLE red_packet_claims ADD COLUMN is_bomb BOOLEAN DEFAULT FALSE"))
                conn.commit()
                logger.info("✅ Added is_bomb column")
            except Exception as e:
                logger.error(f"Failed to add is_bomb: {e}")
                conn.rollback()
        else:
            logger.info("✅ is_bomb column already exists")
        
        # 检查并添加 penalty_amount 字段到 red_packet_claims
        if 'penalty_amount' not in claim_cols:
            logger.info("Adding penalty_amount column to red_packet_claims...")
            try:
                # 根据数据库类型选择合适的数据类型
                db_url = str(sync_engine.url)
                if 'sqlite' in db_url.lower():
                    conn.execute(text("ALTER TABLE red_packet_claims ADD COLUMN penalty_amount NUMERIC(20, 8)"))
                else:  # PostgreSQL
                    conn.execute(text("ALTER TABLE red_packet_claims ADD COLUMN penalty_amount NUMERIC(20, 8)"))
                conn.commit()
                logger.info("✅ Added penalty_amount column")
            except Exception as e:
                logger.error(f"Failed to add penalty_amount: {e}")
                conn.rollback()
        else:
            logger.info("✅ penalty_amount column already exists")
    
    logger.info("✅ Database structure check and fix completed!")

if __name__ == "__main__":
    check_and_fix_database()

