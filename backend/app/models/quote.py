import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, ForeignKey, Index, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    security_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("securities.id"), nullable=False
    )
    trade_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    open: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    high: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    low: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    close: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    adj_close: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    volume: Mapped[int | None] = mapped_column(BigInteger)
    value: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    num_trades: Mapped[int | None] = mapped_column(Integer)

    security = relationship("Security", back_populates="quotes")

    __table_args__ = (
        Index("idx_quotes_security_date", "security_id", "trade_date", unique=True),
        Index("idx_quotes_trade_date", "trade_date"),
    )
