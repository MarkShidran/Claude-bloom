from fastapi import Request
from fastapi.responses import JSONResponse


class BloomException(Exception):
    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(BloomException):
    status_code = 404
    detail = "Resource not found"


class ValidationError(BloomException):
    status_code = 422
    detail = "Validation error"


class CollectionError(BloomException):
    status_code = 502
    detail = "External data source error"


async def bloom_exception_handler(request: Request, exc: BloomException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "type": type(exc).__name__},
    )
