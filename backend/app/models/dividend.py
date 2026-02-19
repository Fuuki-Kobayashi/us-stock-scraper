from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.ticker import Base


class Dividend(Base):
    __tablename__ = "dividends"
    __table_args__ = (
        Index("ix_dividends_symbol_ex_date", "symbol", "ex_dividend_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    cash_amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    declaration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    ex_dividend_date: Mapped[date] = mapped_column(Date, index=True)
    frequency: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pay_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    record_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    dividend_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
