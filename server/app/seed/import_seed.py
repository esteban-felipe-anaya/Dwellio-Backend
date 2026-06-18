"""Idempotent seed importer. Upserts every entity by id in dependency order so
it can be run repeatedly.

    python -m app.seed.import_seed [--path app/seed/seed_data.json]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.computations import parse_scheduled_for
from app.core.config import settings
from app.core.db import SessionLocal, create_all
from app.core.security import hash_password
from app.models import (
    Agent,
    Amenity,
    Favorite,
    Inquiry,
    InquiryMessage,
    Listing,
    ListingPhoto,
    Notification,
    PropertyType,
    SavedSearch,
    Tour,
    User,
)


def _dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


async def _upsert(db: AsyncSession, model, pk, **fields):
    obj = await db.get(model, pk)
    if obj is None:
        obj = model(id=pk, **fields)
        db.add(obj)
    else:
        for k, v in fields.items():
            setattr(obj, k, v)
    return obj


async def run(path: str) -> None:
    if settings.is_sqlite:
        await create_all()

    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    async with SessionLocal() as db:
        # 1. Property types
        for pt in data.get("propertyTypes", []):
            await _upsert(
                db, PropertyType, pt["id"], name=pt["name"], icon=pt.get("icon", "home")
            )
        # 2. Amenities
        for am in data.get("amenities", []):
            await _upsert(
                db, Amenity, am["id"], name=am["name"], icon=am.get("icon", "check")
            )
        # 3. Agents
        for a in data.get("agents", []):
            await _upsert(
                db,
                Agent,
                a["id"],
                name=a["name"],
                photo=a.get("photo"),
                agency=a.get("agency", ""),
                phone=a.get("phone", ""),
                rating=a.get("rating", 0),
                review_count=a.get("reviewCount", 0),
            )
        # 4. Users
        for u in data.get("users", []):
            await _upsert(
                db,
                User,
                u["id"],
                email=u["email"].lower(),
                hashed_password=hash_password(u.get("password", "password")),
                name=u.get("name", ""),
                phone=u.get("phone", ""),
                photo=u.get("photo"),
                is_staff=u.get("isStaff", False),
                is_superuser=u.get("isSuperuser", False),
                is_active=True,
            )
        await db.flush()

        # Cache amenity objects for m2m.
        amenity_map = {
            a.id: a for a in (await db.execute(select(Amenity))).scalars().all()
        }

        # 5. Listings (+ photos, amenities). Assign collections directly (no
        # pre-flush access) so selectin relationships never lazy-load in async.
        for lst in data.get("listings", []):
            obj = await db.get(Listing, lst["id"])
            if obj is None:
                obj = Listing(id=lst["id"])
                db.add(obj)
            obj.title = lst["title"]
            obj.deal_type = lst["dealType"]
            obj.price = lst["price"]
            obj.currency = lst.get("currency", "USD")
            obj.property_type_id = lst.get("propertyType")
            obj.beds = lst.get("beds", 0)
            obj.baths = lst.get("baths", 0)
            obj.area_sqm = lst.get("areaSqm", 0)
            obj.parking = lst.get("parking", 0)
            obj.address = lst.get("address", "")
            obj.city = lst.get("city", "")
            obj.lat = lst["lat"]
            obj.lng = lst["lng"]
            obj.agent_id = lst.get("agentId")
            obj.owner_id = lst.get("ownerId")
            obj.description = lst.get("description", "")
            obj.featured = lst.get("featured", False)
            obj.listed_at = _dt(lst.get("listedAt")) or datetime.now(timezone.utc)
            obj.photos = [
                ListingPhoto(url=url, position=i)
                for i, url in enumerate(lst.get("photos", []))
            ]
            obj.amenities = [
                amenity_map[a] for a in lst.get("amenities", []) if a in amenity_map
            ]
        await db.flush()

        # 6. Favorites
        for fav in data.get("favorites", []):
            exists = await db.get(
                Favorite,
                {"user_id": fav["userId"], "listing_id": fav["listingId"]},
            )
            if exists is None:
                db.add(Favorite(user_id=fav["userId"], listing_id=fav["listingId"]))

        # 7. Saved searches
        for s in data.get("savedSearches", []):
            await _upsert(
                db,
                SavedSearch,
                s["id"],
                user_id=s["userId"],
                label=s["label"],
                filters=s.get("filters", {}),
                created_at=_dt(s.get("createdAt")) or datetime.now(timezone.utc),
            )

        # 8. Tours (stamped relative to now so the status flow looks live)
        now = datetime.now(timezone.utc)
        for t in data.get("tours", []):
            days = t.get("daysFromNow", 1)
            day = (now + timedelta(days=days)).strftime("%Y-%m-%d")
            slot = t.get("slot", "2:00 PM")
            await _upsert(
                db,
                Tour,
                t["id"],
                user_id=t["userId"],
                listing_id=t["listingId"],
                date=day,
                slot=slot,
                scheduled_for=parse_scheduled_for(day, slot),
                status_override=t.get("statusOverride", ""),
                created_at=now - timedelta(days=3),
            )

        # 9. Inquiries (+ messages)
        for i in data.get("inquiries", []):
            obj = await db.get(Inquiry, i["id"])
            if obj is None:
                obj = Inquiry(id=i["id"])
                db.add(obj)
            obj.user_id = i["userId"]
            obj.listing_id = i["listingId"]
            obj.type = i.get("type", "message")
            obj.last_message = i.get("lastMessage", "")
            obj.status = i.get("status", "open")
            obj.date = _dt(i.get("date")) or datetime.now(timezone.utc)
            obj.messages = [
                InquiryMessage(
                    sender=m.get("from", "user"),
                    text=m.get("text", ""),
                    at=_dt(m.get("at")) or datetime.now(timezone.utc),
                )
                for m in i.get("messages", [])
            ]

        # 10. Notifications
        for n in data.get("notifications", []):
            await _upsert(
                db,
                Notification,
                n["id"],
                user_id=n["userId"],
                title=n["title"],
                body=n.get("body", ""),
                type=n.get("type", "system"),
                read=n.get("read", False),
                date=_dt(n.get("date")) or datetime.now(timezone.utc),
                listing_id=n.get("listingId"),
            )

        await db.commit()

    print("Seed import complete:", ", ".join(f"{k}={len(v)}" for k, v in data.items()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", default=settings.SEED_DATA_PATH)
    args = parser.parse_args()
    path = args.path
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    from app.core.event_loop import use_selector_event_loop

    use_selector_event_loop()
    asyncio.run(run(path))


if __name__ == "__main__":
    main()
