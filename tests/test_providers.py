"""Tests for replaceable mortgage catalog providers."""

from datetime import date
from decimal import Decimal

import pytest

from mortgage_mcp.domain import ProductType
from mortgage_mcp.providers import FixtureMortgageCatalog, RateDataUnavailableError


def test_fixture_exposes_dated_demo_provenance() -> None:
    catalog = FixtureMortgageCatalog()

    quote = catalog.get_rate(ProductType.ANNUITY, 10, date(2026, 9, 10))

    assert quote.annual_interest_percent == Decimal("4.00")
    assert quote.effective_date == date(2026, 9, 10)
    assert quote.source_reference.startswith("demo://")
    assert quote.is_demo_data is True


def test_fixture_lists_supported_products() -> None:
    products = FixtureMortgageCatalog().list_products()

    assert {product.product_type for product in products} == set(ProductType)
    assert all(product.fixed_rate_periods_years == (5, 10, 20) for product in products)


def test_stale_data_fails_explicitly() -> None:
    with pytest.raises(RateDataUnavailableError, match="No current demo rates"):
        FixtureMortgageCatalog().list_rates(date(2027, 1, 1))


def test_missing_product_rate_fails_explicitly() -> None:
    with pytest.raises(RateDataUnavailableError, match="No rate is available"):
        FixtureMortgageCatalog().get_rate(ProductType.LINEAR, 5, date(2026, 9, 10))