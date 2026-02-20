"""Async database adapter for MCP tools.

Provides shared connection pool with FastAPI and RLS context management.
This replaces the separate MCP database manager with a unified async engine.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from tracertm.config.manager import ConfigManager
from tracertm.core.context import current_user_id

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# Singleton async engine (shared with FastAPI)
_async_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker | None = None
_engine_lock = asyncio.Lock()


async def get_async_engine() -> AsyncEngine:
    """Get or create the shared async database engine.

    This engine is shared between MCP tools and FastAPI routes,
    ensuring a single connection pool for optimal resource usage.

    Returns:
        AsyncEngine: Shared async SQLAlchemy engine

    Raises:
        ValueError: If database_url is not configured
    """
    global _async_engine, _async_session_factory

    if _async_engine is not None:
        return _async_engine

    async with _engine_lock:
        # Double-check after acquiring lock
        if _async_engine is not None:
            return _async_engine

        config_manager = ConfigManager()
        database_url = config_manager.get("database_url")

        if not database_url:
            # Fall back to local SQLite for development
            base_dir = Path.home() / ".tracertm"
            base_dir.mkdir(parents=True, exist_ok=True)
            database_url = f"sqlite:///{base_dir / 'tracertm.db'}"

        # Ensure database_url is a string
        if not isinstance(database_url, str):
            database_url = str(database_url)

        # Convert to async URL
        async_database_url = _convert_to_async_url(database_url)

        # Create async engine with optimized pool settings
        _async_engine = create_async_engine(
            async_database_url,
            echo=False,
            pool_size=20,  # Base pool size (shared with FastAPI)
            max_overflow=30,  # Additional connections under load
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,  # Recycle after 1 hour
        )

        # Create session factory
        _async_session_factory = async_sessionmaker(
            _async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

        # Test connection
        async with _async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        return _async_engine


def _convert_to_async_url(database_url: str) -> str:
    """Convert sync database URL to async driver URL.

    Args:
        database_url: Sync database URL (postgresql:// or sqlite://)

    Returns:
        Async database URL with appropriate driver
    """
    if database_url.startswith("sqlite:///"):
        return database_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    if database_url.startswith("sqlite://"):
        return database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if database_url.startswith("postgresql://"):
        # Remove query parameters that asyncpg doesn't support
        base_url = database_url.split("?", maxsplit=1)[0]
        return base_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return database_url


@asynccontextmanager
async def get_mcp_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session with RLS context for MCP tools.

    This session:
    - Shares the connection pool with FastAPI
    - Sets RLS context (app.current_user_id) if user is authenticated
    - Automatically commits/rollbacks transactions
    - Properly closes connections back to the pool

    Usage:
        async with get_mcp_session() as session:
            result = await session.execute(query)

    Yields:
        AsyncSession: Database session with RLS context set

    Raises:
        RuntimeError: If engine is not initialized
    """
    if _async_session_factory is None:
        # Initialize engine if not already done
        await get_async_engine()

    if _async_session_factory is None:
        msg = "Failed to initialize async session factory"
        raise RuntimeError(msg)

    async with _async_session_factory() as session:
        try:
            # Set RLS context if user is authenticated
            user_id = current_user_id.get()
            if user_id:
                config_manager = ConfigManager()
                database_url: str = str(config_manager.get("database_url") or "")

                # Only set RLS for PostgreSQL
                if database_url and "postgres" in database_url:
                    await session.execute(
                        text("SELECT set_config('app.current_user_id', :user_id, false)"),
                        {"user_id": user_id},
                    )

            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def reset_engine() -> None:
    """Reset the async engine (for testing purposes).

    This should only be called in test teardown or when reconfiguring
    the database connection.
    """
    global _async_engine, _async_session_factory

    if _async_engine is not None:
        await _async_engine.dispose()
        _async_engine = None
        _async_session_factory = None


async def get_pool_status() -> dict[str, object]:
    """Get current connection pool status.

    Returns:
        Dictionary with pool metrics:
        - size: Total pool size
        - checked_out: Connections currently in use
        - overflow: Connections beyond pool_size
        - checked_in: Available connections
    """
    await asyncio.sleep(0)
    if _async_engine is None:
        return {"status": "not_initialized"}

    pool = _async_engine.pool
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


__all__ = [
    "get_async_engine",
    "get_mcp_session",
    "get_pool_status",
    "reset_engine",
]
