from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.tracking import TrackingBySectorResponse, TrackingResponse
from app.services import tracking_service

router = APIRouter(prefix="/api/tracking", tags=["tracking"])


@router.get("/", response_model=TrackingResponse)
async def tracking_performance(
    session: AsyncSession = Depends(get_session),
):
    performance = await tracking_service.get_tracking_performance(session)
    return TrackingResponse(performance=performance)


@router.get("/by-sector", response_model=TrackingBySectorResponse)
async def tracking_by_sector(
    session: AsyncSession = Depends(get_session),
):
    sectors = await tracking_service.get_tracking_by_sector(session)
    return TrackingBySectorResponse(sectors=sectors)
