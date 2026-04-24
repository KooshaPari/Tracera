"""Root pytest configuration - loads pytest-asyncio and shared test utilities.

pytest_plugins must be assigned before any other imports so pytest discovers
the plugin before collection begins.
"""

import asyncio
import os
import unittest.mock as _um
from pathlib import Path
from typing import Any

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

pytest_plugins = ["pytest_asyncio"]

# Disable problematic Pydantic plugins during tests
os.environ.setdefault("PYDANTIC_DISABLE_PLUGINS", "logfire-plugin")

# Ensure Mock supports context manager magic methods in tests that rely on __enter__/__exit__
_um.Mock = _um.MagicMock  # type: ignore[assignment]

# Make Path.mkdir safer when called on a file-like path (e.g., "*.py")
_original_mkdir = Path.mkdir


def _safe_mkdir(self: Path, *args: Any, **kwargs: Any) -> None:
    # If path looks like a file (has a suffix), just ensure parents exist
    if self.suffix:
        return _original_mkdir(self.parent, parents=True, exist_ok=True)
    return _original_mkdir(self, *args, **kwargs)


Path.mkdir = _safe_mkdir  # type: ignore[assignment]


# Set asyncio mode to auto for better fixture handling
@pytest.fixture(scope="session")
def asyncio_mode() -> str:
    return "auto"


try:
    from router import TOOL_REGISTRY, ArchRouter, ToolRegistry  # type: ignore[import-untyped,unresolved-import]
except ImportError:
    # Router module not available in test environment
    ArchRouter = None  # type: ignore[assignment,misc]
    ToolRegistry = None  # type: ignore[assignment,misc]
    TOOL_REGISTRY = None  # type: ignore[assignment,misc]

# Import models to register them with SQLAlchemy
try:
    from tracertm.models.base import Base
except ImportError:
    Base = None  # type: ignore[assignment,misc]


@pytest.fixture(scope="session")
def sync_engine() -> None:
    """Shared synchronous SQLite engine."""
    import tempfile

    db_url = os.getenv("TEST_SYNC_DATABASE_URL")
    if db_url is None:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            db_path = temp_db.name
        db_url = f"sqlite:///{db_path}"

    from sqlalchemy import create_engine

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    if Base is not None:
        Base.metadata.create_all(engine)
    yield engine
    try:
        if Base is not None:
            Base.metadata.drop_all(engine)
        engine.dispose()
    finally:
        if not os.getenv("TEST_SYNC_DATABASE_URL"):
            try:
                Path(db_url.replace("sqlite:///", "")).unlink()
            except Exception as e:
                __import__("logging").getLogger(__name__).debug("unlink temp db: %s", e)


@pytest.fixture
def db_session(sync_engine: Any) -> None:
    """Synchronous SQLAlchemy session."""
    from sqlalchemy.orm import sessionmaker

    session_local = sessionmaker(bind=sync_engine)
    session = session_local()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest_asyncio.fixture(scope="session")
async def async_db_engine() -> None:
    """Async engine for async-specific tests."""
    import tempfile

    db_url = os.getenv("TEST_DATABASE_URL")
    if db_url is None:
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
            db_path = temp_db.name
        db_url = f"sqlite+aiosqlite:///{db_path}"

    engine = create_async_engine(db_url, echo=False, future=True)
    if Base is not None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield engine
    try:
        async with engine.begin() as conn:
            if Base is not None:
                await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()
    finally:
        if not os.getenv("TEST_DATABASE_URL"):
            try:
                db_path = Path(db_url.replace("sqlite+aiosqlite:///", ""))
                if db_path.is_file():
                    await asyncio.to_thread(db_path.unlink)
            except Exception as e:
                __import__("logging").getLogger(__name__).debug("unlink temp db: %s", e)


@pytest_asyncio.fixture
async def async_db_session(async_db_engine: Any) -> None:
    """Async SQLAlchemy session."""
    async_session_maker = async_sessionmaker(async_db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
def project_factory(db_session: Any) -> None:
    """Factory for creating test projects."""

    async def create_project(
        name: Any = "Test Project", description: Any = "Test project", metadata: Any = None
    ) -> None:
        from tracertm.repositories.project_repository import ProjectRepository

        repo = ProjectRepository(db_session)
        project = await repo.create(name=name, description=description, metadata=metadata)
        await db_session.flush()
        return project

    return create_project


@pytest_asyncio.fixture
def item_factory(db_session: Any) -> None:
    """Factory for creating test items."""

    async def create_item(
        project_id: Any,
        title: Any = "Test Item",
        view: Any = "FEATURE",
        item_type: Any = "feature",
        status: Any = "todo",
        **kwargs: Any,
    ) -> None:
        from tracertm.repositories.item_repository import ItemRepository

        repo = ItemRepository(db_session)
        item = await repo.create(
            project_id=project_id,
            title=title,
            view=view,
            item_type=item_type,
            status=status,
            **kwargs,
        )
        await db_session.flush()
        return item

    return create_item


@pytest.fixture
def router() -> None:
    """Create router instance."""
    router_cls = ArchRouter
    if router_cls is not None:
        return router_cls()
    pytest.skip("router module not available")


@pytest.fixture
def registry() -> None:
    """Create registry instance."""
    if ToolRegistry is not None and TOOL_REGISTRY is not None:
        return ToolRegistry(TOOL_REGISTRY)
    pytest.skip("router module not available")


@pytest.fixture
def tool_registry_dict() -> None:
    """Get tool registry dictionary."""
    return TOOL_REGISTRY


@pytest.fixture
def sample_routes() -> None:
    """Sample routes for testing."""
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
