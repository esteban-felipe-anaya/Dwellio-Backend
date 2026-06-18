"""Reusable listing filtering: replicates the app's query params exactly
(dealType, q, price/bed/bath/area, type, amenities, map bounds, sort, paging)
plus Haversine distance sort. Plain lat/lng range filtering so it works on both
PostgreSQL and the SQLite fallback (PostGIS is an optional prod upgrade)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.computations import haversine_km
from app.models import Listing, listing_amenities


@dataclass
class ListingFilters:
    deal_type: str | None = None
    q: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    beds: int | None = None
    baths: int | None = None
    type: str | None = None
    min_area: float | None = None
    amenities: list[str] = field(default_factory=list)
    featured: bool | None = None
    sw_lat: float | None = None
    sw_lng: float | None = None
    ne_lat: float | None = None
    ne_lng: float | None = None
    sort: str = "newest"
    user_lat: float | None = None
    user_lng: float | None = None
    page: int | None = None
    limit: int | None = None

    @property
    def has_bounds(self) -> bool:
        return None not in (self.sw_lat, self.sw_lng, self.ne_lat, self.ne_lng)


def build_conditions(f: ListingFilters) -> list:
    conds: list = []
    if f.deal_type:
        conds.append(Listing.deal_type == f.deal_type)
    if f.type:
        conds.append(Listing.property_type_id == f.type)
    if f.q:
        like = f"%{f.q.lower()}%"
        conds.append(
            or_(
                func.lower(Listing.title).like(like),
                func.lower(Listing.address).like(like),
                func.lower(Listing.city).like(like),
            )
        )
    if f.min_price is not None:
        conds.append(Listing.price >= f.min_price)
    if f.max_price is not None:
        conds.append(Listing.price <= f.max_price)
    if f.beds is not None:
        conds.append(Listing.beds >= f.beds)
    if f.baths is not None:
        conds.append(Listing.baths >= f.baths)
    if f.min_area is not None:
        conds.append(Listing.area_sqm >= f.min_area)
    if f.featured is not None:
        conds.append(Listing.featured.is_(f.featured))
    if f.has_bounds:
        conds.append(Listing.lat >= f.sw_lat)
        conds.append(Listing.lat <= f.ne_lat)
        conds.append(Listing.lng >= f.sw_lng)
        conds.append(Listing.lng <= f.ne_lng)
    for amenity_id in f.amenities:
        conds.append(
            select(listing_amenities.c.listing_id)
            .where(
                and_(
                    listing_amenities.c.listing_id == Listing.id,
                    listing_amenities.c.amenity_id == amenity_id,
                )
            )
            .exists()
        )
    return conds


def _sort_key(sort: str):
    if sort == "price_asc":
        return lambda lst: (lst.price, lst.id)
    if sort == "price_desc":
        return lambda lst: (-lst.price, lst.id)
    if sort == "area_desc":
        return lambda lst: (-lst.area_sqm, lst.id)
    return None  # newest / distance handled separately


async def query_listings(
    db: AsyncSession, f: ListingFilters
) -> tuple[list[Listing], int, dict[str, float]]:
    stmt = select(Listing)
    conds = build_conditions(f)
    if conds:
        stmt = stmt.where(and_(*conds))

    items = list((await db.execute(stmt)).scalars().unique().all())

    distances: dict[str, float] = {}
    if f.sort == "distance" and f.user_lat is not None and f.user_lng is not None:
        for lst in items:
            distances[lst.id] = haversine_km(f.user_lat, f.user_lng, lst.lat, lst.lng)
        items.sort(key=lambda lst: distances[lst.id])
    else:
        key = _sort_key(f.sort)
        if key is not None:
            items.sort(key=key)
        else:  # newest (default)
            epoch = datetime.min.replace(tzinfo=timezone.utc)
            items.sort(key=lambda lst: lst.listed_at or epoch, reverse=True)

    total = len(items)
    if f.page and f.limit:
        start = (f.page - 1) * f.limit
        items = items[start : start + f.limit]
    elif f.limit:
        items = items[: f.limit]

    return items, total, distances


async def count_matches(db: AsyncSession, filters_json: dict) -> int:
    """Live 'new matches' count for a saved search's stored filter JSON."""
    f = ListingFilters(
        deal_type=filters_json.get("dealType"),
        q=filters_json.get("q"),
        min_price=filters_json.get("minPrice"),
        max_price=filters_json.get("maxPrice"),
        beds=filters_json.get("beds"),
        baths=filters_json.get("baths"),
        type=filters_json.get("type"),
        min_area=filters_json.get("minArea"),
        amenities=(
            filters_json.get("amenities", [])
            if isinstance(filters_json.get("amenities"), list)
            else (
                str(filters_json.get("amenities", "")).split(",")
                if filters_json.get("amenities")
                else []
            )
        ),
    )
    items, total, _ = await query_listings(db, f)
    return total
