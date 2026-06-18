from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.serializers import user_out
from app.core.db import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    new_id,
    verify_password,
)
from app.models import User
from app.schemas.auth import (
    AuthResponse,
    LoginIn,
    MeResponse,
    ProfileUpdate,
    RegisterIn,
)

router = APIRouter(tags=["auth"])


async def _by_email(db: AsyncSession, email: str) -> User | None:
    res = await db.execute(select(User).where(User.email == email.lower()))
    return res.scalar_one_or_none()


# NOTE: login/register do NOT depend on get_current_user, so a stale or expired
# Authorization header never causes the login itself to 401.
@router.post("/auth/login", response_model=AuthResponse)
async def login(body: LoginIn, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    user = await _by_email(db, body.email)
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return AuthResponse(
        token=create_access_token(user.id),
        refresh=create_refresh_token(user.id),
        user=user_out(user),
    )


@router.post(
    "/auth/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    body: RegisterIn, db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    if await _by_email(db, body.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with that email already exists",
        )
    user = User(
        id=new_id("usr"),
        email=body.email.lower(),
        hashed_password=hash_password(body.password),
        name=body.name or "New User",
        phone=body.phone or "",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return AuthResponse(
        token=create_access_token(user.id),
        refresh=create_refresh_token(user.id),
        user=user_out(user),
    )


@router.get("/auth/me", response_model=MeResponse)
async def me(user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(user=user_out(user))


@router.patch("/auth/me", response_model=MeResponse)
async def update_me(
    body: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MeResponse:
    if body.name is not None:
        user.name = body.name
    if body.phone is not None:
        user.phone = body.phone
    if body.photo is not None:
        user.photo = body.photo
    if body.password:
        user.hashed_password = hash_password(body.password)
    await db.commit()
    await db.refresh(user)
    return MeResponse(user=user_out(user))
