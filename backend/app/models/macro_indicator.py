import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, Index, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MacroIndicator(Base):
    __tablename__ = "macro_indicators"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    indicator_type: Mapped[str] = mapped_column(String(50), nullable=False)
    indicator_code: Mapped[str] = mapped_column(String(50), nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    value: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    source: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    __table_args__ = (
        Index("idx_macro_code_date", "indicator_code", "date", unique=True),
        Index("idx_macro_type", "indicator_type"),
    )
