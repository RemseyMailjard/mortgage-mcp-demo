"""Tests for mortgage input validation."""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from mortgage_mcp.domain import MortgageRequest, ProductType


def valid_request(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "principal_eur": "300000.00",
        "annual_interest_percent": "4.125",
        "term_years": 30,
        "product_type": ProductType.ANNUITY,
        "start_date": date(2026, 9, 10),
        "fixed_rate_years": 10,
    }
    values.update(overrides)
    return values


def test_accepts_exact_decimal_inputs() -> None:
    request = MortgageRequest.model_validate(valid_request())

    assert request.principal_eur == Decimal("300000.00")
    assert request.annual_interest_percent == Decimal("4.125")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("principal_eur", "0"),
        ("principal_eur", "100.001"),
        ("annual_interest_percent", "25.000001"),
        ("term_years", 41),
    ],
)
def test_rejects_out_of_range_or_overprecise_values(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        MortgageRequest.model_validate(valid_request(**{field: value}))


def test_rejects_binary_float_for_financial_values() -> None:
    with pytest.raises(ValidationError, match="decimal values must be supplied"):
        MortgageRequest.model_validate(valid_request(principal_eur=300000.01))


def test_rejects_fixed_rate_longer_than_term() -> None:
    with pytest.raises(ValidationError, match="fixed_rate_years cannot exceed term_years"):
        MortgageRequest.model_validate(valid_request(term_years=10, fixed_rate_years=20))


def test_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        MortgageRequest.model_validate(valid_request(customer_name="Example Customer"))