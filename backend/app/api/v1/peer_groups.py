from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db
from app.models.peer_group import PeerGroup, PeerGroupMember
from app.schemas.peer_group import PeerGroupCreate, PeerGroupDetail, PeerGroupOut

router = APIRouter(prefix="/peergroups", tags=["Peer Groups"])


@router.get("/", response_model=list[PeerGroupOut])
async def list_peer_groups(
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(
            PeerGroup,
            func.count(PeerGroupMember.id).label("member_count"),
        )
        .outerjoin(PeerGroupMember, PeerGroup.id == PeerGroupMember.peer_group_id)
        .group_by(PeerGroup.id)
        .order_by(PeerGroup.name)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        PeerGroupOut(
            id=row.PeerGroup.id,
            name=row.PeerGroup.name,
            description=row.PeerGroup.description,
            formation_type=row.PeerGroup.formation_type,
            created_by=row.PeerGroup.created_by,
            created_at=row.PeerGroup.created_at,
            member_count=row.member_count,
        )
        for row in rows
    ]


@router.post("/", response_model=PeerGroupDetail, status_code=201)
async def create_peer_group(
    data: PeerGroupCreate,
    db: AsyncSession = Depends(get_db),
):
    peer_group = PeerGroup(
        name=data.name,
        description=data.description,
        formation_type="manual",
    )
    db.add(peer_group)
    await db.flush()

    for company_id in data.company_ids:
        member = PeerGroupMember(
            peer_group_id=peer_group.id,
            company_id=company_id,
        )
        db.add(member)

    await db.flush()
    await db.refresh(peer_group)

    return PeerGroupDetail(
        id=peer_group.id,
        name=peer_group.name,
        description=peer_group.description,
        formation_type=peer_group.formation_type,
        created_by=peer_group.created_by,
        created_at=peer_group.created_at,
        member_count=len(data.company_ids),
        company_ids=data.company_ids,
    )


@router.get("/{peer_group_id}", response_model=PeerGroupDetail)
async def get_peer_group(
    peer_group_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(PeerGroup)
        .where(PeerGroup.id == peer_group_id)
        .options(selectinload(PeerGroup.members))
    )
    result = await db.execute(stmt)
    peer_group = result.scalar_one_or_none()

    if peer_group is None:
        raise HTTPException(status_code=404, detail="Peer group not found")

    return PeerGroupDetail(
        id=peer_group.id,
        name=peer_group.name,
        description=peer_group.description,
        formation_type=peer_group.formation_type,
        created_by=peer_group.created_by,
        created_at=peer_group.created_at,
        member_count=len(peer_group.members),
        company_ids=[m.company_id for m in peer_group.members],
    )


@router.delete("/{peer_group_id}")
async def delete_peer_group(
    peer_group_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(PeerGroup).where(PeerGroup.id == peer_group_id)
    result = await db.execute(stmt)
    peer_group = result.scalar_one_or_none()

    if peer_group is None:
        raise HTTPException(status_code=404, detail="Peer group not found")

    await db.delete(peer_group)
    await db.flush()

    return {"status": "deleted", "id": peer_group_id}
