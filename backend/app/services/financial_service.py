import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.financial_statement import FinancialStatement
from app.models.statement_item import StatementItem
from app.models.statement_item_dict import StatementItemDict
from app.schemas.financial import (
    FinancialStatementBrief,
    FinancialStatementOut,
    PeriodComparisonResponse,
    PeriodComparisonRow,
    StatementItemOut,
)


class FinancialService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_statements(
        self,
        company_id: int,
        standard: str | None = None,
        statement_type: str | None = None,
        period_type: str | None = None,
    ) -> list[FinancialStatementBrief]:
        stmt = (
            select(FinancialStatement)
            .where(FinancialStatement.company_id == company_id)
            .order_by(FinancialStatement.period_end.desc())
        )

        if standard:
            stmt = stmt.where(FinancialStatement.standard == standard)
        if statement_type:
            stmt = stmt.where(FinancialStatement.statement_type == statement_type)
        if period_type:
            stmt = stmt.where(FinancialStatement.period_type == period_type)

        result = await self.db.execute(stmt)
        statements = result.scalars().all()
        return [FinancialStatementBrief.model_validate(s) for s in statements]

    async def get_statement_with_items(
        self, statement_id: int
    ) -> FinancialStatementOut | None:
        stmt = (
            select(FinancialStatement)
            .where(FinancialStatement.id == statement_id)
            .options(
                selectinload(FinancialStatement.items).selectinload(
                    StatementItem.item_dict
                )
            )
        )

        result = await self.db.execute(stmt)
        statement = result.scalar_one_or_none()
        if statement is None:
            return None

        items_out = []
        for item in sorted(statement.items, key=lambda i: i.item_dict.sort_order):
            items_out.append(
                StatementItemOut(
                    id=item.id,
                    item_dict_id=item.item_dict_id,
                    code=item.item_dict.code,
                    name_ru=item.item_dict.name_ru,
                    name_en=item.item_dict.name_en,
                    value=item.value,
                    parent_code=item.item_dict.parent_code,
                    sort_order=item.item_dict.sort_order,
                )
            )

        return FinancialStatementOut(
            id=statement.id,
            company_id=statement.company_id,
            standard=statement.standard,
            statement_type=statement.statement_type,
            period_type=statement.period_type,
            period_start=statement.period_start,
            period_end=statement.period_end,
            currency=statement.currency,
            unit_multiplier=statement.unit_multiplier,
            source=statement.source,
            is_audited=statement.is_audited,
            items=items_out,
        )

    async def compare_periods(
        self,
        company_id: int,
        standard: str,
        statement_type: str,
        period_ends: list[datetime.date],
    ) -> PeriodComparisonResponse:
        # Fetch statements with items for each requested period
        period_data: dict[str, dict[str, tuple[Decimal | None, str, str | None, str | None, int]]] = {}

        for period_end in sorted(period_ends):
            stmt = (
                select(FinancialStatement)
                .where(
                    FinancialStatement.company_id == company_id,
                    FinancialStatement.standard == standard,
                    FinancialStatement.statement_type == statement_type,
                    FinancialStatement.period_end == period_end,
                )
                .options(
                    selectinload(FinancialStatement.items).selectinload(
                        StatementItem.item_dict
                    )
                )
            )
            result = await self.db.execute(stmt)
            statement = result.scalar_one_or_none()

            period_key = period_end.isoformat()
            period_data[period_key] = {}

            if statement:
                for item in statement.items:
                    d = item.item_dict
                    period_data[period_key][d.code] = (
                        item.value,
                        d.name_ru,
                        d.name_en,
                        d.parent_code,
                        d.sort_order,
                    )

        # Collect all unique item codes across periods
        all_codes: dict[str, tuple[str, str | None, str | None, int]] = {}
        for items in period_data.values():
            for code, (_, name_ru, name_en, parent_code, sort_order) in items.items():
                if code not in all_codes:
                    all_codes[code] = (name_ru, name_en, parent_code, sort_order)

        # Build comparison rows
        sorted_periods = sorted(period_data.keys())
        rows: list[PeriodComparisonRow] = []

        for code, (name_ru, name_en, parent_code, sort_order) in sorted(
            all_codes.items(), key=lambda x: x[1][3]
        ):
            values: dict[str, Decimal | None] = {}
            for period_key in sorted_periods:
                item_data = period_data[period_key].get(code)
                values[period_key] = item_data[0] if item_data else None

            # Calculate percentage changes between consecutive periods
            changes: dict[str, Decimal | None] = {}
            for i in range(1, len(sorted_periods)):
                prev_period = sorted_periods[i - 1]
                curr_period = sorted_periods[i]
                change_key = f"{prev_period}_to_{curr_period}"

                prev_val = values.get(prev_period)
                curr_val = values.get(curr_period)

                if prev_val is not None and curr_val is not None and prev_val != 0:
                    pct = ((curr_val - prev_val) / abs(prev_val)) * 100
                    changes[change_key] = Decimal(str(round(float(pct), 2)))
                else:
                    changes[change_key] = None

            rows.append(
                PeriodComparisonRow(
                    code=code,
                    name_ru=name_ru,
                    name_en=name_en,
                    parent_code=parent_code,
                    sort_order=sort_order,
                    values=values,
                    changes=changes,
                )
            )

        return PeriodComparisonResponse(
            company_id=company_id,
            standard=standard,
            statement_type=statement_type,
            periods=sorted_periods,
            rows=rows,
        )

    async def create_statement(
        self,
        company_id: int,
        data: dict,
        items: list[dict],
    ) -> FinancialStatement:
        statement = FinancialStatement(
            company_id=company_id,
            **data,
        )
        self.db.add(statement)
        await self.db.flush()

        if items:
            statement_items = [
                StatementItem(
                    statement_id=statement.id,
                    item_dict_id=item["item_dict_id"],
                    value=item.get("value"),
                    note=item.get("note"),
                )
                for item in items
            ]
            self.db.add_all(statement_items)
            await self.db.flush()

        await self.db.refresh(statement)
        return statement
