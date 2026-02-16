from datetime import datetime

from pydantic import BaseModel, Field


class CompanyBase(BaseModel):
    name: str = Field(..., max_length=500)
    name_en: str | None = None
    ticker: str | None = Field(None, max_length=20)
    inn: str | None = Field(None, max_length=12)
    ogrn: str | None = Field(None, max_length=15)
    sector: str | None = None
    industry: str | None = None
    country: str = Field("RUS", max_length=3)
    description: str | None = None
    website: str | None = None
    edisclosure_id: int | None = None
    moex_secid: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = None
    name_en: str | None = None
    ticker: str | None = None
    inn: str | None = None
    sector: str | None = None
    industry: str | None = None
    description: str | None = None
    website: str | None = None
    edisclosure_id: int | None = None
    moex_secid: str | None = None
    is_active: bool | None = None


class CompanyOut(BaseModel):
    id: int
    name: str
    name_en: str | None = None
    ticker: str | None = None
    inn: str | None = None
    sector: str | None = None
    industry: str | None = None
    country: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SecurityBrief(BaseModel):
    id: int
    ticker: str
    security_type: str
    currency: str
    exchange: str

    model_config = {"from_attributes": True}


class CompanyDetail(CompanyOut):
    ogrn: str | None = None
    description: str | None = None
    website: str | None = None
    edisclosure_id: int | None = None
    moex_secid: str | None = None
    sec_cik: str | None = None
    yahoo_ticker: str | None = None
    updated_at: datetime
    securities: list[SecurityBrief] = []

    model_config = {"from_attributes": True}
