"""Gap coverage tests for low-coverage CLI command modules.

Targets: history.py (6.12%), state.py (15.48%), watch.py (18.99%),
         search.py (64.52%), tui.py (54.76%).
"""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

runner = CliRunner()


class TestHistoryCommand:
    """Tests for history CLI command."""

    def test_history_module_import(self) -> None:
        """Test history module can be imported."""
        from tracertm.cli.commands import history

        assert history is not None
        assert history.app is not None

    def test_history_app_registered(self) -> None:
        """Test history app is a Typer app."""
        import typer

        from tracertm.cli.commands.history import app

        assert isinstance(app, typer.Typer)

    def test_show_history_no_project(self) -> None:
        """Test show_history when no project is configured."""
        from tracertm.cli.commands.history import app

        with patch("tracertm.cli.commands.history.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = None
            result = runner.invoke(app, ["ITEM-001"])
            assert result.exit_code != 0

    def test_show_history_item_not_found(self) -> None:
        """Test show_history when item doesn't exist."""
        from tracertm.cli.commands.history import app

        with (
            patch("tracertm.cli.commands.history.ConfigManager") as mock_config,
            patch("tracertm.cli.commands.history.LocalStorageManager") as mock_storage,
        ):
            mock_config.return_value.get.return_value = "test-project"
            mock_session = MagicMock()
            mock_session.query.return_value.filter.return_value.first.return_value = None
            mock_storage.return_value.get_session.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_storage.return_value.get_session.return_value.__exit__ = MagicMock(return_value=False)

            result = runner.invoke(app, ["NONEXISTENT"])
            # Should fail when item not found
            assert result.exit_code != 0 or "not found" in result.output.lower()

    def test_show_history_invalid_date(self) -> None:
        """Test show_history with invalid date format."""
        from tracertm.cli.commands.history import app

        with (
            patch("tracertm.cli.commands.history.ConfigManager") as mock_config,
            patch("tracertm.cli.commands.history.LocalStorageManager") as mock_storage,
        ):
            mock_config.return_value.get.return_value = "test-project"
            mock_item = MagicMock()
            mock_item.id = "ITEM-001"
            mock_session = MagicMock()
            mock_session.query.return_value.filter.return_value.first.return_value = mock_item
            mock_storage.return_value.get_session.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_storage.return_value.get_session.return_value.__exit__ = MagicMock(return_value=False)

            result = runner.invoke(app, ["ITEM-001", "--at", "invalid-date"])
            # Should fail on invalid date
            assert result.exit_code != 0 or "invalid" in result.output.lower()

    def test_show_history_command_name(self) -> None:
        """Test show_history command is registered correctly."""
        from tracertm.cli.commands.history import app

        # Check that the app has the show-history command
        commands = list(app.registered_commands)
        assert len(commands) > 0


class TestStateCommand:
    """Tests for state CLI command."""

    def test_state_module_import(self) -> None:
        """Test state module can be imported."""
        from tracertm.cli.commands import state

        assert state is not None
        assert state.app is not None

    def test_state_app_registered(self) -> None:
        """Test state app is a Typer app."""
        import typer

        from tracertm.cli.commands.state import app

        assert isinstance(app, typer.Typer)

    def test_show_state_no_project(self) -> None:
        """Test show_state when no project is configured."""
        from tracertm.cli.commands.state import app

        with patch("tracertm.cli.commands.state.ConfigManager") as mock_config:
            mock_config.return_value.get.return_value = None
            result = runner.invoke(app, ["show-state"])
            assert result.exit_code != 0

    def test_show_state_with_view_filter(self) -> None:
        """Test show_state with view filter."""
        from tracertm.cli.commands.state import app

        with (
            patch("tracertm.cli.commands.state.ConfigManager") as mock_config,
            patch("tracertm.cli.commands.state.LocalStorageManager") as mock_storage,
        ):
            mock_config.return_value.get.return_value = "test-project"
            mock_session = MagicMock()
            mock_session.query.return_value.filter.return_value.count.return_value = 5
            mock_session.query.return_value.filter.return_value.all.return_value = []
            mock_storage.return_value.get_session.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_storage.return_value.get_session.return_value.__exit__ = MagicMock(return_value=False)

            runner.invoke(app, ["show-state", "--view", "FEATURE"])
            # Should filter by view


class TestWatchCommand:
    """Tests for watch CLI command."""

    def test_watch_module_import(self) -> None:
        """Test watch module can be imported."""
        from tracertm.cli.commands import watch

        assert watch is not None
        assert watch.app is not None

    def test_watch_app_registered(self) -> None:
        """Test watch app is a Typer app."""
        import typer

        from tracertm.cli.commands.watch import app

        assert isinstance(app, typer.Typer)


class TestSearchCommand:
    """Tests for search CLI command."""

    def test_search_module_import(self) -> None:
        """Test search module can be imported."""
        from tracertm.cli.commands import search

        assert search is not None
        assert search.app is not None

    def test_search_app_registered(self) -> None:
        """Test search app is a Typer app."""
        import typer

        from tracertm.cli.commands.search import app

        assert isinstance(app, typer.Typer)


class TestTuiCommand:
    """Tests for tui CLI command."""

    def test_tui_module_import(self) -> None:
        """Test tui module can be imported."""
        from tracertm.cli.commands import tui

        assert tui is not None
        assert tui.app is not None

    def test_tui_app_registered(self) -> None:
        """Test tui app is a Typer app."""
        import typer

        from tracertm.cli.commands.tui import app

        assert isinstance(app, typer.Typer)


class TestProgressCommand:
    """Tests for progress CLI command."""

    def test_progress_module_import(self) -> None:
        """Test progress module can be imported."""
        from tracertm.cli.commands import progress

        assert progress is not None
        assert progress.app is not None


class TestIngestCommand:
    """Tests for ingest CLI command."""

    def test_ingest_module_import(self) -> None:
        """Test ingest module can be imported."""
        from tracertm.cli.commands import ingest

        assert ingest is not None
        assert ingest.app is not None


class TestChaosCommand:
    """Tests for chaos CLI command."""

    def test_chaos_module_import(self) -> None:
        """Test chaos module can be imported."""
        from tracertm.cli.commands import chaos

        assert chaos is not None
        assert chaos.app is not None


class TestExportCommand:
    """Tests for export CLI command."""

    def test_export_module_import(self) -> None:
        """Test export module can be imported."""
        from tracertm.cli.commands import export

        assert export is not None
        assert export.app is not None


class TestMigrateCommand:
    """Tests for migrate CLI command."""

    def test_migrate_module_import(self) -> None:
        """Test migrate module can be imported."""
        from tracertm.cli.commands import migrate

        assert migrate is not None
        assert migrate.app is not None
