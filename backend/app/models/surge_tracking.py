from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.ticker import Base


class SurgeTracking(Base):
    __tablename__ = "surge_tracking"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    surge_event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("surge_events.id"), index=True
    )
    days_after: Mapped[int] = mapped_column(Integer)
    close_price: Mapped[float] = mapped_column(Float)
    change_from_surge_pct: Mapped[float] = mapped_column(Float)
    tracked_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    surge_event: Mapped["SurgeEvent"] = relationship(  # noqa: F821
        back_populates="tracking_records"
    )
