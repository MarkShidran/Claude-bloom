"""Seed script for initial data population.

Run with: python -m app.scripts.seed_data
"""

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import AsyncSessionLocal
from app.models.company import Company
from app.models.security import Security
from app.models.statement_item_dict import StatementItemDict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Major Russian public companies for initial seeding
SEED_COMPANIES = [
    {"name": "Сбербанк", "name_en": "Sberbank", "ticker": "SBER", "inn": "7707083893", "sector": "Финансы", "industry": "Банки", "moex_secid": "SBER", "edisclosure_id": 3043},
    {"name": "Газпром", "name_en": "Gazprom", "ticker": "GAZP", "inn": "7736050003", "sector": "Энергетика", "industry": "Нефть и газ", "moex_secid": "GAZP", "edisclosure_id": 934},
    {"name": "Лукойл", "name_en": "Lukoil", "ticker": "LKOH", "inn": "7708004767", "sector": "Энергетика", "industry": "Нефть и газ", "moex_secid": "LKOH", "edisclosure_id": 1724},
    {"name": "Роснефть", "name_en": "Rosneft", "ticker": "ROSN", "inn": "7706107510", "sector": "Энергетика", "industry": "Нефть и газ", "moex_secid": "ROSN", "edisclosure_id": 7721},
    {"name": "Норильский никель", "name_en": "Norilsk Nickel", "ticker": "GMKN", "inn": "8401005730", "sector": "Материалы", "industry": "Металлургия", "moex_secid": "GMKN", "edisclosure_id": 564},
    {"name": "Яндекс", "name_en": "Yandex", "ticker": "YDEX", "inn": "7736207543", "sector": "Технологии", "industry": "Интернет", "moex_secid": "YDEX"},
    {"name": "ВТБ", "name_en": "VTB", "ticker": "VTBR", "inn": "7702070139", "sector": "Финансы", "industry": "Банки", "moex_secid": "VTBR", "edisclosure_id": 1397},
    {"name": "Татнефть", "name_en": "Tatneft", "ticker": "TATN", "inn": "1644003838", "sector": "Энергетика", "industry": "Нефть и газ", "moex_secid": "TATN", "edisclosure_id": 484},
    {"name": "Сургутнефтегаз", "name_en": "Surgutneftegas", "ticker": "SNGS", "inn": "8602060555", "sector": "Энергетика", "industry": "Нефть и газ", "moex_secid": "SNGS", "edisclosure_id": 440},
    {"name": "Северсталь", "name_en": "Severstal", "ticker": "CHMF", "inn": "3528000597", "sector": "Материалы", "industry": "Металлургия", "moex_secid": "CHMF", "edisclosure_id": 2423},
    {"name": "НЛМК", "name_en": "NLMK", "ticker": "NLMK", "inn": "4823006703", "sector": "Материалы", "industry": "Металлургия", "moex_secid": "NLMK", "edisclosure_id": 1814},
    {"name": "Полюс", "name_en": "Polyus", "ticker": "PLZL", "inn": "7703389295", "sector": "Материалы", "industry": "Золотодобыча", "moex_secid": "PLZL"},
    {"name": "Магнит", "name_en": "Magnit", "ticker": "MGNT", "inn": "2309085638", "sector": "Потребительский", "industry": "Розничная торговля", "moex_secid": "MGNT", "edisclosure_id": 7498},
    {"name": "МТС", "name_en": "MTS", "ticker": "MTSS", "inn": "7740000076", "sector": "Телекоммуникации", "industry": "Мобильная связь", "moex_secid": "MTSS", "edisclosure_id": 7828},
    {"name": "НОВАТЭК", "name_en": "Novatek", "ticker": "NVTK", "inn": "7224020694", "sector": "Энергетика", "industry": "Нефть и газ", "moex_secid": "NVTK", "edisclosure_id": 2410},
]

