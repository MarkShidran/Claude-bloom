import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.macro import MacroTimeSeries
from app.services.macro_service import MacroService

router = APIRouter(prefix="/macro", tags=["Macro Data"])


@router.get("/fx", response_model=dict[str, MacroTimeSeries])
async def get_fx_rates(
    from_date: datetime.date | None = Query(None, description="Start date"),
    to_date: datetime.date | None = Query(None, description="End date"),
    currencies: str = Query(
        "USD_RUB,EUR_RUB",
        description="Comma-separated currency pairs",
    ),
    db: AsyncSession = Depends(get_db),
):
    currency_list = [c.strip() for c in currencies.split(",") if c.strip()]
    service = MacroService(db)
    return await service.get_fx_rates(
        from_date=from_date, to_date=to_date, currencies=currency_list
    )


@router.get("/rates", response_model=MacroTimeSeries)
async def get_key_rates(
    from_date: datetime.date | None = Query(None, description="Start date"),
    to_date: datetime.date | None = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db),
):
    service = MacroService(db)
    return await service.get_rates(
        indicator_code="CBR_KEY_RATE", from_date=from_date, to_date=to_date
    )


@router.get("/latest")
async def get_latest_macro(
    db: AsyncSession = Depends(get_db),
):
    service = MacroService(db)

    usd = await service.get_latest_rate("USD_RUB")
    eur = await service.get_latest_rate("EUR_RUB")
    key_rate = await service.get_latest_rate("CBR_KEY_RATE")

    return {
        "fx": {
            "USD_RUB": usd.model_dump() if usd else None,
            "EUR_RUB": eur.model_dump() if eur else None,
        },
        "key_rate": key_rate.model_dump() if key_rate else None,
    }
