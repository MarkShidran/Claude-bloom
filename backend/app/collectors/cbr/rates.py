import logging
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import CollectionResult
from app.collectors.cbr.client import CBRClient
from app.models.macro_indicator import MacroIndicator

logger = logging.getLogger(__name__)

TARGET_CURRENCIES = ["USD", "EUR", "CNY", "GBP"]


class CBRRateCollector:
    """Collects FX rates from CBR XML API."""

    def __init__(self, db: AsyncSession, client: CBRClient | None = None):
        self.db = db
        self.client = client or CBRClient()

    async def collect_daily(self, req_date: date | None = None) -> CollectionResult:
        """Collect daily FX rates for a specific date."""
        result = CollectionResult(source="cbr_fx_daily")
        req_date = req_date or date.today()

        try:
            rates = await self.client.get_daily_rates(req_date)
            for rate in rates:
                char_code = rate["char_code"]
                if char_code not in TARGET_CURRENCIES:
                    continue

                indicator_code = f"{char_code}_RUB"
                stmt = pg_insert(MacroIndicator).values(
                    indicator_type="fx_rate",
                    indicator_code=indicator_code,
                    date=req_date,
                    value=Decimal(str(rate["value"])),
                    source="cbr",
                ).on_conflict_do_update(
                    index_elements=["indicator_code", "date"],
                    set_={"value": Decimal(str(rate["value"]))},
                )
                await self.db.execute(stmt)
                result.records_created += 1

            await self.db.flush()
            result.records_processed = len(rates)
        except Exception as e:
            result.errors.append(str(e))
            logger.exception("CBR daily rate collection failed")

        return result

    async def collect_history(
        self, from_date: date, to_date: date | None = None
    ) -> CollectionResult:
        """Collect historical FX rates for all target currencies."""
        result = CollectionResult(source="cbr_fx_history")
        to_date = to_date or date.today()

        for currency in TARGET_CURRENCIES:
            try:
                rates = await self.client.get_dynamic_rates(currency, from_date, to_date)
                indicator_code = f"{currency}_RUB"

                for rate in rates:
                    stmt = pg_insert(MacroIndicator).values(
                        indicator_type="fx_rate",
                        indicator_code=indicator_code,
                        date=rate["date"],
                        value=Decimal(str(rate["value"])),
                        source="cbr",
                    ).on_conflict_do_update(
                        index_elements=["indicator_code", "date"],
                        set_={"value": Decimal(str(rate["value"]))},
                    )
                    await self.db.execute(stmt)
                    result.records_created += 1

                result.records_processed += len(rates)
                logger.info(f"Collected {len(rates)} {currency}/RUB rates")
            except Exception as e:
                result.errors.append(f"{currency}: {e}")
                logger.exception(f"Failed to collect {currency} rates")

        await self.db.flush()
        return result
