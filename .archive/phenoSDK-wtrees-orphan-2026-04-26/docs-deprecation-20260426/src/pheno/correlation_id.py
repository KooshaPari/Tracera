"""Utilities for managing request-scoped correlation identifiers.

These helpers wrap a :class:`contextvars.ContextVar` so asynchronous workflows,
background tasks, and thread pools all observe the same identifier without
needing to pass it explicitly through every function call.
"""

import uuid
from contextvars import ContextVar

_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """Retrieve the active correlation identifier, creating one when absent.

    Returns:
        Hex-based UUID string bound to the current context. A new identifier is
        generated and stored if none has been set yet.
    """
    cid = _correlation_id.get()
    if not cid:
        cid = str(uuid.uuid4())
        _correlation_id.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    """Persist an explicit correlation identifier for the active context.

    Args:
        cid: Pre-generated identifier, often sourced from an upstream request
            header such as ``X-Correlation-ID``.
    """
    _correlation_id.set(cid)


def generate_correlation_id() -> str:
    """Create a brand-new correlation identifier without mutating the context.

    Returns:
        Random UUID string callers can propagate to other systems or inject into
        telemetry payloads.
    """
    return str(uuid.uuid4())


__all__ = ["generate_correlation_id", "get_correlation_id", "set_correlation_id"]
