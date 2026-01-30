"""Authentication helpers for TraceRTM MCP server.

Supports:
- WorkOS AuthKit OAuth tokens
- Static dev API keys
- JWT token verification
- Composite token verification (try multiple verifiers)
"""

from __future__ import annotations

import logging
import os
from typing import Any

from fastmcp.server.auth import AccessToken, AuthProvider, TokenVerifier
from fastmcp.server.auth.providers.jwt import JWTVerifier, StaticTokenVerifier
from fastmcp.server.auth.providers.workos import AuthKitProvider
from fastmcp.utilities.auth import parse_scopes

logger = logging.getLogger(__name__)


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


class CompositeTokenVerifier(TokenVerifier):
    """Tries multiple token verifiers in order (first match wins)."""

    def __init__(self, verifiers: list[TokenVerifier]):
        super().__init__(required_scopes=None)
        self._verifiers = verifiers

    async def verify_token(self, token: str) -> AccessToken | None:
        for verifier in self._verifiers:
            try:
                access = await verifier.verify_token(token)
            except Exception:
                access = None
            if access is not None:
                return access
        return None


def _build_static_verifier(required_scopes: list[str] | None = None) -> StaticTokenVerifier | None:
    """Build static token verifier for dev API keys.

    Args:
        required_scopes: Required scopes for static tokens

    Returns:
        StaticTokenVerifier if dev keys configured, None otherwise
    """
    dev_tokens = _parse_csv(os.getenv("TRACERTM_MCP_DEV_API_KEYS"))
    if not dev_tokens:
        logger.debug("No dev API keys configured (TRACERTM_MCP_DEV_API_KEYS)")
        return None

    scopes = required_scopes or _parse_csv(os.getenv("TRACERTM_MCP_DEV_SCOPES"))
    tokens: dict[str, dict[str, Any]] = {}
    for index, token in enumerate(dev_tokens, start=1):
        tokens[token] = {
            "client_id": f"dev-key-{index}",
            "scopes": scopes,
            "claims": {"sub": f"dev-key-{index}", "auth_type": "api_key"},
        }

    logger.info(f"Configured {len(dev_tokens)} dev API keys with scopes: {scopes}")
    return StaticTokenVerifier(tokens=tokens, required_scopes=scopes or None)


def build_auth_provider() -> AuthProvider | None:
    """Build an AuthProvider for FastMCP.

    Uses WorkOS AuthKit for OAuth tokens with optional static dev keys.
    Returns None if auth is disabled or not configured.

    Environment variables:
        TRACERTM_MCP_AUTH_MODE: "disabled" to disable auth
        TRACERTM_MCP_AUTHKIT_DOMAIN: WorkOS auth domain
        TRACERTM_MCP_BASE_URL: Server base URL
        TRACERTM_MCP_REQUIRED_SCOPES: Space-separated scopes
        TRACERTM_MCP_DEV_API_KEYS: Comma-separated dev keys
        TRACERTM_MCP_DEV_SCOPES: Comma-separated dev scopes
    """

    mode = (os.getenv("TRACERTM_MCP_AUTH_MODE") or "").lower().strip()
    if mode in {"disabled", "none", "off"}:
        logger.info("MCP auth disabled (TRACERTM_MCP_AUTH_MODE=disabled)")
        return None

    authkit_domain = os.getenv("TRACERTM_MCP_AUTHKIT_DOMAIN") or os.getenv(
        "FASTMCP_SERVER_AUTH_AUTHKITPROVIDER_AUTHKIT_DOMAIN"
    )
    base_url = os.getenv("TRACERTM_MCP_BASE_URL") or os.getenv(
        "FASTMCP_SERVER_AUTH_AUTHKITPROVIDER_BASE_URL"
    )
    required_scopes = parse_scopes(
        os.getenv("TRACERTM_MCP_REQUIRED_SCOPES")
        or os.getenv("FASTMCP_SERVER_AUTH_AUTHKITPROVIDER_REQUIRED_SCOPES")
    )

    logger.debug(f"Building auth provider. Mode: {mode or 'default'}, Scopes: {required_scopes}")

    static_verifier = _build_static_verifier(required_scopes)

    if authkit_domain and base_url:
        logger.info(f"Configuring WorkOS AuthKit: {authkit_domain}")

        jwt_verifier = JWTVerifier(
            jwks_uri=f"{authkit_domain.rstrip('/')}/oauth2/jwks",
            issuer=authkit_domain.rstrip("/"),
            required_scopes=required_scopes or None,
        )

        if static_verifier:
            logger.info("Using composite verifier: static dev keys + JWT")
            verifier: TokenVerifier = CompositeTokenVerifier([static_verifier, jwt_verifier])
        else:
            logger.info("Using JWT verifier only")
            verifier = jwt_verifier

        return AuthKitProvider(
            authkit_domain=authkit_domain,
            base_url=base_url,
            required_scopes=required_scopes or None,
            token_verifier=verifier,
        )

    if static_verifier:
        logger.info("Using static dev key verifier only")

        class StaticAuthProvider(AuthProvider):
            async def verify_token(self, token: str) -> AccessToken | None:
                return await static_verifier.verify_token(token)

        return StaticAuthProvider(required_scopes=required_scopes or None)

    logger.warning("Auth enabled but no auth provider configured")
    return None
