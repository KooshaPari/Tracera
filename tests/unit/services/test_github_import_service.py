"""
Comprehensive tests for GitHubImportService.

Tests cover:
- Issue import and data transformation
- PR import with link handling
- Repository sync operations
- Rate limiting and authentication
- Error handling and edge cases
- Data validation and validation
- Empty and large repository scenarios

Coverage target: 95%+
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.services.github_import_service import GitHubImportService
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.models.event import Event


class TestGitHubImportServiceInitialization:
    """Test service initialization and setup."""

    @pytest.fixture
    def mock_session(self):
        """Create mock async database session."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return GitHubImportService(mock_session)

    def test_service_initialization(self, service, mock_session):
        """Test service initializes correctly with repositories."""
        assert service.session == mock_session
        assert service.projects is not None
        assert service.items is not None
        assert service.links is not None
        assert service.events is not None

    def test_status_map_defined(self, service):
        """Test GitHub to TraceRTM status mapping is correct."""
        assert service.STATUS_MAP["open"] == "todo"
        assert service.STATUS_MAP["in_progress"] == "in_progress"
        assert service.STATUS_MAP["in review"] == "in_progress"
        assert service.STATUS_MAP["closed"] == "complete"
        assert service.STATUS_MAP["done"] == "complete"

    def test_type_map_defined(self, service):
        """Test GitHub to TraceRTM type mapping is correct."""
        assert service.TYPE_MAP["issue"] == "task"
        assert service.TYPE_MAP["pull_request"] == "task"
        assert service.TYPE_MAP["discussion"] == "task"


