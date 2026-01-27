"""
Pytest configuration for repository tests.

Provides async session fixtures with proper SQLite async support.
"""

import asyncio
import os
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Import models to register them with SQLAlchemy
from tracertm.models.base import Base
from tracertm.models.agent import Agent
from tracertm.models.agent_event import AgentEvent
from tracertm.models.agent_lock import AgentLock
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


@pytest_asyncio.fixture(scope="function")
async def async_session_factory():
    """
    Create an async session factory for tests.

    Returns a factory function that creates new async sessions for each test.
    Manages the database lifecycle including schema creation and cleanup.
    """
    # Determine database URL
    db_url = os.getenv("TEST_DATABASE_URL")

    temp_path = None
    if db_url is None:
        # Create a temporary file-based database
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_path = temp_db.name
        temp_db.close()
        db_url = f"sqlite+aiosqlite:///{temp_path}"

    # Create engine
    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        future=True,
    )

    yield async_session

    # Cleanup
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
    finally:
        # Clean up temp file if it was created
        if temp_path:
            try:
                Path(temp_path).unlink()
            except Exception:
                pass


@pytest_asyncio.fixture(scope="function")
async def db_session(async_session_factory):
    """
    Create an async database session for a test.

    Provides a fresh session for each test with automatic rollback
    and cleanup.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
