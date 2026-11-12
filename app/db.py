import os
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, create_engine, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


class Base(DeclarativeBase):
    pass


class Rate(Base):
    __tablename__ = "rates"
    __table_args__ = (UniqueConstraint("rate_date", "currency"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    rate_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    currency: Mapped[str] = mapped_column(String(3))
    value: Mapped[Decimal] = mapped_column(Numeric(12, 4))
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )