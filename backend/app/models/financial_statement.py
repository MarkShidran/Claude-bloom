import datetime

from sqlalchemy import Boolean, Date, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class FinancialStatement(TimestampMixin, Base):
    __tablename__ = "financial_statements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    standard: Mapped[str] = mapped_column(String(10), nullable=False)  # RSBU, IFRS, US_GAAP
    statement_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # balance_sheet, income_statement, cash_flow
    period_type: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # annual, semi_annual, quarterly
    period_start: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    period_end: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    unit_multiplier: Mapped[int] = mapped_column(Integer, default=1000)
    source: Mapped[str | None] = mapped_column(String(50))
    source_url: Mapped[str | None] = mapped_column(String(1000))
    is_audited: Mapped[bool] = mapped_column(Boolean, default=False)

    company = relationship("Company", back_populates="financial_statements")
    items = relationship("StatementItem", back_populates="statement", cascade="all, delete-orphan")

    __table_args__ = (
        Index(
            "idx_fs_company_period",
            "company_id",
            "standard",
            "statement_type",
            "period_end",
            unique=True,
        ),
        Index("idx_fs_company", "company_id"),
        Index("idx_fs_period_end", "period_end"),
    )
