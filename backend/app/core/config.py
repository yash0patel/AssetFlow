"""
app/core/config.py
──────────────────
Central settings loaded from environment variables via pydantic-settings.
All configuration lives here — import `settings` anywhere in the app.
"""

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide settings resolved from .env / environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────────────────────────────────────
    APP_NAME: str = "AssetFlow"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ── Server ─────────────────────────────────────────────────────────────────
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_URL: str = "http://localhost:8000"

    # ── Frontend / CORS ────────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:5173"

    @field_validator("FRONTEND_URL", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str) -> str:
        return v

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Return a list of allowed origins for CORS."""
        origins = [self.FRONTEND_URL, self.BACKEND_URL]
        if self.ENVIRONMENT == "development":
            origins += [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
        return list(set(origins))

    # ── Database ───────────────────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+psycopg://postgres:password@localhost:5432/assetflow_db"
    )

    # ── Redis ──────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""

    # ── JWT ────────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Logging ────────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    # ── File Uploads ───────────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "uploads"

    @property
    def MAX_UPLOAD_SIZE_BYTES(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Return a cached singleton Settings instance.
    Use `get_settings()` as a FastAPI dependency or import `settings` directly.
    """
    return Settings()


# Module-level singleton — convenient for non-DI usage
settings: Settings = get_settings()
