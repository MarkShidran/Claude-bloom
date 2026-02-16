from datetime import datetime

from pydantic import BaseModel, Field


class PeerGroupBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: str | None = None


class PeerGroupCreate(PeerGroupBase):
    company_ids: list[int] = []


class PeerGroupOut(PeerGroupBase):
    id: int
    formation_type: str
    created_by: str | None = None
    created_at: datetime
    member_count: int = 0

    model_config = {"from_attributes": True}


class PeerGroupDetail(PeerGroupOut):
    company_ids: list[int] = []
