"""Security controls shared by delivery adapters."""

import logging
from uuid import uuid4

LOGGER = logging.getLogger("mortgage_mcp.operations")


def require_local_transport(transport: str) -> None:
    """Reject remote transports until an authenticated gateway is implemented."""
    if transport != "stdio":
        raise RuntimeError(
            "Remote transport is disabled; deploy only behind reviewed authentication "
            "and authorization controls"
        )


def log_operational_event(event: str) -> str:
    """Log non-sensitive operational metadata and return its correlation ID."""
    correlation_id = uuid4().hex
    LOGGER.info("event=%s correlation_id=%s", event, correlation_id)
    return correlation_id
