import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.quote import QuoteStats, QuoteTimeSeries
from app.services.quote_service import QuoteService

router = APIRouter(prefix="/securities", tags=["Quotes"])


@router.get("/{security_id}/quotes", response_model=QuoteTimeSeries)
async def get_quotes(
    security_id: int,
    from_date: datetime.date | None = Query(None, description="Start date"),
    to_date: datetime.date | None = Query(None, description="End date"),
    interval: str = Query("day", description="Aggregation interval: day, week, month"),
    db: AsyncSession = Depends(get_db),
):
    service = QuoteService(db)
    return await service.get_quotes(
        security_id=security_id,
        from_date=from_date,
        to_date=to_date,
        interval=interval,
    )


@router.get("/{security_id}/quotes/stats", response_model=QuoteStats)
async def get_quote_stats(
    security_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = QuoteService(db)
    return await service.get_stats(security_id)
