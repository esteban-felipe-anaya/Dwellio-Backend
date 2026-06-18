from __future__ import annotations

import os
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_staff
from app.api.listing_query import count_matches
from app.core.computations import tour_status
from app.core.config import settings
from app.core.db import get_db
from app.core.security import new_id
from app.models import (
    Agent,
    Amenity,
    Favorite,
    Inquiry,
    Listing,
    ListingPhoto,
    Notification,
    PropertyType,
    SavedSearch,
    Tour,
    User,
)
from app.schemas.admin import (
    AdminAgentIn,
    AdminAgentOut,
    AdminInquiryOut,
    AdminListingIn,
    AdminListingOut,
    AdminLookupIn,
    AdminLookupOut,
    AdminNotificationIn,
    AdminSavedSearchOut,
    AdminStatusIn,
    AdminTourOut,
    AdminUserOut,
    AgentCount,
    CityAvg,
    LabelCount,
    RecentInquiry,
    RecentListing,
    StatsOut,
    TimePoint,
    UploadOut,
)
from app.schemas.common import to_iso
from app.schemas.engagement import NotificationOut

router = APIRouter(
    prefix="/admin-api", tags=["admin"], dependencies=[Depends(require_staff)]
)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
async def _agent_names(db: AsyncSession) -> dict[str, str]:
    rows = (await db.execute(select(Agent.id, Agent.name))).all()
    return {r[0]: r[1] for r in rows}


def _admin_listing_out(listing: Listing, agent_name: str | None) -> AdminListingOut:
    return AdminListingOut(
        id=listing.id,
        title=listing.title,
        deal_type=listing.deal_type,
        price=listing.price,
        currency=listing.currency or "USD",
        property_type=listing.property_type_id or "",
        beds=listing.beds,
        baths=listing.baths,
        area_sqm=listing.area_sqm,
        parking=listing.parking,
        address=listing.address or "",
        city=listing.city or "",
        lat=listing.lat,
        lng=listing.lng,
        amenities=[a.id for a in listing.amenities],
        photos=[p.url for p in listing.photos],
        agent_id=listing.agent_id,
        agent_name=agent_name,
        owner_id=listing.owner_id,
        description=listing.description or "",
        featured=listing.featured,
        listed_at=to_iso(listing.listed_at),
    )


# --------------------------------------------------------------------------- #
# Upload
# --------------------------------------------------------------------------- #
@router.post("/upload", response_model=UploadOut)
async def upload_media(file: UploadFile = File(...)) -> UploadOut:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {ext or 'unknown'}"
        )
    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")
    uploads_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    name = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(uploads_dir, name), "wb") as fh:
        fh.write(data)
    # Host-independent relative path; clients prepend their own base URL.
    return UploadOut(url=f"{settings.MEDIA_URL}/uploads/{name}")


