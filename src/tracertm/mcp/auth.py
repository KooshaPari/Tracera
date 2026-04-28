"""Authentication helpers for TraceRTM MCP server.

Supports:
- WorkOS AuthKit OAuth tokens
- JWT token verification
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.auth.providers.workos import AuthKitProvider
from fastmcp.utilities.auth import parse_scopes

if TYPE_CHECKING:
    from fastmcp.server.auth import AuthProvider

logger = logging.getLogger(__name__)


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def build_auth_provider(transport: str = "stdio") -> AuthProvider | None:
    """Build an AuthProvider for FastMCP.

    OAuth + bearer only: WorkOS AuthKit OAuth for user MCP clients and bearer tokens
    for forwarding frontend AuthKit context. API keys are not supported.

    Transport modes:
    - "stdio": Standard MCP mode - uses MCP auth provider (OAuth)
    - "http": HTTP transport mode - auth handled by FastAPI auth_guard

    Environment variables:
        TRACERTM_MCP_AUTH_MODE: must be "oauth"
        TRACERTM_MCP_AUTHKIT_DOMAIN: WorkOS auth domain
        TRACERTM_MCP_BASE_URL: Server base URL
        TRACERTM_MCP_REQUIRED_SCOPES: Space-separated scopes

    Args:
        transport: Transport mode ("stdio" or "http")

    Returns:
        AuthProvider for STDIO mode, None for HTTP mode
    """
    # HTTP transport: auth is handled by FastAPI auth_guard
    if transport == "http":
        logger.info("MCP auth disabled for HTTP transport (auth_guard handles it)")
        return None

    mode_env = os.getenv("TRACERTM_MCP_AUTH_MODE") or "oauth"
    mode = mode_env.lower().strip()
    if mode != "oauth":
        msg = "MCP auth must be enabled with TRACERTM_MCP_AUTH_MODE=oauth"
        raise RuntimeError(msg)

    authkit_domain = (
        os.getenv("TRACERTM_MCP_AUTHKIT_DOMAIN")
        or os.getenv("FASTMCP_SERVER_AUTH_AUTHKITPROVIDER_AUTHKIT_DOMAIN")
        or os.getenv("WORKOS_AUTHKIT_DOMAIN")
    )
    base_url = (
        os.getenv("TRACERTM_MCP_BASE_URL")
        or os.getenv("FASTMCP_SERVER_AUTH_AUTHKITPROVIDER_BASE_URL")
        or os.getenv("PYTHON_BACKEND_URL")
        or "http://127.0.0.1:4000"
    )
    if base_url and not base_url.rstrip("/").endswith("/api/v1/mcp"):
        base_url = f"{base_url.rstrip('/')}/api/v1/mcp"
    required_scopes = parse_scopes(
        os.getenv("TRACERTM_MCP_REQUIRED_SCOPES") or os.getenv("FASTMCP_SERVER_AUTH_AUTHKITPROVIDER_REQUIRED_SCOPES"),
    )

    logger.debug("Building auth provider. Mode: %s, Scopes: %s", mode or "default", required_scopes)

    if authkit_domain and not authkit_domain.startswith("http"):
        authkit_domain = f"https://{authkit_domain}"

    if not authkit_domain:
        msg = "TRACERTM_MCP_AUTHKIT_DOMAIN (or WORKOS_AUTHKIT_DOMAIN) is required"
        raise RuntimeError(msg)

    if not base_url:
        msg = "TRACERTM_MCP_BASE_URL (or PYTHON_BACKEND_URL) is required"
        raise RuntimeError(msg)

    logger.info("Configuring WorkOS AuthKit: %s", authkit_domain)
    jwt_verifier = JWTVerifier(
        jwks_uri=f"{authkit_domain.rstrip('/')}/oauth2/jwks",
        issuer=authkit_domain.rstrip("/"),
        required_scopes=required_scopes or None,
    )

    return AuthKitProvider(
        authkit_domain=authkit_domain,
        base_url=base_url,
        required_scopes=required_scopes or None,
        token_verifier=jwt_verifier,
    )
