"""
app/middleware/exception_handler.py
─────────────────────────────────────
Global exception handlers registered on the FastAPI application.
Returns structured JSON error responses for all unhandled exceptions.
"""

import logging
import traceback

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("assetflow.errors")


# ── Structured error response helper ──────────────────────────────────────────
def error_response(
    status_code: int,
    message: str,
    details: object = None,
) -> JSONResponse:
    body: dict = {"success": False, "message": message}
    if details is not None:
        body["details"] = details
    return JSONResponse(status_code=status_code, content=body)


# ── Handlers ───────────────────────────────────────────────────────────────────

async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle FastAPI/Starlette HTTP exceptions."""
    logger.warning("HTTPException %s: %s  [%s]", exc.status_code, exc.detail, request.url)
    return error_response(exc.status_code, str(exc.detail))


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic request validation errors."""
    logger.warning("Validation error on %s: %s", request.url, exc.errors())
    return error_response(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        "Request validation failed.",
        details=exc.errors(),
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all for any unhandled server errors."""
    logger.error(
        "Unhandled exception on %s:\n%s",
        request.url,
        traceback.format_exc(),
    )
    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "An unexpected error occurred. Please try again later.",
    )
