import asyncio
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.collection_log import CollectionLog
from app.models.surge_event import SurgeEvent
from app.models.ticker import Ticker
from app.schemas.admin import (
    AdminStatusResponse,
    BackfillResponse,
    BulkDownloadResponse,
    CollectResponse,
    CollectionLogResponse,
    TickerSyncResponse,
)
from app.tasks.backfill import run_backfill
from app.tasks.bulk_download import run_bulk_download
from app.tasks.daily_collection import run_daily_collection
from app.tasks.scheduler import scheduler
from app.tasks.ticker_sync import run_ticker_sync

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/status", response_model=AdminStatusResponse)
async def admin_status(
    session: AsyncSession = Depends(get_session),
):
    # Last collection log
    last_log_result = await session.execute(
        select(CollectionLog).order_by(CollectionLog.id.desc()).limit(1)
    )
    last_log = last_log_result.scalar_one_or_none()

    # Counts
    surge_count_result = await session.execute(select(func.count(SurgeEvent.id)))
    surge_count = surge_count_result.scalar() or 0

    ticker_count_result = await session.execute(select(func.count(Ticker.symbol)))
    ticker_count = ticker_count_result.scalar() or 0

    return AdminStatusResponse(
        scheduler_running=scheduler.running,
        last_collection=(
            CollectionLogResponse.model_validate(last_log) if last_log else None
        ),
        total_surge_events=surge_count,
        total_tickers=ticker_count,
    )


@router.post("/collect", response_model=CollectResponse)
async def manual_collect(
    target_date: date = Query(default=None, alias="date"),
):
    if target_date is None:
        target_date = datetime.now(timezone.utc).date()

    try:
        log_id = await run_daily_collection(target_date)
        return CollectResponse(
            message=f"Collection completed for {target_date}", log_id=log_id
        )
    except Exception as e:
        return CollectResponse(message=f"Collection failed: {e}", log_id=None)


@router.post("/backfill", response_model=BackfillResponse)
async def backfill(
    from_date: date = Query(alias="from_date"),
    to_date: date = Query(alias="to_date"),
):
    try:
        log_id = await run_backfill(from_date, to_date)
        return BackfillResponse(
            message=f"Backfill completed from {from_date} to {to_date}",
            log_id=log_id,
        )
    except Exception as e:
        return BackfillResponse(message=f"Backfill failed: {e}", log_id=None)


@router.post("/bulk-download", response_model=BulkDownloadResponse)
async def bulk_download(
    from_date: date = Query(alias="from_date"),
    to_date: date = Query(alias="to_date"),
):
    try:
        log_id = await run_bulk_download(from_date, to_date)
        return BulkDownloadResponse(
            message=f"Bulk download completed from {from_date} to {to_date}",
            log_id=log_id,
        )
    except Exception as e:
        return BulkDownloadResponse(
            message=f"Bulk download failed: {e}", log_id=None
        )


@router.post("/ticker-sync", response_model=TickerSyncResponse)
async def manual_ticker_sync():
    try:
        log_id = await run_ticker_sync()
        return TickerSyncResponse(
            message="Ticker sync completed", log_id=log_id
        )
    except Exception as e:
        return TickerSyncResponse(
            message=f"Ticker sync failed: {e}", log_id=None
        )
