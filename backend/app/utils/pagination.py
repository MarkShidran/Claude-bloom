from sqlalchemy import Select, func, select


async def paginate(db, query: Select, offset: int = 0, limit: int = 50) -> tuple[list, int]:
    """Execute a paginated query, returning (items, total_count)."""
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    result = await db.execute(query.offset(offset).limit(limit))
    items = result.scalars().all()

    return items, total
