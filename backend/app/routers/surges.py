from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.surge import (
    SurgeEventDetail,
    SurgeEventResponse,
    SurgeListResponse,
    SurgeStatsResponse,
)
from app.services import surge_service

router = APIRouter(prefix="/api/surges", tags=["surges"])


@router.get("/", response_model=SurgeListResponse)
async def list_surges(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    from_date: date | None = None,
    to_date: date | None = None,
    min_pct: float | None = None,
    sector: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    items, total = await surge_service.get_surges(
        session,
        page=page,
        page_size=page_size,
        from_date=from_date,
        to_date=to_date,
        min_pct=min_pct,
        sector=sector,
    )
    return SurgeListResponse(
        items=[
            SurgeEventResponse(
                id=s.id,
                symbol=s.symbol,
                event_date=s.event_date,
                open=s.open,
                high=s.high,
                low=s.low,
                close=s.close,
                volume=s.volume,
                prev_close=s.prev_close,
                change_pct=s.change_pct,
                vwap=s.vwap,
                created_at=s.created_at,
                ticker_name=s.ticker.name if s.ticker else None,
                sic_description=s.ticker.sic_description if s.ticker else None,
            )
            for s in items
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/today", response_model=list[SurgeEventResponse])
async def today_surges(
    session: AsyncSession = Depends(get_session),
):
    items = await surge_service.get_today_surges(session)
    return [
        SurgeEventResponse(
            id=s.id,
            symbol=s.symbol,
            event_date=s.event_date,
            open=s.open,
            high=s.high,
            low=s.low,
            close=s.close,
            volume=s.volume,
            prev_close=s.prev_close,
            change_pct=s.change_pct,
            vwap=s.vwap,
            created_at=s.created_at,
            ticker_name=s.ticker.name if s.ticker else None,
            sic_description=s.ticker.sic_description if s.ticker else None,
        )
        for s in items
    ]


@router.get("/stats", response_model=SurgeStatsResponse)
async def surge_stats(
    session: AsyncSession = Depends(get_session),
):
    stats = await surge_service.get_surge_stats(session)
    return SurgeStatsResponse(**stats)


@router.get("/{surge_id}", response_model=SurgeEventDetail)
async def surge_detail(
    surge_id: int,
    session: AsyncSession = Depends(get_session),
):
    event = await surge_service.get_surge_detail(session, surge_id)
    if event is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Surge event not found")
    return SurgeEventDetail(
        id=event.id,
        symbol=event.symbol,
        event_date=event.event_date,
        open=event.open,
        high=event.high,
        low=event.low,
        close=event.close,
        volume=event.volume,
        prev_close=event.prev_close,
        change_pct=event.change_pct,
        vwap=event.vwap,
        created_at=event.created_at,
        ticker_name=event.ticker.name if event.ticker else None,
        sic_description=event.ticker.sic_description if event.ticker else None,
        tracking_records=event.tracking_records,
    )
