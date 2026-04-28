"""Database manager for MCP tools with connection pooling and query optimization.

This module provides a singleton DatabaseManager that:
- Manages async connection pools
- Provides optimized query patterns
- Tracks query performance
- Enables connection reuse across tool calls
"""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

from tracertm.config.manager import ConfigManager

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# Max number of slow queries to retain in memory
_MAX_SLOW_QUERIES = 100


class QueryMetrics:
    """Track query performance metrics."""

    def __init__(self) -> None:
        """Initialize query metrics."""
        self.slow_queries: list[dict[str, object]] = []
        self.query_count = 0
        self.total_duration = 0.0
        self.slow_threshold_ms = 100.0

    def record_query(self, query: str, duration_ms: float, params: dict[str, object] | None = None) -> None:
        """Record a query execution."""
        self.query_count += 1
        self.total_duration += duration_ms

        if duration_ms > self.slow_threshold_ms:
            self.slow_queries.append({
                "query": query,
                "duration_ms": duration_ms,
                "params": params,
                "timestamp": time.time(),
            })
            # Keep only last N slow queries
            if len(self.slow_queries) > _MAX_SLOW_QUERIES:
                self.slow_queries.pop(0)

    def get_stats(self) -> dict[str, object]:
        """Get current query statistics."""
        return {
            "total_queries": self.query_count,
            "total_duration_ms": self.total_duration,
            "avg_duration_ms": self.total_duration / max(1, self.query_count),
            "slow_queries_count": len(self.slow_queries),
            "recent_slow_queries": self.slow_queries[-10:] if self.slow_queries else [],
        }

    def reset(self) -> None:
        """Reset metrics."""
        self.slow_queries.clear()
        self.query_count = 0
        self.total_duration = 0.0


class DatabaseManager:
    """Singleton database manager with connection pooling and optimization.

    Features:
    - Async connection pooling (pool_size=10, max_overflow=20)
    - Connection reuse across tool calls
    - Query performance tracking
    - Automatic pool health monitoring
    """

    _instance: DatabaseManager | None = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __init__(self, database_url: str | None = None) -> None:
        """Initialize database manager.

        Args:
            database_url: Database URL (defaults to config or local SQLite)
        """
        if database_url is None:
            config = ConfigManager()
            db_url_obj = config.get("database_url")
            database_url = str(db_url_obj) if db_url_obj else None

        if not database_url:
            base_dir = Path.home() / ".tracertm"
            base_dir.mkdir(parents=True, exist_ok=True)
            # Convert to async SQLite URL
            database_url = f"sqlite+aiosqlite:///{base_dir / 'tracertm.db'}"

        # Convert sync PostgreSQL URL to async if needed
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        self.database_url = database_url
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker | None = None
        self.metrics = QueryMetrics()
        self._initialized = False

    @classmethod
    async def get_instance(cls, database_url: str | None = None) -> DatabaseManager:
        """Get or create the singleton DatabaseManager instance."""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(database_url)
                    await cls._instance.initialize()
        return cls._instance

    async def initialize(self) -> None:
        """Initialize connection pool and engine."""
        if self._initialized:
            return

        # Create async engine with optimized pool settings
        self._engine = create_async_engine(
            self.database_url,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=10,  # Base pool size
            max_overflow=20,  # Additional connections under load
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,  # Recycle connections after 1 hour
            echo=False,
            connect_args={"server_settings": {"jit": "off"}} if "postgresql" in self.database_url else {},
        )

        # Create session factory
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        # Set up query instrumentation
        self._setup_instrumentation()

        # Test connection
        async with self._engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        self._initialized = True

    def _setup_instrumentation(self) -> None:
        """Set up query performance tracking."""
        if not self._engine:
            return

        @event.listens_for(self._engine.sync_engine, "before_cursor_execute")
        def before_cursor_execute(
            _conn: object,
            _cursor: object,
            _statement: object,
            _parameters: object,
            context: object,
            _executemany: object,
        ) -> None:
            context._query_start_time = time.perf_counter()  # type: ignore[attr-defined]

        @event.listens_for(self._engine.sync_engine, "after_cursor_execute")
        def after_cursor_execute(
            _conn: object, _cursor: object, statement: object, parameters: object, context: object, _executemany: object
        ) -> None:
            duration_ms = (time.perf_counter() - context._query_start_time) * 1000  # type: ignore[attr-defined]
            self.metrics.record_query(str(statement), duration_ms, parameters if isinstance(parameters, dict) else None)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session from the pool.

        Usage:
            async with db_manager.session() as session:
                result = await session.execute(query)
        """
        if not self._session_factory:
            msg = "DatabaseManager not initialized. Call initialize() first."
            raise RuntimeError(msg)

        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def get_pool_status(self) -> dict[str, object]:
        """Get connection pool status."""
        if not self._engine:
            return {"status": "not_initialized"}

        pool = self._engine.pool
        size_fn = getattr(pool, "size", lambda: 0)
        checkedout_fn = getattr(pool, "checkedout", lambda: 0)
        overflow_fn = getattr(pool, "overflow", lambda: 0)
        size = size_fn() if callable(size_fn) else 0
        checked_out = checkedout_fn() if callable(checkedout_fn) else 0
        overflow = overflow_fn() if callable(overflow_fn) else 0
        return {
            "size": size,
            "checked_out": checked_out,
            "overflow": overflow,
            "checked_in": size - checked_out,
        }

    async def health_check(self) -> dict[str, object]:
        """Perform health check on database connection."""
        if not self._engine:
            return {"status": "error", "error": "Not initialized"}

        try:
            async with self._engine.begin() as conn:
                if "postgresql" in self.database_url:
                    result = await conn.execute(text("SELECT version()"))
                    version = result.scalar()
                else:
                    result = await conn.execute(text("SELECT sqlite_version()"))
                    version = f"SQLite {result.scalar()}"

            pool_status = await self.get_pool_status()
            query_stats = self.metrics.get_stats()
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
            }
        else:
            return {
                "status": "healthy",
                "version": version,
                "pool": pool_status,
                "queries": query_stats,
            }

    async def close(self) -> None:
        """Close all connections and dispose of pool."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self._initialized = False


# Singleton access function
_manager: DatabaseManager | None = None


async def get_database_manager() -> DatabaseManager:
    """Get or create the global DatabaseManager instance."""
    global _manager
    if _manager is None:
        _manager = await DatabaseManager.get_instance()
    return _manager


__all__ = ["DatabaseManager", "QueryMetrics", "get_database_manager"]
