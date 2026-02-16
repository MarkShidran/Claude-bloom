from sqlalchemy import Boolean, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class Company(TimestampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(500))
    ticker: Mapped[str | None] = mapped_column(String(20))
    inn: Mapped[str | None] = mapped_column(String(12), unique=True)
    ogrn: Mapped[str | None] = mapped_column(String(15))
    sector: Mapped[str | None] = mapped_column(String(100))
    industry: Mapped[str | None] = mapped_column(String(200))
    country: Mapped[str] = mapped_column(String(3), default="RUS")
    description: Mapped[str | None] = mapped_column(Text)
    website: Mapped[str | None] = mapped_column(String(500))
    edisclosure_id: Mapped[int | None] = mapped_column(Integer)
    moex_secid: Mapped[str | None] = mapped_column(String(50))
    sec_cik: Mapped[str | None] = mapped_column(String(20))
    yahoo_ticker: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    securities = relationship("Security", back_populates="company", cascade="all, delete-orphan")
    financial_statements = relationship(
        "FinancialStatement", back_populates="company", cascade="all, delete-orphan"
    )
    multiples = relationship("Multiple", back_populates="company", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_companies_ticker", "ticker"),
        Index("idx_companies_inn", "inn"),
        Index("idx_companies_sector", "sector"),
        Index("idx_companies_country", "country"),
    )
