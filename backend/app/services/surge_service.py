from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.surge_event import SurgeEvent
from app.models.ticker import Ticker


async def get_surges(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    from_date: date | None = None,
    to_date: date | None = None,
    min_pct: float | None = None,
    sector: str | None = None,
) -> tuple[list[SurgeEvent], int]:
    """Get paginated surge events with optional filters."""
    query = select(SurgeEvent).join(Ticker, isouter=True)
    count_query = select(func.count(SurgeEvent.id))

    if from_date:
        query = query.where(SurgeEvent.event_date >= from_date)
        count_query = count_query.where(SurgeEvent.event_date >= from_date)
    if to_date:
        query = query.where(SurgeEvent.event_date <= to_date)
        count_query = count_query.where(SurgeEvent.event_date <= to_date)
    if min_pct is not None:
        query = query.where(SurgeEvent.change_pct >= min_pct)
        count_query = count_query.where(SurgeEvent.change_pct >= min_pct)
    if sector:
        query = query.where(Ticker.sic_description == sector)
        count_query = count_query.join(Ticker).where(
            Ticker.sic_description == sector
        )

    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    query = (
        query.options(joinedload(SurgeEvent.ticker))
        .order_by(SurgeEvent.change_pct.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await session.execute(query)
    items = list(result.unique().scalars().all())

    return items, total


async def get_today_surges(session: AsyncSession) -> list[SurgeEvent]:
    """Get today's surge events."""
    today = date.today()
    query = (
        select(SurgeEvent)
        .options(joinedload(SurgeEvent.ticker))
        .where(SurgeEvent.event_date == today)
        .order_by(SurgeEvent.change_pct.desc())
    )
    result = await session.execute(query)
    return list(result.unique().scalars().all())


async def get_surge_detail(
    session: AsyncSession, surge_id: int
) -> SurgeEvent | None:
    """Get surge event with tracking records."""
    query = (
        select(SurgeEvent)
        .options(
            joinedload(SurgeEvent.ticker),
            joinedload(SurgeEvent.tracking_records),
        )
        .where(SurgeEvent.id == surge_id)
    )
    result = await session.execute(query)
    return result.unique().scalar_one_or_none()


async def get_surge_stats(
    session: AsyncSession,
) -> dict:
    """Get surge statistics."""
    # Total count
    total_result = await session.execute(select(func.count(SurgeEvent.id)))
    total = total_result.scalar() or 0

    # By sector
    sector_query = (
        select(
            Ticker.sic_description,
            func.count(SurgeEvent.id),
            func.avg(SurgeEvent.change_pct),
        )
        .join(Ticker)
        .where(Ticker.sic_description.isnot(None))
        .group_by(Ticker.sic_description)
        .order_by(func.count(SurgeEvent.id).desc())
        .limit(20)
    )
    sector_result = await session.execute(sector_query)
    by_sector = [
        {"sector": row[0], "count": row[1], "avg_change_pct": round(float(row[2]), 2)}
        for row in sector_result.all()
    ]

    # Repeat surgers
    repeat_query = (
        select(
            SurgeEvent.symbol,
            Ticker.name,
            func.count(SurgeEvent.id).label("cnt"),
            func.avg(SurgeEvent.change_pct),
        )
        .join(Ticker, isouter=True)
        .group_by(SurgeEvent.symbol, Ticker.name)
        .having(func.count(SurgeEvent.id) > 1)
        .order_by(func.count(SurgeEvent.id).desc())
        .limit(20)
    )
    repeat_result = await session.execute(repeat_query)
    repeat_surgers = [
        {
            "symbol": row[0],
            "name": row[1],
            "surge_count": row[2],
            "avg_change_pct": round(float(row[3]), 2),
        }
        for row in repeat_result.all()
    ]

    return {
        "total_surges": total,
        "by_sector": by_sector,
        "by_day_of_week": [],
        "by_month": [],
        "repeat_surgers": repeat_surgers,
    }