# Statement item dictionary entries for RSBU and IFRS
STATEMENT_ITEMS = [
    # Balance Sheet - Assets
    {"code": "intangible_assets", "name_ru": "Нематериальные активы", "name_en": "Intangible assets", "statement_type": "balance_sheet", "parent_code": "total_noncurrent_assets", "sort_order": 10},
    {"code": "fixed_assets", "name_ru": "Основные средства", "name_en": "Fixed assets", "statement_type": "balance_sheet", "parent_code": "total_noncurrent_assets", "sort_order": 20},
    {"code": "lt_financial_investments", "name_ru": "Финансовые вложения (долгосрочные)", "name_en": "Long-term financial investments", "statement_type": "balance_sheet", "parent_code": "total_noncurrent_assets", "sort_order": 30},
    {"code": "deferred_tax_assets", "name_ru": "Отложенные налоговые активы", "name_en": "Deferred tax assets", "statement_type": "balance_sheet", "parent_code": "total_noncurrent_assets", "sort_order": 40},
    {"code": "other_noncurrent_assets", "name_ru": "Прочие внеоборотные активы", "name_en": "Other non-current assets", "statement_type": "balance_sheet", "parent_code": "total_noncurrent_assets", "sort_order": 50},
    {"code": "total_noncurrent_assets", "name_ru": "Итого внеоборотные активы", "name_en": "Total non-current assets", "statement_type": "balance_sheet", "parent_code": "total_assets", "sort_order": 60},
    {"code": "inventories", "name_ru": "Запасы", "name_en": "Inventories", "statement_type": "balance_sheet", "parent_code": "total_current_assets", "sort_order": 70},
    {"code": "accounts_receivable", "name_ru": "Дебиторская задолженность", "name_en": "Accounts receivable", "statement_type": "balance_sheet", "parent_code": "total_current_assets", "sort_order": 80},
    {"code": "st_financial_investments", "name_ru": "Финансовые вложения (краткосрочные)", "name_en": "Short-term financial investments", "statement_type": "balance_sheet", "parent_code": "total_current_assets", "sort_order": 90},
    {"code": "cash_and_equivalents", "name_ru": "Денежные средства и эквиваленты", "name_en": "Cash and cash equivalents", "statement_type": "balance_sheet", "parent_code": "total_current_assets", "sort_order": 100},
    {"code": "other_current_assets", "name_ru": "Прочие оборотные активы", "name_en": "Other current assets", "statement_type": "balance_sheet", "parent_code": "total_current_assets", "sort_order": 110},
    {"code": "total_current_assets", "name_ru": "Итого оборотные активы", "name_en": "Total current assets", "statement_type": "balance_sheet", "parent_code": "total_assets", "sort_order": 120},
    {"code": "total_assets", "name_ru": "ИТОГО АКТИВЫ", "name_en": "TOTAL ASSETS", "statement_type": "balance_sheet", "sort_order": 130},

    # Balance Sheet - Equity
    {"code": "share_capital", "name_ru": "Уставный капитал", "name_en": "Share capital", "statement_type": "balance_sheet", "parent_code": "total_equity", "sort_order": 140},
    {"code": "additional_capital", "name_ru": "Добавочный капитал", "name_en": "Additional paid-in capital", "statement_type": "balance_sheet", "parent_code": "total_equity", "sort_order": 150},
    {"code": "reserve_capital", "name_ru": "Резервный капитал", "name_en": "Reserve capital", "statement_type": "balance_sheet", "parent_code": "total_equity", "sort_order": 160},
    {"code": "retained_earnings", "name_ru": "Нераспределённая прибыль", "name_en": "Retained earnings", "statement_type": "balance_sheet", "parent_code": "total_equity", "sort_order": 170},
    {"code": "total_equity", "name_ru": "ИТОГО КАПИТАЛ", "name_en": "TOTAL EQUITY", "statement_type": "balance_sheet", "sort_order": 180},

    # Balance Sheet - Liabilities
    {"code": "long_term_debt", "name_ru": "Долгосрочные заёмные средства", "name_en": "Long-term borrowings", "statement_type": "balance_sheet", "parent_code": "total_lt_liabilities", "sort_order": 190},
    {"code": "deferred_tax_liabilities", "name_ru": "Отложенные налоговые обязательства", "name_en": "Deferred tax liabilities", "statement_type": "balance_sheet", "parent_code": "total_lt_liabilities", "sort_order": 200},
    {"code": "other_lt_liabilities", "name_ru": "Прочие долгосрочные обязательства", "name_en": "Other long-term liabilities", "statement_type": "balance_sheet", "parent_code": "total_lt_liabilities", "sort_order": 210},
    {"code": "total_lt_liabilities", "name_ru": "Итого долгосрочные обязательства", "name_en": "Total long-term liabilities", "statement_type": "balance_sheet", "sort_order": 220},
    {"code": "short_term_debt", "name_ru": "Краткосрочные заёмные средства", "name_en": "Short-term borrowings", "statement_type": "balance_sheet", "parent_code": "total_st_liabilities", "sort_order": 230},
    {"code": "accounts_payable", "name_ru": "Кредиторская задолженность", "name_en": "Accounts payable", "statement_type": "balance_sheet", "parent_code": "total_st_liabilities", "sort_order": 240},
    {"code": "other_st_liabilities", "name_ru": "Прочие краткосрочные обязательства", "name_en": "Other short-term liabilities", "statement_type": "balance_sheet", "parent_code": "total_st_liabilities", "sort_order": 250},
    {"code": "total_st_liabilities", "name_ru": "Итого краткосрочные обязательства", "name_en": "Total short-term liabilities", "statement_type": "balance_sheet", "sort_order": 260},
    {"code": "total_liabilities", "name_ru": "ИТОГО ОБЯЗАТЕЛЬСТВА", "name_en": "TOTAL LIABILITIES", "statement_type": "balance_sheet", "sort_order": 270},
    {"code": "total_liabilities_and_equity", "name_ru": "ИТОГО ПАССИВЫ", "name_en": "TOTAL LIABILITIES AND EQUITY", "statement_type": "balance_sheet", "sort_order": 280},

    # Income Statement
    {"code": "revenue", "name_ru": "Выручка", "name_en": "Revenue", "statement_type": "income_statement", "sort_order": 10},
    {"code": "cost_of_sales", "name_ru": "Себестоимость продаж", "name_en": "Cost of sales", "statement_type": "income_statement", "sort_order": 20},
    {"code": "gross_profit", "name_ru": "Валовая прибыль (убыток)", "name_en": "Gross profit", "statement_type": "income_statement", "sort_order": 30, "is_calculated": True, "formula": "revenue - cost_of_sales"},
    {"code": "selling_expenses", "name_ru": "Коммерческие расходы", "name_en": "Selling expenses", "statement_type": "income_statement", "sort_order": 40},
    {"code": "administrative_expenses", "name_ru": "Управленческие расходы", "name_en": "Administrative expenses", "statement_type": "income_statement", "sort_order": 50},
    {"code": "operating_income", "name_ru": "Прибыль (убыток) от продаж", "name_en": "Operating income", "statement_type": "income_statement", "sort_order": 60},
    {"code": "interest_income", "name_ru": "Проценты к получению", "name_en": "Interest income", "statement_type": "income_statement", "sort_order": 70},
    {"code": "interest_expense", "name_ru": "Проценты к уплате", "name_en": "Interest expense", "statement_type": "income_statement", "sort_order": 80},
    {"code": "other_income", "name_ru": "Прочие доходы", "name_en": "Other income", "statement_type": "income_statement", "sort_order": 90},
    {"code": "other_expenses", "name_ru": "Прочие расходы", "name_en": "Other expenses", "statement_type": "income_statement", "sort_order": 100},
    {"code": "income_before_tax", "name_ru": "Прибыль (убыток) до налогообложения", "name_en": "Income before tax", "statement_type": "income_statement", "sort_order": 110},
    {"code": "income_tax", "name_ru": "Налог на прибыль", "name_en": "Income tax expense", "statement_type": "income_statement", "sort_order": 120},
    {"code": "net_income", "name_ru": "Чистая прибыль (убыток)", "name_en": "Net income", "statement_type": "income_statement", "sort_order": 130},
    {"code": "depreciation_amortization", "name_ru": "Амортизация", "name_en": "Depreciation & amortization", "statement_type": "income_statement", "sort_order": 135},
    {"code": "ebitda", "name_ru": "EBITDA", "name_en": "EBITDA", "statement_type": "income_statement", "sort_order": 140, "is_calculated": True, "formula": "operating_income + depreciation_amortization"},

    # Cash Flow Statement
    {"code": "cf_operating", "name_ru": "Денежные потоки от текущих операций", "name_en": "Cash from operating activities", "statement_type": "cash_flow", "sort_order": 10},
    {"code": "cf_operating_receipts", "name_ru": "Поступления от продажи продукции", "name_en": "Receipts from sales", "statement_type": "cash_flow", "parent_code": "cf_operating", "sort_order": 20},
    {"code": "cf_operating_payments", "name_ru": "Платежи поставщикам и подрядчикам", "name_en": "Payments to suppliers", "statement_type": "cash_flow", "parent_code": "cf_operating", "sort_order": 30},
    {"code": "cf_operating_wages", "name_ru": "Расходы на оплату труда", "name_en": "Wage payments", "statement_type": "cash_flow", "parent_code": "cf_operating", "sort_order": 40},
    {"code": "cf_operating_taxes", "name_ru": "Налоги уплаченные", "name_en": "Tax payments", "statement_type": "cash_flow", "parent_code": "cf_operating", "sort_order": 50},
    {"code": "cf_operating_net", "name_ru": "Чистые денежные потоки от текущих операций", "name_en": "Net operating cash flow", "statement_type": "cash_flow", "sort_order": 60},
    {"code": "cf_investing", "name_ru": "Денежные потоки от инвестиционных операций", "name_en": "Cash from investing activities", "statement_type": "cash_flow", "sort_order": 70},
    {"code": "cf_capex", "name_ru": "Приобретение основных средств", "name_en": "Capital expenditures", "statement_type": "cash_flow", "parent_code": "cf_investing", "sort_order": 80},
    {"code": "cf_investing_net", "name_ru": "Чистые денежные потоки от инвестиционных операций", "name_en": "Net investing cash flow", "statement_type": "cash_flow", "sort_order": 90},
    {"code": "cf_financing", "name_ru": "Денежные потоки от финансовых операций", "name_en": "Cash from financing activities", "statement_type": "cash_flow", "sort_order": 100},
    {"code": "cf_debt_proceeds", "name_ru": "Получение кредитов и займов", "name_en": "Debt proceeds", "statement_type": "cash_flow", "parent_code": "cf_financing", "sort_order": 110},
    {"code": "cf_debt_repayment", "name_ru": "Погашение кредитов и займов", "name_en": "Debt repayment", "statement_type": "cash_flow", "parent_code": "cf_financing", "sort_order": 120},
    {"code": "cf_dividends_paid", "name_ru": "Дивиденды уплаченные", "name_en": "Dividends paid", "statement_type": "cash_flow", "parent_code": "cf_financing", "sort_order": 130},
    {"code": "cf_financing_net", "name_ru": "Чистые денежные потоки от финансовых операций", "name_en": "Net financing cash flow", "statement_type": "cash_flow", "sort_order": 140},
    {"code": "cf_net_change", "name_ru": "Чистое изменение денежных средств", "name_en": "Net change in cash", "statement_type": "cash_flow", "sort_order": 150},
    {"code": "cf_opening_balance", "name_ru": "Денежные средства на начало периода", "name_en": "Cash at beginning of period", "statement_type": "cash_flow", "sort_order": 160},
    {"code": "cf_closing_balance", "name_ru": "Денежные средства на конец периода", "name_en": "Cash at end of period", "statement_type": "cash_flow", "sort_order": 170},

    # Additional derived items
    {"code": "total_debt", "name_ru": "Общий долг", "name_en": "Total debt", "statement_type": "balance_sheet", "sort_order": 285, "is_calculated": True, "formula": "long_term_debt + short_term_debt"},
    {"code": "net_debt", "name_ru": "Чистый долг", "name_en": "Net debt", "statement_type": "balance_sheet", "sort_order": 286, "is_calculated": True, "formula": "total_debt - cash_and_equivalents"},
]


