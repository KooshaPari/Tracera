"""Protocol for database monitoring implementations.

This module defines the DatabaseProvider protocol for database monitoring.
"""

from typing import Protocol


class DatabaseProvider(Protocol):
    """Protocol for database monitoring implementations.

    Implement this protocol to integrate database monitoring into the widget.
    Supports any database system (PostgreSQL, MySQL, MongoDB, etc.).

    Example:
        class PostgreSQLProvider:
            def __init__(self, pool):
                self.pool = pool

            async def get_pool_stats(self) -> Dict[str, int]:
                return {
                    "active": self.pool.get_size() - self.pool.get_idle_size(),
                    "idle": self.pool.get_idle_size(),
                    "total": self.pool.get_size(),
                    "max": self.pool.get_max_size()
                }

            async def get_query_latency(self) -> float:
                start = time.perf_counter()
                async with self.pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                return (time.perf_counter() - start) * 1000

            async def check_health(self) -> bool:
                try:
                    async with self.pool.acquire() as conn:
                        await conn.fetchval("SELECT 1")
                    return True
                except Exception:
                    return False
    """

    async def get_pool_stats(self) -> dict[str, int]:
        """Get connection pool statistics.

        Returns:
            Dict with keys:
                - active: Number of active connections
                - idle: Number of idle connections
                - total: Total connections
                - max: Maximum connections
        """
        ...

    async def get_query_latency(self) -> float:
        """Get average query latency in milliseconds.

        Returns:
            float: Average query latency in ms
        """
        ...

    async def check_health(self) -> bool:
        """Check if database is healthy.

        Returns:
            bool: True if database is healthy
        """
        ...
