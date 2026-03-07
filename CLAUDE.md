# CLAUDE.md — Claude Bloom Financial Analytics Platform

## Project Overview

Web platform replacing Bloomberg Terminal for a PE fund. 25-35 analysts working with Russian private companies. Investment horizon 3-7 years.

**Branch**: `claude/financial-analytics-platform-WBEcz`
**Repo**: `MarkShidran/Claude-bloom`

---

## What Has Been Built (Stage 1 — Complete)

### Tech Stack
- **Backend**: Python 3.12, FastAPI (async), SQLAlchemy 2.0 async + asyncpg, Alembic, APScheduler
- **Frontend**: React 18, TypeScript, Mantine v7, AG Grid Community, Plotly.js, TanStack Query, Zustand, Axios
- **Database**: PostgreSQL 16
- **Infrastructure**: Docker Compose (3 containers: db, backend, frontend)

### Directory Structure
```
Claude-bloom/
├── docker-compose.yml
├── Makefile                        # make up/down/migrate/seed/test/lint
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml              # Python deps
│   ├── alembic.ini + alembic/     # Async migrations
│   └── app/
│       ├── main.py                 # FastAPI app, lifespan (starts APScheduler)
│       ├── config.py               # pydantic-settings (reads .env)
│       ├── database.py             # async engine, AsyncSessionLocal, Base
│       ├── dependencies.py         # get_db() Depends()
│       ├── exceptions.py           # BloomException, NotFoundError, CollectionError
│       ├── models/                 # SQLAlchemy ORM (10 models)
│       ├── schemas/                # Pydantic v2 schemas
│       ├── api/v1/                 # FastAPI routers
│       ├── services/               # Business logic layer
│       ├── collectors/             # Data ingestion (MOEX, CBR, e-disclosure, Excel)
│       ├── tasks/                  # APScheduler setup + job definitions
│       ├── scripts/seed_data.py    # Initial data seeding
│       └── utils/                  # pagination.py, date_utils.py
└── frontend/
    ├── Dockerfile (multi-stage dev/build/prod)
    ├── nginx.conf
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── main.tsx                # MantineProvider + QueryClientProvider
        ├── App.tsx                 # React Router routes
        ├── api/                    # Axios API functions
        ├── hooks/                  # TanStack Query hooks
        ├── types/                  # TypeScript interfaces
        ├── store/uiStore.ts        # Zustand (sidebar toggle, favorites)
        ├── components/
        │   ├── layout/             # AppLayout, Sidebar, Header
        │   ├── common/             # DataGrid (AG Grid wrapper), Chart (Plotly wrapper), ExportButton, etc.
        │   ├── companies/          # CompanyList, CompanyCard, CompanySearch
        │   ├── financials/         # FinancialTable, PeriodComparison
        │   ├── quotes/             # QuoteChart (candlestick/line), QuoteStats
        │   ├── multiples/          # MultiplesTable, MultiplesChart
        │   └── macro/              # MacroDashboard
        ├── pages/
        │   ├── CompaniesPage.tsx
        │   ├── CompanyDetailPage.tsx  # 4 tabs: Overview, Financials, Quotes, Multiples
        │   ├── MacroPage.tsx
        │   ├── MultiplesPage.tsx      # Screening view
        │   └── PeerGroupsPage.tsx     # Stub — Stage 2
        └── styles/                 # global.css, ag-grid-theme.css
```

