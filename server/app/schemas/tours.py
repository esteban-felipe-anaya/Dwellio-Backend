from __future__ import annotations

from app.schemas.common import CamelModel


class TourOut(CamelModel):
    id: str
    listing_id: str  # -> listingId
    date: str
    slot: str
    status: str = "requested"


class TourCreate(CamelModel):
    listing_id: str  # -> listingId
    date: str
    slot: str
