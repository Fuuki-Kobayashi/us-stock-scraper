from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class StockDataSource(ABC):
    @abstractmethod
    async def grouped_daily(self, target_date: date) -> list[dict[str, Any]]:
        """Fetch all stock OHLCV data for a given date."""
        ...

    @abstractmethod
    async def ticker_details(self, symbol: str) -> dict[str, Any] | None:
        """Fetch ticker details for a symbol."""
        ...

    @abstractmethod
    async def tickers_list(self, page: int = 1) -> dict[str, Any]:
        """Fetch paginated list of active tickers."""
        ...

    @abstractmethod
    async def aggregate_bars(
        self, symbol: str, from_date: date, to_date: date
    ) -> list[dict[str, Any]]:
        """Fetch aggregate bars for a symbol over a date range."""
        ...
