import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.data_sources.polygon_client import polygon_client
from app.models.collection_log import CollectionLog
from app.models.ticker import Ticker

logger = logging.getLogger(__name__)


async def _sync_page(session: AsyncSession, cursor: str | None = None) -> tuple[int, str | None]:
    """Sync one page of tickers. Returns (count, next_cursor)."""
    data = await polygon_client.tickers_list(cursor)
    results = data.get("results", [])
    next_cursor = data.get("next_cursor")
    count = 0

    for item in results:
        symbol = item.get("ticker", "")
        if not symbol:
            continue

        result = await session.execute(
            select(Ticker).where(Ticker.symbol == symbol)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.name = item.get("name")
            existing.market = item.get("market")
            existing.exchange = item.get("primary_exchange")
            existing.type = item.get("type")
            existing.currency = item.get("currency_name")
            existing.active = item.get("active", True)
            existing.updated_at = datetime.utcnow()
        else:
            ticker = Ticker(
                symbol=symbol,
                name=item.get("name"),
                market=item.get("market"),
                exchange=item.get("primary_exchange"),
                type=item.get("type"),
                currency=item.get("currency_name"),
                active=item.get("active", True),
            )
            session.add(ticker)
        count += 1

    return count, next_cursor


async def run_ticker_sync() -> int:
    """Run ticker sync job. Returns the collection log ID."""
    async with async_session() as session:
        log = CollectionLog(job_type="ticker_sync", status="running")
        session.add(log)
        await session.flush()
        log_id = log.id

        try:
            total_count = 0
            cursor: str | None = None
            pages_fetched = 0
            max_pages = 10  # Safety limit for free tier

            while pages_fetched < max_pages:
                count, next_cursor = await _sync_page(session, cursor)
                total_count += count
                pages_fetched += 1
                if not next_cursor or count == 0:
                    break
                cursor = next_cursor

            log.status = "completed"
            log.records_count = total_count
            log.completed_at = datetime.utcnow()
            await session.commit()

            logger.info("Ticker sync completed: %d tickers synced", total_count)
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
            await session.commit()
            logger.error("Ticker sync failed: %s", e)
            raise

    return log_id
