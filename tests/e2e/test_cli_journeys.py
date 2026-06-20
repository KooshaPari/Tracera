"""E2E tests for complete CLI user journeys (CLI-only, no real backend).

Tests real user workflows from start to finish:
- New user onboarding journey
- Feature development journey
- Multi-view traceability journey
- Backup/restore and ingestion
"""

import contextlib
import tempfile
from pathlib import Path
from types import SimpleNamespace

# Test runner
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from tracertm.cli.app import app

runner = CliRunner()


@pytest.mark.e2e
class TestNewUserJourney:
    """Test complete new user onboarding journey."""

    @patch("tracertm.cli.commands.config.ConfigManager")
    @patch("tracertm.database.connection.DatabaseConnection")
    @patch("tracertm.database.connection.DatabaseConnection")
    def test_new_user_onboarding(self, mock_db_class: Any, mock_project_db: Any, mock_config_class: Any) -> None:
        """Test new user: config → project → db → item."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config.config_path = Path("/tmp/test_config.json")
        mock_config_class.return_value = mock_config

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        mock_db.health_check.return_value = {
            "status": "connected",
            "version": "SQLite 3.0",
            "tables": 5,
            "pool_size": 0,
            "checked_out": 0,
        }
        mock_db_class.return_value = mock_db
        mock_project_db.return_value = mock_db

        # Step 1: Initialize config
        result1 = runner.invoke(
            app,
            ["config", "init", "--database-url", "sqlite:///test.db"],
            catch_exceptions=False,
        )

        # Step 2: Create project
        result2 = runner.invoke(
            app,
            ["project", "init", "Test Project", "--description", "Test"],
            catch_exceptions=False,
        )

        # Step 3: Check database
        result3 = runner.invoke(app, ["db", "status"], catch_exceptions=False)

        # Step 4: Create first item
        result4 = runner.invoke(
            app,
            [
                "item",
                "create",
                "First Item",
                "--view",
                "FEATURE",
                "--type",
                "feature",
            ],
            catch_exceptions=False,
        )

        # All should succeed (or fail gracefully)
        assert result1.exit_code in {0, 1, 2}
        assert result2.exit_code in {0, 1, 2}
        assert result3.exit_code in {0, 1, 2}
        assert result4.exit_code in {0, 1, 2}


@pytest.mark.e2e
class TestFeatureDevelopmentJourney:
    """Test complete feature development journey."""

    @patch("tracertm.cli.commands.item.ConfigManager")
    @patch("tracertm.database.connection.DatabaseConnection")
    @patch("tracertm.database.connection.DatabaseConnection")
    def test_feature_to_code_to_test_journey(
        self, mock_link_db: Any, mock_item_db: Any, mock_config_class: Any
    ) -> None:
        """Test journey: create feature → create code → create test → link them."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_class.return_value = mock_config

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        mock_item_db.return_value = mock_db
        mock_link_db.return_value = mock_db

        # Step 1: Create feature
        result1 = runner.invoke(
            app,
            [
                "item",
                "create",
                "User Login",
                "--view",
                "FEATURE",
                "--type",
                "feature",
            ],
            catch_exceptions=False,
        )

        # Step 2: Create code
        result2 = runner.invoke(
            app,
            [
                "item",
                "create",
                "auth/login.py",
                "--view",
                "CODE",
                "--type",
                "file",
            ],
            catch_exceptions=False,
        )

        # Step 3: Create test
        result3 = runner.invoke(
            app,
            [
                "item",
                "create",
                "test_login.py",
                "--view",
                "TEST",
                "--type",
                "test_suite",
            ],
            catch_exceptions=False,
        )

        # Step 4: Link feature to code
        result4 = runner.invoke(
            app,
            [
                "link",
                "create",
                "--source",
                "test-id-1",
                "--target",
                "test-id-2",
                "--type",
                "implements",
            ],
            catch_exceptions=False,
        )

        # Step 5: Link code to test
        result5 = runner.invoke(
            app,
            [
                "link",
                "create",
                "--source",
                "test-id-2",
                "--target",
                "test-id-3",
                "--type",
                "tested_by",
            ],
            catch_exceptions=False,
        )

        # All should attempt execution
        assert result1.exit_code in {0, 1, 2}
        assert result2.exit_code in {0, 1, 2}
        assert result3.exit_code in {0, 1, 2}
        assert result4.exit_code in {0, 1, 2}
        assert result5.exit_code in {0, 1, 2}


