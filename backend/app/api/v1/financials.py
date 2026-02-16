import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.schemas.financial import (
    FinancialStatementBrief,
    FinancialStatementOut,
    PeriodComparisonResponse,
)
from app.services.financial_service import FinancialService

router = APIRouter(prefix="", tags=["Financials"])


@router.get(
    "/companies/{company_id}/financials",
    response_model=list[FinancialStatementBrief],
)
async def list_financials(
    company_id: int,
    standard: str | None = Query(None, description="Accounting standard: RSBU, IFRS"),
    statement_type: str | None = Query(
        None, description="Statement type: balance_sheet, income_statement, cash_flow"
    ),
    period_type: str | None = Query(
        None, description="Period type: annual, semi_annual, quarterly"
    ),
    db: AsyncSession = Depends(get_db),
):
    service = FinancialService(db)
    return await service.get_statements(
        company_id=company_id,
        standard=standard,
        statement_type=statement_type,
        period_type=period_type,
    )


@router.get("/financials/{statement_id}/items", response_model=FinancialStatementOut)
async def get_statement_with_items(
    statement_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = FinancialService(db)
    statement = await service.get_statement_with_items(statement_id)
    if statement is None:
        raise HTTPException(status_code=404, detail="Financial statement not found")
    return statement


@router.get("/financials/compare", response_model=PeriodComparisonResponse)
async def compare_periods(
    company_id: int = Query(..., description="Company ID"),
    standard: str = Query(..., description="Accounting standard"),
    statement_type: str = Query(..., description="Statement type"),
    period_ends: str = Query(
        ..., description="Comma-separated period end dates (YYYY-MM-DD)"
    ),
    db: AsyncSession = Depends(get_db),
):
    parsed_dates: list[datetime.date] = []
    for date_str in period_ends.split(","):
        date_str = date_str.strip()
        try:
            parsed_dates.append(datetime.date.fromisoformat(date_str))
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid date format: {date_str}. Expected YYYY-MM-DD.",
            )

    if len(parsed_dates) < 2:
        raise HTTPException(
            status_code=422,
            detail="At least two period end dates are required for comparison.",
        )

    service = FinancialService(db)
    return await service.compare_periods(
        company_id=company_id,
        standard=standard,
        statement_type=statement_type,
        period_ends=parsed_dates,
    )


@router.post("/companies/{company_id}/financials/upload")
async def upload_financials(
    company_id: int,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
):
    if not file.filename or not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=422,
            detail="Only Excel files (.xlsx, .xls) are accepted.",
        )

    content = await file.read()
    max_size = 10 * 1024 * 1024  # 10 MB
    if len(content) > max_size:
        raise HTTPException(
            status_code=422,
            detail="File size exceeds the 10 MB limit.",
        )

    # Placeholder: parse and process the uploaded Excel file.
    # Full implementation would read sheets, map codes to item_dict IDs,
    # and call FinancialService.create_statement for each sheet.
    return {
        "status": "accepted",
        "company_id": company_id,
        "filename": file.filename,
        "size_bytes": len(content),
        "message": "File received. Processing will create financial statements.",
    }
