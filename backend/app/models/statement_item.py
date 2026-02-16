from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class StatementItem(Base):
    __tablename__ = "statement_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    statement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("financial_statements.id", ondelete="CASCADE"), nullable=False
    )
    item_dict_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("statement_item_dict.id"), nullable=False
    )
    value: Mapped[Decimal | None] = mapped_column(Numeric(20, 2))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    statement = relationship("FinancialStatement", back_populates="items")
    item_dict = relationship("StatementItemDict")

    __table_args__ = (
        Index("idx_si_statement", "statement_id"),
        Index("idx_si_statement_item", "statement_id", "item_dict_id", unique=True),
    )