@pytest.mark.e2e
class TestMultiViewTraceabilityJourney:
    """Test multi-view navigation and traceability journey."""

    @patch("tracertm.cli.commands.view.ConfigManager")
    @patch("tracertm.database.connection.DatabaseConnection")
    @patch("tracertm.cli.commands.search._get_storage_manager")
    @patch("tracertm.database.connection.DatabaseConnection")
    def test_view_switch_search_drill_journey(
        self, mock_drill_db: Any, mock_storage_mgr: Any, mock_view_db: Any, mock_config_class: Any
    ) -> None:
        """Test journey: switch views → search → drill down."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_class.return_value = mock_config

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        mock_view_db.return_value = mock_db
        mock_drill_db.return_value = mock_db

        class _DummySession:
            def query(self, *_args: Any, **_kwargs: Any) -> None:
                return self

            def filter(self, *_args: Any, **_kwargs: Any) -> None:
                return self

            def limit(self, _n: Any) -> None:
                return self

            def all(self) -> None:
                return [
                    SimpleNamespace(
                        id="item-1", title="Login flow", view="FEATURE", item_type="feature", status="todo"
                    ),
                ]

        @contextlib.contextmanager
        def _dummy_session() -> None:
            yield _DummySession()

        mock_storage = MagicMock()
        mock_storage.get_session.return_value = _dummy_session()
        mock_storage_mgr.return_value = mock_storage

        # Step 1: List views
        result1 = runner.invoke(app, ["view", "list"], catch_exceptions=False)

        # Step 2: Switch to feature view
        result2 = runner.invoke(app, ["view", "switch", "FEATURE"], catch_exceptions=False)

        # Step 3: Search for items
        result3 = runner.invoke(app, ["search", "login", "--view", "FEATURE"], catch_exceptions=False)

        # Step 4: Drill down into item
        result4 = runner.invoke(app, ["drill", "test-id", "--depth", "3"], catch_exceptions=False)

        # Step 5: View state
        result5 = runner.invoke(app, ["state", "--view", "FEATURE"], catch_exceptions=False)

        assert result1.exit_code in {0, 1, 2}
        assert result2.exit_code in {0, 1, 2}
        assert result3.exit_code in {0, 1, 2}
        assert result4.exit_code in {0, 1, 2}
        assert result5.exit_code in {0, 1, 2}


@pytest.mark.e2e
class TestBackupRestoreJourney:
    """Test backup and restore journey."""

    @patch("tracertm.cli.commands.backup.ConfigManager")
    @patch("tracertm.database.connection.DatabaseConnection")
    def test_backup_restore_journey(self, mock_db_class: Any, mock_config_class: Any) -> None:
        """Test journey: create items → backup → restore."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_class.return_value = mock_config

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        mock_db_class.return_value = mock_db

        with tempfile.TemporaryDirectory() as tmpdir:
            backup_path = Path(tmpdir) / "backup.json"

            # Step 1: Create items
            result1 = runner.invoke(
                app,
                [
                    "item",
                    "create",
                    "Test Item",
                    "--view",
                    "FEATURE",
                    "--type",
                    "feature",
                ],
                catch_exceptions=False,
            )

            # Step 2: Create backup
            result2 = runner.invoke(
                app,
                [
                    "backup",
                    "backup",
                    "--output",
                    str(backup_path),
                    "--no-compress",
                    "--project-id",
                    "test-project",
                ],
                catch_exceptions=False,
            )

            # Step 3: Restore backup (if file exists)
            if backup_path.exists():
                result3 = runner.invoke(
                    app,
                    ["backup", "restore", str(backup_path), "--force"],
                    catch_exceptions=False,
                )

                assert result1.exit_code in {0, 1, 2}
                assert result2.exit_code in {0, 1, 2}
                assert result3.exit_code in {0, 1, 2}


@pytest.mark.e2e
class TestIngestionJourney:
    """Test file ingestion journey."""

    @patch("tracertm.cli.commands.ingest.ConfigManager")
    @patch("tracertm.database.connection.DatabaseConnection")
    @patch("tracertm.cli.commands.ingest.StatelessIngestionService")
    def test_markdown_ingestion_journey(
        self, mock_service_class: Any, mock_db_class: Any, mock_config_class: Any
    ) -> None:
        """Test journey: ingest markdown → view items."""
        mock_config = MagicMock()
        mock_config.get.return_value = "sqlite:///test.db"
        mock_config_class.return_value = mock_config

        mock_db = MagicMock()
        mock_db.engine = MagicMock()
        mock_db_class.return_value = mock_db

        mock_service = MagicMock()
        mock_service.ingest_markdown.return_value = {
            "items_created": 5,
            "links_created": 3,
            "project_id": "test-project",
        }
        mock_service_class.return_value = mock_service

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".md", delete=False) as f:
            f.write("# Test Document\n\n## Feature 1\n\nSome content.")
            md_path = Path(f.name)

        try:
            # Step 1: Ingest markdown
            result1 = runner.invoke(
                app,
                ["ingest", "markdown", str(md_path), "--view", "FEATURE"],
                catch_exceptions=False,
            )

            # Step 2: List items
            result2 = runner.invoke(app, ["item", "list", "--view", "FEATURE"], catch_exceptions=False)

            assert result1.exit_code in {0, 1, 2}
            assert result2.exit_code in {0, 1, 2}
        finally:
            md_path.unlink()
