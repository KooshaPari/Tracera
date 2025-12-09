"""
Pytest configuration and fixtures
"""

import asyncio
import contextlib
import os
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Force pytest-asyncio plugin to load
pytest_plugins = ("pytest_asyncio",)

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
    # Import ALL models to ensure they're registered with Base.metadata
    # This is critical - SQLAlchemy only creates tables for imported models
    from tracertm.models.agent import Agent
    from tracertm.models.agent_event import AgentEvent
    from tracertm.models.agent_lock import AgentLock
    from tracertm.models.event import Event
    from tracertm.models.item import Item
    from tracertm.models.link import Link
    from tracertm.models.project import Project
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


@pytest_asyncio.fixture(scope="function")
async def db_session(test_db_engine):
    """
    Create a test database session for each test with proper transaction handling.

    This fixture provides a clean session for each test. Tests can call commit()
    or flush() as needed, and all changes will be automatically rolled back
    after the test completes to ensure test isolation.

    The fixture uses expire_on_commit=False to allow accessing objects after
    commit within the same test.
    """
    async_session_maker = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        try:
            yield session
        finally:
            # Always rollback to ensure test isolation
            await session.rollback()
            await session.close()


@pytest_asyncio.fixture
def project_factory(db_session):
    """
    Factory for creating test projects using ProjectRepository.

    This ensures projects are created using the same code path as production,
    providing more realistic test coverage.
    """
    async def create_project(name="Test Project", description="Test project", metadata=None):
        from tracertm.repositories.project_repository import ProjectRepository
        repo = ProjectRepository(db_session)
        project = await repo.create(name=name, description=description, metadata=metadata)
        await db_session.flush()
        return project
    return create_project


@pytest_asyncio.fixture
def item_factory(db_session):
    """
    Factory for creating test items using ItemRepository.

    This ensures items are created using the same code path as production,
    providing more realistic test coverage.
    """
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


# ============================================================
# TUI Testing Infrastructure
# ============================================================

try:
    from textual.app import App, ComposeResult
    from textual.pilot import Pilot
    from textual.widgets import Static
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False


if TEXTUAL_AVAILABLE:
    class TextualTestApp(App):
        """
        Test application for mounting widgets in isolation.

        This app provides a minimal container for testing Textual widgets
        that require an app context to initialize properly.
        """

        def __init__(self, widget=None, *args, **kwargs):
            """
            Initialize test app.

            Args:
                widget: Widget to mount in the app (optional)
            """
            super().__init__(*args, **kwargs)
            self._test_widget = widget

        def compose(self) -> ComposeResult:
            """Compose the app with the test widget if provided."""
            if self._test_widget is not None:
                yield self._test_widget
            else:
                yield Static("Test App")


@pytest_asyncio.fixture
async def textual_app():
    """
    Provides a Textual application context for widget testing.

    This fixture creates a test app and provides a pilot for interaction.

    Usage:
        async def test_widget(textual_app):
            widget = MyWidget()
            async with textual_app(widget) as pilot:
                assert widget.is_mounted
                await pilot.pause()

    Returns:
        Context manager that yields a Pilot for the test app
    """
    if not TEXTUAL_AVAILABLE:
        pytest.skip("Textual not available")

    async def _create_app_context(widget=None):
        """Create app context with widget mounted."""
        app = TextualTestApp(widget=widget)
        async with app.run_test() as pilot:
            yield pilot

    return _create_app_context


@pytest.fixture
def textual_app_context():
    """
    Enhanced Textual application context fixture for comprehensive widget testing.

    Provides both app and pilot instances for tests that need full app lifecycle control.
    Supports both async context manager and direct instantiation patterns.

    Usage:
        @pytest.mark.asyncio
        async def test_widget(textual_app_context):
            async with textual_app_context() as (app, pilot):
                widget = MyWidget()
                await app.mount(widget)
                await pilot.pause()
                assert widget.is_mounted

    Returns:
        Async context manager yielding (app, pilot) tuple
    """
    if not TEXTUAL_AVAILABLE:
        pytest.skip("Textual not available")

    @contextlib.asynccontextmanager
    async def _create_context():
        """Create app context and return (app, pilot) tuple."""
        app = TextualTestApp()
        async with app.run_test() as pilot:
            yield (app, pilot)

    return _create_context


@pytest.fixture
def mounted_widget():
    """
    Synchronous fixture for widgets that need to be in an app context.

    This is a workaround for tests that call methods requiring query_one()
    but don't actually need async interaction.

    Usage:
        def test_widget(mounted_widget):
            widget = SyncStatusWidget()
            mounted_widget(widget)  # Mounts and composes widget
            # Widget is now ready for testing

    Returns:
        Function that mounts a widget and waits for composition
    """
    if not TEXTUAL_AVAILABLE:
        pytest.skip("Textual not available")

    def _mount_widget(widget):
        """
        Mount widget in a test app synchronously.

        This simulates the widget being mounted without needing
        an async context. Useful for testing reactive attributes
        and methods that call query_one().

        Args:
            widget: Widget to mount

        Returns:
            The mounted widget
        """
        # Create a minimal app
        app = TextualTestApp(widget=widget)

        # Manually trigger compose to create child widgets
        # This allows query_one() to work without full app run
        widget._parent = app
        widget.app = app

        # Compose the widget to create its children
        children = list(widget.compose())
        for child in children:
            child._parent = widget
            child.app = app
            # If child has compose, call it too
            if hasattr(child, 'compose'):
                grandchildren = list(child.compose())
                for gc in grandchildren:
                    gc._parent = child
                    gc.app = app

        # Store children for query_one to find
        widget._nodes = children

        return widget

    return _mount_widget
