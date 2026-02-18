import logging
from datetime import date, datetime, timedelta

from app.database import async_session
from app.models.collection_log import CollectionLog
from app.tasks.daily_collection import _collect_surges_for_date, _get_threshold

logger = logging.getLogger(__name__)


async def run_backfill(from_date: date, to_date: date) -> int:
    """Backfill surge data for a date range. Returns collection log ID."""
    async with async_session() as session:
        log = CollectionLog(job_type="backfill", status="running")
        session.add(log)
        await session.flush()
        log_id = log.id

        try:
            threshold = await _get_threshold(session)
            total_surges = 0
            current_date = from_date

            while current_date <= to_date:
                # Skip weekends
                if current_date.weekday() < 5:
                    count = await _collect_surges_for_date(
                        session, current_date, threshold
                    )
                    total_surges += count
                    logger.info(
                        "Backfill %s: %d surges", current_date, count
                    )
                current_date += timedelta(days=1)

            log.status = "completed"
            log.records_count = total_surges
            log.completed_at = datetime.utcnow()
            await session.commit()

            logger.info(
                "Backfill completed (%s to %s): %d total surges",
                from_date,
                to_date,
                total_surges,
            )
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
            await session.commit()
            logger.error("Backfill failed: %s", e)
            raise

    return log_id
