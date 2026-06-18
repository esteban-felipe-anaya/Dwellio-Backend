"""Pure, server-side derived computations. Never trust the client for these."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone


# --- Mortgage (standard amortization) ---------------------------------------
def mortgage_estimate(
    price: float,
    down_payment: float = 0.0,
    annual_rate_percent: float = 6.5,
    term_years: int = 30,
) -> dict[str, float]:
    principal = max(0.0, float(price) - max(0.0, float(down_payment)))
    n = max(0, int(term_years)) * 12
    if principal <= 0 or n <= 0:
        return {
            "monthly_payment": 0.0,
            "loan_amount": 0.0,
            "total_interest": 0.0,
            "total_paid": 0.0,
        }
    r = float(annual_rate_percent) / 100.0 / 12.0
    if r == 0:
        monthly = principal / n
    else:
        factor = math.pow(1 + r, -n)
        monthly = principal * r / (1 - factor)
    total_paid = monthly * n
    return {
        "monthly_payment": round(monthly, 2),
        "loan_amount": round(principal, 2),
        "total_interest": round(total_paid - principal, 2),
        "total_paid": round(total_paid, 2),
    }


def price_per_sqm(price: float, area_sqm: float) -> float | None:
    if not area_sqm or area_sqm <= 0:
        return None
    return round(float(price) / float(area_sqm), 2)


# --- Haversine distance ------------------------------------------------------
def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius = 6371.0  # km
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    return round(radius * 2 * math.asin(math.sqrt(a)), 3)


# --- Tour time-based status --------------------------------------------------
def parse_scheduled_for(date: str, slot: str) -> datetime:
    """Combine ``yyyy-MM-dd`` + ``2:00 PM`` into a UTC datetime."""
    for fmt in ("%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(f"{date} {slot}".strip(), fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return datetime.now(timezone.utc) + timedelta(days=1)


def tour_status(
    scheduled_for: datetime,
    created_at: datetime,
    override: str = "",
    now: datetime | None = None,
) -> str:
    """requested → confirmed → upcoming → completed, computed from time.
    A terminal ``cancelled`` override stays authoritative."""
    if override == "cancelled":
        return "cancelled"
    now = now or datetime.now(timezone.utc)
    if scheduled_for.tzinfo is None:
        scheduled_for = scheduled_for.replace(tzinfo=timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    if now >= scheduled_for + timedelta(hours=2):
        return "completed"
    if scheduled_for - now <= timedelta(hours=48):
        return "upcoming"
    if override == "confirmed" or now - created_at >= timedelta(hours=1):
        return "confirmed"
    return "requested"
