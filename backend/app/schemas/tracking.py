from datetime import date

from pydantic import BaseModel


class TrackingRecord(BaseModel):
    id: int
    surge_event_id: int
    days_after: int
    close_price: float
    change_from_surge_pct: float
    tracked_date: date

    model_config = {"from_attributes": True}


class PerformanceSummary(BaseModel):
    days_after: int
    avg_change_pct: float
    win_rate: float
    sample_count: int


class TrackingResponse(BaseModel):
    performance: list[PerformanceSummary]


class SectorTracking(BaseModel):
    sector: str
    performance: list[PerformanceSummary]


class TrackingBySectorResponse(BaseModel):
    sectors: list[SectorTracking]
