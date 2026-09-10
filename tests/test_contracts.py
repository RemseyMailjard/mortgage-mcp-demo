"""MCP schema and error-contract tests."""

import json
from pathlib import Path

import pytest
from mcp import Client

from mortgage_mcp.server import mcp

CONTRACT_PATH = Path(__file__).with_name("contracts") / "tool-input-schemas.json"


@pytest.mark.anyio
async def test_tool_input_schemas_match_reviewed_contract() -> None:
    expected = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    async with Client(mcp) as client:
        result = await client.list_tools()

    actual = {tool.name: tool.input_schema for tool in result.tools}
    assert actual == expected


@pytest.mark.anyio
@pytest.mark.parametrize(
    "arguments",
    [
        {
            "principal_eur": "not-a-number",
            "term_years": 30,
            "product_type": "annuity",
            "fixed_rate_years": 10,
            "start_date": "2026-09-10",
            "rate_date": "2026-09-10"
        },
        {
            "principal_eur": "300000",
            "term_years": 30,
            "product_type": "annuity",
            "fixed_rate_years": 10,
            "start_date": "2026-09-10",
            "rate_date": "2026-09-10",
            "schedule_limit": 121
        }
    ],
)
async def test_invalid_tool_requests_return_errors(arguments: dict[str, object]) -> None:
    async with Client(mcp) as client:
        result = await client.call_tool("calculate_mortgage", arguments)

    assert result.is_error is True