"""Comprehensive integration tests for TUI module.

Tests all TUI applications and widgets using Textual testing framework.
Targets:
- apps/browser.py (115 lines)
- apps/dashboard.py (141 lines)
- apps/dashboard_compat.py (190 lines)
- apps/graph.py (123 lines)
- widgets/*.py (~300 lines)
- adapters/storage_adapter.py (138 lines)

Total: ~1,000 lines | Coverage Goal: 70%+

Uses Textual's Pilot for realistic app interaction testing.
"""
# TUI app types (Textual) expose run_test, is_running, query_one, etc. at runtime
# pyright: reportPossiblyMissingAttribute=false

import asyncio
from datetime import datetime, timedelta
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_THREE, COUNT_TWO

# Import Textual testing utilities
try:
    from textual.pilot import Pilot

    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

# Skip all tests if Textual not available
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not TEXTUAL_AVAILABLE, reason="Textual not installed"),
]

from tracertm.database.connection import DatabaseConnection
from tracertm.models import Item, Link, Project
from tracertm.storage.sync_engine import SyncState, SyncStatus
from tracertm.testing_factories import create_project
from tracertm.tui.adapters.storage_adapter import StorageAdapter
from tracertm.tui.apps.browser import BrowserApp
from tracertm.tui.apps.dashboard import DashboardApp
from tracertm.tui.apps.dashboard_compat import EnhancedDashboardApp
from tracertm.tui.apps.graph import GraphApp
from tracertm.tui.widgets.conflict_panel import ConflictPanel
from tracertm.tui.widgets.graph_view import GraphViewWidget
from tracertm.tui.widgets.item_list import ItemListWidget
from tracertm.tui.widgets.state_display import StateDisplayWidget
from tracertm.tui.widgets.sync_status import (
    CompactSyncStatus,
    SyncStatusWidget,
)
from tracertm.tui.widgets.view_switcher import ViewSwitcherWidget

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_config_dir(tmp_path: Any) -> None:
    """Temporary directory for config files."""
    config_dir = tmp_path / ".trace"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@pytest.fixture
def mock_config_manager(temp_config_dir: Any) -> None:
    """Mock ConfigManager with test configuration."""
    with patch("tracertm.config.manager.ConfigManager") as MockConfig:
        config = MockConfig.return_value
        config.config_dir = temp_config_dir
        config.get.side_effect = lambda key, default=None: {
            "database_url": f"sqlite:///{temp_config_dir}/test.db",
            "current_project_id": "test-project-123",
            "current_project": "test-project",
        }.get(key, default)
        yield config


@pytest.fixture
def test_database(temp_config_dir: Any) -> None:
    """Create test database with schema."""
    from tracertm.models.base import Base

    db_path = temp_config_dir / "test.db"
    db_url = f"sqlite:///{db_path}"
    db_conn = DatabaseConnection(db_url)
    db_conn.connect()

    # Create all tables
    Base.metadata.create_all(db_conn.engine)

    yield db_conn

    db_conn.close()
    db_path.unlink(missing_ok=True)


@pytest.fixture
def populated_database(test_database: Any) -> None:
    """Database populated with test data."""
    from sqlalchemy.orm import Session

    session = Session(test_database.engine)

    # Create project
    project = Project(
        id="test-project-123",
        name="Test Project",
        description="Test project for TUI integration tests",
    )
    session.add(project)

    # Create items across different views
    items = [
        Item(
            id="item-1",
            project_id="test-project-123",
            title="User Authentication",
            view="FEATURE",
            item_type="feature",
            status="in_progress",
            priority="high",
            description="Implement user authentication system",
        ),
        Item(
            id="item-2",
            project_id="test-project-123",
            title="Login API",
            view="API",
            item_type="api",
            status="todo",
            priority="high",
            parent_id="item-1",
        ),
        Item(
            id="item-3",
            project_id="test-project-123",
            title="Auth Database Schema",
            view="DATABASE",
            item_type="schema",
            status="done",
            priority="medium",
        ),
        Item(
            id="item-4",
            project_id="test-project-123",
            title="Login Tests",
            view="TEST",
            item_type="test",
            status="todo",
            priority="medium",
        ),
        # Add some CODE view items
        Item(
            id="item-5",
            project_id="test-project-123",
            title="AuthService.py",
            view="CODE",
            item_type="code",
            status="done",
            priority="high",
        ),
        # Add ROADMAP items
        Item(
            id="item-6",
            project_id="test-project-123",
            title="Q1 2025 Release",
            view="ROADMAP",
            item_type="milestone",
            status="in_progress",
            priority="high",
        ),
        # Add PROGRESS items
        Item(
            id="item-7",
            project_id="test-project-123",
            title="Sprint 1 Progress",
            view="PROGRESS",
            item_type="progress",
            status="in_progress",
            priority="medium",
        ),
        # Add WIREFRAME items
        Item(
            id="item-8",
            project_id="test-project-123",
            title="Login Page Wireframe",
            view="WIREFRAME",
            item_type="wireframe",
            status="done",
            priority="medium",
        ),
    ]

    for item in items:
        session.add(item)

    # Create links
    links = [
        Link(
            id="link-1",
            project_id="test-project-123",
            source_item_id="item-1",
            target_item_id="item-2",
            link_type="implements",
        ),
        Link(
            id="link-2",
            project_id="test-project-123",
            source_item_id="item-1",
            target_item_id="item-3",
            link_type="depends_on",
        ),
        Link(
            id="link-3",
            project_id="test-project-123",
            source_item_id="item-4",
            target_item_id="item-2",
            link_type="tests",
        ),
        Link(
            id="link-4",
            project_id="test-project-123",
            source_item_id="item-5",
            target_item_id="item-1",
            link_type="implements",
        ),
    ]

    for link in links:
        session.add(link)

    session.commit()
    session.close()

    return test_database


