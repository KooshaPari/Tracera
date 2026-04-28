"""SQLAlchemy session management.

Provides session factory and engine configuration for database connections.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .models import Base

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


def create_engine_from_config(
    database_url: str,
    echo: bool = False,
    pool_size: int = 5,
    max_overflow: int = 10,
) -> AsyncEngine:
    """Create SQLAlchemy async engine from configuration.

    Args:
        database_url: Database connection URL
        echo: Whether to echo SQL statements
        pool_size: Connection pool size
        max_overflow: Maximum overflow connections

    Returns:
        Configured async engine
    """
    return create_async_engine(
        database_url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create session factory from engine.

    Args:
        engine: SQLAlchemy async engine

    Returns:
        Session factory
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@asynccontextmanager
async def get_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Get database session context manager.

    Args:
        session_factory: Session factory

    Yields:
        Database session
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables(engine: AsyncEngine) -> None:
    """Create all database tables.

    Args:
        engine: SQLAlchemy async engine
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(engine: AsyncEngine) -> None:
    """Drop all database tables.

    Args:
        engine: SQLAlchemy async engine
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
