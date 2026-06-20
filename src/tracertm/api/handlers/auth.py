"""Authentication handlers for TraceRTM API."""

import hashlib
import logging
import os
import re
import secrets
import time
from typing import cast

from fastapi import Depends, HTTPException
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_db
from tracertm.repositories.account_repository import AccountRepository
from tracertm.schemas.auth import (
    DeviceCodeRequest,
    DeviceCodeResponse,
    DeviceTokenRequest,
    DeviceTokenResponse,
    LoginRequest,
    SignupRequest,
)
from tracertm.services import workos_auth_service

logger = logging.getLogger(__name__)

# System admin: emails listed in TRACERTM_SYSTEM_ADMIN_EMAILS (comma-separated) get full access.
_admin_emails_cache: frozenset[str] | None = None
_admin_user_ids: set[str] = set()

# Device Authorization Flow (RFC 8628)
# Store pending device codes in memory (use Redis/database for production)
_device_code_store: dict[str, dict] = {}
WORKOS_HANDLER_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    OSError,
    LookupError,
    ConnectionError,
    TimeoutError,
)
TOKEN_EXTRACTION_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    OSError,
)


class AuthCallbackPayload(BaseModel):
    """Schema for auth callback payload."""

    code: str


def _system_admin_emails() -> frozenset[str]:
    """Get system admin emails from environment."""
    global _admin_emails_cache
    if _admin_emails_cache is not None:
        return _admin_emails_cache
    raw = os.getenv("TRACERTM_SYSTEM_ADMIN_EMAILS", "kooshapari@gmail.com").strip()
    emails = frozenset(e.strip().lower() for e in raw.split(",") if e.strip())
    _admin_emails_cache = emails
    return emails


def _is_system_admin_email(email: str | None) -> bool:
    """Check if email is a system admin."""
    if not email:
        return False
    return email.strip().lower() in _system_admin_emails()


async def _get_user_info(user_id: str | None) -> dict[str, object] | None:
    """Get user info from WorkOS, return None on error."""
    if not user_id:
        return None
    try:
        return workos_auth_service.get_user(user_id)
    except WORKOS_HANDLER_ERRORS:
        return None


def _enrich_admin_user(user: dict[str, object] | None, user_id: str | None) -> dict[str, object] | None:
    """Add admin role to user if they are a system admin."""
    if not user or not isinstance(user, dict):
        return user

    user_email = user.get("email") or user.get("email_address")
    if _is_system_admin_email(cast("str | None", user_email)):
        user = dict[str, object](user)
        user["role"] = "admin"
        if user_id:
            _admin_user_ids.add(user_id)
    return user


async def _get_user_accounts(user_id: str | None, db: AsyncSession) -> list[dict[str, object]]:
    """Get list of accounts for a user."""
    if not user_id:
        return []

    account_repo = AccountRepository(db)
    accounts_list = await account_repo.list_by_user(user_id)
    return [
        {
            "id": acc.id,
            "name": acc.name,
            "slug": acc.slug,
            "account_type": acc.account_type,
        }
        for acc in accounts_list
    ]


async def _get_current_account(
    account_id: str | None,
    accounts_list: list[dict[str, object]],
    db: AsyncSession,
) -> dict[str, object] | None:
    """Get current account from claims or first account."""
    if not account_id and not accounts_list:
        return None

    account_repo = AccountRepository(db)

    # Try to get account from claims
    if account_id:
        account_obj = await account_repo.get_by_id(account_id)
        if account_obj:
            return {
                "id": account_obj.id,
                "name": account_obj.name,
                "slug": account_obj.slug,
                "account_type": account_obj.account_type,
            }

    # Use first account as default
    if accounts_list:
        return accounts_list[0]

    return None


# ==================== Endpoint Handlers ====================


async def auth_callback_handler(payload: AuthCallbackPayload) -> dict[str, object]:
    """Exchange authorization code for user data and tokens (B2B flow)."""
    try:
        return workos_auth_service.authenticate_with_code(payload.code)
    except WORKOS_HANDLER_ERRORS as exc:
        logger.exception("Auth callback failed")
        raise HTTPException(status_code=400, detail=str(exc)) from exc


async def auth_me_handler(
    claims: dict[str, object],
    db: AsyncSession,
) -> dict[str, object]:
    """Return current authenticated user context with account info.

    Complexity reduced by extracting helper functions:
    - _get_user_info: Get user from WorkOS
    - _enrich_admin_user: Add admin role if applicable
    - _get_user_accounts: Get list of user's accounts
    - _get_current_account: Get current account from claims or default
    """
    user_id = cast("str | None", claims.get("sub")) if isinstance(claims, dict) else None
    account_id = cast("str | None", claims.get("account_id")) if isinstance(claims, dict) else None

    # Get user info
    user = await _get_user_info(user_id)

    # Enrich with admin role if applicable
    user = _enrich_admin_user(user, user_id)

    # Get user's accounts
    accounts = await _get_user_accounts(user_id, db)

    # Get current account
    account = await _get_current_account(account_id, accounts, db)

    return {
        "claims": claims,
        "user": user,
        "account": account,
        "accounts": accounts,
    }


