from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.surge_event import SurgeEvent
from app.models.surge_tracking import SurgeTracking
from app.models.ticker import Ticker


async def get_tracking_performance(
    session: AsyncSession,
) -> list[dict]:
    """Get average post-surge performance by days_after."""
    query = (
        select(
            SurgeTracking.days_after,
            func.avg(SurgeTracking.change_from_surge_pct),
            func.count(SurgeTracking.id),
        )
        .group_by(SurgeTracking.days_after)
        .order_by(SurgeTracking.days_after)
    )
    result = await session.execute(query)
    rows = result.all()

    performance = []
    for row in rows:
        days_after = row[0]
        avg_change = float(row[1]) if row[1] else 0.0
        count = row[2]

        # Calculate win rate (positive change)
        win_query = (
            select(func.count(SurgeTracking.id))
            .where(
                SurgeTracking.days_after == days_after,
                SurgeTracking.change_from_surge_pct > 0,
            )
        )
        win_result = await session.execute(win_query)
        win_count = win_result.scalar() or 0
        win_rate = (win_count / count * 100) if count > 0 else 0.0

        performance.append(
            {
                "days_after": days_after,
                "avg_change_pct": round(avg_change, 2),
                "win_rate": round(win_rate, 2),
                "sample_count": count,
            }
        )

    return performance


async def get_tracking_by_sector(
    session: AsyncSession,
) -> list[dict]:
    """Get post-surge tracking breakdown by sector."""
    query = (
        select(
            Ticker.sic_description,
            SurgeTracking.days_after,
            func.avg(SurgeTracking.change_from_surge_pct),
            func.count(SurgeTracking.id),
        )
        .join(SurgeEvent, SurgeTracking.surge_event_id == SurgeEvent.id)
        .join(Ticker, SurgeEvent.symbol == Ticker.symbol)
        .where(Ticker.sic_description.isnot(None))
        .group_by(Ticker.sic_description, SurgeTracking.days_after)
        .order_by(Ticker.sic_description, SurgeTracking.days_after)
    )
    result = await session.execute(query)
    rows = result.all()

    sectors: dict[str, list[dict]] = {}
    for row in rows:
        sector = row[0]
        if sector not in sectors:
            sectors[sector] = []

        total = row[3]
        avg_change = float(row[2]) if row[2] else 0.0

        # Win rate per sector/days combination
        win_query = (
            select(func.count(SurgeTracking.id))
            .join(SurgeEvent, SurgeTracking.surge_event_id == SurgeEvent.id)
            .join(Ticker, SurgeEvent.symbol == Ticker.symbol)
            .where(
                Ticker.sic_description == sector,
                SurgeTracking.days_after == row[1],
                SurgeTracking.change_from_surge_pct > 0,
            )
        )
        win_result = await session.execute(win_query)
        win_count = win_result.scalar() or 0
        win_rate = (win_count / total * 100) if total > 0 else 0.0

        sectors[sector].append(
            {
                "days_after": row[1],
                "avg_change_pct": round(avg_change, 2),
                "win_rate": round(win_rate, 2),
                "sample_count": total,
            }
        )

    return [
        {"sector": sector, "performance": perf} for sector, perf in sectors.items()
    ]
