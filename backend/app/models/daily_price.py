from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.ticker import Base


class DailyPrice(Base):
    __tablename__ = "daily_prices"
    __table_args__ = (
        Index("ix_daily_prices_symbol_date", "symbol", "trade_date", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    trade_date: Mapped[date] = mapped_column(Date, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[int] = mapped_column(BigInteger)
    vwap: Mapped[float | None] = mapped_column(Float, nullable=True)
    transactions: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
