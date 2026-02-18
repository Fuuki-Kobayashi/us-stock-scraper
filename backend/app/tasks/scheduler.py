import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduler() -> None:
    """Register scheduled jobs."""
    from app.tasks.daily_collection import run_daily_collection
    from app.tasks.ticker_sync import run_ticker_sync

    # Daily collection at 22:00 UTC (after US market close)
    scheduler.add_job(
        run_daily_collection,
        "cron",
        hour=22,
        minute=0,
        id="daily_collection",
        replace_existing=True,
    )

    # Weekly ticker sync on Sunday at 00:00 UTC
    scheduler.add_job(
        run_ticker_sync,
        "cron",
        day_of_week="sun",
        hour=0,
        minute=0,
        id="ticker_sync",
        replace_existing=True,
    )

    logger.info("Scheduler jobs registered")
