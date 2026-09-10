"""MCP server entry point and transport adapter."""

import os
from datetime import date
from typing import Annotated

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field, ValidationError

from mortgage_mcp.domain import ProductType
from mortgage_mcp.providers import FixtureMortgageCatalog, RateDataUnavailableError
from mortgage_mcp.security import log_operational_event, require_local_transport
from mortgage_mcp.service import (
    CalculationResponse,
    ComparisonResponse,
    MortgageService,
    ProductCatalogResponse,
    RateCatalogResponse,
)

mcp = MCPServer(
    "Rabobank Mortgage Demo",
    instructions=(
        "Provide transparent, indicative mortgage calculations. "
        "Never describe results as approval, an offer, or personalized financial advice."
    ),
)
service = MortgageService(FixtureMortgageCatalog())


@mcp.tool(title="Check server health")
def health() -> str:
    """Return the service health status."""
    return "ok"


@mcp.tool(title="Calculate an indicative mortgage")
def calculate_mortgage(
    principal_eur: str,
    term_years: int,
    product_type: ProductType,
    fixed_rate_years: int,
    start_date: date,
    rate_date: date,
    schedule_offset: Annotated[int, Field(ge=0)] = 0,
    schedule_limit: Annotated[int, Field(ge=1, le=120)] = 12,
) -> CalculationResponse:
    """Calculate one scenario using a dated provider rate and a bounded schedule page."""
    try:
        response = service.calculate(
            principal_eur=principal_eur,
            term_years=term_years,
            product_type=product_type,
            fixed_rate_years=fixed_rate_years,
            start_date=start_date,
            rate_date=rate_date,
            schedule_offset=schedule_offset,
            schedule_limit=schedule_limit,
        )
        log_operational_event("mortgage_calculation_completed")
        return response
    except (ValidationError, RateDataUnavailableError) as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(title="Compare mortgage products")
def compare_mortgages(
    principal_eur: str,
    term_years: int,
    fixed_rate_years: int,
    start_date: date,
    rate_date: date,
) -> ComparisonResponse:
    """Compare supported products using equal inputs without recommending one."""
    try:
        response = service.compare(
            principal_eur=principal_eur,
            term_years=term_years,
            fixed_rate_years=fixed_rate_years,
            start_date=start_date,
            rate_date=rate_date,
        )
        log_operational_event("mortgage_comparison_completed")
        return response
    except (ValidationError, RateDataUnavailableError) as exc:
        raise ToolError(str(exc)) from exc


@mcp.tool(title="List mortgage products")
def list_mortgage_products() -> ProductCatalogResponse:
    """List products and constraints from the configured provider."""
    return service.list_products()


@mcp.tool(title="Get dated interest rates")
def get_interest_rates(as_of: date) -> RateCatalogResponse:
    """Return available rates with effective dates and source metadata."""
    try:
        return service.list_rates(as_of)
    except RateDataUnavailableError as exc:
        raise ToolError(str(exc)) from exc


@mcp.resource("mortgage://disclaimer", title="Mortgage calculation disclaimer")
def disclaimer() -> str:
    """Explain the limits of this independent demonstration."""
    return (
        "Dit is een onafhankelijke demo en is niet verbonden aan of goedgekeurd door Rabobank. "
        "Uitkomsten zijn indicatief en vormen geen aanbod, kredietbesluit of persoonlijk advies."
    )


def main() -> None:
    """Run the MCP server over stdio."""
    require_local_transport(os.getenv("MORTGAGE_MCP_TRANSPORT", "stdio"))
    mcp.run()


if __name__ == "__main__":
    main()
