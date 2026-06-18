from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Tour(Base):
    """A scheduled viewing. The *effective* status is computed on read from
    ``scheduled_for`` (requested → confirmed → upcoming → completed), unless a
    terminal/explicit status (cancelled) was set."""

    __tablename__ = "tours"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    listing_id: Mapped[str] = mapped_column(
        String(40), ForeignKey("listings.id", ondelete="CASCADE"), index=True
    )

    # Raw fields the app sends/reads.
    date: Mapped[str] = mapped_column(String(20))  # yyyy-MM-dd
    slot: Mapped[str] = mapped_column(String(20))  # e.g. "2:00 PM"

    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # Stored status; "" means "let it be computed from time".
    status_override: Mapped[str] = mapped_column(String(20), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    user = relationship("User", back_populates="tours")
    listing = relationship("Listing")
