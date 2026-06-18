from __future__ import annotations

from typing import Any

from pydantic import Field

from app.schemas.common import CamelModel


class FavoriteCreate(CamelModel):
    listing_id: str  # <- listingId


class SavedSearchOut(CamelModel):
    id: str
    label: str
    filters: dict[str, Any] = {}
    created_at: str | None = None  # -> createdAt
    # Derived live: how many current listings match this saved search.
    new_matches: int = 0  # -> newMatches


class SavedSearchCreate(CamelModel):
    label: str
    filters: dict[str, Any] = {}
    created_at: str | None = None


class InquiryMessageOut(CamelModel):
    # The app uses the JSON key "from"; "from" is a Python keyword.
    sender: str = Field(alias="from")
    text: str
    at: str | None = None


class InquiryOut(CamelModel):
    id: str
    listing_id: str  # -> listingId
    type: str = "message"
    last_message: str = ""  # -> lastMessage
    status: str = "open"
    date: str | None = None
    messages: list[InquiryMessageOut] = []


class InquiryCreate(CamelModel):
    listing_id: str  # -> listingId
    message: str


class NotificationOut(CamelModel):
    id: str
    title: str
    body: str = ""
    type: str = "system"
    read: bool = False
    date: str | None = None
    listing_id: str | None = None  # -> listingId