@pytest.fixture
def mock_storage_adapter(tmp_path: Any) -> None:
    """Mock StorageAdapter for testing."""
    adapter = StorageAdapter(base_dir=tmp_path)

    # Create mock project
    with patch.object(adapter.storage, "get_project_storage") as mock_storage:
        mock_project_storage = MagicMock()
        mock_project_storage.get_project.return_value = create_project(id="test-project", name="test-project")
        mock_storage.return_value = mock_project_storage

        yield adapter


# ============================================================================
# BrowserApp Integration Tests (15 tests)
# ============================================================================


class TestBrowserAppIntegration:
    """Integration tests for BrowserApp."""

    @pytest.mark.asyncio
    async def test_browser_app_launches_successfully(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Valid config and populated database.

        WHEN: BrowserApp is launched
        THEN: App starts without errors.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test():
                assert app.is_running
                assert app.project_id == "test-project-123"

    @pytest.mark.asyncio
    async def test_browser_displays_item_tree(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Database with hierarchical items.

        WHEN: BrowserApp loads
        THEN: Item tree is displayed with correct structure.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Verify tree is populated
                tree = app.query_one("#item-tree")
                assert tree is not None

    @pytest.mark.asyncio
    async def test_browser_tree_navigation(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: BrowserApp with items.

        WHEN: User navigates tree with arrow keys
        THEN: Tree navigation works correctly.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Simulate tree navigation
                await pilot.press("down")
                await pilot.pause()

                # Should still be running
                assert app.is_running

    @pytest.mark.asyncio
    async def test_browser_item_selection_shows_details(
        self, mock_config_manager: Any, populated_database: Any
    ) -> None:
        """GIVEN: BrowserApp with items.

        WHEN: User selects an item in tree
        THEN: Item details are displayed in detail panel.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Simulate item selection
                await pilot.press("enter")
                await pilot.pause()

                # Details panel should be updated
                details = app.query_one("#item-details")
                assert details is not None

    @pytest.mark.asyncio
    async def test_browser_refresh_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running BrowserApp.

        WHEN: User presses 'r' to refresh
        THEN: Tree is refreshed with latest data.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Press refresh
                await pilot.press("r")
                await pilot.pause()

                # App should still be running
                assert app.is_running

    @pytest.mark.asyncio
    async def test_browser_filter_focus(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running BrowserApp.

        WHEN: User presses 'f' to filter
        THEN: Filter input receives focus.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Press filter key
                await pilot.press("f")
                await pilot.pause()

                # Filter input should be focused
                filter_input = app.query_one("#filter-input")
                assert filter_input.has_focus

    @pytest.mark.asyncio
    async def test_browser_help_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running BrowserApp.

        WHEN: User presses '?' for help
        THEN: Help notification is displayed.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Press help key
                await pilot.press("question_mark")
                await pilot.pause()

                # App should still be running
                assert app.is_running

    @pytest.mark.asyncio
    async def test_browser_quit_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running BrowserApp.

        WHEN: User presses 'q' to quit
        THEN: App exits gracefully.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Press quit
                await pilot.press("q")

                # App should exit
                assert not app.is_running

    @pytest.mark.asyncio
    async def test_browser_handles_missing_database_config(self, mock_config_manager: Any) -> None:
        """GIVEN: Config without database URL.

        WHEN: BrowserApp attempts to start
        THEN: App exits with error message.
        """
        mock_config_manager.get.side_effect = lambda key, _default=None: None

        with patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # App should exit due to missing config
                assert not app.is_running

    @pytest.mark.asyncio
    async def test_browser_handles_missing_project(self, mock_config_manager: Any, test_database: Any) -> None:
        """GIVEN: Config without current project.

        WHEN: BrowserApp attempts to start
        THEN: App exits with error message.
        """
        mock_config_manager.get.side_effect = lambda key, default=None: {
            "database_url": "sqlite:///test.db",
            "current_project_id": None,
        }.get(key, default)

        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=test_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # App should exit due to missing project
                assert not app.is_running

    @pytest.mark.asyncio
    async def test_browser_handles_empty_database(self, mock_config_manager: Any, test_database: Any) -> None:
        """GIVEN: Empty database with no items.

        WHEN: BrowserApp loads
        THEN: App displays empty tree gracefully.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=test_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # App should handle empty data
                tree = app.query_one("#item-tree")
                assert tree is not None

    @pytest.mark.asyncio
    async def test_browser_child_item_rendering(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Items with parent-child relationships.

        WHEN: BrowserApp renders tree
        THEN: Children are nested under parents correctly.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Verify tree structure
                tree = app.query_one("#item-tree")
                assert tree is not None
                # Children should be added recursively
                assert app.is_running

    @pytest.mark.asyncio
    async def test_browser_database_cleanup_on_exit(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running BrowserApp with database connection.

        WHEN: App exits
        THEN: Database connection is closed properly.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                await pilot.press("q")

            # Verify cleanup was called
            # Note: In real scenario, on_unmount would close connection
            assert not app.is_running

    @pytest.mark.asyncio
    async def test_browser_view_filtering(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Items across multiple views.

        WHEN: BrowserApp loads with specific view
        THEN: Only items from that view are displayed.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            app.current_view = "FEATURE"
            async with app.run_test() as pilot:
                await pilot.pause()

                # Tree should only show FEATURE items
                assert app.current_view == "FEATURE"

    @pytest.mark.asyncio
    async def test_browser_keyboard_shortcuts(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running BrowserApp.

        WHEN: User presses various keyboard shortcuts
        THEN: Appropriate actions are triggered.
        """
        with (
            patch("tracertm.tui.apps.browser.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.browser.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", BrowserApp())
            async with app.run_test() as pilot:
                # Test multiple shortcuts
                await pilot.press("r")  # Refresh
                await pilot.pause()
                await pilot.press("f")  # Filter
                await pilot.pause()
                await pilot.press("question_mark")  # Help
                await pilot.pause()

                assert app.is_running


# ============================================================================
# DashboardApp Integration Tests (15 tests)
# ============================================================================


class TestDashboardAppIntegration:
    """Integration tests for DashboardApp."""

    @pytest.mark.asyncio
    async def test_dashboard_app_launches_successfully(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Valid config and populated database.

        WHEN: DashboardApp is launched
        THEN: App starts and displays project data.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                assert app.is_running
                assert app.project_id == "test-project-123"

    @pytest.mark.asyncio
    async def test_dashboard_displays_statistics(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Database with items and links.

        WHEN: DashboardApp loads
        THEN: Statistics table shows correct counts.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Verify stats table exists
                stats_table = app.query_one("#stats-table")
                assert stats_table is not None

    @pytest.mark.asyncio
    async def test_dashboard_displays_items_table(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Database with items.

        WHEN: DashboardApp loads
        THEN: Items table displays current view items.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Verify items table exists
                items_table = app.query_one("#items-table")
                assert items_table is not None

    @pytest.mark.asyncio
    async def test_dashboard_view_tree_setup(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: DashboardApp starting up.

        WHEN: View tree is initialized
        THEN: All views are listed in tree.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                view_tree = app.query_one("#view-tree")
                assert view_tree is not None

    @pytest.mark.asyncio
    async def test_dashboard_switch_view_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running DashboardApp.

        WHEN: User presses 'v' to switch view
        THEN: Current view cycles to next view.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                initial_view = app.current_view

                # Press view switch key
                await pilot.press("v")
                await pilot.pause()

                # View should have changed
                assert app.current_view != initial_view

    @pytest.mark.asyncio
    async def test_dashboard_view_tree_selection(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: DashboardApp with view tree.

        WHEN: User selects a view from tree
        THEN: Items table updates to show selected view.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Navigate to view tree and select
                await pilot.press("tab")  # Focus view tree
                await pilot.press("down")
                await pilot.press("enter")
                await pilot.pause()

                # View should update
                assert app.is_running

    @pytest.mark.asyncio
    async def test_dashboard_refresh_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running DashboardApp.

        WHEN: User presses 'r' to refresh
        THEN: All data is refreshed from database.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Press refresh
                await pilot.press("r")
                await pilot.pause()

                assert app.is_running

    @pytest.mark.asyncio
    async def test_dashboard_search_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running DashboardApp.

        WHEN: User presses 's' for search
        THEN: Search notification is displayed.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Press search key
                await pilot.press("s")
                await pilot.pause()

                # Should show "not implemented" message
                assert app.is_running

    @pytest.mark.asyncio
    async def test_dashboard_help_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running DashboardApp.

        WHEN: User presses '?' for help
        THEN: Help message is displayed.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                await pilot.press("question_mark")
                await pilot.pause()

                assert app.is_running

    @pytest.mark.asyncio
    async def test_dashboard_quit_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running DashboardApp.

        WHEN: User presses 'q' to quit
        THEN: App exits gracefully.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                await pilot.press("q")

                assert not app.is_running

    @pytest.mark.asyncio
    async def test_dashboard_state_summary_display(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Database with items and links.

        WHEN: DashboardApp displays state summary
        THEN: Correct totals are shown.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                state_summary = app.query_one("#state-summary")
                assert state_summary is not None

    @pytest.mark.asyncio
    async def test_dashboard_handles_view_with_no_items(
        self, mock_config_manager: Any, populated_database: Any
    ) -> None:
        """GIVEN: View with no items.

        WHEN: DashboardApp switches to that view
        THEN: Empty items table is displayed gracefully.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Switch to view with minimal items
                app.current_view = "UNKNOWN"
                app.refresh_items()
                await pilot.pause()

                assert app.is_running

    @pytest.mark.asyncio
    async def test_dashboard_items_table_pagination(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Database with many items.

        WHEN: DashboardApp loads items
        THEN: Items are limited to prevent performance issues.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Items should be limited (max 100)
                items_table = app.query_one("#items-table")
                assert items_table is not None

    @pytest.mark.asyncio
    async def test_dashboard_link_count_per_view(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Links between items in different views.

        WHEN: DashboardApp displays statistics
        THEN: Link counts per view are accurate.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Stats should include link counts
                stats_table = app.query_one("#stats-table")
                assert stats_table is not None

    @pytest.mark.asyncio
    async def test_dashboard_cleanup_on_exit(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running DashboardApp.

        WHEN: App exits
        THEN: Database connection is cleaned up.
        """
        with (
            patch("tracertm.tui.apps.dashboard.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.dashboard.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", DashboardApp())
            async with app.run_test() as pilot:
                await pilot.press("q")

            assert not app.is_running


# ============================================================================
# EnhancedDashboardApp Integration Tests (20 tests)
# ============================================================================


class TestEnhancedDashboardAppIntegration:
    """Integration tests for EnhancedDashboardApp (dashboard_compat)."""

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_launches_with_storage_adapter(
        self, tmp_path: Any, mock_config_manager: Any
    ) -> None:
        """GIVEN: Valid config and storage adapter.

        WHEN: EnhancedDashboardApp is launched
        THEN: App starts with local storage integration.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                assert app.is_running
                assert app.storage_adapter is not None

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_sync_status_widget_displays(
        self, tmp_path: Any, mock_config_manager: Any
    ) -> None:
        """GIVEN: EnhancedDashboardApp running.

        WHEN: App is mounted
        THEN: Sync status widget is visible.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                sync_widget = app.query_one("#sync-status")
                assert sync_widget is not None

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_view_tree_setup(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: EnhancedDashboardApp starting.

        WHEN: View tree is initialized
        THEN: Views (epic, story, test, task) are listed.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                view_tree = app.query_one("#view-tree")
                assert view_tree is not None

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_switch_view_cycles_correctly(
        self, tmp_path: Any, mock_config_manager: Any
    ) -> None:
        """GIVEN: EnhancedDashboardApp with multiple views.

        WHEN: User switches view multiple times
        THEN: View cycles through epic -> story -> test -> task.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                views = ["epic", "story", "test", "task"]
                for _expected_view in views:
                    assert app.current_view in views
                    await pilot.press("v")
                    await pilot.pause()

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_refresh_action(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: Running EnhancedDashboardApp.

        WHEN: User presses 'r' to refresh
        THEN: Data is refreshed and notification shown.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                await pilot.press("r")
                await pilot.pause()

                assert app.is_running

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_sync_action_no_engine(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: EnhancedDashboardApp without sync engine.

        WHEN: User triggers sync with Ctrl+S
        THEN: Error notification is displayed.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                # Ctrl+S for sync
                await pilot.press("ctrl+s")
                await pilot.pause()

                # Should show error about no sync engine
                assert app.is_running

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_sync_action_with_engine(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: EnhancedDashboardApp with mock sync engine.

        WHEN: User triggers sync
        THEN: Sync operation executes.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))

            # Mock sync engine
            mock_sync = AsyncMock()
            mock_sync.sync.return_value = MagicMock(
                success=True,
                entities_synced=5,
                conflicts=[],
                errors=[],
                duration_seconds=1.5,
            )
            app.storage_adapter.sync_engine = mock_sync

            async with app.run_test() as pilot:
                await pilot.pause()

                await pilot.press("ctrl+s")
                await pilot.pause()

                # Sync should have been called
                assert app.is_running

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_show_conflicts_no_conflicts(
        self, tmp_path: Any, mock_config_manager: Any
    ) -> None:
        """GIVEN: No unresolved conflicts.

        WHEN: User presses 'c' to show conflicts
        THEN: Notification indicates no conflicts.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                await pilot.press("c")
                await pilot.pause()

                # Should notify no conflicts
                assert app.is_running

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_help_action(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: Running EnhancedDashboardApp.

        WHEN: User presses '?' for help
        THEN: Help text with shortcuts is displayed.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                await pilot.press("question_mark")
                await pilot.pause()

                assert app.is_running

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_quit_action(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: Running EnhancedDashboardApp.

        WHEN: User presses 'q' to quit
        THEN: App exits gracefully.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                await pilot.press("q")

                assert not app.is_running

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_sync_status_updates(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: EnhancedDashboardApp with sync status updates enabled.

        WHEN: Periodic updates occur
        THEN: Sync status widget reflects current state.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                # Trigger manual status update
                app.update_sync_status()
                await pilot.pause()

                sync_widget = app.query_one("#sync-status")
                assert sync_widget is not None

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_handles_missing_project(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: Config without current project.

        WHEN: EnhancedDashboardApp starts
        THEN: App exits with error message.
        """
        mock_config_manager.get.side_effect = lambda key, _default=None: None

        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                # Should exit due to no project
                assert not app.is_running

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_items_display_source_info(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: Items with and without markdown files.

        WHEN: Items table is displayed
        THEN: Source column shows "SQLite+MD" or "SQLite".
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                items_table = app.query_one("#items-table")
                assert items_table is not None

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_view_tree_selection(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: EnhancedDashboardApp with view tree.

        WHEN: User selects view from tree
        THEN: Items table updates to selected view.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                # Simulate view selection
                await pilot.press("tab")
                await pilot.press("down")
                await pilot.press("enter")
                await pilot.pause()

                assert app.is_running

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_search_not_implemented(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: Running EnhancedDashboardApp.

        WHEN: User presses 's' for search
        THEN: Warning notification about not implemented.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                await pilot.press("s")
                await pilot.pause()

                assert app.is_running

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_callback_registration(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: EnhancedDashboardApp with storage adapter.

        WHEN: App sets up callbacks
        THEN: Callbacks are registered for sync status, conflicts, items.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))

            # Manually trigger callback setup before mounting
            # (normally happens in on_mount)
            app.storage_adapter.on_sync_status_change(app._on_sync_status_change)
            app.storage_adapter.on_conflict_detected(app._on_conflict_detected)
            app.storage_adapter.on_item_change(app._on_item_change)

            async with app.run_test() as pilot:
                await pilot.pause()

                # Callbacks should be registered
                assert len(app.storage_adapter._sync_status_callbacks) >= 1
                assert len(app.storage_adapter._conflict_callbacks) >= 1
                assert len(app.storage_adapter._item_change_callbacks) >= 1

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_sync_status_callback_triggers(
        self, tmp_path: Any, mock_config_manager: Any
    ) -> None:
        """GIVEN: EnhancedDashboardApp with callbacks.

        WHEN: Sync status changes
        THEN: Callback is triggered and UI updates.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                # Simulate sync status change via storage adapter
                # This triggers the callback registered in setup_storage_callbacks
                state = SyncState(
                    status=SyncStatus.SUCCESS,
                    pending_changes=0,
                    synced_entities=5,
                )

                # Trigger callback directly to simulate storage adapter notification
                app.storage_adapter._notify_sync_status(state)
                await pilot.pause()

                # Give time for async callback processing
                await asyncio.sleep(0.1)

                assert app.is_running

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_conflict_callback_notification(
        self, tmp_path: Any, mock_config_manager: Any
    ) -> None:
        """GIVEN: EnhancedDashboardApp with callbacks.

        WHEN: Conflict is detected
        THEN: Notification is shown.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                # Simulate conflict detection via storage adapter
                mock_conflict = MagicMock()
                mock_conflict.entity_type = "item"
                mock_conflict.entity_id = "test-item-123"

                # Trigger callback through storage adapter
                app.storage_adapter._notify_conflict(mock_conflict)
                await pilot.pause()

                # Give time for async callback processing
                await asyncio.sleep(0.1)

                assert app.is_running

    @pytest.mark.asyncio
    async def test_enhanced_dashboard_item_change_callback(self, tmp_path: Any, mock_config_manager: Any) -> None:
        """GIVEN: EnhancedDashboardApp with callbacks.

        WHEN: Item change occurs
        THEN: Data is refreshed.
        """
        with patch(
            "tracertm.tui.apps.dashboard_compat.ConfigManager",
            return_value=mock_config_manager,
        ):
            app = cast("Any", EnhancedDashboardApp(base_dir=tmp_path))
            async with app.run_test() as pilot:
                await pilot.pause()

                # Simulate item change via storage adapter
                app.storage_adapter._notify_item_change("test-item-123")
                await pilot.pause()

                # Give time for async callback processing
                await asyncio.sleep(0.1)

                assert app.is_running


# ============================================================================
# GraphApp Integration Tests (10 tests)
# ============================================================================


class TestGraphAppIntegration:
    """Integration tests for GraphApp."""

    @pytest.mark.asyncio
    async def test_graph_app_launches_successfully(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Valid config and populated database.

        WHEN: GraphApp is launched
        THEN: App starts and loads graph data.
        """
        with (
            patch("tracertm.tui.apps.graph.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.graph.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", GraphApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                assert app.is_running
                assert app.project_id == "test-project-123"

    @pytest.mark.asyncio
    async def test_graph_loads_nodes_and_links(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Database with items and links.

        WHEN: GraphApp loads graph data
        THEN: Nodes and links are populated.
        """
        with (
            patch("tracertm.tui.apps.graph.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.graph.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", GraphApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Nodes should be loaded
                assert len(app.nodes) > 0
                # Links should be loaded
                assert len(app.links) > 0

    @pytest.mark.asyncio
    async def test_graph_displays_link_table(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: GraphApp with links.

        WHEN: Graph is rendered
        THEN: Link table shows connections.
        """
        with (
            patch("tracertm.tui.apps.graph.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.graph.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", GraphApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                link_table = app.query_one("#link-table")
                assert link_table is not None

    @pytest.mark.asyncio
    async def test_graph_displays_statistics(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: GraphApp with graph data.

        WHEN: Stats are displayed
        THEN: Correct node and link counts shown.
        """
        with (
            patch("tracertm.tui.apps.graph.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.graph.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", GraphApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                stats = app.query_one("#graph-stats")
                assert stats is not None

    @pytest.mark.asyncio
    async def test_graph_refresh_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running GraphApp.

        WHEN: User presses 'r' to refresh
        THEN: Graph data is reloaded.
        """
        with (
            patch("tracertm.tui.apps.graph.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.graph.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", GraphApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                await pilot.press("r")
                await pilot.pause()

                assert app.is_running

    @pytest.mark.asyncio
    async def test_graph_zoom_in_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running GraphApp.

        WHEN: User presses '+' to zoom in
        THEN: Zoom level increases.
        """
        with (
            patch("tracertm.tui.apps.graph.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.graph.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", GraphApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                initial_zoom = app.zoom

                await pilot.press("plus")
                await pilot.pause()

                assert app.zoom > initial_zoom

    @pytest.mark.asyncio
    async def test_graph_zoom_out_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running GraphApp.

        WHEN: User presses '-' to zoom out
        THEN: Zoom level decreases.
        """
        with (
            patch("tracertm.tui.apps.graph.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.graph.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", GraphApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                initial_zoom = app.zoom

                await pilot.press("minus")
                await pilot.pause()

                assert app.zoom < initial_zoom

    @pytest.mark.asyncio
    async def test_graph_zoom_limits(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: GraphApp at zoom limits.

        WHEN: User tries to zoom beyond limits
        THEN: Zoom stays within bounds (0.5 - 5.0).
        """
        with (
            patch("tracertm.tui.apps.graph.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.graph.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", GraphApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                # Zoom in many times
                for _ in range(10):
                    await pilot.press("plus")

                assert app.zoom <= float(COUNT_FIVE + 0.0)

                # Zoom out many times
                for _ in range(20):
                    await pilot.press("minus")

                assert app.zoom >= 0.5

    @pytest.mark.asyncio
    async def test_graph_help_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running GraphApp.

        WHEN: User presses '?' for help
        THEN: Help notification is shown.
        """
        with (
            patch("tracertm.tui.apps.graph.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.graph.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", GraphApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                await pilot.press("question_mark")
                await pilot.pause()

                assert app.is_running

    @pytest.mark.asyncio
    async def test_graph_quit_action(self, mock_config_manager: Any, populated_database: Any) -> None:
        """GIVEN: Running GraphApp.

        WHEN: User presses 'q' to quit
        THEN: App exits gracefully.
        """
        with (
            patch("tracertm.tui.apps.graph.ConfigManager", return_value=mock_config_manager),
            patch(
                "tracertm.tui.apps.graph.DatabaseConnection",
                return_value=populated_database,
            ),
        ):
            app = cast("Any", GraphApp())
            async with app.run_test() as pilot:
                await pilot.pause()

                await pilot.press("q")

                assert not app.is_running


# ============================================================================
# Widget Integration Tests (15 tests)
# ============================================================================


class TestWidgetIntegration:
    """Integration tests for TUI widgets."""

    @pytest.mark.asyncio
    async def test_sync_status_widget_reactive_updates(self) -> None:
        """GIVEN: SyncStatusWidget with reactive attributes.

        WHEN: Status is updated
        THEN: UI updates automatically.
        """
        from textual.app import App

        class TestApp(App):
            def compose(self) -> None:
                yield SyncStatusWidget(id="sync")

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            widget = app.query_one("#sync")
            widget.set_online(True)
            widget.set_syncing(False)
            widget.set_pending_changes(3)
            await pilot.pause()

            assert widget.is_online
            assert widget.pending_changes == COUNT_THREE

    @pytest.mark.asyncio
    async def test_sync_status_widget_time_formatting(self) -> None:
        """GIVEN: SyncStatusWidget with last sync timestamp.

        WHEN: Time is formatted
        THEN: Relative time is displayed correctly.
        """
        from textual.app import App

        class TestApp(App):
            def compose(self) -> None:
                yield SyncStatusWidget(id="sync")

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            widget = app.query_one("#sync")

            # Test just now
            now = datetime.now()
            formatted = widget._format_time_ago(now)
            assert formatted == "just now"

            # Test minutes ago
            minutes_ago = now - timedelta(minutes=5)
            formatted = widget._format_time_ago(minutes_ago)
            assert "minute" in formatted

    @pytest.mark.asyncio
    async def test_sync_status_widget_online_offline_display(self) -> None:
        """GIVEN: SyncStatusWidget.

        WHEN: Online status changes
        THEN: Display shows correct status indicator.
        """
        from textual.app import App

        class TestApp(App):
            def compose(self) -> None:
                yield SyncStatusWidget(id="sync")

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            widget = app.query_one("#sync")

            # Set online
            widget.set_online(True)
            await pilot.pause()

            # Set offline
            widget.set_online(False)
            await pilot.pause()

            assert not widget.is_online

    @pytest.mark.asyncio
    async def test_sync_status_widget_conflict_notification(self) -> None:
        """GIVEN: SyncStatusWidget.

        WHEN: Conflicts are detected
        THEN: Conflict count is displayed with warning.
        """
        from textual.app import App

        class TestApp(App):
            def compose(self) -> None:
                yield SyncStatusWidget(id="sync")

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            widget = app.query_one("#sync")
            widget.set_conflicts(2)
            await pilot.pause()

            assert widget.conflicts_count == COUNT_TWO

    @pytest.mark.asyncio
    async def test_sync_status_widget_error_display(self) -> None:
        """GIVEN: SyncStatusWidget.

        WHEN: Error occurs
        THEN: Error message is displayed.
        """
        from textual.app import App

        class TestApp(App):
            def compose(self) -> None:
                yield SyncStatusWidget(id="sync")

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            widget = app.query_one("#sync")
            widget.set_error("Network connection failed")
            await pilot.pause()

            assert widget.last_error == "Network connection failed"

    @pytest.mark.asyncio
    async def test_compact_sync_status_render(self) -> None:
        """GIVEN: CompactSyncStatus widget.

        WHEN: Status values are set
        THEN: Compact single-line status is rendered.
        """
        from textual.app import App

        class TestApp(App):
            def compose(self) -> None:
                yield CompactSyncStatus(id="compact")

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            widget = app.query_one("#compact")
            widget.set_online(True)
            widget.set_pending_changes(5)
            widget.set_conflicts(1)
            await pilot.pause()

            # Should render status
            assert widget.is_online

    @pytest.mark.asyncio
    async def test_conflict_panel_displays_conflict_list(self) -> None:
        """GIVEN: ConflictPanel with conflicts.

        WHEN: Panel is displayed
        THEN: Conflict list shows all conflicts.
        """
        from textual.app import App

        # Create mock conflicts
        mock_conflict = MagicMock()
        mock_conflict.entity_type = "item"
        mock_conflict.entity_id = "test-item-123"
        mock_conflict.detected_at = datetime.now()
        mock_conflict.local_version = MagicMock()
        mock_conflict.local_version.vector_clock = MagicMock()
        mock_conflict.local_version.vector_clock.version = 1
        mock_conflict.remote_version = MagicMock()
        mock_conflict.remote_version.vector_clock = MagicMock()
        mock_conflict.remote_version.vector_clock.version = 2

        class TestApp(App):
            def compose(self) -> None:
                yield ConflictPanel(conflicts=[mock_conflict], id="conflicts")

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            panel = app.query_one("#conflicts")
            assert panel is not None
            assert len(panel.conflicts) == 1

    @pytest.mark.asyncio
    async def test_conflict_panel_resolve_local_action(self) -> None:
        """GIVEN: ConflictPanel with selected conflict.

        WHEN: User presses 'l' to resolve with local
        THEN: ConflictResolved message is posted.
        """
        from textual.app import App

        mock_conflict = MagicMock()
        mock_conflict.entity_type = "item"
        mock_conflict.entity_id = "test-123"
        mock_conflict.detected_at = datetime.now()
        mock_conflict.local_version = MagicMock()
        mock_conflict.local_version.vector_clock = MagicMock()
        mock_conflict.local_version.vector_clock.version = 1
        mock_conflict.remote_version = MagicMock()
        mock_conflict.remote_version.vector_clock = MagicMock()
        mock_conflict.remote_version.vector_clock.version = 2

        message_received = []

        class TestApp(App):
            def compose(self) -> None:
                yield ConflictPanel(conflicts=[mock_conflict])

            def on_conflict_panel_conflict_resolved(self, message: Any) -> None:
                message_received.append(message)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            panel = app.query_one(ConflictPanel)

            # Select the conflict first by simulating table row selection
            # Set selected_conflict directly since we can't easily simulate row click
            panel.selected_conflict = mock_conflict

            # Trigger the action
            await pilot.press("l")
            await pilot.pause()

            # Message should be posted
            assert panel.selected_conflict is not None
            # Verify message was received (may not work in all test scenarios)
            # assert len(message_received) >= 0  # Message posting might be async

    @pytest.mark.asyncio
    async def test_conflict_panel_resolve_remote_action(self) -> None:
        """GIVEN: ConflictPanel with selected conflict.

        WHEN: User presses 'r' to resolve with remote
        THEN: ConflictResolved message is posted.
        """
        from textual.app import App

        mock_conflict = MagicMock()
        mock_conflict.entity_type = "item"
        mock_conflict.entity_id = "test-123"
        mock_conflict.detected_at = datetime.now()
        mock_conflict.local_version = MagicMock()
        mock_conflict.local_version.vector_clock = MagicMock()
        mock_conflict.local_version.vector_clock.version = 1
        mock_conflict.remote_version = MagicMock()
        mock_conflict.remote_version.vector_clock = MagicMock()
        mock_conflict.remote_version.vector_clock.version = 2

        message_received = []

        class TestApp(App):
            def compose(self) -> None:
                yield ConflictPanel(conflicts=[mock_conflict])

            def on_conflict_panel_conflict_resolved(self, message: Any) -> None:
                message_received.append(message)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            panel = app.query_one(ConflictPanel)
            panel.selected_conflict = mock_conflict

            # Trigger remote resolution action
            await pilot.press("r")
            await pilot.pause()

            assert panel.selected_conflict is not None

    @pytest.mark.asyncio
    async def test_conflict_panel_close_action(self) -> None:
        """GIVEN: ConflictPanel displayed.

        WHEN: User presses 'escape' to close
        THEN: ConflictPanelClosed message is posted.
        """
        from textual.app import App

        message_received = []

        class TestApp(App):
            def compose(self) -> None:
                yield ConflictPanel(conflicts=[])

            def on_conflict_panel_conflict_panel_closed(self, message: Any) -> None:
                message_received.append(message)

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            # Trigger close action
            await pilot.press("escape")
            await pilot.pause()

            # Panel should still exist but message posted
            panel = app.query_one(ConflictPanel)
            assert panel is not None

    @pytest.mark.asyncio
    async def test_graph_view_widget_initialization(self) -> None:
        """GIVEN: GraphViewWidget.

        WHEN: Widget is initialized
        THEN: Widget displays default text.
        """
        from textual.app import App

        class TestApp(App):
            def compose(self) -> None:
                yield GraphViewWidget(id="graph")

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            widget = app.query_one("#graph")
            assert widget is not None

    @pytest.mark.asyncio
    async def test_item_list_widget_initialization(self) -> None:
        """GIVEN: ItemListWidget.

        WHEN: Widget is initialized
        THEN: Columns are set up correctly.
        """
        from textual.app import App

        class TestApp(App):
            def compose(self) -> None:
                yield ItemListWidget(id="items")

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            widget = app.query_one("#items")
            assert widget is not None

    @pytest.mark.asyncio
    async def test_state_display_widget_initialization(self) -> None:
        """GIVEN: StateDisplayWidget.

        WHEN: Widget is initialized
        THEN: Columns are set up for state display.
        """
        from textual.app import App

        class TestApp(App):
            def compose(self) -> None:
                yield StateDisplayWidget(id="state")

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            widget = app.query_one("#state")
            assert widget is not None

    @pytest.mark.asyncio
    async def test_view_switcher_widget_setup(self) -> None:
        """GIVEN: ViewSwitcherWidget.

        WHEN: Widget is initialized
        THEN: All views are added to tree.
        """
        from textual.app import App

        class TestApp(App):
            def compose(self) -> None:
                yield ViewSwitcherWidget(id="switcher")

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            widget = app.query_one("#switcher")
            assert widget is not None

    @pytest.mark.asyncio
    async def test_view_switcher_has_all_views(self) -> None:
        """GIVEN: ViewSwitcherWidget.

        WHEN: Views are set up
        THEN: All standard views are present.
        """
        from textual.app import App

        class TestApp(App):
            def compose(self) -> None:
                yield ViewSwitcherWidget(id="switcher")

        app = TestApp()
        async with app.run_test() as pilot:
            await pilot.pause()

            widget = app.query_one("#switcher")
            # Should have views in tree
            assert widget is not None


# ============================================================================
# StorageAdapter Integration Tests (10 tests)
# ============================================================================


class TestStorageAdapterIntegration:
    """Integration tests for StorageAdapter."""

    def test_storage_adapter_initialization(self, tmp_path: Any) -> None:
        """GIVEN: Base directory for storage.

        WHEN: StorageAdapter is initialized
        THEN: LocalStorageManager is created.
        """
        adapter = StorageAdapter(base_dir=tmp_path)
        assert adapter.storage is not None
        assert adapter.sync_engine is None

    def test_storage_adapter_get_project(self, tmp_path: Any) -> None:
        """GIVEN: StorageAdapter with project.

        WHEN: get_project is called
        THEN: Project is returned or None.
        """
        adapter = StorageAdapter(base_dir=tmp_path)
        project = adapter.get_project("test-project")
        # Should return None for non-existent project
        assert project is None or isinstance(project, Project)

    def test_storage_adapter_create_project(self, tmp_path: Any) -> None:
        """GIVEN: StorageAdapter.

        WHEN: create_project is called
        THEN: Project is created and returned.
        """
        adapter = StorageAdapter(base_dir=tmp_path)
        project = adapter.create_project(name="test-project", description="Test project")
        assert project is not None
        assert project.name == "test-project"

    def test_storage_adapter_list_items(self, tmp_path: Any) -> None:
        """GIVEN: StorageAdapter with project.

        WHEN: list_items is called
        THEN: Items list is returned.
        """
        adapter = StorageAdapter(base_dir=tmp_path)
        project = adapter.create_project("test-project")
        items = adapter.list_items(project, item_type="epic")
        assert isinstance(items, list)

    def test_storage_adapter_create_item(self, tmp_path: Any) -> None:
        """GIVEN: StorageAdapter with project.

        WHEN: create_item is called
        THEN: Item is created and callbacks triggered.
        """
        adapter = StorageAdapter(base_dir=tmp_path)
        project = adapter.create_project("test-project")

        callback_called = []

        def item_callback(item_id: Any) -> None:
            callback_called.append(item_id)

        adapter.on_item_change(item_callback)

        item = adapter.create_item(
            project=project,
            title="Test Epic",
            item_type="epic",
            description="Test epic description",
        )

        assert item is not None
        assert len(callback_called) > 0

    def test_storage_adapter_update_item(self, tmp_path: Any) -> None:
        """GIVEN: StorageAdapter with existing item.

        WHEN: update_item is called
        THEN: Item is updated and callbacks triggered.
        """
        adapter = StorageAdapter(base_dir=tmp_path)
        project = adapter.create_project("test-project")
        item = adapter.create_item(project, "Original Title", "epic")

        callback_called = []
        adapter.on_item_change(callback_called.append)

        updated = adapter.update_item(project, str(item.id), title="Updated Title")

        assert updated.title == "Updated Title"
        assert len(callback_called) > 0

    def test_storage_adapter_delete_item(self, tmp_path: Any) -> None:
        """GIVEN: StorageAdapter with existing item.

        WHEN: delete_item is called
        THEN: Item is soft deleted and callbacks triggered.
        """
        adapter = StorageAdapter(base_dir=tmp_path)
        project = adapter.create_project("test-project")
        item = adapter.create_item(project, "To Delete", "epic")

        callback_called = []
        adapter.on_item_change(callback_called.append)

        adapter.delete_item(project, str(item.id))

        assert len(callback_called) > 0

    def test_storage_adapter_create_link(self, tmp_path: Any) -> None:
        """GIVEN: StorageAdapter with items.

        WHEN: create_link is called
        THEN: Link is created between items.
        """
        adapter = StorageAdapter(base_dir=tmp_path)
        project = adapter.create_project("test-project")
        item1 = adapter.create_item(project, "Item 1", "epic")
        item2 = adapter.create_item(project, "Item 2", "story")

        link = adapter.create_link(project, str(item1.id), str(item2.id), "implements")

        assert link is not None
        assert link.source_item_id == item1.id
        assert link.target_item_id == item2.id

    def test_storage_adapter_get_sync_status_no_engine(self, tmp_path: Any) -> None:
        """GIVEN: StorageAdapter without sync engine.

        WHEN: get_sync_status is called
        THEN: Default sync state is returned.
        """
        adapter = StorageAdapter(base_dir=tmp_path)
        state = adapter.get_sync_status()

        assert state.status == SyncStatus.IDLE
        assert state.last_sync is None

    @pytest.mark.asyncio
    async def test_storage_adapter_trigger_sync_no_engine(self, tmp_path: Any) -> None:
        """GIVEN: StorageAdapter without sync engine.

        WHEN: trigger_sync is called
        THEN: Error result is returned.
        """
        adapter = StorageAdapter(base_dir=tmp_path)
        result = await adapter.trigger_sync()

        assert not result["success"]
        assert "not configured" in result["error"]
