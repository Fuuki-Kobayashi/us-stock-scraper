import logging
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.data_sources.polygon_client import polygon_client
from app.models.collection_log import CollectionLog
from app.models.daily_price import DailyPrice

logger = logging.getLogger(__name__)

BATCH_COMMIT_SIZE = 10  # Commit every N trading days


async def _save_daily_prices(
    session: AsyncSession, target_date: date, results: list[dict]
) -> int:
    """Save grouped_daily results to daily_prices table. Returns count saved."""
    saved = 0
    for item in results:
        symbol = item.get("T", "")
        close = item.get("c")
        if not symbol or close is None:
            continue

        session.add(
            DailyPrice(
                symbol=symbol,
                trade_date=target_date,
                open=float(item.get("o", 0)),
                high=float(item.get("h", 0)),
                low=float(item.get("l", 0)),
                close=float(close),
                volume=int(item.get("v", 0)),
                vwap=float(item["vw"]) if item.get("vw") else None,
                transactions=int(item["n"]) if item.get("n") else None,
            )
        )
        saved += 1
    return saved


async def _get_last_downloaded_date(session: AsyncSession) -> date | None:
    """Get the most recent date already in daily_prices."""
    result = await session.execute(
        select(func.max(DailyPrice.trade_date))
    )
    return result.scalar_one_or_none()


async def run_bulk_download(from_date: date, to_date: date) -> int:
    """Download all daily OHLCV data for a date range using grouped_daily API.

    Returns the collection log ID.
    """
    async with async_session() as session:
        log = CollectionLog(job_type="bulk_download", status="running")
        session.add(log)
        await session.flush()
        log_id = log.id

        try:
            # Check which dates already have data to allow resume
            result = await session.execute(
                select(DailyPrice.trade_date)
                .where(
                    DailyPrice.trade_date >= from_date,
                    DailyPrice.trade_date <= to_date,
                )
                .distinct()
            )
            existing_dates = {row[0] for row in result.all()}

            total_records = 0
            days_processed = 0
            current_date = from_date

            while current_date <= to_date:
                # Skip weekends
                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    continue

                # Skip dates already downloaded
                if current_date in existing_dates:
                    logger.info(
                        "Skipping %s (already downloaded)", current_date
                    )
                    current_date += timedelta(days=1)
                    continue

                results = await polygon_client.grouped_daily(current_date)
                if results:
                    count = await _save_daily_prices(
                        session, current_date, results
                    )
                    total_records += count
                    days_processed += 1
                    logger.info(
                        "Bulk download %s: %d records (total: %d)",
                        current_date,
                        count,
                        total_records,
                    )

                    # Periodic commit to avoid huge transactions
                    if days_processed % BATCH_COMMIT_SIZE == 0:
                        await session.commit()
                        logger.info(
                            "Committed batch (%d days, %d records so far)",
                            days_processed,
                            total_records,
                        )
                else:
                    logger.info(
                        "No data for %s (holiday?)", current_date
                    )

                current_date += timedelta(days=1)

            log.status = "completed"
            log.records_count = total_records
            log.completed_at = datetime.utcnow()
            await session.commit()

            logger.info(
                "Bulk download completed (%s to %s): %d days, %d total records",
                from_date,
                to_date,
                days_processed,
                total_records,
            )
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)[:500]
            log.completed_at = datetime.utcnow()
            await session.commit()
            logger.error("Bulk download failed: %s", e)
            raise

    return log_id
