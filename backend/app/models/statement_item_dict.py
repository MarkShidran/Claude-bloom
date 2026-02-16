from sqlalchemy import Boolean, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class StatementItemDict(Base):
    __tablename__ = "statement_item_dict"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name_ru: Mapped[str] = mapped_column(String(500), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(500))
    statement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    standard: Mapped[str | None] = mapped_column(String(10))  # NULL = universal
    parent_code: Mapped[str | None] = mapped_column(String(100))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_calculated: Mapped[bool] = mapped_column(Boolean, default=False)
    formula: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        Index("idx_sid_statement", "statement_type", "standard"),
    )
