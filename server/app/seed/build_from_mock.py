"""One-off: migrate the legacy json-server `mock-api/db.json` into this
backend's `seed_data.json`. Run once; the output is committed.

    python -m app.seed.build_from_mock --mock ../../mock-api/db.json
"""

from __future__ import annotations

import argparse
import json
import os

HERE = os.path.dirname(__file__)


def build(mock_path: str) -> dict:
    with open(mock_path, encoding="utf-8") as fh:
        db = json.load(fh)

    demo = db["users"][0]
    demo_id = demo["id"]

    users = [
        {
            "id": demo_id,
            "name": demo["name"],
            "email": demo["email"],
            "phone": demo.get("phone", ""),
            "photo": demo.get("photo"),
            "password": demo.get("password", "password"),
            "isStaff": False,
            "isSuperuser": False,
        },
        {
            "id": "usr_admin",
            "name": "Dwellio Admin",
            "email": "admin@dwellio.app",
            "phone": "+1 (555) 000-0000",
            "photo": "https://randomuser.me/api/portraits/men/32.jpg",
            "password": "password",
            "isStaff": True,
            "isSuperuser": True,
        },
    ]

    # Agent avatars -> randomuser.me (per the brief).
    agents = []
    for i, a in enumerate(db["agents"]):
        gender = "women" if i % 2 == 0 else "men"
        agents.append(
            {
                "id": a["id"],
                "name": a["name"],
                "photo": f"https://randomuser.me/api/portraits/{gender}/{(i * 7) % 90}.jpg",
                "agency": a.get("agency", ""),
                "phone": a.get("phone", ""),
                "rating": a.get("rating", 0),
                "reviewCount": a.get("reviewCount", 0),
            }
        )

    listings = [
        {
            "id": lst["id"],
            "title": lst["title"],
            "dealType": lst["dealType"],
            "price": lst["price"],
            "currency": lst.get("currency", "USD"),
            "propertyType": lst["propertyType"],
            "beds": lst.get("beds", 0),
            "baths": lst.get("baths", 0),
            "areaSqm": lst.get("areaSqm", 0),
            "parking": lst.get("parking", 0),
            "address": lst.get("address", ""),
            "city": lst.get("city", ""),
            "lat": lst["lat"],
            "lng": lst["lng"],
            "amenities": lst.get("amenities", []),
            "photos": lst.get("photos", []),
            "agentId": lst.get("agentId"),
            "description": lst.get("description", ""),
            "featured": lst.get("featured", False),
            "listedAt": lst.get("listedAt"),
        }
        for lst in db["listings"]
    ]

    favorites = [
        {"userId": demo_id, "listingId": lid} for lid in db.get("favorites", [])
    ]

    saved_searches = [
        {
            "id": s["id"],
            "userId": demo_id,
            "label": s["label"],
            "filters": s.get("filters", {}),
            "createdAt": s.get("createdAt"),
        }
        for s in db.get("saved-searches", [])
    ]

    inquiries = [
        {
            "id": i["id"],
            "userId": demo_id,
            "listingId": i["listingId"],
            "type": i.get("type", "message"),
            "lastMessage": i.get("lastMessage", ""),
            "status": i.get("status", "open"),
            "date": i.get("date"),
            "messages": i.get("messages", []),
        }
        for i in db.get("inquiries", [])
    ]

    notifications = [
        {
            "id": n["id"],
            "userId": demo_id,
            "title": n["title"],
            "body": n.get("body", ""),
            "type": n.get("type", "system"),
            "read": n.get("read", False),
            "date": n.get("date"),
            "listingId": n.get("listingId"),
        }
        for n in db.get("notifications", [])
    ]

    # Synthetic tours, stamped relative to "now" at import time so the
    # time-based status flow (requested -> confirmed -> upcoming -> completed)
    # looks live. `daysFromNow` is resolved by the importer.
    tours = [
        {
            "id": "tour_seed01",
            "userId": demo_id,
            "listingId": listings[2]["id"],
            "slot": "2:00 PM",
            "daysFromNow": 1,
        },
        {
            "id": "tour_seed02",
            "userId": demo_id,
            "listingId": listings[5]["id"],
            "slot": "11:00 AM",
            "daysFromNow": 5,
        },
        {
            "id": "tour_seed03",
            "userId": demo_id,
            "listingId": listings[8]["id"],
            "slot": "9:00 AM",
            "daysFromNow": -2,
        },
    ]

    return {
        "users": users,
        "agents": agents,
        "propertyTypes": db["property-types"],
        "amenities": db["amenities"],
        "listings": listings,
        "favorites": favorites,
        "savedSearches": saved_searches,
        "tours": tours,
        "inquiries": inquiries,
        "notifications": notifications,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mock",
        default=os.path.join(HERE, "..", "..", "..", "..", "mock-api", "db.json"),
    )
    parser.add_argument("--out", default=os.path.join(HERE, "seed_data.json"))
    args = parser.parse_args()
    data = build(os.path.abspath(args.mock))
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    print(f"Wrote {args.out}: " + ", ".join(f"{k}={len(v)}" for k, v in data.items()))


if __name__ == "__main__":
    main()
