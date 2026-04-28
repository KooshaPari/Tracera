"""Rate limiting utilities for development and production use.

Provides both simple and advanced rate limiting implementations.
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque


class SlidingWindowRateLimiter:
    """Sliding window rate limiter implementation.

    Tracks requests in a sliding time window and enforces rate limits.
    """

    def __init__(self, window_seconds: int = 60, max_requests: int = 100):
        """Initialize the rate limiter.

        Args:
            window_seconds: Size of the sliding window in seconds
            max_requests: Maximum number of requests allowed in the window
        """
        self.window_seconds = window_seconds
        self.max_requests = max_requests
        self.requests: dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str = "default") -> bool:
        """Check if a request is allowed for the given key.

        Args:
            key: Unique identifier for the rate limit (e.g., user ID, IP)

        Returns:
            True if request is allowed, False if rate limited
        """
        async with self._lock:
            now = time.time()
            window_start = now - self.window_seconds

            # Clean old requests outside the window
            requests_queue = self.requests[key]
            while requests_queue and requests_queue[0] < window_start:
                requests_queue.popleft()

            # Check if we're under the limit
            if len(requests_queue) < self.max_requests:
                requests_queue.append(now)
                return True

            return False

    def is_allowed_sync(self, key: str = "default") -> bool:
        """Synchronous version of is_allowed.

        Args:
            key: Unique identifier for the rate limit

        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests outside the window
        requests_queue = self.requests[key]
        while requests_queue and requests_queue[0] < window_start:
            requests_queue.popleft()

        # Check if we're under the limit
        if len(requests_queue) < self.max_requests:
            requests_queue.append(now)
            return True

        return False

    def get_remaining_requests(self, key: str = "default") -> int:
        """Get the number of remaining requests for a key.

        Args:
            key: Unique identifier for the rate limit

        Returns:
            Number of remaining requests in the current window
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests outside the window
        requests_queue = self.requests[key]
        while requests_queue and requests_queue[0] < window_start:
            requests_queue.popleft()

        return max(0, self.max_requests - len(requests_queue))

    def reset(self, key: str = "default") -> None:
        """Reset the rate limit for a specific key.

        Args:
            key: Unique identifier for the rate limit
        """
        self.requests[key].clear()

    def reset_all(self) -> None:
        """Reset all rate limits."""
        self.requests.clear()


class RateLimiter:
    """Simple rate limiter wrapper.

    Provides a simplified interface for rate limiting.
    """

    def __init__(self, requests_per_minute: int = 60):
        """Initialize the rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute
        """
        self.limiter = SlidingWindowRateLimiter(
            window_seconds=60,
            max_requests=requests_per_minute,
        )

    async def is_allowed(self, key: str = "default") -> bool:
        """Check if a request is allowed.

        Args:
            key: Unique identifier for the rate limit

        Returns:
            True if request is allowed, False if rate limited
        """
        return await self.limiter.is_allowed(key)

    def is_allowed_sync(self, key: str = "default") -> bool:
        """Synchronous version of is_allowed.

        Args:
            key: Unique identifier for the rate limit

        Returns:
            True if request is allowed, False if rate limited
        """
        return self.limiter.is_allowed_sync(key)

    def get_remaining_requests(self, key: str = "default") -> int:
        """Get remaining requests for a key.

        Args:
            key: Unique identifier for the rate limit

        Returns:
            Number of remaining requests
        """
        return self.limiter.get_remaining_requests(key)


__all__ = [
    "RateLimiter",
    "SlidingWindowRateLimiter",
]
