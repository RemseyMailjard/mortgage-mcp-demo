"""Tests for the mortgage calculation engine."""

from datetime import date
from decimal import Decimal

import pytest

from mortgage_mcp.calculator import calculate_mortgage
from mortgage_mcp.domain import MortgageRequest, ProductType


def request_for(product_type: ProductType, **overrides: object) -> MortgageRequest:
    values: dict[str, object] = {
        "principal_eur": "300000",
        "annual_interest_percent": "4",
        "term_years": 30,
        "product_type": product_type,
        "start_date": date(2026, 9, 10),
    }
    values.update(overrides)
    return MortgageRequest.model_validate(values)


@pytest.mark.parametrize("product_type", list(ProductType))
def test_schedule_reconciles_principal_and_finishes_at_zero(product_type: ProductType) -> None:
    result = calculate_mortgage(request_for(product_type))

    assert len(result.schedule) == 360
    assert sum(line.principal_eur for line in result.schedule) == Decimal("300000.00")
    assert result.schedule[-1].remaining_balance_eur == Decimal("0")
    assert all(line.remaining_balance_eur >= 0 for line in result.schedule)
    assert result.total_payment_eur == result.principal_eur + result.total_interest_eur


def test_annuity_matches_independently_verified_first_payment() -> None:
    result = calculate_mortgage(request_for(ProductType.ANNUITY))

    assert result.monthly_payment_eur == Decimal("1432.25")
    assert result.schedule[0].interest_eur == Decimal("1000.00")
    assert result.schedule[0].principal_eur == Decimal("432.25")


def test_linear_matches_independently_verified_first_payment() -> None:
    result = calculate_mortgage(request_for(ProductType.LINEAR))

    assert result.monthly_payment_eur == Decimal("1833.33")
    assert result.schedule[0].interest_eur == Decimal("1000.00")
    assert result.schedule[0].principal_eur == Decimal("833.33")
    assert result.schedule[1].payment_eur == Decimal("1830.55")


def test_zero_rate_is_handled_without_division_by_zero() -> None:
    result = calculate_mortgage(
        request_for(
            ProductType.ANNUITY,
            principal_eur="1200",
            annual_interest_percent="0",
            term_years=1,
        )
    )

    assert result.monthly_payment_eur == Decimal("100.00")
    assert result.total_interest_eur == Decimal("0.00")
    assert result.total_payment_eur == Decimal("1200.00")