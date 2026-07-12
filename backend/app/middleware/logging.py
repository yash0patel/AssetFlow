"""
app/middleware/logging.py
──────────────────────────
Request / response logging middleware.
Logs method, path, status code, and duration for every request.
"""

import time
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("assetflow.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming requests and their response status + duration."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s -> %s  [%.1f ms]",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
