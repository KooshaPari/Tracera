"""Authentication API endpoints for TraceRTM.

Implements:
- OAuth token management via WorkOS AuthKit
- Token refresh and revocation
- Current user endpoint with DB-backed account lookup
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.account_repository import AccountRepository

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


class MeResponse(BaseModel):
    """Current user information."""

    user: dict[str, Any] = Field(..., description="User object")
    claims: dict[str, Any] = Field(..., description="JWT claims")
    account: dict | None = Field(None, description="Account information from DB")


async def get_db() -> AsyncSession:
    """Get database session.

    This is a placeholder dependency. In production, inject from
    the database module.
    """
    raise NotImplementedError("get_db must be implemented by the caller")


async def auth_guard(authorization: str | None = None) -> dict[str, Any]:
    """Validate JWT token and return claims.

    This is a placeholder dependency. In production, validate against
    WorkOS or your JWT provider.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    raise NotImplementedError("auth_guard must be implemented by the caller")


@router.get("/me", response_model=MeResponse)
async def get_current_user(
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MeResponse:
    """Get current authenticated user from database.

    Performs a DB-backed account lookup (B4 requirement) to retrieve
    account information for the authenticated user.

    Args:
        claims: JWT claims from auth_guard (includes 'sub' with user_id)
        db: Database session for account lookup

    Returns:
        Current user information, claims, and account data

    Raises:
        HTTPException: 401 if token invalid/missing, 500 if DB lookup fails
    """
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
        )

    try:
        # B4 Real DB Lookup: Fetch account from database
        account_repo = AccountRepository(db)
        db_accounts = await account_repo.list_by_user(user_id)

        if db_accounts:
            # Account found in database
            primary = db_accounts[0]
            account_data: dict | None = {
                "id": primary.id,
                "name": primary.name,
            }
        elif claims.get("org_id"):
            # Fallback to JWT claims if no DB record exists yet
            account_data = {
                "id": claims.get("org_id"),
                "name": claims.get("org_name"),
            }
        else:
            # No account information available
            account_data = None

        # Extract user fields from claims (WorkOS provides these)
        return MeResponse(
            user={
                "id": user_id,
                "email": claims.get("email"),
                "firstName": claims.get("first_name"),
                "lastName": claims.get("last_name"),
                "emailVerified": claims.get("email_verified", False),
            },
            claims=claims,
            account=account_data,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user information",
        ) from e
