from datetime import datetime

from pydantic import BaseModel


class CollectionLogResponse(BaseModel):
    id: int
    job_type: str
    started_at: datetime
    completed_at: datetime | None = None
    status: str
    records_count: int
    error_message: str | None = None

    model_config = {"from_attributes": True}


class AdminStatusResponse(BaseModel):
    scheduler_running: bool
    last_collection: CollectionLogResponse | None = None
    total_surge_events: int
    total_tickers: int


class CollectResponse(BaseModel):
    message: str
    log_id: int | None = None


class BackfillResponse(BaseModel):
    message: str
    log_id: int | None = None


class TickerSyncResponse(BaseModel):
    message: str
    log_id: int | None = None
