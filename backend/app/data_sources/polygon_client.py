import asyncio
import logging
from datetime import date
from typing import Any

import httpx

from app.config import settings
from app.data_sources.base import StockDataSource
from app.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

BASE_URL = "https://api.polygon.io"
MAX_RETRIES = 3
RETRY_BACKOFF = 65  # seconds to wait on 429


class PolygonFreeSource(StockDataSource):
    def __init__(self) -> None:
        self._api_key = settings.POLYGON_API_KEY
        self._rate_limiter = RateLimiter(max_tokens=4, refill_rate=4 / 60)
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(self, url: str, params: dict | None = None) -> dict[str, Any]:
        if params is None:
            params = {}
        params["apiKey"] = self._api_key

        for attempt in range(MAX_RETRIES):
            await self._rate_limiter.acquire()
            response = await self._client.get(url, params=params)
            if response.status_code == 429:
                logger.warning(
                    "Rate limited (429), waiting %ds (attempt %d/%d)",
                    RETRY_BACKOFF, attempt + 1, MAX_RETRIES,
                )
                await asyncio.sleep(RETRY_BACKOFF)
                continue
            response.raise_for_status()
            return response.json()

        response.raise_for_status()
        return response.json()

    async def grouped_daily(self, target_date: date) -> list[dict[str, Any]]:
        date_str = target_date.strftime("%Y-%m-%d")
        url = f"{BASE_URL}/v2/aggs/grouped/locale/us/market/stocks/{date_str}"
        data = await self._request(url)
        return data.get("results", [])

    async def ticker_details(self, symbol: str) -> dict[str, Any] | None:
        url = f"{BASE_URL}/v3/reference/tickers/{symbol}"
        try:
            data = await self._request(url)
            return data.get("results")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def search_tickers(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        url = f"{BASE_URL}/v3/reference/tickers"
        params = {
            "search": query,
            "market": "stocks",
            "active": "true",
            "limit": str(limit),
        }
        try:
            data = await self._request(url, params)
            return data.get("results", [])
        except Exception as e:
            logger.warning("Polygon ticker search failed: %s", e)
            return []

    async def tickers_list(self, cursor: str | None = None) -> dict[str, Any]:
        url = f"{BASE_URL}/v3/reference/tickers"
        params: dict[str, str] = {
            "market": "stocks",
            "active": "true",
            "limit": "1000",
        }
        if cursor:
            params["cursor"] = cursor
        data = await self._request(url, params)
        # Extract cursor from next_url for pagination
        next_cursor: str | None = None
        next_url = data.get("next_url")
        if next_url:
            from urllib.parse import parse_qs, urlparse

            parsed = urlparse(next_url)
            qs = parse_qs(parsed.query)
            next_cursor = qs.get("cursor", [None])[0]
        return {
            "results": data.get("results", []),
            "next_cursor": next_cursor,
            "count": data.get("count", 0),
        }

    async def dividends(
        self, cursor: str | None = None, limit: int = 1000
    ) -> dict[str, Any]:
        url = f"{BASE_URL}/v3/reference/dividends"
        params: dict[str, str] = {"limit": str(limit), "order": "asc"}
        if cursor:
            params["cursor"] = cursor
        data = await self._request(url, params)
        next_cursor: str | None = None
        next_url = data.get("next_url")
        if next_url:
            from urllib.parse import parse_qs, urlparse
            parsed = urlparse(next_url)
            qs = parse_qs(parsed.query)
            next_cursor = qs.get("cursor", [None])[0]
        return {
            "results": data.get("results", []),
            "next_cursor": next_cursor,
        }

    async def splits(
        self, cursor: str | None = None, limit: int = 1000
    ) -> dict[str, Any]:
        url = f"{BASE_URL}/v3/reference/splits"
        params: dict[str, str] = {"limit": str(limit), "order": "asc"}
        if cursor:
            params["cursor"] = cursor
        data = await self._request(url, params)
        next_cursor: str | None = None
        next_url = data.get("next_url")
        if next_url:
            from urllib.parse import parse_qs, urlparse
            parsed = urlparse(next_url)
            qs = parse_qs(parsed.query)
            next_cursor = qs.get("cursor", [None])[0]
        return {
            "results": data.get("results", []),
            "next_cursor": next_cursor,
        }

    async def aggregate_bars(
        self, symbol: str, from_date: date, to_date: date
    ) -> list[dict[str, Any]]:
        from_str = from_date.strftime("%Y-%m-%d")
        to_str = to_date.strftime("%Y-%m-%d")
        url = (
            f"{BASE_URL}/v2/aggs/ticker/{symbol}"
            f"/range/1/day/{from_str}/{to_str}"
        )
        data = await self._request(url)
        return data.get("results", [])


# Singleton instance
polygon_client = PolygonFreeSource()
