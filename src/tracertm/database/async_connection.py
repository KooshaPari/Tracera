"""Async database connection and session management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from tracertm.core.config import get_config
from tracertm.models.base import Base

# Global engine instance
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get or create database engine."""
    global _engine
    if _engine is None:
        config = get_config()
        # Convert postgresql:// to postgresql+asyncpg://
        url = config.database.url.replace("postgresql://", "postgresql+asyncpg://")

        # SQLite doesn't support pool_size and max_overflow
        engine_kwargs: dict[str, bool | int] = {
            "pool_pre_ping": True,
            "echo": False,
        }

        # Only add pool parameters for non-SQLite databases
        if "sqlite" not in url.lower():
            engine_kwargs.update({
                "pool_size": config.database.pool_size,
                "max_overflow": config.database.max_overflow,
                "pool_timeout": config.database.pool_timeout,
                "pool_recycle": config.database.pool_recycle,
            })

        _engine = create_async_engine(url, **engine_kwargs)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create session factory."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session context manager."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database (create all tables)."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Drop all database tables (for testing)."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
