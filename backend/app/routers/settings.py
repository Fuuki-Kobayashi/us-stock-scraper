from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.settings import SettingsResponse, SettingsUpdate
from app.services import settings_service

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/", response_model=SettingsResponse)
async def get_settings(
    session: AsyncSession = Depends(get_session),
):
    settings = await settings_service.get_settings(session)
    return SettingsResponse(
        surge_threshold_pct=float(settings.get("surge_threshold_pct", "20.0")),
        collection_enabled=settings.get("collection_enabled", "true").lower() == "true",
    )


@router.put("/", response_model=SettingsResponse)
async def update_settings(
    body: SettingsUpdate,
    session: AsyncSession = Depends(get_session),
):
    updates: dict[str, str | None] = {}
    if body.surge_threshold_pct is not None:
        updates["surge_threshold_pct"] = str(body.surge_threshold_pct)
    if body.collection_enabled is not None:
        updates["collection_enabled"] = str(body.collection_enabled).lower()

    settings = await settings_service.update_settings(session, updates)
    return SettingsResponse(
        surge_threshold_pct=float(settings.get("surge_threshold_pct", "20.0")),
        collection_enabled=settings.get("collection_enabled", "true").lower() == "true",
    )
