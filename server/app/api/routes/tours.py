from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.serializers import tour_out
from app.core.computations import parse_scheduled_for
from app.core.db import get_db
from app.core.security import new_id
from app.models import Inquiry, InquiryMessage, Listing, Tour, User
from app.schemas.tours import TourCreate, TourOut

router = APIRouter(tags=["tours"])


@router.post("/tours", response_model=TourOut, status_code=status.HTTP_201_CREATED)
async def schedule_tour(
    body: TourCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TourOut:
    if await db.get(Listing, body.listing_id) is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    tour = Tour(
        id=new_id("tour"),
        user_id=user.id,
        listing_id=body.listing_id,
        date=body.date,
        slot=body.slot,
        scheduled_for=parse_scheduled_for(body.date, body.slot),
    )
    db.add(tour)

    # Surface the request in My Inquiries (mirrors the previous mock behavior).
    msg = f"Tour requested for {body.date} ({body.slot})."
    inquiry = Inquiry(
        id=new_id("inq"),
        user_id=user.id,
        listing_id=body.listing_id,
        type="tour",
        last_message=msg,
        status="pending",
        date=datetime.now(timezone.utc),
    )
    inquiry.messages.append(InquiryMessage(sender="user", text=msg))
    db.add(inquiry)

    await db.commit()
    await db.refresh(tour)
    return tour_out(tour)
