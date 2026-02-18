from datetime import date, datetime

from pydantic import BaseModel


class TickerResponse(BaseModel):
    symbol: str
    name: str | None = None
    market: str | None = None
    exchange: str | None = None
    type: str | None = None
    sic_code: str | None = None
    sic_description: str | None = None
    currency: str | None = None
    active: bool = True

    model_config = {"from_attributes": True}


class OHLCVBar(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float | None = None


class ChartResponse(BaseModel):
    symbol: str
    bars: list[OHLCVBar]


class SearchResult(BaseModel):
    symbol: str
    name: str | None = None
    exchange: str | None = None


class SearchResponse(BaseModel):
    results: list[SearchResult]
    count: int
