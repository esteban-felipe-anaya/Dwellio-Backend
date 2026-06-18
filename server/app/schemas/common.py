"""Shared Pydantic base: camelCase aliases matching the Flutter app's JSON."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Serializes/validates with camelCase aliases but also accepts snake_case
    (``populate_by_name``) so we can construct instances from ORM attributes."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        ser_json_timedelta="float",
    )


def to_iso(value: datetime | None) -> str | None:
    """ISO-8601 in UTC with a trailing ``Z`` (matches the app's seed format)."""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
