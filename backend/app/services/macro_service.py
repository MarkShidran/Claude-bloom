import datetime

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.macro_indicator import MacroIndicator
from app.schemas.macro import MacroDataPoint, MacroTimeSeries


class MacroService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_rates(
        self,
        indicator_code: str,
        from_date: datetime.date | None = None,
        to_date: datetime.date | None = None,
    ) -> MacroTimeSeries:
        stmt = (
            select(MacroIndicator)
            .where(MacroIndicator.indicator_code == indicator_code)
            .order_by(MacroIndicator.date)
        )

        if from_date:
            stmt = stmt.where(MacroIndicator.date >= from_date)
        if to_date:
            stmt = stmt.where(MacroIndicator.date <= to_date)

        result = await self.db.execute(stmt)
        rows = result.scalars().all()

        data = [MacroDataPoint.model_validate(r) for r in rows]
        indicator_type = rows[0].indicator_type if rows else "unknown"

        return MacroTimeSeries(
            indicator_code=indicator_code,
            indicator_type=indicator_type,
            data=data,
            total=len(data),
        )

    async def get_latest_rate(
        self, indicator_code: str
    ) -> MacroDataPoint | None:
        stmt = (
            select(MacroIndicator)
            .where(MacroIndicator.indicator_code == indicator_code)
            .order_by(MacroIndicator.date.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return MacroDataPoint.model_validate(row)

    async def get_fx_rates(
        self,
        from_date: datetime.date | None = None,
        to_date: datetime.date | None = None,
        currencies: list[str] | None = None,
    ) -> dict[str, MacroTimeSeries]:
        if currencies is None:
            currencies = ["USD_RUB", "EUR_RUB"]

        result: dict[str, MacroTimeSeries] = {}
        for currency in currencies:
            result[currency] = await self.get_rates(currency, from_date, to_date)

        return result

    async def bulk_upsert(
        self,
        indicator_code: str,
        indicator_type: str,
        data: list[dict],
    ) -> int:
        if not data:
            return 0

        values = []
        for item in data:
            values.append(
                {
                    "indicator_code": indicator_code,
                    "indicator_type": indicator_type,
                    "date": item["date"],
                    "value": item["value"],
                    "source": item.get("source"),
                }
            )

        stmt = pg_insert(MacroIndicator).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["indicator_code", "date"],
            set_={
                "value": stmt.excluded.value,
                "source": stmt.excluded.source,
            },
        )

        await self.db.execute(stmt)
        await self.db.flush()
        return len(values)
