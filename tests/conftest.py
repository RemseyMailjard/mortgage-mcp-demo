"""Shared pytest configuration."""

import pytest


@pytest.fixture
def anyio_backend() -> str:
    """Use asyncio for MCP in-process tests."""
    return "asyncio"
