"""MCP helpers for calling the TraceRTM REST API."""

from __future__ import annotations

from tracertm.api.http_client import TraceRTMHttpClient


def _extract_token(token: object | None) -> str | None:
    """Extract string token from Various token-like objects.

    Args:
        token: Token string or object with token attributes

    Returns:
        Extracted token string or None
    """
    if token is None:
        return None
    if isinstance(token, str):
        return token.strip() or None
    for attr in ("raw", "token", "access_token", "value"):
        value = getattr(token, attr, None)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def get_mcp_bearer_token() -> str | None:
    """Retrieve bearer token from MCP context.

    Returns:
        Bearer token string or None
    """
    try:
        from fastmcp.server.dependencies import get_access_token
    except Exception:
        return None
    return _extract_token(get_access_token())


def get_api_client() -> TraceRTMHttpClient:
    """Create API client using MCP bearer token if available."""
    return TraceRTMHttpClient(token=get_mcp_bearer_token())
