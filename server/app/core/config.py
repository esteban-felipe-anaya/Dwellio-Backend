"""Application configuration via pydantic-settings.

Reads from environment / `.env`. Splits cleanly between a zero-install SQLite
fallback (so the project runs and tests with no external services) and the
documented PostgreSQL target.
"""

from __future__ import annotations

from functools import lru_cache

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

    # --- CORS --- comma-separated origins. Kept as a plain string so reading it
    # from .env never triggers pydantic-settings' JSON decoding of list fields;
    # `cors_origins` exposes the parsed list.
    CORS_ORIGINS: str = (
        "http://localhost:3001,http://127.0.0.1:3001,"
        "http://localhost:3000,http://localhost:8080"
    )

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

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
