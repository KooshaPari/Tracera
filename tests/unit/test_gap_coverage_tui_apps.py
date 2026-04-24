"""Gap coverage tests for TUI apps and storage adapter.

Targets: tui/apps/*.py, tui/adapters/storage_adapter.py.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestStorageAdapter:
    """Tests for StorageAdapter."""

    def test_storage_adapter_import(self) -> None:
        """Test StorageAdapter can be imported."""
        from tracertm.tui.adapters.storage_adapter import StorageAdapter

        assert StorageAdapter is not None

    def test_storage_adapter_init(self) -> None:
        """Test StorageAdapter initialization."""
        from tracertm.tui.adapters.storage_adapter import StorageAdapter

        with patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager"):
            adapter = StorageAdapter()

            assert adapter.sync_engine is None
            assert adapter._sync_status_callbacks == []
            assert adapter._conflict_callbacks == []
            assert adapter._item_change_callbacks == []

    def test_storage_adapter_init_with_base_dir(self) -> None:
        """Test StorageAdapter initialization with base_dir."""
        from tracertm.tui.adapters.storage_adapter import StorageAdapter

        with patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager") as mock_storage:
            test_path = Path(tempfile.mkdtemp())
            StorageAdapter(base_dir=test_path)

            mock_storage.assert_called_once_with(test_path)

    def test_storage_adapter_init_with_sync_engine(self) -> None:
        """Test StorageAdapter initialization with sync_engine."""
        from tracertm.tui.adapters.storage_adapter import StorageAdapter

        mock_sync_engine = MagicMock()

        with patch("tracertm.tui.adapters.storage_adapter.LocalStorageManager"):
            adapter = StorageAdapter(sync_engine=mock_sync_engine)

            assert adapter.sync_engine == mock_sync_engine


class TestTuiAppsImports:
    """Tests for TUI app imports."""

    def test_browser_app_import(self) -> None:
        """Test Browser app can be imported."""
        from tracertm.tui.apps.browser import BrowserApp

        assert BrowserApp is not None

    def test_dashboard_app_import(self) -> None:
        """Test Dashboard app can be imported."""
        from tracertm.tui.apps.dashboard import DashboardApp

        assert DashboardApp is not None

    def test_dashboard_compat_import(self) -> None:
        """Test dashboard_compat module can be imported."""
        from tracertm.tui.apps import dashboard_compat

        assert dashboard_compat is not None

    def test_graph_app_import(self) -> None:
        """Test GraphApp can be imported."""
        from tracertm.tui.apps.graph import GraphApp

        assert GraphApp is not None


class TestTuiAdaptersInit:
    """Tests for TUI adapters __init__.py."""

    def test_adapters_init_import(self) -> None:
        """Test adapters module can be imported."""
        from tracertm.tui import adapters

        assert adapters is not None

    def test_adapters_exports_storage_adapter(self) -> None:
        """Test StorageAdapter is exported from adapters."""
        from tracertm.tui.adapters import StorageAdapter

        assert StorageAdapter is not None


class TestBrowserAppConstants:
    """Tests for BrowserApp constants."""

    def test_browser_app_module(self) -> None:
        """Test browser module can be imported."""
        from tracertm.tui.apps import browser

        assert browser is not None


class TestDashboardAppConstants:
    """Tests for DashboardApp constants."""

    def test_dashboard_app_module(self) -> None:
        """Test dashboard module can be imported."""
        from tracertm.tui.apps import dashboard

        assert dashboard is not None


class TestGraphAppConstants:
    """Tests for GraphApp constants."""

    def test_graph_app_module(self) -> None:
        """Test graph module can be imported."""
        from tracertm.tui.apps import graph

        assert graph is not None


class TestTuiAppsInit:
    """Tests for TUI apps __init__.py."""

    def test_apps_init_import(self) -> None:
        """Test apps module can be imported."""
        from tracertm.tui import apps

        assert apps is not None

    def test_apps_exports_browser(self) -> None:
        """Test BrowserApp is exported from apps."""
        from tracertm.tui.apps import BrowserApp

        assert BrowserApp is not None

    def test_apps_exports_dashboard(self) -> None:
        """Test DashboardApp is exported from apps."""
        from tracertm.tui.apps import DashboardApp

        assert DashboardApp is not None

    def test_apps_exports_graph(self) -> None:
        """Test GraphApp is exported from apps."""
        from tracertm.tui.apps import GraphApp

        assert GraphApp is not None


class TestTuiInit:
    """Tests for TUI __init__.py."""

    def test_tui_init_import(self) -> None:
        """Test TUI module can be imported."""
        from tracertm import tui

        assert tui is not None
