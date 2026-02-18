from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
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
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    surge_events: Mapped[list["SurgeEvent"]] = relationship(  # noqa: F821
        back_populates="ticker"
    )
