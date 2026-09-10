"""MCP server smoke tests."""

import pytest
from mcp import Client
from mcp.types import TextResourceContents

from mortgage_mcp.server import mcp


@pytest.mark.anyio
async def test_server_initializes_and_reports_health() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        result = await client.call_tool("health", {})
        server_info = client.server_info

    assert server_info is not None
    assert server_info.name == "Rabobank Mortgage Demo"
    assert {tool.name for tool in tools.tools} == {
        "health",
        "calculate_mortgage",
        "compare_mortgages",
        "list_mortgage_products",
        "get_interest_rates",
    }
    assert result.is_error is False
    assert result.structured_content == {"result": "ok"}


@pytest.mark.anyio
async def test_calculation_tool_returns_structured_bounded_schedule() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool(
            "calculate_mortgage",
            {
                "principal_eur": "300000",
                "term_years": 30,
                "product_type": "annuity",
                "fixed_rate_years": 10,
                "start_date": "2026-09-10",
                "rate_date": "2026-09-10",
                "schedule_limit": 2,
            },
        )

    assert result.is_error is False
    assert result.structured_content is not None
    assert result.structured_content["schedule_total_periods"] == 360
    assert result.structured_content["schedule_count"] == 2
    assert result.structured_content["rate"]["is_demo_data"] is True


@pytest.mark.anyio
async def test_stale_rate_is_a_tool_error() -> None:
    async with Client(mcp) as client:
        result = await client.call_tool("get_interest_rates", {"as_of": "2027-01-01"})

    assert result.is_error is True
    assert "No current demo rates" in result.content[0].text


@pytest.mark.anyio
async def test_catalog_comparison_and_disclaimer_are_available() -> None:
    async with Client(mcp) as client:
        products = await client.call_tool("list_mortgage_products", {})
        rates = await client.call_tool("get_interest_rates", {"as_of": "2026-09-10"})
        comparison = await client.call_tool(
            "compare_mortgages",
            {
                "principal_eur": "300000",
                "term_years": 30,
                "fixed_rate_years": 10,
                "start_date": "2026-09-10",
                "rate_date": "2026-09-10",
            },
        )
        disclaimer = await client.read_resource("mortgage://disclaimer")

    assert products.structured_content is not None
    assert len(products.structured_content["products"]) == 2
    assert rates.structured_content is not None
    assert all(rate["is_demo_data"] for rate in rates.structured_content["rates"])
    assert comparison.structured_content is not None
    scenarios = comparison.structured_content["scenarios"]
    assert {scenario["product_type"] for scenario in scenarios} == {"annuity", "linear"}
    assert "recommendation" not in comparison.structured_content
    assert isinstance(disclaimer.contents[0], TextResourceContents)
    assert "geen aanbod" in disclaimer.contents[0].text
