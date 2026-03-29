from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Ticker(Base):
    __tablename__ = "tickers"

    symbol: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    market: Mapped[str | None] = mapped_column(String(50), nullable=True)
    exchange: Mapped[str | None] = mapped_column(String(50), nullable=True)
    type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sic_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    sic_description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Fundamentals from ticker_details API
    market_cap: Mapped[float | None] = mapped_column(Float, nullable=True)
    shares_outstanding: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    weighted_shares_outstanding: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True
    )
    total_employees: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    homepage_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    list_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    primary_exchange: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cik: Mapped[str | None] = mapped_column(String(20), nullable=True)
    details_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    surge_events: Mapped[list["SurgeEvent"]] = relationship(  # noqa: F821
        back_populates="ticker"
    )
