import datetime
from decimal import Decimal

import numpy as np
import pandas as pd
from sqlalchemy import select, func, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quote import Quote
from app.models.security import Security
from app.schemas.quote import QuoteOut, QuoteStats, QuoteTimeSeries


class QuoteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_quotes(
        self,
        security_id: int,
        from_date: datetime.date | None = None,
        to_date: datetime.date | None = None,
        interval: str = "day",
    ) -> QuoteTimeSeries:
        security = await self._get_security(security_id)

        if interval == "day":
            quotes = await self._get_daily_quotes(security_id, from_date, to_date)
        else:
            quotes = await self._get_aggregated_quotes(
                security_id, from_date, to_date, interval
            )

        return QuoteTimeSeries(
            security_id=security_id,
            ticker=security.ticker,
            currency=security.currency,
            quotes=quotes,
            total=len(quotes),
        )

    async def _get_daily_quotes(
        self,
        security_id: int,
        from_date: datetime.date | None,
        to_date: datetime.date | None,
    ) -> list[QuoteOut]:
        stmt = (
            select(Quote)
            .where(Quote.security_id == security_id)
            .order_by(Quote.trade_date)
        )

        if from_date:
            stmt = stmt.where(Quote.trade_date >= from_date)
        if to_date:
            stmt = stmt.where(Quote.trade_date <= to_date)

        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return [QuoteOut.model_validate(r) for r in rows]

    async def _get_aggregated_quotes(
        self,
        security_id: int,
        from_date: datetime.date | None,
        to_date: datetime.date | None,
        interval: str,
    ) -> list[QuoteOut]:
        trunc_unit = "week" if interval == "week" else "month"

        stmt = (
            select(
                func.date_trunc(trunc_unit, Quote.trade_date).label("period"),
                func.first_value(Quote.open).over(
                    partition_by=func.date_trunc(trunc_unit, Quote.trade_date),
                    order_by=Quote.trade_date,
                ).label("open"),
                func.max(Quote.high).label("high"),
                func.min(Quote.low).label("low"),
                func.first_value(Quote.close).over(
                    partition_by=func.date_trunc(trunc_unit, Quote.trade_date),
                    order_by=Quote.trade_date.desc(),
                ).label("close"),
                func.sum(Quote.volume).label("volume"),
                func.sum(Quote.value).label("value"),
            )
            .where(Quote.security_id == security_id)
        )

        if from_date:
            stmt = stmt.where(Quote.trade_date >= from_date)
        if to_date:
            stmt = stmt.where(Quote.trade_date <= to_date)

        # Use a subquery approach: aggregate per period using group by for min/max/sum,
        # and pick first/last open/close with a raw SQL CTE for clarity.
        agg_sql = text("""
            SELECT
                date_trunc(:trunc_unit, trade_date)::date AS trade_date,
                (array_agg(open ORDER BY trade_date ASC))[1] AS open,
                MAX(high) AS high,
                MIN(low) AS low,
                (array_agg(close ORDER BY trade_date DESC))[1] AS close,
                SUM(volume) AS volume,
                SUM(value) AS value
            FROM quotes
            WHERE security_id = :security_id
                AND (:from_date::date IS NULL OR trade_date >= :from_date)
                AND (:to_date::date IS NULL OR trade_date <= :to_date)
            GROUP BY date_trunc(:trunc_unit, trade_date)
            ORDER BY trade_date
        """)

        result = await self.db.execute(
            agg_sql,
            {
                "trunc_unit": trunc_unit,
                "security_id": security_id,
                "from_date": from_date,
                "to_date": to_date,
            },
        )
        rows = result.fetchall()
        return [
            QuoteOut(
                trade_date=row.trade_date,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
                volume=int(row.volume) if row.volume is not None else None,
                value=row.value,
            )
            for row in rows
        ]

    async def get_stats(self, security_id: int) -> QuoteStats:
        security = await self._get_security(security_id)
        today = datetime.date.today()
        one_year_ago = today - datetime.timedelta(days=365)

        # Fetch quotes for the last year
        stmt = (
            select(Quote)
            .where(
                Quote.security_id == security_id,
                Quote.trade_date >= one_year_ago,
            )
            .order_by(Quote.trade_date)
        )
        result = await self.db.execute(stmt)
        quotes = result.scalars().all()

        if not quotes:
            return QuoteStats(
                security_id=security_id,
                ticker=security.ticker,
            )

        df = pd.DataFrame(
            [
                {
                    "trade_date": q.trade_date,
                    "close": float(q.close),
                    "volume": q.volume or 0,
                }
                for q in quotes
            ]
        )
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df = df.sort_values("trade_date").reset_index(drop=True)

        last_row = df.iloc[-1]
        last_price = Decimal(str(last_row["close"]))
        last_date = last_row["trade_date"].date()

        high_52w = Decimal(str(df["close"].max()))
        low_52w = Decimal(str(df["close"].min()))

        # 30-day average volume
        last_30 = df[df["trade_date"] >= pd.Timestamp(today - datetime.timedelta(days=30))]
        avg_volume_30d = (
            Decimal(str(round(last_30["volume"].mean(), 2)))
            if not last_30.empty
            else None
        )

        # Returns calculation
        def calc_return(days: int) -> Decimal | None:
            cutoff = pd.Timestamp(today - datetime.timedelta(days=days))
            past = df[df["trade_date"] <= cutoff]
            if past.empty:
                return None
            base_price = past.iloc[-1]["close"]
            if base_price == 0:
                return None
            ret = (float(last_price) - base_price) / base_price * 100
            return Decimal(str(round(ret, 4)))

        return_1m = calc_return(30)
        return_3m = calc_return(90)
        return_1y = calc_return(365)

        # YTD return
        ytd_start = pd.Timestamp(datetime.date(today.year, 1, 1))
        ytd_data = df[df["trade_date"] <= ytd_start]
        if not ytd_data.empty:
            ytd_base = ytd_data.iloc[-1]["close"]
            return_ytd = (
                Decimal(str(round((float(last_price) - ytd_base) / ytd_base * 100, 4)))
                if ytd_base != 0
                else None
            )
        else:
            return_ytd = None

        # 1-year annualized volatility
        df["daily_return"] = df["close"].pct_change()
        daily_returns = df["daily_return"].dropna()
        if len(daily_returns) > 1:
            vol = float(np.std(daily_returns, ddof=1)) * np.sqrt(252) * 100
            volatility_1y = Decimal(str(round(vol, 4)))
        else:
            volatility_1y = None

        return QuoteStats(
            security_id=security_id,
            ticker=security.ticker,
            last_price=last_price,
            last_date=last_date,
            high_52w=high_52w,
            low_52w=low_52w,
            avg_volume_30d=avg_volume_30d,
            return_1m=return_1m,
            return_3m=return_3m,
            return_ytd=return_ytd,
            return_1y=return_1y,
            volatility_1y=volatility_1y,
        )

    async def bulk_upsert_quotes(
        self, security_id: int, quotes_data: list[dict]
    ) -> int:
        if not quotes_data:
            return 0

        values = []
        for q in quotes_data:
            q["security_id"] = security_id
            values.append(q)

        stmt = pg_insert(Quote).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["security_id", "trade_date"],
            set_={
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "close": stmt.excluded.close,
                "adj_close": stmt.excluded.adj_close,
                "volume": stmt.excluded.volume,
                "value": stmt.excluded.value,
                "num_trades": stmt.excluded.num_trades,
            },
        )

        await self.db.execute(stmt)
        await self.db.flush()
        return len(values)

    async def _get_security(self, security_id: int) -> Security:
        stmt = select(Security).where(Security.id == security_id)
        result = await self.db.execute(stmt)
        security = result.scalar_one_or_none()
        if security is None:
            from app.exceptions import NotFoundError

            raise NotFoundError(f"Security {security_id} not found")
        return security
