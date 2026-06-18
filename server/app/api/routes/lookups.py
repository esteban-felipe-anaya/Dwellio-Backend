from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models import Amenity, PropertyType
from app.schemas.catalog import AmenityOut, PropertyTypeOut

router = APIRouter(tags=["lookups"])


@router.get("/property-types", response_model=list[PropertyTypeOut])
async def property_types(db: AsyncSession = Depends(get_db)) -> list[PropertyTypeOut]:
    rows = (
        (await db.execute(select(PropertyType).order_by(PropertyType.name)))
        .scalars()
        .all()
    )
    return [PropertyTypeOut.model_validate(r) for r in rows]


@router.get("/amenities", response_model=list[AmenityOut])
async def amenities(db: AsyncSession = Depends(get_db)) -> list[AmenityOut]:
    rows = (await db.execute(select(Amenity).order_by(Amenity.name))).scalars().all()
    return [AmenityOut.model_validate(r) for r in rows]
