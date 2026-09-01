"""Bounded, per-principal rate limiting for expensive analysis routes."""

from __future__ import annotations

import os
import time
from collections import OrderedDict, deque
from dataclasses import dataclass
from math import ceil
from threading import Lock
from typing import Any

from fastapi import HTTPException, status
from starlette.requests import Request

DEFAULT_SENSITIVE_PREFIXES = (
    "/api/v1/impact",
    "/api/v1/trace",
    "/api/v1/blast-radius",
    "/api/v1/coverage-matrix",
    "/analysis/",
)


@dataclass(frozen=True)
class RateLimitConfig:
    """Runtime rate-limit policy, sourced explicitly from environment variables."""

    limit: int = 30
    window_seconds: float = 60.0
    max_buckets: int = 10_000
    sensitive_prefixes: tuple[str, ...] = DEFAULT_SENSITIVE_PREFIXES

    @classmethod
    def from_env(cls) -> RateLimitConfig:
        """Load and validate ``TRACERA_RATE_LIMIT_*`` settings."""
        limit = int(os.getenv("TRACERA_RATE_LIMIT_REQUESTS", str(cls.limit)))
        window = float(os.getenv("TRACERA_RATE_LIMIT_WINDOW_SECONDS", str(cls.window_seconds)))
        max_buckets = int(os.getenv("TRACERA_RATE_LIMIT_MAX_BUCKETS", str(cls.max_buckets)))
        prefixes = tuple(
            item.strip()
            for item in os.getenv("TRACERA_RATE_LIMIT_SENSITIVE_PREFIXES", "").split(",")
            if item.strip()
        ) or DEFAULT_SENSITIVE_PREFIXES
        if limit < 1 or window <= 0 or max_buckets < 1 or not prefixes:
            raise ValueError("Rate-limit settings must be positive and include sensitive routes")
        return cls(limit, window, max_buckets, prefixes)


class RateLimiter:
    """Thread-safe sliding-window limiter with bounded principal state."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._buckets: OrderedDict[str, deque[float]] = OrderedDict()
        self._lock = Lock()

    @property
    def bucket_count(self) -> int:
        with self._lock:
            return len(self._buckets)

    def enforce(self, request: Request, claims: dict[str, Any]) -> None:
        """Allow a request or raise a standards-compatible HTTP error."""
        if not request.url.path.startswith(self.config.sensitive_prefixes):
            return
        principal = claims.get("sub")
        if not isinstance(principal, str) or not principal.strip():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authenticated principal required")
        now = time.monotonic()
        with self._lock:
            timestamps = self._buckets.get(principal)
            if timestamps is None:
                if len(self._buckets) >= self.config.max_buckets:
                    self._buckets.popitem(last=False)
                timestamps = deque()
                self._buckets[principal] = timestamps
            else:
                self._buckets.move_to_end(principal)
            cutoff = now - self.config.window_seconds
            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()
            if len(timestamps) >= self.config.limit:
                retry_after = max(1, ceil(timestamps[0] + self.config.window_seconds - now))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": str(retry_after)},
                )
            timestamps.append(now)


_LIMITER: RateLimiter | None = None
_LIMITER_LOCK = Lock()


def enforce_rate_limit(request: Request, claims: dict[str, Any]) -> None:
    """Enforce the configured limiter, failing closed when configuration is invalid."""
    global _LIMITER
    with _LIMITER_LOCK:
        if _LIMITER is None:
            try:
                _LIMITER = RateLimiter(RateLimitConfig.from_env())
            except (TypeError, ValueError, OverflowError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Rate limiting configuration unavailable",
                ) from exc
    _LIMITER.enforce(request, claims)
