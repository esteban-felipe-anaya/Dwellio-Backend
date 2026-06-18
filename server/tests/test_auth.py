from __future__ import annotations

from httpx import AsyncClient

from tests.conftest import auth_header


async def test_login_returns_token_and_user(client: AsyncClient):
    res = await client.post(
        "/auth/login", json={"email": "demo@dwellio.app", "password": "password"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "token" in data and data["token"]
    assert data["user"]["email"] == "demo@dwellio.app"
    # camelCase parity
    assert "isStaff" in data["user"]


async def test_login_ignores_stale_authorization_header(client: AsyncClient):
    # A bogus/expired token in the header must NOT block logging in.
    res = await client.post(
        "/auth/login",
        json={"email": "demo@dwellio.app", "password": "password"},
        headers={"Authorization": "Bearer not.a.real.token"},
    )
    assert res.status_code == 200
    assert res.json()["token"]


async def test_login_wrong_password_401(client: AsyncClient):
    res = await client.post(
        "/auth/login", json={"email": "demo@dwellio.app", "password": "nope"}
    )
    assert res.status_code == 401


async def test_register_then_me(client: AsyncClient):
    res = await client.post(
        "/auth/register",
        json={"name": "New", "email": "new@dwellio.app", "password": "secret1"},
    )
    assert res.status_code == 201
    token = res.json()["token"]
    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["user"]["email"] == "new@dwellio.app"


async def test_me_requires_auth(client: AsyncClient):
    assert (await client.get("/auth/me")).status_code == 401


async def test_favorites_round_trip(client: AsyncClient):
    headers = await auth_header(client)
    assert (await client.get("/favorites", headers=headers)).json() == []
    await client.post("/favorites", json={"listingId": "lst_austin"}, headers=headers)
    assert (await client.get("/favorites", headers=headers)).json() == ["lst_austin"]
    await client.delete("/favorites/lst_austin", headers=headers)
    assert (await client.get("/favorites", headers=headers)).json() == []
