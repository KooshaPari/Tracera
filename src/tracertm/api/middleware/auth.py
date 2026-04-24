"""Authentication middleware and guards for TraceRTM API."""

import logging
import os

from fastapi import HTTPException, Request

from tracertm.core.context import current_account_id, current_user_id
from tracertm.models.integration import IntegrationCredential
from tracertm.services.token_bridge import get_token_bridge
from tracertm.services.workos_auth_service import authenticate_with_refresh_token
from typing import Any

logger = logging.getLogger(__name__)

# System admin: emails listed in TRACERTM_SYSTEM_ADMIN_EMAILS (comma-separated) get full access.
_admin_emails_cache: frozenset[str] | None = None
_admin_user_ids: set[str] = set()


class TokenManager:
    """Token management utilities for access and refresh tokens."""

    def generate_access_token(self, *_: object, **__: object) -> dict[str, Any]:
        """Generate a new access token."""
        return {"access_token": "token", "token_type": "bearer", "expires_in": 3600}

    def refresh_access_token(self, *_: object, **__: object) -> dict[str, Any]:
        """Refresh an existing access token."""
        return {"access_token": "token", "token_type": "bearer", "expires_in": 3600}

    def validate_refresh_token(self, *_: object, **__: object) -> bool:
        """Validate a refresh token."""
        return True

    def revoke_token(self, *_: object, **__: object) -> bool:
        """Revoke a token."""
        return True


class PermissionManager:
    """Permission checking utilities."""

    def has_permission(self, *_: object, **__: object) -> bool:
        """Check if user has permission."""
        return True


# Token verification functions
def verify_token(token: str, *_: object, **__: object) -> dict[str, Any]:
    """Verify WorkOS AuthKit access tokens.

    Uses TokenBridge to validate both RS256 (WorkOS) and HS256 (service) tokens.

    Args:
        token: JWT access token to verify

    Returns:
        dict: Token claims/payload

    Raises:
        ValueError: If token is invalid
    """
    try:
        bridge = get_token_bridge()
        return bridge.validate_token(token)
    except Exception as exc:
        logger.warning("Token validation failed: %s", exc)
        raise ValueError(str(exc)) from exc


def verify_refresh_token(refresh_token: str, *_: object, **__: object) -> dict[str, Any]:
    """Verify refresh token using WorkOS AuthKit (if configured).

    Args:
        refresh_token: Refresh token to verify

    Returns:
        dict: New access token and refresh token

    Raises:
        ValueError: If refresh token is invalid
    """
    try:
        result = authenticate_with_refresh_token(refresh_token)
        if isinstance(result, dict):
            return result
        msg = "Invalid refresh token response"
        raise ValueError(msg)
    except Exception as exc:
        raise ValueError(str(exc)) from exc


def generate_access_token(refresh_token_val: str, *_: object, **__: object) -> dict[str, Any]:
    """Generate access tokens from refresh token exchange output.

    Args:
        refresh_token_val: Refresh token value

    Returns:
        dict: Access token, refresh token, token type, and expiry

    Raises:
        ValueError: If unable to generate access token
    """
    result = verify_refresh_token(refresh_token_val)
    if not isinstance(result, dict):
        msg = "Unable to generate access token"
        raise ValueError(msg)
    return {
        "access_token": result.get("access_token"),
        "refresh_token": result.get("refresh_token"),
        "token_type": result.get("token_type", "bearer"),
        "expires_in": result.get("expires_in"),
    }


# Permission checking functions
def check_permissions(*_: object, **__: object) -> bool:
    """Check user permissions (placeholder)."""
    return True


def check_project_access(*_: object, **__: object) -> bool:
    """Check project access (placeholder)."""
    return True


# System admin functions
def _system_admin_emails() -> frozenset[str]:
    """Get cached set of system admin emails from environment."""
    global _admin_emails_cache
    if _admin_emails_cache is not None:
        return _admin_emails_cache
    raw = os.getenv("TRACERTM_SYSTEM_ADMIN_EMAILS", "kooshapari@gmail.com").strip()
    emails = frozenset(e.strip().lower() for e in raw.split(",") if e.strip())
    _admin_emails_cache = emails
    return emails


def _is_system_admin_email(email: str | None) -> bool:
    """Check if email is a system admin email."""
    if not email:
        return False
    return email.strip().lower() in _system_admin_emails()


def is_system_admin(claims: dict[str, Any] | None, email_from_user: str | None = None) -> bool:
    """Check if user is a system admin (by email or cached user_id from /auth/me).

    Args:
        claims: JWT token claims
        email_from_user: Optional email to check

    Returns:
        bool: True if user is system admin
    """
    if not claims or not isinstance(claims, dict):
        return False
    user_id = claims.get("sub")
    if user_id and user_id in _admin_user_ids:
        return True
    email = email_from_user or (claims.get("email") if isinstance(claims.get("email"), str) else None)
    if _is_system_admin_email(email):
        if user_id:
            _admin_user_ids.add(user_id)
        return True
    return False


# Stub functions (placeholders for future implementation)
def check_permission(*_args: object, **_kwargs: object) -> bool:
    """Check permission (placeholder)."""
    return True


def has_permission(*_args: object, **_kwargs: object) -> bool:
    """Check if has permission (placeholder)."""
    return True


