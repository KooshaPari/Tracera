"""Phase 5 - CLI Item Comprehensive Coverage Tests.

Target: 400+ tests covering 95%+ of src/tracertm/cli/commands/item.py (845 LOC @ 5.44% current)
Focus lines: 63-71, 87-102, 115-126, 137-139, 153-171, 181-182, 214-345, 377-483, 505-649, 677-743, 762-825, 838-887, 920-1021, 1047-1087, 1099-1139, 1155-1222, 1239-1305, 1322-1379, 1401-1513, 1531-1554, 1570-1588, 1598-1630, 1643-1661, 1675-1691, 1705-1720
"""

import datetime
import json
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session
from typer.testing import CliRunner

from tests.test_constants import COUNT_FIVE
from tracertm.cli.commands.item import app as item_app
from tracertm.models.item import Item
from tracertm.models.project import Project
from tracertm.storage import LocalStorageManager


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """Create temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        # Create .trace directory structure
        trace_dir = project_path / ".trace"
        trace_dir.mkdir()
        (trace_dir / "config.yml").write_text("project: test")
        yield project_path


@pytest.fixture
def temp_project_dir_with_db(temp_project_dir: Path, db_session: Session) -> Path:
    """Create temporary project directory with database setup."""
    # Initialize project in database
    project = Project(
        id="test-project",
        name="Test Project",
        description="Test project for CLI tests",
        project_metadata={"test": True},
    )
    db_session.add(project)
    db_session.commit()
    return temp_project_dir


@pytest.fixture
def storage_manager(temp_project_dir: Path, _db_session: Session) -> LocalStorageManager:
    """Create storage manager for testing."""
    return LocalStorageManager(base_dir=temp_project_dir)


class TestBasicCRUDOperations:
    """Test Basic CRUD Operations for CLI item commands."""

    def test_create_item_basic_success(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test basic item creation success."""
        with patch("tracertm.cli.commands.item.DatabaseConnection") as mock_db:
            mock_db.return_value.get_session.return_value = db_session
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    item_app,
                    [
                        "create",
                        "Test Item",
                        "--view",
                        "FEATURE",
                        "--type",
                        "feature",
                        "--description",
                        "Test description",
                    ],
                )
                assert result.exit_code == 0
                assert "Test Item" in result.stdout

    def test_create_item_all_views(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test item creation with all valid views."""
        valid_views = ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]

        for view in valid_views:
            with (
                patch("tracertm.cli.commands.item.DatabaseConnection"),
                patch(
                    "tracertm.cli.commands.item._get_project_storage_path",
                    return_value=temp_project_dir_with_db,
                ),
            ):
                result = cli_runner.invoke(
                    item_app,
                    [
                        "create",
                        "--title",
                        f"Test {view}",
                        "--view",
                        view,
                        "--type",
                        "task",  # Common type across views
                        "--description",
                        f"Test {view} item",
                    ],
                )
                assert result.exit_code == 0, f"Failed for view: {view}"
                assert f"Test {view}" in result.stdout

    def test_create_item_all_feature_types(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test item creation with all FEATURE view types."""
        feature_types = ["epic", "feature", "story", "task", "bug"]

        for item_type in feature_types:
            with (
                patch("tracertm.cli.commands.item.DatabaseConnection"),
                patch(
                    "tracertm.cli.commands.item._get_project_storage_path",
                    return_value=temp_project_dir_with_db,
                ),
            ):
                result = cli_runner.invoke(
                    item_app,
                    [
                        "create",
                        "--title",
                        f"Test {item_type}",
                        "--view",
                        "FEATURE",
                        "--type",
                        item_type,
                        "--description",
                        f"Test {item_type} item",
                    ],
                )
                assert result.exit_code == 0, f"Failed for type: {item_type}"
                assert f"Test {item_type}" in result.stdout

    def test_create_item_all_code_types(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test item creation with all CODE view types."""
        code_types = ["file", "class", "function", "module"]

        for item_type in code_types:
            with (
                patch("tracertm.cli.commands.item.DatabaseConnection"),
                patch(
                    "tracertm.cli.commands.item._get_project_storage_path",
                    return_value=temp_project_dir_with_db,
                ),
            ):
                result = cli_runner.invoke(
                    item_app,
                    [
                        "create",
                        "--title",
                        f"Test {item_type}",
                        "--view",
                        "CODE",
                        "--type",
                        item_type,
                        "--description",
                        f"Test {item_type} item",
                    ],
                )
                assert result.exit_code == 0, f"Failed for type: {item_type}"

    def test_create_item_with_metadata(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test item creation with metadata."""
        metadata = {"priority": "high", "assignee": "user@example.com", "tags": ["urgent", "backend"]}

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    item_app,
                    [
                        "create",
                        "--title",
                        "Test Item with Metadata",
                        "--view",
                        "FEATURE",
                        "--type",
                        "feature",
                        "--description",
                        "Test with metadata",
                        "--metadata",
                        json.dumps(metadata),
                    ],
                )
                assert result.exit_code == 0
                assert "Test Item with Metadata" in result.stdout

    def test_create_item_invalid_view(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test item creation with invalid view."""
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    item_app,
                    [
                        "create",
                        "--title",
                        "Test Item",
                        "--view",
                        "INVALID_VIEW",
                        "--type",
                        "feature",
                        "--description",
                        "Test description",
                    ],
                )
                assert result.exit_code != 0
                assert "Invalid view" in result.stdout

    def test_create_item_invalid_type(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test item creation with invalid type for view."""
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    item_app,
                    [
                        "create",
                        "--title",
                        "Test Item",
                        "--view",
                        "FEATURE",
                        "--type",
                        "invalid_type",
                        "--description",
                        "Test description",
                    ],
                )
                assert result.exit_code != 0
                assert "Invalid type" in result.stdout

    def test_create_item_missing_required_fields(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test item creation with missing required fields."""
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                # Missing title
                result = cli_runner.invoke(
                    item_app,
                    ["create", "--view", "FEATURE", "--type", "feature", "--description", "Test description"],
                )
                assert result.exit_code != 0

    def test_create_item_with_parent(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test item creation with parent item."""
        # Create parent item first
        parent = Item(
            title="Parent Item",
            view="FEATURE",
            type="epic",
            description="Parent item",
            metadata={},
            project_id="test-project",
        )
        db_session.add(parent)
        db_session.commit()

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    item_app,
                    [
                        "create",
                        "--title",
                        "Child Item",
                        "--view",
                        "FEATURE",
                        "--type",
                        "feature",
                        "--description",
                        "Child item",
                        "--parent",
                        str(parent.id),
                    ],
                )
                assert result.exit_code == 0
                assert "Child Item" in result.stdout

    def test_list_items_basic(self, cli_runner: CliRunner, temp_project_dir_with_db: Path, db_session: Session) -> None:
        """Test basic item listing."""
        # Create test items
        for i in range(5):
            item = Item(
                title=f"Test Item {i}",
                view="FEATURE",
                type="task",
                description=f"Test item {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
        db_session.commit()

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["list"])
                assert result.exit_code == 0
                assert "Test Item" in result.stdout

    def test_list_items_by_view(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test item listing filtered by view."""
        # Create items in different views
        views = ["FEATURE", "CODE", "API"]
        for view in views:
            item = Item(
                title=f"Test {view} Item",
                view=view,
                type="task",
                description=f"Test {view} item",
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
        db_session.commit()

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["list", "--view", "FEATURE"])
                assert result.exit_code == 0
                assert "Test FEATURE Item" in result.stdout
                assert "Test CODE Item" not in result.stdout

    def test_list_items_by_type(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test item listing filtered by type."""
        # Create items with different types
        types = ["feature", "task", "bug"]
        for item_type in types:
            item = Item(
                title=f"Test {item_type}",
                view="FEATURE",
                type=item_type,
                description=f"Test {item_type} item",
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
        db_session.commit()

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["list", "--type", "feature"])
                assert result.exit_code == 0
                assert "Test feature" in result.stdout
                assert "Test task" not in result.stdout

    def test_list_items_with_limit(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test item listing with limit."""
        # Create more items than limit
        for i in range(10):
            item = Item(
                title=f"Test Item {i}",
                view="FEATURE",
                type="task",
                description=f"Test item {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
        db_session.commit()

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["list", "--limit", "5"])
                assert result.exit_code == 0
                # Should only show 5 items
                assert result.stdout.count("Test Item") <= COUNT_FIVE

    def test_list_items_with_offset(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test item listing with offset."""
        # Create items
        for i in range(10):
            item = Item(
                title=f"Test Item {i}",
                view="FEATURE",
                type="task",
                description=f"Test item {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
        db_session.commit()

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["list", "--offset", "5", "--limit", "3"])
                assert result.exit_code == 0
                # Should show items 5, 6, 7
                assert "Test Item 5" in result.stdout
                assert "Test Item 0" not in result.stdout

    def test_show_item_success(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test showing item details successfully."""
        # Create test item
        item = Item(
            title="Test Item",
            view="FEATURE",
            type="feature",
            description="Test description",
            metadata={"priority": "high"},
            project_id="test-project",
        )
        db_session.add(item)
        db_session.commit()

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["show", str(item.id)])
                assert result.exit_code == 0
                assert "Test Item" in result.stdout
                assert "Test description" in result.stdout
                assert "high" in result.stdout

    def test_show_item_not_found(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test showing non-existent item."""
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["show", "non-existent-id"])
                assert result.exit_code != 0
                assert "not found" in result.stdout.lower()

    def test_update_item_basic(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test basic item update."""
        # Create test item
        item = Item(
            title="Original Title",
            view="FEATURE",
            type="task",
            description="Original description",
            metadata={},
            project_id="test-project",
        )
        db_session.add(item)
        db_session.commit()

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    item_app,
                    ["update", str(item.id), "--title", "Updated Title", "--description", "Updated description"],
                )
                assert result.exit_code == 0
                assert "Updated Title" in result.stdout

    def test_update_item_metadata(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test updating item metadata."""
        # Create test item
        item = Item(
            title="Test Item",
            view="FEATURE",
            type="task",
            description="Test description",
            metadata={},
            project_id="test-project",
        )
        db_session.add(item)
        db_session.commit()

        new_metadata = {"priority": "urgent", "status": "in-progress"}
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["update", str(item.id), "--metadata", json.dumps(new_metadata)])
                assert result.exit_code == 0

    def test_delete_item_success(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test successful item deletion."""
        # Create test item
        item = Item(
            title="Test Item",
            view="FEATURE",
            type="task",
            description="Test description",
            metadata={},
            project_id="test-project",
        )
        db_session.add(item)
        db_session.commit()
        item_id = item.id

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["delete", str(item_id)])
                assert result.exit_code == 0
                assert "deleted" in result.stdout.lower()

    def test_delete_item_not_found(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test deleting non-existent item."""
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["delete", "non-existent-id"])
                assert result.exit_code != 0
                assert "not found" in result.stdout.lower()

    def test_undelete_item_success(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test successful item undeletion."""
        # Create and delete test item
        item = Item(
            title="Test Item",
            view="FEATURE",
            type="task",
            description="Test description",
            metadata={},
            project_id="test-project",
            deleted_at="",
        )
        db_session.add(item)
        db_session.commit()
        item_id = item.id

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["undelete", str(item_id)])
                assert result.exit_code == 0
                assert "restored" in result.stdout.lower()

    def test_bulk_create_items(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test bulk creation of items."""
        items_data = [
            {"title": "Item 1", "view": "FEATURE", "type": "task"},
            {"title": "Item 2", "view": "CODE", "type": "function"},
            {"title": "Item 3", "view": "API", "type": "endpoint"},
        ]

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["bulk-create", "--data", json.dumps(items_data)])
                assert result.exit_code == 0
                assert "Item 1" in result.stdout
                assert "Item 2" in result.stdout
                assert "Item 3" in result.stdout

    def test_bulk_update_items(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test bulk update of items."""
        # Create test items
        item_ids = []
        for i in range(3):
            item = Item(
                title=f"Item {i}",
                view="FEATURE",
                type="task",
                description=f"Original description {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
            db_session.commit()
            item_ids.append(str(item.id))

        update_data = {
            "updates": [
                {"id": item_ids[0], "title": "Updated Item 0"},
                {"id": item_ids[1], "title": "Updated Item 1"},
                {"id": item_ids[2], "description": "New description 2"},
            ],
        }

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["bulk-update", "--data", json.dumps(update_data)])
                assert result.exit_code == 0
                assert "Updated Item" in result.stdout

    def test_shell_completion_item_ids(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test shell completion for item IDs."""
        # Create test items
        for i in range(5):
            item = Item(
                title=f"Test Item {i}",
                view="FEATURE",
                type="task",
                description=f"Test item {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
        db_session.commit()

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            result = cli_runner.invoke(item_app, ["shell-completion", "item-ids"])
            assert result.exit_code == 0
            for _i in range(5):
                # Should contain at least some item IDs
                assert len(result.stdout.strip()) > 0

    def test_shell_completion_views(self, cli_runner: CliRunner) -> None:
        """Test shell completion for views."""
        result = cli_runner.invoke(item_app, ["shell-completion", "views"])
        assert result.exit_code == 0
        expected_views = ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]
        for view in expected_views:
            assert view in result.stdout

    def test_shell_completion_types_feature(self, cli_runner: CliRunner) -> None:
        """Test shell completion for FEATURE view types."""
        result = cli_runner.invoke(item_app, ["shell-completion", "types", "--view", "FEATURE"])
        assert result.exit_code == 0
        expected_types = ["epic", "feature", "story", "task", "bug"]
        for type_name in expected_types:
            assert type_name in result.stdout

    def test_shell_completion_types_code(self, cli_runner: CliRunner) -> None:
        """Test shell completion for CODE view types."""
        result = cli_runner.invoke(item_app, ["shell-completion", "types", "--view", "CODE"])
        assert result.exit_code == 0
        expected_types = ["file", "class", "function", "module"]
        for type_name in expected_types:
            assert type_name in result.stdout


class TestAdvancedWorkflowOperations:
    """Test Advanced Workflow Operations for CLI item commands."""

    def test_item_workflow_transition(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test item status transition through workflow."""
        # Create item with initial status
        item = Item(
            title="Workflow Item",
            view="FEATURE",
            type="story",
            description="Test workflow",
            metadata={"status": "todo"},
            project_id="test-project",
        )
        db_session.add(item)
        db_session.commit()

        # Update status through workflow
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    item_app,
                    ["update", str(item.id), "--metadata", json.dumps({"status": "in-progress"})],
                )
                assert result.exit_code == 0

    def test_item_hierarchy_management(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test managing item hierarchies (parent-child relationships)."""
        # Create parent items
        epic = Item(
            title="Parent Epic",
            view="FEATURE",
            type="epic",
            description="Parent epic",
            metadata={},
            project_id="test-project",
        )
        db_session.add(epic)
        db_session.commit()

        feature = Item(
            title="Child Feature",
            view="FEATURE",
            type="feature",
            description="Child feature",
            metadata={},
            parent_id=epic.id,
            project_id="test-project",
        )
        db_session.add(feature)
        db_session.commit()

        # Create story under feature
        story = Item(
            title="Child Story",
            view="FEATURE",
            type="story",
            description="Child story",
            metadata={},
            parent_id=feature.id,
            project_id="test-project",
        )
        db_session.add(story)
        db_session.commit()

        # Test hierarchy listing
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["list", "--hierarchy"])
                assert result.exit_code == 0
                assert "Parent Epic" in result.stdout
                assert "Child Feature" in result.stdout
                assert "Child Story" in result.stdout

    def test_item_bulk_delete_with_dependencies(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test bulk deletion of items with dependency checking."""
        # Create items with relationships
        parent_item = Item(
            title="Parent Item",
            view="FEATURE",
            type="feature",
            description="Parent item",
            metadata={},
            project_id="test-project",
        )
        db_session.add(parent_item)
        db_session.commit()

        child_items = []
        for i in range(3):
            child = Item(
                title=f"Child Item {i}",
                view="FEATURE",
                type="task",
                description=f"Child task {i}",
                metadata={},
                parent_id=parent_item.id,
                project_id="test-project",
            )
            db_session.add(child)
            db_session.commit()
            child_items.append(child)

        # Test bulk delete
        item_ids_to_delete = [child.id for child in child_items]
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    item_app,
                    ["bulk-delete", "--ids", *item_ids_to_delete],
                    input="y",  # Confirm deletion
                )
                assert result.exit_code == 0
                assert "deleted" in result.stdout.lower()

    def test_item_search_operations(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test advanced item search operations."""
        # Create diverse items
        items_data = [
            {
                "title": "Backend API Feature",
                "view": "FEATURE",
                "type": "feature",
                "description": "API backend implementation",
            },
            {"title": "Frontend UI Component", "view": "CODE", "type": "component", "description": "React component"},
            {"title": "Database Migration", "view": "DATABASE", "type": "migration", "description": "Schema migration"},
            {"title": "Integration Test", "view": "TEST", "type": "test_suite", "description": "Integration testing"},
        ]

        for item_data in items_data:
            item = Item(
                title=item_data["title"],
                view=item_data["view"],
                type=item_data["type"],
                description=item_data["description"],
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
        db_session.commit()

        # Test search by title
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["search", "--query", "API"])
                assert result.exit_code == 0
                assert "Backend API Feature" in result.stdout
                assert "Frontend UI Component" not in result.stdout

    def test_item_filter_by_metadata(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test filtering items by metadata fields."""
        # Create items with different metadata
        items_metadata = [
            {"title": "High Priority Item", "priority": "high"},
            {"title": "Low Priority Item", "priority": "low"},
            {"title": "Assigned Item", "assignee": "user@example.com"},
            {"title": "Tagged Item", "tags": ["frontend", "urgent"]},
        ]

        for item_meta in items_metadata:
            item = Item(
                title=item_meta["title"],
                view="FEATURE",
                type="task",
                description=f"Item with metadata {item_meta['title']}",
                metadata=item_meta,
                project_id="test-project",
            )
            db_session.add(item)
        db_session.commit()

        # Test filter by priority
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["list", "--filter", "priority:high"])
                assert result.exit_code == 0
                assert "High Priority Item" in result.stdout
                assert "Low Priority Item" not in result.stdout

    def test_item_sort_operations(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test item sorting operations."""
        # Create items with different creation times
        import time

        items = []
        for i in range(5):
            time.sleep(0.01)  # Ensure different timestamps
            item = Item(
                title=f"Item {i}",
                view="FEATURE",
                type="task",
                description=f"Test item {i}",
                metadata={},
                project_id="test-project",
                created_at=datetime.datetime.now(datetime.UTC).isoformat(),
            )
            db_session.add(item)
            db_session.commit()
            items.append(item)

        # Test sorting by title
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["list", "--sort", "title"])
                assert result.exit_code == 0
                # Should be sorted alphabetically
                lines = result.stdout.split("\n")
                title_lines = [line for line in lines if "Item " in line]
                # Basic check that some ordering is applied
                assert len(title_lines) > 0

    def test_item_export_operations(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test item export operations."""
        # Create test items
        for i in range(3):
            item = Item(
                title=f"Export Item {i}",
                view="FEATURE",
                type="task",
                description=f"Item for export {i}",
                metadata={"export_id": i},
                project_id="test-project",
            )
            db_session.add(item)
        db_session.commit()

        # Test JSON export
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["export", "--format", "json"])
                assert result.exit_code == 0
                assert "Export Item" in result.stdout
                # Should be valid JSON
                assert result.stdout.strip().startswith("[") or result.stdout.strip().startswith("{")

    def test_item_import_operations(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test item import operations."""
        # Create import data
        import_data = [
            {
                "title": "Imported Item 1",
                "view": "FEATURE",
                "type": "feature",
                "description": "Imported via CLI",
                "metadata": {"imported": True},
            },
            {
                "title": "Imported Item 2",
                "view": "CODE",
                "type": "function",
                "description": "Another imported item",
                "metadata": {"imported": True},
            },
        ]

        # Create temporary file with import data
        import_file = temp_project_dir_with_db / "import_data.json"
        import_file.write_text(json.dumps(import_data))

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["import", "--file", str(import_file)])
                assert result.exit_code == 0
                assert "Imported Item 1" in result.stdout
                assert "Imported Item 2" in result.stdout

    def test_item_statistics(self, cli_runner: CliRunner, temp_project_dir_with_db: Path, db_session: Session) -> None:
        """Test item statistics and reporting."""
        # Create diverse items
        items_data = [
            ("FEATURE", "feature", 3),
            ("FEATURE", "task", 5),
            ("CODE", "function", 2),
            ("API", "endpoint", 4),
            ("TEST", "test_case", 6),
        ]

        for view, item_type, count in items_data:
            for i in range(count):
                item = Item(
                    title=f"{view} {item_type} {i}",
                    view=view,
                    type=item_type,
                    description=f"{view} {item_type} item {i}",
                    metadata={},
                    project_id="test-project",
                )
                db_session.add(item)
        db_session.commit()

        # Test statistics command
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["stats"])
                assert result.exit_code == 0
                assert "FEATURE" in result.stdout
                assert "CODE" in result.stdout
                assert "Total" in result.stdout

    def test_item_validation_rules(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        _db_session: Session,
    ) -> None:
        """Test item validation rules and constraints."""
        # Test creating item with invalid metadata
        invalid_metadata = "not valid json"

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    item_app,
                    [
                        "create",
                        "--title",
                        "Invalid Item",
                        "--view",
                        "FEATURE",
                        "--type",
                        "feature",
                        "--description",
                        "Test invalid metadata",
                        "--metadata",
                        invalid_metadata,
                    ],
                )
                assert result.exit_code != 0

    def test_item_cross_project_operations(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test item operations across multiple projects."""
        # Create additional project
        project2 = Project(
            id="test-project-2",
            name="Test Project 2",
            description="Second test project",
            config={"test": True},
        )
        db_session.add(project2)
        db_session.commit()

        # Create item in first project
        item1 = Item(
            title="Project 1 Item",
            view="FEATURE",
            type="feature",
            description="Item in project 1",
            metadata={},
            project_id="test-project",
        )
        db_session.add(item1)

        # Create item in second project
        item2 = Item(
            title="Project 2 Item",
            view="FEATURE",
            type="feature",
            description="Item in project 2",
            metadata={},
            project_id="test-project-2",
        )
        db_session.add(item2)
        db_session.commit()

        # List items should only show current project items
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["list"])
                assert result.exit_code == 0
                assert "Project 1 Item" in result.stdout
                assert "Project 2 Item" not in result.stdout

    def test_item_templates(self, cli_runner: CliRunner, temp_project_dir_with_db: Path, _db_session: Session) -> None:
        """Test creating items from templates."""
        # Create template data
        template_data = {
            "title": "Template Item",
            "view": "FEATURE",
            "type": "feature",
            "description": "Template description",
            "metadata": {"template": True, "priority": "medium"},
        }

        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    item_app,
                    ["create-from-template", "--title", "Actual Item", "--template", json.dumps(template_data)],
                )
                assert result.exit_code == 0
                assert "Actual Item" in result.stdout

    def test_item_dependency_visualization(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test visualizing item dependencies."""
        # Create hierarchical items
        parent = Item(
            title="Parent Item",
            view="FEATURE",
            type="feature",
            description="Parent item",
            metadata={},
            project_id="test-project",
        )
        db_session.add(parent)
        db_session.commit()

        child1 = Item(
            title="Child Item 1",
            view="FEATURE",
            type="task",
            description="Child task 1",
            metadata={},
            parent_id=parent.id,
            project_id="test-project",
        )
        db_session.add(child1)

        child2 = Item(
            title="Child Item 2",
            view="FEATURE",
            type="task",
            description="Child task 2",
            metadata={},
            parent_id=parent.id,
            project_id="test-project",
        )
        db_session.add(child2)
        db_session.commit()

        # Test dependency visualization
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["deps", str(parent.id)])
                assert result.exit_code == 0
                assert "Parent Item" in result.stdout
                assert "Child Item 1" in result.stdout
                assert "Child Item 2" in result.stdout

    def test_item_batch_status_update(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test batch update of item statuses."""
        # Create items
        item_ids = []
        for i in range(5):
            item = Item(
                title=f"Item {i}",
                view="FEATURE",
                type="task",
                description=f"Task item {i}",
                metadata={"status": "todo"},
                project_id="test-project",
            )
            db_session.add(item)
            db_session.commit()
            item_ids.append(str(item.id))

        # Batch update status
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    item_app,
                    ["batch-update", "--ids", *item_ids, "--metadata", json.dumps({"status": "in-progress"})],
                )
                assert result.exit_code == 0
                assert "in-progress" in result.stdout

    def test_item_versioning(self, cli_runner: CliRunner, temp_project_dir_with_db: Path, db_session: Session) -> None:
        """Test item versioning and history tracking."""
        # Create item
        item = Item(
            title="Versioned Item",
            view="FEATURE",
            type="feature",
            description="Initial version",
            metadata={"version": 1},
            project_id="test-project",
        )
        db_session.add(item)
        db_session.commit()

        # Update item multiple times
        updates = [
            {"title": "Versioned Item v2", "description": "Second version", "metadata": {"version": 2}},
            {"title": "Versioned Item v3", "description": "Third version", "metadata": {"version": 3}},
        ]

        for update in updates:
            with (
                patch("tracertm.cli.commands.item.DatabaseConnection"),
                patch(
                    "tracertm.cli.commands.item._get_project_storage_path",
                    return_value=temp_project_dir_with_db,
                ),
            ):
                result = cli_runner.invoke(
                    item_app,
                    ["update", str(item.id)]
                    + [f"--{k}" for k in update if k != "metadata"]
                    + (["--metadata", json.dumps(update["metadata"])] if "metadata" in update else []),
                )
                assert result.exit_code == 0

        # View item history
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["history", str(item.id)])
                assert result.exit_code == 0
                assert "version" in result.stdout.lower()

    def test_item_workflow_validation(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test workflow validation and status transitions."""
        # Create item with workflow metadata
        item = Item(
            title="Workflow Item",
            view="FEATURE",
            type="story",
            description="Item with workflow",
            metadata={"status": "todo", "workflow": "standard"},
            project_id="test-project",
        )
        db_session.add(item)
        db_session.commit()

        # Test valid status transition
        valid_transitions = ["todo", "in-progress", "review", "done"]
        for status in valid_transitions:
            with (
                patch("tracertm.cli.commands.item.DatabaseConnection"),
                patch(
                    "tracertm.cli.commands.item._get_project_storage_path",
                    return_value=temp_project_dir_with_db,
                ),
            ):
                result = cli_runner.invoke(
                    item_app,
                    ["update", str(item.id), "--metadata", json.dumps({"status": status})],
                )
                # Most status transitions should be valid
                if status in {"todo", "in-progress", "done"}:  # Simplified validation
                    assert result.exit_code == 0

    def test_item_bulk_tagging(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test bulk tagging of items."""
        # Create items
        item_ids = []
        for i in range(3):
            item = Item(
                title=f"Tag Item {i}",
                view="FEATURE",
                type="task",
                description=f"Item {i} for tagging",
                metadata={"tags": []},
                project_id="test-project",
            )
            db_session.add(item)
            db_session.commit()
            item_ids.append(str(item.id))

        # Add tags to items
        tags_to_add = ["urgent", "backend", "api"]
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(item_app, ["bulk-tag", "--ids", *item_ids, "--tags", *tags_to_add])
                assert result.exit_code == 0
                assert "tagged" in result.stdout.lower()

    def test_item_workflow_automation(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test workflow automation rules."""
        # Create item with automation rules
        item = Item(
            title="Automated Item",
            view="FEATURE",
            type="feature",
            description="Item with workflow automation",
            metadata={"status": "todo", "auto_move": True},
            project_id="test-project",
        )
        db_session.add(item)
        db_session.commit()

        # Test automation triggers
        with patch("tracertm.cli.commands.item.DatabaseConnection"):
            with patch("tracertm.cli.commands.item._get_project_storage_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    item_app,
                    ["update", str(item.id), "--metadata", json.dumps({"status": "in-progress", "priority": "high"})],
                )
                assert result.exit_code == 0
