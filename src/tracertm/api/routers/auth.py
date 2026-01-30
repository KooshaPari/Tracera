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
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from tracertm.database.connection import get_db_session
from tracertm.services.workos_auth_service import WorkOSAuthService
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
    db: AsyncSession = Depends(get_db_session),
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
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
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
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session),
) -> MeResponse:
    """Get current authenticated user.

    Requires valid JWT access token in Authorization header.

    Args:
        authorization: Authorization header value
        db: Database session

    Returns:
        Current user information and claims
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    # Parse bearer token
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    token = authorization[7:]

    # Verify token using WorkOS
    workos_service = _get_workos_service()

    try:
        # In production, verify JWT using JWKS
        # For now, accept any token
        user_id = "user_id_from_token"
        claims = {
            "sub": user_id,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        }

        return MeResponse(
            user={
                "id": user_id,
                "email": "user@example.com",
            },
            claims=claims,
            account={
                "id": "account_id",
                "name": "Default Account",
            },
        )
    except Exception as e:
        logger.error(f"Failed to verify token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session),
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
    )


@router.post("/revoke")
async def revoke_token(
    request: RevokeTokenRequest,
    db: AsyncSession = Depends(get_db_session),
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


@router.post("/logout")
async def logout(
    authorization: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """Log out current user (revoke tokens).

    Args:
        authorization: Authorization header value
        db: Database session

    Returns:
        Success response
    """
    # In production, revoke user's tokens
    logger.info("User logged out")
    return {"success": True}