async def seed_companies(db):
    """Seed the database with major Russian public companies."""
    logger.info("Seeding companies...")
    for company_data in SEED_COMPANIES:
        stmt = pg_insert(Company).values(
            **company_data, country="RUS", is_active=True
        ).on_conflict_do_update(
            index_elements=["inn"],
            set_={k: v for k, v in company_data.items() if k != "inn"},
        )
        await db.execute(stmt)

    await db.flush()

    # Create securities for each company
    result = await db.execute(select(Company).where(Company.is_active.is_(True)))
    companies = result.scalars().all()

    for company in companies:
        if company.moex_secid:
            stmt = pg_insert(Security).values(
                company_id=company.id,
                ticker=company.ticker or company.moex_secid,
                security_type="common_stock",
                currency="RUB",
                exchange="MOEX",
                moex_secid=company.moex_secid,
                moex_boardid="TQBR",
                is_active=True,
            ).on_conflict_do_update(
                index_elements=["ticker", "exchange"],
                set_={"moex_secid": company.moex_secid, "moex_boardid": "TQBR"},
            )
            await db.execute(stmt)

    await db.flush()
    logger.info(f"Seeded {len(SEED_COMPANIES)} companies with securities")


async def seed_statement_items(db):
    """Seed the statement item dictionary."""
    logger.info("Seeding statement item dictionary...")
    for item_data in STATEMENT_ITEMS:
        stmt = pg_insert(StatementItemDict).values(
            **item_data
        ).on_conflict_do_update(
            index_elements=["code"],
            set_={k: v for k, v in item_data.items() if k != "code"},
        )
        await db.execute(stmt)

    await db.flush()
    logger.info(f"Seeded {len(STATEMENT_ITEMS)} statement item definitions")


async def main():
    """Run all seed operations."""
    logger.info("Starting database seeding...")
    async with AsyncSessionLocal() as db:
        try:
            await seed_statement_items(db)
            await seed_companies(db)
            await db.commit()
            logger.info("Database seeding completed successfully")
        except Exception:
            await db.rollback()
            logger.exception("Database seeding failed")
            raise


if __name__ == "__main__":
    asyncio.run(main())
