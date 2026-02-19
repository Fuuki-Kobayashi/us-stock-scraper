import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.data_sources.polygon_client import polygon_client
from app.models.collection_log import CollectionLog
from app.models.surge_event import SurgeEvent
from app.models.surge_tracking import SurgeTracking
from app.models.ticker import Ticker
from app.models.user_setting import UserSetting

logger = logging.getLogger(__name__)

TRACKING_DAYS = [1, 3, 7, 30]
MAX_PREV_DAY_LOOKBACK = 7


async def _get_threshold(session: AsyncSession) -> float:
    result = await session.execute(
        select(UserSetting).where(UserSetting.key == "surge_threshold_pct")
    )
    setting = result.scalar_one_or_none()
    if setting:
        return float(setting.value)
    from app.config import settings

    return settings.SURGE_THRESHOLD_PCT


async def _ensure_ticker(session: AsyncSession, symbol: str) -> None:
    result = await session.execute(select(Ticker).where(Ticker.symbol == symbol))
    if result.scalar_one_or_none() is None:
        session.add(Ticker(symbol=symbol))


async def _collect_surges_for_date(
    session: AsyncSession, target_date: date, threshold: float
) -> int:
    """Collect surge events for a specific date. Returns count of surges found."""
    results = await polygon_client.grouped_daily(target_date)
    if not results:
        logger.info("No results for %s", target_date)
        return 0

    # Find previous trading day via Polygon API (handles weekends + holidays)
    prev_close_map: dict[str, float] = {}
    prev_date = target_date - timedelta(days=1)
    for _ in range(MAX_PREV_DAY_LOOKBACK):
        while prev_date.weekday() >= 5:
            prev_date -= timedelta(days=1)
        prev_results = await polygon_client.grouped_daily(prev_date)
        if prev_results:
            for item in prev_results:
                symbol = item.get("T", "")
                close = item.get("c")
                if symbol and close:
                    prev_close_map[symbol] = float(close)
            logger.info("Previous trading day: %s (%d tickers)", prev_date, len(prev_close_map))
            break
        logger.info("No data for %s (holiday?), trying earlier date", prev_date)
        prev_date -= timedelta(days=1)
    else:
        logger.warning("No previous trading day found within %d days", MAX_PREV_DAY_LOOKBACK)

    surge_count = 0
    for item in results:
        symbol = item.get("T", "")
        close = item.get("c")
        if not symbol or close is None:
            continue

        prev_close = prev_close_map.get(symbol)
        if prev_close is None or prev_close <= 0:
            continue

        change_pct = (float(close) - prev_close) / prev_close * 100

        if change_pct >= threshold:
            # Check for duplicate
            existing = await session.execute(
                select(SurgeEvent).where(
                    SurgeEvent.symbol == symbol,
                    SurgeEvent.event_date == target_date,
                )
            )
            if existing.scalar_one_or_none():
                continue

            await _ensure_ticker(session, symbol)
            surge_event = SurgeEvent(
                symbol=symbol,
                event_date=target_date,
                open=float(item.get("o", 0)),
                high=float(item.get("h", 0)),
                low=float(item.get("l", 0)),
                close=float(close),
                volume=int(item.get("v", 0)),
                prev_close=prev_close,
                change_pct=round(change_pct, 2),
                vwap=float(item["vw"]) if item.get("vw") else None,
            )
            session.add(surge_event)
            surge_count += 1

    return surge_count


async def _update_tracking(session: AsyncSession, target_date: date) -> None:
    """Update post-surge tracking for past surge events."""
    for days in TRACKING_DAYS:
        check_date = target_date - timedelta(days=days)
        result = await session.execute(
            select(SurgeEvent).where(SurgeEvent.event_date == check_date)
        )
        surge_events = result.scalars().all()

        for event in surge_events:
            # Check if tracking already exists
            existing = await session.execute(
                select(SurgeTracking).where(
                    SurgeTracking.surge_event_id == event.id,
                    SurgeTracking.days_after == days,
                )
            )
            if existing.scalar_one_or_none():
                continue

            # Get current price from today's grouped daily
            bars = await polygon_client.aggregate_bars(
                event.symbol, target_date, target_date
            )
            if bars:
                current_close = float(bars[0].get("c", 0))
                change_from_surge = (
                    (current_close - event.close) / event.close * 100
                )
                tracking = SurgeTracking(
                    surge_event_id=event.id,
                    days_after=days,
                    close_price=current_close,
                    change_from_surge_pct=round(change_from_surge, 2),
                    tracked_date=target_date,
                )
                session.add(tracking)


async def run_daily_collection(target_date: date | None = None) -> int:
    """Run the daily collection job. Returns the collection log ID."""
    if target_date is None:
        target_date = datetime.now(timezone.utc).date()

    async with async_session() as session:
        log = CollectionLog(job_type="daily_collection", status="running")
        session.add(log)
        await session.flush()
        log_id = log.id

        try:
            threshold = await _get_threshold(session)
            surge_count = await _collect_surges_for_date(
                session, target_date, threshold
            )
            await _update_tracking(session, target_date)

            log.status = "completed"
            log.records_count = surge_count
            log.completed_at = datetime.utcnow()
            await session.commit()

            logger.info(
                "Daily collection completed for %s: %d surges found",
                target_date,
                surge_count,
            )
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)
            log.completed_at = datetime.utcnow()
            await session.commit()
            logger.error("Daily collection failed: %s", e)
            raise

    return log_id
