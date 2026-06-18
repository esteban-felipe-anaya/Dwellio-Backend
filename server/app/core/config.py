"""Application configuration via pydantic-settings.

Reads from environment / `.env`. Splits cleanly between a zero-install SQLite
fallback (so the project runs and tests with no external services) and the
documented PostgreSQL target.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- App ---
    PROJECT_NAME: str = "Dwellio API"
    ENV: str = "dev"  # dev | prod
    DEBUG: bool = True

    # --- Security ---
    SECRET_KEY: str = "dev-insecure-secret-change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    # --- Database ---
    # When unset, falls back to a local SQLite file so everything runs with
    # zero install. Production: postgresql+asyncpg://user:pass@host:5432/dwellio
    DATABASE_URL: str | None = None

    # --- Media / uploads ---
    MEDIA_ROOT: str = "media"
    MEDIA_URL: str = "/media"
    MAX_UPLOAD_MB: int = 10

    # --- Seed ---
    SEED_DATA_PATH: str = "app/seed/seed_data.json"

    # --- CORS ---  comma-separated origins in env, list in code.
    CORS_ORIGINS: list[str] = [
        "http://localhost:3001",  # admin
        "http://127.0.0.1:3001",
        "http://localhost:3000",  # flutter web dev
        "http://localhost:8080",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, v: object) -> object:
        if isinstance(v, str) and not v.startswith("["):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def sqlalchemy_url(self) -> str:
        return self.DATABASE_URL or "sqlite+aiosqlite:///./dev.sqlite3"

    @property
    def is_sqlite(self) -> bool:
        return self.sqlalchemy_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
