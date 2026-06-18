from __future__ import annotations

import math

from httpx import AsyncClient

from app.core.computations import mortgage_estimate


def test_mortgage_amortization_formula():
    # $300k loan ($400k - $100k down), 6% APR, 30 years -> ~$1798.65/mo.
    est = mortgage_estimate(400000, 100000, 6, 30)
    assert est["loan_amount"] == 300000
    assert math.isclose(est["monthly_payment"], 1798.65, abs_tol=0.5)
    # total_paid ~= monthly * 360 (allow for independent 2dp rounding).
    assert math.isclose(est["total_paid"], est["monthly_payment"] * 360, abs_tol=1.0)


def test_mortgage_zero_rate_is_straight_line():
    est = mortgage_estimate(120000, 0, 0, 10)
    assert est["monthly_payment"] == 1000  # 120000 / 120
    assert est["total_interest"] == 0


async def test_mortgage_endpoint_is_server_side(client: AsyncClient):
    # Client sends a bogus monthlyPayment=1 — the server must ignore it and
    # compute from the listing price + inputs.
    res = await client.get(
        "/listings/lst_austin/mortgage",
        params={
            "downPayment": 80000,
            "annualRate": 6,
            "termYears": 30,
            "monthlyPayment": 1,  # bogus, must be ignored
        },
    )
    assert res.status_code == 200
    data = res.json()
    expected = mortgage_estimate(400000, 80000, 6, 30)
    assert data["monthlyPayment"] == expected["monthly_payment"]
    assert data["monthlyPayment"] > 100  # definitely not the bogus 1
    assert data["loanAmount"] == 320000
