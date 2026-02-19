from datetime import date, datetime

from sqlalchemy import Date, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.ticker import Base


class StockSplit(Base):
    __tablename__ = "stock_splits"
    __table_args__ = (
        Index("ix_stock_splits_symbol_date", "symbol", "execution_date", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    execution_date: Mapped[date] = mapped_column(Date, index=True)
    split_from: Mapped[int] = mapped_column(Integer)
    split_to: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
