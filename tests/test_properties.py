"""Property-based invariants for mortgage calculations."""

from datetime import date
from decimal import Decimal

from hypothesis import given, settings
from hypothesis import strategies as st

from mortgage_mcp.calculator import calculate_mortgage
from mortgage_mcp.domain import MortgageRequest, ProductType


@given(
    principal_cents=st.integers(min_value=1, max_value=1_000_000_000),
    rate_millionths=st.integers(min_value=0, max_value=25_000_000),
    term_years=st.integers(min_value=1, max_value=40),
    product_type=st.sampled_from(list(ProductType)),
)
@settings(max_examples=30, deadline=None)
def test_schedule_invariants(
    principal_cents: int,
    rate_millionths: int,
    term_years: int,
    product_type: ProductType,
) -> None:
    principal = Decimal(principal_cents) / 100
    rate = Decimal(rate_millionths) / 1_000_000
    request = MortgageRequest.model_validate(
        {
            "principal_eur": principal,
            "annual_interest_percent": rate,
            "term_years": term_years,
            "product_type": product_type,
            "start_date": date(2026, 9, 10),
        }
    )

    result = calculate_mortgage(request)

    assert len(result.schedule) == term_years * 12
    assert sum(line.principal_eur for line in result.schedule) == principal
    assert result.schedule[-1].remaining_balance_eur == 0
    assert all(line.payment_eur >= 0 for line in result.schedule)
    assert all(line.interest_eur >= 0 for line in result.schedule)
    assert all(line.remaining_balance_eur >= 0 for line in result.schedule)
    assert result.total_payment_eur == result.principal_eur + result.total_interest_eur
