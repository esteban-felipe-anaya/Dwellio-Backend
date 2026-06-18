"""Admin-only schemas. Distinct class names from the public ones so OpenAPI
components don't collide."""

from __future__ import annotations

from typing import Any

from pydantic import EmailStr

from app.schemas.common import CamelModel


# --- Listings ---
class AdminListingOut(CamelModel):
    id: str
    title: str
    deal_type: str
    price: float
    currency: str = "USD"
    property_type: str = ""
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
    agent_name: str | None = None
    owner_id: str | None = None
    description: str = ""
    featured: bool = False
    listed_at: str | None = None


class AdminListingIn(CamelModel):
    title: str | None = None
    deal_type: str | None = None
    price: float | None = None
    currency: str | None = None
    property_type: str | None = None
    beds: int | None = None
    baths: int | None = None
    area_sqm: float | None = None
    parking: int | None = None
    address: str | None = None
    city: str | None = None
    lat: float | None = None
    lng: float | None = None
    amenities: list[str] | None = None
    photos: list[str] | None = None
    agent_id: str | None = None
    description: str | None = None
    featured: bool | None = None


# --- Agents ---
class AdminAgentOut(CamelModel):
    id: str
    name: str
    photo: str | None = None
    agency: str = ""
    phone: str = ""
    rating: float = 0
    review_count: int = 0
    listing_count: int = 0


class AdminAgentIn(CamelModel):
    name: str | None = None
    photo: str | None = None
    agency: str | None = None
    phone: str | None = None
    rating: float | None = None
    review_count: int | None = None


# --- Lookups (property types & amenities) ---
class AdminLookupOut(CamelModel):
    id: str
    name: str
    icon: str = ""


class AdminLookupIn(CamelModel):
    id: str | None = None  # slug; auto-generated from name when omitted
    name: str
    icon: str = ""


# --- Users ---
class AdminUserOut(CamelModel):
    id: str
    name: str
    email: EmailStr
    phone: str = ""
    photo: str | None = None
    is_staff: bool = False
    is_superuser: bool = False
    is_active: bool = True
    created_at: str | None = None
    favorites_count: int = 0
    saved_searches_count: int = 0


# --- Tours & inquiries ---
class AdminTourOut(CamelModel):
    id: str
    listing_id: str
    listing_title: str | None = None
    user_id: str
    user_name: str | None = None
    date: str
    slot: str
    status: str
    scheduled_for: str | None = None
    created_at: str | None = None


class AdminStatusIn(CamelModel):
    status: str


class AdminInquiryOut(CamelModel):
    id: str
    listing_id: str
    listing_title: str | None = None
    user_id: str
    user_name: str | None = None
    type: str = "message"
    last_message: str = ""
    status: str = "open"
    date: str | None = None


class AdminSavedSearchOut(CamelModel):
    id: str
    label: str
    filters: dict[str, Any] = {}
    created_at: str | None = None
    user_id: str
    user_name: str | None = None
    new_matches: int = 0


# --- Notifications ---
class AdminNotificationIn(CamelModel):
    title: str
    body: str = ""
    type: str = "system"
    listing_id: str | None = None
    user_id: str | None = None  # None -> broadcast to all users


# --- Uploads ---
class UploadOut(CamelModel):
    url: str


# --- Stats ---
class LabelCount(CamelModel):
    label: str
    value: int


class TimePoint(CamelModel):
    label: str
    value: int


class CityAvg(CamelModel):
    city: str
    avg_price: float


class AgentCount(CamelModel):
    name: str
    value: int


class RecentListing(CamelModel):
    id: str
    title: str
    price: float
    city: str = ""
    deal_type: str = "buy"
    listed_at: str | None = None


class RecentInquiry(CamelModel):
    id: str
    listing_title: str | None = None
    type: str = "message"
    status: str = "open"
    date: str | None = None


class StatsOut(CamelModel):
    total_listings: int
    active_listings: int
    tours_scheduled: int
    open_inquiries: int
    total_users: int
    total_agents: int
    listings_over_time: list[TimePoint] = []
    by_property_type: list[LabelCount] = []
    by_deal_type: list[LabelCount] = []
    avg_price_by_city: list[CityAvg] = []
    top_agents: list[AgentCount] = []
    recent_listings: list[RecentListing] = []
    recent_inquiries: list[RecentInquiry] = []
