"""Async fixtures for tests - separate file to avoid import issues."""

import os

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from tracertm.models.base import Base
from tracertm.models.item import Item

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest_asyncio.fixture(scope="function")
async def test_db_engine():
    """Create a test database engine for each test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables and cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_db_engine):
    """Create a new database session for each test function."""
    SessionLocal = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with SessionLocal() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def sample_item(db_session: AsyncSession) -> Item:
    """Create a sample item for testing."""
    from tracertm.repositories.item_repository import ItemRepository

    repo = ItemRepository(db_session)
    item = await repo.create(
        project_id="test-project",
        title="Sample Item",
        view="FEATURE",
        item_type="feature",
        description="Sample description",
        status="todo",
    )
    await db_session.commit()
    return item
