import datetime
import logging
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.multiple import Multiple
from app.schemas.common import PaginatedResponse
from app.schemas.multiple import MultipleOut, MultipleScreenRow

logger = logging.getLogger(__name__)


class MultipleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_multiples(
        self,
        company_id: int,
        from_date: datetime.date | None = None,
        to_date: datetime.date | None = None,
    ) -> list[MultipleOut]:
        stmt = (
            select(Multiple)
            .where(Multiple.company_id == company_id)
            .order_by(Multiple.calc_date.desc())
        )

        if from_date:
            stmt = stmt.where(Multiple.calc_date >= from_date)
        if to_date:
            stmt = stmt.where(Multiple.calc_date <= to_date)

        result = await self.db.execute(stmt)
        multiples = result.scalars().all()
        return [MultipleOut.model_validate(m) for m in multiples]

    async def get_latest(self, company_id: int) -> MultipleOut | None:
        stmt = (
            select(Multiple)
            .where(Multiple.company_id == company_id)
            .order_by(Multiple.calc_date.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        m = result.scalar_one_or_none()
        if m is None:
            return None
        return MultipleOut.model_validate(m)

    async def screen_multiples(
        self,
        sector: str | None = None,
        sort_by: str = "pe",
        sort_dir: str = "asc",
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResponse[MultipleScreenRow]:
        latest_sub = (
            select(
                Multiple.company_id,
                func.max(Multiple.calc_date).label("max_calc_date"),
            )
            .group_by(Multiple.company_id)
            .subquery()
        )

        stmt = (
            select(
                Multiple,
                Company.name.label("company_name"),
                Company.ticker.label("company_ticker"),
                Company.sector.label("company_sector"),
            )
            .join(
                latest_sub,
                (Multiple.company_id == latest_sub.c.company_id)
                & (Multiple.calc_date == latest_sub.c.max_calc_date),
            )
            .join(Company, Multiple.company_id == Company.id)
            .where(Company.is_active.is_(True))
        )

        count_stmt = (
            select(func.count())
            .select_from(Multiple)
            .join(
                latest_sub,
                (Multiple.company_id == latest_sub.c.company_id)
                & (Multiple.calc_date == latest_sub.c.max_calc_date),
            )
            .join(Company, Multiple.company_id == Company.id)
            .where(Company.is_active.is_(True))
        )

        if sector:
            stmt = stmt.where(Company.sector == sector)
            count_stmt = count_stmt.where(Company.sector == sector)

        sort_column_map = {
            "pe": Multiple.pe,
            "ev_ebitda": Multiple.ev_ebitda,
            "ev_sales": Multiple.ev_sales,
            "pb": Multiple.pb,
            "ps": Multiple.ps,
            "roe": Multiple.roe,
            "roa": Multiple.roa,
            "debt_ebitda": Multiple.debt_ebitda,
            "market_cap": Multiple.market_cap,
        }
        sort_col = sort_column_map.get(sort_by, Multiple.pe)
        if sort_dir == "desc":
            stmt = stmt.order_by(sort_col.desc().nulls_last())
        else:
            stmt = stmt.order_by(sort_col.asc().nulls_last())

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        rows = result.all()

        items = [
            MultipleScreenRow(
                company_id=row.Multiple.company_id,
                company_name=row.company_name,
                ticker=row.company_ticker,
                sector=row.company_sector,
                calc_date=row.Multiple.calc_date,
                pe=row.Multiple.pe,
                ev_ebitda=row.Multiple.ev_ebitda,
                ev_sales=row.Multiple.ev_sales,
                pb=row.Multiple.pb,
                ps=row.Multiple.ps,
                roe=row.Multiple.roe,
                roa=row.Multiple.roa,
                debt_ebitda=row.Multiple.debt_ebitda,
                market_cap=row.Multiple.market_cap,
            )
            for row in rows
        ]

        return PaginatedResponse[MultipleScreenRow](
            items=items,
            total=total,
            offset=offset,
            limit=limit,
        )

    async def recalculate_all(self) -> int:
        """Recalculate multiples for all active companies with financial and market data."""
        from app.models.financial_statement import FinancialStatement
        from app.models.quote import Quote
        from app.models.security import Security
        from app.models.statement_item import StatementItem
        from app.models.statement_item_dict import StatementItemDict
        from app.services.calculation.multiples import MultiplesCalculator

        calculator = MultiplesCalculator()
        today = datetime.date.today()
        count = 0

        companies_stmt = select(Company).where(Company.is_active.is_(True))
        result = await self.db.execute(companies_stmt)
        companies = result.scalars().all()

        for company in companies:
            try:
                # Latest annual income statement
                fs_stmt = (
                    select(FinancialStatement)
                    .where(
                        FinancialStatement.company_id == company.id,
                        FinancialStatement.statement_type == "income_statement",
                        FinancialStatement.period_type == "annual",
                    )
                    .order_by(FinancialStatement.period_end.desc())
                    .limit(1)
                )
                fs_result = await self.db.execute(fs_stmt)
                fs = fs_result.scalar_one_or_none()
                if not fs:
                    continue

                # Collect financial item values
                items_stmt = (
                    select(StatementItem.value, StatementItemDict.code)
                    .join(StatementItemDict, StatementItem.item_dict_id == StatementItemDict.id)
                    .where(StatementItem.statement_id == fs.id)
                )
                items_result = await self.db.execute(items_stmt)
                financials = {row.code: row.value for row in items_result if row.value is not None}

                if not financials:
                    continue

                # Merge balance sheet items from same period
                bs_stmt = (
                    select(FinancialStatement)
                    .where(
                        FinancialStatement.company_id == company.id,
                        FinancialStatement.statement_type == "balance_sheet",
                        FinancialStatement.period_end == fs.period_end,
                    )
                    .limit(1)
                )
                bs_result = await self.db.execute(bs_stmt)
                bs = bs_result.scalar_one_or_none()
                if bs:
                    bs_items_stmt = (
                        select(StatementItem.value, StatementItemDict.code)
                        .join(StatementItemDict, StatementItem.item_dict_id == StatementItemDict.id)
                        .where(StatementItem.statement_id == bs.id)
                    )
                    bs_items_result = await self.db.execute(bs_items_stmt)
                    for row in bs_items_result:
                        if row.value is not None:
                            financials[row.code] = row.value

                # Latest security and quote
                sec_stmt = (
                    select(Security)
                    .where(Security.company_id == company.id, Security.is_active.is_(True))
                    .limit(1)
                )
                sec_result = await self.db.execute(sec_stmt)
                security = sec_result.scalar_one_or_none()
                if not security:
                    continue

                quote_stmt = (
                    select(Quote)
                    .where(Quote.security_id == security.id)
                    .order_by(Quote.trade_date.desc())
                    .limit(1)
                )
                quote_result = await self.db.execute(quote_stmt)
                latest_quote = quote_result.scalar_one_or_none()
                if not latest_quote:
                    continue

                share_price = latest_quote.close
                lot_size = Decimal(str(security.lot_size or 1))
                market_cap = share_price * lot_size

                mult_values = calculator.calculate_all(
                    financials=financials,
                    market_cap=market_cap,
                    share_price=share_price,
                    shares_outstanding=int(lot_size),
                )

                await self.save_multiples(
                    company_id=company.id,
                    calc_date=today,
                    period_end=fs.period_end,
                    values=mult_values,
                )
                count += 1
            except Exception:
                logger.exception("Failed to recalculate multiples for company %d", company.id)

        return count

    async def save_multiples(
        self,
        company_id: int,
        calc_date: datetime.date,
        period_end: datetime.date,
        values: dict,
    ) -> Multiple:
        multiple = Multiple(
            company_id=company_id,
            calc_date=calc_date,
            period_end=period_end,
            **values,
        )
        self.db.add(multiple)
        await self.db.flush()
        await self.db.refresh(multiple)
        return multiple
