import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.export_service import ExportService

router = APIRouter(prefix="/export", tags=["Export"])

EXCEL_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


class FinancialsExportRequest(BaseModel):
    company_id: int
    statement_ids: list[int]


class MultiplesExportRequest(BaseModel):
    company_id: int


class QuotesExportRequest(BaseModel):
    security_id: int
    from_date: datetime.date | None = None
    to_date: datetime.date | None = None


@router.post("/financials")
async def export_financials(
    body: FinancialsExportRequest,
    db: AsyncSession = Depends(get_db),
):
    service = ExportService(db)
    output = await service.export_financials(
        company_id=body.company_id, statement_ids=body.statement_ids
    )
    return StreamingResponse(
        output,
        media_type=EXCEL_MEDIA_TYPE,
        headers={
            "Content-Disposition": (
                f"attachment; filename=financials_{body.company_id}.xlsx"
            )
        },
    )


@router.post("/multiples")
async def export_multiples(
    body: MultiplesExportRequest,
    db: AsyncSession = Depends(get_db),
):
    service = ExportService(db)
    output = await service.export_multiples(company_id=body.company_id)
    return StreamingResponse(
        output,
        media_type=EXCEL_MEDIA_TYPE,
        headers={
            "Content-Disposition": (
                f"attachment; filename=multiples_{body.company_id}.xlsx"
            )
        },
    )


@router.post("/quotes")
async def export_quotes(
    body: QuotesExportRequest,
    db: AsyncSession = Depends(get_db),
):
    service = ExportService(db)
    output = await service.export_quotes(
        security_id=body.security_id,
        from_date=body.from_date,
        to_date=body.to_date,
    )
    return StreamingResponse(
        output,
        media_type=EXCEL_MEDIA_TYPE,
        headers={
            "Content-Disposition": (
                f"attachment; filename=quotes_{body.security_id}.xlsx"
            )
        },
    )


@router.get("/template/financials")
async def download_financials_template(
    db: AsyncSession = Depends(get_db),
):
    service = ExportService(db)
    output = await service.generate_upload_template()
    return StreamingResponse(
        output,
        media_type=EXCEL_MEDIA_TYPE,
        headers={
            "Content-Disposition": "attachment; filename=financials_template.xlsx"
        },
    )