async def auth_logout_handler(claims: dict[str, object]) -> dict[str, object]:
    """Return logout metadata including WorkOS logout URL if sid is present."""
    session_id = claims.get("sid")
    logout_url = None
    if session_id:
        try:
            logout_url = workos_auth_service.get_logout_url(cast("str", session_id))
        except WORKOS_HANDLER_ERRORS as exc:
            logger.warning("Failed to generate logout URL: %s", exc)

    return {
        "status": "ok",
        "logout_url": logout_url,
    }


async def signup_handler(
    data: dict[str, object],
    db: AsyncSession,
) -> dict[str, object]:
    """Create a new user account and initial account."""
    try:
        signup_data = SignupRequest.model_validate(data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Generate slug from account name if not provided
    account_slug = signup_data.account_slug
    if not account_slug:
        account_slug = re.sub(r"[^a-z0-9-]", "", signup_data.account_name.lower().replace(" ", "-"))
        if not account_slug:
            account_slug = (
                "account-" + hashlib.md5(signup_data.account_name.encode(), usedforsecurity=False).hexdigest()[:8]
            )

    # Check if slug exists
    account_repo = AccountRepository(db)
    existing = await account_repo.get_by_slug(account_slug)
    if existing:
        raise HTTPException(status_code=400, detail=f"Account slug '{account_slug}' already exists")

    # Create account
    account = await account_repo.create(
        name=signup_data.account_name,
        slug=account_slug,
        account_type="personal",
    )

    # For now, we'll use WorkOS for user creation
    # In a full implementation, you'd create a user record here
    # For now, return account info - user will authenticate via WorkOS

    await db.commit()

    return {
        "account": {
            "id": account.id,
            "name": account.name,
            "slug": account.slug,
            "account_type": account.account_type,
        },
        "message": "Account created. Please sign in with WorkOS.",
    }


async def login_handler(
    data: dict[str, object],
    _db: AsyncSession,
) -> dict[str, object]:
    """Login endpoint - currently delegates to WorkOS AuthKit."""
    try:
        LoginRequest.model_validate(data)  # validate request body
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # For now, login is handled by WorkOS AuthKit on the frontend
    # This endpoint can be used for custom auth in the future
    # Return instructions to use WorkOS
    return {
        "message": "Please use WorkOS AuthKit for authentication",
        "workos_enabled": bool(os.environ.get("WORKOS_CLIENT_ID")),
    }


async def device_code_handler(data: dict[str, object]) -> DeviceCodeResponse:
    """Start device authorization flow. Returns device code and verification URL.

    The user navigates to the verification URL and enters the user code.
    The device then polls /api/v1/auth/device/token to complete authentication.
    """
    try:
        request_data = DeviceCodeRequest.model_validate(data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    client_id = request_data.client_id or os.getenv("WORKOS_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="WORKOS_CLIENT_ID is required")

    # Generate device code (high entropy for security)
    device_code = secrets.token_urlsafe(32)
    user_code = secrets.token_urlsafe(8).upper()  # 8 char uppercase code

    # Build verification URL - use WorkOS AuthKit or fallback
    authkit_domain = os.getenv("WORKOS_AUTHKIT_DOMAIN")
    if authkit_domain:
        verification_uri = f"{authkit_domain.rstrip('/')}/device"
        verification_uri_complete = f"{verification_uri}?user_code={user_code}"
    else:
        # Fallback to API server for testing
        base_url = os.getenv("APP_URL", "http://localhost:8000")
        verification_uri = f"{base_url}/device"
        verification_uri_complete = f"{verification_uri}?user_code={user_code}"

    # Store device code with metadata
    _device_code_store[device_code] = {
        "user_code": user_code,
        "client_id": client_id,
        "created_at": time.time(),
        "expires_in": 900,  # 15 minutes default
        "interval": 5,  # polling interval in seconds
        "completed": False,
        "tokens": None,
    }

    return DeviceCodeResponse(
        device_code=device_code,
        user_code=user_code,
        verification_uri=verification_uri,
        verification_uri_complete=verification_uri_complete,
        expires_in=900,
        interval=5,
    )


async def device_token_handler(data: dict[str, object]) -> DeviceTokenResponse:
    """Poll for device authorization completion.

    The device should poll this endpoint with the device_code until
    authentication is complete or the code expires.
    Returns access_token on success, or 400 with 'authorization_pending'
    while waiting, or 'expired_token' if the code has expired.
    """
    try:
        request_data = DeviceTokenRequest.model_validate(data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    device_code = request_data.device_code

    # Check if device code exists and is valid
    code_data = _device_code_store.get(device_code)
    if not code_data:
        raise HTTPException(status_code=400, detail="invalid_grant")

    # Check expiration
    elapsed = time.time() - code_data["created_at"]
    if elapsed > code_data["expires_in"]:
        del _device_code_store[device_code]
        raise HTTPException(status_code=400, detail="expired_token")

    # Check if authorization is complete
    if code_data["completed"] and code_data["tokens"]:
        # Clean up after returning tokens
        del _device_code_store[device_code]
        tokens = code_data["tokens"]
        return DeviceTokenResponse(
            access_token=tokens.get("access_token", ""),
            token_type=tokens.get("token_type", "bearer"),
            expires_in=tokens.get("expires_in"),
            refresh_token=tokens.get("refresh_token"),
            user=tokens.get("user"),
        )

    # Still waiting for user authorization
    raise HTTPException(
        status_code=400,
        detail="authorization_pending",
        headers={"Retry-After": str(code_data["interval"])},
    )


async def device_complete_handler(data: dict[str, object]) -> dict[str, object]:
    """Complete device authorization from browser.

    This endpoint is called by the browser after the user enters the code.
    """
    user_code = _require_user_code(data)
    found_code = _find_pending_device_code(user_code)
    auth_code = _require_auth_code(data)
    _require_workos_api_key()
    result = _exchange_auth_code(auth_code)
    _device_code_store[found_code]["completed"] = True
    _device_code_store[found_code]["tokens"] = result
    return {"status": "authorized", "user": _extract_user_info(result)}


def _require_user_code(data: dict[str, object]) -> str:
    user_code = data.get("user_code")
    if not user_code:
        raise HTTPException(status_code=400, detail="user_code required")
    return cast("str", user_code)


def _find_pending_device_code(user_code: str) -> str:
    for code, code_data in _device_code_store.items():
        if code_data.get("user_code") == user_code and not code_data["completed"]:
            return code
    raise HTTPException(status_code=400, detail="Invalid or expired user code")


def _require_auth_code(data: dict[str, object]) -> str:
    auth_code = data.get("code")
    if not auth_code:
        raise HTTPException(status_code=400, detail="authorization code required")
    return cast("str", auth_code)


def _require_workos_api_key() -> None:
    api_key = os.getenv("WORKOS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Server configuration error")


def _exchange_auth_code(auth_code: str) -> dict[str, object]:
    try:
        return workos_auth_service.authenticate_with_code(auth_code)
    except WORKOS_HANDLER_ERRORS as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {e!s}") from e


def _extract_user_info(result: dict[str, object]) -> dict[str, object] | None:
    user_obj = result.get("user")
    if user_obj:
        return cast("dict[str, object]", user_obj)
    access_token = result.get("access_token")
    if access_token:
        try:
            claims = workos_auth_service.verify_access_token(cast("str", access_token))
            return {"sub": claims.get("sub"), "email": claims.get("email")}
        except TOKEN_EXTRACTION_ERRORS:
            return None
    return None


# ==================== FastAPI Endpoint Wrappers ====================


async def auth_callback_endpoint(payload: AuthCallbackPayload) -> dict[str, object]:
    """FastAPI endpoint wrapper for auth callback."""
    return await auth_callback_handler(payload)


async def auth_me_endpoint(
    claims: dict[str, object] = Depends(lambda: None),  # Will be provided by main.py
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """FastAPI endpoint wrapper for auth/me."""
    return await auth_me_handler(claims, db)


async def auth_logout_endpoint(
    claims: dict[str, object] = Depends(lambda: None),  # Will be provided by main.py
) -> dict[str, object]:
    """FastAPI endpoint wrapper for auth logout."""
    return await auth_logout_handler(claims)


async def signup_endpoint(
    data: dict[str, object],
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """FastAPI endpoint wrapper for signup."""
    return await signup_handler(data, db)


async def login_endpoint(
    data: dict[str, object],
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """FastAPI endpoint wrapper for login."""
    return await login_handler(data, db)


async def device_code_endpoint(data: dict[str, object]) -> DeviceCodeResponse:
    """FastAPI endpoint wrapper for device code."""
    return await device_code_handler(data)


async def device_token_endpoint(data: dict[str, object]) -> DeviceTokenResponse:
    """FastAPI endpoint wrapper for device token."""
    return await device_token_handler(data)


async def device_complete_endpoint(data: dict[str, object]) -> dict[str, object]:
    """FastAPI endpoint wrapper for device complete."""
    return await device_complete_handler(data)
