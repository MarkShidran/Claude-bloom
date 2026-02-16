import datetime
from decimal import Decimal

from pydantic import BaseModel


class MultipleOut(BaseModel):
    id: int
    company_id: int
    calc_date: datetime.date
    period_end: datetime.date
    pe: Decimal | None = None
    ev_ebitda: Decimal | None = None
    ev_sales: Decimal | None = None
    pb: Decimal | None = None
    ps: Decimal | None = None
    roe: Decimal | None = None
    roa: Decimal | None = None
    debt_ebitda: Decimal | None = None
    dividend_yield: Decimal | None = None
    market_cap: Decimal | None = None
    enterprise_value: Decimal | None = None
    currency: str

    model_config = {"from_attributes": True}


class MultipleScreenRow(BaseModel):
    company_id: int
    company_name: str
    ticker: str | None = None
    sector: str | None = None
    calc_date: datetime.date
    pe: Decimal | None = None
    ev_ebitda: Decimal | None = None
    ev_sales: Decimal | None = None
    pb: Decimal | None = None
    ps: Decimal | None = None
    roe: Decimal | None = None
    roa: Decimal | None = None
    debt_ebitda: Decimal | None = None
    market_cap: Decimal | None = None
