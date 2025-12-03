"""
Root pytest configuration - loads pytest-asyncio and shared test utilities
"""

# Load pytest-asyncio plugin BEFORE any other imports
pytest_plugins = ["pytest_asyncio"]

import asyncio
import os
from pathlib import Path
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

try:
    from router import TOOL_REGISTRY, ArchRouter, ToolRegistry
except ImportError:
    # Router module not available in test environment
    ArchRouter = None
    ToolRegistry = None
    TOOL_REGISTRY = None

# Import models to register them with SQLAlchemy
try:
    from tracertm.models.base import Base
except ImportError:
    Base = None


@pytest.fixture(scope="session")
async def test_db_engine():
    """Create test database engine with SQLite."""
    # Use in-memory SQLite for tests by default, or file-based if specified
    db_url = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")

    engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
    )

    # Create all tables
    if Base is not None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        if Base is not None:
            await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_db_engine):
    """Create a test database session for each test."""
    async_session_maker = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def project_factory(db_session):
    """Factory for creating test projects."""
    async def create_project(name="Test Project", description="Test project"):
        from tracertm.models.project import Project
        project = Project(name=name, description=description)
        db_session.add(project)
        await db_session.flush()
        return project
    return create_project


@pytest.fixture
def item_factory(db_session):
    """Factory for creating test items."""
    async def create_item(project_id, title="Test Item", view="FEATURE", item_type="feature", status="todo"):
        from tracertm.models.item import Item
        item = Item(
            project_id=project_id,
            title=title,
            view=view,
            item_type=item_type,
            status=status,
        )
        db_session.add(item)
        await db_session.flush()
        return item
    return create_item


@pytest.fixture
def router():
    """Create router instance"""
    return ArchRouter()


@pytest.fixture
def registry():
    """Create registry instance"""
    return ToolRegistry(TOOL_REGISTRY)


@pytest.fixture
def tool_registry_dict():
    """Get tool registry dictionary"""
    return TOOL_REGISTRY


@pytest.fixture
def sample_routes():
    """Sample routes for testing"""
    return {
        "test_route_1": {
            "description": "Test route 1",
            "tools": ["tool1", "tool2"],
        },
        "test_route_2": {
            "description": "Test route 2",
            "tools": ["tool3", "tool4"],
        },
    }
