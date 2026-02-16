import datetime
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Multiple(Base):
    __tablename__ = "multiples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    calc_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    period_end: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    pe: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    ev_ebitda: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    ev_sales: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    pb: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    ps: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    roe: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    roa: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    debt_ebitda: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    dividend_yield: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    market_cap: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    enterprise_value: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    company = relationship("Company", back_populates="multiples")

    __table_args__ = (
        Index("idx_multiples_company_date", "company_id", "calc_date", "period_end", unique=True),
        Index("idx_multiples_calc_date", "calc_date"),
    )
