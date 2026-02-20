"""Device flow authentication handlers for TraceRTM.

This module implements OAuth 2.0 Device Authorization Grant (RFC 8628)
for authentication on devices without a browser or with limited input.
"""

import os
import secrets
import time
from typing import cast

from fastapi import HTTPException
from pydantic import ValidationError

from tracertm.schemas.auth import (
    DeviceCodeRequest,
    DeviceCodeResponse,
    DeviceTokenRequest,
    DeviceTokenResponse,
)
from tracertm.services.workos_auth_service import WorkOSAuthService

# Store pending device codes in memory (use Redis/database for production)
_device_code_store: dict[str, dict[str, object]] = {}
WORKOS_DEVICE_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    OSError,
    LookupError,
    ConnectionError,
    TimeoutError,
)
TOKEN_CLAIM_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    OSError,
)


def _generate_device_codes() -> tuple[str, str]:
    """Generate secure device and user codes.

    Returns:
        Tuple of (device_code, user_code)
    """
    device_code = secrets.token_urlsafe(32)  # High entropy for security
    user_code = secrets.token_urlsafe(8).upper()  # 8 char uppercase code
    return device_code, user_code


def _build_verification_urls(user_code: str) -> tuple[str, str]:
    """Build device verification URLs.

    Args:
        user_code: The user code to include in complete URL

    Returns:
        Tuple of (verification_uri, verification_uri_complete)
    """
    authkit_domain = os.getenv("WORKOS_AUTHKIT_DOMAIN")
    if authkit_domain:
        verification_uri = f"{authkit_domain.rstrip('/')}/device"
    else:
        # Fallback to API server for testing
        base_url = os.getenv("APP_URL", "http://localhost:8000")
        verification_uri = f"{base_url}/device"

    verification_uri_complete = f"{verification_uri}?user_code={user_code}"
    return verification_uri, verification_uri_complete


def _store_device_code(device_code: str, user_code: str, client_id: str) -> dict[str, object]:
    """Store device code with metadata in the code store.

    Args:
        device_code: The generated device code
        user_code: The user-friendly code to display
        client_id: OAuth client ID

    Returns:
        The stored code data dict
    """
    code_data = {
        "user_code": user_code,
        "client_id": client_id,
        "created_at": time.time(),
        "expires_in": 900,  # 15 minutes default
        "interval": 5,  # polling interval in seconds
        "completed": False,
        "tokens": None,
    }
    _device_code_store[device_code] = code_data
    return code_data


