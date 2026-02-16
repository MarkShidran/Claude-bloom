import io
import logging
import re
from decimal import Decimal, InvalidOperation

from openpyxl import load_workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import CollectionResult
from app.collectors.edisclosure.client import EDisclosureClient
from app.models.financial_statement import FinancialStatement
from app.models.statement_item import StatementItem
from app.models.statement_item_dict import StatementItemDict

logger = logging.getLogger(__name__)

# Mapping of common Russian financial terms to standardized codes
ITEM_NAME_PATTERNS = {
    r"итого\s+актив": "total_assets",
    r"нематериальн\w+\s+актив": "intangible_assets",
    r"основн\w+\s+средств": "fixed_assets",
    r"финансов\w+\s+вложени.*долгосроч": "lt_financial_investments",
    r"запас": "inventories",
    r"дебиторск\w+\s+задолженн": "accounts_receivable",
    r"денежн\w+\s+средств": "cash_and_equivalents",
    r"итого\s+оборотн": "total_current_assets",
    r"уставн\w+\s+капитал": "share_capital",
    r"нераспределённ\w+\s+прибыл": "retained_earnings",
    r"итого\s+капитал": "total_equity",
    r"долгосрочн\w+.*заёмн\w+\s+средств": "long_term_debt",
    r"краткосрочн\w+.*заёмн\w+\s+средств": "short_term_debt",
    r"кредиторск\w+\s+задолженн": "accounts_payable",
    r"итого\s+долгосрочн\w+\s+обязат": "total_lt_liabilities",
    r"итого\s+краткосрочн\w+\s+обязат": "total_st_liabilities",
    r"баланс|итого\s+пассив": "total_liabilities_and_equity",
    r"выручк": "revenue",
    r"себестоимость": "cost_of_sales",
    r"валов\w+\s+прибыл": "gross_profit",
    r"коммерческ\w+\s+расход": "selling_expenses",
    r"управленческ\w+\s+расход": "administrative_expenses",
    r"прибыл\w+.*от\s+продаж": "operating_income",
    r"прибыл\w+.*до\s+налогообл": "income_before_tax",
    r"налог\s+на\s+прибыл": "income_tax",
    r"чист\w+\s+прибыл": "net_income",
    r"амортизац": "depreciation_amortization",
    r"ebitda": "ebitda",
}


class EDisclosureParser:
    """Parses financial reports from e-disclosure.ru XLSX files."""

    def __init__(self, db: AsyncSession, client: EDisclosureClient | None = None):
        self.db = db
        self.client = client or EDisclosureClient()
        self._item_dict_cache: dict[str, int] | None = None

    async def _load_item_dict(self) -> dict[str, int]:
        """Load statement item dictionary into a code -> id mapping."""
        if self._item_dict_cache is not None:
            return self._item_dict_cache

        stmt = select(StatementItemDict)
        result = await self.db.execute(stmt)
        items = result.scalars().all()
        self._item_dict_cache = {item.code: item.id for item in items}
        return self._item_dict_cache

    def match_item_code(self, name: str) -> str | None:
        """Match a Russian financial term to a standardized code."""
        name_lower = name.lower().strip()
        for pattern, code in ITEM_NAME_PATTERNS.items():
            if re.search(pattern, name_lower):
                return code
        return None

    async def parse_xlsx(
        self,
        file_content: bytes,
        company_id: int,
        standard: str = "RSBU",
        source_url: str | None = None,
    ) -> CollectionResult:
        """Parse an XLSX financial report and store in database."""
        result = CollectionResult(source="edisclosure_parser")
        item_dict = await self._load_item_dict()

        try:
            wb = load_workbook(io.BytesIO(file_content), read_only=True, data_only=True)
        except Exception as e:
            result.errors.append(f"Failed to open workbook: {e}")
            return result

        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            statement_type = self._detect_statement_type(sheet_name)
            if not statement_type:
                continue

            parsed_items = self._extract_items_from_sheet(sheet)
            if not parsed_items:
                continue

            period_info = self._detect_period(sheet)
            if not period_info:
                result.errors.append(f"Could not detect period in sheet '{sheet_name}'")
                continue

            fs = FinancialStatement(
                company_id=company_id,
                standard=standard,
                statement_type=statement_type,
                period_type=period_info["period_type"],
                period_start=period_info["period_start"],
                period_end=period_info["period_end"],
                currency="RUB",
                unit_multiplier=period_info.get("unit_multiplier", 1000),
                source="edisclosure",
                source_url=source_url,
            )
            self.db.add(fs)
            await self.db.flush()

            for code, value in parsed_items.items():
                dict_id = item_dict.get(code)
                if not dict_id:
                    continue
                item = StatementItem(
                    statement_id=fs.id,
                    item_dict_id=dict_id,
                    value=value,
                )
                self.db.add(item)
                result.records_created += 1

            await self.db.flush()
            result.records_processed += 1

        wb.close()
        return result

    def _detect_statement_type(self, sheet_name: str) -> str | None:
        name = sheet_name.lower()
        if any(kw in name for kw in ["баланс", "balance", "актив", "пассив"]):
            return "balance_sheet"
        if any(kw in name for kw in ["прибыл", "убыт", "income", "p&l", "опу"]):
            return "income_statement"
        if any(kw in name for kw in ["движени", "денежн", "cash", "оддс"]):
            return "cash_flow"
        return None

    def _extract_items_from_sheet(self, sheet) -> dict[str, Decimal]:
        """Extract financial items from a worksheet."""
        items: dict[str, Decimal] = {}

        for row in sheet.iter_rows(min_row=1, values_only=False):
            name_cell = None
            value_cell = None

            for cell in row:
                if cell.value and isinstance(cell.value, str) and len(cell.value) > 3:
                    name_cell = cell
                elif cell.value and isinstance(cell.value, (int, float)):
                    value_cell = cell

            if name_cell and value_cell:
                code = self.match_item_code(str(name_cell.value))
                if code:
                    try:
                        items[code] = Decimal(str(value_cell.value))
                    except (InvalidOperation, ValueError):
                        pass

        return items

    def _detect_period(self, sheet) -> dict | None:
        """Attempt to detect the reporting period from the sheet."""
        import datetime

        for row in sheet.iter_rows(min_row=1, max_row=10, values_only=True):
            for cell in row:
                if not cell or not isinstance(cell, str):
                    continue
                # Look for date patterns like "31.12.2024" or "на 31 декабря 2024"
                date_match = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", str(cell))
                if date_match:
                    day, month, year = int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))
                    try:
                        period_end = datetime.date(year, month, day)
                        period_start = datetime.date(year, 1, 1)
                        period_type = "annual" if month == 12 else "quarterly"
                        return {
                            "period_start": period_start,
                            "period_end": period_end,
                            "period_type": period_type,
                            "unit_multiplier": 1000,
                        }
                    except ValueError:
                        continue

        return None
