import asyncio
import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class MOEXClient:
    """HTTP client for MOEX ISS API with pagination support."""

    BASE_URL = settings.MOEX_BASE_URL

    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self.client = http_client or httpx.AsyncClient(timeout=30.0)

    async def _get_json(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.BASE_URL}{path}.json"
        params = params or {}
        params.setdefault("iss.meta", "off")

        for attempt in range(3):
            try:
                resp = await self.client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                if attempt < 2:
                    wait = 2**attempt
                    logger.warning(f"MOEX API retry {attempt + 1}: {e}")
                    await asyncio.sleep(wait)
                    continue
                raise

    def _parse_block(self, data: dict, block_name: str) -> list[dict]:
        """Parse a MOEX ISS response block into a list of dicts."""
        block = data.get(block_name, {})
        columns = block.get("columns", [])
        rows = block.get("data", [])
        return [dict(zip(columns, row)) for row in rows]

    async def get_securities_list(
        self, market: str = "shares", engine: str = "stock"
    ) -> list[dict]:
        """Get all securities listed on MOEX."""
        all_securities = []
        start = 0

        while True:
            data = await self._get_json(
                f"/engines/{engine}/markets/{market}/securities",
                params={"start": start},
            )
            securities = self._parse_block(data, "securities")
            if not securities:
                break
            all_securities.extend(securities)
            start += len(securities)
            await asyncio.sleep(0.2)

        return all_securities

    async def get_security_info(self, secid: str) -> dict[str, Any]:
        """Get detailed info for a single security."""
        data = await self._get_json(f"/securities/{secid}")
        description = self._parse_block(data, "description")
        return {item.get("name", ""): item.get("value", "") for item in description}

    async def get_quote_history(
        self,
        secid: str,
        from_date: str | None = None,
        to_date: str | None = None,
        market: str = "shares",
        engine: str = "stock",
        board: str | None = None,
    ) -> list[dict]:
        """Get historical quotes for a security with pagination."""
        all_quotes: list[dict] = []
        start = 0

        board_path = f"/boards/{board}" if board else ""
        path = f"/history/engines/{engine}/markets/{market}{board_path}/securities/{secid}"

        params: dict[str, Any] = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["till"] = to_date

        while True:
            params["start"] = start
            data = await self._get_json(path, params=params)
            quotes = self._parse_block(data, "history")
            if not quotes:
                break
            all_quotes.extend(quotes)

            cursor = self._parse_block(data, "history.cursor")
            if cursor:
                total = cursor[0].get("TOTAL", 0)
                index = cursor[0].get("INDEX", 0)
                page_size = cursor[0].get("PAGESIZE", 100)
                if index + page_size >= total:
                    break
                start = index + page_size
            else:
                break

            await asyncio.sleep(0.2)

        return all_quotes

    async def search_security(self, query: str) -> list[dict]:
        """Search for securities by query string."""
        data = await self._get_json("/securities", params={"q": query, "limit": 20})
        return self._parse_block(data, "securities")
