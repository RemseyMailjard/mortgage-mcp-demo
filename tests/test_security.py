"""Tests for privacy and transport controls."""

import logging

import pytest

from mortgage_mcp.security import log_operational_event, require_local_transport


def test_local_stdio_transport_is_allowed() -> None:
    require_local_transport("stdio")


def test_remote_transport_is_denied() -> None:
    with pytest.raises(RuntimeError, match="Remote transport is disabled"):
        require_local_transport("streamable-http")


def test_operational_log_contains_no_customer_financial_data(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.INFO, logger="mortgage_mcp.operations"):
        correlation_id = log_operational_event("mortgage_calculation_completed")

    assert correlation_id in caplog.text
    assert "mortgage_calculation_completed" in caplog.text
    assert "principal" not in caplog.text
    assert "income" not in caplog.text
    assert "customer" not in caplog.text
