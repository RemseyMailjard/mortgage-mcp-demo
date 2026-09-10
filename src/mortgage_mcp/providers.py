"""Replaceable product and interest-rate providers."""

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict

from mortgage_mcp.domain import AnnualRate, ProductType


class RateDataUnavailableError(RuntimeError):
    """Raised when no current, matching rate data is available."""


class ProductDefinition(BaseModel):
    """A mortgage product exposed by a catalog."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    product_type: ProductType
    display_name_nl: str
    minimum_term_years: int
    maximum_term_years: int
    fixed_rate_periods_years: tuple[int, ...]


class RateQuote(BaseModel):
    """A dated interest-rate quote with source provenance."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    product_type: ProductType
    fixed_rate_years: int
    annual_interest_percent: AnnualRate
    effective_date: date
    valid_until: date
    provider: str
    source_reference: str
    retrieved_date: date
    is_demo_data: bool


class CatalogData(BaseModel):
    """Validated serialized catalog structure."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    products: tuple[ProductDefinition, ...]
    rates: tuple[RateQuote, ...]


class MortgageCatalog(Protocol):
    """Boundary for Rabobank-approved or demo mortgage data."""

    def list_products(self) -> tuple[ProductDefinition, ...]: ...

    def list_rates(self, as_of: date) -> tuple[RateQuote, ...]: ...

    def get_rate(
        self, product_type: ProductType, fixed_rate_years: int, as_of: date
    ) -> RateQuote: ...


class FixtureMortgageCatalog:
    """Catalog loaded from reviewed, static demo JSON."""

    def __init__(self, fixture_path: Path | None = None) -> None:
        path = fixture_path or Path(__file__).with_name("data") / "demo_rates.json"
        self._data = CatalogData.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def list_products(self) -> tuple[ProductDefinition, ...]:
        return self._data.products

    def list_rates(self, as_of: date) -> tuple[RateQuote, ...]:
        rates = tuple(
            rate
            for rate in self._data.rates
            if rate.effective_date <= as_of <= rate.valid_until
        )
        if not rates:
            raise RateDataUnavailableError(
                f"No current demo rates are available for {as_of.isoformat()}"
            )
        return rates

    def get_rate(
        self, product_type: ProductType, fixed_rate_years: int, as_of: date
    ) -> RateQuote:
        for rate in self.list_rates(as_of):
            if rate.product_type is product_type and rate.fixed_rate_years == fixed_rate_years:
                return rate
        raise RateDataUnavailableError(
            f"No rate is available for {product_type.value} "
            f"with {fixed_rate_years} fixed-rate years"
        )


def decimal_rate(quote: RateQuote) -> Decimal:
    """Return the quote rate as an explicit Decimal for calculation input."""
    return quote.annual_interest_percent
