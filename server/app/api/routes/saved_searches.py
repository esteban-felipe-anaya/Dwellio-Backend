from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.listing_query import count_matches
from app.api.serializers import saved_search_out
from app.core.db import get_db
from app.core.security import new_id
from app.models import SavedSearch, User
from app.schemas.engagement import SavedSearchCreate, SavedSearchOut

router = APIRouter(tags=["saved-searches"])


@router.get("/saved-searches", response_model=list[SavedSearchOut])
async def list_saved_searches(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[SavedSearchOut]:
    rows = (
        (
            await db.execute(
                select(SavedSearch)
                .where(SavedSearch.user_id == user.id)
                .order_by(SavedSearch.created_at.desc())
            )
        )
        .scalars()
        .all()
    )
    out = []
    for s in rows:
        matches = await count_matches(db, s.filters or {})
        out.append(saved_search_out(s, matches))
    return out


@router.post(
    "/saved-searches",
    response_model=SavedSearchOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_saved_search(
    body: SavedSearchCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SavedSearchOut:
    search = SavedSearch(
        id=new_id("srch"),
        user_id=user.id,
        label=body.label,
        filters=body.filters or {},
    )
    db.add(search)
    await db.commit()
    await db.refresh(search)
    matches = await count_matches(db, search.filters or {})
    return saved_search_out(search, matches)
