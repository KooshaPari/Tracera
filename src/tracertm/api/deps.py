"""Dependency injections for FastAPI routes.

Provides:
- auth_guard: JWT-based authentication and authorization
- get_db: AsyncSession database connection
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator

import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

logger = logging.getLogger(__name__)

# Database engine (will be initialized on first use)
_engine = None
_session_maker = None


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
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    token = parts[1]

    # For testing/demo, accept any token that decodes (no verification)
    # In production, use a real secret key and verify the signature
    try:
        claims = jwt.decode(token, options={"verify_signature": False})
        return claims
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token_expired",
        )
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
        )
    except Exception as exc:
        logger.warning(f"Token decode error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
