from __future__ import annotations

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from tracertm.api.config.rate_limiting import RateLimitConfig, RateLimiter


def request(path: str) -> Request:
    return Request({"type": "http", "method": "POST", "path": path, "headers": []})


def test_rate_limit_is_isolated_by_authenticated_principal() -> None:
    limiter = RateLimiter(RateLimitConfig(limit=1, window_seconds=60, max_buckets=10))

    limiter.enforce(request("/api/v1/impact"), {"sub": "alice"})
    limiter.enforce(request("/api/v1/impact"), {"sub": "bob"})

    with pytest.raises(HTTPException) as error:
        limiter.enforce(request("/api/v1/impact"), {"sub": "alice"})
    assert error.value.status_code == 429
    assert int(error.value.headers["Retry-After"]) >= 1


def test_non_sensitive_route_is_not_limited() -> None:
    limiter = RateLimiter(RateLimitConfig(limit=1, window_seconds=60, max_buckets=10))

    limiter.enforce(request("/health"), {"sub": "alice"})
    limiter.enforce(request("/health"), {"sub": "alice"})


def test_bucket_capacity_is_bounded_and_oldest_principal_evicted() -> None:
    limiter = RateLimiter(RateLimitConfig(limit=1, window_seconds=60, max_buckets=2))

    for principal in ("alice", "bob", "carol"):
        limiter.enforce(request("/api/v1/impact"), {"sub": principal})

    assert limiter.bucket_count == 2


def test_missing_principal_fails_closed_on_sensitive_route() -> None:
    limiter = RateLimiter(RateLimitConfig(limit=1, window_seconds=60, max_buckets=10))

    with pytest.raises(HTTPException) as error:
        limiter.enforce(request("/api/v1/impact"), {})
    assert error.value.status_code == 401
