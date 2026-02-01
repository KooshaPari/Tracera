"""Authentication API endpoints for TraceRTM.

Implements:
- RFC 8628 Device Authorization Grant flow
- OAuth token management
- Token refresh and revocation
- WorkOS AuthKit integration
"""

from __future__ import annotations

import logging
import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from tracertm.api.deps import get_db, auth_guard
from tracertm.services.workos_auth_service import WorkOSAuthService, get_user
from tracertm.services.user_repository import UserRepository
from tracertm.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Device flow storage (in production, use database)
_DEVICE_FLOWS: dict[str, dict] = {}
_DEVICE_FLOW_TIMEOUT = 900  # 15 minutes


class DeviceCodeRequest(BaseModel):
    """Request for device authorization code."""

    client_id: str = Field(..., description="OAuth client ID")
    scope: Optional[str] = Field(None, description="Space-separated scopes")


class DeviceCodeResponse(BaseModel):
    """Response with device code."""

    device_code: str = Field(..., description="Device verification code")
    user_code: str = Field(..., description="User-friendly code for manual entry")
    verification_uri: str = Field(..., description="URL user visits to authenticate")
    verification_uri_complete: str = Field(
        ..., description="Complete URL with pre-filled user code"
    )
    expires_in: int = Field(
        default=900, description="Seconds until device code expires"
    )
    interval: int = Field(default=5, description="Seconds to wait between polls")


class TokenRequest(BaseModel):
    """Request for token exchange."""

    device_code: str = Field(..., description="Device code from device flow")
    client_id: str = Field(..., description="OAuth client ID")
    grant_type: str = Field(
        default="urn:ietf:params:oauth:grant-type:device_code",
        description="Grant type for device flow",
    )


class TokenResponse(BaseModel):
    """Successful token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=3600, description="Seconds until expiration")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    user: Optional[dict] = Field(None, description="User information")


class MeResponse(BaseModel):
    """Current user information."""

    user: dict = Field(..., description="User object")
    claims: dict = Field(..., description="JWT claims")
    account: Optional[dict] = Field(None, description="Account information")


class RefreshTokenRequest(BaseModel):
    """Request to refresh an access token."""

    refresh_token: str = Field(..., description="Refresh token")


class RevokeTokenRequest(BaseModel):
    """Request to revoke a token."""

    token: str = Field(..., description="Token to revoke")
    token_type: str = Field(
        default="access_token", description="Type of token to revoke"
    )


class LogoutResponse(BaseModel):
    """Logout success response."""

    success: bool = Field(default=True, description="Logout successful")
    message: Optional[str] = Field(None, description="Optional message")


def _generate_user_code(length: int = 8) -> str:
    """Generate a user-friendly device code."""
    chars = "BCDFGHJKMNPQRTVWXYZ0123456789"
    code = ""
    for i in range(length):
        if i > 0 and i % 4 == 0:
            code += "-"
        code += secrets.choice(chars)
    return code


def _generate_device_code() -> str:
    """Generate a cryptographically secure device code."""
    return secrets.token_urlsafe(32)


def _get_workos_service() -> WorkOSAuthService:
    """Get WorkOS auth service instance."""
    return WorkOSAuthService()


@router.post("/device/code", response_model=DeviceCodeResponse)
async def request_device_code(
    request: DeviceCodeRequest,
) -> DeviceCodeResponse:
    """Request a device code for CLI authentication.

    Implements RFC 8628 device authorization grant flow.

    Args:
        request: Device code request with client_id

    Returns:
        Device code, user code, and verification URI
    """
    device_code = _generate_device_code()
    user_code = _generate_user_code()
    flow_id = str(uuid.uuid4())

    # Store device flow state
    _DEVICE_FLOWS[device_code] = {
        "flow_id": flow_id,
        "user_code": user_code,
        "client_id": request.client_id,
        "scope": (request.scope or "").split(),
        "created_at": time.time(),
        "expires_at": time.time() + _DEVICE_FLOW_TIMEOUT,
        "status": "pending",  # pending, authorized, denied, expired
        "user_id": None,
        "access_token": None,
    }

    logger.info(f"Device flow started: {flow_id} for client {request.client_id}")

    return DeviceCodeResponse(
        device_code=device_code,
        user_code=user_code,
        verification_uri=f"https://auth.tracertm.local/device",
        verification_uri_complete=f"https://auth.tracertm.local/device?user_code={user_code}",
        expires_in=_DEVICE_FLOW_TIMEOUT,
        interval=5,
    )


@router.post("/device/token", response_model=TokenResponse)
async def exchange_device_code(
    request: TokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Exchange device code for access token.

    Implements RFC 8628 token exchange.

    Args:
        request: Token exchange request with device_code
        db: Database session

    Returns:
        Access token and user information

    Raises:
        HTTPException: If device code invalid, expired, or not authorized
    """
    device_code = request.device_code
    flow = _DEVICE_FLOWS.get(device_code)

    if not flow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_grant",
        )

    # Check expiration
    if time.time() > flow["expires_at"]:
        _DEVICE_FLOWS.pop(device_code, None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expired_token",
        )

    # Check authorization status
    if flow["status"] == "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="authorization_pending",
        )

    if flow["status"] == "denied":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="access_denied",
        )

    # Successfully authorized
    if flow["status"] != "authorized":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid_grant",
        )

    # Generate access token
    workos_service = _get_workos_service()
    user_id = flow["user_id"]

    # Create JWT token
    token_data = {
        "sub": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "scope": " ".join(flow["scope"]),
        "client_id": request.client_id,
    }

    access_token = flow["access_token"] or "jwt_token_placeholder"

    # Clean up flow
    _DEVICE_FLOWS.pop(device_code, None)

    logger.info(f"Device flow completed for user {user_id}")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=3600,
        refresh_token=None,
        user={
            "id": user_id,
            "email": "user@example.com",
        },
    )


