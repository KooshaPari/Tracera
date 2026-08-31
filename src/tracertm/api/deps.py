"""Dependency injections for FastAPI routes.

Provides:
- auth_guard: JWT-based authentication and authorization
- get_db: AsyncSession database connection
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any, AsyncGenerator

import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

logger = logging.getLogger(__name__)

_AUTH_HEADER_PREFIX = "Bearer "
_MAX_TOKEN_LENGTH = 12000

# Database engine (will be initialized on first use)
_engine = None
_session_maker = None


def _safe_token_error(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
    )


def _parse_authorization_header(authorization: str | None) -> str:
    """Parse ``Authorization: Bearer <token>`` and apply shape checks."""
    if not authorization:
        raise _safe_token_error("Authorization header missing")

    if not authorization.startswith(_AUTH_HEADER_PREFIX):
        raise _safe_token_error("Invalid authorization header format")

    token = authorization[len(_AUTH_HEADER_PREFIX) :].strip()
    if not token:
        raise _safe_token_error("Authorization token is empty")

    if len(token) > _MAX_TOKEN_LENGTH:
        raise _safe_token_error("Authorization token too long")

    return token


def _extract_scope_set(claims: dict[str, Any]) -> set[str]:
    """Normalize supported scope claim formats into a set."""
    raw_scope = claims.get("scope")
    if raw_scope is None:
        return set()
    if isinstance(raw_scope, str):
        return {scope.strip() for scope in raw_scope.split() if scope.strip()}
    if isinstance(raw_scope, (list, tuple, set)):
        return {
            str(scope).strip()
            for scope in raw_scope
            if isinstance(scope, str) and scope.strip()
        }
    return set()


def _validate_jwt_claims(claims: dict[str, Any]) -> dict[str, Any]:
    """Validate required claim structure before handlers use values."""
    required_claims = ("sub", "exp")
    missing = [claim for claim in required_claims if claim not in claims]
    if missing:
        raise _safe_token_error(f"Missing required claims: {', '.join(missing)}")

    expiry = claims.get("exp")
    if not isinstance(expiry, (int, float)):
        raise _safe_token_error("Invalid token expiration claim type")

    expiry_dt = datetime.fromtimestamp(expiry, tz=UTC)
    if datetime.now(UTC) > (expiry_dt + timedelta(seconds=30)):
        raise _safe_token_error("Token has expired")

    return claims


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session for dependency injection."""
    global _engine, _session_maker

    # Lazy initialization of engine and session maker
    if _engine is None or _session_maker is None:
        # For now, use in-memory SQLite for testing
        # In production, read from config/env
        from sqlalchemy.pool import StaticPool

        _engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        _session_maker = async_sessionmaker(
            _engine, class_=AsyncSession, expire_on_commit=False
        )

    async with _session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def auth_guard(authorization: str | None = None) -> dict[str, object]:
    """
    Verify JWT token from Authorization header.

    Raises HTTPException with 401 if token is missing, malformed, or expired.
    Returns claims dict with 'sub', 'scope', etc.
    """
    token = _parse_authorization_header(authorization)

    # Environment-driven hardening knobs (TODO: move into a shared settings module).
    # In production, set TRACERA_JWT_SECRET and tighten algorithm/audience checks.
    secret = os.getenv("TRACERA_JWT_SECRET")
    algorithm = os.getenv("TRACERA_JWT_ALG", "HS256").upper()

    verification_options = {
        "verify_aud": False,
        "verify_iss": False,
        "verify_signature": False,
    }
    decode_kwargs: dict[str, Any] = {"options": verification_options}

    if secret:
        verification_options["verify_signature"] = True
        decode_kwargs["key"] = secret
        decode_kwargs["algorithms"] = [algorithm]

    if audience := os.getenv("TRACERA_JWT_AUDIENCE"):
        verification_options["verify_aud"] = True
        decode_kwargs["audience"] = audience

    if issuer := os.getenv("TRACERA_JWT_ISSUER"):
        verification_options["verify_iss"] = True
        decode_kwargs["issuer"] = issuer

    try:
        claims = jwt.decode(token, **decode_kwargs)
        return _validate_jwt_claims(claims)
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token_expired",
        ) from exc
    except jwt.InvalidSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
        ) from exc
    except Exception as exc:
        logger.warning(f"Token decode error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc


def extract_scopes(claims: dict[str, object]) -> set[str]:
    """Return normalized scopes from token claims."""
    return _extract_scope_set(claims)
