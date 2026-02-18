from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings as app_settings
from app.models.user_setting import UserSetting

DEFAULT_SETTINGS = {
    "surge_threshold_pct": str(app_settings.SURGE_THRESHOLD_PCT),
    "collection_enabled": "true",
}


async def get_settings(session: AsyncSession) -> dict[str, str]:
    """Get all user settings, with defaults."""
    result = await session.execute(select(UserSetting))
    db_settings = {s.key: s.value for s in result.scalars().all()}

    merged = {**DEFAULT_SETTINGS, **db_settings}
    return merged


async def update_settings(
    session: AsyncSession, updates: dict[str, str | None]
) -> dict[str, str]:
    """Update user settings."""
    for key, value in updates.items():
        if value is None:
            continue
        result = await session.execute(
            select(UserSetting).where(UserSetting.key == key)
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.value = str(value)
            existing.updated_at = datetime.utcnow()
        else:
            session.add(UserSetting(key=key, value=str(value)))

    await session.commit()
    return await get_settings(session)
