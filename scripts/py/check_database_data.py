#!/usr/bin/env python3
"""
检查数据库中的数据
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from shared.database.connection import get_async_db
from loguru import logger


async def check_database_data():
    """检查数据库中的数据"""
    async with get_async_db() as db:
        try:
            # 检查各个表的数据
            tables = {
                'users': '用户',
                'red_packets': '红包',
                'transactions': '交易',
                'admin_users': '管理员',
                'red_packet_claims': '红包领取',
                'checkin_records': '签到记录'
            }
            
            logger.info("=" * 50)
            logger.info("数据库数据统计")
            logger.info("=" * 50)
            
            for table, name in tables.items():
                try:
                    result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar_one()
                    logger.info(f"{name} ({table}): {count} 条记录")
                except Exception as e:
                    logger.warning(f"{name} ({table}): 查询失败 - {e}")
            
            logger.info("=" * 50)
            
            # 检查用户数据详情
            logger.info("\n用户数据示例（前5条）:")
            result = await db.execute(text("""
                SELECT id, tg_id, username, first_name, balance_usdt, balance_ton, level, created_at 
                FROM users 
                ORDER BY created_at DESC 
                LIMIT 5
            """))
            users = result.fetchall()
            if users:
                for user in users:
                    logger.info(f"  ID: {user[0]}, TG_ID: {user[1]}, 用户名: {user[2]}, 余额USDT: {user[4]}, 等级: {user[6]}")
            else:
                logger.warning("  没有用户数据")
            
            # 检查红包数据详情
            logger.info("\n红包数据示例（前5条）:")
            result = await db.execute(text("""
                SELECT id, uuid, sender_id, total_amount, total_count, claimed_count, status, created_at 
                FROM red_packets 
                ORDER BY created_at DESC 
                LIMIT 5
            """))
            redpackets = result.fetchall()
            if redpackets:
                for rp in redpackets:
                    logger.info(f"  ID: {rp[0]}, UUID: {rp[1][:20]}..., 发送者: {rp[2]}, 总金额: {rp[3]}, 状态: {rp[6]}")
            else:
                logger.warning("  没有红包数据")
            
            # 检查交易数据详情
            logger.info("\n交易数据示例（前5条）:")
            result = await db.execute(text("""
                SELECT id, user_id, type, currency, amount, created_at 
                FROM transactions 
                ORDER BY created_at DESC 
                LIMIT 5
            """))
            transactions = result.fetchall()
            if transactions:
                for tx in transactions:
                    logger.info(f"  ID: {tx[0]}, 用户: {tx[1]}, 类型: {tx[2]}, 币种: {tx[3]}, 金额: {tx[4]}")
            else:
                logger.warning("  没有交易数据")
            
        except Exception as e:
            logger.error(f"❌ 检查失败: {e}", exc_info=True)
            raise


if __name__ == "__main__":
    asyncio.run(check_database_data())