# --------------------------------------------------------------------------- #
# Stats
# --------------------------------------------------------------------------- #
@router.get("/stats", response_model=StatsOut)
async def stats(db: AsyncSession = Depends(get_db)) -> StatsOut:
    listings = (await db.execute(select(Listing))).scalars().unique().all()
    total_listings = len(listings)
    active_listings = sum(1 for lst in listings if lst.featured)

    tours = (await db.execute(select(Tour))).scalars().all()
    tours_scheduled = sum(
        1
        for t in tours
        if tour_status(t.scheduled_for, t.created_at, t.status_override)
        in {"requested", "confirmed", "upcoming"}
    )

    inquiries = (await db.execute(select(Inquiry))).scalars().all()
    open_inquiries = sum(1 for i in inquiries if i.status in {"open", "pending"})

    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    total_agents = (await db.execute(select(func.count(Agent.id)))).scalar() or 0

    # Listings over time (by month).
    buckets: dict[str, int] = defaultdict(int)
    for lst in listings:
        if lst.listed_at:
            buckets[lst.listed_at.strftime("%Y-%m")] += 1
    over_time = [TimePoint(label=k, value=v) for k, v in sorted(buckets.items())]

    by_type_counter = Counter(lst.property_type_id or "other" for lst in listings)
    by_property_type = [
        LabelCount(label=k, value=v) for k, v in by_type_counter.most_common()
    ]

    by_deal_counter = Counter(lst.deal_type for lst in listings)
    by_deal_type = [LabelCount(label=k, value=v) for k, v in by_deal_counter.items()]

    city_prices: dict[str, list[float]] = defaultdict(list)
    for lst in listings:
        if lst.city:
            city_prices[lst.city].append(lst.price)
    avg_price_by_city = sorted(
        (
            CityAvg(city=c, avg_price=round(sum(p) / len(p), 2))
            for c, p in city_prices.items()
        ),
        key=lambda x: x.avg_price,
        reverse=True,
    )[:6]

    names = await _agent_names(db)
    agent_counter = Counter(lst.agent_id for lst in listings if lst.agent_id)
    top_agents = [
        AgentCount(name=names.get(aid, aid), value=v)
        for aid, v in agent_counter.most_common(6)
    ]

    recent = sorted(
        listings,
        key=lambda lst: lst.listed_at or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )[:5]
    recent_listings = [
        RecentListing(
            id=lst.id,
            title=lst.title,
            price=lst.price,
            city=lst.city or "",
            deal_type=lst.deal_type,
            listed_at=to_iso(lst.listed_at),
        )
        for lst in recent
    ]

    titles = {lst.id: lst.title for lst in listings}
    recent_inq = sorted(
        inquiries,
        key=lambda i: i.date or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )[:5]
    recent_inquiries = [
        RecentInquiry(
            id=i.id,
            listing_title=titles.get(i.listing_id),
            type=i.type,
            status=i.status,
            date=to_iso(i.date),
        )
        for i in recent_inq
    ]

    return StatsOut(
        total_listings=total_listings,
        active_listings=active_listings,
        tours_scheduled=tours_scheduled,
        open_inquiries=open_inquiries,
        total_users=total_users,
        total_agents=total_agents,
        listings_over_time=over_time,
        by_property_type=by_property_type,
        by_deal_type=by_deal_type,
        avg_price_by_city=avg_price_by_city,
        top_agents=top_agents,
        recent_listings=recent_listings,
        recent_inquiries=recent_inquiries,
    )


# --------------------------------------------------------------------------- #
# Listings CRUD
# --------------------------------------------------------------------------- #
@router.get("/listings", response_model=list[AdminListingOut])
async def admin_list_listings(db: AsyncSession = Depends(get_db)):
    rows = (
        (await db.execute(select(Listing).order_by(Listing.listed_at.desc())))
        .scalars()
        .unique()
        .all()
    )
    names = await _agent_names(db)
    return [_admin_listing_out(lst, names.get(lst.agent_id or "")) for lst in rows]


async def _apply_amenities(db: AsyncSession, listing: Listing, ids: list[str]) -> None:
    ams = (await db.execute(select(Amenity).where(Amenity.id.in_(ids)))).scalars().all()
    listing.amenities = list(ams)


@router.post("/listings", response_model=AdminListingOut, status_code=201)
async def admin_create_listing(
    body: AdminListingIn, db: AsyncSession = Depends(get_db)
):
    listing = Listing(
        id=new_id("lst"),
        title=body.title or "Untitled",
        deal_type=body.deal_type or "buy",
        price=body.price or 0,
        currency=body.currency or "USD",
        property_type_id=body.property_type,
        beds=body.beds or 0,
        baths=body.baths or 0,
        area_sqm=body.area_sqm or 0,
        parking=body.parking or 0,
        address=body.address or "",
        city=body.city or "",
        lat=body.lat or 0,
        lng=body.lng or 0,
        agent_id=body.agent_id,
        description=body.description or "",
        featured=bool(body.featured),
        listed_at=datetime.now(timezone.utc),
    )
    for i, url in enumerate(body.photos or []):
        listing.photos.append(ListingPhoto(url=url, position=i))
    db.add(listing)
    if body.amenities:
        await _apply_amenities(db, listing, body.amenities)
    await db.commit()
    refreshed = await db.get(Listing, listing.id)
    names = await _agent_names(db)
    return _admin_listing_out(refreshed, names.get(refreshed.agent_id or ""))


