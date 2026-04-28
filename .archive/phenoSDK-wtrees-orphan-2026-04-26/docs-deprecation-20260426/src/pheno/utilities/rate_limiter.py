"""
Token bucket rate limiter with per-key configuration and async safety.
"""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class RateLimitRule:
    """
    Token bucket configuration for a specific key.
    """

    requests_per_period: float
    period_seconds: float
    burst: float | None = None

    @property
    def capacity(self) -> float:
        return float(self.burst if self.burst is not None else self.requests_per_period)

    @property
    def refill_rate(self) -> float:
        if self.period_seconds <= 0:
            raise ValueError("period_seconds must be positive")
        return float(self.requests_per_period) / float(self.period_seconds)


@dataclass(slots=True)
class _BucketState:
    capacity: float
    tokens: float
    refill_rate: float
    updated_at: float

    def refill(self, now: float) -> None:
        if now <= self.updated_at:
            return
        elapsed = now - self.updated_at
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.updated_at = now

    def consume(self, permits: float, now: float) -> bool:
        self.refill(now)
        if self.tokens >= permits:
            self.tokens -= permits
            return True
        return False

    def refund(self, permits: float) -> None:
        self.tokens = min(self.capacity, self.tokens + permits)

    def wait_time(self, permits: float, now: float) -> float:
        self.refill(now)
        if self.tokens >= permits:
            return 0.0
        deficit = permits - self.tokens
        if self.refill_rate <= 0:
            return float("inf")
        return deficit / self.refill_rate


class TokenBucketRateLimiter:
    """
    Per-key token bucket limiter with async locking.
    """

    def __init__(
        self,
        default_rule: RateLimitRule | None = None,
        clock: callable = time.monotonic,
    ) -> None:
        self._default_rule = default_rule or RateLimitRule(60, 60.0, burst=60)
        self._clock = clock
        self._rules: dict[str, RateLimitRule] = {}
        self._buckets: dict[str, _BucketState] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    @staticmethod
    def _normalize_key(key: Iterable[str] | str) -> str:
        if isinstance(key, str):
            return key
        return "::".join(str(part) for part in key)

    def configure_rule(self, key: Iterable[str] | str, rule: RateLimitRule) -> None:
        norm = self._normalize_key(key)
        self._rules[norm] = rule
        self._buckets.pop(norm, None)

    def reset(self, key: Iterable[str] | str | None = None) -> None:
        if key is None:
            self._buckets.clear()
            return
        norm = self._normalize_key(key)
        self._buckets.pop(norm, None)

    async def allow(self, key: Iterable[str] | str, permits: float = 1.0) -> bool:
        norm = self._normalize_key(key)
        lock = self._locks.setdefault(norm, asyncio.Lock())
        async with lock:
            bucket = self._ensure_bucket(norm)
            return bucket.consume(permits, self._clock())

    async def release(self, key: Iterable[str] | str, permits: float = 1.0) -> None:
        norm = self._normalize_key(key)
        lock = self._locks.setdefault(norm, asyncio.Lock())
        async with lock:
            bucket = self._ensure_bucket(norm)
            bucket.refund(permits)

    def get_retry_after(self, key: Iterable[str] | str, permits: float = 1.0) -> float:
        norm = self._normalize_key(key)
        bucket = self._ensure_bucket(norm)
        return bucket.wait_time(permits, self._clock())

    def get_remaining(self, key: Iterable[str] | str) -> float:
        norm = self._normalize_key(key)
        bucket = self._ensure_bucket(norm)
        bucket.refill(self._clock())
        return bucket.tokens

    def configure_defaults(
        self,
        *,
        requests_per_period: float,
        period_seconds: float,
        burst: float | None = None,
    ) -> None:
        self._default_rule = RateLimitRule(requests_per_period, period_seconds, burst)
        self._buckets.clear()

    @asynccontextmanager
    async def limit(
        self,
        key: Iterable[str] | str,
        permits: float = 1.0,
    ):
        allowed = await self.allow(key, permits)
        if not allowed:
            raise TimeoutError("Rate limit exceeded")
        try:
            yield
        finally:
            await self.release(key, permits)

    def _ensure_bucket(self, norm_key: str) -> _BucketState:
        bucket = self._buckets.get(norm_key)
        if bucket is None:
            rule = self._rules.get(norm_key, self._default_rule)
            bucket = _BucketState(
                capacity=rule.capacity,
                tokens=rule.capacity,
                refill_rate=rule.refill_rate,
                updated_at=self._clock(),
            )
            self._buckets[norm_key] = bucket
        return bucket


__all__ = ["RateLimitRule", "TokenBucketRateLimiter"]
