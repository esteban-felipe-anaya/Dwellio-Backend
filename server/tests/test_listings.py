from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import auth_header


async def test_create_listing_without_amenities_or_photos(client: AsyncClient):
    # Regression: creating a listing with empty collections must not lazy-load
    # them during serialization (would raise MissingGreenlet under async).
    headers = await auth_header(client)
    res = await client.post(
        "/listings",
        headers=headers,
        json={
            "title": "Bare",
            "dealType": "buy",
            "price": 100,
            "propertyType": "apartment",
            "lat": 1,
            "lng": 1,
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert body["amenities"] == []
    assert body["photos"] == []
    assert body["title"] == "Bare"


async def test_listings_returns_plain_array_with_camelcase(client: AsyncClient):
    res = await client.get("/listings")
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, list)  # plain array, not a wrapper
    item = next(x for x in body if x["id"] == "lst_austin")
    assert item["dealType"] == "buy"
    assert item["propertyType"] == "apartment"
    assert item["areaSqm"] == 90
    assert item["agentId"] == "agt_01"
    assert isinstance(item["price"], (int, float))  # number, not a string
    assert item["pricePerSqm"] is not None


async def test_map_bounds_filter(client: AsyncClient):
    # A bbox over Austin should include the Austin listing and exclude Lisbon.
    res = await client.get(
        "/listings",
        params={"swLat": 30.2, "swLng": -97.85, "neLat": 30.35, "neLng": -97.65},
    )
    ids = {x["id"] for x in res.json()}
    assert "lst_austin" in ids
    assert "lst_lisbon" not in ids


async def test_filters_narrow_results(client: AsyncClient):
    # minPrice above Lisbon's price keeps only Austin.
    res = await client.get("/listings", params={"minPrice": 300000})
    ids = {x["id"] for x in res.json()}
    assert ids == {"lst_austin"}

    # beds filter
    res = await client.get("/listings", params={"beds": 2})
    assert {x["id"] for x in res.json()} == {"lst_austin"}

    # amenity filter (none have 'pool')
    res = await client.get("/listings", params={"amenities": "pool"})
    assert res.json() == []


async def test_total_count_header(client: AsyncClient):
    res = await client.get("/listings", params={"_page": 1, "_limit": 1})
    assert res.headers.get("x-total-count") == "2"
    assert len(res.json()) == 1


async def test_distance_sort(client: AsyncClient):
    # From near Lisbon, the Lisbon listing should sort first.
    res = await client.get(
        "/listings", params={"sort": "distance", "lat": 38.7, "lng": -9.1}
    )
    body = res.json()
    assert body[0]["id"] == "lst_lisbon"
    assert body[0]["distanceKm"] is not None
    assert body[0]["distanceKm"] < body[1]["distanceKm"]


async def test_similar_and_detail(client: AsyncClient):
    detail = await client.get("/listings/lst_austin")
    assert detail.status_code == 200
    assert detail.json()["title"] == "Austin Loft"

    similar = await client.get("/listings/lst_austin/similar")
    assert similar.status_code == 200
    ids = {x["id"] for x in similar.json()}
    assert "lst_austin" not in ids  # never itself
