"""
测试PaymentService支付网关功能
"""
import sys
import asyncio
from pathlib import Path
from decimal import Decimal

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.payment_service import get_payment_service


async def test_payment_service():
    """测试PaymentService功能"""
    print("=" * 60)
    print("测试 PaymentService 支付网关")
    print("=" * 60)
    
    payment_service = get_payment_service()
    
    # 测试1: 获取汇率
    print("\n[测试1] 获取汇率（CNY -> USDT）")
    rate = await payment_service.get_exchange_rate('CNY', 'USDT')
    print(f"✅ 汇率: 1 USDT = {rate} CNY (含3%利润点)")
    
    # 测试2: 法币支付
    print("\n[测试2] 法币支付（100 CNY -> USDT）")
    success, transaction_id, virtual_usdt, payment_info = await payment_service.process_fiat_payment(
        amount=Decimal('100.0'),
        fiat_currency='CNY',
        provider='unionpay',
        metadata={'test': True}
    )
    
    if success:
        print(f"✅ 支付成功:")
        print(f"   交易ID: {transaction_id}")
        print(f"   支付金额: 100 CNY")
        print(f"   虚拟USDT: {virtual_usdt} USDT")
        print(f"   汇率: {payment_info.get('exchange_rate')}")
    else:
        print(f"❌ 支付失败: {payment_info}")
    
    # 测试3: 加密货币充值
    print("\n[测试3] 加密货币充值（10 USDT）")
    success, transaction_id, deposit_info = await payment_service.process_crypto_deposit(
        amount=Decimal('10.0'),
        crypto_currency='USDT',
        transaction_hash='0x1234567890abcdef',
        metadata={'test': True}
    )
    
    if success:
        print(f"✅ 充值成功:")
        print(f"   交易ID: {transaction_id}")
        print(f"   充值金额: 10 USDT")
        print(f"   交易哈希: {deposit_info.get('transaction_hash')}")
    else:
        print(f"❌ 充值失败: {deposit_info}")
    
    # 测试4: 提现
    print("\n[测试4] 提现（5 USDT）")
    success, transaction_id, withdrawal_info = await payment_service.process_withdrawal(
        amount=Decimal('5.0'),
        currency='USDT',
        destination='0xabcdef1234567890',
        withdrawal_type='crypto',
        metadata={'test': True}
    )
    
    if success:
        print(f"✅ 提现成功:")
        print(f"   交易ID: {transaction_id}")
        print(f"   提现金额: 5 USDT")
        print(f"   目标地址: {withdrawal_info.get('destination')}")
    else:
        print(f"❌ 提现失败: {withdrawal_info}")
    
    print("\n" + "=" * 60)
    print("✅ PaymentService测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