@router.patch("/listings/{listing_id}", response_model=AdminListingOut)
async def admin_update_listing(
    listing_id: str, body: AdminListingIn, db: AsyncSession = Depends(get_db)
):
    listing = await db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    data = body.model_dump(exclude_unset=True, by_alias=False)
    field_map = {
        "title": "title",
        "deal_type": "deal_type",
        "price": "price",
        "currency": "currency",
        "property_type": "property_type_id",
        "beds": "beds",
        "baths": "baths",
        "area_sqm": "area_sqm",
        "parking": "parking",
        "address": "address",
        "city": "city",
        "lat": "lat",
        "lng": "lng",
        "agent_id": "agent_id",
        "description": "description",
        "featured": "featured",
    }
    for key, col in field_map.items():
        if key in data and data[key] is not None:
            setattr(listing, col, data[key])
    if "photos" in data and data["photos"] is not None:
        listing.photos.clear()
        for i, url in enumerate(data["photos"]):
            listing.photos.append(ListingPhoto(url=url, position=i))
    if "amenities" in data and data["amenities"] is not None:
        await _apply_amenities(db, listing, data["amenities"])
    await db.commit()
    refreshed = await db.get(Listing, listing.id)
    names = await _agent_names(db)
    return _admin_listing_out(refreshed, names.get(refreshed.agent_id or ""))


@router.delete("/listings/{listing_id}")
async def admin_delete_listing(listing_id: str, db: AsyncSession = Depends(get_db)):
    listing = await db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    await db.delete(listing)
    await db.commit()
    return {"ok": True}


# --------------------------------------------------------------------------- #
# Agents CRUD
# --------------------------------------------------------------------------- #
@router.get("/agents", response_model=list[AdminAgentOut])
async def admin_list_agents(db: AsyncSession = Depends(get_db)):
    agents = (await db.execute(select(Agent).order_by(Agent.name))).scalars().all()
    counts = dict(
        (
            await db.execute(
                select(Listing.agent_id, func.count(Listing.id)).group_by(
                    Listing.agent_id
                )
            )
        ).all()
    )
    return [
        AdminAgentOut(
            id=a.id,
            name=a.name,
            photo=a.photo,
            agency=a.agency or "",
            phone=a.phone or "",
            rating=a.rating or 0,
            review_count=a.review_count or 0,
            listing_count=counts.get(a.id, 0),
        )
        for a in agents
    ]


@router.post("/agents", response_model=AdminAgentOut, status_code=201)
async def admin_create_agent(body: AdminAgentIn, db: AsyncSession = Depends(get_db)):
    agent = Agent(
        id=new_id("agt"),
        name=body.name or "New Agent",
        photo=body.photo,
        agency=body.agency or "",
        phone=body.phone or "",
        rating=body.rating or 0,
        review_count=body.review_count or 0,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return AdminAgentOut.model_validate(agent)


@router.patch("/agents/{agent_id}", response_model=AdminAgentOut)
async def admin_update_agent(
    agent_id: str, body: AdminAgentIn, db: AsyncSession = Depends(get_db)
):
    agent = await db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    for key, value in body.model_dump(exclude_unset=True, by_alias=False).items():
        if value is not None:
            setattr(agent, key, value)
    await db.commit()
    await db.refresh(agent)
    return AdminAgentOut.model_validate(agent)


@router.delete("/agents/{agent_id}")
async def admin_delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    agent = await db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    await db.delete(agent)
    await db.commit()
    return {"ok": True}


# --------------------------------------------------------------------------- #
# Property types & amenities CRUD
# --------------------------------------------------------------------------- #
def _slug(name: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in name.strip().lower()).strip("_")


@router.get("/property-types", response_model=list[AdminLookupOut])
async def admin_list_property_types(db: AsyncSession = Depends(get_db)):
    rows = (
        (await db.execute(select(PropertyType).order_by(PropertyType.name)))
        .scalars()
        .all()
    )
    return [AdminLookupOut.model_validate(r) for r in rows]


@router.post("/property-types", response_model=AdminLookupOut, status_code=201)
async def admin_create_property_type(
    body: AdminLookupIn, db: AsyncSession = Depends(get_db)
):
    pid = body.id or _slug(body.name)
    if await db.get(PropertyType, pid):
        raise HTTPException(status_code=409, detail="Property type already exists")
    pt = PropertyType(id=pid, name=body.name, icon=body.icon or "home")
    db.add(pt)
    await db.commit()
    return AdminLookupOut.model_validate(pt)


@router.patch("/property-types/{type_id}", response_model=AdminLookupOut)
async def admin_update_property_type(
    type_id: str, body: AdminLookupIn, db: AsyncSession = Depends(get_db)
):
    pt = await db.get(PropertyType, type_id)
    if pt is None:
        raise HTTPException(status_code=404, detail="Property type not found")
    pt.name = body.name
    if body.icon:
        pt.icon = body.icon
    await db.commit()
    return AdminLookupOut.model_validate(pt)


@router.delete("/property-types/{type_id}")
async def admin_delete_property_type(type_id: str, db: AsyncSession = Depends(get_db)):
    pt = await db.get(PropertyType, type_id)
    if pt is None:
        raise HTTPException(status_code=404, detail="Property type not found")
    await db.delete(pt)
    await db.commit()
    return {"ok": True}


@router.get("/amenities", response_model=list[AdminLookupOut])
async def admin_list_amenities(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Amenity).order_by(Amenity.name))).scalars().all()
    return [AdminLookupOut.model_validate(r) for r in rows]


