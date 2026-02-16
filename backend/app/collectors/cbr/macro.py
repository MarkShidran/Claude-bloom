import logging
from datetime import date
from decimal import Decimal

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import CollectionResult
from app.collectors.cbr.client import CBRClient
from app.models.macro_indicator import MacroIndicator

logger = logging.getLogger(__name__)


class CBRMacroCollector:
    """Collects macro indicators from CBR: key rate, inflation."""

    def __init__(self, db: AsyncSession, client: CBRClient | None = None):
        self.db = db
        self.client = client or CBRClient()

    async def collect_key_rate(
        self, from_date: date, to_date: date | None = None
    ) -> CollectionResult:
        """Collect CBR key rate history."""
        result = CollectionResult(source="cbr_key_rate")
        to_date = to_date or date.today()

        try:
            rates = await self.client.get_key_rate(from_date, to_date)

            for rate in rates:
                stmt = pg_insert(MacroIndicator).values(
                    indicator_type="key_rate",
                    indicator_code="CBR_KEY_RATE",
                    date=rate["date"],
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
            logger.info(f"Collected {len(rates)} key rate records")
        except Exception as e:
            result.errors.append(str(e))
            logger.exception("CBR key rate collection failed")

        return result