### Database Schema (10 tables)
- **companies** — central entity (name, ticker, inn, sector, country, moex_secid, edisclosure_id)
- **securities** — linked to company (ticker, isin, security_type, exchange, moex_secid, moex_boardid)
- **quotes** — partitioned by year (trade_date, OHLCV, value, num_trades)
- **financial_statements** — (standard: RSBU/IFRS/US_GAAP, statement_type, period_start/end, currency, unit_multiplier)
- **statement_item_dict** — reference: code, name_ru, name_en, parent_code, sort_order, is_calculated, formula
- **statement_items** — actual values (statement_id, item_dict_id, value)
- **multiples** — calculated (pe, ev_ebitda, ev_sales, pb, ps, roe, roa, debt_ebitda, market_cap, ev)
- **macro_indicators** — partitioned by year (indicator_code, date, value, source)
- **peer_groups** — (name, formation_type, auto_criteria JSONB) — schema exists, Stage 2
- **peer_group_members** — (peer_group_id, company_id) — Stage 2

PostgreSQL extension: `pg_trgm` (trigram fuzzy search on company name)

### API Endpoints (all under `/api/v1/`)
```
GET  /health
GET  /companies                    # ?search=&sector=&country=&offset=&limit=
GET  /companies/search             # ?q=&limit=
GET  /companies/{id}
POST /companies
PUT  /companies/{id}
GET  /companies/{id}/financials    # ?standard=&statement_type=&period_type=
POST /companies/{id}/financials/upload  # Excel file upload
GET  /financials/{id}/items
GET  /financials/compare           # ?company_id=&standard=&statement_type=&period_ends=
GET  /securities/{id}
GET  /securities/company/{id}
POST /securities
GET  /securities/{id}/quotes       # ?from_date=&to_date=&interval=day/week/month
GET  /securities/{id}/quotes/stats
GET  /companies/{id}/multiples     # ?from_date=&to_date=
GET  /multiples/screen             # ?sector=&sort_by=&sort_dir=&offset=&limit=
GET  /peergroups                   # Stage 2 stub
POST /peergroups
GET  /peergroups/{id}
DELETE /peergroups/{id}
POST /risk/beta                    # Stage 2 stub
POST /risk/wacc                    # Stage 2 stub
GET  /macro/fx                     # ?from_date=&to_date=&currencies=USD_RUB,EUR_RUB
GET  /macro/rates                  # CBR key rate
GET  /macro/latest
POST /export/financials            # body: {company_id, statement_ids}
POST /export/multiples             # body: {company_id}
POST /export/quotes                # body: {security_id, from_date, to_date}
GET  /export/template/financials   # Download upload template
```
API docs at `http://localhost:8000/api/docs`

### Data Collectors
- **MOEX ISS** (`collectors/moex/`): Securities metadata sync (weekly) + daily quote collection with pagination via `history.cursor`. Endpoint: `/iss/history/engines/stock/markets/shares/securities/{secid}.json`
- **CBR** (`collectors/cbr/`): Daily FX rates via XML (`/scripts/XML_daily.asp`) + key rate history (`/scripts/XML_key_rate.asp`). Currencies: USD, EUR, CNY, GBP vs RUB. Indicator codes: `USD_RUB`, `EUR_RUB`, etc., `CBR_KEY_RATE`
- **e-disclosure** (`collectors/edisclosure/`): Scrapes XLSX reports from `https://e-disclosure.ru/portal/files.aspx?id={id}&type=3` (RSBU) / `type=4` (IFRS). Parses with openpyxl using Russian term → code mapping dictionary.
- **Excel upload** (`collectors/excel/template.py`): Generate/parse structured upload template. Companies with non-standard reports use this for manual entry.

### Scheduled Jobs (APScheduler, in-process)
| Job | Cron | What it does |
|-----|------|-------------|
| `collect_moex_quotes` | `0 19 * * 1-5` | Daily MOEX quotes |
| `collect_cbr_fx_rates` | `0 15 * * *` | Daily CBR FX |
| `collect_cbr_macro` | `0 10 1 * *` | Monthly key rate |
| `recalculate_multiples` | `30 19 * * 1-5` | Recalculate all multiples |