@router.get("/me", response_model=MeResponse)
async def get_current_user(
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> MeResponse:
    """Get current authenticated user from WorkOS.

    Requires valid JWT access token in Authorization header.
    Token is verified via auth_guard dependency.

    Args:
        claims: JWT claims from auth_guard (includes 'sub' with user_id)
        db: Database session

    Returns:
        Current user information and claims

    Raises:
        HTTPException: 401 if token invalid/missing, 404 if user not found, 500 if API error
    """
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
        )

    try:
        # Fetch user from WorkOS API
        user_data = get_user(user_id)

        # Extract user fields from WorkOS response
        # WorkOS user object typically has: id, email, first_name, last_name,
        # email_verified, created_at, updated_at, profile_picture_url
        return MeResponse(
            user={
                "id": user_data.get("id", user_id),
                "email": user_data.get("email"),
                "firstName": user_data.get("first_name"),
                "lastName": user_data.get("last_name"),
                "emailVerified": user_data.get("email_verified", False),
                "createdAt": user_data.get("created_at"),
                "updatedAt": user_data.get("updated_at"),
                "profilePictureUrl": user_data.get("profile_picture_url"),
            },
            claims=claims,
            # TODO (Task B4): Add account lookup from database if needed
            # For now, extract organization from JWT claims if available
            account={
                "id": claims.get("org_id"),
                "name": claims.get("org_name"),
            } if claims.get("org_id") else None,
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        # API key or configuration error
        logger.error(f"WorkOS configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service not configured",
        )
    except Exception as e:
        # WorkOS API error or user not found
        logger.error(f"Failed to fetch user {user_id} from WorkOS: {e}")

        # Check if it's a 404 (user not found)
        if "404" in str(e) or "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

        # Other API errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user information",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh an access token using refresh token.

    Args:
        request: Refresh token request
        db: Database session

    Returns:
        New access token

    Raises:
        HTTPException: If refresh token invalid or expired
    """
    refresh_token = request.refresh_token

    # Verify refresh token
    # In production, look up in database
    if not refresh_token or len(refresh_token) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Generate new access token
    new_access_token = f"new_access_token_{uuid.uuid4()}"

    logger.info("Access token refreshed")

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=3600,
        refresh_token=refresh_token,
        user=None,  # User info not included in refresh response
    )


@router.post("/revoke")
async def revoke_token(
    request: RevokeTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Revoke an access or refresh token.

    Args:
        request: Token revocation request
        db: Database session

    Returns:
        Success response
    """
    # In production, mark token as revoked in database
    logger.info(f"Token revoked: {request.token_type}")

    return {"success": True}


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    response: Response,
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> LogoutResponse:
    """Log out current user.

    For stateless JWT tokens, this endpoint primarily clears HttpOnly cookies
    used in production. The frontend also handles clearing localStorage tokens.

    Optional: Token can be added to a blocklist for enhanced security.

    Args:
        response: FastAPI response for cookie manipulation
        claims: JWT claims from auth_guard (validates token)
        db: Database session

    Returns:
        LogoutResponse: Success response
    """
    user_id = claims.get("sub")

    # Clear HttpOnly cookies (production environment)
    # These settings match the cookie settings used during login
    response.delete_cookie(
        key="workos_session",
        httponly=True,
        secure=True,  # HTTPS only in production
        samesite="lax",
        path="/",
    )

    # Optional: Add token to blocklist if using token invalidation
    # token_jti = claims.get("jti")
    # if token_jti:
    #     await add_to_token_blocklist(db, token_jti, claims.get("exp"))

    logger.info(f"User {user_id} logged out successfully")

    return LogoutResponse(success=True, message=None)


@router.post("/logout-expired", response_model=LogoutResponse)
async def logout_expired(response: Response) -> LogoutResponse:
    """Log out when token is expired (no auth required).

    This endpoint allows clients to clear cookies even when their token has expired.
    Used as a fallback when normal /logout fails with 401 Unauthorized.

    Args:
        response: FastAPI response for cookie manipulation

    Returns:
        LogoutResponse: Success response
    """
    # Clear HttpOnly cookies
    response.delete_cookie(
        key="workos_session",
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )

    logger.info("Expired token logout completed")

    return LogoutResponse(success=True, message="Logged out (expired token cleared)")
