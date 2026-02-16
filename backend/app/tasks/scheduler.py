import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def configure_scheduler():
    """Configure all scheduled jobs."""
    from app.tasks.jobs import (
        collect_cbr_fx_rates,
        collect_cbr_macro,
        collect_moex_quotes,
        recalculate_multiples,
    )

    scheduler.add_job(
        collect_moex_quotes,
        CronTrigger.from_crontab(settings.QUOTE_SYNC_CRON),
        id="moex_quotes",
        name="Collect MOEX daily quotes",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    scheduler.add_job(
        collect_cbr_fx_rates,
        CronTrigger.from_crontab(settings.FX_SYNC_CRON),
        id="cbr_fx",
        name="Collect CBR FX rates",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    scheduler.add_job(
        collect_cbr_macro,
        CronTrigger.from_crontab(settings.MACRO_SYNC_CRON),
        id="cbr_macro",
        name="Collect CBR macro indicators",
        replace_existing=True,
        misfire_grace_time=86400,
    )

    scheduler.add_job(
        recalculate_multiples,
        CronTrigger.from_crontab("30 19 * * 1-5"),
        id="recalculate_multiples",
        name="Recalculate financial multiples",
        replace_existing=True,
        misfire_grace_time=3600,
    )

    logger.info("Scheduler configured with %d jobs", len(scheduler.get_jobs()))
