from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.data_sources.polygon_client import polygon_client
from app.models.ticker import Ticker


async def search_tickers(
    session: AsyncSession, query: str, limit: int = 20
) -> list:
    """Search tickers by symbol or name. Falls back to Polygon.io API if local DB is empty."""
    pattern = f"%{query.upper()}%"
    stmt = (
        select(Ticker)
        .where(
            (Ticker.symbol.like(pattern)) | (Ticker.name.like(pattern))
        )
        .limit(limit)
    )
    result = await session.execute(stmt)
    local_results = list(result.scalars().all())

    if local_results:
        return local_results

    # Fallback: search via Polygon.io API
    api_results = await polygon_client.search_tickers(query, limit)
    return [
        _PolygonSearchResult(
            symbol=r.get("ticker", ""),
            name=r.get("name"),
            exchange=r.get("primary_exchange"),
        )
        for r in api_results
    ]


class _PolygonSearchResult:
    """Lightweight object matching Ticker interface for search results."""

    def __init__(self, symbol: str, name: str | None, exchange: str | None):
        self.symbol = symbol
        self.name = name
        self.exchange = exchange


async def get_chart_data(
    symbol: str, from_date: date, to_date: date
) -> list[dict]:
    """Get OHLCV chart data for a symbol."""
    bars = await polygon_client.aggregate_bars(symbol, from_date, to_date)
    result = []
    for bar in bars:
        timestamp_ms = bar.get("t")
        bar_date = None
        if timestamp_ms:
            bar_date = date.fromtimestamp(timestamp_ms / 1000)

        result.append(
            {
                "date": bar_date.isoformat() if bar_date else None,
                "open": bar.get("o"),
                "high": bar.get("h"),
                "low": bar.get("l"),
                "close": bar.get("c"),
                "volume": bar.get("v"),
                "vwap": bar.get("vw"),
            }
        )
    return result
