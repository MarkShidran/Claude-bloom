import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import CollectionResult
from app.collectors.moex.client import MOEXClient
from app.models.company import Company
from app.models.security import Security

logger = logging.getLogger(__name__)

SECURITY_TYPE_MAP = {
    "1": "common_stock",
    "2": "preferred_stock",
    "common_share": "common_stock",
    "preferred_share": "preferred_stock",
}


class MOEXSecurityCollector:
    """Syncs security metadata from MOEX ISS API."""

    def __init__(self, db: AsyncSession, client: MOEXClient | None = None):
        self.db = db
        self.client = client or MOEXClient()

    async def collect(self, secids: list[str] | None = None) -> CollectionResult:
        result = CollectionResult(source="moex_securities")

        try:
            if secids:
                for secid in secids:
                    await self._sync_security(secid, result)
            else:
                raw = await self.client.get_securities_list()
                for sec_data in raw:
                    secid = sec_data.get("SECID", "")
                    if not secid:
                        continue
                    await self._process_listing(sec_data, result)

            await self.db.flush()
        except Exception as e:
            result.errors.append(str(e))
            logger.exception("MOEX security collection failed")

        return result

    async def _sync_security(self, secid: str, result: CollectionResult):
        info = await self.client.get_security_info(secid)
        if not info:
            result.errors.append(f"No info found for {secid}")
            return

        shortname = info.get("SHORTNAME", secid)
        isin = info.get("ISIN") or None
        sec_type = SECURITY_TYPE_MAP.get(info.get("TYPE", ""), "common_stock")

        company = await self._get_or_create_company(shortname, secid)

        stmt = pg_insert(Security).values(
            company_id=company.id,
            ticker=secid,
            isin=isin,
            security_type=sec_type,
            currency="RUB",
            exchange="MOEX",
            moex_secid=secid,
            moex_boardid=info.get("PRIMARY_BOARDID"),
            is_active=True,
        ).on_conflict_do_update(
            index_elements=["ticker", "exchange"],
            set_={"isin": isin, "moex_boardid": info.get("PRIMARY_BOARDID"), "is_active": True},
        )
        await self.db.execute(stmt)
        result.records_processed += 1

    async def _process_listing(self, sec_data: dict, result: CollectionResult):
        secid = sec_data.get("SECID", "")
        shortname = sec_data.get("SHORTNAME", secid)
        isin = sec_data.get("ISIN") or None
        boardid = sec_data.get("BOARDID")

        if not boardid or boardid not in ("TQBR", "TQTF"):
            return

        company = await self._get_or_create_company(shortname, secid)

        stmt = pg_insert(Security).values(
            company_id=company.id,
            ticker=secid,
            isin=isin,
            security_type="common_stock",
            currency=sec_data.get("CURRENCYID", "SUR"),
            exchange="MOEX",
            moex_secid=secid,
            moex_boardid=boardid,
            lot_size=sec_data.get("LOTSIZE", 1),
            is_active=True,
        ).on_conflict_do_update(
            index_elements=["ticker", "exchange"],
            set_={
                "isin": isin,
                "moex_boardid": boardid,
                "lot_size": sec_data.get("LOTSIZE", 1),
            },
        )
        await self.db.execute(stmt)
        result.records_processed += 1

    async def _get_or_create_company(self, name: str, secid: str) -> Company:
        stmt = select(Company).where(Company.moex_secid == secid)
        row = await self.db.execute(stmt)
        company = row.scalar_one_or_none()

        if not company:
            stmt2 = select(Company).where(Company.ticker == secid)
            row2 = await self.db.execute(stmt2)
            company = row2.scalar_one_or_none()

        if not company:
            company = Company(name=name, ticker=secid, moex_secid=secid, country="RUS")
            self.db.add(company)
            await self.db.flush()

        return company
