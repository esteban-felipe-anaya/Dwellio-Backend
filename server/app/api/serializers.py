"""Build contract-shaped Pydantic responses from ORM objects.

Centralizing the mapping keeps every route emitting the exact JSON the Flutter
app expects (camelCase, slugs for property type/amenities, ISO dates, derived
numbers as JSON numbers)."""

from __future__ import annotations

from app.core.computations import price_per_sqm, tour_status
from app.models import (
    Agent,
    Inquiry,
    Listing,
    Notification,
    SavedSearch,
    Tour,
    User,
)
from app.schemas.agents import AgentOut
from app.schemas.auth import UserOut
from app.schemas.catalog import ListingOut
from app.schemas.common import to_iso
from app.schemas.engagement import (
    InquiryMessageOut,
    InquiryOut,
    NotificationOut,
    SavedSearchOut,
)
from app.schemas.tours import TourOut


def user_out(u: User) -> UserOut:
    return UserOut(
        id=u.id,
        name=u.name,
        email=u.email,
        phone=u.phone or "",
        photo=u.photo,
        is_staff=u.is_staff,
        is_superuser=u.is_superuser,
    )


def agent_out(a: Agent) -> AgentOut:
    return AgentOut(
        id=a.id,
        name=a.name,
        photo=a.photo,
        agency=a.agency or "",
        phone=a.phone or "",
        rating=a.rating or 0,
        review_count=a.review_count or 0,
    )


def listing_out(listing: Listing, distance_km: float | None = None) -> ListingOut:
    return ListingOut(
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
        agent_id=listing.agent_id or "",
        description=listing.description or "",
        featured=listing.featured,
        listed_at=to_iso(listing.listed_at),
        price_per_sqm=price_per_sqm(listing.price, listing.area_sqm),
        distance_km=distance_km,
    )


def saved_search_out(s: SavedSearch, new_matches: int = 0) -> SavedSearchOut:
    return SavedSearchOut(
        id=s.id,
        label=s.label,
        filters=s.filters or {},
        created_at=to_iso(s.created_at),
        new_matches=new_matches,
    )


def inquiry_out(i: Inquiry) -> InquiryOut:
    return InquiryOut(
        id=i.id,
        listing_id=i.listing_id,
        type=i.type,
        last_message=i.last_message or "",
        status=i.status,
        date=to_iso(i.date),
        messages=[
            InquiryMessageOut(**{"from": m.sender, "text": m.text, "at": to_iso(m.at)})
            for m in i.messages
        ],
    )


def notification_out(n: Notification) -> NotificationOut:
    return NotificationOut(
        id=n.id,
        title=n.title,
        body=n.body or "",
        type=n.type,
        read=n.read,
        date=to_iso(n.date),
        listing_id=n.listing_id,
    )


def tour_out(t: Tour) -> TourOut:
    return TourOut(
        id=t.id,
        listing_id=t.listing_id,
        date=t.date,
        slot=t.slot,
        status=tour_status(t.scheduled_for, t.created_at, t.status_override),
    )
