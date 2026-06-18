from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Many-to-many: a listing has amenities (referencing the Amenity lookup table).
listing_amenities = Table(
    "listing_amenities",
    Base.metadata,
    Column(
        "listing_id",
        String(40),
        ForeignKey("listings.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "amenity_id",
        String(40),
        ForeignKey("amenities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class PropertyType(Base):
    """Lookup table — replaces a hardcoded constant in the app."""

    __tablename__ = "property_types"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)  # slug
    name: Mapped[str] = mapped_column(String(80))
    icon: Mapped[str] = mapped_column(String(60), default="home")

    listings = relationship("Listing", back_populates="property_type")


class Amenity(Base):
    """Lookup table — replaces a hardcoded constant in the app."""

    __tablename__ = "amenities"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)  # slug
    name: Mapped[str] = mapped_column(String(80))
    icon: Mapped[str] = mapped_column(String(60), default="check")


class ListingPhoto(Base):
    __tablename__ = "listing_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("listings.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(String(700))  # plain str (allows /media/...)
    position: Mapped[int] = mapped_column(Integer, default=0)

    listing = relationship("Listing", back_populates="photos")


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    deal_type: Mapped[str] = mapped_column(String(10), index=True)  # buy | rent
    price: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(8), default="USD")

    property_type_id: Mapped[str | None] = mapped_column(
        String(40), ForeignKey("property_types.id"), index=True, nullable=True
    )
    beds: Mapped[int] = mapped_column(Integer, default=0)
    baths: Mapped[int] = mapped_column(Integer, default=0)
    area_sqm: Mapped[float] = mapped_column(Float, default=0.0)
    parking: Mapped[int] = mapped_column(Integer, default=0)

    address: Mapped[str] = mapped_column(String(300), default="")
    city: Mapped[str] = mapped_column(String(120), default="", index=True)
    lat: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    lng: Mapped[float] = mapped_column(Float, default=0.0, index=True)

    agent_id: Mapped[str | None] = mapped_column(
        String(40), ForeignKey("agents.id"), index=True, nullable=True
    )
    owner_id: Mapped[str | None] = mapped_column(
        String(40), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    description: Mapped[str] = mapped_column(Text, default="")
    featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    listed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )

    property_type = relationship("PropertyType", back_populates="listings")
    agent = relationship("Agent", back_populates="listings")
    photos = relationship(
        "ListingPhoto",
        back_populates="listing",
        cascade="all, delete-orphan",
        order_by="ListingPhoto.position",
        lazy="selectin",
    )
    amenities = relationship("Amenity", secondary=listing_amenities, lazy="selectin")