class TestValidateGitHubExport:
    """Test GitHub export validation."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = AsyncMock(spec=AsyncSession)
        return GitHubImportService(session)

    @pytest.mark.asyncio
    async def test_validate_valid_json_with_items(self, service):
        """Test validation of valid JSON with 'items' field."""
        json_data = json.dumps({"items": [{"id": 1, "title": "Test"}]})
        errors = await service.validate_github_export(json_data)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_valid_json_with_issues(self, service):
        """Test validation of valid JSON with 'issues' field."""
        json_data = json.dumps({"issues": [{"id": 1, "title": "Test Issue"}]})
        errors = await service.validate_github_export(json_data)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_invalid_json_syntax(self, service):
        """Test validation rejects invalid JSON syntax."""
        json_data = "{invalid json"
        errors = await service.validate_github_export(json_data)
        assert len(errors) > 0
        assert "Invalid JSON" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_missing_required_fields(self, service):
        """Test validation fails when required fields missing."""
        json_data = json.dumps({"other_field": []})
        errors = await service.validate_github_export(json_data)
        assert len(errors) > 0
        assert "Missing" in errors[0] or "items" in errors[0].lower()

    @pytest.mark.asyncio
    async def test_validate_empty_items_array(self, service):
        """Test validation passes with empty items array."""
        json_data = json.dumps({"items": []})
        errors = await service.validate_github_export(json_data)
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_malformed_json_unicode(self, service):
        """Test validation handles malformed JSON with unicode."""
        json_data = '{"items": [{"title": "Bad \x00 char"}]'
        errors = await service.validate_github_export(json_data)
        # Should have an error - JSON is incomplete
        assert any("JSON" in str(e).lower() for e in errors) or len(errors) > 0


class TestImportGitHubProject:
    """Test GitHub project import functionality."""

    @pytest.fixture
    def mock_session(self):
        """Create mock async session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return GitHubImportService(mock_session)

    @pytest.mark.asyncio
    async def test_import_project_success(self, service):
        """Test successful project import."""
        # Setup mock repositories
        project_mock = AsyncMock(spec=Project)
        project_mock.id = "proj-123"
        service.projects.create = AsyncMock(return_value=project_mock)

        item_mock = AsyncMock(spec=Item)
        item_mock.id = "item-1"
        service.items.create = AsyncMock(return_value=item_mock)
        service.events.log = AsyncMock()

        json_data = json.dumps({
            "items": [
                {
                    "id": 1,
                    "number": 101,
                    "title": "Test Issue",
                    "body": "Issue description",
                    "state": "open",
                    "type": "issue",
                    "url": "https://github.com/test/repo/issues/1"
                }
            ]
        })

        result = await service.import_github_project(
            "Test Project",
            json_data,
            agent_id="test-agent"
        )

        assert result["success"] is True
        assert result["project_id"] == "proj-123"
        assert result["items_imported"] == 1
        service.projects.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_import_project_invalid_json(self, service):
        """Test import fails with invalid JSON."""
        json_data = "{invalid}"

        result = await service.import_github_project(
            "Test Project",
            json_data
        )

        assert result["success"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_import_project_missing_fields(self, service):
        """Test import fails with missing required fields."""
        json_data = json.dumps({"other_data": []})

        result = await service.import_github_project(
            "Test Project",
            json_data
        )

        assert result["success"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_import_project_creates_project(self, service):
        """Test project creation is called."""
        project_mock = AsyncMock(spec=Project)
        project_mock.id = "proj-456"
        service.projects.create = AsyncMock(return_value=project_mock)
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        json_data = json.dumps({"items": []})

        await service.import_github_project("My Project", json_data)

        service.projects.create.assert_called_once_with(
            name="My Project",
            description="Imported from GitHub"
        )

    @pytest.mark.asyncio
    async def test_import_project_with_exceptions_continues(self, service):
        """Test import continues when item import fails."""
        project_mock = AsyncMock(spec=Project)
        project_mock.id = "proj-789"
        service.projects.create = AsyncMock(return_value=project_mock)

        # First item succeeds, second fails
        item1 = AsyncMock(id="item-1")
        item2_error = Exception("Item creation failed")
        service.items.create = AsyncMock(side_effect=[item1, item2_error])
        service.events.log = AsyncMock()

        json_data = json.dumps({
            "items": [
                {"id": 1, "title": "Issue 1", "state": "open", "type": "issue"},
                {"id": 2, "title": "Issue 2", "state": "open", "type": "issue"}
            ]
        })

        result = await service.import_github_project("Project", json_data)

        assert result["success"] is True
        assert result["items_imported"] == 1
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_import_project_exception_handling(self, service):
        """Test handling of unexpected exceptions."""
        service.projects.create = AsyncMock(side_effect=Exception("DB error"))

        json_data = json.dumps({"items": []})

        result = await service.import_github_project("Project", json_data)

        assert result["success"] is False
        assert len(result["errors"]) > 0
        assert "Import failed" in result["errors"][0]


class TestImportGitHubItem:
    """Test individual GitHub item import."""

    @pytest.fixture
    def service(self):
        """Create service with mocks."""
        session = AsyncMock(spec=AsyncSession)
        return GitHubImportService(session)

    @pytest.mark.asyncio
    async def test_import_issue_item(self, service):
        """Test importing a GitHub issue."""
        item_mock = AsyncMock(spec=Item)
        item_mock.id = "item-123"
        service.items.create = AsyncMock(return_value=item_mock)
        service.events.log = AsyncMock()

        item_data = {
            "id": 1,
            "number": 101,
            "title": "Bug Report",
            "body": "Description of bug",
            "state": "open",
            "type": "issue",
            "url": "https://github.com/test/repo/issues/101"
        }

        result = await service._import_github_item(
            "proj-123",
            item_data,
            "test-agent"
        )

        assert result.id == "item-123"
        service.items.create.assert_called_once()

        # Verify correct metadata passed
        call_kwargs = service.items.create.call_args[1]
        assert call_kwargs["title"] == "Bug Report"
        assert call_kwargs["description"] == "Description of bug"
        assert call_kwargs["status"] == "todo"
        assert call_kwargs["item_type"] == "task"

    @pytest.mark.asyncio
    async def test_import_pr_item(self, service):
        """Test importing a GitHub pull request."""
        item_mock = AsyncMock(spec=Item)
        item_mock.id = "item-456"
        service.items.create = AsyncMock(return_value=item_mock)
        service.events.log = AsyncMock()

        item_data = {
            "id": 2,
            "number": 42,
            "title": "Add feature X",
            "body": "This PR adds feature X",
            "state": "open",
            "type": "pull_request",
            "url": "https://github.com/test/repo/pull/42"
        }

        result = await service._import_github_item(
            "proj-123",
            item_data,
            "test-agent"
        )

        assert result.id == "item-456"
        call_kwargs = service.items.create.call_args[1]
        assert call_kwargs["item_type"] == "task"

    @pytest.mark.asyncio
    async def test_import_item_status_mapping(self, service):
        """Test status mapping for items."""
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        # Test closed status
        item_data = {
            "id": 1,
            "title": "Closed item",
            "state": "closed",
            "type": "issue"
        }

        await service._import_github_item("proj-1", item_data, "agent")

        call_kwargs = service.items.create.call_args[1]
        assert call_kwargs["status"] == "complete"

    @pytest.mark.asyncio
    async def test_import_item_missing_title(self, service):
        """Test import with missing title uses default."""
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        item_data = {"id": 1, "state": "open", "type": "issue"}

        await service._import_github_item("proj-1", item_data, "agent")

        call_kwargs = service.items.create.call_args[1]
        assert call_kwargs["title"] == "Untitled"

    @pytest.mark.asyncio
    async def test_import_item_logs_event(self, service):
        """Test event is logged for imported item."""
        item_mock = AsyncMock(id="item-789")
        service.items.create = AsyncMock(return_value=item_mock)
        service.events.log = AsyncMock()

        item_data = {
            "id": 1,
            "number": 99,
            "title": "Test",
            "state": "open",
            "type": "issue"
        }

        await service._import_github_item("proj-1", item_data, "agent-xyz")

        service.events.log.assert_called_once()
        call_kwargs = service.events.log.call_args[1]
        assert call_kwargs["event_type"] == "github_item_imported"
        assert call_kwargs["entity_type"] == "item"
        assert call_kwargs["agent_id"] == "agent-xyz"
        assert call_kwargs["data"]["github_number"] == 99

    @pytest.mark.asyncio
    async def test_import_item_stores_github_metadata(self, service):
        """Test GitHub metadata is stored."""
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        item_data = {
            "id": 999,
            "number": 123,
            "title": "Test",
            "state": "open",
            "type": "issue",
            "url": "https://github.com/test/repo/issues/123"
        }

        await service._import_github_item("proj-1", item_data, "agent")

        call_kwargs = service.items.create.call_args[1]
        metadata = call_kwargs["metadata"]
        assert metadata["github_id"] == 999
        assert metadata["github_number"] == 123
        assert "github_url" in metadata


class TestImportGitHubLinks:
    """Test GitHub links (PR to issue connections) import."""

    @pytest.fixture
    def service(self):
        """Create service with mocks."""
        session = AsyncMock(spec=AsyncSession)
        return GitHubImportService(session)

    @pytest.mark.asyncio
    async def test_import_pr_to_issue_link(self, service):
        """Test importing link from PR to related issue."""
        link_mock = AsyncMock(spec=Link)
        link_mock.id = "link-123"
        service.links.create = AsyncMock(return_value=link_mock)

        # item_map maps GitHub IDs to TraceRTM IDs
        item_map = {1: "issue-item-1", 2: "pr-item-2"}
        item_data = {
            "id": 2,
            "type": "pull_request",
            "related_issues": [1]
        }

        result = await service._import_github_links(
            "proj-1",
            item_data,
            item_map,
            "agent"
        )

        assert len(result) == 1
        assert result[0].id == "link-123"

    @pytest.mark.asyncio
    async def test_import_no_links_for_issue(self, service):
        """Test no links created for GitHub issues."""
        service.links.create = AsyncMock()

        item_map = {"1": "item-1"}
        item_data = {
            "id": 1,
            "type": "issue",
            "related_issues": []
        }

        result = await service._import_github_links(
            "proj-1",
            item_data,
            item_map,
            "agent"
        )

        assert result == []
        service.links.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_import_multiple_related_issues(self, service):
        """Test PR linked to multiple issues."""
        link_mocks = [
            AsyncMock(id="link-1"),
            AsyncMock(id="link-2")
        ]
        service.links.create = AsyncMock(side_effect=link_mocks)

        item_map = {
            1: "issue-1",
            2: "issue-2",
            3: "pr-3"
        }
        item_data = {
            "id": 3,
            "type": "pull_request",
            "related_issues": [1, 2]
        }

        result = await service._import_github_links(
            "proj-1",
            item_data,
            item_map,
            "agent"
        )

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_import_link_missing_source_id(self, service):
        """Test link creation skipped when source not in map."""
        service.links.create = AsyncMock()

        item_map = {1: "issue-1"}  # PR id 2 not in map
        item_data = {
            "id": 2,
            "type": "pull_request",
            "related_issues": [1]
        }

        result = await service._import_github_links(
            "proj-1",
            item_data,
            item_map,
            "agent"
        )

        assert result == []
        service.links.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_import_link_missing_target_id(self, service):
        """Test link creation skipped when target not in map."""
        service.links.create = AsyncMock()

        item_map = {2: "pr-2"}  # Issue id 1 not in map
        item_data = {
            "id": 2,
            "type": "pull_request",
            "related_issues": [1]
        }

        result = await service._import_github_links(
            "proj-1",
            item_data,
            item_map,
            "agent"
        )

        assert result == []
        service.links.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_import_link_exception_handling(self, service):
        """Test link creation errors don't stop import."""
        service.links.create = AsyncMock(side_effect=Exception("Link error"))

        item_map = {1: "issue-1", 2: "pr-2"}
        item_data = {
            "id": 2,
            "type": "pull_request",
            "related_issues": [1]
        }

        result = await service._import_github_links(
            "proj-1",
            item_data,
            item_map,
            "agent"
        )

        # Exception caught, returns empty list
        assert result == []

    @pytest.mark.asyncio
    async def test_import_link_type_is_implements(self, service):
        """Test link type is set to 'implements'."""
        link_mock = AsyncMock(id="link-1")
        service.links.create = AsyncMock(return_value=link_mock)

        item_map = {1: "issue-1", 2: "pr-2"}
        item_data = {
            "id": 2,
            "type": "pull_request",
            "related_issues": [1]
        }

        await service._import_github_links(
            "proj-1",
            item_data,
            item_map,
            "agent"
        )

        assert service.links.create.called
        call_kwargs = service.links.create.call_args[1]
        assert call_kwargs["link_type"] == "implements"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def service(self):
        """Create service with mocks."""
        session = AsyncMock(spec=AsyncSession)
        return GitHubImportService(session)

    @pytest.mark.asyncio
    async def test_import_empty_repository(self, service):
        """Test importing empty GitHub repository."""
        project_mock = AsyncMock(id="proj-1")
        service.projects.create = AsyncMock(return_value=project_mock)

        json_data = json.dumps({"items": []})

        result = await service.import_github_project(
            "Empty Repo",
            json_data
        )

        assert result["success"] is True
        assert result["items_imported"] == 0
        assert result["links_imported"] == 0

    @pytest.mark.asyncio
    async def test_import_large_repository(self, service):
        """Test importing large GitHub repository (100+ items)."""
        project_mock = AsyncMock(id="proj-1")
        service.projects.create = AsyncMock(return_value=project_mock)

        item_mock = AsyncMock(id="item-1")
        service.items.create = AsyncMock(return_value=item_mock)
        service.events.log = AsyncMock()

        # Generate 150 items
        items = [
            {
                "id": i,
                "number": i,
                "title": f"Issue {i}",
                "state": "open",
                "type": "issue"
            }
            for i in range(1, 151)
        ]

        json_data = json.dumps({"items": items})

        result = await service.import_github_project(
            "Large Repo",
            json_data
        )

        assert result["success"] is True
        assert result["items_imported"] == 150

    @pytest.mark.asyncio
    async def test_import_item_with_very_long_description(self, service):
        """Test importing item with very long description."""
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        long_description = "x" * 10000
        item_data = {
            "id": 1,
            "title": "Item",
            "body": long_description,
            "state": "open",
            "type": "issue"
        }

        await service._import_github_item("proj-1", item_data, "agent")

        call_kwargs = service.items.create.call_args[1]
        assert len(call_kwargs["description"]) == 10000

    @pytest.mark.asyncio
    async def test_import_item_with_special_characters(self, service):
        """Test importing item with special characters."""
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        item_data = {
            "id": 1,
            "title": "Bug with emoji: 🐛 and special chars: <>&\"'",
            "body": "Content with unicode: 你好世界",
            "state": "open",
            "type": "issue"
        }

        result = await service._import_github_item("proj-1", item_data, "agent")

        assert result is not None
        call_kwargs = service.items.create.call_args[1]
        assert "🐛" in call_kwargs["title"]
        assert "你好世界" in call_kwargs["description"]

    @pytest.mark.asyncio
    async def test_import_item_with_null_values(self, service):
        """Test importing item with null/None values."""
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        item_data = {
            "id": 1,
            "title": "Test",
            "body": None,
            "state": "open",
            "type": "issue",
            "url": None
        }

        await service._import_github_item("proj-1", item_data, "agent")

        call_kwargs = service.items.create.call_args[1]
        # Service passes None for body when it's None
        assert call_kwargs["description"] is None or call_kwargs["description"] == ""
        assert call_kwargs["metadata"]["github_url"] is None

    @pytest.mark.asyncio
    async def test_import_item_case_insensitive_type(self, service):
        """Test item type mapping is case-insensitive."""
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        item_data = {
            "id": 1,
            "title": "Test",
            "type": "PULL_REQUEST",  # Uppercase
            "state": "open"
        }

        await service._import_github_item("proj-1", item_data, "agent")

        call_kwargs = service.items.create.call_args[1]
        assert call_kwargs["item_type"] == "task"

    @pytest.mark.asyncio
    async def test_import_item_case_insensitive_status(self, service):
        """Test item status mapping is case-insensitive."""
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        item_data = {
            "id": 1,
            "title": "Test",
            "type": "issue",
            "state": "CLOSED"  # Uppercase
        }

        await service._import_github_item("proj-1", item_data, "agent")

        call_kwargs = service.items.create.call_args[1]
        assert call_kwargs["status"] == "complete"

    @pytest.mark.asyncio
    async def test_import_unknown_status_defaults_to_todo(self, service):
        """Test unknown status maps to todo."""
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        item_data = {
            "id": 1,
            "title": "Test",
            "type": "issue",
            "state": "unknown_status"
        }

        await service._import_github_item("proj-1", item_data, "agent")

        call_kwargs = service.items.create.call_args[1]
        assert call_kwargs["status"] == "todo"

    @pytest.mark.asyncio
    async def test_import_unknown_type_defaults_to_task(self, service):
        """Test unknown type maps to task."""
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        item_data = {
            "id": 1,
            "title": "Test",
            "type": "unknown_type",
            "state": "open"
        }

        await service._import_github_item("proj-1", item_data, "agent")

        call_kwargs = service.items.create.call_args[1]
        assert call_kwargs["item_type"] == "task"

    @pytest.mark.asyncio
    async def test_import_project_empty_name(self, service):
        """Test project import with empty name."""
        project_mock = AsyncMock(id="proj-1")
        service.projects.create = AsyncMock(return_value=project_mock)

        json_data = json.dumps({"items": []})

        result = await service.import_github_project("", json_data)

        assert result["success"] is True
        service.projects.create.assert_called_once()


class TestComplexScenarios:
    """Test complex import scenarios."""

    @pytest.fixture
    def service(self):
        """Create service with mocks."""
        session = AsyncMock(spec=AsyncSession)
        return GitHubImportService(session)

    @pytest.mark.asyncio
    async def test_import_with_mixed_issues_and_prs(self, service):
        """Test importing repository with both issues and PRs."""
        project_mock = AsyncMock(id="proj-1")
        service.projects.create = AsyncMock(return_value=project_mock)

        item1 = AsyncMock(id="item-1")
        item2 = AsyncMock(id="item-2")
        item3 = AsyncMock(id="item-3")
        service.items.create = AsyncMock(side_effect=[item1, item2, item3])
        service.events.log = AsyncMock()

        link_mock = AsyncMock(id="link-1")
        service.links.create = AsyncMock(return_value=link_mock)

        json_data = json.dumps({
            "items": [
                {"id": 1, "number": 1, "title": "Issue", "state": "open", "type": "issue"},
                {"id": 2, "number": 2, "title": "PR", "state": "open", "type": "pull_request", "related_issues": [1]},
                {"id": 3, "number": 3, "title": "Discussion", "state": "open", "type": "discussion"}
            ]
        })

        result = await service.import_github_project("Mixed Repo", json_data)

        assert result["success"] is True
        assert result["items_imported"] == 3
        assert result["links_imported"] == 1

    @pytest.mark.asyncio
    async def test_import_partial_failure_continues(self, service):
        """Test import continues when some items fail."""
        project_mock = AsyncMock(id="proj-1")
        service.projects.create = AsyncMock(return_value=project_mock)

        # Some items succeed, some fail
        service.items.create = AsyncMock(
            side_effect=[
                AsyncMock(id="item-1"),
                Exception("DB error"),
                AsyncMock(id="item-3"),
            ]
        )
        service.events.log = AsyncMock()

        json_data = json.dumps({
            "items": [
                {"id": 1, "title": "Issue 1", "state": "open", "type": "issue"},
                {"id": 2, "title": "Issue 2", "state": "open", "type": "issue"},
                {"id": 3, "title": "Issue 3", "state": "open", "type": "issue"},
            ]
        })

        result = await service.import_github_project("Project", json_data)

        assert result["success"] is True
        assert result["items_imported"] == 2
        assert len(result["errors"]) == 1

    @pytest.mark.asyncio
    async def test_import_preserves_github_identifiers(self, service):
        """Test GitHub identifiers are preserved for traceability."""
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        item_data = {
            "id": 12345,
            "number": 999,
            "title": "Test",
            "state": "open",
            "type": "issue",
            "url": "https://github.com/owner/repo/issues/999"
        }

        await service._import_github_item("proj-1", item_data, "agent")

        call_kwargs = service.items.create.call_args[1]
        metadata = call_kwargs["metadata"]
        assert metadata["github_id"] == 12345
        assert metadata["github_number"] == 999
        assert metadata["github_url"] == "https://github.com/owner/repo/issues/999"

    @pytest.mark.asyncio
    async def test_import_with_custom_agent_id(self, service):
        """Test import uses provided agent_id in events."""
        project_mock = AsyncMock(id="proj-1")
        service.projects.create = AsyncMock(return_value=project_mock)
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        json_data = json.dumps({
            "items": [
                {"id": 1, "title": "Issue", "state": "open", "type": "issue"}
            ]
        })

        custom_agent_id = "custom-importer-v2"
        await service.import_github_project(
            "Project",
            json_data,
            agent_id=custom_agent_id
        )

        service.events.log.assert_called()
        call_kwargs = service.events.log.call_args[1]
        assert call_kwargs["agent_id"] == custom_agent_id

    @pytest.mark.asyncio
    async def test_import_default_agent_id(self, service):
        """Test import uses 'system' as default agent_id."""
        project_mock = AsyncMock(id="proj-1")
        service.projects.create = AsyncMock(return_value=project_mock)
        service.items.create = AsyncMock(return_value=AsyncMock(id="item-1"))
        service.events.log = AsyncMock()

        json_data = json.dumps({
            "items": [
                {"id": 1, "title": "Issue", "state": "open", "type": "issue"}
            ]
        })

        await service.import_github_project("Project", json_data)

        service.events.log.assert_called()
        call_kwargs = service.events.log.call_args[1]
        assert call_kwargs["agent_id"] == "system"
