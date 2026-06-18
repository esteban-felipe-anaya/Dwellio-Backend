"""SQLAlchemy models. Importing this package registers every table on
``Base.metadata`` (needed for create_all and Alembic autogenerate)."""

from app.models.accounts import User
from app.models.agents import Agent
from app.models.catalog import (
    Amenity,
    Listing,
    ListingPhoto,
    PropertyType,
    listing_amenities,
)
from app.models.engagement import (
    Favorite,
    Inquiry,
    InquiryMessage,
    Notification,
    SavedSearch,
)
from app.models.tours import Tour

__all__ = [
    "User",
    "Agent",
    "PropertyType",
    "Amenity",
    "Listing",
    "ListingPhoto",
    "listing_amenities",
    "Favorite",
    "SavedSearch",
    "Inquiry",
    "InquiryMessage",
    "Notification",
    "Tour",
]
