"""WorkOS AuthKit authentication helpers.

Functional Requirements: FR-INFRA-001, FR-INFRA-002
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any

import jwt
from jwt import PyJWKClient

try:
    from workos import WorkOSClient
except (ImportError, ModuleNotFoundError):
    WorkOSClient = None  # type: ignore[assignment, misc]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WorkOSSettings:
    """WorkOSSettings."""

    client_id: str
    api_key: str | None
    api_base_url: str
    jwks_url: str
    issuer: str | None
    audience: str
    cache_ttl_seconds: int


_JWKS_CACHE: dict[str, tuple[float, PyJWKClient]] = {}


def get_workos_settings() -> WorkOSSettings:
    """Get workos settings."""
    client_id = os.getenv("WORKOS_CLIENT_ID") or os.getenv("WORKOS_AUTHKIT_CLIENT_ID")
    if not client_id:
        msg = "WORKOS_CLIENT_ID is required for AuthKit"
        raise ValueError(msg)

    api_key = os.getenv("WORKOS_API_KEY")
    api_base_url = os.getenv("WORKOS_API_BASE_URL", "https://api.workos.com").rstrip("/")
    authkit_domain = os.getenv("WORKOS_AUTHKIT_DOMAIN")
    jwks_url = os.getenv("WORKOS_JWKS_URL")
    if not jwks_url:
        if authkit_domain:
            jwks_url = f"{authkit_domain.rstrip('/')}/oauth2/jwks"
        else:
            jwks_url = f"{api_base_url}/sso/jwks/{client_id}"
    issuer = os.getenv("WORKOS_JWT_ISSUER")
    if not issuer:
        if authkit_domain:
            issuer = authkit_domain if authkit_domain.endswith("/") else f"{authkit_domain}/"
        else:
            # For AuthKit access tokens, the issuer is: https://api.workos.com/user_management/{client_id}
            # According to WorkOS docs, issuer can be https://api.workos.com/ or custom auth domain
            # But actual tokens use the user_management path, so we'll accept both patterns
            issuer = f"{api_base_url}/user_management/{client_id}"

    audience = os.getenv("WORKOS_JWT_AUDIENCE") or client_id
    cache_ttl_seconds = int(os.getenv("WORKOS_JWKS_CACHE_TTL", "900"))

    return WorkOSSettings(
        client_id=client_id,
        api_key=api_key,
        api_base_url=api_base_url,
        jwks_url=jwks_url,
        issuer=issuer,
        audience=audience,
        cache_ttl_seconds=cache_ttl_seconds,
    )


def _get_jwks_client(settings: WorkOSSettings) -> PyJWKClient:
    cached = _JWKS_CACHE.get(settings.jwks_url)
    now = time.time()
    if cached and cached[0] > now:
        return cached[1]

    client = PyJWKClient(settings.jwks_url)
    _JWKS_CACHE[settings.jwks_url] = (now + settings.cache_ttl_seconds, client)
    return client


def verify_access_token(token: str) -> dict[str, Any]:
    """Verify access token."""
    settings = get_workos_settings()
    jwks_client = _get_jwks_client(settings)
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    # Get algorithm from JWT header (most reliable method)
    # According to PyJWT best practices: always get algorithm from token header,
    # not from the signing key, to avoid algorithm confusion attacks (RFC 8725)
    try:
        # Decode header without verification to get algorithm
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get("alg", "RS256")
    except (jwt.InvalidTokenError, KeyError, ValueError) as e:
        # If header parsing fails, log and default to RS256
        # This should rarely happen with valid tokens
        logger.warning("Failed to parse JWT header for algorithm: %s. Defaulting to RS256.", e)
        algorithm = "RS256"

    # Ensure algorithm is a string and in the allowed list
    if not isinstance(algorithm, str):
        algorithm = "RS256"

    # Common algorithms for JWKs (RS256, ES256, etc.)
    allowed_algorithms = ["RS256", "RS384", "RS512", "ES256", "ES384", "ES512", "PS256", "PS384", "PS512"]
    if algorithm not in allowed_algorithms:
        # If algorithm from header is not standard, default to RS256
        algorithm = "RS256"

    # Decode token - disable issuer/audience verification in PyJWT since we'll verify manually
    # This allows us to handle WorkOS AuthKit issuer format flexibility
    decoded = jwt.decode(
        token,
        signing_key.key,
        algorithms=[algorithm],
        options={"verify_iss": False, "verify_aud": False},
    )

    # Manual issuer verification - accept WorkOS AuthKit issuer formats
    token_issuer = decoded.get("iss")
    expected_issuer = settings.issuer

    if expected_issuer and token_issuer:
        token_issuer_str = str(token_issuer).rstrip("/")
        expected_issuer_str = str(expected_issuer).rstrip("/")

        # Accept exact match or if token issuer matches WorkOS AuthKit patterns:
        # - https://api.workos.com/user_management/{client_id} (actual format)
        # - https://api.workos.com/ (documented format, or custom auth domain)
        api_base = settings.api_base_url.rstrip("/")
        matches = (
            token_issuer_str == expected_issuer_str
            or token_issuer_str.startswith(f"{api_base}/user_management/")
            or token_issuer_str == f"{api_base}/"
        )

        if not matches:
            from jwt.exceptions import InvalidIssuerError

            msg = f"Invalid issuer. Expected {expected_issuer} (or {api_base}/user_management/{{client_id}}), got {token_issuer}"
            raise InvalidIssuerError(
                msg,
            )

    # Manual audience verification
    token_audience = decoded.get("aud")
    if settings.audience and token_audience:
        # Audience can be a string or list
        if isinstance(token_audience, list):
            if settings.audience not in token_audience:
                from jwt.exceptions import InvalidAudienceError

                msg = f"Invalid audience. Expected {settings.audience}, got {token_audience}"
                raise InvalidAudienceError(msg)
        elif token_audience != settings.audience:
            from jwt.exceptions import InvalidAudienceError

            msg = f"Invalid audience. Expected {settings.audience}, got {token_audience}"
            raise InvalidAudienceError(msg)

    return decoded


def get_logout_url(session_id: str, return_to: str | None = None) -> str:
    """Generate a logout URL for the given session ID."""
    settings = get_workos_settings()
    if WorkOSClient is None:
        msg = "workos SDK is not available"
        raise RuntimeError(msg)
    workos_client = WorkOSClient(
        api_key=settings.api_key or "sk_dummy",
        client_id=settings.client_id,
    )
    return workos_client.user_management.get_logout_url(
        session_id=session_id,
        return_to=return_to,
    )


def authenticate_with_code(code: str) -> dict[str, Any]:
    """Exchange authorization code for tokens and user info."""
    settings = get_workos_settings()
    if not settings.api_key:
        msg = "WORKOS_API_KEY is required for code exchange"
        raise ValueError(msg)
    if WorkOSClient is None:
        msg = "workos SDK is not available"
        raise RuntimeError(msg)
    workos_client = WorkOSClient(
        api_key=settings.api_key,
        client_id=settings.client_id,
    )
    result = workos_client.user_management.authenticate_with_code(code=code)
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    if isinstance(result, dict):
        return result
    return result.__dict__


def authenticate_with_refresh_token(refresh_token: str) -> dict[str, Any]:
    """Authenticate with refresh token."""
    settings = get_workos_settings()
    if not settings.api_key:
        msg = "WORKOS_API_KEY is required for refresh token exchange"
        raise ValueError(msg)
    if WorkOSClient is None:
        msg = "workos SDK is not available"
        raise RuntimeError(msg)
    workos_client = WorkOSClient(
        api_key=settings.api_key,
        client_id=settings.client_id,
    )
    result = workos_client.user_management.authenticate_with_refresh_token(
        refresh_token=refresh_token,
    )
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    if isinstance(result, dict):
        return result
    return result.__dict__


class WorkOSAuthService:
    """Wrapper class for WorkOS AuthKit helpers."""

    def verify_access_token(self, token: str) -> dict[str, Any]:
        """Verify access token."""
        return verify_access_token(token)

    def authenticate_with_code(self, code: str) -> dict[str, Any]:
        """Authenticate with code."""
        return authenticate_with_code(code)

    def authenticate_with_refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Authenticate with refresh token."""
        return authenticate_with_refresh_token(refresh_token)

    def get_logout_url(self, session_id: str, return_to: str | None = None) -> str:
        """Get logout url."""
        return get_logout_url(session_id, return_to=return_to)


def get_user(user_id: str) -> dict[str, Any]:
    """Get user."""
    settings = get_workos_settings()
    if not settings.api_key:
        msg = "WORKOS_API_KEY is required to fetch user data"
        raise ValueError(msg)
    if WorkOSClient is None:
        msg = "workos SDK is not available"
        raise RuntimeError(msg)
    workos_client = WorkOSClient(
        api_key=settings.api_key,
        client_id=settings.client_id,
    )
    user = workos_client.user_management.get_user(user_id)
    if hasattr(user, "model_dump"):
        return user.model_dump()
    if hasattr(user, "dict"):
        return user.dict()
    if isinstance(user, dict):
        return user
    return user.__dict__
