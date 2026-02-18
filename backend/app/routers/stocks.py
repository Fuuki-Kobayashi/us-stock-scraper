from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.stock import ChartResponse, OHLCVBar, SearchResponse, SearchResult
from app.services import stock_service

router = APIRouter(prefix="/api", tags=["stocks"])


@router.get("/stocks/{symbol}/chart", response_model=ChartResponse)
async def stock_chart(
    symbol: str,
    from_date: date = Query(default=None, alias="from"),
    to_date: date = Query(default=None, alias="to"),
):
    if from_date is None:
        from_date = date.today() - timedelta(days=90)
    if to_date is None:
        to_date = date.today()

    bars = await stock_service.get_chart_data(symbol, from_date, to_date)
    return ChartResponse(
        symbol=symbol,
        bars=[
            OHLCVBar(
                date=b["date"],
                open=b["open"],
                high=b["high"],
                low=b["low"],
                close=b["close"],
                volume=b["volume"],
                vwap=b.get("vwap"),
            )
            for b in bars
            if b["date"] is not None
        ],
    )


@router.get("/search", response_model=SearchResponse)
async def search_stocks(
    q: str = Query(min_length=1),
    session: AsyncSession = Depends(get_session),
):
    tickers = await stock_service.search_tickers(session, q)
    results = [
        SearchResult(
            symbol=t.symbol,
            name=t.name,
            exchange=t.exchange,
        )
        for t in tickers
    ]
    return SearchResponse(results=results, count=len(results))
