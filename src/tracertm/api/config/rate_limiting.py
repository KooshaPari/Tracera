"""Rate limiting configuration and enforcement.

Extracted from main.py to reduce complexity (C901 violations).
Breaks down enforce_rate_limit (complexity 12-14) into focused functions.
"""

import inspect
import logging
from collections import defaultdict
from typing import Any

from fastapi import HTTPException, Request

logger = logging.getLogger(__name__)

# Track rate limit counts per (key, method, path)
_rate_limit_counts: defaultdict[tuple[str, str, str], int] = defaultdict(int)


def should_skip_rate_limiting(request: Request | None, claims: dict[str, Any] | None) -> bool:
    """Check if rate limiting should be skipped for this request.

    Args:
        request: FastAPI request object
        claims: Auth claims dictionary

    Returns:
        True if rate limiting should be skipped
    """
    # Skip when request is not injected (e.g. in tests)
    if request is None:
        return True

    # Check for bulk operation header
    if request.headers.get("X-Bulk-Operation") == "true":
        return True

    # Skip for bulk endpoints (POST /api/v1/items, POST /api/v1/links)
    if request.method == "POST" and request.url.path in {"/api/v1/items", "/api/v1/links"}:
        # Allow for public access (no auth) - bulk operations typically don't have auth
        if not claims or claims.get("role") == "public":
            return True

    return False


def should_bypass_for_user(request: Request, claims: dict[str, Any] | None) -> bool:
    """Check if the user/client should bypass rate limiting.

    Args:
        request: FastAPI request object
        claims: Auth claims dictionary

    Returns:
        True if user should bypass rate limiting
    """
    from tracertm.api.security import get_client_ip, is_whitelisted

    # Check if IP is whitelisted
    client_ip = get_client_ip(request) if inspect.signature(get_client_ip).parameters else get_client_ip()
    if is_whitelisted(client_ip):
        return True

    # Check if user has bypass flag in claims
    return bool(claims and claims.get("bypass_rate_limit"))


def get_rate_limit_key(request: Request, claims: dict[str, Any] | None) -> str:
    """Get the rate limit key for this request.

    Priority: user sub -> X-User-ID header -> client IP -> "anonymous"

    Args:
        request: FastAPI request object
        claims: Auth claims dictionary

    Returns:
        Rate limit key string
    """
    from typing import Any, cast

    from tracertm.api.security import get_client_ip

    key: str | None = cast("str | None", claims.get("sub")) if claims else None
    client_ip = get_client_ip(request) if inspect.signature(get_client_ip).parameters else get_client_ip()
    return cast("str", key or request.headers.get("X-User-ID") or client_ip or "anonymous")


def get_resolved_limit(request: Request) -> int | None:
    """Get the resolved rate limit for this endpoint.

    Args:
        request: FastAPI request object

    Returns:
        Integer limit or None if not specified
    """
    from tracertm.api.security import get_endpoint_limit

    limit_info = get_endpoint_limit(request.method, request.url.path)
    resolved_limit: int | None = None

    if isinstance(limit_info, dict):
        val = limit_info.get("limit")
        resolved_limit = val if isinstance(val, int) else None
    elif isinstance(limit_info, int):
        resolved_limit = limit_info

    return resolved_limit


def check_rate_limit(
    key: str,
    request: Request,
    resolved_limit: int | None,
) -> bool:
    """Check if the request is within rate limits.

    Args:
        key: Rate limit key
        request: FastAPI request object
        resolved_limit: Resolved rate limit

    Returns:
        True if request is allowed
    """
    from tracertm.api.security import RateLimiter

    limiter_class = RateLimiter
    limiter = limiter_class()

    # Check with limiter
    allowed = limiter.check_limit(key, method=request.method, path=request.url.path, limit=resolved_limit)

    # Track count and check against resolved limit
    rate_key = (key, request.method, request.url.path)
    if rate_key not in _rate_limit_counts:
        _rate_limit_counts[rate_key] = 0
    _rate_limit_counts[rate_key] += 1

    return not (
        allowed is False or (resolved_limit is not None and _rate_limit_counts[rate_key] > (resolved_limit or 0))
    )


def raise_rate_limit_error(key: str, request: Request) -> None:
    """Raise HTTPException for rate limit exceeded.

    Args:
        key: Rate limit key
        request: FastAPI request object

    Raises:
        HTTPException: 429 Too Many Requests
    """
    from tracertm.api.security import RateLimiter

    limiter_class = RateLimiter
    limiter = limiter_class()

    retry_after = getattr(limiter, "get_retry_after", lambda *_args, **_kwargs: None)(
        key,
        request.method,
        request.url.path,
    )
    message = getattr(limiter, "get_message", lambda *_args, **_kwargs: "Rate limit exceeded")(
        key,
        request.method,
        request.url.path,
    )
    headers = {"Retry-After": str(retry_after)} if retry_after is not None else None

    raise HTTPException(status_code=429, detail=message, headers=headers)


def enforce_rate_limit(request: Request | None, claims: dict[str, Any] | None) -> None:
    """Apply rate limiting to the request.

    Refactored to reduce complexity from 12-14 to ~5.

    Args:
        request: FastAPI request object
        claims: Auth claims dictionary

    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    # Check if we should skip rate limiting
    if should_skip_rate_limiting(request, claims):
        return

    # After skip check, request is guaranteed non-None (skip returns True for None)
    assert request is not None  # narrowed by should_skip_rate_limiting

    # Check if user should bypass rate limiting
    if should_bypass_for_user(request, claims):
        return

    # Get rate limit key and limit
    key = get_rate_limit_key(request, claims)
    resolved_limit = get_resolved_limit(request)

    # Check if request is within limits
    allowed = check_rate_limit(key, request, resolved_limit)

    # Raise error if limit exceeded
    if not allowed:
        raise_rate_limit_error(key, request)
