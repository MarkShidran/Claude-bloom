from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PeerGroup(Base):
    __tablename__ = "peer_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    formation_type: Mapped[str] = mapped_column(String(10), default="manual")
    auto_criteria: Mapped[dict | None] = mapped_column(JSONB)
    created_by: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    members = relationship("PeerGroupMember", back_populates="peer_group", cascade="all, delete-orphan")


class PeerGroupMember(Base):
    __tablename__ = "peer_group_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    peer_group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("peer_groups.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    added_at: Mapped[datetime] = mapped_column(server_default=func.now())

    peer_group = relationship("PeerGroup", back_populates="members")
    company = relationship("Company")

    __table_args__ = (
        Index("idx_pgm_group_company", "peer_group_id", "company_id", unique=True),
    )
