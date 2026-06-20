"""Integration tests for advanced services batch 3.

Tests GitHub import, impact analysis, traceability matrix, query optimization,
and security compliance services with real database interactions.

Coverage Targets:
- github_import_service.py: 0% -> 80%+
- impact_analysis_service.py: 0% -> 80%+
- traceability_matrix_service.py: 14.88% -> 80%+
- query_optimization_service.py: 17.20% -> 80%+
- security_compliance_service.py: 28.07% -> 80%+
"""

import csv
import json
import logging
from datetime import datetime
from io import StringIO

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models.item import Item
from tracertm.models.project import Project
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository
from tracertm.services.github_import_service import GitHubImportService
from tracertm.services.impact_analysis_service import (
    ImpactAnalysisResult,
    ImpactAnalysisService,
)
from tracertm.services.query_optimization_service import QueryOptimizationService
from tracertm.services.security_compliance_service import SecurityComplianceService
from tracertm.services.traceability_matrix_service import (
    TraceabilityMatrix,
    TraceabilityMatrixService,
)

logger = logging.getLogger(__name__)


# ============================================================
# FIXTURES
# ============================================================


@pytest_asyncio.fixture
async def test_project(db_session: AsyncSession) -> Project:
    """Create a test project."""
    project = Project(
        name=f"Advanced Services Test {datetime.now().timestamp()}",
        description="Project for advanced services testing",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest_asyncio.fixture
async def complex_item_hierarchy(db_session: AsyncSession, test_project: Project) -> dict[str, Item]:
    """Create complex item hierarchy for impact analysis testing.

    Structure:
        Root (FEATURE)
        ├── Child1 (CODE)
        │   ├── Grandchild1 (TEST)
        │   └── Grandchild2 (TEST)
        ├── Child2 (CODE)
        │   └── Grandchild3 (API)
        └── Child3 (API)
            └── Grandchild4 (DOC)
    """
    items_repo = ItemRepository(db_session)
    links_repo = LinkRepository(db_session)

    # Create items
    root = await items_repo.create(
        project_id=str(test_project.id),
        title="Root Feature",
        view="FEATURE",
        item_type="feature",
        status="in_progress",
        priority="high",
    )

    child1 = await items_repo.create(
        project_id=str(test_project.id),
        title="Child1 Implementation",
        view="CODE",
        item_type="class",
        status="done",
    )

    child2 = await items_repo.create(
        project_id=str(test_project.id),
        title="Child2 Implementation",
        view="CODE",
        item_type="function",
        status="in_progress",
    )

    child3 = await items_repo.create(
        project_id=str(test_project.id),
        title="Child3 API",
        view="API",
        item_type="endpoint",
        status="todo",
    )

    grandchild1 = await items_repo.create(
        project_id=str(test_project.id),
        title="Unit Test 1",
        view="TEST",
        item_type="unit_test",
        status="done",
    )

    grandchild2 = await items_repo.create(
        project_id=str(test_project.id),
        title="Unit Test 2",
        view="TEST",
        item_type="unit_test",
        status="todo",
    )

    grandchild3 = await items_repo.create(
        project_id=str(test_project.id),
        title="API Endpoint",
        view="API",
        item_type="endpoint",
        status="in_progress",
    )

    grandchild4 = await items_repo.create(
        project_id=str(test_project.id),
        title="Documentation",
        view="DOC",
        item_type="guide",
        status="todo",
    )

    # Create links
    await links_repo.create(
        project_id=str(test_project.id),
        source_item_id=str(root.id),
        target_item_id=str(child1.id),
        link_type="implements",
    )

    await links_repo.create(
        project_id=str(test_project.id),
        source_item_id=str(root.id),
        target_item_id=str(child2.id),
        link_type="implements",
    )

    await links_repo.create(
        project_id=str(test_project.id),
        source_item_id=str(root.id),
        target_item_id=str(child3.id),
        link_type="exposes",
    )

    await links_repo.create(
        project_id=str(test_project.id),
        source_item_id=str(child1.id),
        target_item_id=str(grandchild1.id),
        link_type="tested_by",
    )

    await links_repo.create(
        project_id=str(test_project.id),
        source_item_id=str(child1.id),
        target_item_id=str(grandchild2.id),
        link_type="tested_by",
    )

    await links_repo.create(
        project_id=str(test_project.id),
        source_item_id=str(child2.id),
        target_item_id=str(grandchild3.id),
        link_type="exposes",
    )

    await links_repo.create(
        project_id=str(test_project.id),
        source_item_id=str(child3.id),
        target_item_id=str(grandchild4.id),
        link_type="documented_by",
    )

    await db_session.commit()

    return {
        "root": root,
        "child1": child1,
        "child2": child2,
        "child3": child3,
        "grandchild1": grandchild1,
        "grandchild2": grandchild2,
        "grandchild3": grandchild3,
        "grandchild4": grandchild4,
    }


@pytest_asyncio.fixture
async def traceability_test_items(db_session: AsyncSession, test_project: Project) -> dict[str, list[Item]]:
    """Create items for traceability matrix testing."""
    items_repo = ItemRepository(db_session)
    links_repo = LinkRepository(db_session)

    # Create source items (FEATURE view)
    sources = []
    for i in range(3):
        item = await items_repo.create(
            project_id=str(test_project.id),
            title=f"Feature {i + 1}",
            view="FEATURE",
            item_type="feature",
            status="in_progress",
        )
        sources.append(item)

    # Create target items (CODE view)
    targets = []
    for i in range(4):
        item = await items_repo.create(
            project_id=str(test_project.id),
            title=f"Code Class {i + 1}",
            view="CODE",
            item_type="class",
            status="done",
        )
        targets.append(item)

    # Create links (not all combinations for testing coverage)
    # Feature 1 -> Code 1, Code 2
    await links_repo.create(
        project_id=str(test_project.id),
        source_item_id=str(sources[0].id),
        target_item_id=str(targets[0].id),
        link_type="implements",
    )
    await links_repo.create(
        project_id=str(test_project.id),
        source_item_id=str(sources[0].id),
        target_item_id=str(targets[1].id),
        link_type="implements",
    )

    # Feature 2 -> Code 3
    await links_repo.create(
        project_id=str(test_project.id),
        source_item_id=str(sources[1].id),
        target_item_id=str(targets[2].id),
        link_type="implements",
    )

    # Feature 3 -> No links (uncovered)
    # Code 4 -> No links (uncovered)

    await db_session.commit()

    return {"sources": sources, "targets": targets}


# ============================================================
# GITHUB IMPORT SERVICE TESTS (15 tests)
# ============================================================


class TestGitHubImportService:
    """Integration tests for GitHubImportService."""

    # ========== Validation Tests ==========

    @pytest.mark.asyncio
    async def test_validate_valid_github_export_with_items(self, db_session: AsyncSession) -> None:
        """Test validation of valid GitHub export with items field."""
        service = GitHubImportService(db_session)

        valid_json = json.dumps({
            "items": [
                {
                    "id": 1,
                    "title": "Test Issue",
                    "body": "Description",
                    "state": "open",
                    "type": "issue",
                },
            ],
        })

        errors = await service.validate_github_export(valid_json)

        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_valid_github_export_with_issues(self, db_session: AsyncSession) -> None:
        """Test validation of valid GitHub export with issues field."""
        service = GitHubImportService(db_session)

        valid_json = json.dumps({
            "issues": [
                {
                    "id": 1,
                    "number": 123,
                    "title": "Bug Report",
                    "body": "Found a bug",
                    "state": "closed",
                },
            ],
        })

        errors = await service.validate_github_export(valid_json)

        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_invalid_json(self, db_session: AsyncSession) -> None:
        """Test validation of invalid JSON."""
        service = GitHubImportService(db_session)

        invalid_json = "{ invalid json }"

        errors = await service.validate_github_export(invalid_json)

        assert len(errors) == 1
        assert "Invalid JSON" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_missing_required_fields(self, db_session: AsyncSession) -> None:
        """Test validation of JSON missing required fields."""
        service = GitHubImportService(db_session)

        invalid_json = json.dumps({"some_field": "value"})

        errors = await service.validate_github_export(invalid_json)

        assert len(errors) == 1
        assert "Missing 'items' or 'issues'" in errors[0]

    # ========== Import Tests ==========

    @pytest.mark.asyncio
    async def test_import_github_project_with_issues(self, db_session: AsyncSession) -> None:
        """Test importing GitHub project with issues."""
        service = GitHubImportService(db_session)

        github_data = {
            "issues": [
                {
                    "id": 101,
                    "number": 1,
                    "title": "Add user authentication",
                    "body": "Implement OAuth2 authentication",
                    "state": "open",
                    "type": "issue",
                    "url": "https://github.com/test/repo/issues/1",
                },
                {
                    "id": 102,
                    "number": 2,
                    "title": "Fix login bug",
                    "body": "Login fails on Safari",
                    "state": "closed",
                    "type": "issue",
                    "url": "https://github.com/test/repo/issues/2",
                },
            ],
        }

        result = await service.import_github_project(
            project_name="GitHub Test Project",
            json_data=json.dumps(github_data),
            agent_id="test-agent",
        )

        assert result["success"] is True
        assert result["items_imported"] == COUNT_TWO
        assert result["links_imported"] == 0
        assert "project_id" in result

        # Verify project created
        projects_repo = ProjectRepository(db_session)
        project = await projects_repo.get_by_id(result["project_id"])
        assert project is not None
        assert project.name == "GitHub Test Project"
        assert project.description == "Imported from GitHub"

        # Verify items created
        items_repo = ItemRepository(db_session)
        items = await items_repo.get_by_project(str(project.id))
        assert len(items) == COUNT_TWO

        # Check first item
        item1 = next(i for i in items if i.title == "Add user authentication")
        assert item1.view == "FEATURE"
        assert item1.item_type == "task"
        assert item1.status == "todo"
        assert item1.metadata["github_number"] == 1
        assert item1.metadata["github_id"] == 101

        # Check second item
        item2 = next(i for i in items if i.title == "Fix login bug")
        assert item2.status == "complete"

    @pytest.mark.asyncio
    async def test_import_github_project_with_items_field(self, db_session: AsyncSession) -> None:
        """Test importing GitHub project with items field."""
        service = GitHubImportService(db_session)

        github_data = {
            "items": [
                {
                    "id": 201,
                    "number": 10,
                    "title": "Feature Request",
                    "body": "Add dark mode",
                    "state": "in_progress",
                },
            ],
        }

        result = await service.import_github_project(
            project_name="Items Test",
            json_data=json.dumps(github_data),
        )

        assert result["success"] is True
        assert result["items_imported"] == 1

    @pytest.mark.asyncio
    async def test_import_with_pull_requests(self, db_session: AsyncSession) -> None:
        """Test importing pull requests and related issues."""
        service = GitHubImportService(db_session)

        github_data = {
            "issues": [
                {
                    "id": 301,
                    "number": 1,
                    "title": "Issue to fix",
                    "body": "Bug description",
                    "state": "open",
                    "type": "issue",
                },
                {
                    "id": 302,
                    "number": 2,
                    "title": "Fix for issue #1",
                    "body": "PR description",
                    "state": "in review",
                    "type": "pull_request",
                    "related_issues": [301],  # Links to issue 1
                },
            ],
        }

        result = await service.import_github_project(
            project_name="PR Test",
            json_data=json.dumps(github_data),
        )

        assert result["success"] is True
        assert result["items_imported"] == COUNT_TWO
        assert result["links_imported"] == 1

        # Verify link created
        links_repo = LinkRepository(db_session)
        links = await links_repo.get_by_project(result["project_id"])
        assert len(links) == 1
        assert links[0].link_type == "implements"

    @pytest.mark.asyncio
    async def test_import_with_validation_error(self, db_session: AsyncSession) -> None:
        """Test import fails with validation errors."""
        service = GitHubImportService(db_session)

        invalid_json = "{ invalid }"

        result = await service.import_github_project(
            project_name="Invalid Import",
            json_data=invalid_json,
        )

        assert result["success"] is False
        assert len(result["errors"]) > 0
        assert "Invalid JSON" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_import_status_mapping(self, db_session: AsyncSession) -> None:
        """Test GitHub status to TraceRTM status mapping."""
        service = GitHubImportService(db_session)

        github_data = {
            "issues": [
                {"id": 1, "title": "Open", "state": "open", "type": "issue"},
                {"id": 2, "title": "In Progress", "state": "in_progress", "type": "issue"},
                {"id": 3, "title": "Closed", "state": "closed", "type": "issue"},
                {"id": 4, "title": "Done", "state": "done", "type": "issue"},
            ],
        }

        result = await service.import_github_project(
            project_name="Status Mapping Test",
            json_data=json.dumps(github_data),
        )

        assert result["success"] is True

        items_repo = ItemRepository(db_session)
        items = await items_repo.get_by_project(result["project_id"])

        statuses = {item.title: item.status for item in items}
        assert statuses["Open"] == "todo"
        assert statuses["In Progress"] == "in_progress"
        assert statuses["Closed"] == "complete"
        assert statuses["Done"] == "complete"

    @pytest.mark.asyncio
    async def test_import_type_mapping(self, db_session: AsyncSession) -> None:
        """Test GitHub type to TraceRTM type mapping."""
        service = GitHubImportService(db_session)

        github_data = {
            "issues": [
                {"id": 1, "title": "Issue", "state": "open", "type": "issue"},
                {"id": 2, "title": "PR", "state": "open", "type": "pull_request"},
                {"id": 3, "title": "Discussion", "state": "open", "type": "discussion"},
            ],
        }

        result = await service.import_github_project(
            project_name="Type Mapping Test",
            json_data=json.dumps(github_data),
        )

        assert result["success"] is True

        items_repo = ItemRepository(db_session)
        items = await items_repo.get_by_project(result["project_id"])

        for item in items:
            assert item.item_type == "task"

    @pytest.mark.asyncio
    async def test_import_creates_events(self, db_session: AsyncSession) -> None:
        """Test that import creates event log entries."""
        service = GitHubImportService(db_session)

        github_data = {
            "issues": [
                {
                    "id": 501,
                    "number": 100,
                    "title": "Event Test Issue",
                    "state": "open",
                    "type": "issue",
                },
            ],
        }

        result = await service.import_github_project(
            project_name="Event Test",
            json_data=json.dumps(github_data),
            agent_id="event-test-agent",
        )

        assert result["success"] is True

        # Verify events created
        events_repo = EventRepository(db_session)
        events = await events_repo.get_by_project(result["project_id"])

        import_events = [e for e in events if e.event_type == "github_item_imported"]
        assert len(import_events) == 1
        assert import_events[0].agent_id == "event-test-agent"
        assert import_events[0].data["github_number"] == 100

    @pytest.mark.asyncio
    async def test_import_with_missing_optional_fields(self, db_session: AsyncSession) -> None:
        """Test import handles missing optional fields gracefully."""
        service = GitHubImportService(db_session)

        github_data = {
            "issues": [
                {
                    # Missing id, number, url, body
                    "title": "Minimal Issue",
                    "state": "open",
                },
            ],
        }

        result = await service.import_github_project(
            project_name="Minimal Test",
            json_data=json.dumps(github_data),
        )

        assert result["success"] is True
        assert result["items_imported"] == 1

        items_repo = ItemRepository(db_session)
        items = await items_repo.get_by_project(result["project_id"])
        assert len(items) == 1
        assert items[0].title == "Minimal Issue"
        assert items[0].description == ""

    @pytest.mark.asyncio
    async def test_import_with_partial_link_failures(self, db_session: AsyncSession) -> None:
        """Test import continues if some links fail to create."""
        service = GitHubImportService(db_session)

        github_data = {
            "issues": [
                {
                    "id": 601,
                    "number": 1,
                    "title": "PR with bad link",
                    "state": "open",
                    "type": "pull_request",
                    "related_issues": [999],  # Non-existent issue
                },
            ],
        }

        result = await service.import_github_project(
            project_name="Bad Link Test",
            json_data=json.dumps(github_data),
        )

        # Should succeed even if link fails
        assert result["success"] is True
        assert result["items_imported"] == 1
        assert result["links_imported"] == 0

    @pytest.mark.asyncio
    async def test_import_default_agent_id(self, db_session: AsyncSession) -> None:
        """Test import uses default agent_id when not specified."""
        service = GitHubImportService(db_session)

        github_data = {"issues": [{"id": 701, "title": "Default Agent", "state": "open"}]}

        result = await service.import_github_project(
            project_name="Default Agent Test",
            json_data=json.dumps(github_data),
        )

        assert result["success"] is True

        events_repo = EventRepository(db_session)
        events = await events_repo.get_by_project(result["project_id"])

        # Should use "system" as default
        assert all(e.agent_id == "system" for e in events)


# ============================================================
# IMPACT ANALYSIS SERVICE TESTS (15 tests)
# ============================================================


class TestImpactAnalysisService:
    """Integration tests for ImpactAnalysisService."""

    # ========== Forward Impact Analysis Tests ==========

    @pytest.mark.asyncio
    async def test_analyze_impact_simple_hierarchy(
        self, db_session: AsyncSession, complex_item_hierarchy: dict
    ) -> None:
        """Test impact analysis on simple hierarchy."""
        service = ImpactAnalysisService(db_session)

        root = complex_item_hierarchy["root"]

        result = await service.analyze_impact(str(root.id))

        assert isinstance(result, ImpactAnalysisResult)
        assert result.root_item_id == str(root.id)
        assert result.root_item_title == "Root Feature"
        assert result.total_affected == 7  # All children and grandchildren
        assert result.max_depth_reached == COUNT_TWO

    @pytest.mark.asyncio
    async def test_analyze_impact_depth_distribution(
        self, db_session: AsyncSession, complex_item_hierarchy: dict
    ) -> None:
        """Test impact analysis calculates correct depth distribution."""
        service = ImpactAnalysisService(db_session)

        root = complex_item_hierarchy["root"]

        result = await service.analyze_impact(str(root.id))

        # Depth 1: child1, child2, child3 (3 items)
        assert result.affected_by_depth[1] == COUNT_THREE

        # Depth 2: grandchild1, grandchild2, grandchild3, grandchild4 (4 items)
        assert result.affected_by_depth[2] == COUNT_FOUR

    @pytest.mark.asyncio
    async def test_analyze_impact_view_distribution(
        self, db_session: AsyncSession, complex_item_hierarchy: dict
    ) -> None:
        """Test impact analysis calculates correct view distribution."""
        service = ImpactAnalysisService(db_session)

        root = complex_item_hierarchy["root"]

        result = await service.analyze_impact(str(root.id))

        assert result.affected_by_view["CODE"] == COUNT_TWO  # child1, child2
        assert result.affected_by_view["API"] == COUNT_TWO  # child3, grandchild3
        assert result.affected_by_view["TEST"] == COUNT_TWO  # grandchild1, grandchild2
        assert result.affected_by_view["DOC"] == 1  # grandchild4

    @pytest.mark.asyncio
    async def test_analyze_impact_with_max_depth_limit(
        self, db_session: AsyncSession, complex_item_hierarchy: dict
    ) -> None:
        """Test impact analysis respects max_depth parameter."""
        service = ImpactAnalysisService(db_session)

        root = complex_item_hierarchy["root"]

        result = await service.analyze_impact(str(root.id), max_depth=1)

        # Should only get depth 1 items (children)
        assert result.total_affected == COUNT_THREE
        assert result.max_depth_reached == 1
        assert 2 not in result.affected_by_depth

    @pytest.mark.asyncio
    async def test_analyze_impact_with_link_type_filter(
        self, db_session: AsyncSession, complex_item_hierarchy: dict
    ) -> None:
        """Test impact analysis filters by link types."""
        service = ImpactAnalysisService(db_session)

        root = complex_item_hierarchy["root"]

        # Only follow "implements" links
        result = await service.analyze_impact(str(root.id), link_types=["implements"])

        # Should get child1, child2, and their descendants
        # But NOT child3 (exposes link)
        affected_titles = {item["title"] for item in result.affected_items}
        assert "Child1 Implementation" in affected_titles
        assert "Child2 Implementation" in affected_titles
        assert "Child3 API" not in affected_titles

    @pytest.mark.asyncio
    async def test_analyze_impact_critical_paths(self, db_session: AsyncSession, complex_item_hierarchy: dict) -> None:
        """Test impact analysis identifies critical paths to leaf nodes."""
        service = ImpactAnalysisService(db_session)

        root = complex_item_hierarchy["root"]

        result = await service.analyze_impact(str(root.id))

        # Should have 4 critical paths (to each grandchild)
        assert len(result.critical_paths) == COUNT_FOUR

        # Each path should have 3 items (root -> child -> grandchild)
        for path in result.critical_paths:
            assert len(path) == COUNT_THREE
            assert path[0] == str(root.id)

    @pytest.mark.asyncio
    async def test_analyze_impact_with_nonexistent_item(self, db_session: AsyncSession) -> None:
        """Test impact analysis raises error for nonexistent item."""
        service = ImpactAnalysisService(db_session)

        with pytest.raises(ValueError, match="Item .* not found"):
            await service.analyze_impact("nonexistent-id")

    @pytest.mark.asyncio
    async def test_analyze_impact_leaf_node(self, db_session: AsyncSession, complex_item_hierarchy: dict) -> None:
        """Test impact analysis on leaf node returns empty result."""
        service = ImpactAnalysisService(db_session)

        leaf = complex_item_hierarchy["grandchild1"]

        result = await service.analyze_impact(str(leaf.id))

        # Leaf node has no downstream dependencies
        assert result.total_affected == 0
        assert result.max_depth_reached == 0
        assert len(result.critical_paths) == 0

    # ========== Reverse Impact Analysis Tests ==========

    @pytest.mark.asyncio
    async def test_analyze_reverse_impact_simple(self, db_session: AsyncSession, complex_item_hierarchy: dict) -> None:
        """Test reverse impact analysis finds upstream dependencies."""
        service = ImpactAnalysisService(db_session)

        grandchild1 = complex_item_hierarchy["grandchild1"]

        result = await service.analyze_reverse_impact(str(grandchild1.id))

        # Should find child1 and root
        assert result.total_affected == COUNT_TWO
        assert result.max_depth_reached == COUNT_TWO

        affected_titles = {item["title"] for item in result.affected_items}
        assert "Child1 Implementation" in affected_titles
        assert "Root Feature" in affected_titles

    @pytest.mark.asyncio
    async def test_analyze_reverse_impact_root_node(
        self, db_session: AsyncSession, complex_item_hierarchy: dict
    ) -> None:
        """Test reverse impact on root node returns empty."""
        service = ImpactAnalysisService(db_session)

        root = complex_item_hierarchy["root"]

        result = await service.analyze_reverse_impact(str(root.id))

        # Root has no upstream dependencies
        assert result.total_affected == 0
        assert result.max_depth_reached == 0

    @pytest.mark.asyncio
    async def test_analyze_reverse_impact_depth_distribution(
        self,
        db_session: AsyncSession,
        complex_item_hierarchy: dict,
    ) -> None:
        """Test reverse impact calculates correct depth distribution."""
        service = ImpactAnalysisService(db_session)

        grandchild3 = complex_item_hierarchy["grandchild3"]

        result = await service.analyze_reverse_impact(str(grandchild3.id))

        # Depth 1: child2
        # Depth 2: root
        assert result.affected_by_depth[1] == 1
        assert result.affected_by_depth[2] == 1

    @pytest.mark.asyncio
    async def test_analyze_reverse_impact_with_max_depth(
        self, db_session: AsyncSession, complex_item_hierarchy: dict
    ) -> None:
        """Test reverse impact respects max_depth parameter."""
        service = ImpactAnalysisService(db_session)

        grandchild1 = complex_item_hierarchy["grandchild1"]

        result = await service.analyze_reverse_impact(str(grandchild1.id), max_depth=1)

        # Should only get child1 (depth 1), not root (depth 2)
        assert result.total_affected == 1
        assert result.max_depth_reached == 1

        affected_titles = {item["title"] for item in result.affected_items}
        assert "Child1 Implementation" in affected_titles
        assert "Root Feature" not in affected_titles

    @pytest.mark.asyncio
    async def test_analyze_reverse_impact_critical_paths(
        self, db_session: AsyncSession, complex_item_hierarchy: dict
    ) -> None:
        """Test reverse impact identifies critical upstream paths."""
        service = ImpactAnalysisService(db_session)

        grandchild2 = complex_item_hierarchy["grandchild2"]

        result = await service.analyze_reverse_impact(str(grandchild2.id))

        # Should have 1 critical path: grandchild2 -> child1 -> root
        assert len(result.critical_paths) == 1
        assert len(result.critical_paths[0]) == COUNT_THREE

    @pytest.mark.asyncio
    async def test_analyze_impact_affected_items_structure(
        self,
        db_session: AsyncSession,
        complex_item_hierarchy: dict,
    ) -> None:
        """Test impact analysis returns properly structured affected items."""
        service = ImpactAnalysisService(db_session)

        root = complex_item_hierarchy["root"]

        result = await service.analyze_impact(str(root.id))

        # Check structure of affected items
        for item in result.affected_items:
            assert "id" in item
            assert "title" in item
            assert "view" in item
            assert "item_type" in item
            assert "status" in item
            assert "depth" in item
            assert "path" in item
            assert "link_type" in item

            assert isinstance(item["path"], list)
            assert len(item["path"]) > 0

    @pytest.mark.asyncio
    async def test_find_critical_paths_empty_nodes(self, db_session: AsyncSession) -> None:
        """Test _find_critical_paths with empty nodes list."""
        service = ImpactAnalysisService(db_session)

        paths = service._find_critical_paths([])

        assert paths == []


# ============================================================
# TRACEABILITY MATRIX SERVICE TESTS (15 tests)
# ============================================================


class TestTraceabilityMatrixService:
    """Integration tests for TraceabilityMatrixService."""

    # ========== Matrix Generation Tests ==========

    @pytest.mark.asyncio
    async def test_generate_matrix_basic(self, db_session: AsyncSession, traceability_test_items: dict) -> None:
        """Test basic matrix generation."""
        service = TraceabilityMatrixService(db_session)

        sources = traceability_test_items["sources"]
        project_id = sources[0].project_id

        matrix = await service.generate_matrix(project_id)

        assert isinstance(matrix, TraceabilityMatrix)
        assert matrix.project_id == str(project_id)
        assert len(matrix.rows) == 7  # 3 sources + 4 targets (all items)
        assert len(matrix.columns) == 7
        assert matrix.total_links == COUNT_THREE

    @pytest.mark.asyncio
    async def test_generate_matrix_with_source_view_filter(
        self,
        db_session: AsyncSession,
        traceability_test_items: dict,
    ) -> None:
        """Test matrix generation with source view filter."""
        service = TraceabilityMatrixService(db_session)

        sources = traceability_test_items["sources"]
        project_id = sources[0].project_id

        matrix = await service.generate_matrix(project_id, source_view="FEATURE")

        # Only FEATURE items as rows
        assert len(matrix.rows) == COUNT_THREE
        assert all(row["view"] == "FEATURE" for row in matrix.rows)

    @pytest.mark.asyncio
    async def test_generate_matrix_with_target_view_filter(
        self,
        db_session: AsyncSession,
        traceability_test_items: dict,
    ) -> None:
        """Test matrix generation with target view filter."""
        service = TraceabilityMatrixService(db_session)

        sources = traceability_test_items["sources"]
        project_id = sources[0].project_id

        matrix = await service.generate_matrix(project_id, target_view="CODE")

        # Only CODE items as columns
        assert len(matrix.columns) == COUNT_FOUR
        assert all(col["view"] == "CODE" for col in matrix.columns)

    @pytest.mark.asyncio
    async def test_generate_matrix_with_both_view_filters(
        self,
        db_session: AsyncSession,
        traceability_test_items: dict,
    ) -> None:
        """Test matrix generation with both source and target view filters."""
        service = TraceabilityMatrixService(db_session)

        sources = traceability_test_items["sources"]
        project_id = sources[0].project_id

        matrix = await service.generate_matrix(
            project_id,
            source_view="FEATURE",
            target_view="CODE",
        )

        assert len(matrix.rows) == COUNT_THREE  # 3 FEATURE items
        assert len(matrix.columns) == COUNT_FOUR  # 4 CODE items
        assert len(matrix.matrix) == COUNT_THREE
        assert len(matrix.matrix[0]) == COUNT_FOUR

    @pytest.mark.asyncio
    async def test_generate_matrix_with_link_type_filter(
        self, db_session: AsyncSession, traceability_test_items: dict
    ) -> None:
        """Test matrix generation filters by link types."""
        service = TraceabilityMatrixService(db_session)

        sources = traceability_test_items["sources"]
        project_id = sources[0].project_id

        matrix = await service.generate_matrix(
            project_id,
            source_view="FEATURE",
            target_view="CODE",
            link_types=["implements"],
        )

        # All 3 links are "implements" type
        assert matrix.total_links == COUNT_THREE

        # Verify link types in matrix
        for row in matrix.matrix:
            for cell in row:
                if cell:
                    assert cell == "implements"

    @pytest.mark.asyncio
    async def test_generate_matrix_coverage_calculation(
        self, db_session: AsyncSession, traceability_test_items: dict
    ) -> None:
        """Test matrix coverage percentage calculation."""
        service = TraceabilityMatrixService(db_session)

        sources = traceability_test_items["sources"]
        project_id = sources[0].project_id

        matrix = await service.generate_matrix(
            project_id,
            source_view="FEATURE",
            target_view="CODE",
        )

        # 3 rows x 4 columns = 12 cells
        # 3 links = 3 filled cells
        # Coverage = 3/12 * 100 = 25%
        assert matrix.coverage == pytest.approx(25.0, rel=0.01)

    @pytest.mark.asyncio
    async def test_generate_matrix_empty_project(self, db_session: AsyncSession, test_project: Project) -> None:
        """Test matrix generation for empty project."""
        service = TraceabilityMatrixService(db_session)

        matrix = await service.generate_matrix(str(test_project.id))

        assert len(matrix.rows) == 0
        assert len(matrix.columns) == 0
        assert len(matrix.matrix) == 0
        assert matrix.total_links == 0
        assert matrix.coverage == 0

    # ========== CSV Export Tests ==========

    @pytest.mark.asyncio
    async def test_export_matrix_csv(self, db_session: AsyncSession, traceability_test_items: dict) -> None:
        """Test CSV export of traceability matrix."""
        service = TraceabilityMatrixService(db_session)

        sources = traceability_test_items["sources"]
        project_id = sources[0].project_id

        matrix = await service.generate_matrix(
            project_id,
            source_view="FEATURE",
            target_view="CODE",
        )

        csv_output = await service.export_matrix_csv(matrix)

        assert isinstance(csv_output, str)
        assert "Source" in csv_output
        assert "Feature 1" in csv_output
        assert "Code Class 1" in csv_output
        assert "implements" in csv_output
        assert f"Total Links,{matrix.total_links}" in csv_output
        assert f"Coverage,{matrix.coverage:.1f}%" in csv_output

    @pytest.mark.asyncio
    async def test_export_matrix_csv_structure(self, db_session: AsyncSession, traceability_test_items: dict) -> None:
        """Test CSV export has correct structure."""
        service = TraceabilityMatrixService(db_session)

        sources = traceability_test_items["sources"]
        project_id = sources[0].project_id

        matrix = await service.generate_matrix(
            project_id,
            source_view="FEATURE",
            target_view="CODE",
        )

        csv_output = await service.export_matrix_csv(matrix)

        lines = csv_output.strip().split("\n")

        # Header + 3 data rows + empty line + 2 summary rows
        assert len(lines) >= 6

        # Parse header
        reader = csv.reader(StringIO(csv_output))
        header = next(reader)
        assert header[0] == "Source"
        assert len(header) == COUNT_FIVE  # Source + 4 code classes

    # ========== HTML Export Tests ==========

    @pytest.mark.asyncio
    async def test_export_matrix_html(self, db_session: AsyncSession, traceability_test_items: dict) -> None:
        """Test HTML export of traceability matrix."""
        service = TraceabilityMatrixService(db_session)

        sources = traceability_test_items["sources"]
        project_id = sources[0].project_id

        matrix = await service.generate_matrix(
            project_id,
            source_view="FEATURE",
            target_view="CODE",
        )

        html_output = await service.export_matrix_html(matrix)

        assert isinstance(html_output, str)
        assert "<table" in html_output
        assert "<th>Source</th>" in html_output
        assert "Feature 1" in html_output
        assert "implements" in html_output
        assert "background-color: #90EE90" in html_output  # Highlighted cells
        assert f"Total Links: {matrix.total_links}" in html_output
        assert f"Coverage: {matrix.coverage:.1f}%" in html_output

    @pytest.mark.asyncio
    async def test_export_matrix_html_structure(self, db_session: AsyncSession, traceability_test_items: dict) -> None:
        """Test HTML export has correct table structure."""
        service = TraceabilityMatrixService(db_session)

        sources = traceability_test_items["sources"]
        project_id = sources[0].project_id

        matrix = await service.generate_matrix(
            project_id,
            source_view="FEATURE",
            target_view="CODE",
        )

        html_output = await service.export_matrix_html(matrix)

        # Should have header row and data rows
        assert html_output.count("<tr>") == COUNT_FOUR  # 1 header + 3 data rows
        assert html_output.count("<th>") == COUNT_FIVE  # Source + 4 columns

        # Check for highlighted cells (linked items)
        assert "background-color: #90EE90" in html_output

    # ========== Uncovered Items Tests ==========

    @pytest.mark.asyncio
    async def test_get_uncovered_items(self, db_session: AsyncSession, traceability_test_items: dict) -> None:
        """Test identification of uncovered items."""
        service = TraceabilityMatrixService(db_session)

        sources = traceability_test_items["sources"]
        targets = traceability_test_items["targets"]
        project_id = sources[0].project_id

        matrix = await service.generate_matrix(
            project_id,
            source_view="FEATURE",
            target_view="CODE",
        )

        uncovered = await service.get_uncovered_items(matrix)

        assert "uncovered_sources" in uncovered
        assert "uncovered_targets" in uncovered

        # Feature 3 has no links
        assert str(sources[2].id) in uncovered["uncovered_sources"]

        # Code Class 4 has no links
        assert str(targets[3].id) in uncovered["uncovered_targets"]

    @pytest.mark.asyncio
    async def test_get_uncovered_items_empty_matrix(self, db_session: AsyncSession, test_project: Project) -> None:
        """Test uncovered items for empty matrix."""
        service = TraceabilityMatrixService(db_session)

        matrix = await service.generate_matrix(str(test_project.id))

        uncovered = await service.get_uncovered_items(matrix)

        assert len(uncovered["uncovered_sources"]) == 0
        assert len(uncovered["uncovered_targets"]) == 0

    @pytest.mark.asyncio
    async def test_get_uncovered_items_fully_covered(self, db_session: AsyncSession, test_project: Project) -> None:
        """Test uncovered items when all items are covered."""
        # Create items with full coverage
        items_repo = ItemRepository(db_session)
        links_repo = LinkRepository(db_session)

        source = await items_repo.create(
            project_id=str(test_project.id),
            title="Source",
            view="FEATURE",
            item_type="feature",
        )

        target = await items_repo.create(
            project_id=str(test_project.id),
            title="Target",
            view="CODE",
            item_type="class",
        )

        await links_repo.create(
            project_id=str(test_project.id),
            source_item_id=str(source.id),
            target_item_id=str(target.id),
            link_type="implements",
        )

        await db_session.commit()

        service = TraceabilityMatrixService(db_session)
        matrix = await service.generate_matrix(
            str(test_project.id),
            source_view="FEATURE",
            target_view="CODE",
        )

        uncovered = await service.get_uncovered_items(matrix)

        # All items covered
        assert len(uncovered["uncovered_sources"]) == 0
        assert len(uncovered["uncovered_targets"]) == 0


# ============================================================
# QUERY OPTIMIZATION SERVICE TESTS (8 tests)
# ============================================================


class TestQueryOptimizationService:
    """Integration tests for QueryOptimizationService."""

    # ========== Query Performance Analysis Tests ==========

    @pytest.mark.asyncio
    async def test_analyze_query_performance(self, db_session: AsyncSession, test_project: Project) -> None:
        """Test query performance analysis."""
        # Create test items
        items_repo = ItemRepository(db_session)
        for i in range(10):
            await items_repo.create(
                project_id=str(test_project.id),
                title=f"Item {i}",
                view="FEATURE",
                item_type="feature",
                status="todo",
            )
        await db_session.commit()

        service = QueryOptimizationService(db_session)

        result = await service.analyze_query_performance(
            str(test_project.id),
            {"status": "todo"},
        )

        assert "execution_time_seconds" in result
        assert "items_returned" in result
        assert "performance_rating" in result
        assert "optimization_suggestions" in result

        assert result["items_returned"] == COUNT_TEN
        assert isinstance(result["execution_time_seconds"], float)
        assert result["performance_rating"] in {"Excellent", "Good", "Fair", "Poor"}

    @pytest.mark.asyncio
    async def test_analyze_query_performance_tracks_stats(
        self, db_session: AsyncSession, test_project: Project
    ) -> None:
        """Test that query analysis tracks statistics."""
        service = QueryOptimizationService(db_session)

        # Run multiple queries
        for _ in range(3):
            await service.analyze_query_performance(
                str(test_project.id),
                {"view": "FEATURE"},
            )

        assert len(service.query_stats) == COUNT_THREE

        # Check stats structure
        for stat in service.query_stats:
            assert "query_filters" in stat
            assert "execution_time_seconds" in stat
            assert "items_returned" in stat
            assert "timestamp" in stat

    @pytest.mark.asyncio
    async def test_performance_rating_excellent(self, db_session: AsyncSession, _test_project: Project) -> None:
        """Test excellent performance rating."""
        service = QueryOptimizationService(db_session)

        rating = service._rate_performance(0.05)

        assert rating == "Excellent"

    @pytest.mark.asyncio
    async def test_performance_rating_poor(self, db_session: AsyncSession) -> None:
        """Test poor performance rating."""
        service = QueryOptimizationService(db_session)

        rating = service._rate_performance(1.5)

        assert rating == "Poor"

    # ========== Cache Tests ==========

    @pytest.mark.asyncio
    async def test_cache_query_and_retrieval(self, db_session: AsyncSession) -> None:
        """Test caching and retrieving query results."""
        service = QueryOptimizationService(db_session)

        result = {"items": [1, 2, 3]}

        service.cache_query("test-query", result, ttl_seconds=300)

        cached = service.get_cached_query("test-query")

        assert cached == result

    @pytest.mark.asyncio
    async def test_cache_expiration(self, db_session: AsyncSession) -> None:
        """Test cache expiration."""
        service = QueryOptimizationService(db_session)

        result = {"data": "test"}

        # Cache with very short TTL
        service.cache_query("expiring-query", result, ttl_seconds=0)

        # Should be expired immediately
        cached = service.get_cached_query("expiring-query")

        assert cached is None
        # Cache entry should be removed
        assert "expiring-query" not in service.query_cache

    @pytest.mark.asyncio
    async def test_cache_nonexistent_key(self, db_session: AsyncSession) -> None:
        """Test retrieving nonexistent cache key."""
        service = QueryOptimizationService(db_session)

        cached = service.get_cached_query("nonexistent")

        assert cached is None

    @pytest.mark.asyncio
    async def test_clear_cache(self, db_session: AsyncSession) -> None:
        """Test clearing all cached queries."""
        service = QueryOptimizationService(db_session)

        # Cache multiple queries
        service.cache_query("query1", {"data": 1})
        service.cache_query("query2", {"data": 2})
        service.cache_query("query3", {"data": 3})

        count = service.clear_cache()

        assert count == COUNT_THREE
        assert len(service.query_cache) == 0

    @pytest.mark.asyncio
    async def test_get_cache_stats(self, db_session: AsyncSession, test_project: Project) -> None:
        """Test getting cache statistics."""
        service = QueryOptimizationService(db_session)

        # Cache some queries
        service.cache_query("query1", {"data": 1})
        service.cache_query("query2", {"data": 2})

        # Execute some queries
        await service.analyze_query_performance(str(test_project.id), {})

        stats = service.get_cache_stats()

        assert stats["cached_queries"] == COUNT_TWO
        assert stats["total_queries_executed"] == 1
        assert "query1" in stats["cache_keys"]
        assert "query2" in stats["cache_keys"]

    @pytest.mark.asyncio
    async def test_get_query_statistics_empty(self, db_session: AsyncSession) -> None:
        """Test query statistics when no queries executed."""
        service = QueryOptimizationService(db_session)

        stats = service.get_query_statistics()

        assert stats["total_queries"] == 0
        assert stats["average_execution_time"] == 0
        assert stats["min_execution_time"] == 0
        assert stats["max_execution_time"] == 0

    @pytest.mark.asyncio
    async def test_get_query_statistics_with_data(self, db_session: AsyncSession, test_project: Project) -> None:
        """Test query statistics calculation."""
        service = QueryOptimizationService(db_session)

        # Execute multiple queries
        for _ in range(3):
            await service.analyze_query_performance(str(test_project.id), {})

        stats = service.get_query_statistics()

        assert stats["total_queries"] == COUNT_THREE
        assert stats["average_execution_time"] > 0
        assert stats["min_execution_time"] > 0
        assert stats["max_execution_time"] > 0
        assert "total_items_returned" in stats

    @pytest.mark.asyncio
    async def test_optimization_suggestions_slow_query(self, db_session: AsyncSession) -> None:
        """Test optimization suggestions for slow queries."""
        service = QueryOptimizationService(db_session)

        suggestions = service._suggest_optimizations(1.5, 50)

        assert "Consider adding indexes" in suggestions[0]

    @pytest.mark.asyncio
    async def test_optimization_suggestions_large_result(self, db_session: AsyncSession) -> None:
        """Test optimization suggestions for large result sets."""
        service = QueryOptimizationService(db_session)

        suggestions = service._suggest_optimizations(0.3, 15000)

        assert any("pagination" in s for s in suggestions)

    @pytest.mark.asyncio
    async def test_optimization_suggestions_cache_candidate(self, db_session: AsyncSession) -> None:
        """Test optimization suggestions for cache candidates."""
        service = QueryOptimizationService(db_session)

        suggestions = service._suggest_optimizations(0.7, 50)

        assert any("caching" in s for s in suggestions)

    @pytest.mark.asyncio
    async def test_recommend_indexes_insufficient_data(self, db_session: AsyncSession, test_project: Project) -> None:
        """Test index recommendations with insufficient query data."""
        service = QueryOptimizationService(db_session)

        # Execute only a few queries
        await service.analyze_query_performance(str(test_project.id), {"status": "todo"})

        recommendations = service.recommend_indexes(str(test_project.id))

        # Should return empty with < COUNT_TEN queries
        assert recommendations == []

    @pytest.mark.asyncio
    async def test_recommend_indexes_status_queries(self, db_session: AsyncSession, test_project: Project) -> None:
        """Test index recommendations for frequent status queries."""
        service = QueryOptimizationService(db_session)

        # Execute many status queries
        for _ in range(15):
            await service.analyze_query_performance(
                str(test_project.id),
                {"status": "todo"},
            )

        recommendations = service.recommend_indexes(str(test_project.id))

        # Should recommend status index
        assert any("idx_item_status" in rec for rec in recommendations)

    @pytest.mark.asyncio
    async def test_recommend_indexes_view_queries(self, db_session: AsyncSession, test_project: Project) -> None:
        """Test index recommendations for frequent view queries."""
        service = QueryOptimizationService(db_session)

        # Execute many view queries
        for _ in range(15):
            await service.analyze_query_performance(
                str(test_project.id),
                {"view": "FEATURE"},
            )

        recommendations = service.recommend_indexes(str(test_project.id))

        # Should recommend view index
        assert any("idx_item_view" in rec for rec in recommendations)


# ============================================================
# SECURITY COMPLIANCE SERVICE TESTS (7 tests)
# ============================================================


class TestSecurityComplianceService:
    """Integration tests for SecurityComplianceService."""

    # ========== Encryption Tests ==========

    @pytest.mark.asyncio
    async def test_enable_encryption(self, db_session: AsyncSession) -> None:
        """Test enabling encryption."""
        service = SecurityComplianceService(db_session)

        result = service.enable_encryption()

        assert result["encryption_enabled"] is True
        assert result["status"] == "Encryption enabled successfully"
        assert "timestamp" in result
        assert service.is_encryption_enabled() is True

    @pytest.mark.asyncio
    async def test_disable_encryption(self, db_session: AsyncSession) -> None:
        """Test disabling encryption."""
        service = SecurityComplianceService(db_session)

        # Enable first
        service.enable_encryption()

        # Then disable
        result = service.disable_encryption()

        assert result["encryption_enabled"] is False
        assert result["status"] == "Encryption disabled successfully"
        assert service.is_encryption_enabled() is False

    @pytest.mark.asyncio
    async def test_is_encryption_enabled_default(self, db_session: AsyncSession) -> None:
        """Test encryption is disabled by default."""
        service = SecurityComplianceService(db_session)

        assert service.is_encryption_enabled() is False

    # ========== Audit Logging Tests ==========

    @pytest.mark.asyncio
    async def test_log_audit_event(self, db_session: AsyncSession) -> None:
        """Test logging audit events."""
        service = SecurityComplianceService(db_session)

        result = service.log_audit_event(
            event_type="access",
            user_id="user123",
            resource="item/456",
            action="read",
            details={"ip": "192.168.1.1"},
        )

        assert result["logged"] is True
        assert result["event_id"] == 1
        assert result["status"] == "Audit event logged successfully"

        # Verify event in log
        log = service.get_audit_log()
        assert len(log) == 1
        assert log[0]["event_type"] == "access"
        assert log[0]["user_id"] == "user123"
        assert log[0]["resource"] == "item/456"
        assert log[0]["action"] == "read"
        assert log[0]["details"]["ip"] == "192.168.1.1"

    @pytest.mark.asyncio
    async def test_log_audit_event_without_details(self, db_session: AsyncSession) -> None:
        """Test logging audit event without details."""
        service = SecurityComplianceService(db_session)

        result = service.log_audit_event(
            event_type="login",
            user_id="user456",
            resource="auth",
            action="authenticate",
        )

        assert result["logged"] is True

        log = service.get_audit_log()
        assert log[0]["details"] == {}

    @pytest.mark.asyncio
    async def test_get_audit_log_filter_by_user(self, db_session: AsyncSession) -> None:
        """Test filtering audit log by user."""
        service = SecurityComplianceService(db_session)

        # Log events for different users
        service.log_audit_event("access", "user1", "resource1", "read")
        service.log_audit_event("access", "user2", "resource2", "read")
        service.log_audit_event("access", "user1", "resource3", "write")

        # Filter by user1
        log = service.get_audit_log(user_id="user1")

        assert len(log) == COUNT_TWO
        assert all(e["user_id"] == "user1" for e in log)

    @pytest.mark.asyncio
    async def test_get_audit_log_filter_by_event_type(self, db_session: AsyncSession) -> None:
        """Test filtering audit log by event type."""
        service = SecurityComplianceService(db_session)

        # Log different event types
        service.log_audit_event("login", "user1", "auth", "authenticate")
        service.log_audit_event("access", "user1", "resource1", "read")
        service.log_audit_event("login", "user2", "auth", "authenticate")

        # Filter by login events
        log = service.get_audit_log(event_type="login")

        assert len(log) == COUNT_TWO
        assert all(e["event_type"] == "login" for e in log)

    @pytest.mark.asyncio
    async def test_get_audit_log_filter_by_both(self, db_session: AsyncSession) -> None:
        """Test filtering audit log by user and event type."""
        service = SecurityComplianceService(db_session)

        # Log various events
        service.log_audit_event("login", "user1", "auth", "authenticate")
        service.log_audit_event("access", "user1", "resource1", "read")
        service.log_audit_event("login", "user2", "auth", "authenticate")
        service.log_audit_event("access", "user2", "resource2", "write")

        # Filter by user1 and access
        log = service.get_audit_log(user_id="user1", event_type="access")

        assert len(log) == 1
        assert log[0]["user_id"] == "user1"
        assert log[0]["event_type"] == "access"

    @pytest.mark.asyncio
    async def test_get_audit_stats(self, db_session: AsyncSession) -> None:
        """Test getting audit log statistics."""
        service = SecurityComplianceService(db_session)

        # Log various events
        service.log_audit_event("login", "user1", "auth", "authenticate")
        service.log_audit_event("access", "user1", "resource1", "read")
        service.log_audit_event("login", "user2", "auth", "authenticate")
        service.log_audit_event("access", "user2", "resource2", "write")
        service.log_audit_event("delete", "user1", "resource3", "delete")

        stats = service.get_audit_stats()

        assert stats["total_events"] == COUNT_FIVE
        assert stats["unique_users"] == COUNT_TWO
        assert stats["event_types"]["login"] == COUNT_TWO
        assert stats["event_types"]["access"] == COUNT_TWO
        assert stats["event_types"]["delete"] == 1

    @pytest.mark.asyncio
    async def test_clear_audit_log(self, db_session: AsyncSession) -> None:
        """Test clearing audit log."""
        service = SecurityComplianceService(db_session)

        # Log some events
        service.log_audit_event("access", "user1", "resource1", "read")
        service.log_audit_event("access", "user2", "resource2", "write")
        service.log_audit_event("delete", "user1", "resource3", "delete")

        result = service.clear_audit_log()

        assert result["cleared_count"] == COUNT_THREE
        assert result["status"] == "Audit log cleared successfully"
        assert len(service.audit_log) == 0

    # ========== Data Hashing Tests ==========

    @pytest.mark.asyncio
    async def test_hash_sensitive_data(self, db_session: AsyncSession) -> None:
        """Test hashing sensitive data."""
        service = SecurityComplianceService(db_session)

        data = "sensitive-password-123"

        hashed = service.hash_sensitive_data(data)

        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA256 produces 64 hex characters
        assert hashed != data

    @pytest.mark.asyncio
    async def test_hash_sensitive_data_deterministic(self, db_session: AsyncSession) -> None:
        """Test hashing produces deterministic results."""
        service = SecurityComplianceService(db_session)

        data = "test-data"

        hash1 = service.hash_sensitive_data(data)
        hash2 = service.hash_sensitive_data(data)

        assert hash1 == hash2

    @pytest.mark.asyncio
    async def test_hash_sensitive_data_different_inputs(self, db_session: AsyncSession) -> None:
        """Test different inputs produce different hashes."""
        service = SecurityComplianceService(db_session)

        hash1 = service.hash_sensitive_data("data1")
        hash2 = service.hash_sensitive_data("data2")

        assert hash1 != hash2

    # ========== Access Control Tests ==========

    @pytest.mark.asyncio
    async def test_validate_access_control_default_role(self, db_session: AsyncSession) -> None:
        """Test access control validation with default viewer role."""
        service = SecurityComplianceService(db_session)

        result = service.validate_access_control(
            user_id="user123",
            resource="item/456",
            action="read",
        )

        assert result["user_id"] == "user123"
        assert result["resource"] == "item/456"
        assert result["action"] == "read"
        assert result["allowed"] is True  # Viewer can read
        assert result["role"] == "viewer"

    @pytest.mark.asyncio
    async def test_validate_access_control_write_denied(self, db_session: AsyncSession) -> None:
        """Test access control denies write for viewer."""
        service = SecurityComplianceService(db_session)

        result = service.validate_access_control(
            user_id="user123",
            resource="item/456",
            action="write",
        )

        assert result["allowed"] is False  # Viewer cannot write
        assert result["role"] == "viewer"

    # ========== Compliance Report Tests ==========

    @pytest.mark.asyncio
    async def test_generate_compliance_report_non_compliant(self, db_session: AsyncSession) -> None:
        """Test compliance report when not compliant."""
        service = SecurityComplianceService(db_session)

        # Log some events
        service.log_audit_event("access", "user1", "resource1", "read")

        report = service.generate_compliance_report()

        assert "generated_at" in report
        assert report["encryption_enabled"] is False
        assert report["compliance_status"] == "NON_COMPLIANT"
        assert "audit_stats" in report
        assert len(report["recommendations"]) > 0
        assert any("encryption" in r.lower() for r in report["recommendations"])

    @pytest.mark.asyncio
    async def test_generate_compliance_report_compliant(self, db_session: AsyncSession) -> None:
        """Test compliance report when compliant."""
        service = SecurityComplianceService(db_session)

        # Enable encryption
        service.enable_encryption()

        report = service.generate_compliance_report()

        assert report["encryption_enabled"] is True
        assert report["compliance_status"] == "COMPLIANT"

    @pytest.mark.asyncio
    async def test_generate_compliance_report_includes_audit_stats(self, db_session: AsyncSession) -> None:
        """Test compliance report includes audit statistics."""
        service = SecurityComplianceService(db_session)

        # Log events
        service.log_audit_event("access", "user1", "resource1", "read")
        service.log_audit_event("access", "user2", "resource2", "write")

        report = service.generate_compliance_report()

        assert report["audit_stats"]["total_events"] == COUNT_TWO
        assert report["audit_stats"]["unique_users"] == COUNT_TWO
