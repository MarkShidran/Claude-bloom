from datetime import datetime

from pydantic import BaseModel, Field


class SecurityBase(BaseModel):
    ticker: str = Field(..., max_length=20)
    isin: str | None = Field(None, max_length=12)
    security_type: str = Field(..., max_length=20)
    currency: str = Field("RUB", max_length=3)
    exchange: str = Field("MOEX", max_length=20)
    moex_secid: str | None = None
    moex_boardid: str | None = None
    lot_size: int = 1


class SecurityCreate(SecurityBase):
    company_id: int


class SecurityOut(SecurityBase):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
