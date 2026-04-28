"""Generic JWT handling utilities for the pheno SDK.

This module provides secure JWT encoding, decoding, and validation with
explicit control over signature verification. Supports both verified and
unverified decoding modes with clear opt-in semantics.

Security Features:
- Explicit verification control (must opt-in for unverified decoding)
- Configurable algorithm support
- Audience validation
- Comprehensive error handling

Usage:
    from pheno.auth.jwt_handler import JWTHandler, decode_jwt_unverified

    # Verified decoding (production use)
    handler = JWTHandler(secret_key="your-secret")
    payload = handler.decode(token)

    # Unverified decoding (development/debugging only)
    payload = decode_jwt_unverified(token)
"""

from __future__ import annotations

import base64
import json
from typing import TYPE_CHECKING, Any

import jwt
from jwt import InvalidTokenError

from .types import AuthError, TokenError

if TYPE_CHECKING:
    from collections.abc import Sequence


class JWTHandler:
    """Generic JWT handler with verification support.

    This class provides secure JWT operations with signature verification.
    Use this for production code where token authenticity must be validated.

    Attributes:
        secret_key: Secret or public key for signature verification
        algorithms: Allowed signing algorithms (default: RS256, HS256)
        audience: Expected audience claim(s) for validation

    Examples:
        >>> handler = JWTHandler(secret_key="your-secret")
        >>> payload = handler.decode(token)
        >>> new_token = handler.encode({"user_id": "123"})
    """

    def __init__(
        self,
        secret_key: str | bytes,
        algorithms: Sequence[str] | None = None,
        audience: str | Sequence[str] | None = None,
    ):
        """Initialize JWT handler with verification settings.

        Args:
            secret_key: Secret or public key for JWT operations
            algorithms: Allowed algorithms (default: ["RS256", "HS256"])
            audience: Expected audience claim(s)
        """
        self.secret_key = secret_key
        self.algorithms = list(algorithms or ["RS256", "HS256"])
        self.audience = audience

    def decode(
        self,
        token: str,
        verify: bool = True,
        audience: str | Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Decode and optionally verify a JWT token.

        Args:
            token: Encoded JWT string
            verify: Whether to verify signature (default: True)
            audience: Override audience validation

        Returns:
            Decoded JWT payload as dictionary

        Raises:
            TokenError: If token is invalid or verification fails

        Examples:
            >>> payload = handler.decode(token)  # Verified
            >>> payload = handler.decode(token, verify=False)  # Unverified
        """
        if not verify:
            # Explicit opt-in for unverified decoding
            return decode_jwt_unverified(token)

        try:
            aud = audience if audience is not None else self.audience
            options = {"verify_aud": aud is not None}

            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=self.algorithms,
                audience=aud,
                options=options,
            )
            return payload or {}
        except InvalidTokenError as exc:
            raise TokenError(f"Failed to verify JWT: {exc}") from exc

    def encode(
        self,
        payload: dict[str, Any],
        algorithm: str | None = None,
    ) -> str:
        """Encode a payload as a JWT token.

        Args:
            payload: Claims to encode in the token
            algorithm: Signing algorithm (default: first in self.algorithms)

        Returns:
            Encoded JWT token string

        Raises:
            TokenError: If encoding fails

        Examples:
            >>> token = handler.encode({"user_id": "123", "exp": 1234567890})
        """
        try:
            algo = algorithm or self.algorithms[0]
            return jwt.encode(payload, self.secret_key, algorithm=algo)
        except Exception as exc:
            raise TokenError(f"Failed to encode JWT: {exc}") from exc

    def validate(self, token: str) -> bool:
        """Validate a JWT token without returning payload.

        Args:
            token: JWT token to validate

        Returns:
            True if token is valid and verified, False otherwise

        Examples:
            >>> if handler.validate(token):
            ...     print("Token is valid")
        """
        try:
            self.decode(token, verify=True)
            return True
        except (TokenError, AuthError):
            return False


def _b64url_decode(segment: str) -> bytes:
    """Decode a base64url segment with restored padding.

    Args:
        segment: Base64url encoded string

    Returns:
        Decoded bytes
    """
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def decode_jwt_unverified(token: str) -> dict[str, Any]:
    """Decode a JWT without signature verification.

    WARNING: This function does NOT verify the token signature. Only use this
    for development, debugging, or when the token has been validated through
    other means. NEVER use this in production authentication flows.

    Args:
        token: Encoded JWT string

    Returns:
        Decoded JWT payload

    Raises:
        TokenError: If token format is invalid

    Examples:
        >>> # Development/debugging only!
        >>> payload = decode_jwt_unverified(token)
        >>> print(payload.get("user_id"))
    """
    parts = token.split(".")
    if len(parts) < 2:
        raise TokenError("Invalid JWT: expected at least header.payload")

    payload_b64 = parts[1]

    try:
        payload_json = _b64url_decode(payload_b64).decode("utf-8")
        return json.loads(payload_json) or {}
    except Exception as exc:
        raise TokenError(f"Failed to decode JWT payload: {exc}") from exc


def decode_jwt(
    token: str,
    *,
    verify: bool,
    key: str | bytes | None = None,
    algorithms: Sequence[str] | None = None,
    audience: str | Sequence[str] | None = None,
) -> dict[str, Any]:
    """Decode a JWT and optionally verify its signature.

    This is a legacy-compatible function for backward compatibility with
    existing code. New code should use JWTHandler class instead.

    Args:
        token: Encoded JWT string
        verify: When True, verify the signature using ``key``
        key: Secret or public key to verify the token (required if verify=True)
        algorithms: Allowed algorithms for signature verification
        audience: Optional audience claim(s) to validate when verifying

    Returns:
        The decoded JWT payload

    Raises:
        ValueError: If the token is malformed, verification fails, or key is missing

    Examples:
        >>> # Verified decoding
        >>> payload = decode_jwt(token, verify=True, key="secret")

        >>> # Unverified decoding (opt-in with verify=False)
        >>> payload = decode_jwt(token, verify=False)
    """
    if verify:
        if key is None:
            raise ValueError("JWT key is required when verify=True")

        handler = JWTHandler(secret_key=key, algorithms=algorithms, audience=audience)
        try:
            return handler.decode(token, verify=True)
        except TokenError as exc:
            raise ValueError(str(exc)) from exc

    # Explicit non-verifying decode; callers must opt-in by passing verify=False.
    try:
        return decode_jwt_unverified(token)
    except TokenError as exc:
        raise ValueError(str(exc)) from exc


__all__ = [
    "JWTHandler",
    "decode_jwt",
    "decode_jwt_unverified",
]
