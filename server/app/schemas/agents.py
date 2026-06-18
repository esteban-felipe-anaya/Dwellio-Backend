from __future__ import annotations

from app.schemas.common import CamelModel


class AgentOut(CamelModel):
    id: str
    name: str
    photo: str | None = None
    agency: str = ""
    phone: str = ""
    rating: float = 0
    review_count: int = 0  # -> reviewCount
