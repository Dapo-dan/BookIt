from sqlalchemy import String, Boolean, Numeric, Integer, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from datetime import datetime

class Service(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(2000))
    price: Mapped[float] = mapped_column(Numeric(10,2))
    duration_minutes: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
