"""Application services that orchestrate calculation and catalog boundaries."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from mortgage_mcp.calculator import calculate_mortgage
from mortgage_mcp.domain import MortgageRequest, MortgageResult, ProductType
from mortgage_mcp.providers import MortgageCatalog, ProductDefinition, RateQuote


class CalculationResponse(BaseModel):
    """A calculation with rate provenance and a bounded schedule window."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    calculation: MortgageResult
    rate: RateQuote
    schedule_total_periods: int
    schedule_offset: int
    schedule_count: int


class ComparisonItem(BaseModel):
    """Comparable summary for one product."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    product_type: ProductType
    first_month_payment_eur: Decimal
    total_payment_eur: Decimal
    total_interest_eur: Decimal
    annual_interest_percent: Decimal
    rate: RateQuote


class ComparisonResponse(BaseModel):
    """Side-by-side scenarios without a product recommendation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    currency: str = "EUR"
    calculation_version: str = "v1"
    scenarios: tuple[ComparisonItem, ...]
    disclaimer: str


class ProductCatalogResponse(BaseModel):
    """Products available from the configured provider."""

    products: tuple[ProductDefinition, ...]


class RateCatalogResponse(BaseModel):
    """Current rates with provider metadata."""

    as_of: date
    rates: tuple[RateQuote, ...]


class MortgageService:
    """Use cases shared by MCP and future delivery adapters."""

    def __init__(self, catalog: MortgageCatalog) -> None:
        self._catalog = catalog

    def calculate(
        self,
        *,
        principal_eur: str,
        term_years: int,
        product_type: ProductType,
        fixed_rate_years: int,
        start_date: date,
        rate_date: date,
        schedule_offset: int = 0,
        schedule_limit: int = 12,
    ) -> CalculationResponse:
        quote = self._catalog.get_rate(product_type, fixed_rate_years, rate_date)
        request = MortgageRequest.model_validate(
            {
                "principal_eur": principal_eur,
                "annual_interest_percent": quote.annual_interest_percent,
                "term_years": term_years,
                "product_type": product_type,
                "start_date": start_date,
                "fixed_rate_years": fixed_rate_years,
            }
        )
        full_result = calculate_mortgage(request)
        schedule = full_result.schedule[schedule_offset : schedule_offset + schedule_limit]
        return CalculationResponse(
            calculation=full_result.model_copy(update={"schedule": schedule}),
            rate=quote,
            schedule_total_periods=len(full_result.schedule),
            schedule_offset=schedule_offset,
            schedule_count=len(schedule),
        )

    def compare(
        self,
        *,
        principal_eur: str,
        term_years: int,
        fixed_rate_years: int,
        start_date: date,
        rate_date: date,
    ) -> ComparisonResponse:
        scenarios = []
        for product_type in ProductType:
            response = self.calculate(
                principal_eur=principal_eur,
                term_years=term_years,
                product_type=product_type,
                fixed_rate_years=fixed_rate_years,
                start_date=start_date,
                rate_date=rate_date,
                schedule_limit=1,
            )
            result = response.calculation
            scenarios.append(
                ComparisonItem(
                    product_type=product_type,
                    first_month_payment_eur=result.monthly_payment_eur,
                    total_payment_eur=result.total_payment_eur,
                    total_interest_eur=result.total_interest_eur,
                    annual_interest_percent=result.annual_interest_percent,
                    rate=response.rate,
                )
            )
        return ComparisonResponse(
            scenarios=tuple(scenarios),
            disclaimer="Indicative comparison; no product recommendation or financial advice.",
        )

    def list_products(self) -> ProductCatalogResponse:
        return ProductCatalogResponse(products=self._catalog.list_products())

    def list_rates(self, as_of: date) -> RateCatalogResponse:
        return RateCatalogResponse(as_of=as_of, rates=self._catalog.list_rates(as_of))
