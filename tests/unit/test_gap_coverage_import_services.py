"""Gap coverage tests for import services.

Targets: services/github_import_service.py (22.73%), services/jira_import_service.py (18.26%).

Functional Requirements Coverage:
    - FR-DISC-001: GitHub Issue Import
    - FR-DISC-005: Webhook Ingestion (partial)

Epics:
    - EPIC-001: External Integration

Tests verify GitHub and Jira import service initialization, validation,
and basic import operations including status mapping and type mapping.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.test_constants import COUNT_TWO


class TestGitHubImportService:
    """Tests for GitHubImportService."""

    def test_github_import_service_import(self) -> None:
        """Test GitHubImportService can be imported.

        Tests: FR-DISC-001
        """
        from tracertm.services.github_import_service import GitHubImportService

        assert GitHubImportService is not None

    def test_github_import_service_init(self) -> None:
        """Test GitHubImportService initialization.

        Tests: FR-DISC-001
        """
        from tracertm.services.github_import_service import GitHubImportService

        mock_session = MagicMock()
        service = GitHubImportService(mock_session)

        assert service.session == mock_session
        assert service.projects is not None
        assert service.items is not None
        assert service.links is not None
        assert service.events is not None

    def test_github_status_map(self) -> None:
        """Test STATUS_MAP contains expected mappings."""
        from tracertm.services.github_import_service import GitHubImportService

        assert GitHubImportService.STATUS_MAP["open"] == "todo"
        assert GitHubImportService.STATUS_MAP["in_progress"] == "in_progress"
        assert GitHubImportService.STATUS_MAP["closed"] == "complete"
        assert GitHubImportService.STATUS_MAP["done"] == "complete"

    def test_github_type_map(self) -> None:
        """Test TYPE_MAP contains expected mappings."""
        from tracertm.services.github_import_service import GitHubImportService

        assert GitHubImportService.TYPE_MAP["issue"] == "task"
        assert GitHubImportService.TYPE_MAP["pull_request"] == "task"
        assert GitHubImportService.TYPE_MAP["discussion"] == "task"

    @pytest.mark.asyncio
    async def test_validate_github_export_invalid_json(self) -> None:
        """Test validation with invalid JSON."""
        from tracertm.services.github_import_service import GitHubImportService

        mock_session = MagicMock()
        service = GitHubImportService(mock_session)

        errors = await service.validate_github_export("not valid json")

        assert len(errors) == 1
        assert "Invalid JSON" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_github_export_missing_items(self) -> None:
        """Test validation with missing items field."""
        from tracertm.services.github_import_service import GitHubImportService

        mock_session = MagicMock()
        service = GitHubImportService(mock_session)

        errors = await service.validate_github_export('{"name": "test"}')

        assert len(errors) == 1
        assert "Missing 'items' or 'issues' field" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_github_export_valid(self) -> None:
        """Test validation with valid data."""
        from tracertm.services.github_import_service import GitHubImportService

        mock_session = MagicMock()
        service = GitHubImportService(mock_session)

        valid_data = json.dumps({"items": [{"id": 1, "title": "Test"}]})
        errors = await service.validate_github_export(valid_data)

        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_import_github_project_validation_fails(self) -> None:
        """Test import with validation failures."""
        from tracertm.services.github_import_service import GitHubImportService

        mock_session = MagicMock()
        service = GitHubImportService(mock_session)

        result = await service.import_github_project("test-project", "invalid json")

        assert result["success"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_import_github_project_success(self) -> None:
        """Test successful GitHub project import."""
        from tracertm.services.github_import_service import GitHubImportService

        mock_session = MagicMock()
        service = GitHubImportService(mock_session)

        # Mock project creation
        mock_project = MagicMock()
        mock_project.id = "proj-123"
        service.projects.create = AsyncMock(return_value=mock_project)

        # Mock item creation
        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)

        # Mock event logging
        service.events.log = AsyncMock()

        # Mock links
        service.links.create = AsyncMock()

        valid_data = json.dumps({
            "items": [
                {"id": 1, "title": "Test Item", "body": "Description", "state": "open"},
                {"id": 2, "title": "Test Item 2", "body": "Description 2", "state": "closed"},
            ],
        })

        result = await service.import_github_project("test-project", valid_data)

        assert result["success"] is True
        assert result["project_id"] == "proj-123"
        assert result["items_imported"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_import_github_project_with_issues_field(self) -> None:
        """Test import with 'issues' field instead of 'items'."""
        from tracertm.services.github_import_service import GitHubImportService

        mock_session = MagicMock()
        service = GitHubImportService(mock_session)

        mock_project = MagicMock()
        mock_project.id = "proj-123"
        service.projects.create = AsyncMock(return_value=mock_project)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()
        service.links.create = AsyncMock()

        valid_data = json.dumps({"issues": [{"number": 1, "title": "Issue 1", "state": "open"}]})

        result = await service.import_github_project("test-project", valid_data)

        assert result["success"] is True
        assert result["items_imported"] == 1

    @pytest.mark.asyncio
    async def test_import_github_project_with_pull_requests(self) -> None:
        """Test import with pull requests and links."""
        from tracertm.services.github_import_service import GitHubImportService

        mock_session = MagicMock()
        service = GitHubImportService(mock_session)

        mock_project = MagicMock()
        mock_project.id = "proj-123"
        service.projects.create = AsyncMock(return_value=mock_project)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()

        mock_link = MagicMock()
        service.links.create = AsyncMock(return_value=mock_link)

        valid_data = json.dumps({
            "items": [
                {"id": 1, "title": "Issue 1", "type": "issue", "state": "open"},
                {"id": 2, "title": "PR 1", "type": "pull_request", "state": "closed", "related_issues": [1]},
            ],
        })

        result = await service.import_github_project("test-project", valid_data)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_import_github_project_exception(self) -> None:
        """Test import with exception during processing."""
        from tracertm.services.github_import_service import GitHubImportService

        mock_session = MagicMock()
        service = GitHubImportService(mock_session)

        service.projects.create = AsyncMock(side_effect=Exception("DB error"))

        valid_data = json.dumps({"items": []})

        result = await service.import_github_project("test-project", valid_data)

        assert result["success"] is False
        assert "Import failed" in result["errors"][0]


class TestJiraImportService:
    """Tests for JiraImportService."""

    def test_jira_import_service_import(self) -> None:
        """Test JiraImportService can be imported."""
        from tracertm.services.jira_import_service import JiraImportService

        assert JiraImportService is not None

    def test_jira_import_service_init(self) -> None:
        """Test JiraImportService initialization."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        assert service.session == mock_session
        assert service.projects is not None
        assert service.items is not None
        assert service.links is not None
        assert service.events is not None

    def test_jira_status_map(self) -> None:
        """Test STATUS_MAP contains expected mappings."""
        from tracertm.services.jira_import_service import JiraImportService

        assert JiraImportService.STATUS_MAP["To Do"] == "todo"
        assert JiraImportService.STATUS_MAP["In Progress"] == "in_progress"
        assert JiraImportService.STATUS_MAP["Done"] == "complete"
        assert JiraImportService.STATUS_MAP["Closed"] == "complete"

    def test_jira_type_map(self) -> None:
        """Test TYPE_MAP contains expected mappings."""
        from tracertm.services.jira_import_service import JiraImportService

        assert JiraImportService.TYPE_MAP["Epic"] == "epic"
        assert JiraImportService.TYPE_MAP["Story"] == "story"
        assert JiraImportService.TYPE_MAP["Task"] == "task"
        assert JiraImportService.TYPE_MAP["Bug"] == "bug"
        assert JiraImportService.TYPE_MAP["Sub-task"] == "subtask"

    def test_jira_link_type_map(self) -> None:
        """Test LINK_TYPE_MAP contains expected mappings."""
        from tracertm.services.jira_import_service import JiraImportService

        assert JiraImportService.LINK_TYPE_MAP["relates to"] == "relates_to"
        assert JiraImportService.LINK_TYPE_MAP["blocks"] == "blocks"
        assert JiraImportService.LINK_TYPE_MAP["implements"] == "implements"

    @pytest.mark.asyncio
    async def test_validate_jira_export_invalid_json(self) -> None:
        """Test validation with invalid JSON."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        errors = await service.validate_jira_export("not valid json")

        assert len(errors) == 1
        assert "Invalid JSON" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_jira_export_missing_issues(self) -> None:
        """Test validation with missing issues field."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        errors = await service.validate_jira_export('{"name": "test"}')

        assert len(errors) >= 1
        assert any("Missing 'issues'" in e for e in errors)

    @pytest.mark.asyncio
    async def test_validate_jira_export_issues_not_list(self) -> None:
        """Test validation with issues not a list."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        errors = await service.validate_jira_export('{"issues": "not a list"}')

        assert len(errors) >= 1
        assert any("must be a list" in e for e in errors)

    @pytest.mark.asyncio
    async def test_validate_jira_export_issue_missing_key(self) -> None:
        """Test validation with issue missing key field."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        errors = await service.validate_jira_export('{"issues": [{"fields": {}}]}')

        assert len(errors) >= 1
        assert any("missing 'key'" in e for e in errors)

    @pytest.mark.asyncio
    async def test_validate_jira_export_valid(self) -> None:
        """Test validation with valid data."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        valid_data = json.dumps({"issues": [{"key": "TEST-1", "id": "10001", "fields": {"summary": "Test"}}]})
        errors = await service.validate_jira_export(valid_data)

        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_import_jira_project_validation_fails(self) -> None:
        """Test import with validation failures."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        result = await service.import_jira_project("test-project", "invalid json")

        assert result["success"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_import_jira_project_success(self) -> None:
        """Test successful Jira project import."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_project = MagicMock()
        mock_project.id = "proj-123"
        service.projects.create = AsyncMock(return_value=mock_project)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()
        service.links.create = AsyncMock()

        valid_data = json.dumps({
            "issues": [
                {
                    "key": "TEST-1",
                    "id": "10001",
                    "fields": {
                        "summary": "Test Issue",
                        "description": "Description",
                        "status": {"name": "To Do"},
                        "issuetype": {"name": "Story"},
                    },
                },
            ],
        })

        result = await service.import_jira_project("test-project", valid_data)

        assert result["success"] is True
        assert result["project_id"] == "proj-123"
        assert result["items_imported"] == 1

    @pytest.mark.asyncio
    async def test_import_jira_project_with_links(self) -> None:
        """Test import with issue links."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_project = MagicMock()
        mock_project.id = "proj-123"
        service.projects.create = AsyncMock(return_value=mock_project)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()

        mock_link = MagicMock()
        service.links.create = AsyncMock(return_value=mock_link)

        valid_data = json.dumps({
            "issues": [
                {"key": "TEST-1", "id": "10001", "fields": {"summary": "Test Issue 1", "issuelinks": []}},
                {
                    "key": "TEST-2",
                    "id": "10002",
                    "fields": {
                        "summary": "Test Issue 2",
                        "issuelinks": [{"type": {"name": "blocks"}, "outwardIssue": {"key": "TEST-1"}}],
                    },
                },
            ],
        })

        result = await service.import_jira_project("test-project", valid_data)

        assert result["success"] is True
        assert result["items_imported"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_import_jira_project_with_inward_links(self) -> None:
        """Test import with inward issue links."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_project = MagicMock()
        mock_project.id = "proj-123"
        service.projects.create = AsyncMock(return_value=mock_project)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()

        mock_link = MagicMock()
        service.links.create = AsyncMock(return_value=mock_link)

        valid_data = json.dumps({
            "issues": [
                {
                    "key": "TEST-1",
                    "id": "10001",
                    "fields": {
                        "summary": "Test Issue 1",
                        "issuelinks": [{"type": {"name": "relates to"}, "inwardIssue": {"key": "TEST-2"}}],
                    },
                },
                {"key": "TEST-2", "id": "10002", "fields": {"summary": "Test Issue 2", "issuelinks": []}},
            ],
        })

        result = await service.import_jira_project("test-project", valid_data)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_import_jira_project_exception(self) -> None:
        """Test import with exception during processing."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        service.projects.create = AsyncMock(side_effect=Exception("DB error"))

        valid_data = json.dumps({"issues": []})

        result = await service.import_jira_project("test-project", valid_data)

        assert result["success"] is False
        assert "Import failed" in result["errors"][0]
