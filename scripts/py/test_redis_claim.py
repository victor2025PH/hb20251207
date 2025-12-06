"""
测试Redis高并发抢红包功能
"""
import sys
import asyncio
from pathlib import Path
from decimal import Decimal

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.redis_claim_service import RedisClaimService


async def test_redis_claim():
    """测试Redis抢红包功能"""
    print("=" * 60)
    print("测试 Redis 高并发抢红包")
    print("=" * 60)
    
    # 测试红包UUID
    packet_uuid = "test-packet-001"
    
    # 测试1: 初始化红包
    print("\n[测试1] 初始化红包到Redis")
    success = await RedisClaimService.init_packet(
        packet_uuid=packet_uuid,
        packet_data={
            'sender_id': 1,
            'currency': 'USDT',
            'packet_type': 'RANDOM',
            'total_amount': 100.0,
            'total_count': 10,
            'claimed_amount': 0,
            'claimed_count': 0,
            'status': 'ACTIVE',
            'expires_at': 9999999999,  # 未来时间
            'bomb_number': None,
        }
    )
    
    if success:
        print(f"✅ 红包初始化成功: {packet_uuid}")
    else:
        print("❌ 红包初始化失败（Redis可能不可用）")
        print("   将使用数据库模式")
        return
    
    # 测试2: 获取红包状态
    print("\n[测试2] 获取红包状态")
    status = await RedisClaimService.get_packet_status(packet_uuid)
    if status:
        print(f"✅ 获取状态成功:")
        print(f"   已领取: {status['claimed_count']}/{status['total_count']}")
        print(f"   剩余金额: {status['remaining_amount']} USDT")
    else:
        print("❌ 获取状态失败")
    
    # 测试3: 模拟抢红包
    print("\n[测试3] 模拟抢红包（用户1）")
    import uuid
    success, error, amount, packet_status = await RedisClaimService.claim_packet(
        packet_uuid=packet_uuid,
        user_id=1,
        claim_id=str(uuid.uuid4())
    )
    
    if success:
        print(f"✅ 抢红包成功: 获得 {amount} USDT")
        print(f"   剩余: {packet_status['remaining_amount']} USDT")
        print(f"   已领取: {packet_status['claimed_count']}/{packet_status.get('total_count', 10)}")
    else:
        print(f"❌ 抢红包失败: {error}")
    
    # 测试4: 重复领取（应该失败）
    print("\n[测试4] 重复领取（应该失败）")
    success, error, amount, _ = await RedisClaimService.claim_packet(
        packet_uuid=packet_uuid,
        user_id=1,
        claim_id=str(uuid.uuid4())
    )
    
    if not success and error == 'ALREADY_CLAIMED':
        print("✅ 重复领取被正确阻止")
    else:
        print(f"❌ 重复领取检查失败: success={success}, error={error}")
    
    # 测试5: 检查用户是否已领取
    print("\n[测试5] 检查用户是否已领取")
    claimed = await RedisClaimService.check_user_claimed(packet_uuid, 1)
    if claimed:
        print("✅ 用户已领取（正确）")
    else:
        print("❌ 用户领取状态检查失败")
    
    print("\n" + "=" * 60)
    print("✅ Redis抢红包测试完成")
    print("=" * 60)


async def test_concurrent_claims():
    """测试并发抢红包"""
    print("\n" + "=" * 60)
    print("测试并发抢红包（10个用户同时抢）")
    print("=" * 60)
    
    packet_uuid = "test-packet-concurrent"
    
    # 初始化红包
    await RedisClaimService.init_packet(
        packet_uuid=packet_uuid,
        packet_data={
            'sender_id': 1,
            'currency': 'USDT',
            'packet_type': 'RANDOM',
            'total_amount': 100.0,
            'total_count': 10,
            'claimed_amount': 0,
            'claimed_count': 0,
            'status': 'ACTIVE',
            'expires_at': 9999999999,
            'bomb_number': None,
        }
    )
    
    # 并发抢红包
    import uuid
    tasks = []
    for user_id in range(1, 11):
        task = RedisClaimService.claim_packet(
            packet_uuid=packet_uuid,
            user_id=user_id,
            claim_id=str(uuid.uuid4())
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 统计结果
    success_count = sum(1 for r in results if isinstance(r, tuple) and r[0])
    failed_count = len(results) - success_count
    
    print(f"\n✅ 并发测试完成:")
    print(f"   成功: {success_count}/10")
    print(f"   失败: {failed_count}/10")
    
    # 检查最终状态
    status = await RedisClaimService.get_packet_status(packet_uuid)
    if status:
        print(f"   最终状态: 已领取 {status['claimed_count']}/10")
        print(f"   剩余金额: {status['remaining_amount']} USDT")


async def main():
    """主函数"""
    await test_redis_claim()
    await test_concurrent_claims()
    print("\n所有测试完成！")


if __name__ == "__main__":
    asyncio.run(main())