@router.post("/amenities", response_model=AdminLookupOut, status_code=201)
async def admin_create_amenity(body: AdminLookupIn, db: AsyncSession = Depends(get_db)):
    aid = body.id or _slug(body.name)
    if await db.get(Amenity, aid):
        raise HTTPException(status_code=409, detail="Amenity already exists")
    am = Amenity(id=aid, name=body.name, icon=body.icon or "check")
    db.add(am)
    await db.commit()
    return AdminLookupOut.model_validate(am)


@router.patch("/amenities/{amenity_id}", response_model=AdminLookupOut)
async def admin_update_amenity(
    amenity_id: str, body: AdminLookupIn, db: AsyncSession = Depends(get_db)
):
    am = await db.get(Amenity, amenity_id)
    if am is None:
        raise HTTPException(status_code=404, detail="Amenity not found")
    am.name = body.name
    if body.icon:
        am.icon = body.icon
    await db.commit()
    return AdminLookupOut.model_validate(am)


@router.delete("/amenities/{amenity_id}")
async def admin_delete_amenity(amenity_id: str, db: AsyncSession = Depends(get_db)):
    am = await db.get(Amenity, amenity_id)
    if am is None:
        raise HTTPException(status_code=404, detail="Amenity not found")
    await db.delete(am)
    await db.commit()
    return {"ok": True}


# --------------------------------------------------------------------------- #
# Users (read-only) + drawer lookups
# --------------------------------------------------------------------------- #
@router.get("/users", response_model=list[AdminUserOut])
async def admin_list_users(db: AsyncSession = Depends(get_db)):
    users = (
        (await db.execute(select(User).order_by(User.created_at.desc())))
        .scalars()
        .all()
    )
    fav_counts = dict(
        (
            await db.execute(
                select(Favorite.user_id, func.count()).group_by(Favorite.user_id)
            )
        ).all()
    )
    ss_counts = dict(
        (
            await db.execute(
                select(SavedSearch.user_id, func.count()).group_by(SavedSearch.user_id)
            )
        ).all()
    )
    return [
        AdminUserOut(
            id=u.id,
            name=u.name,
            email=u.email,
            phone=u.phone or "",
            photo=u.photo,
            is_staff=u.is_staff,
            is_superuser=u.is_superuser,
            is_active=u.is_active,
            created_at=to_iso(u.created_at),
            favorites_count=fav_counts.get(u.id, 0),
            saved_searches_count=ss_counts.get(u.id, 0),
        )
        for u in users
    ]


@router.get("/saved-searches", response_model=list[AdminSavedSearchOut])
async def admin_list_saved_searches(
    user: str | None = None, db: AsyncSession = Depends(get_db)
):
    stmt = select(SavedSearch)
    if user:
        stmt = stmt.where(SavedSearch.user_id == user)
    rows = (
        (await db.execute(stmt.order_by(SavedSearch.created_at.desc()))).scalars().all()
    )
    names = dict((await db.execute(select(User.id, User.name))).all())
    out = []
    for s in rows:
        matches = await count_matches(db, s.filters or {})
        out.append(
            AdminSavedSearchOut(
                id=s.id,
                label=s.label,
                filters=s.filters or {},
                created_at=to_iso(s.created_at),
                user_id=s.user_id,
                user_name=names.get(s.user_id),
                new_matches=matches,
            )
        )
    return out


@router.get("/favorites", response_model=list[str])
async def admin_user_favorites(user: str, db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(Favorite.listing_id).where(Favorite.user_id == user))
    return [r[0] for r in rows.all()]


