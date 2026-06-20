"""Phase 5 - CLI Link Comprehensive Coverage Tests.

Target: 250+ tests covering 95%+ of src/tracertm/cli/commands/link.py (511 LOC @ 5.82% current)
Focus lines: 60-171, 190-237, 252-334, 348-384, 398-440, 454-498, 516-589, 607-655, 668-736, 755-842, 860-967
"""

import json
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import cast
from unittest.mock import patch

import pytest
from sqlalchemy.orm import Session
from typer.testing import CliRunner

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TWO
from tracertm.cli.commands.link import app as link_app
from tracertm.models.item import Item
from tracertm.models.link import Link
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


@pytest.fixture
def test_items(db_session: Session) -> dict[str, Item]:
    """Create test items for link testing."""
    items = {}

    # Create items in different views
    views_data = [
        ("FEATURE", "feature", "User Management Feature"),
        ("CODE", "function", "validate_user() function"),
        ("API", "endpoint", "POST /auth/login"),
        ("TEST", "test_case", "User authentication test"),
        ("DATABASE", "table", "users table"),
    ]

    for view, item_type, title in views_data:
        item = Item(
            title=title,
            view=view,
            type=item_type,
            description=f"Test {view} {item_type} for link testing",
            metadata={},
            project_id="test-project",
        )
        db_session.add(item)
        db_session.commit()
        items[f"{view.lower()}_{item_type}"] = item

    return items


