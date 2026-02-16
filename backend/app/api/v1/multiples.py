import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.multiple import MultipleOut, MultipleScreenRow
from app.services.multiple_service import MultipleService

router = APIRouter(prefix="", tags=["Multiples"])


@router.get(
    "/companies/{company_id}/multiples", response_model=list[MultipleOut]
)
async def get_company_multiples(
    company_id: int,
    from_date: datetime.date | None = Query(None, description="Start date"),
    to_date: datetime.date | None = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db),
):
    service = MultipleService(db)
    return await service.get_multiples(
        company_id=company_id, from_date=from_date, to_date=to_date
    )


@router.get(
    "/multiples/screen", response_model=PaginatedResponse[MultipleScreenRow]
)
async def screen_multiples(
    sector: str | None = Query(None, description="Filter by sector"),
    sort_by: str = Query("pe", description="Sort field"),
    sort_dir: str = Query("asc", description="Sort direction: asc or desc"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    service = MultipleService(db)
    return await service.screen_multiples(
        sector=sector,
        sort_by=sort_by,
        sort_dir=sort_dir,
        offset=offset,
        limit=limit,
    )
