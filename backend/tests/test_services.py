import pytest
from datetime import date

from app.models.surge_event import SurgeEvent
from app.models.ticker import Ticker
from app.services import surge_service, settings_service


@pytest.mark.asyncio
async def test_get_surges_empty(db_session):
    items, total = await surge_service.get_surges(db_session)
    assert items == []
    assert total == 0


@pytest.mark.asyncio
async def test_get_surges_with_filter(db_session):
    ticker = Ticker(symbol="GME", name="GameStop Corp.")
    db_session.add(ticker)
    await db_session.flush()

    surge1 = SurgeEvent(
        symbol="GME",
        event_date=date(2025, 1, 10),
        open=10.0, high=15.0, low=9.0, close=14.0,
        volume=100000, prev_close=10.0, change_pct=40.0,
    )
    surge2 = SurgeEvent(
        symbol="GME",
        event_date=date(2025, 1, 11),
        open=14.0, high=16.0, low=13.0, close=15.5,
        volume=80000, prev_close=14.0, change_pct=10.71,
    )
    db_session.add_all([surge1, surge2])
    await db_session.commit()

    # Filter by min_pct
    items, total = await surge_service.get_surges(db_session, min_pct=20.0)
    assert total == 1
    assert items[0].change_pct == 40.0


@pytest.mark.asyncio
async def test_get_settings_defaults(db_session):
    settings = await settings_service.get_settings(db_session)
    assert "surge_threshold_pct" in settings
    assert "collection_enabled" in settings


@pytest.mark.asyncio
async def test_update_settings(db_session):
    updated = await settings_service.update_settings(
        db_session, {"surge_threshold_pct": "15.0"}
    )
    assert updated["surge_threshold_pct"] == "15.0"
