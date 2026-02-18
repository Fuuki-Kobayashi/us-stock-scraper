from pydantic import BaseModel


class SettingsResponse(BaseModel):
    surge_threshold_pct: float = 20.0
    collection_enabled: bool = True


class SettingsUpdate(BaseModel):
    surge_threshold_pct: float | None = None
    collection_enabled: bool | None = None
