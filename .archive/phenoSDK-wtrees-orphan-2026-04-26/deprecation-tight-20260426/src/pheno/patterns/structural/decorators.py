"""Decorator Pattern implementations for adding cross-cutting concerns.

Decorators wrap repository and use case implementations to add functionality like
caching, logging, retry logic, and metrics.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

    from pheno.application.ports.repositories import UserRepository
    from pheno.domain.entities.user import User
    from pheno.domain.value_objects.common import UserId

T = TypeVar("T")

logger = logging.getLogger(__name__)


class RepositoryDecorator:
    """Base decorator for repository implementations.

    This provides a template for creating repository decorators that add cross-cutting
    concerns.
    """

    def __init__(self, repository: Any):
        """Initialize the decorator.

        Args:
            repository: The repository to decorate
        """
        self._repository = repository

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the wrapped repository.
        """
        return getattr(self._repository, name)


class CachingDecorator(RepositoryDecorator):
    """Caching decorator for repositories.

    Adds caching functionality to repository operations to reduce
    database queries and improve performance.

    Example:
        user_repo = InMemoryUserRepository()
        cached_repo = CachingDecorator(user_repo, ttl=300)
    """

    def __init__(self, repository: UserRepository, ttl: int = 300):
        """Initialize the caching decorator.

        Args:
            repository: The repository to decorate
            ttl: Time-to-live for cache entries in seconds
        """
        super().__init__(repository)
        self._cache: dict[str, tuple[Any, float]] = {}
        self._ttl = ttl

    def _get_cache_key(self, method: str, *args, **kwargs) -> str:
        """
        Generate a cache key from method name and arguments.
        """
        key_parts = [method]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return ":".join(key_parts)

    def _is_expired(self, timestamp: float) -> bool:
        """
        Check if a cache entry has expired.
        """
        return time.time() - timestamp > self._ttl

    async def find_by_id(self, user_id: UserId) -> User | None:
        """
        Find user by ID with caching.
        """
        cache_key = self._get_cache_key("find_by_id", str(user_id.value))

        # Check cache
        if cache_key in self._cache:
            value, timestamp = self._cache[cache_key]
            if not self._is_expired(timestamp):
                logger.debug(f"Cache hit for {cache_key}")
                return value

        # Cache miss - fetch from repository
        logger.debug(f"Cache miss for {cache_key}")
        result = await self._repository.find_by_id(user_id)

        # Store in cache
        self._cache[cache_key] = (result, time.time())

        return result

    async def save(self, user: User) -> None:
        """
        Save user and invalidate cache.
        """
        await self._repository.save(user)

        # Invalidate cache for this user
        cache_key = self._get_cache_key("find_by_id", str(user.id.value))
        if cache_key in self._cache:
            del self._cache[cache_key]

    def clear_cache(self) -> None:
        """
        Clear all cache entries.
        """
        self._cache.clear()


class LoggingDecorator(RepositoryDecorator):
    """Logging decorator for repositories.

    Adds logging to all repository operations for debugging
    and monitoring purposes.

    Example:
        user_repo = InMemoryUserRepository()
        logged_repo = LoggingDecorator(user_repo)
    """

    def __init__(self, repository: UserRepository, logger_name: str | None = None):
        """Initialize the logging decorator.

        Args:
            repository: The repository to decorate
            logger_name: Optional logger name (defaults to repository class name)
        """
        super().__init__(repository)
        self._logger = logging.getLogger(logger_name or repository.__class__.__name__)

    async def find_by_id(self, user_id: UserId) -> User | None:
        """
        Find user by ID with logging.
        """
        self._logger.info(f"Finding user by ID: {user_id.value}")
        start_time = time.time()

        try:
            result = await self._repository.find_by_id(user_id)
            elapsed = time.time() - start_time

            if result:
                self._logger.info(f"Found user {user_id.value} in {elapsed:.3f}s")
            else:
                self._logger.warning(f"User {user_id.value} not found in {elapsed:.3f}s")

            return result
        except Exception as e:
            elapsed = time.time() - start_time
            self._logger.exception(f"Error finding user {user_id.value} after {elapsed:.3f}s: {e}")
            raise

    async def save(self, user: User) -> None:
        """
        Save user with logging.
        """
        self._logger.info(f"Saving user: {user.id.value}")
        start_time = time.time()

        try:
            await self._repository.save(user)
            elapsed = time.time() - start_time
            self._logger.info(f"Saved user {user.id.value} in {elapsed:.3f}s")
        except Exception as e:
            elapsed = time.time() - start_time
            self._logger.exception(f"Error saving user {user.id.value} after {elapsed:.3f}s: {e}")
            raise


