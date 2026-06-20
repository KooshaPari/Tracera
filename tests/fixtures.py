from typing import Any

"""Async fixtures for tests - separate file to avoid import issues."""

import os

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

# Import ALL models to ensure they're registered with Base.metadata
# This is critical - SQLAlchemy only creates tables for imported models
from tracertm.models.base import Base
from tracertm.models.item import Item
from tracertm.models.project import Project

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
SYNC_TEST_DATABASE_URL = os.getenv("SYNC_TEST_DATABASE_URL", "sqlite:///:memory:")


@pytest_asyncio.fixture(scope="function")
async def test_db_engine() -> None:
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
async def db_session(test_db_engine: Any) -> None:
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
async def sample_project(db_session: AsyncSession) -> Project:
    """Create a sample project for testing."""
    from tracertm.repositories.project_repository import ProjectRepository

    repo = ProjectRepository(db_session)
    project = await repo.create(
        name="Test Project",
        description="Test project for fixtures",
    )
    await db_session.commit()
    return project


@pytest_asyncio.fixture
async def sample_item(db_session: AsyncSession, sample_project: Project) -> Item:
    """Create a sample item for testing.

    CRITICAL: Depends on sample_project to satisfy foreign key constraint.
    """
    from tracertm.repositories.item_repository import ItemRepository

    repo = ItemRepository(db_session)
    item = await repo.create(
        project_id=str(sample_project.id),
        title="Sample Item",
        view="FEATURE",
        item_type="feature",
        description="Sample description",
        status="todo",
    )
    await db_session.commit()
    return item


# Sync fixtures for tests that don't use async/await
@pytest.fixture
def sync_test_db_engine() -> None:
    """Create a sync test database engine for each test."""
    engine = create_engine(
        SYNC_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in SYNC_TEST_DATABASE_URL else {},
        poolclass=StaticPool if "sqlite" in SYNC_TEST_DATABASE_URL else NullPool,
        echo=False,
    )

    # Create all tables
    Base.metadata.create_all(engine)

    yield engine

    # Drop all tables and cleanup
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def sync_db_session(sync_test_db_engine: Any) -> None:
    """Create a new synchronous database session for each test function."""
    SessionLocal = sessionmaker(
        bind=sync_test_db_engine,
        class_=Session,
    )

    session = SessionLocal()
    yield session
    session.close()
