from datetime import date, datetime

from pydantic import BaseModel

from app.schemas.tracking import TrackingRecord


class SurgeEventResponse(BaseModel):
    id: int
    symbol: str
    event_date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    prev_close: float
    change_pct: float
    vwap: float | None = None
    created_at: datetime
    ticker_name: str | None = None
    sic_description: str | None = None

    model_config = {"from_attributes": True}


class SurgeEventDetail(SurgeEventResponse):
    tracking_records: list[TrackingRecord] = []


class SurgeListResponse(BaseModel):
    items: list[SurgeEventResponse]
    total: int
    page: int
    page_size: int


class SectorStat(BaseModel):
    sector: str
    count: int
    avg_change_pct: float


class DayOfWeekStat(BaseModel):
    day_of_week: int
    day_name: str
    count: int


class MonthStat(BaseModel):
    month: int
    month_name: str
    count: int


class RepeatSurger(BaseModel):
    symbol: str
    name: str | None = None
    surge_count: int
    avg_change_pct: float


class SurgeStatsResponse(BaseModel):
    total_surges: int
    by_sector: list[SectorStat]
    by_day_of_week: list[DayOfWeekStat]
    by_month: list[MonthStat]
    repeat_surgers: list[RepeatSurger]