### Seed Data
Running `make seed` populates:
- **15 companies**: SBER, GAZP, LKOH, ROSN, GMKN, YDEX, VTBR, TATN, SNGS, CHMF, NLMK, PLZL, MGNT, MTSS, NVTK
- **~50 statement_item_dict entries**: Standard RSBU/IFRS lines for balance sheet, income statement, cash flow (with hierarchy via parent_code)

### Key Patterns & Conventions
- All DB access is **async** — use `await db.execute(select(...))`, `result.scalars().all()`, `result.scalar_one_or_none()`
- **Eager loading** required for relationships: use `selectinload()` or `joinedload()` (no lazy loading with async SQLAlchemy)
- Service layer: `XxxService(db: AsyncSession)` — each endpoint instantiates `service = XxxService(db)`, never import services into each other at module level (use local imports in methods to avoid circular deps)
- Schemas use `model_config = {"from_attributes": True}` for ORM model serialization
- All list endpoints return `PaginatedResponse[T]` with `items`, `total`, `offset`, `limit`
- Upserts use `pg_insert(...).on_conflict_do_update(...)` for idempotent data collection
- Export endpoints return `StreamingResponse` with `media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"`
- **No authentication** in Stage 1 (internal network / VPN). Add JWT in later stage.

---

## What Needs to Be Built

### Stage 2 — Peer Groups & Advanced Analytics

#### Peer Groups Module
- `services/peer_group_service.py` — CRUD + auto-formation by sector/criteria
- `api/v1/peer_groups.py` — currently stub, implement fully:
  - `GET /peergroups/{id}/compare` — comparison table with stats (median, mean, quartiles)
  - `GET /peergroups/{id}/export` — Excel export of comparison
- Frontend `PeerGroupsPage.tsx` — search/add companies, comparison table, visualization

#### Beta Calculation
- `services/calculation/beta.py` — levered/unlevered beta, volatility, correlation, regression
  - Use quotes data + index data (IMOEX)
  - Parameters: period (1/2/3/5 years), frequency (daily/weekly/monthly), index
  - Hamada equation for un/re-levering: `β_unlevered = β_levered / (1 + (1-tax_rate) * D/E)`
- `api/v1/risk.py` — implement `POST /risk/beta` endpoint (currently returns stub)
- Frontend: Beta analysis tab on CompanyDetailPage

#### WACC Calculator
- `services/calculation/wacc.py`
  - Inputs: risk-free rate (from CBR key rate), equity risk premium, beta, cost of debt, tax rate, D/E ratio
  - Auto-fill from platform data where available
  - Dynamic WACC history by quarter
- `api/v1/risk.py` — implement `POST /risk/wacc` and `GET /companies/{id}/wacc/history`
- Frontend: Dedicated WACC calculator page

#### Also in Stage 2
- Expand to Tier 2/3 Russian companies and bonds
- Add `GET /peergroups/{id}/compare` endpoint

### Stage 3 — Foreign Data

#### SEC EDGAR Integration
- `collectors/edgar/` — parse 10-K, 10-Q forms with XBRL extraction
  - Endpoint: `https://data.sec.gov/submissions/CIK{cik}.json`
  - XBRL facts: `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json`
- Map US GAAP line items to `statement_item_dict` (add `standard='US_GAAP'` entries)
- Companies with `sec_cik` field populated

#### Yahoo Finance Integration
- `collectors/yahoo/` — use `yfinance` library for US equity quotes
- Companies with `yahoo_ticker` field populated

#### Adapt existing modules for US GAAP
- Russian/foreign company comparison in peer groups
- Currency conversion for cross-border comparisons

#### Excel Forecast Upload
- `POST /macro/forecasts/upload` endpoint
- Template with: GDP, inflation, key rate projections, FX forecasts, commodity prices
- Store as `macro_indicators` with `source='internal_forecast'`

### Stage 4 — Optimization
- Redis caching for frequently accessed data (latest quotes, latest multiples)
- PostgreSQL query optimization (explain analyze on slow endpoints)
- Custom Excel export templates (user-configurable column sets)
- Admin panel: data collection status, job history, error logs
- Performance targets: page load <2s, comparison tables <3s, Excel export <5s

