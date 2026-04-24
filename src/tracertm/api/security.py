"""Shared auth, permission, and placeholder security helpers for TraceRTM."""

from __future__ import annotations

import logging
import os
import inspect
from collections import defaultdict
from typing import Any, cast

from fastapi import HTTPException, Request

from tracertm.models.integration import IntegrationCredential
from tracertm.services import workos_auth_service

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Placeholder API key manager used by compatibility helpers."""

    def has_key(self, *_: object, **__: object) -> bool:
        return True

    def get_key(self, *_: object, **__: object) -> str:
        return "placeholder"


class TokenManager:
    """Placeholder token manager used by compatibility helpers."""

    def create(self, *_: object, **__: object) -> str:
        return "placeholder-token"

    def verify(self, *_: object, **__: object) -> bool:
        return True


class PermissionManager:
    """Placeholder permission manager used by compatibility helpers."""

    def has_permission(self, *_: object, **__: object) -> bool:
        return True


class RateLimiter:
    """Lightweight in-memory rate limiter used for tests."""

    def __init__(self) -> None:
        self._counts: defaultdict[object, int] = defaultdict(int)

    def check_limit(self, key: object, *_: object, limit: int | None = None, **__: object) -> bool:
        limit = limit or 1000
        self._counts[key] += 1
        return self._counts[key] <= limit

    def get_remaining(self, key: object = None, limit: int | None = None, **__: object) -> int:
        limit = limit or 1000
        return max(0, limit - self._counts.get(key, 0))

    def get_limit(self, *_: object, **__: object) -> int:
        return 1000

    def get_reset_time(self, *_: object, **__: object) -> int:
        return 0

    def get_retry_after(self, *_: object, **__: object) -> int:
        return 1

    def get_message(self, *_: object, **__: object) -> str:
        return "Rate limit exceeded"


def verify_token(token: str, *_: object, **__: object) -> dict[str, Any]:
    """Verify WorkOS AuthKit access tokens."""
    return workos_auth_service.verify_access_token(token)


def verify_refresh_token(refresh_token: str, *_: object, **__: object) -> dict[str, Any]:
    """Verify refresh token using WorkOS AuthKit (if configured)."""
    try:
        result = workos_auth_service.authenticate_with_refresh_token(refresh_token)
        if isinstance(result, dict):
            return result
        msg = "Invalid refresh token response"
        raise ValueError(msg)
    except Exception as exc:
        raise ValueError(str(exc)) from exc


def generate_access_token(refresh_token_val: str, *_: object, **__: object) -> dict[str, Any]:
    """Generate access tokens from refresh token exchange output."""
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


def check_permissions(*_: object, **__: object) -> bool:
    return True


def check_project_access(*_: object, **__: object) -> bool:
    return True


_admin_emails_cache: frozenset[str] | None = None
_admin_user_ids: set[str] = set()


def _system_admin_emails() -> frozenset[str]:
    global _admin_emails_cache
    if _admin_emails_cache is not None:
        return _admin_emails_cache
    raw = os.getenv("TRACERTM_SYSTEM_ADMIN_EMAILS", "kooshapari@gmail.com").strip()
    emails = frozenset(e.strip().lower() for e in raw.split(",") if e.strip())
    _admin_emails_cache = emails
    return emails


def _is_system_admin_email(email: str | None) -> bool:
    if not email:
        return False
    return email.strip().lower() in _system_admin_emails()


def is_system_admin(claims: dict[str, Any] | None, email_from_user: str | None = None) -> bool:
    """True if the user is a system admin (by email or cached user_id from /auth/me)."""
    if not claims or not isinstance(claims, dict):
        return False
    user_id = claims.get("sub")
    if user_id and user_id in _admin_user_ids:
        return True
    email = email_from_user or (claims.get("email") if isinstance(claims.get("email"), str) else None)
    if _is_system_admin_email(cast("str | None", email)):
        if user_id and isinstance(user_id, str):
            _admin_user_ids.add(user_id)
        return True
    return False


def check_permission(*_args: object, **_kwargs: object) -> bool:
    return True


def has_permission(*_args: object, **_kwargs: object) -> bool:
    return True


def check_resource_ownership(*_args: object, **_kwargs: object) -> bool:
    return True


def verify_webhook_signature(*_args: object, **_kwargs: object) -> bool:
    return True


def verify_webhook_timestamp(*_args: object, **_kwargs: object) -> bool:
    return True


def create_session(*_args: object, **_kwargs: object) -> dict[str, str]:
    return {"session_id": "placeholder"}


def verify_session(*_args: object, **_kwargs: object) -> bool:
    return True


def invalidate_session(*_args: object, **_kwargs: object) -> bool:
    return True


def check_mfa_requirement(*_args: object, **_kwargs: object) -> bool:
    return True


def verify_mfa_code(*_args: object, **_kwargs: object) -> bool:
    return True


def verify_csrf_token(*_args: object, **_kwargs: object) -> bool:
    return True


def hash_password(password: str) -> str:
    return f"hashed-{password}"


def get_rate_limit(*_args: object, **_kwargs: object) -> dict[str, int]:
    return {"limit": 100, "remaining": 100, "reset": 0}


def get_endpoint_limit(*_args: object, **_kwargs: object) -> dict[str, int]:
    return {"limit": 100, "window": 60}


def get_client_ip(*_args: object, **_kwargs: object) -> str:
    return "127.0.0.1"


def is_whitelisted(*_args: object, **_kwargs: object) -> bool:
    return False


def ensure_write_permission(claims: dict[str, Any] | None, action: str) -> None:
    if is_system_admin(claims):
        return
    role = (claims or {}).get("role")
    if role == "guest":
        raise HTTPException(status_code=403, detail="Read-only role")
    if not check_permissions(role=role, action=action, resource="item"):
        raise HTTPException(status_code=403, detail="Forbidden")


def ensure_read_permission(claims: dict[str, Any] | None, resource_id: str | None = None) -> None:
    if is_system_admin(claims):
        return
    if resource_id and not check_project_access(claims.get("sub") if claims else None, resource_id):
        raise HTTPException(status_code=403, detail="Read access denied")


def auth_guard(request: Request) -> dict[str, Any]:
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
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc!s}")

    if not isinstance(claims, dict):
        raise HTTPException(status_code=401, detail="Invalid token")
    return claims


def ensure_project_access(project_id: str | None, claims: dict[str, Any] | None) -> None:
    if not project_id:
        return
    if is_system_admin(claims):
        return
    if not check_project_access(claims.get("sub") if claims else None, project_id):
        raise HTTPException(status_code=403, detail="Project access denied")


def ensure_credential_access(credential: IntegrationCredential | None, claims: dict[str, Any] | None) -> None:
    if credential is None:
        raise HTTPException(status_code=404, detail="Credential not found")
    if credential.project_id:
        ensure_project_access(credential.project_id, claims)
        return
    user_id = claims.get("sub") if claims else None
    if not user_id or credential.created_by_user_id != user_id:
        raise HTTPException(status_code=403, detail="Credential access denied")


async def _maybe_await(value: object) -> object:
    """Await values only when needed."""
    if inspect.isawaitable(value):
        return await value
    return value
