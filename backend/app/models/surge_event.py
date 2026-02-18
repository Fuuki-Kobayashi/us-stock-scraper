from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.ticker import Base


class SurgeEvent(Base):
    __tablename__ = "surge_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(
        String(20), ForeignKey("tickers.symbol"), index=True
    )
    event_date: Mapped[date] = mapped_column(Date, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[int] = mapped_column(Integer)
    prev_close: Mapped[float] = mapped_column(Float)
    change_pct: Mapped[float] = mapped_column(Float, index=True)
    vwap: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ticker: Mapped["Ticker"] = relationship(back_populates="surge_events")  # noqa: F821
    tracking_records: Mapped[list["SurgeTracking"]] = relationship(  # noqa: F821
        back_populates="surge_event"
    )