---

## Running the Project

```bash
# First time setup
cp .env.example .env
make up          # Start PostgreSQL + backend + frontend
make migrate     # Run Alembic migrations (creates all tables)
make seed        # Load 15 companies + statement item dictionary

# Daily use
make up          # Start containers
make down        # Stop containers
make logs        # Tail all logs
make shell-db    # psql into PostgreSQL

# Development
make test        # pytest
make lint        # ruff check
make migration msg="add new table"   # Generate new Alembic migration

# Trigger data collection manually (inside backend container)
docker compose exec backend python -c "
import asyncio
from app.tasks.jobs import collect_moex_quotes
asyncio.run(collect_moex_quotes())
"

# Historical backfill (example: 2 years of SBER quotes)
docker compose exec backend python -c "
import asyncio
from app.database import AsyncSessionLocal
from app.collectors.moex.quotes import MOEXQuoteCollector
async def run():
    async with AsyncSessionLocal() as db:
        c = MOEXQuoteCollector(db)
        await c.collect(from_date='2023-01-01')
        await db.commit()
asyncio.run(run())
"
```

URLs:
- Frontend: `http://localhost:5173`
- API docs (Swagger): `http://localhost:8000/api/docs`
- API docs (ReDoc): `http://localhost:8000/api/redoc`

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app factory + APScheduler lifecycle |
| `backend/app/config.py` | All settings (DATABASE_URL, MOEX_BASE_URL, cron expressions, etc.) |
| `backend/app/models/__init__.py` | Imports all models (required by Alembic) |
| `backend/app/api/router.py` | Master router including all v1 sub-routers |
| `backend/app/services/multiple_service.py` | Includes `recalculate_all()` called by scheduler |
| `backend/app/services/calculation/multiples.py` | `MultiplesCalculator` + `safe_div()` |
| `backend/app/collectors/moex/client.py` | MOEX ISS HTTP client with pagination |
| `backend/app/collectors/cbr/client.py` | CBR XML API parser |
| `backend/app/collectors/edisclosure/parser.py` | XLSX report parser + Russian term mapping |
| `backend/app/scripts/seed_data.py` | Seed companies + statement_item_dict |
| `backend/alembic/env.py` | Async Alembic configuration |
| `frontend/src/main.tsx` | App entry — MantineProvider + QueryClient |
| `frontend/src/App.tsx` | React Router setup |
| `frontend/src/components/common/DataGrid.tsx` | AG Grid wrapper used everywhere |
| `frontend/src/components/common/Chart.tsx` | Plotly wrapper used everywhere |
| `frontend/src/pages/CompanyDetailPage.tsx` | Most complex page — 4 tabs |

---

## Environment Variables (.env)

```env
DB_PASSWORD=bloom_dev
DATABASE_URL=postgresql+asyncpg://bloom:bloom_dev@db:5432/bloom
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
MOEX_BASE_URL=https://iss.moex.com/iss
CBR_BASE_URL=https://www.cbr.ru/scripts
EDISCLOSURE_BASE_URL=https://e-disclosure.ru
QUOTE_SYNC_CRON=0 19 * * 1-5
FX_SYNC_CRON=0 15 * * *
MACRO_SYNC_CRON=0 10 1 * *
MAX_UPLOAD_SIZE_MB=10
```

## Decisions Made
- **No auth in Stage 1** — internal network behind VPN
- **APScheduler (in-process)** over Celery — single server, 5 jobs
- **AG Grid Community** — no Enterprise license needed; datasets are hundreds to low thousands of rows
- **E-disclosure: semi-automated** — XLSX parsing with Russian term → code mapping, Excel upload as fallback
- **UI language**: Russian (all labels, navigation, table headers in Russian)
- **Mantine v7** for UI components
