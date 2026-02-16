import datetime
from decimal import Decimal

from pydantic import BaseModel


class QuoteOut(BaseModel):
    trade_date: datetime.date
    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    close: Decimal
    adj_close: Decimal | None = None
    volume: int | None = None
    value: Decimal | None = None

    model_config = {"from_attributes": True}


class QuoteTimeSeries(BaseModel):
    security_id: int
    ticker: str
    currency: str
    quotes: list[QuoteOut]
    total: int


class QuoteStats(BaseModel):
    security_id: int
    ticker: str
    last_price: Decimal | None = None
    last_date: datetime.date | None = None
    high_52w: Decimal | None = None
    low_52w: Decimal | None = None
    avg_volume_30d: Decimal | None = None
    return_1m: Decimal | None = None
    return_3m: Decimal | None = None
    return_ytd: Decimal | None = None
    return_1y: Decimal | None = None
    volatility_1y: Decimal | None = None
