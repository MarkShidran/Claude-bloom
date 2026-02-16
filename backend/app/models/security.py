from sqlalchemy import Boolean, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class Security(TimestampMixin, Base):
    __tablename__ = "securities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    isin: Mapped[str | None] = mapped_column(String(12), unique=True)
    security_type: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    exchange: Mapped[str] = mapped_column(String(20), default="MOEX")
    moex_secid: Mapped[str | None] = mapped_column(String(50))
    moex_boardid: Mapped[str | None] = mapped_column(String(20))
    lot_size: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    company = relationship("Company", back_populates="securities")
    quotes = relationship("Quote", back_populates="security", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_securities_ticker_exchange", "ticker", "exchange", unique=True),
        Index("idx_securities_company", "company_id"),
    )