# --------------------------------------------------------------------------- #
# Tours & inquiries management
# --------------------------------------------------------------------------- #
@router.get("/tours", response_model=list[AdminTourOut])
async def admin_list_tours(db: AsyncSession = Depends(get_db)):
    tours = (
        (await db.execute(select(Tour).order_by(Tour.scheduled_for.desc())))
        .scalars()
        .all()
    )
    titles = dict((await db.execute(select(Listing.id, Listing.title))).all())
    names = dict((await db.execute(select(User.id, User.name))).all())
    return [
        AdminTourOut(
            id=t.id,
            listing_id=t.listing_id,
            listing_title=titles.get(t.listing_id),
            user_id=t.user_id,
            user_name=names.get(t.user_id),
            date=t.date,
            slot=t.slot,
            status=tour_status(t.scheduled_for, t.created_at, t.status_override),
            scheduled_for=to_iso(t.scheduled_for),
            created_at=to_iso(t.created_at),
        )
        for t in tours
    ]


@router.patch("/tours/{tour_id}", response_model=AdminTourOut)
async def admin_update_tour(
    tour_id: str, body: AdminStatusIn, db: AsyncSession = Depends(get_db)
):
    tour = await db.get(Tour, tour_id)
    if tour is None:
        raise HTTPException(status_code=404, detail="Tour not found")
    tour.status_override = body.status
    await db.commit()
    await db.refresh(tour)
    listing = await db.get(Listing, tour.listing_id)
    user = await db.get(User, tour.user_id)
    return AdminTourOut(
        id=tour.id,
        listing_id=tour.listing_id,
        listing_title=listing.title if listing else None,
        user_id=tour.user_id,
        user_name=user.name if user else None,
        date=tour.date,
        slot=tour.slot,
        status=tour_status(tour.scheduled_for, tour.created_at, tour.status_override),
        scheduled_for=to_iso(tour.scheduled_for),
        created_at=to_iso(tour.created_at),
    )


@router.get("/inquiries", response_model=list[AdminInquiryOut])
async def admin_list_inquiries(db: AsyncSession = Depends(get_db)):
    inquiries = (
        (await db.execute(select(Inquiry).order_by(Inquiry.date.desc())))
        .scalars()
        .all()
    )
    titles = dict((await db.execute(select(Listing.id, Listing.title))).all())
    names = dict((await db.execute(select(User.id, User.name))).all())
    return [
        AdminInquiryOut(
            id=i.id,
            listing_id=i.listing_id,
            listing_title=titles.get(i.listing_id),
            user_id=i.user_id,
            user_name=names.get(i.user_id),
            type=i.type,
            last_message=i.last_message or "",
            status=i.status,
            date=to_iso(i.date),
        )
        for i in inquiries
    ]


@router.patch("/inquiries/{inquiry_id}", response_model=AdminInquiryOut)
async def admin_update_inquiry(
    inquiry_id: str, body: AdminStatusIn, db: AsyncSession = Depends(get_db)
):
    inquiry = await db.get(Inquiry, inquiry_id)
    if inquiry is None:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    inquiry.status = body.status
    await db.commit()
    await db.refresh(inquiry)
    listing = await db.get(Listing, inquiry.listing_id)
    user = await db.get(User, inquiry.user_id)
    return AdminInquiryOut(
        id=inquiry.id,
        listing_id=inquiry.listing_id,
        listing_title=listing.title if listing else None,
        user_id=inquiry.user_id,
        user_name=user.name if user else None,
        type=inquiry.type,
        last_message=inquiry.last_message or "",
        status=inquiry.status,
        date=to_iso(inquiry.date),
    )


# --------------------------------------------------------------------------- #
# Notifications (compose / broadcast)
# --------------------------------------------------------------------------- #
@router.get("/notifications", response_model=list[NotificationOut])
async def admin_list_notifications(db: AsyncSession = Depends(get_db)):
    from app.api.serializers import notification_out

    rows = (
        (await db.execute(select(Notification).order_by(Notification.date.desc())))
        .scalars()
        .all()
    )
    return [notification_out(n) for n in rows]


@router.post("/notifications", status_code=201)
async def admin_create_notification(
    body: AdminNotificationIn, db: AsyncSession = Depends(get_db)
) -> dict:
    if body.user_id:
        targets = [body.user_id]
    else:
        targets = [r[0] for r in (await db.execute(select(User.id))).all()]  # broadcast
    created = 0
    now = datetime.now(timezone.utc)
    for uid in targets:
        db.add(
            Notification(
                id=new_id("ntf"),
                user_id=uid,
                title=body.title,
                body=body.body,
                type=body.type,
                read=False,
                date=now,
                listing_id=body.listing_id,
            )
        )
        created += 1
    await db.commit()
    return {"ok": True, "created": created}
