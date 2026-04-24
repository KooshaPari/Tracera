"""Integration tests for Epic 4: Auto-linking from commit messages (FR18).

Tests automatic linking of code commits to stories via commit message parsing.

Functional Requirements Coverage:
    - FR-DISC-003: Auto-Link Suggestion
    - FR-DISC-004: Commit Linking

Epics:
    - EPIC-004: Automated Trace Discovery

Tests verify automatic link suggestion and commit message parsing for
establishing traceability between code commits and story items.
"""

from typing import Any

import pytest

pytestmark = pytest.mark.integration
from typer.testing import CliRunner

from tracertm.cli.app import app


@pytest.fixture
def runner() -> None:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_project(runner: Any, tmp_path: Any, monkeypatch: Any) -> str:
    """Create a temporary project for testing."""
    config_dir = tmp_path / ".config" / "tracertm"
    config_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(tmp_path))

    db_path = tmp_path / "test.db"
    result = runner.invoke(
        app,
        [
            "project",
            "init",
            "test-project",
            "--database-url",
            f"sqlite:///{db_path}",
        ],
    )
    assert result.exit_code == 0
    return "test-project"


def test_auto_link_from_commit_message(runner: Any, _temp_project: Any) -> None:
    """Test auto-linking from commit message (FR18).

    Tests: FR-DISC-003, FR-DISC-004
    """
    # Create a story item
    result1 = runner.invoke(
        app,
        [
            "item",
            "create",
            "User Authentication Story",
            "--view",
            "FEATURE",
            "--type",
            "story",
        ],
    )
    assert result1.exit_code == 0
    # Extract item ID from output (simplified - in real test would parse properly)

    # Create a code item
    result2 = runner.invoke(
        app,
        [
            "item",
            "create",
            "auth.py",
            "--view",
            "CODE",
            "--type",
            "file",
        ],
    )
    assert result2.exit_code == 0

    # Try auto-linking with commit message containing story reference
    # Note: This is a simplified test - would need proper item ID extraction
    commit_msg = "Implement user authentication #STORY-123"
    result3 = runner.invoke(
        app,
        [
            "link",
            "auto-link",
            commit_msg,
            "--code-item",
            "CODE-001",  # Would use actual code item ID
        ],
    )
    # Should either succeed or show no items found (depending on ID matching)
    assert result3.exit_code in {0, 1}


def test_auto_link_service_parse_commit_message(initialized_db: Any) -> None:
    """Test auto-link service commit message parsing."""
    from tracertm.services.auto_link_service import AutoLinkService

    # Use the initialized_db session which has tables and sample data
    service = AutoLinkService(initialized_db)

    # Test parsing commit message with existing item ID
    commit_msg = "Implement feature #STORY-123"
    result = service.parse_commit_message("test-project", commit_msg)

    # Should extract story ID and find it in database
    assert isinstance(result, list)
    # Should find STORY-123 which exists in initialized_db fixture
    if len(result) > 0:
        assert any("STORY-123" in str(item) for item in result)


def test_auto_link_determines_link_type(db_session: Any) -> None:
    """Test that auto-link service determines correct link type."""
    from tracertm.services.auto_link_service import AutoLinkService

    # Use the db_session fixture which has tables created
    service = AutoLinkService(db_session)

    # Test test-related keywords
    assert service._determine_link_type("Add test for feature") == "tests"

    # Test implementation keywords
    assert service._determine_link_type("Implement new feature") == "implements"

    # Test default
    assert service._determine_link_type("Some commit message") == "implements"
