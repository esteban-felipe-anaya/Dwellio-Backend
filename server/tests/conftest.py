"""Test fixtures: isolated SQLite DB + seeded lookups, and an ASGI client."""
from __future__ import annotations

import os

# Point at an isolated test database BEFORE importing the app/settings.
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_dwellio.sqlite3"

from datetime import datetime, timezone  # noqa: E402

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.core.db import Base, SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models import (  # noqa: E402
    Agent,
    Amenity,
    Listing,
    ListingPhoto,
    PropertyType,
    User,
)


@pytest_asyncio.fixture(autouse=True)
async def _db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as db:
        db.add(PropertyType(id="house", name="House", icon="house"))
        db.add(PropertyType(id="apartment", name="Apartment", icon="apartment"))
        db.add(Amenity(id="pool", name="Pool", icon="pool"))
        db.add(Amenity(id="gym", name="Gym", icon="fitness_center"))
        db.add(
            Agent(
                id="agt_01",
                name="Test Agent",
                agency="Testing Realty",
                phone="+1 555",
                rating=4.5,
                review_count=10,
            )
        )
        db.add(
            User(
                id="usr_demo",
                email="demo@dwellio.app",
                hashed_password=hash_password("password"),
                name="Demo User",
            )
        )
        # Austin listing (inside the test bbox), Lisbon listing (outside).
        austin = Listing(
            id="lst_austin",
            title="Austin Loft",
            deal_type="buy",
            price=400000,
            property_type_id="apartment",
            beds=2,
            baths=2,
            area_sqm=90,
            city="Austin",
            lat=30.27,
            lng=-97.74,
            agent_id="agt_01",
            listed_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
        )
        austin.photos = [ListingPhoto(url="/media/uploads/a.jpg", position=0)]
        db.add(austin)
        db.add(
            Listing(
                id="lst_lisbon",
                title="Lisbon Flat",
                deal_type="buy",
                price=250000,
                property_type_id="apartment",
                beds=1,
                baths=1,
                area_sqm=60,
                city="Lisbon",
                lat=38.72,
                lng=-9.14,
                agent_id="agt_01",
                listed_at=datetime(2026, 5, 2, tzinfo=timezone.utc),
            )
        )
        await db.commit()
    yield


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


async def auth_header(client: AsyncClient) -> dict:
    res = await client.post(
        "/auth/login", json={"email": "demo@dwellio.app", "password": "password"}
    )
    token = res.json()["token"]
    return {"Authorization": f"Bearer {token}"}
