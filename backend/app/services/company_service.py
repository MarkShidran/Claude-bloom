from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company import Company
from app.schemas.common import PaginatedResponse
from app.schemas.company import CompanyCreate, CompanyOut, CompanyUpdate


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_companies(
        self,
        search: str | None = None,
        sector: str | None = None,
        country: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> PaginatedResponse[CompanyOut]:
        stmt = select(Company).where(Company.is_active.is_(True))
        count_stmt = select(func.count(Company.id)).where(Company.is_active.is_(True))

        if search:
            pattern = f"%{search}%"
            search_filter = or_(
                Company.name.ilike(pattern),
                Company.ticker.ilike(pattern),
            )
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        if sector:
            stmt = stmt.where(Company.sector == sector)
            count_stmt = count_stmt.where(Company.sector == sector)

        if country:
            stmt = stmt.where(Company.country == country)
            count_stmt = count_stmt.where(Company.country == country)

        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(Company.name).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        companies = result.scalars().all()

        return PaginatedResponse[CompanyOut](
            items=[CompanyOut.model_validate(c) for c in companies],
            total=total,
            offset=offset,
            limit=limit,
        )

    async def get_company(self, company_id: int) -> Company | None:
        stmt = (
            select(Company)
            .where(Company.id == company_id)
            .options(selectinload(Company.securities))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_company(self, data: CompanyCreate) -> Company:
        company = Company(**data.model_dump())
        self.db.add(company)
        await self.db.flush()
        await self.db.refresh(company)
        return company

    async def update_company(
        self, company_id: int, data: CompanyUpdate
    ) -> Company | None:
        company = await self.get_company(company_id)
        if company is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)

        await self.db.flush()
        await self.db.refresh(company)
        return company

    async def search_companies(
        self, query: str, limit: int = 20
    ) -> list[CompanyOut]:
        pattern = f"%{query}%"
        stmt = (
            select(Company)
            .where(
                Company.is_active.is_(True),
                or_(
                    Company.name.ilike(pattern),
                    Company.ticker.ilike(pattern),
                    Company.inn.ilike(pattern),
                ),
            )
            .order_by(Company.name)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        companies = result.scalars().all()
        return [CompanyOut.model_validate(c) for c in companies]
