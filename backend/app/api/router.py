from fastapi import APIRouter

from app.api.v1.companies import router as companies_router
from app.api.v1.export import router as export_router
from app.api.v1.financials import router as financials_router
from app.api.v1.health import router as health_router
from app.api.v1.macro import router as macro_router
from app.api.v1.multiples import router as multiples_router
from app.api.v1.peer_groups import router as peer_groups_router
from app.api.v1.quotes import router as quotes_router
from app.api.v1.risk import router as risk_router
from app.api.v1.securities import router as securities_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(companies_router)
api_router.include_router(securities_router)
api_router.include_router(quotes_router)
api_router.include_router(financials_router)
api_router.include_router(multiples_router)
api_router.include_router(peer_groups_router)
api_router.include_router(risk_router)
api_router.include_router(macro_router)
api_router.include_router(export_router)
