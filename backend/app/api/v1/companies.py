from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.company import CompanyCreate, CompanyDetail, CompanyOut, CompanyUpdate
from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("/", response_model=PaginatedResponse[CompanyOut])
async def list_companies(
    search: str | None = Query(None, description="Search by name or ticker"),
    sector: str | None = Query(None, description="Filter by sector"),
    country: str | None = Query(None, description="Filter by country code"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    return await service.list_companies(
        search=search, sector=sector, country=country, offset=offset, limit=limit
    )


@router.get("/search", response_model=list[CompanyOut])
async def search_companies(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    return await service.search_companies(query=q, limit=limit)


@router.get("/{company_id}", response_model=CompanyDetail)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    company = await service.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/", response_model=CompanyOut, status_code=201)
async def create_company(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    company = await service.create_company(data)
    return CompanyOut.model_validate(company)


@router.put("/{company_id}", response_model=CompanyOut)
async def update_company(
    company_id: int,
    data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    company = await service.update_company(company_id, data)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyOut.model_validate(company)
