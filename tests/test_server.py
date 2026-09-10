"""MCP server smoke tests."""

import pytest
from mcp import Client

from mortgage_mcp.server import mcp


@pytest.mark.anyio
async def test_server_initializes_and_reports_health() -> None:
    async with Client(mcp) as client:
        tools = await client.list_tools()
        result = await client.call_tool("health", {})
        server_info = client.server_info

    assert server_info is not None
    assert server_info.name == "Rabobank Mortgage Demo"
    assert [tool.name for tool in tools.tools] == ["health"]
    assert result.is_error is False
    assert result.structured_content == {"result": "ok"}
