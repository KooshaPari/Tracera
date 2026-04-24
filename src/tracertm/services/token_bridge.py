"""Token bridge for HS256/RS256 compatibility.

Provides bidirectional authentication between:
- WorkOS RS256 tokens (user authentication)
- Internal HS256 service tokens (service-to-service)
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import PyJWKClient
from jwt.exceptions import ExpiredSignatureError, InvalidAudienceError, InvalidIssuerError

logger = logging.getLogger(__name__)

# Minimum secret length for HS256 tokens (256 bits = 32 bytes)
HS256_MIN_SECRET_LENGTH = 32


class TokenBridge:
    """Handles both WorkOS RS256 and internal HS256 token validation.

    Validation Strategy:
    1. Try RS256 first (WorkOS user tokens with JWKS)
    2. Fall back to HS256 (internal service tokens with shared secret)

    Token Types:
    - RS256: WorkOS AuthKit user authentication tokens
    - HS256: Short-lived service tokens (5 min TTL)
    """

    def __init__(
        self,
        hs_secret: str,
        jwks_url: str,
        audience: str | None = None,
        issuer: str | None = None,
        cache_ttl: int = 86400,  # 24 hours
    ) -> None:
        """Initialize token bridge.

        Args:
            hs_secret: Shared secret for HS256 service tokens (min 32 chars)
            jwks_url: WorkOS JWKS URL for RS256 public keys
            audience: Expected audience claim (typically WorkOS client ID)
            issuer: Expected issuer claim (typically WorkOS API base URL)
            cache_ttl: JWKS cache TTL in seconds (default 24 hours)
        """
        if len(hs_secret) < HS256_MIN_SECRET_LENGTH:
            msg = "HS256 secret must be at least 32 characters"
            raise ValueError(msg)

        self.hs_secret = hs_secret
        self.jwks_url = jwks_url
        self.audience = audience or os.getenv("WORKOS_CLIENT_ID")
        self.issuer = issuer
        self.jwks_client = PyJWKClient(
            jwks_url,
            cache_keys=True,
            lifespan=cache_ttl,
        )

    def validate_token(self, token: str) -> dict[str, Any]:
        """Validate token using RS256 (user) or HS256 (service).

        Args:
            token: JWT token string

        Returns:
            Decoded token claims

        Raises:
            jwt.InvalidTokenError: If token is invalid for both methods
        """
        # Read header (unverified) to avoid trying HS256 on an RS256 token
        try:
            unverified = jwt.get_unverified_header(token)
            alg = (unverified.get("alg") or "RS256").upper() if isinstance(unverified.get("alg"), str) else "RS256"
        except (jwt.InvalidTokenError, KeyError, ValueError):
            alg = "RS256"

        rs_failure: Exception | None = None
        if alg == "HS256":
            # Token claims HS256: try HS256 first, then RS256
            try:
                return self._validate_hs256_token(token)
            except (jwt.InvalidTokenError, ValueError) as e:
                rs_failure = e
                logger.debug("HS256 validation failed: %s, trying RS256...", e)
            try:
                return self._validate_rs256_token(token)
            except Exception as e:
                logger.exception("Token validation failed for both HS256 and RS256")
                msg = f"Token validation failed: HS256={rs_failure!r}, RS256={e!r}"
                raise jwt.InvalidTokenError(msg) from e

        # RS256 or other: try RS256 only (skip HS256 to avoid InvalidAlgorithmError)
        try:
            return self._validate_rs256_token(token)
        except ExpiredSignatureError as e:
            logger.warning("Token expired (RS256)")
            msg = "Token expired"
            raise jwt.InvalidTokenError(msg) from e
        except Exception as e:
            logger.debug("RS256 validation failed: %s", e)
            msg = f"Token validation failed: {e!r}"
            raise jwt.InvalidTokenError(msg) from e

    def _validate_rs256_token(self, token: str) -> dict[str, Any]:
        """Validate WorkOS RS256 token using JWKS.

        Uses optional audience/issuer verification so tokens without aud (e.g. some
        WorkOS AuthKit flows) still validate; when present, aud/iss are checked manually.
        """
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)

        # Decode with signature and time checks only. Do not require aud/iss:
        # WorkOS AuthKit access tokens often omit aud; PyJWT defaults verify_aud to
        # verify_signature, so we pass audience=None/issuer=None and options explicitly.
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=None,
            issuer=None,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_aud": False,
                "verify_iss": False,
            },
        )

        # Optional manual issuer check when token has iss
        token_issuer = decoded.get("iss")
        if self.issuer and token_issuer:
            iss_ok = str(token_issuer).rstrip("/") == str(self.issuer).rstrip("/") or str(token_issuer).startswith(
                "https://api.workos.com/",
            )
            if not iss_ok:
                msg = f"Invalid issuer: expected {self.issuer!r}, got {token_issuer!r}"
                raise InvalidIssuerError(msg)

        # Optional manual audience check only when token has aud (avoid MissingRequiredClaimError)
        token_aud = decoded.get("aud")
        if self.audience and token_aud:
            if isinstance(token_aud, list[object]):
                if self.audience not in token_aud:
                    msg = f"Invalid audience: expected {self.audience!r}, got {token_aud!r}"
                    raise InvalidAudienceError(msg)
            elif token_aud != self.audience:
                msg = f"Invalid audience: expected {self.audience!r}, got {token_aud!r}"
                raise InvalidAudienceError(msg)

        logger.info("Validated RS256 token for user %s", decoded.get("sub"))
        return decoded

    def _validate_hs256_token(self, token: str) -> dict[str, Any]:
        """Validate internal HS256 service token.

        Args:
            token: JWT token string

        Returns:
            Decoded token claims

        Raises:
            jwt.InvalidTokenError: If token is invalid
        """
        decoded = jwt.decode(
            token,
            self.hs_secret,
            algorithms=["HS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
            },
        )

        # Service tokens should have type="service"
        if decoded.get("type") != "service":
            logger.warning("HS256 token missing type=service claim")

        logger.info("Validated HS256 service token for user %s", decoded.get("sub"))
        return decoded

    def create_bridge_token(
        self,
        user_id: str,
        org_id: str,
        ttl_minutes: int = 5,
    ) -> str:
        """Create short-lived HS256 service token.

        Args:
            user_id: User ID (sub claim)
            org_id: Organization ID
            ttl_minutes: Token lifetime in minutes (default 5)

        Returns:
            Encoded JWT token string
        """
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "org_id": org_id,
            "type": "service",
            "iat": now,
            "exp": now + timedelta(minutes=ttl_minutes),
            "nbf": now,
        }

        token = jwt.encode(payload, self.hs_secret, algorithm="HS256")
        logger.info("Created bridge token for user %s (org %s), expires in %s minutes", user_id, org_id, ttl_minutes)
        return token

    def refresh_jwks(self) -> None:
        """Force refresh of JWKS cache.

        This is typically handled automatically by PyJWKClient,
        but can be called manually if needed.
        """
        # PyJWKClient handles caching internally
        # To force refresh, we'd need to recreate the client
        self.jwks_client = PyJWKClient(
            self.jwks_url,
            cache_keys=True,
            lifespan=86400,
        )
        logger.info("Refreshed JWKS cache")


def get_token_bridge() -> TokenBridge:
    """Factory function to create TokenBridge instance.

    Environment Variables:
        JWT_SECRET: Shared HS256 secret
        WORKOS_JWKS_URL: WorkOS JWKS endpoint
        WORKOS_CLIENT_ID: WorkOS client ID (audience)
        WORKOS_JWT_ISSUER: Expected issuer claim (optional)

    Returns:
        Configured TokenBridge instance

    Raises:
        ValueError: If required environment variables are missing
    """
    hs_secret = os.getenv("JWT_SECRET")
    if not hs_secret:
        msg = "JWT_SECRET environment variable is required"
        raise ValueError(msg)

    jwks_url = os.getenv("WORKOS_JWKS_URL")
    if not jwks_url:
        # Construct default JWKS URL from client ID
        client_id = os.getenv("WORKOS_CLIENT_ID")
        api_base = os.getenv("WORKOS_API_BASE_URL", "https://api.workos.com")
        if client_id:
            jwks_url = f"{api_base.rstrip('/')}/sso/jwks/{client_id}"
        else:
            msg = "Either WORKOS_JWKS_URL or WORKOS_CLIENT_ID must be set"
            raise ValueError(msg)

    return TokenBridge(
        hs_secret=hs_secret,
        jwks_url=jwks_url,
        audience=os.getenv("WORKOS_CLIENT_ID"),
        issuer=os.getenv("WORKOS_JWT_ISSUER"),
    )
