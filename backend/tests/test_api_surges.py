import pytest
from datetime import date, datetime

from app.models.surge_event import SurgeEvent
from app.models.ticker import Ticker


@pytest.mark.asyncio
async def test_list_surges_empty(client):
    response = await client.get("/api/surges/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1


@pytest.mark.asyncio
async def test_list_surges_with_data(client, db_session):
    # Create test data
    ticker = Ticker(symbol="AAPL", name="Apple Inc.")
    db_session.add(ticker)
    await db_session.flush()

    surge = SurgeEvent(
        symbol="AAPL",
        event_date=date(2025, 1, 15),
        open=150.0,
        high=185.0,
        low=149.0,
        close=180.0,
        volume=1000000,
        prev_close=150.0,
        change_pct=20.0,
        vwap=175.0,
    )
    db_session.add(surge)
    await db_session.commit()

    response = await client.get("/api/surges/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["symbol"] == "AAPL"
    assert data["items"][0]["change_pct"] == 20.0


@pytest.mark.asyncio
async def test_surge_detail_not_found(client):
    response = await client.get("/api/surges/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_surge_detail(client, db_session):
    ticker = Ticker(symbol="TSLA", name="Tesla Inc.")
    db_session.add(ticker)
    await db_session.flush()

    surge = SurgeEvent(
        symbol="TSLA",
        event_date=date(2025, 1, 15),
        open=200.0,
        high=260.0,
        low=198.0,
        close=250.0,
        volume=5000000,
        prev_close=200.0,
        change_pct=25.0,
    )
    db_session.add(surge)
    await db_session.commit()

    response = await client.get(f"/api/surges/{surge.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "TSLA"
    assert data["change_pct"] == 25.0
    assert data["tracking_records"] == []


@pytest.mark.asyncio
async def test_surge_stats(client):
    response = await client.get("/api/surges/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_surges" in data
    assert "by_sector" in data
    assert "repeat_surgers" in data


@pytest.mark.asyncio
async def test_today_surges(client):
    response = await client.get("/api/surges/today")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
