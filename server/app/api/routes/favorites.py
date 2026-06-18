from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import Favorite, User
from app.schemas.engagement import FavoriteCreate

router = APIRouter(tags=["favorites"])


# The app expects GET /favorites -> a plain array of listing-id strings.
@router.get("/favorites", response_model=list[str])
async def list_favorites(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[str]:
    rows = await db.execute(
        select(Favorite.listing_id).where(Favorite.user_id == user.id)
    )
    return [r[0] for r in rows.all()]


@router.post("/favorites", status_code=201)
async def add_favorite(
    body: FavoriteCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    existing = await db.get(
        Favorite, {"user_id": user.id, "listing_id": body.listing_id}
    )
    if existing is None:
        db.add(Favorite(user_id=user.id, listing_id=body.listing_id))
        await db.commit()
    return {"listingId": body.listing_id}


@router.delete("/favorites/{listing_id}")
async def remove_favorite(
    listing_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    fav = await db.get(Favorite, {"user_id": user.id, "listing_id": listing_id})
    if fav is not None:
        await db.delete(fav)
        await db.commit()
    return {"ok": True}
