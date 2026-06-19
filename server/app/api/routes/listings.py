from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.listing_query import ListingFilters, query_listings
from app.api.serializers import listing_out
from app.core.computations import mortgage_estimate
from app.core.db import get_db
from app.core.security import new_id
from app.models import Amenity, Listing, ListingPhoto, User
from app.schemas.catalog import ListingCreate, ListingOut, MortgageOut

router = APIRouter(tags=["listings"])


@router.get("/listings", response_model=list[ListingOut])
async def list_listings(
    response: Response,
    db: AsyncSession = Depends(get_db),
    deal_type: str | None = Query(None, alias="dealType"),
    q: str | None = None,
    min_price: float | None = Query(None, alias="minPrice"),
    max_price: float | None = Query(None, alias="maxPrice"),
    beds: int | None = None,
    baths: int | None = None,
    type: str | None = None,
    min_area: float | None = Query(None, alias="minArea"),
    amenities: str | None = None,  # comma-separated slugs
    featured: bool | None = None,
    sw_lat: float | None = Query(None, alias="swLat"),
    sw_lng: float | None = Query(None, alias="swLng"),
    ne_lat: float | None = Query(None, alias="neLat"),
    ne_lng: float | None = Query(None, alias="neLng"),
    sort: str = "newest",
    lat: float | None = None,  # user location for sort=distance
    lng: float | None = None,
    page: int | None = Query(None, alias="_page"),
    limit: int | None = Query(None, alias="_limit"),
) -> list[ListingOut]:
    f = ListingFilters(
        deal_type=deal_type,
        q=q,
        min_price=min_price,
        max_price=max_price,
        beds=beds,
        baths=baths,
        type=type,
        min_area=min_area,
        amenities=[a for a in (amenities.split(",") if amenities else []) if a],
        featured=featured,
        sw_lat=sw_lat,
        sw_lng=sw_lng,
        ne_lat=ne_lat,
        ne_lng=ne_lng,
        sort=sort,
        user_lat=lat,
        user_lng=lng,
        page=page,
        limit=limit,
    )
    items, total, distances = await query_listings(db, f)
    response.headers["X-Total-Count"] = str(total)
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    return [listing_out(lst, distances.get(lst.id)) for lst in items]


# Declared before /listings/{id} so the literal segment matches first.
@router.get("/listings/{listing_id}/similar", response_model=list[ListingOut])
async def similar_listings(
    listing_id: str, db: AsyncSession = Depends(get_db)
) -> list[ListingOut]:
    target = await db.get(Listing, listing_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    stmt = (
        select(Listing)
        .where(
            Listing.id != target.id,
            Listing.deal_type == target.deal_type,
            Listing.property_type_id == target.property_type_id,
        )
        .limit(6)
    )
    items = (await db.execute(stmt)).scalars().unique().all()
    return [listing_out(lst) for lst in items]


@router.get("/listings/{listing_id}/mortgage", response_model=MortgageOut)
async def listing_mortgage(
    listing_id: str,
    db: AsyncSession = Depends(get_db),
    down_payment: float = Query(0, alias="downPayment"),
    annual_rate: float = Query(6.5, alias="annualRate"),
    term_years: int = Query(30, alias="termYears"),
    # Accepted but IGNORED — derived amounts are computed server-side only.
    monthly_payment: float | None = Query(None, alias="monthlyPayment"),
) -> MortgageOut:
    listing = await db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    est = mortgage_estimate(listing.price, down_payment, annual_rate, term_years)
    return MortgageOut(**est)


@router.get("/listings/{listing_id}", response_model=ListingOut)
async def get_listing(
    listing_id: str, db: AsyncSession = Depends(get_db)
) -> ListingOut:
    listing = await db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing_out(listing)


@router.post(
    "/listings", response_model=ListingOut, status_code=status.HTTP_201_CREATED
)
async def create_listing(
    body: ListingCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ListingOut:
    listing = Listing(
        id=new_id("lst"),
        title=body.title,
        deal_type=body.deal_type,
        price=body.price,
        currency=body.currency,
        property_type_id=body.property_type,
        beds=body.beds,
        baths=body.baths,
        area_sqm=body.area_sqm,
        parking=body.parking,
        address=body.address,
        city=body.city,
        lat=body.lat,
        lng=body.lng,
        agent_id=body.agent_id,
        owner_id=user.id,
        description=body.description,
        featured=body.featured,
        listed_at=datetime.now(timezone.utc),
    )
    # Assign both collections (even when empty) so they're loaded in memory and
    # never lazy-load during serialization after commit (fails under async).
    listing.photos = [
        ListingPhoto(url=url, position=i) for i, url in enumerate(body.photos)
    ]
    ams = (
        (await db.execute(select(Amenity).where(Amenity.id.in_(body.amenities))))
        .scalars()
        .all()
        if body.amenities
        else []
    )
    listing.amenities = list(ams)
    db.add(listing)
    await db.commit()
    return listing_out(listing)
