from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.security import SecurityCreate, SecurityOut
from app.services.security_service import SecurityService

router = APIRouter(prefix="/securities", tags=["Securities"])


@router.get("/{security_id}", response_model=SecurityOut)
async def get_security(
    security_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = SecurityService(db)
    security = await service.get_security(security_id)
    if security is None:
        raise HTTPException(status_code=404, detail="Security not found")
    return SecurityOut.model_validate(security)


@router.get("/company/{company_id}", response_model=list[SecurityOut])
async def list_securities_by_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = SecurityService(db)
    securities = await service.list_by_company(company_id)
    return [SecurityOut.model_validate(s) for s in securities]


@router.post("/", response_model=SecurityOut, status_code=201)
async def create_security(
    data: SecurityCreate,
    db: AsyncSession = Depends(get_db),
):
    service = SecurityService(db)
    security = await service.create_security(data)
    return SecurityOut.model_validate(security)
