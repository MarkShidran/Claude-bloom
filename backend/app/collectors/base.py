import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@dataclass
class CollectionResult:
    source: str = ""
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


class BaseCollector(ABC):
    def __init__(self, db: AsyncSession, http_client: httpx.AsyncClient | None = None):
        self.db = db
        self.client = http_client or httpx.AsyncClient(timeout=30.0)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def collect(self, **kwargs) -> CollectionResult:
        ...

    async def _request(self, url: str, **kwargs) -> httpx.Response:
        for attempt in range(3):
            try:
                resp = await self.client.get(url, **kwargs)
                resp.raise_for_status()
                return resp
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait = 2**attempt
                    self.logger.warning(f"Rate limited, waiting {wait}s: {url}")
                    await asyncio.sleep(wait)
                    continue
                self.logger.error(f"HTTP error {e.response.status_code}: {url}")
                raise
            except httpx.RequestError as e:
                if attempt < 2:
                    wait = 2**attempt
                    self.logger.warning(f"Request error, retry in {wait}s: {e}")
                    await asyncio.sleep(wait)
                    continue
                raise
        raise RuntimeError(f"Failed after 3 retries: {url}")
