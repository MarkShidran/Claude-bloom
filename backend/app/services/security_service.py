from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.security import Security
from app.schemas.security import SecurityCreate


class SecurityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_by_company(self, company_id: int) -> list[Security]:
        stmt = (
            select(Security)
            .where(Security.company_id == company_id, Security.is_active.is_(True))
            .order_by(Security.ticker)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_security(self, security_id: int) -> Security | None:
        stmt = select(Security).where(Security.id == security_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_security(self, data: SecurityCreate) -> Security:
        security = Security(**data.model_dump())
        self.db.add(security)
        await self.db.flush()
        await self.db.refresh(security)
        return security

    async def get_by_ticker(
        self, ticker: str, exchange: str = "MOEX"
    ) -> Security | None:
        stmt = select(Security).where(
            Security.ticker == ticker,
            Security.exchange == exchange,
            Security.is_active.is_(True),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