async def device_code_handler(data: dict[str, object]) -> DeviceCodeResponse:
    """Start device authorization flow.

    Returns device code and verification URL. The user navigates to the
    verification URL and enters the user code. The device then polls
    /api/v1/auth/device/token to complete authentication.

    Args:
        data: Request data with optional client_id

    Returns:
        DeviceCodeResponse with codes and verification URLs

    Raises:
        HTTPException: If client_id is missing or invalid
    """
    try:
        # Pydantic will validate and parse the data
        request_data = DeviceCodeRequest.model_validate(data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    client_id = request_data.client_id or os.getenv("WORKOS_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="WORKOS_CLIENT_ID is required")

    # Generate codes
    device_code, user_code = _generate_device_codes()

    # Build verification URLs
    verification_uri, verification_uri_complete = _build_verification_urls(user_code)

    # Store device code with metadata
    code_data = _store_device_code(device_code, user_code, client_id)

    return DeviceCodeResponse(
        device_code=device_code,
        user_code=user_code,
        verification_uri=verification_uri,
        verification_uri_complete=verification_uri_complete,
        expires_in=cast("int", code_data["expires_in"]),
        interval=cast("int", code_data["interval"]),
    )


def _validate_device_code(device_code: str) -> dict[str, object]:
    """Validate device code and check expiration.

    Args:
        device_code: The device code to validate

    Returns:
        The code data dict if valid

    Raises:
        HTTPException: If code is invalid or expired
    """
    code_data = _device_code_store.get(device_code)
    if not code_data:
        raise HTTPException(status_code=400, detail="invalid_grant")

    # Check expiration
    elapsed = time.time() - cast("float", code_data["created_at"])
    if elapsed > cast("float", code_data["expires_in"]):
        del _device_code_store[device_code]
        raise HTTPException(status_code=400, detail="expired_token")

    return code_data


def _extract_tokens_and_cleanup(device_code: str, code_data: dict[str, object]) -> DeviceTokenResponse:
    """Extract tokens from code data and cleanup store.

    Args:
        device_code: The device code key
        code_data: The code data dict

    Returns:
        DeviceTokenResponse with tokens
    """
    # Clean up after returning tokens
    del _device_code_store[device_code]
    tokens = cast("dict[str, object]", code_data["tokens"])

    return DeviceTokenResponse(
        access_token=cast("str", tokens.get("access_token", "")),
        token_type=cast("str", tokens.get("token_type", "bearer")),
        expires_in=cast("int | None", tokens.get("expires_in")),
        refresh_token=cast("str | None", tokens.get("refresh_token")),
        user=cast("dict[str, object] | None", tokens.get("user")),
    )


async def device_token_handler(data: dict[str, object]) -> DeviceTokenResponse:
    """Poll for device authorization completion.

    The device should poll this endpoint with the device_code until
    authentication is complete or the code expires.

    Args:
        data: Request data with device_code and client_id

    Returns:
        DeviceTokenResponse with access token on success

    Raises:
        HTTPException: With 'authorization_pending' while waiting,
                      'expired_token' if code expired, or 'invalid_grant'
                      if code is invalid
    """
    try:
        # Pydantic will validate and parse the data
        request_data = DeviceTokenRequest.model_validate(data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    device_code = request_data.device_code

    # Validate device code and check expiration
    code_data = _validate_device_code(device_code)

    # Check if authorization is complete
    if code_data["completed"] and code_data["tokens"]:
        return _extract_tokens_and_cleanup(device_code, code_data)

    # Still waiting for user authorization
    raise HTTPException(
        status_code=400,
        detail="authorization_pending",
        headers={"Retry-After": str(code_data["interval"])},
    )


def _find_device_code_by_user_code(user_code: str) -> str | None:
    """Find device code by user code.

    Args:
        user_code: The user code to search for

    Returns:
        The device code if found, None otherwise
    """
    for code, code_data in _device_code_store.items():
        if code_data.get("user_code") == user_code and not code_data["completed"]:
            return code
    return None


def _authenticate_with_code(auth_code: str, workos_auth_service: WorkOSAuthService) -> dict[str, object]:
    """Exchange authorization code for tokens using WorkOS.

    Args:
        auth_code: Authorization code from browser
        workos_auth_service: WorkOS auth service instance

    Returns:
        Token data dict from WorkOS

    Raises:
        HTTPException: If authentication fails
    """
    try:
        return workos_auth_service.authenticate_with_code(auth_code)
    except WORKOS_DEVICE_ERRORS as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {e!s}") from e


def _extract_user_info(result: dict[str, object], workos_auth_service: WorkOSAuthService) -> dict[str, object] | None:
    """Extract user info from authentication result.

    Args:
        result: Authentication result from WorkOS
        workos_auth_service: WorkOS auth service instance

    Returns:
        User info dict or None if not available
    """
    user_obj = result.get("user")
    if user_obj:
        return cast("dict[str, object]", user_obj)

    # Try to get from access token claims
    access_token = result.get("access_token")
    if access_token:
        try:
            claims = workos_auth_service.verify_access_token(cast("str", access_token))
            return {"sub": claims.get("sub"), "email": claims.get("email")}
        except TOKEN_CLAIM_ERRORS:
            return None

    return None


async def device_complete_handler(data: dict[str, object], workos_auth_service: WorkOSAuthService) -> dict[str, object]:
    """Complete device authorization from browser.

    This endpoint is called by the browser after the user enters the code
    and authorizes the device.

    Args:
        data: Request data with user_code and authorization code
        workos_auth_service: WorkOS auth service instance

    Returns:
        Success response with status and user info

    Raises:
        HTTPException: If user_code is invalid, expired, or auth fails
    """
    user_code_obj = data.get("user_code")
    if not user_code_obj:
        raise HTTPException(status_code=400, detail="user_code required")
    user_code = cast("str", user_code_obj)

    # Find the pending device code for this user_code
    found_code = _find_device_code_by_user_code(user_code)
    if not found_code:
        raise HTTPException(status_code=400, detail="Invalid or expired user code")

    # Exchange the authorization code for tokens
    auth_code_obj = data.get("code")
    if not auth_code_obj:
        raise HTTPException(status_code=400, detail="authorization code required")
    auth_code = cast("str", auth_code_obj)

    # Verify API key is configured
    api_key = os.getenv("WORKOS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Server configuration error")

    # Authenticate with WorkOS
    result = _authenticate_with_code(auth_code, workos_auth_service)

    # Store the tokens and mark as complete
    _device_code_store[found_code]["completed"] = True
    _device_code_store[found_code]["tokens"] = result

    # Get user info if available
    user_info = _extract_user_info(result, workos_auth_service)

    return {
        "status": "authorized",
        "user": user_info,
    }
