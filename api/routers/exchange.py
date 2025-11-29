"""
Lucky Red - 貨幣兌換路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional, Dict, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import httpx
from loguru import logger

from shared.database.connection import get_db_session
from shared.database.models import User, Transaction, CurrencyType
from api.utils.telegram_auth import get_tg_id_from_header

router = APIRouter()

# 匯率緩存（避免頻繁請求）
_rate_cache: Dict[str, Tuple[Decimal, datetime]] = {}
CACHE_DURATION = timedelta(minutes=5)  # 緩存5分鐘


class ExchangeRequest(BaseModel):
    """兌換請求"""
    from_currency: CurrencyType
    to_currency: CurrencyType
    amount: float = Field(..., gt=0)


class ExchangeResponse(BaseModel):
    """兌換響應"""
    success: bool
    from_currency: str
    to_currency: str
    from_amount: float
    to_amount: float
    exchange_rate: float
    transaction_id: int
    message: str


class ExchangeRateResponse(BaseModel):
    """匯率響應"""
    from_currency: str
    to_currency: str
    rate: float
    source: str  # "market" 或 "fixed"
    updated_at: Optional[datetime] = None


# 固定匯率配置（用於 POINTS/ENERGY，這些不是市場交易貨幣）
FIXED_RATES = {
    (CurrencyType.USDT, CurrencyType.POINTS): Decimal("10"),
    (CurrencyType.POINTS, CurrencyType.USDT): Decimal("0.1"),
    (CurrencyType.TON, CurrencyType.POINTS): None,  # 需要通過 USDT 計算
    (CurrencyType.POINTS, CurrencyType.TON): None,  # 需要通過 USDT 計算
}


async def get_binance_price(symbol: str) -> Optional[Decimal]:
    """從幣安 API 獲取價格"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            )
            response.raise_for_status()
            data = response.json()
            return Decimal(str(data["price"]))
    except Exception as e:
        logger.warning(f"Failed to fetch price from Binance for {symbol}: {e}")
        return None


async def get_market_rate(from_currency: CurrencyType, to_currency: CurrencyType) -> Optional[Decimal]:
    """獲取市場匯率（從幣安或其他來源）"""
    # 檢查緩存
    cache_key = f"{from_currency.value}_{to_currency.value}"
    if cache_key in _rate_cache:
        rate, cached_time = _rate_cache[cache_key]
        if datetime.utcnow() - cached_time < CACHE_DURATION:
            return rate
    
    # USDT <-> TON 從幣安獲取
    if from_currency == CurrencyType.USDT and to_currency == CurrencyType.TON:
        price = await get_binance_price("TONUSDT")
        if price:
            _rate_cache[cache_key] = (price, datetime.utcnow())
            return price
    elif from_currency == CurrencyType.TON and to_currency == CurrencyType.USDT:
        price = await get_binance_price("TONUSDT")
        if price:
            rate = Decimal("1") / price
            _rate_cache[cache_key] = (rate, datetime.utcnow())
            return rate
    
    return None


async def get_exchange_rate(from_currency: CurrencyType, to_currency: CurrencyType) -> Decimal:
    """獲取匯率（優先從市場獲取，否則使用固定匯率）"""
    if from_currency == to_currency:
        return Decimal("1.0")
    
    # 嘗試從市場獲取匯率
    market_rate = await get_market_rate(from_currency, to_currency)
    if market_rate:
        return market_rate
    
    # 如果是固定匯率，直接返回
    fixed_rate = FIXED_RATES.get((from_currency, to_currency))
    if fixed_rate is not None:
        return fixed_rate
    
    # 如果是通過 USDT 計算的匯率
    if (from_currency, to_currency) == (CurrencyType.TON, CurrencyType.POINTS):
        # TON -> POINTS: 先獲取 TON/USDT，然後乘以 USDT/POINTS
        ton_usdt = await get_market_rate(CurrencyType.TON, CurrencyType.USDT)
        if ton_usdt:
            usdt_points = FIXED_RATES[(CurrencyType.USDT, CurrencyType.POINTS)]
            return ton_usdt * usdt_points
    elif (from_currency, to_currency) == (CurrencyType.POINTS, CurrencyType.TON):
        # POINTS -> TON: 先獲取 POINTS/USDT，然後乘以 USDT/TON
        points_usdt = FIXED_RATES[(CurrencyType.POINTS, CurrencyType.USDT)]
        usdt_ton = await get_market_rate(CurrencyType.USDT, CurrencyType.TON)
        if usdt_ton:
            return points_usdt * usdt_ton
    
    # 如果都失敗，使用備用固定匯率
    fallback_rates = {
        (CurrencyType.USDT, CurrencyType.TON): Decimal("1.2"),
        (CurrencyType.TON, CurrencyType.USDT): Decimal("0.83"),
        (CurrencyType.TON, CurrencyType.POINTS): Decimal("12"),
        (CurrencyType.POINTS, CurrencyType.TON): Decimal("0.083"),
    }
    
    rate = fallback_rates.get((from_currency, to_currency))
    if rate is None:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的兌換: {from_currency.value} -> {to_currency.value}"
        )
    
    logger.warning(f"Using fallback rate for {from_currency.value} -> {to_currency.value}: {rate}")
    return rate