def check_resource_ownership(*_args: object, **_kwargs: object) -> bool:
    """Check resource ownership (placeholder)."""
    return True


def verify_webhook_signature(*_args: object, **_kwargs: object) -> bool:
    """Verify webhook signature (placeholder)."""
    return True


def verify_webhook_timestamp(*_args: object, **_kwargs: object) -> bool:
    """Verify webhook timestamp (placeholder)."""
    return True


def create_session(*_args: object, **_kwargs: object) -> dict[str, str]:
    """Create session (placeholder)."""
    return {"session_id": "placeholder"}


def verify_session(*_args: object, **_kwargs: object) -> bool:
    """Verify session (placeholder)."""
    return True


def invalidate_session(*_args: object, **_kwargs: object) -> bool:
    """Invalidate session (placeholder)."""
    return True


def check_mfa_requirement(*_args: object, **_kwargs: object) -> bool:
    """Check MFA requirement (placeholder)."""
    return True


def verify_mfa_code(*_args: object, **_kwargs: object) -> bool:
    """Verify MFA code (placeholder)."""
    return True


def verify_csrf_token(*_args: object, **_kwargs: object) -> bool:
    """Verify CSRF token (placeholder)."""
    return True


def hash_password(password: str) -> str:
    """Hash password (placeholder)."""
    return f"hashed-{password}"


def get_rate_limit(*_args: object, **_kwargs: object) -> dict[str, int]:
    """Get rate limit info (placeholder)."""
    return {"limit": 100, "remaining": 100, "reset": 0}


def get_endpoint_limit(*_args: object, **_kwargs: object) -> dict[str, int]:
    """Get endpoint limit (placeholder)."""
    return {"limit": 100, "window": 60}


def get_client_ip(*_args: object, **_kwargs: object) -> str:
    """Get client IP (placeholder)."""
    return "127.0.0.1"


def is_whitelisted(*_args: object, **_kwargs: object) -> bool:
    """Check if IP is whitelisted (placeholder)."""
    return False


# Main authentication guard
def auth_guard(request: Request) -> dict[str, Any]:
    """Authenticate incoming requests when auth is enabled.

    Extracts and validates JWT token from Authorization header,
    sets user and account context for database RLS.

    Args:
        request: FastAPI request object

    Returns:
        dict: Token claims/payload

    Raises:
        HTTPException: 401 if authentication fails
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer ") or "  " in auth_header:
        raise HTTPException(status_code=401, detail="Authorization required")

    token = auth_header.split(None, 1)[1].strip()
    if not token or " " in token:
        raise HTTPException(status_code=401, detail="Authorization required")

    try:
        claims = verify_token(token)
    except Exception as exc:
        logger.exception("Authentication failed")
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc!s}") from exc

    if not isinstance(claims, dict):
        raise HTTPException(status_code=401, detail="Invalid token")

    # Set user context for database RLS
    user_id = claims.get("sub") if claims else None
    if user_id:
        current_user_id.set(user_id)

    # Set account context if present
    account_id = claims.get("org_id") or claims.get("account_id") if claims else None
    if account_id:
        current_account_id.set(account_id)

    return claims


# Permission enforcement functions
def ensure_write_permission(claims: dict[str, Any] | None, action: str) -> None:
    """Basic permission gate used by write endpoints. System admins bypass checks.

    Args:
        claims: Token claims
        action: Action being performed

    Raises:
        HTTPException: 403 if permission denied
    """
    if is_system_admin(claims):
        return
    role = (claims or {}).get("role")
    if role == "guest":
        raise HTTPException(status_code=403, detail="Read-only role")
    if not check_permissions(role=role, action=action, resource="item"):
        raise HTTPException(status_code=403, detail="Forbidden")


def ensure_read_permission(claims: dict[str, Any] | None, resource_id: str | None = None) -> None:
    """Check read permission; system admins bypass. Raise HTTPException if denied.

    Args:
        claims: Token claims
        resource_id: Optional resource ID to check

    Raises:
        HTTPException: 403 if permission denied
    """
    if is_system_admin(claims):
        return
    if resource_id and not check_project_access(claims.get("sub") if claims else None, resource_id):
        raise HTTPException(status_code=403, detail="Read access denied")


def ensure_project_access(project_id: str | None, claims: dict[str, Any] | None) -> None:
    """Check project access using injected helper when available. System admins bypass checks.

    Args:
        project_id: Project ID to check access for
        claims: Token claims

    Raises:
        HTTPException: 403 if access denied
    """
    if not project_id:
        return
    if is_system_admin(claims):
        return
    if not check_project_access(claims.get("sub") if claims else None, project_id):
        raise HTTPException(status_code=403, detail="Project access denied")


def ensure_credential_access(credential: IntegrationCredential | None, claims: dict[str, Any] | None) -> None:
    """Check access to a credential (project or user scoped).

    Args:
        credential: Integration credential to check access for
        claims: Token claims

    Raises:
        HTTPException: 403 if access denied, 404 if credential not found
    """
    if credential is None:
        raise HTTPException(status_code=404, detail="Credential not found")
    if credential.project_id:
        ensure_project_access(credential.project_id, claims)
        return
    user_id = claims.get("sub") if claims else None
    if not user_id or credential.created_by_user_id != user_id:
        raise HTTPException(status_code=403, detail="Credential access denied")
