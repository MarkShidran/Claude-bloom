import datetime
import logging
from decimal import Decimal, InvalidOperation

from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import CollectionResult
from app.collectors.moex.client import MOEXClient
from app.models.quote import Quote
from app.models.security import Security

logger = logging.getLogger(__name__)


class MOEXQuoteCollector:
    """Collects historical quote data from MOEX ISS API."""

    def __init__(self, db: AsyncSession, client: MOEXClient | None = None):
        self.db = db
        self.client = client or MOEXClient()

    async def collect(
        self,
        security_ids: list[int] | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> CollectionResult:
        result = CollectionResult(source="moex_quotes")

        try:
            if security_ids:
                stmt = select(Security).where(
                    Security.id.in_(security_ids), Security.is_active.is_(True)
                )
            else:
                stmt = select(Security).where(
                    Security.exchange == "MOEX", Security.is_active.is_(True)
                )

            rows = await self.db.execute(stmt)
            securities = rows.scalars().all()

            for security in securities:
                try:
                    count = await self._collect_for_security(security, from_date, to_date)
                    result.records_created += count
                    result.records_processed += 1
                except Exception as e:
                    result.errors.append(f"{security.ticker}: {e}")
                    logger.exception(f"Failed to collect quotes for {security.ticker}")

        except Exception as e:
            result.errors.append(str(e))
            logger.exception("MOEX quote collection failed")

        return result

    async def _collect_for_security(
        self,
        security: Security,
        from_date: str | None,
        to_date: str | None,
    ) -> int:
        if not from_date:
            last_date = await self._get_last_quote_date(security.id)
            if last_date:
                from_date = (last_date + datetime.timedelta(days=1)).isoformat()

        secid = security.moex_secid or security.ticker
        board = security.moex_boardid

        raw_quotes = await self.client.get_quote_history(
            secid=secid,
            from_date=from_date,
            to_date=to_date,
            board=board,
        )

        if not raw_quotes:
            logger.info(f"No new quotes for {secid}")
            return 0

        count = 0
        for q in raw_quotes:
            trade_date = q.get("TRADEDATE")
            close = q.get("CLOSE") or q.get("LEGALCLOSEPRICE")
            if not trade_date or not close:
                continue

            try:
                stmt = pg_insert(Quote).values(
                    security_id=security.id,
                    trade_date=trade_date,
                    open=self._to_decimal(q.get("OPEN")),
                    high=self._to_decimal(q.get("HIGH")),
                    low=self._to_decimal(q.get("LOW")),
                    close=self._to_decimal(close),
                    volume=self._to_int(q.get("VOLUME")),
                    value=self._to_decimal(q.get("VALUE")),
                    num_trades=self._to_int(q.get("NUMTRADES")),
                ).on_conflict_do_update(
                    index_elements=["security_id", "trade_date"],
                    set_={
                        "open": self._to_decimal(q.get("OPEN")),
                        "high": self._to_decimal(q.get("HIGH")),
                        "low": self._to_decimal(q.get("LOW")),
                        "close": self._to_decimal(close),
                        "volume": self._to_int(q.get("VOLUME")),
                        "value": self._to_decimal(q.get("VALUE")),
                        "num_trades": self._to_int(q.get("NUMTRADES")),
                    },
                )
                await self.db.execute(stmt)
                count += 1
            except Exception as e:
                logger.warning(f"Skip quote {secid}/{trade_date}: {e}")

        await self.db.flush()
        logger.info(f"Collected {count} quotes for {secid}")
        return count

    async def _get_last_quote_date(self, security_id: int) -> datetime.date | None:
        stmt = select(func.max(Quote.trade_date)).where(Quote.security_id == security_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def _to_decimal(value) -> Decimal | None:
        if value is None or value == "":
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None

    @staticmethod
    def _to_int(value) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
