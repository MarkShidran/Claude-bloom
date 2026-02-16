import logging
import re
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)


class EDisclosureClient:
    """HTTP client for e-disclosure.ru scraping."""

    BASE_URL = settings.EDISCLOSURE_BASE_URL

    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self.client = http_client or httpx.AsyncClient(
            timeout=60.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "ru-RU,ru;q=0.9",
            },
        )

    async def get_filing_list(
        self, edisclosure_id: int, report_type: int = 3
    ) -> list[dict]:
        """Get list of financial report filings.

        Args:
            edisclosure_id: Company ID on e-disclosure.ru
            report_type: 3=RSBU, 4=IFRS
        """
        url = f"{self.BASE_URL}/portal/files.aspx"
        params = {"id": edisclosure_id, "type": report_type}

        try:
            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch filing list for {edisclosure_id}: {e}")
            return []

        soup = BeautifulSoup(resp.text, "lxml")
        filings = []

        for row in soup.select("table.files_table tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            link = row.find("a", href=True)
            if not link:
                continue

            href = link.get("href", "")
            name = link.get_text(strip=True)
            date_text = cells[-1].get_text(strip=True) if cells else ""

            if not any(ext in href.lower() for ext in [".xlsx", ".xls"]):
                continue

            filings.append({
                "name": name,
                "url": urljoin(self.BASE_URL, href),
                "date": date_text,
            })

        return filings

    async def download_file(self, url: str) -> bytes:
        """Download a file from e-disclosure.ru."""
        resp = await self.client.get(url)
        resp.raise_for_status()
        return resp.content
