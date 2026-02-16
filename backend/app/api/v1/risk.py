from fastapi import APIRouter

router = APIRouter(prefix="/risk", tags=["Risk Analytics"])


@router.post("/beta")
async def calculate_beta():
    return {
        "status": "not_implemented",
        "message": "Beta calculation available in Stage 2",
    }


@router.post("/wacc")
async def calculate_wacc():
    return {
        "status": "not_implemented",
        "message": "WACC calculation available in Stage 2",
    }
