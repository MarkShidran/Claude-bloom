import datetime
from decimal import Decimal

from pydantic import BaseModel


class MacroDataPoint(BaseModel):
    date: datetime.date
    value: Decimal
    indicator_code: str
    indicator_type: str
    source: str | None = None

    model_config = {"from_attributes": True}


class MacroTimeSeries(BaseModel):
    indicator_code: str
    indicator_type: str
    data: list[MacroDataPoint]
    total: int
