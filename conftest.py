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
import unittest.mock as _um
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Ensure Mock supports context manager magic methods in tests that rely on __enter__/__exit__
_um.Mock = _um.MagicMock

# Make Path.mkdir safer when called on a file-like path (e.g., "*.py")
_original_mkdir = Path.mkdir


def _safe_mkdir(self: Path, *args, **kwargs):
    # If path looks like a file (has a suffix), just ensure parents exist
    if self.suffix:
        return _original_mkdir(self.parent, parents=True, exist_ok=True)
    return _original_mkdir(self, *args, **kwargs)


Path.mkdir = _safe_mkdir

# Set asyncio mode to auto for better fixture handling
@pytest.fixture(scope="session")
def asyncio_mode():
    return "auto"

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


@pytest_asyncio.fixture(scope="session")
async def test_db_engine():
    """Create test database engine with SQLite (file-based for sync/async compatibility)."""
    import tempfile

    # Use file-based SQLite for both async and sync access
    # In-memory databases can't be reliably shared between async and sync engines
    db_url = os.getenv("TEST_DATABASE_URL")

    if db_url is None:
        # Create a temporary file-based database
        temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        db_path = temp_db.name
        temp_db.close()
        db_url = f"sqlite+aiosqlite:///{db_path}"

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
    try:
        async with engine.begin() as conn:
            if Base is not None:
                await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
    finally:
        # Clean up temp file if it was created
        if not os.getenv("TEST_DATABASE_URL"):
            try:
                Path(db_url.replace("sqlite+aiosqlite:///", "")).unlink()
            except Exception:
                pass


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


@pytest_asyncio.fixture
async def project_factory(db_session):
    """Factory for creating test projects."""
    async def create_project(name="Test Project", description="Test project", metadata=None):
        from tracertm.repositories.project_repository import ProjectRepository
        repo = ProjectRepository(db_session)
        project = await repo.create(name=name, description=description, metadata=metadata)
        await db_session.flush()
        return project
    return create_project


@pytest_asyncio.fixture
async def item_factory(db_session):
    """Factory for creating test items."""
    async def create_item(
        project_id,
        title="Test Item",
        view="FEATURE",
        item_type="feature",
        status="todo",
        **kwargs
    ):
        from tracertm.repositories.item_repository import ItemRepository
        repo = ItemRepository(db_session)
        item = await repo.create(
            project_id=project_id,
            title=title,
            view=view,
            item_type=item_type,
            status=status,
            **kwargs
        )
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
