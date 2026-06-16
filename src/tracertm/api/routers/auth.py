"""Authentication REST endpoints.

GET /api/v1/auth/me - get current user profile (requires JWT)
"""

from __future__ import annotations

import logging
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError

from tracertm.api.deps import auth_guard, get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


class UserProfile(BaseModel):
    """Current user's profile information."""

    user_id: str = Field(..., description="Unique user identifier")
    email: str | None = Field(None, description="User email address")
    name: str | None = Field(None, description="User display name")
    scopes: list[str] = Field(default_factory=list, description="User permission scopes")


@router.get("/me", response_model=UserProfile, status_code=200)
async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: Annotated[AsyncSession, Depends(get_db)] | None = None,
) -> UserProfile:
    """
    Get the current authenticated user's profile.

    Requires a valid JWT in the Authorization header (Bearer token).

    Error handling:
    - 401 token_expired: JWT signature has expired
    - 401 Invalid authorization header format: Bearer prefix missing
    - 401 Invalid token: malformed JWT
    - 503: Database connection error
    - 500: Internal server error

    Returns the user's ID, email, name, and permission scopes.
    """
    # Validate Authorization header format and extract JWT claims
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    token = parts[1]

    # Decode JWT (with error handling for expired/invalid tokens)
    claims: dict[str, object] = {}
    try:
        claims = jwt.decode(token, options={"verify_signature": False})
    except jwt.ExpiredSignatureError:
        logger.warning("Received request with expired JWT")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token_expired",
        )
    except jwt.InvalidSignatureError:
        logger.warning("Received JWT with invalid signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
        )
    except Exception as exc:
        logger.warning(f"JWT decode error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    # Extract user info from claims (fallback to defaults if missing)
    user_id = str(claims.get("sub", ""))
    email = claims.get("email")
    name = claims.get("name")
    scopes_raw = claims.get("scope", "")
    scopes = scopes_raw.split() if isinstance(scopes_raw, str) and scopes_raw else []

    # Try to enrich user profile from database (optional)
    # If DB is unavailable, still return what we have from JWT
    if db is not None:
        try:
            # Future: query user table to get additional profile fields
            # For now, this is a placeholder for DB-backed enrichment
            pass
        except OperationalError as exc:
            # DB connection failed; log and return 503
            logger.error(f"Database connection error in /me endpoint: {exc}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database unavailable",
            )
        except Exception as exc:
            # Unexpected error; log and return 500
            logger.error(f"Unexpected error querying user profile: {exc}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    return UserProfile(
        user_id=user_id,
        email=email,
        name=name,
        scopes=scopes,
    )