@router.post("/exchange", response_model=ExchangeResponse)
async def exchange_currency(
    request: ExchangeRequest,
    tg_id: Optional[int] = Depends(get_tg_id_from_header),
    db: AsyncSession = Depends(get_db_session)
):
    """兌換貨幣"""
    if tg_id is None:
        raise HTTPException(status_code=401, detail="Telegram user ID is required")
    
    if request.from_currency == request.to_currency:
        raise HTTPException(status_code=400, detail="不能兌換相同貨幣")
    
    # 查找用戶
    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 驗證金額
    amount = Decimal(str(request.amount))
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")
    
    # 檢查餘額
    from_balance_field = f"balance_{request.from_currency.value}"
    current_from_balance = getattr(user, from_balance_field, 0) or Decimal(0)
    
    if current_from_balance < amount:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Current: {current_from_balance} {request.from_currency.value.upper()}, Required: {amount} {request.from_currency.value.upper()}"
        )
    
    # 獲取匯率
    exchange_rate = await get_exchange_rate(request.from_currency, request.to_currency)
    
    # 計算兌換後的金額
    to_amount = amount * exchange_rate
    to_amount = round(to_amount, 8)
    
    # 更新餘額
    new_from_balance = current_from_balance - amount
    
    to_balance_field = f"balance_{request.to_currency.value}"
    current_to_balance = getattr(user, to_balance_field, 0) or Decimal(0)
    new_to_balance = current_to_balance + to_amount
    
    setattr(user, from_balance_field, new_from_balance)
    setattr(user, to_balance_field, new_to_balance)
    
    # 創建兌換交易記錄（兩筆：一筆扣除，一筆增加）
    # 扣除交易
    from_transaction = Transaction(
        user_id=user.id,
        type="exchange",
        currency=request.from_currency,
        amount=-amount,  # 負數表示扣除
        balance_before=current_from_balance,
        balance_after=new_from_balance,
        ref_id=f"exchange_to_{request.to_currency.value}",
        note=f"兌換: {amount} {request.from_currency.value.upper()} -> {to_amount} {request.to_currency.value.upper()}",
        status="completed"
    )
    
    # 增加交易
    to_transaction = Transaction(
        user_id=user.id,
        type="exchange",
        currency=request.to_currency,
        amount=to_amount,
        balance_before=current_to_balance,
        balance_after=new_to_balance,
        ref_id=f"exchange_from_{request.from_currency.value}",
        note=f"兌換: {amount} {request.from_currency.value.upper()} -> {to_amount} {request.to_currency.value.upper()}",
        status="completed"
    )
    
    db.add(from_transaction)
    db.add(to_transaction)
    await db.commit()
    await db.refresh(to_transaction)
    
    logger.info(
        f"Currency exchanged: user_id={user.id}, "
        f"{amount} {request.from_currency.value} -> {to_amount} {request.to_currency.value}, "
        f"rate={exchange_rate}"
    )
    
    return ExchangeResponse(
        success=True,
        from_currency=request.from_currency.value,
        to_currency=request.to_currency.value,
        from_amount=float(amount),
        to_amount=float(to_amount),
        exchange_rate=float(exchange_rate),
        transaction_id=to_transaction.id,
        message=f"成功兌換 {amount} {request.from_currency.value.upper()} = {to_amount} {request.to_currency.value.upper()}"
    )


@router.get("/exchange/rate", response_model=ExchangeRateResponse)
async def get_exchange_rate_api(
    from_currency: CurrencyType = Query(..., description="源貨幣"),
    to_currency: CurrencyType = Query(..., description="目標貨幣"),
):
    """獲取當前匯率（不認證）"""
    if from_currency == to_currency:
        return ExchangeRateResponse(
            from_currency=from_currency.value,
            to_currency=to_currency.value,
            rate=1.0,
            source="fixed",
            updated_at=datetime.utcnow()
        )
    
    # 嘗試從市場獲取
    try:
        market_rate = await get_market_rate(from_currency, to_currency)
        if market_rate:
            return ExchangeRateResponse(
                from_currency=from_currency.value,
                to_currency=to_currency.value,
                rate=float(market_rate),
                source="market",
                updated_at=datetime.utcnow()
            )
    except Exception as e:
        logger.warning(f"Failed to get market rate: {e}")
    
    # 使用固定匯率或計算（包含備用匯率）
    try:
        rate = await get_exchange_rate(from_currency, to_currency)
        return ExchangeRateResponse(
            from_currency=from_currency.value,
            to_currency=to_currency.value,
            rate=float(rate),
            source="fixed",
            updated_at=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Failed to get exchange rate: {e}")
        # 即使出錯也返回備用匯率，確保 API 不會失敗
        fallback_rates = {
            (CurrencyType.USDT, CurrencyType.TON): Decimal("1.2"),
            (CurrencyType.TON, CurrencyType.USDT): Decimal("0.83"),
            (CurrencyType.USDT, CurrencyType.POINTS): Decimal("10"),
            (CurrencyType.POINTS, CurrencyType.USDT): Decimal("0.1"),
            (CurrencyType.TON, CurrencyType.POINTS): Decimal("12"),
            (CurrencyType.POINTS, CurrencyType.TON): Decimal("0.083"),
        }
        fallback_rate = fallback_rates.get((from_currency, to_currency))
        if fallback_rate:
            return ExchangeRateResponse(
                from_currency=from_currency.value,
                to_currency=to_currency.value,
                rate=float(fallback_rate),
                source="fixed",
                updated_at=datetime.utcnow()
            )
        raise HTTPException(
            status_code=400,
            detail=f"無法獲取匯率: {str(e)}"
        )
