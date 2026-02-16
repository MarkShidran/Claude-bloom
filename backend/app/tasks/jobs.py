import logging
from datetime import date, timedelta

import httpx

from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def collect_moex_quotes():
    """Scheduled job: collect daily quotes from MOEX."""
    from app.collectors.moex.quotes import MOEXQuoteCollector

    logger.info("Starting MOEX quote collection")
    async with AsyncSessionLocal() as db:
        try:
            async with httpx.AsyncClient(timeout=60.0) as http:
                from app.collectors.moex.client import MOEXClient

                client = MOEXClient(http)
                collector = MOEXQuoteCollector(db, client)
                result = await collector.collect()
                await db.commit()

            logger.info(
                "MOEX quotes: processed=%d, created=%d, errors=%d",
                result.records_processed,
                result.records_created,
                len(result.errors),
            )
            if result.errors:
                logger.warning("MOEX quote errors: %s", result.errors[:5])
        except Exception:
            await db.rollback()
            logger.exception("MOEX quote collection job failed")


async def collect_cbr_fx_rates():
    """Scheduled job: collect daily FX rates from CBR."""
    from app.collectors.cbr.rates import CBRRateCollector

    logger.info("Starting CBR FX rate collection")
    async with AsyncSessionLocal() as db:
        try:
            async with httpx.AsyncClient(timeout=30.0) as http:
                from app.collectors.cbr.client import CBRClient

                client = CBRClient(http)
                collector = CBRRateCollector(db, client)
                result = await collector.collect_daily()
                await db.commit()

            logger.info(
                "CBR FX rates: processed=%d, created=%d",
                result.records_processed,
                result.records_created,
            )
        except Exception:
            await db.rollback()
            logger.exception("CBR FX rate collection job failed")


async def collect_cbr_macro():
    """Scheduled job: collect macro indicators from CBR."""
    from app.collectors.cbr.macro import CBRMacroCollector

    logger.info("Starting CBR macro collection")
    async with AsyncSessionLocal() as db:
        try:
            async with httpx.AsyncClient(timeout=30.0) as http:
                from app.collectors.cbr.client import CBRClient

                client = CBRClient(http)
                collector = CBRMacroCollector(db, client)
                from_date = date.today() - timedelta(days=90)
                result = await collector.collect_key_rate(from_date)
                await db.commit()

            logger.info(
                "CBR macro: processed=%d, created=%d",
                result.records_processed,
                result.records_created,
            )
        except Exception:
            await db.rollback()
            logger.exception("CBR macro collection job failed")


async def recalculate_multiples():
    """Scheduled job: recalculate financial multiples for all companies."""
    from app.services.multiple_service import MultipleService

    logger.info("Starting multiples recalculation")
    async with AsyncSessionLocal() as db:
        try:
            service = MultipleService(db)
            count = await service.recalculate_all()
            await db.commit()
            logger.info("Multiples recalculated for %d companies", count)
        except Exception:
            await db.rollback()
            logger.exception("Multiples recalculation job failed")
