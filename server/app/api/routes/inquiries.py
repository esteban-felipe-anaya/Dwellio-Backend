from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.serializers import inquiry_out
from app.core.db import get_db
from app.core.security import new_id
from app.models import Inquiry, InquiryMessage, Listing, User
from app.schemas.engagement import InquiryCreate, InquiryOut

router = APIRouter(tags=["inquiries"])


@router.get("/inquiries", response_model=list[InquiryOut])
async def list_inquiries(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[InquiryOut]:
    rows = (
        (
            await db.execute(
                select(Inquiry)
                .where(Inquiry.user_id == user.id)
                .order_by(Inquiry.date.desc())
            )
        )
        .scalars()
        .all()
    )
    return [inquiry_out(i) for i in rows]


@router.post(
    "/inquiries", response_model=InquiryOut, status_code=status.HTTP_201_CREATED
)
async def create_inquiry(
    body: InquiryCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InquiryOut:
    if await db.get(Listing, body.listing_id) is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    inquiry = Inquiry(
        id=new_id("inq"),
        user_id=user.id,
        listing_id=body.listing_id,
        type="message",
        last_message=body.message,
        status="open",
        date=datetime.now(timezone.utc),
    )
    inquiry.messages.append(InquiryMessage(sender="user", text=body.message))
    db.add(inquiry)
    await db.commit()
    await db.refresh(inquiry)
    return inquiry_out(inquiry)
