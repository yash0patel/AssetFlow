"""
app/main.py
────────────
FastAPI application factory.

Start with:
    uvicorn app.main:app --reload

The application:
  - Registers CORS, logging, and exception-handler middleware
  - Mounts all API v1 routers
  - Opens the Redis connection on startup and closes it on shutdown
  - Exposes a /health endpoint
"""

import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.constants import API_V1_PREFIX
from app.middleware.exception_handler import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.middleware.logging import RequestLoggingMiddleware
from app.redis.client import close_redis_client, get_redis_client

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": settings.LOG_LEVEL,
    },
    "loggers": {
        "uvicorn": {"propagate": True},
        "uvicorn.error": {"propagate": True},
        "uvicorn.access": {"propagate": False},  # handled by RequestLoggingMiddleware
        "sqlalchemy.engine": {
            "level": "DEBUG" if settings.DEBUG else "WARNING",
            "propagate": True,
        },
    },
}
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("assetflow")


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown events
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("Starting AssetFlow API  [env=%s]", settings.ENVIRONMENT)

    # Warm up the Redis connection pool
    try:
        redis = await get_redis_client()
        await redis.ping()
        logger.info("Redis connection established  [%s]", settings.REDIS_URL)
    except Exception as exc:
        logger.warning("Redis unavailable at startup: %s", exc)

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Shutting down AssetFlow API …")
    await close_redis_client()
    logger.info("Redis connection closed.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AssetFlow ERP — Asset Management Platform",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request logging ───────────────────────────────────────────────────────
    app.add_middleware(RequestLoggingMiddleware)

    # ── Exception handlers ────────────────────────────────────────────────────
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ── Routers ───────────────────────────────────────────────────────────────
    from app.api.v1 import (
        auth, departments, asset_categories, employees,
        assets, allocations, bookings, maintenance, audits,
        dashboard, notifications, reports, activity_logs,
    )
    app.include_router(auth.router, prefix=API_V1_PREFIX + "/auth", tags=["Auth"])
    app.include_router(departments.router, prefix=API_V1_PREFIX + "/departments", tags=["Departments"])
    app.include_router(asset_categories.router, prefix=API_V1_PREFIX + "/asset-categories", tags=["Asset Categories"])
    app.include_router(employees.router, prefix=API_V1_PREFIX + "/employees", tags=["Employees"])
    app.include_router(assets.router, prefix=API_V1_PREFIX + "/assets", tags=["Assets"])
    app.include_router(allocations.router, prefix=API_V1_PREFIX + "/allocations", tags=["Allocations"])
    app.include_router(bookings.router, prefix=API_V1_PREFIX + "/bookings", tags=["Bookings"])
    app.include_router(maintenance.router, prefix=API_V1_PREFIX + "/maintenance", tags=["Maintenance"])
    app.include_router(audits.router, prefix=API_V1_PREFIX + "/audits", tags=["Audits"])
    app.include_router(dashboard.router, prefix=API_V1_PREFIX + "/dashboard", tags=["Dashboard"])
    app.include_router(notifications.router, prefix=API_V1_PREFIX + "/notifications", tags=["Notifications"])
    app.include_router(reports.router, prefix=API_V1_PREFIX + "/reports", tags=["Reports"])
    app.include_router(activity_logs.router, prefix=API_V1_PREFIX + "/activity-logs", tags=["Activity Logs"])

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Health check")
    async def health_check():
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    return app


app = create_application()