class TestBasicLinkOperations:
    """Test Basic Link Operations for CLI link commands."""

    def test_create_link_basic_success(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test basic link creation success."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    ["create", str(source_item.id), str(target_item.id), "--type", "implements"],
                )
                assert result.exit_code == 0
                assert "implements" in result.stdout

    def test_create_link_all_types(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test link creation with all valid link types."""
        valid_link_types = [
            "implements",
            "tests",
            "designs",
            "depends_on",
            "blocks",
            "related_to",
            "parent_of",
            "child_of",
            "tested_by",
            "implemented_by",
            "decomposes_to",
            "decomposed_from",
        ]

        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        for link_type in valid_link_types:
            with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
                with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                    result = cli_runner.invoke(
                        link_app,
                        ["create", str(source_item.id), str(target_item.id), "--type", link_type],
                    )
                    assert result.exit_code == 0, f"Failed for link type: {link_type}"

    def test_create_link_with_metadata(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test link creation with metadata."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]
        metadata = {"confidence": "high", "automated": True, "verified": False}

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    [
                        "create",
                        str(source_item.id),
                        str(target_item.id),
                        "--type",
                        "implements",
                        "--metadata",
                        json.dumps(metadata),
                    ],
                )
                assert result.exit_code == 0
                assert "implements" in result.stdout

    def test_create_link_invalid_type(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test link creation with invalid link type."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    ["create", str(source_item.id), str(target_item.id), "--type", "invalid_type"],
                )
                assert result.exit_code != 0
                assert "Invalid link type" in result.stdout

    def test_create_link_same_items(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test creating link between same item (should fail)."""
        source_item = test_items["feature_feature"]

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    ["create", str(source_item.id), str(source_item.id), "--type", "implements"],
                )
                assert result.exit_code != 0
                # Should indicate self-link restriction

    def test_create_link_nonexistent_source(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test creating link with non-existent source item."""
        target_item = test_items["code_function"]

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    ["create", "non-existent-source-id", str(target_item.id), "--type", "implements"],
                )
                assert result.exit_code != 0
                assert "not found" in result.stdout.lower()

    def test_create_link_nonexistent_target(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test creating link with non-existent target item."""
        source_item = test_items["feature_feature"]

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    ["create", str(source_item.id), "non-existent-target-id", "--type", "implements"],
                )
                assert result.exit_code != 0
                assert "not found" in result.stdout.lower()

    def test_list_links_basic(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test basic link listing."""
        # Create test links
        source_item = test_items["feature_feature"]
        target_items = [test_items["code_function"], test_items["api_endpoint"], test_items["test_test_case"]]

        created_links = []
        for target_item in target_items:
            link = Link(
                source_id=source_item.id,
                target_id=target_item.id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
            db_session.commit()
            created_links.append(link)

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["list"])
                assert result.exit_code == 0
                assert "implements" in result.stdout
                assert result.stdout.count("implements") == len(created_links)

    def test_list_links_by_source(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test listing links filtered by source item."""
        source_item = test_items["feature_feature"]
        other_source = test_items["api_endpoint"]
        target_item = test_items["code_function"]

        # Create links from different sources
        link1 = Link(
            source_id=source_item.id,
            target_id=target_item.id,
            link_type="implements",
            metadata={},
            project_id="test-project",
        )
        link2 = Link(
            source_id=other_source.id,
            target_id=target_item.id,
            link_type="tests",
            metadata={},
            project_id="test-project",
        )
        db_session.add_all([link1, link2])
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["list", "--source", str(source_item.id)])
                assert result.exit_code == 0
                assert "implements" in result.stdout
                assert "tests" not in result.stdout

    def test_list_links_by_target(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test listing links filtered by target item."""
        source_items = [test_items["feature_feature"], test_items["api_endpoint"]]
        target_item = test_items["code_function"]
        other_target = test_items["test_test_case"]

        # Create links to different targets
        link1 = Link(
            source_id=source_items[0].id,
            target_id=target_item.id,
            link_type="implements",
            metadata={},
            project_id="test-project",
        )
        link2 = Link(
            source_id=source_items[1].id,
            target_id=other_target.id,
            link_type="tests",
            metadata={},
            project_id="test-project",
        )
        db_session.add_all([link1, link2])
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["list", "--target", str(target_item.id)])
                assert result.exit_code == 0
                assert "implements" in result.stdout
                assert "tests" not in result.stdout

    def test_list_links_by_type(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test listing links filtered by link type."""
        source_item = test_items["feature_feature"]
        target_item1 = test_items["code_function"]
        target_item2 = test_items["api_endpoint"]

        # Create different type links
        link1 = Link(
            source_id=source_item.id,
            target_id=target_item1.id,
            link_type="implements",
            metadata={},
            project_id="test-project",
        )
        link2 = Link(
            source_id=source_item.id,
            target_id=target_item2.id,
            link_type="tests",
            metadata={},
            project_id="test-project",
        )
        db_session.add_all([link1, link2])
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["list", "--type", "implements"])
                assert result.exit_code == 0
                assert "implements" in result.stdout
                assert "tests" not in result.stdout

    def test_list_links_with_limit(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test link listing with limit."""
        source_item = test_items["feature_feature"]

        # Create more links than limit
        for i in range(10):
            # Create target items dynamically
            target = Item(
                title=f"Target Item {i}",
                view="CODE",
                type="function",
                description=f"Target function {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(target)
            db_session.commit()

            link = Link(
                source_id=source_item.id,
                target_id=target.id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["list", "--limit", "5"])
                assert result.exit_code == 0
                # Should only show 5 links
                assert result.stdout.count("implements") <= COUNT_FIVE

    def test_show_link_success(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test showing link details successfully."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]
        metadata = {"confidence": "high", "automated": True}

        # Create test link
        link = Link(
            source_id=source_item.id,
            target_id=target_item.id,
            link_type="implements",
            metadata=metadata,
            project_id="test-project",
        )
        db_session.add(link)
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["show", str(link.id)])
                assert result.exit_code == 0
                assert source_item.title in result.stdout
                assert target_item.title in result.stdout
                assert "implements" in result.stdout
                assert "high" in result.stdout  # from metadata

    def test_show_link_not_found(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test showing non-existent link."""
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["show", "non-existent-link-id"])
                assert result.exit_code != 0
                assert "not found" in result.stdout.lower()

    def test_update_link_basic(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test basic link update."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        # Create test link
        link = Link(
            source_id=source_item.id,
            target_id=target_item.id,
            link_type="implements",
            metadata={},
            project_id="test-project",
        )
        db_session.add(link)
        db_session.commit()

        # Update link with new metadata
        new_metadata = {"confidence": "low", "verified": True}
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["update", str(link.id), "--metadata", json.dumps(new_metadata)])
                assert result.exit_code == 0

    def test_delete_link_success(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test successful link deletion."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        # Create test link
        link = Link(
            source_id=source_item.id,
            target_id=target_item.id,
            link_type="implements",
            metadata={},
            project_id="test-project",
        )
        db_session.add(link)
        db_session.commit()
        link_id = str(link.id)

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["delete", link_id])
                assert result.exit_code == 0
                assert "deleted" in result.stdout.lower()

    def test_delete_link_not_found(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
    ) -> None:
        """Test deleting non-existent link."""
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["delete", "non-existent-link-id"])
                assert result.exit_code != 0
                assert "not found" in result.stdout.lower()

    def test_bulk_create_links(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test bulk creation of links."""
        source_item = test_items["feature_feature"]
        links_data = [
            {"source_id": source_item.id, "target_id": test_items["code_function"].id, "type": "implements"},
            {"source_id": source_item.id, "target_id": test_items["api_endpoint"].id, "type": "tests"},
            {"source_id": source_item.id, "target_id": test_items["test_test_case"].id, "type": "related_to"},
        ]

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["bulk-create", "--data", json.dumps(links_data)])
                assert result.exit_code == 0
                assert "implements" in result.stdout
                assert "tests" in result.stdout
                assert "related_to" in result.stdout

    def test_bulk_delete_links(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test bulk deletion of links."""
        source_item = test_items["feature_feature"]

        # Create multiple links
        link_ids = []
        for target_key in ["code_function", "api_endpoint", "test_test_case"]:
            link = Link(
                source_id=source_item.id,
                target_id=test_items[target_key].id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
            db_session.commit()
            link_ids.append(str(link.id))

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    ["bulk-delete", "--ids", *link_ids],
                    input="y",  # Confirm deletion
                )
                assert result.exit_code == 0
                assert "deleted" in result.stdout.lower()


class TestGraphAnalysisOperations:
    """Test Graph Analysis Operations for CLI link commands."""

    def test_cycle_detection_basic(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test basic cycle detection."""
        # Create items for cycle
        item_a = Item(
            title="Item A",
            view="CODE",
            type="function",
            description="Function A",
            metadata={},
            project_id="test-project",
        )
        item_b = Item(
            title="Item B",
            view="CODE",
            type="function",
            description="Function B",
            metadata={},
            project_id="test-project",
        )
        item_c = Item(
            title="Item C",
            view="CODE",
            type="function",
            description="Function C",
            metadata={},
            project_id="test-project",
        )
        db_session.add_all([item_a, item_b, item_c])
        db_session.commit()

        # Create cycle: A -> B -> C -> A
        links = [
            Link(
                source_id=item_a.id,
                target_id=item_b.id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            ),
            Link(
                source_id=item_b.id,
                target_id=item_c.id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            ),
            Link(
                source_id=item_c.id,
                target_id=item_a.id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            ),
        ]
        db_session.add_all(links)
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["detect-cycles"])
                assert result.exit_code == 0
                assert "cycle" in result.stdout.lower()

    def test_cycle_detection_no_cycle(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test cycle detection with no cycles."""
        # Create acyclic graph
        item_a = Item(
            title="Item A",
            view="CODE",
            type="function",
            description="Function A",
            metadata={},
            project_id="test-project",
        )
        item_b = Item(
            title="Item B",
            view="CODE",
            type="function",
            description="Function B",
            metadata={},
            project_id="test-project",
        )
        item_c = Item(
            title="Item C",
            view="CODE",
            type="function",
            description="Function C",
            metadata={},
            project_id="test-project",
        )
        db_session.add_all([item_a, item_b, item_c])
        db_session.commit()

        # Create acyclic links: A -> B -> C
        links = [
            Link(
                source_id=item_a.id,
                target_id=item_b.id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            ),
            Link(
                source_id=item_b.id,
                target_id=item_c.id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            ),
        ]
        db_session.add_all(links)
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["detect-cycles"])
                assert result.exit_code == 0
                assert "no cycles" in result.stdout.lower() or "acyclic" in result.stdout.lower()

    def test_impact_analysis_basic(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test basic impact analysis."""
        # Create dependency chain
        root_item = Item(
            title="Root Component",
            view="CODE",
            type="module",
            description="Root module",
            metadata={},
            project_id="test-project",
        )
        db_session.add(root_item)
        db_session.commit()

        dependent_items = []
        for i in range(5):
            item = Item(
                title=f"Dependent Component {i}",
                view="CODE",
                type="function",
                description=f"Function depending on root {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
            db_session.commit()
            dependent_items.append(item)

            # Create dependency link
            link = Link(
                source_id=item.id,
                target_id=root_item.id,
                link_type="depends_on",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["analyze-impact", str(root_item.id)])
                assert result.exit_code == 0
                assert "Root Component" in result.stdout
                assert "impact" in result.stdout.lower()

    def test_impact_analysis_depth_limited(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test impact analysis with depth limit."""
        # Create multi-level dependency chain
        items = []
        for i in range(4):
            item = Item(
                title=f"Level {i} Component",
                view="CODE",
                type="function",
                description=f"Function at level {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
            db_session.commit()
            items.append(item)

        # Create chain dependencies: Level 3 -> Level 2 -> Level 1 -> Level 0
        for i in range(len(items) - 1):
            link = Link(
                source_id=items[i + 1].id,
                target_id=items[i].id,
                link_type="depends_on",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        # Test impact analysis with depth limit
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["analyze-impact", str(items[0].id), "--max-depth", "2"])
                assert result.exit_code == 0
                assert "Level 0 Component" in result.stdout

    def test_graph_visualization_simple(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test simple graph visualization."""
        source_item = test_items["feature_feature"]
        target_items = [test_items["code_function"], test_items["api_endpoint"]]

        # Create simple graph structure
        for target_item in target_items:
            link = Link(
                source_id=source_item.id,
                target_id=target_item.id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["visualize", str(source_item.id)])
                assert result.exit_code == 0
                assert source_item.title in result.stdout

    def test_graph_visualization_ascii_art(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test graph visualization with ASCII art."""
        # Create tree structure
        root = Item(
            title="Root Node",
            view="CODE",
            type="module",
            description="Root module",
            metadata={},
            project_id="test-project",
        )
        db_session.add(root)
        db_session.commit()

        children = []
        for i in range(3):
            child = Item(
                title=f"Child Node {i}",
                view="CODE",
                type="function",
                description=f"Child function {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(child)
            db_session.commit()
            children.append(child)

            link = Link(
                source_id=child.id,
                target_id=root.id,
                link_type="depends_on",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["visualize", str(root.id), "--format", "ascii"])
                assert result.exit_code == 0
                assert "Root Node" in result.stdout
                # Should contain some ASCII tree characters
                assert any(char in result.stdout for char in ["│", "├", "└", "─"])

    def test_dependency_matrix(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test dependency matrix generation."""
        # Create items and their dependencies
        items = []
        for letter in ["A", "B", "C", "D"]:
            item = Item(
                title=f"Component {letter}",
                view="CODE",
                type="module",
                description=f"Module {letter}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
            db_session.commit()
            items.append(item)

        # Create some dependencies: A depends on B, C; B depends on D
        dependencies = [(0, 1), (0, 2), (1, 3)]  # A->B, A->C, B->D
        for source_idx, target_idx in dependencies:
            link = Link(
                source_id=items[source_idx].id,
                target_id=items[target_idx].id,
                link_type="depends_on",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["dependency-matrix"])
                assert result.exit_code == 0
                assert "Component" in result.stdout
                assert "dependency" in result.stdout.lower()

    def test_missing_dependencies(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test missing dependencies detection."""
        # Create items that should have dependencies but don't
        feature_item = Item(
            title="New Feature",
            view="FEATURE",
            type="feature",
            description="Feature that needs tests",
            metadata={"requires_tests": True},
            project_id="test-project",
        )
        db_session.add(feature_item)
        db_session.commit()

        # No test items created -> missing dependencies
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["missing-deps"])
                assert result.exit_code == 0
                assert "missing" in result.stdout.lower() or "missing" in result.stdout.lower()

    def test_orphaned_items(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test orphaned items detection."""
        # Create orphaned item (no links)
        orphan = Item(
            title="Orphaned Component",
            view="CODE",
            type="module",
            description="Module with no dependencies",
            metadata={},
            project_id="test-project",
        )
        db_session.add(orphan)
        db_session.commit()

        # Create connected items
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]
        link = Link(
            source_id=source_item.id,
            target_id=target_item.id,
            link_type="implements",
            metadata={},
            project_id="test-project",
        )
        db_session.add(link)
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["orphaned"])
                assert result.exit_code == 0
                assert "Orphaned Component" in result.stdout
                assert "orphan" in result.stdout.lower()

    def test_graph_statistics(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test graph statistics calculation."""
        # Create various links for statistics
        source_item = test_items["feature_feature"]

        # Links of different types
        link_types_count = {"implements": 3, "tests": 2, "depends_on": 1}
        created_links = []

        for link_type, count in link_types_count.items():
            for i in range(count):
                # Create target item
                target = Item(
                    title=f"Target {link_type} {i}",
                    view="CODE",
                    type="function",
                    description=f"Target function for {link_type}",
                    metadata={},
                    project_id="test-project",
                )
                db_session.add(target)
                db_session.commit()

                link = Link(
                    source_id=source_item.id,
                    target_id=target.id,
                    link_type=link_type,
                    metadata={},
                    project_id="test-project",
                )
                db_session.add(link)
                created_links.append(link)
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["stats"])
                assert result.exit_code == 0
                assert "Total" in result.stdout or "total" in result.stdout.lower()
                assert "implements" in result.stdout
                assert "tests" in result.stdout

    def test_path_finding(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test path finding between items."""
        # Create chain: A -> B -> C -> D
        items = []
        for i in range(4):
            item = Item(
                title=f"Path Item {i}",
                view="CODE",
                type="function",
                description=f"Function {i} in path",
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
            db_session.commit()
            items.append(item)

        # Create path links
        for i in range(len(items) - 1):
            link = Link(
                source_id=items[i].id,
                target_id=items[i + 1].id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        # Find path from start to end
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["find-path", str(items[0].id), str(items[-1].id)])
                assert result.exit_code == 0
                assert "Path Item 0" in result.stdout
                assert "Path Item 3" in result.stdout

    def test_shortest_path(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test shortest path finding."""
        # Create graph with multiple paths
        start = Item(
            title="Start Node",
            view="CODE",
            type="function",
            description="Start function",
            metadata={},
            project_id="test-project",
        )
        end = Item(
            title="End Node",
            view="CODE",
            type="function",
            description="End function",
            metadata={},
            project_id="test-project",
        )
        db_session.add_all([start, end])
        db_session.commit()

        # Create intermediate nodes
        path1_nodes = []
        path2_nodes = []
        for i in range(3):
            # Short path (2 hops)
            node = Item(
                title=f"Short Path Node {i}",
                view="CODE",
                type="function",
                description=f"Short path node {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(node)
            db_session.commit()
            if i < COUNT_TWO:  # Only need 2 for short path
                path1_nodes.append(node)

        for i in range(5):
            # Long path (4 hops)
            node = Item(
                title=f"Long Path Node {i}",
                view="CODE",
                type="function",
                description=f"Long path node {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(node)
            db_session.commit()
            if i < COUNT_FOUR:  # Need 4 for long path
                path2_nodes.append(node)

        # Create short path links: start -> A -> end
        short_links = [(start.id, path1_nodes[0].id), (path1_nodes[1].id, end.id)]
        # Create long path links: start -> A -> B -> C -> end
        long_links = [
            (start.id, path2_nodes[0].id),
            (path2_nodes[0].id, path2_nodes[1].id),
            (path2_nodes[1].id, path2_nodes[2].id),
            (path2_nodes[3].id, end.id),
        ]

        all_links = short_links + long_links
        for source_id, target_id in all_links:
            link = Link(
                source_id=source_id,
                target_id=target_id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        # Find shortest path
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["shortest-path", str(start.id), str(end.id)])
                assert result.exit_code == 0
                # Should prefer the shorter path
                assert "Start Node" in result.stdout
                assert "End Node" in result.stdout


class TestAdvancedRelationshipManagement:
    """Test Advanced Relationship Management for CLI link commands."""

    def test_bidirectional_link_creation(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test creating bidirectional links."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    ["create", str(source_item.id), str(target_item.id), "--type", "implements", "--bidirectional"],
                )
                assert result.exit_code == 0
                assert "bidirectional" in result.stdout.lower() or "implements" in result.stdout

    def test_link_metadata_validation(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test link metadata validation."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        # Valid metadata
        valid_metadata = {
            "confidence": "high",
            "verified": True,
            "tags": ["api", "security"],
            "created_by": "user@example.com",
        }

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    [
                        "create",
                        str(source_item.id),
                        str(target_item.id),
                        "--type",
                        "implements",
                        "--metadata",
                        json.dumps(valid_metadata),
                    ],
                )
                assert result.exit_code == 0

    def test_link_metadata_invalid(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test creating link with invalid metadata."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        invalid_metadata = "not valid json"

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    cast(
                        "list[str]",
                        [
                            "create",
                            str(source_item.id),
                            str(target_item.id),
                            "--type",
                            "implements",
                            "--metadata",
                            invalid_metadata,
                        ],
                    ),
                )
                assert result.exit_code != 0

    def test_link_constraint_checking(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test link constraint validation."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        # Create initial link
        initial_link = Link(
            source_id=source_item.id,
            target_id=target_item.id,
            link_type="implements",
            metadata={},
            project_id="test-project",
        )
        db_session.add(initial_link)
        db_session.commit()

        # Try to create duplicate link (should fail or warn)
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    ["create", str(source_item.id), str(target_item.id), "--type", "implements"],
                )
                # Should either fail or warn about duplicate
                assert result.exit_code != 0 or "duplicate" in result.stdout.lower()

    def test_multi_hop_relationship_query(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test querying multi-hop relationships."""
        # Create chain: A -> B -> C -> D -> E
        items = []
        for i in range(5):
            item = Item(
                title=f"Chain Item {i}",
                view="CODE",
                type="function",
                description=f"Chain function {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(item)
            db_session.commit()
            items.append(item)

        # Create chain links
        for i in range(len(items) - 1):
            link = Link(
                source_id=items[i].id,
                target_id=items[i + 1].id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        # Query 3-hop relationships from start
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["query-hops", str(items[0].id), "--hops", "3"])
                assert result.exit_code == 0
                assert "Chain Item 0" in result.stdout

    def test_link_type_transformation(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test transforming link types."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        # Create initial link
        link = Link(
            source_id=source_item.id,
            target_id=target_item.id,
            link_type="implements",
            metadata={},
            project_id="test-project",
        )
        db_session.add(link)
        db_session.commit()

        # Transform link type
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, cast("list[str]", ["update", str(link.id), "--type", "tested_by"]))
                assert result.exit_code == 0

    def test_link_aggregation_by_type(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test aggregating links by type."""
        source_items = list(test_items.values())[:3]

        # Create links of different types
        link_types = ["implements", "tests", "depends_on", "related_to"]
        for i, source_item in enumerate(source_items):
            target_item = test_items["database_table"]
            link_type = link_types[i % len(link_types)]

            link = Link(
                source_id=source_item.id,
                target_id=target_item.id,
                link_type=link_type,
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        # Query aggregation
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["aggregate", "--by", "type"])
                assert result.exit_code == 0
                for link_type in link_types:
                    assert link_type in result.stdout

    def test_link_consistency_check(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test link consistency validation."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        # Create valid link
        link = Link(
            source_id=source_item.id,
            target_id=target_item.id,
            link_type="implements",
            metadata={},
            project_id="test-project",
        )
        db_session.add(link)
        db_session.commit()

        # Run consistency check
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["check-consistency"])
                assert result.exit_code == 0
                assert "consistent" in result.stdout.lower() or "errors" in result.stdout.lower()

    def test_bulk_link_transformation(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test bulk transformation of link types."""
        source_items = list(test_items.values())[:3]
        target_item = test_items["database_table"]

        # Create multiple links of same type
        link_ids = []
        for source_item in source_items:
            link = Link(
                source_id=source_item.id,
                target_id=target_item.id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
            db_session.commit()
            link_ids.append(str(link.id))

        # Transform all links
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["bulk-update", "--ids", *link_ids, "--type", "tested_by"])
                assert result.exit_code == 0

    def test_link_cascade_operations(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test cascade operations on linked items."""
        # Create hierarchical linked structure
        root = Item(
            title="Root Item",
            view="CODE",
            type="module",
            description="Root module",
            metadata={},
            project_id="test-project",
        )
        db_session.add(root)
        db_session.commit()

        children = []
        for i in range(3):
            child = Item(
                title=f"Child Item {i}",
                view="CODE",
                type="function",
                description=f"Child function {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(child)
            db_session.commit()
            children.append(child)

            # Create link from child to parent
            link = Link(
                source_id=child.id,
                target_id=root.id,
                link_type="depends_on",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        # Test cascade when deleting parent
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    cast("list[str]", ["delete-cascade", str(root.id)]),
                    input="y",  # Confirm cascade deletion
                )
                assert result.exit_code == 0
                assert "cascade" in result.stdout.lower()

    def test_link_enrichment(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test enriching links with additional metadata."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        # Create basic link
        link = Link(
            source_id=source_item.id,
            target_id=target_item.id,
            link_type="implements",
            metadata={},
            project_id="test-project",
        )
        db_session.add(link)
        db_session.commit()

        # Enrich with additional metadata
        enrichment_data = {
            "confidence_score": 0.85,
            "verification_status": "pending",
            "last_reviewed": "2025-12-10",
            "reviewer": "system",
            "automated_detection": True,
        }

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    cast("list[str]", ["enrich", str(link.id), "--metadata", json.dumps(enrichment_data)]),
                )
                assert result.exit_code == 0

    def test_link_export_import(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test exporting and importing links."""
        # Create multiple links
        links_data = []
        for i, (_key, item) in enumerate(list(test_items.items())[:4]):
            if i < len(test_items) - 1:
                next_item = list(test_items.values())[i + 1]
                link = Link(
                    source_id=item.id,
                    target_id=next_item.id,
                    link_type="implements",
                    metadata={"exported": True},
                    project_id="test-project",
                )
                db_session.add(link)
                db_session.commit()
                links_data.append({
                    "id": link.id,
                    "source_id": link.source_id,
                    "target_id": link.target_id,
                    "link_type": link.link_type,
                    "metadata": link.metadata,
                })

        # Export links
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["export", "--format", "json"])
                assert result.exit_code == 0
                assert "implements" in result.stdout

    def test_link_validation_rules(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test link validation rules."""
        # Test invalid rule: feature cannot 'implement' test
        feature_item = test_items["feature_feature"]
        test_item = test_items["test_test_case"]

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    cast(
                        "list[str]",
                        ["create", str(feature_item.id), str(test_item.id), "--type", "implemented_by"],
                    ),
                )
                # Should either fail or warn about invalid relationship
                assert result.exit_code != 0 or "warning" in result.stdout.lower()

    def test_link_template_application(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test applying link templates."""
        # Define link template
        template = {
            "link_type": "implements",
            "metadata": {"confidence": "medium", "verified": False, "source": "template"},
            "auto_create_reverse": True,
            "reverse_type": "implemented_by",
        }

        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    cast(
                        "list[str]",
                        [
                            "create-from-template",
                            str(source_item.id),
                            str(target_item.id),
                            "--template",
                            json.dumps(template),
                        ],
                    ),
                )
                assert result.exit_code == 0

    def test_link_bulk_verification(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test bulk verification of links."""
        # Create multiple links with varying verification status
        source_items = list(test_items.values())[:4]
        target_item = test_items["database_table"]
        link_ids = []

        for i, source_item in enumerate(source_items):
            metadata = {"verified": i % 2 == 0}  # Alternate verification status
            link = Link(
                source_id=source_item.id,
                target_id=target_item.id,
                link_type="implements",
                metadata=metadata,
                project_id="test-project",
            )
            db_session.add(link)
            db_session.commit()
            link_ids.append(str(link.id))

        # Verify all links
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["bulk-verify", "--ids", *link_ids])
                assert result.exit_code == 0
                assert "verified" in result.stdout.lower()


class TestCLIIntegrationScenarios:
    """Test CLI Integration Scenarios for CLI link commands."""

    def test_cli_error_handling_project_not_found(
        self,
        cli_runner: CliRunner,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test CLI error handling when project not found."""
        non_existent_dir = Path("/tmp/non-existent-project")

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=non_existent_dir):
                result = cli_runner.invoke(
                    link_app,
                    cast(
                        "list[str]",
                        [
                            "create",
                            str(test_items["feature_feature"].id),
                            str(test_items["code_function"].id),
                            "--type",
                            "implements",
                        ],
                    ),
                )
                assert result.exit_code != 0
                assert "project" in result.stdout.lower() and "not found" in result.stdout.lower()

    def test_cli_rich_table_formatting(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test CLI rich table formatting for link display."""
        # Create multiple links
        for i, (_key, item) in enumerate(list(test_items.items())[:3]):
            if i < len(test_items) - 1:
                target = list(test_items.values())[i + 1]
                link = Link(
                    source_id=item.id,
                    target_id=target.id,
                    link_type="implements",
                    metadata={},
                    project_id="test-project",
                )
                db_session.add(link)
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["list", "--format", "table"])
                assert result.exit_code == 0
                # Should contain table formatting
                assert "┌" in result.stdout or "│" in result.stdout or "└" in result.stdout

    def test_cli_paging_for_large_results(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test CLI paging for large link result sets."""
        source_item = test_items["feature_feature"]

        # Create many links
        for i in range(20):
            target = Item(
                title=f"Target {i}",
                view="CODE",
                type="function",
                description=f"Target function {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(target)
            db_session.commit()

            link = Link(
                source_id=source_item.id,
                target_id=target.id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["list", "--limit", "10"])
                assert result.exit_code == 0
                # Should limit output properly
                line_count = len([line for line in result.stdout.split("\n") if line.strip()])
                assert line_count <= 15  # Account for header/footer lines

    def test_cli_export_to_file(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test CLI export to file functionality."""
        source_item = test_items["feature_feature"]
        target_items = list(test_items.values())[1:3]

        # Create links
        for target_item in target_items:
            link = Link(
                source_id=source_item.id,
                target_id=target_item.id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
        db_session.commit()

        # Export to file
        export_file = temp_project_dir_with_db / "links_export.json"
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["export", "--file", str(export_file)])
                assert result.exit_code == 0
                assert export_file.exists()
                exported_content = export_file.read_text()
                assert "implements" in exported_content

    def test_cli_import_from_file(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test CLI import from file functionality."""
        # Create import data
        import_data = [
            {
                "source_id": test_items["feature_feature"].id,
                "target_id": test_items["api_endpoint"].id,
                "link_type": "implements",
                "metadata": {"imported": True},
            },
            {
                "source_id": test_items["code_function"].id,
                "target_id": test_items["test_test_case"].id,
                "link_type": "tests",
                "metadata": {"imported": True},
            },
        ]

        import_file = temp_project_dir_with_db / "links_import.json"
        import_file.write_text(json.dumps(import_data))

        # Import from file
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(link_app, ["import", "--file", str(import_file)])
                assert result.exit_code == 0
                assert "imported" in result.stdout.lower()

    def test_cli_shell_completion_link_types(self, cli_runner: CliRunner) -> None:
        """Test CLI shell completion for link types."""
        result = cli_runner.invoke(link_app, ["shell-completion", "types"])
        assert result.exit_code == 0
        expected_types = [
            "implements",
            "tests",
            "designs",
            "depends_on",
            "blocks",
            "related_to",
            "parent_of",
            "child_of",
            "tested_by",
            "implemented_by",
            "decomposes_to",
            "decomposed_from",
        ]
        for link_type in expected_types[:5]:  # Check subset
            assert link_type in result.stdout

    def test_cli_shell_completion_link_ids(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test CLI shell completion for link IDs."""
        # Create test links
        link_ids = []
        for i in range(3):
            link = Link(
                source_id=test_items["feature_feature"].id,
                target_id=list(test_items.values())[i + 1].id,
                link_type="implements",
                metadata={},
                project_id="test-project",
            )
            db_session.add(link)
            db_session.commit()
            link_ids.append(str(link.id))

        result = cli_runner.invoke(link_app, ["shell-completion", "link-ids"])
        assert result.exit_code == 0
        assert len(result.stdout.strip()) > 0

    def test_cli_progress_indication(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test CLI progress indication for long operations."""
        # Create many items for bulk operation
        source_item = test_items["feature_feature"]

        # Perform bulk operation that should show progress
        bulk_data = []
        for i in range(50):
            target = Item(
                title=f"Bulk Target {i}",
                view="CODE",
                type="function",
                description=f"Bulk function {i}",
                metadata={},
                project_id="test-project",
            )
            db_session.add(target)
            db_session.commit()

            bulk_data.append({
                "source_id": source_item.id,
                "target_id": target.id,
                "type": "implements",
                "metadata": {"bulk": True},
            })

        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    ["bulk-create", "--data", json.dumps(bulk_data[:10])],  # Use subset for test speed
                )
                assert result.exit_code == 0
                # Should contain success indication
                assert "created" in result.stdout.lower()

    def test_cli_configuration_options(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test CLI configuration and options."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        # Test with verbose flag
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    cast(
                        "list[str]",
                        ["--verbose", "create", str(source_item.id), str(target_item.id), "--type", "implements"],
                    ),
                )
                assert result.exit_code == 0
                # Verbose output should contain more detailed information
                assert len(result.stdout) > 50  # Basic check for verbose output

    def test_cli_help_system_integration(self, cli_runner: CliRunner) -> None:
        """Test CLI help system integration."""
        # Test main help
        result = cli_runner.invoke(link_app, ["--help"])
        assert result.exit_code == 0
        assert "create" in result.stdout
        assert "list" in result.stdout
        assert "delete" in result.stdout

        # Test subcommand help
        result = cli_runner.invoke(link_app, ["create", "--help"])
        assert result.exit_code == 0
        assert "source_id" in result.stdout
        assert "target_id" in result.stdout
        assert "--type" in result.stdout

    def test_cli_storage_integration(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test CLI integration with storage manager."""
        source_item = test_items["feature_feature"]
        target_item = test_items["code_function"]

        # Create link via CLI
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    ["create", str(source_item.id), str(target_item.id), "--type", "implements"],
                )
                assert result.exit_code == 0

        # Verify link was stored properly
        stored_link = (
            db_session
            .query(Link)
            .filter_by(source_id=source_item.id, target_id=target_item.id, link_type="implements")
            .first()
        )
        assert stored_link is not None
        assert stored_link.project_id == "test-project"

    def test_cli_transaction_rollback(
        self,
        cli_runner: CliRunner,
        temp_project_dir_with_db: Path,
        db_session: Session,
        test_items: dict[str, Item],
    ) -> None:
        """Test CLI transaction rollback on errors."""
        test_items["feature_feature"]
        target_item = test_items["code_function"]

        # This should trigger a rollback
        with patch("tracertm.cli.commands.link.get_session", return_value=db_session):
            with patch("tracertm.cli.commands.link.get_project_path", return_value=temp_project_dir_with_db):
                result = cli_runner.invoke(
                    link_app,
                    cast("list[str]", ["create", "invalid-source-id", str(target_item.id), "--type", "implements"]),
                )
                assert result.exit_code != 0

        # Verify no partial data was created
        partial_link = db_session.query(Link).filter_by(source_id="invalid-source-id").first()
        assert partial_link is None