class RetryDecorator(RepositoryDecorator):
    """Retry decorator for repositories.

    Adds automatic retry logic for transient failures.

    Example:
        user_repo = InMemoryUserRepository()
        retry_repo = RetryDecorator(user_repo, max_retries=3, delay=1.0)
    """

    def __init__(
        self,
        repository: UserRepository,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
    ):
        """Initialize the retry decorator.

        Args:
            repository: The repository to decorate
            max_retries: Maximum number of retry attempts
            delay: Initial delay between retries in seconds
            backoff: Backoff multiplier for exponential backoff
        """
        super().__init__(repository)
        self._max_retries = max_retries
        self._delay = delay
        self._backoff = backoff

    async def _retry_operation(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Execute an operation with retry logic.
        """
        last_exception = None

        for attempt in range(self._max_retries + 1):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self._max_retries:
                    wait_time = self._delay * (self._backoff**attempt)
                    logger.warning(
                        f"Operation failed (attempt {attempt + 1}/{self._max_retries + 1}), "
                        f"retrying in {wait_time:.1f}s: {e}",
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.exception(f"Operation failed after {self._max_retries + 1} attempts: {e}")

        raise last_exception

    async def find_by_id(self, user_id: UserId) -> User | None:
        """
        Find user by ID with retry logic.
        """
        return await self._retry_operation(self._repository.find_by_id, user_id)

    async def save(self, user: User) -> None:
        """
        Save user with retry logic.
        """
        await self._retry_operation(self._repository.save, user)


class MetricsDecorator(RepositoryDecorator):
    """Metrics decorator for repositories.

    Collects metrics about repository operations for monitoring
    and performance analysis.

    Example:
        user_repo = InMemoryUserRepository()
        metrics_repo = MetricsDecorator(user_repo)
    """

    def __init__(self, repository: UserRepository):
        """Initialize the metrics decorator.

        Args:
            repository: The repository to decorate
        """
        super().__init__(repository)
        self._metrics: dict[str, dict[str, Any]] = {}

    def _record_metric(self, operation: str, duration: float, success: bool) -> None:
        """
        Record a metric for an operation.
        """
        if operation not in self._metrics:
            self._metrics[operation] = {
                "count": 0,
                "success_count": 0,
                "failure_count": 0,
                "total_duration": 0.0,
                "min_duration": float("inf"),
                "max_duration": 0.0,
            }

        metrics = self._metrics[operation]
        metrics["count"] += 1
        metrics["total_duration"] += duration
        metrics["min_duration"] = min(metrics["min_duration"], duration)
        metrics["max_duration"] = max(metrics["max_duration"], duration)

        if success:
            metrics["success_count"] += 1
        else:
            metrics["failure_count"] += 1

    async def find_by_id(self, user_id: UserId) -> User | None:
        """
        Find user by ID with metrics collection.
        """
        start_time = time.time()
        success = False

        try:
            result = await self._repository.find_by_id(user_id)
            success = True
            return result
        finally:
            duration = time.time() - start_time
            self._record_metric("find_by_id", duration, success)

    async def save(self, user: User) -> None:
        """
        Save user with metrics collection.
        """
        start_time = time.time()
        success = False

        try:
            await self._repository.save(user)
            success = True
        finally:
            duration = time.time() - start_time
            self._record_metric("save", duration, success)

    def get_metrics(self) -> dict[str, dict[str, Any]]:
        """
        Get collected metrics.
        """
        # Calculate averages
        result = {}
        for operation, metrics in self._metrics.items():
            result[operation] = {
                **metrics,
                "avg_duration": (
                    metrics["total_duration"] / metrics["count"] if metrics["count"] > 0 else 0.0
                ),
                "success_rate": (
                    metrics["success_count"] / metrics["count"] if metrics["count"] > 0 else 0.0
                ),
            }
        return result

    def reset_metrics(self) -> None:
        """
        Reset all metrics.
        """
        self._metrics.clear()
