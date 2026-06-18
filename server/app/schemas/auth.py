from __future__ import annotations

from pydantic import EmailStr, Field

from app.schemas.common import CamelModel


class UserOut(CamelModel):
    id: str
    name: str
    email: EmailStr
    phone: str = ""
    photo: str | None = None
    is_staff: bool = False
    is_superuser: bool = False


class LoginIn(CamelModel):
    email: EmailStr
    password: str


class RegisterIn(CamelModel):
    name: str = "New User"
    email: EmailStr
    password: str = Field(min_length=4)
    phone: str = ""


class ProfileUpdate(CamelModel):
    name: str | None = None
    phone: str | None = None
    photo: str | None = None
    password: str | None = Field(default=None, min_length=4)


class AuthResponse(CamelModel):
    """Matches the app's AuthResponse: ``{ token, user }`` (+ optional refresh)."""

    token: str
    refresh: str | None = None
    user: UserOut


class MeResponse(CamelModel):
    user: UserOut
