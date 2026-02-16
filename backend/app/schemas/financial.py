import datetime
from decimal import Decimal

from pydantic import BaseModel


class StatementItemDictOut(BaseModel):
    id: int
    code: str
    name_ru: str
    name_en: str | None = None
    statement_type: str
    parent_code: str | None = None
    sort_order: int

    model_config = {"from_attributes": True}


class StatementItemOut(BaseModel):
    id: int
    item_dict_id: int
    code: str
    name_ru: str
    name_en: str | None = None
    value: Decimal | None = None
    parent_code: str | None = None
    sort_order: int

    model_config = {"from_attributes": True}


class FinancialStatementOut(BaseModel):
    id: int
    company_id: int
    standard: str
    statement_type: str
    period_type: str
    period_start: datetime.date
    period_end: datetime.date
    currency: str
    unit_multiplier: int
    source: str | None = None
    is_audited: bool
    items: list[StatementItemOut] = []

    model_config = {"from_attributes": True}


class FinancialStatementBrief(BaseModel):
    id: int
    standard: str
    statement_type: str
    period_type: str
    period_end: datetime.date
    currency: str

    model_config = {"from_attributes": True}


class PeriodComparisonRow(BaseModel):
    code: str
    name_ru: str
    name_en: str | None = None
    parent_code: str | None = None
    sort_order: int
    values: dict[str, Decimal | None]  # period_end_str -> value
    changes: dict[str, Decimal | None]  # period pair -> pct change


class PeriodComparisonResponse(BaseModel):
    company_id: int
    standard: str
    statement_type: str
    periods: list[str]
    rows: list[PeriodComparisonRow]
