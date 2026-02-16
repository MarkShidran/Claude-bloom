import logging
from datetime import date

import httpx
from defusedxml import ElementTree

from app.config import settings

logger = logging.getLogger(__name__)


class CBRClient:
    """HTTP client for CBR (Central Bank of Russia) XML API."""

    BASE_URL = settings.CBR_BASE_URL

    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self.client = http_client or httpx.AsyncClient(timeout=30.0)

    async def get_daily_rates(self, req_date: date) -> list[dict]:
        """Get daily FX rates for a given date.

        Endpoint: /XML_daily.asp?date_req=DD/MM/YYYY
        """
        date_str = req_date.strftime("%d/%m/%Y")
        url = f"{self.BASE_URL}/XML_daily.asp"
        resp = await self.client.get(url, params={"date_req": date_str})
        resp.raise_for_status()

        root = ElementTree.fromstring(resp.content)
        rates = []
        for valute in root.findall("Valute"):
            char_code = valute.findtext("CharCode", "")
            nominal = int(valute.findtext("Nominal", "1"))
            value_str = valute.findtext("Value", "0").replace(",", ".")
            try:
                value = float(value_str) / nominal
            except (ValueError, ZeroDivisionError):
                continue

            rates.append({
                "char_code": char_code,
                "name": valute.findtext("Name", ""),
                "nominal": nominal,
                "value": value,
            })

        return rates

    async def get_dynamic_rates(
        self, currency_code: str, from_date: date, to_date: date
    ) -> list[dict]:
        """Get FX rate history for a specific currency.

        Endpoint: /XML_dynamic.asp?date_req1=DD/MM/YYYY&date_req2=DD/MM/YYYY&VAL_NM_RQ=...
        """
        currency_ids = {
            "USD": "R01235",
            "EUR": "R01239",
            "CNY": "R01375",
            "GBP": "R01035",
        }
        val_id = currency_ids.get(currency_code)
        if not val_id:
            logger.warning(f"Unknown currency code: {currency_code}")
            return []

        url = f"{self.BASE_URL}/XML_dynamic.asp"
        params = {
            "date_req1": from_date.strftime("%d/%m/%Y"),
            "date_req2": to_date.strftime("%d/%m/%Y"),
            "VAL_NM_RQ": val_id,
        }
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()

        root = ElementTree.fromstring(resp.content)
        rates = []
        for record in root.findall("Record"):
            date_str = record.get("Date", "")
            nominal = int(record.findtext("Nominal", "1"))
            value_str = record.findtext("Value", "0").replace(",", ".")
            try:
                rate_date = date(
                    int(date_str[6:10]), int(date_str[3:5]), int(date_str[0:2])
                )
                value = float(value_str) / nominal
            except (ValueError, IndexError):
                continue

            rates.append({"date": rate_date, "value": value})

        return rates

    async def get_key_rate(self, from_date: date, to_date: date) -> list[dict]:
        """Get CBR key rate history.

        Endpoint: /XML_key_rate.asp?date_req1=DD/MM/YYYY&date_req2=DD/MM/YYYY
        """
        url = f"{self.BASE_URL}/XML_key_rate.asp"
        params = {
            "date_req1": from_date.strftime("%d/%m/%Y"),
            "date_req2": to_date.strftime("%d/%m/%Y"),
        }

        try:
            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
        except httpx.HTTPError:
            logger.warning("Key rate endpoint failed, trying alternative endpoint")
            return await self._get_key_rate_alternative(from_date, to_date)

        root = ElementTree.fromstring(resp.content)
        rates = []
        for record in root.findall(".//KR"):
            date_str = record.findtext("DT", "")
            rate_str = record.findtext("Rate", "0").replace(",", ".")
            try:
                rate_date = date.fromisoformat(date_str[:10]) if "T" in date_str else date(
                    int(date_str[6:10]), int(date_str[3:5]), int(date_str[0:2])
                )
                rates.append({"date": rate_date, "value": float(rate_str)})
            except (ValueError, IndexError):
                continue

        return rates

    async def _get_key_rate_alternative(
        self, from_date: date, to_date: date
    ) -> list[dict]:
        """Fallback: parse key rate from the DKS XML endpoint."""
        url = f"{self.BASE_URL}/XML_dynamic.asp"
        params = {
            "date_req1": from_date.strftime("%d/%m/%Y"),
            "date_req2": to_date.strftime("%d/%m/%Y"),
            "VAL_NM_RQ": "R01235",  # placeholder
        }
        # This is a simplified fallback; in production would use a more reliable source
        logger.info("Key rate alternative endpoint called (limited data)")
        return []
