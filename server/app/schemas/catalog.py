from __future__ import annotations

from pydantic import Field

from app.schemas.common import CamelModel


class PropertyTypeOut(CamelModel):
    id: str
    name: str
    icon: str = "home"


class AmenityOut(CamelModel):
    id: str
    name: str
    icon: str = "check"


class ListingOut(CamelModel):
    id: str
    title: str
    deal_type: str  # -> dealType
    price: float
    currency: str = "USD"
    property_type: str  # -> propertyType (slug)
    beds: int = 0
    baths: int = 0
    area_sqm: float = 0  # -> areaSqm
    parking: int = 0
    address: str = ""
    city: str = ""
    lat: float
    lng: float
    amenities: list[str] = []  # amenity slugs
    photos: list[str] = []  # image urls (absolute or /media/...)
    agent_id: str = ""  # -> agentId
    description: str = ""
    featured: bool = False
    listed_at: str | None = None  # -> listedAt (ISO)
    # Derived, computed server-side (the app ignores unknown fields).
    price_per_sqm: float | None = None  # -> pricePerSqm
    distance_km: float | None = None  # -> distanceKm (only when sort=distance)


class ListingCreate(CamelModel):
    title: str
    deal_type: str = "buy"
    price: float = 0
    currency: str = "USD"
    property_type: str = "apartment"
    beds: int = 0
    baths: int = 0
    area_sqm: float = 0
    parking: int = 0
    address: str = ""
    city: str = ""
    lat: float = 0
    lng: float = 0
    amenities: list[str] = []
    photos: list[str] = []
    agent_id: str | None = None
    description: str = ""
    featured: bool = False


class MortgageOut(CamelModel):
    """Server-side mortgage estimate (amortization)."""

    monthly_payment: float
    loan_amount: float
    total_interest: float
    total_paid: float = Field(description="principal + interest over the term")
