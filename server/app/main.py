from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import (
    admin,
    agents,
    auth,
    favorites,
    inquiries,
    listings,
    lookups,
    notifications,
    saved_searches,
    tours,
)
from app.core.config import settings
from app.core.db import create_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On the zero-install SQLite path, ensure tables exist so the app runs
    # without a manual migration step. Postgres uses Alembic (`make migrate`).
    if settings.is_sqlite:
        await create_all()
    os.makedirs(os.path.join(settings.MEDIA_ROOT, "uploads"), exist_ok=True)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Backend for the Dwellio real-estate app (contract-compatible).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)

# Serve uploaded media in development. In production, serve /media via a reverse
# proxy or object store (see README).
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
app.mount(settings.MEDIA_URL, StaticFiles(directory=settings.MEDIA_ROOT), name="media")

# Public, contract-parity routers (same paths/shapes the Flutter app uses).
app.include_router(auth.router)
app.include_router(lookups.router)
app.include_router(listings.router)
app.include_router(agents.router)
app.include_router(favorites.router)
app.include_router(saved_searches.router)
app.include_router(tours.router)
app.include_router(inquiries.router)
app.include_router(notifications.router)

# Staff-only dashboard API.
app.include_router(admin.router)


@app.get("/", tags=["meta"])
async def root() -> dict:
    return {
        "name": settings.PROJECT_NAME,
        "status": "ok",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Keep a uniform error envelope; FastAPI handles HTTPException itself.
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)},
    )
