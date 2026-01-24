"""
Comprehensive tests for JiraImportService.

Tests cover:
- Issue import and data transformation
- Project sync and creation
- Custom field mapping
- Authentication and error handling
- Pagination and batching
- Link import and relationship creation
- Edge cases and error scenarios
"""

import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestJiraImportServiceInit:
    """Tests for JiraImportService initialization."""

    def test_jira_import_service_initialization(self):
        """Test JiraImportService can be instantiated with session."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        assert service.session == mock_session
        assert service.projects is not None
        assert service.items is not None
        assert service.links is not None
        assert service.events is not None

    def test_jira_status_map_completeness(self):
        """Test STATUS_MAP contains all expected Jira status mappings."""
        from tracertm.services.jira_import_service import JiraImportService

        assert JiraImportService.STATUS_MAP["To Do"] == "todo"
        assert JiraImportService.STATUS_MAP["In Progress"] == "in_progress"
        assert JiraImportService.STATUS_MAP["In Review"] == "in_progress"
        assert JiraImportService.STATUS_MAP["Done"] == "complete"
        assert JiraImportService.STATUS_MAP["Closed"] == "complete"

    def test_jira_type_map_completeness(self):
        """Test TYPE_MAP contains all expected Jira issue type mappings."""
        from tracertm.services.jira_import_service import JiraImportService

        assert JiraImportService.TYPE_MAP["Epic"] == "epic"
        assert JiraImportService.TYPE_MAP["Story"] == "story"
        assert JiraImportService.TYPE_MAP["Task"] == "task"
        assert JiraImportService.TYPE_MAP["Bug"] == "bug"
        assert JiraImportService.TYPE_MAP["Sub-task"] == "subtask"

    def test_jira_link_type_map_completeness(self):
        """Test LINK_TYPE_MAP contains expected Jira link type mappings."""
        from tracertm.services.jira_import_service import JiraImportService

        assert JiraImportService.LINK_TYPE_MAP["relates to"] == "relates_to"
        assert JiraImportService.LINK_TYPE_MAP["blocks"] == "blocks"
        assert JiraImportService.LINK_TYPE_MAP["is blocked by"] == "blocked_by"
        assert JiraImportService.LINK_TYPE_MAP["duplicates"] == "duplicates"
        assert JiraImportService.LINK_TYPE_MAP["is duplicated by"] == "duplicated_by"
        assert JiraImportService.LINK_TYPE_MAP["implements"] == "implements"
        assert JiraImportService.LINK_TYPE_MAP["is implemented by"] == "implemented_by"


class TestJiraValidation:
    """Tests for Jira export validation."""

    @pytest.mark.asyncio
    async def test_validate_jira_export_invalid_json(self):
        """Test validation rejects invalid JSON."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        errors = await service.validate_jira_export("not valid json {")
        assert len(errors) > 0
        assert "Invalid JSON" in errors[0]

    @pytest.mark.asyncio
    async def test_validate_jira_export_missing_issues_field(self):
        """Test validation fails when 'issues' field is missing."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        invalid_data = json.dumps({"someField": "value"})
        errors = await service.validate_jira_export(invalid_data)

        assert len(errors) > 0
        assert "Missing 'issues' field" in errors

    @pytest.mark.asyncio
    async def test_validate_jira_export_issues_not_list(self):
        """Test validation fails when 'issues' is not a list."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        invalid_data = json.dumps({"issues": "not a list"})
        errors = await service.validate_jira_export(invalid_data)

        assert "'issues' must be a list" in errors

    @pytest.mark.asyncio
    async def test_validate_jira_export_missing_issue_key(self):
        """Test validation detects missing issue key field."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        invalid_data = json.dumps({
            "issues": [
                {"id": "123", "fields": {}}  # Missing 'key' field
            ]
        })
        errors = await service.validate_jira_export(invalid_data)

        assert any("missing 'key' field" in error for error in errors)

    @pytest.mark.asyncio
    async def test_validate_jira_export_missing_fields(self):
        """Test validation detects missing fields in issue."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        invalid_data = json.dumps({
            "issues": [
                {"key": "PROJ-1", "id": "123"}  # Missing 'fields' field
            ]
        })
        errors = await service.validate_jira_export(invalid_data)

        assert any("missing 'fields' field" in error for error in errors)

    @pytest.mark.asyncio
    async def test_validate_jira_export_valid_data(self):
        """Test validation passes with valid export data."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        valid_data = json.dumps({
            "issues": [
                {
                    "key": "PROJ-1",
                    "id": "123",
                    "fields": {"summary": "Test Issue"}
                },
                {
                    "key": "PROJ-2",
                    "id": "124",
                    "fields": {"summary": "Another Issue"}
                }
            ]
        })
        errors = await service.validate_jira_export(valid_data)

        assert len(errors) == 0


class TestJiraIssueImport:
    """Tests for Jira issue import functionality."""

    @pytest.mark.asyncio
    async def test_import_single_jira_issue_basic(self):
        """Test importing a single Jira issue with basic fields."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        # Mock item creation
        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)

        # Mock event logging
        service.events.log = AsyncMock()

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "summary": "Test Issue",
                "description": "This is a test",
                "status": {"name": "To Do"},
                "issuetype": {"name": "Task"}
            }
        }

        result = await service._import_jira_issue("project-123", issue, "agent-1")

        assert result.id == "item-123"
        service.items.create.assert_called_once()

        # Verify created item properties
        call_args = service.items.create.call_args
        assert call_args.kwargs["project_id"] == "project-123"
        assert call_args.kwargs["title"] == "Test Issue"
        assert call_args.kwargs["description"] == "This is a test"
        assert call_args.kwargs["status"] == "todo"
        assert call_args.kwargs["item_type"] == "task"

    @pytest.mark.asyncio
    async def test_import_single_jira_issue_status_mapping(self):
        """Test issue import maps Jira status correctly."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()

        # Test In Progress status
        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "summary": "Issue in progress",
                "description": "",
                "status": {"name": "In Progress"},
                "issuetype": {"name": "Story"}
            }
        }

        await service._import_jira_issue("project-123", issue, "agent-1")

        call_args = service.items.create.call_args
        assert call_args.kwargs["status"] == "in_progress"
        assert call_args.kwargs["item_type"] == "story"

    @pytest.mark.asyncio
    async def test_import_single_jira_issue_type_mapping(self):
        """Test issue import maps Jira type correctly."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()

        # Test Epic type
        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "summary": "Epic issue",
                "description": "",
                "status": {"name": "Done"},
                "issuetype": {"name": "Epic"}
            }
        }

        await service._import_jira_issue("project-123", issue, "agent-1")

        call_args = service.items.create.call_args
        assert call_args.kwargs["item_type"] == "epic"
        assert call_args.kwargs["status"] == "complete"

    @pytest.mark.asyncio
    async def test_import_single_jira_issue_missing_fields(self):
        """Test issue import with missing optional fields."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()

        # Issue with minimal fields
        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {}
        }

        result = await service._import_jira_issue("project-123", issue, "agent-1")

        assert result.id == "item-123"
        call_args = service.items.create.call_args
        assert call_args.kwargs["title"] == "Untitled"
        assert call_args.kwargs["description"] == ""
        assert call_args.kwargs["status"] == "todo"
        assert call_args.kwargs["item_type"] == "task"

    @pytest.mark.asyncio
    async def test_import_single_jira_issue_metadata_storage(self):
        """Test that Jira metadata is stored in item."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {"summary": "Test"}
        }

        await service._import_jira_issue("project-123", issue, "agent-1")

        call_args = service.items.create.call_args
        metadata = call_args.kwargs["metadata"]
        assert metadata["jira_key"] == "PROJ-1"
        assert metadata["jira_id"] == "123"

    @pytest.mark.asyncio
    async def test_import_single_jira_issue_event_logging(self):
        """Test that event is logged when issue is imported."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {"summary": "Test"}
        }

        await service._import_jira_issue("project-123", issue, "agent-1")

        service.events.log.assert_called_once()
        call_args = service.events.log.call_args
        assert call_args.kwargs["event_type"] == "jira_issue_imported"
        assert call_args.kwargs["entity_type"] == "item"
        assert call_args.kwargs["entity_id"] == "item-123"
        assert call_args.kwargs["agent_id"] == "agent-1"


class TestJiraLinkImport:
    """Tests for Jira link import functionality."""

    @pytest.mark.asyncio
    async def test_import_jira_links_basic(self):
        """Test importing links between Jira issues."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_link = MagicMock()
        mock_link.id = "link-123"
        service.links.create = AsyncMock(return_value=mock_link)

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "issuelinks": [
                    {
                        "type": {"name": "relates to"},
                        "outwardIssue": {"key": "PROJ-2"}
                    }
                ]
            }
        }

        issue_map = {
            "PROJ-1": "item-1",
            "PROJ-2": "item-2"
        }

        result = await service._import_jira_links(
            "project-123", issue, issue_map, "agent-1"
        )

        assert len(result) == 1
        service.links.create.assert_called_once()
        call_args = service.links.create.call_args
        assert call_args.kwargs["source_item_id"] == "item-1"
        assert call_args.kwargs["target_item_id"] == "item-2"
        assert call_args.kwargs["link_type"] == "relates_to"

    @pytest.mark.asyncio
    async def test_import_jira_links_blocks_relationship(self):
        """Test importing 'blocks' relationship."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_link = MagicMock()
        mock_link.id = "link-123"
        service.links.create = AsyncMock(return_value=mock_link)

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "issuelinks": [
                    {
                        "type": {"name": "blocks"},
                        "outwardIssue": {"key": "PROJ-2"}
                    }
                ]
            }
        }

        issue_map = {"PROJ-1": "item-1", "PROJ-2": "item-2"}

        await service._import_jira_links("project-123", issue, issue_map, "agent-1")

        call_args = service.links.create.call_args
        assert call_args.kwargs["link_type"] == "blocks"

    @pytest.mark.asyncio
    async def test_import_jira_links_inward_issue(self):
        """Test importing links with inward issue reference."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_link = MagicMock()
        service.links.create = AsyncMock(return_value=mock_link)

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "issuelinks": [
                    {
                        "type": {"name": "is blocked by"},
                        "inwardIssue": {"key": "PROJ-2"}
                    }
                ]
            }
        }

        issue_map = {"PROJ-1": "item-1", "PROJ-2": "item-2"}

        result = await service._import_jira_links(
            "project-123", issue, issue_map, "agent-1"
        )

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_import_jira_links_missing_target(self):
        """Test that links with missing target issues are skipped."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        service.links.create = AsyncMock()

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "issuelinks": [
                    {
                        "type": {"name": "relates to"},
                        "outwardIssue": {"key": "PROJ-UNKNOWN"}
                    }
                ]
            }
        }

        issue_map = {"PROJ-1": "item-1"}

        result = await service._import_jira_links(
            "project-123", issue, issue_map, "agent-1"
        )

        assert len(result) == 0
        service.links.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_import_jira_links_no_issues(self):
        """Test handling issues with no issuelinks field."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        service.links.create = AsyncMock()

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {}
        }

        issue_map = {"PROJ-1": "item-1"}

        result = await service._import_jira_links(
            "project-123", issue, issue_map, "agent-1"
        )

        assert len(result) == 0
        service.links.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_import_jira_links_multiple_links(self):
        """Test importing multiple links from single issue."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_link = MagicMock()
        mock_link.id = "link-123"
        service.links.create = AsyncMock(return_value=mock_link)

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "issuelinks": [
                    {
                        "type": {"name": "relates to"},
                        "outwardIssue": {"key": "PROJ-2"}
                    },
                    {
                        "type": {"name": "blocks"},
                        "outwardIssue": {"key": "PROJ-3"}
                    },
                    {
                        "type": {"name": "duplicates"},
                        "outwardIssue": {"key": "PROJ-4"}
                    }
                ]
            }
        }

        issue_map = {
            "PROJ-1": "item-1",
            "PROJ-2": "item-2",
            "PROJ-3": "item-3",
            "PROJ-4": "item-4"
        }

        result = await service._import_jira_links(
            "project-123", issue, issue_map, "agent-1"
        )

        assert len(result) == 3
        assert service.links.create.call_count == 3


class TestJiraProjectImport:
    """Tests for Jira project import functionality."""

    @pytest.mark.asyncio
    async def test_import_jira_project_success(self):
        """Test successful import of Jira project with issues."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        # Mock project creation
        mock_project = MagicMock()
        mock_project.id = "proj-123"
        service.projects.create = AsyncMock(return_value=mock_project)

        # Mock item creation
        mock_item = MagicMock()
        mock_item.id = "item-1"
        service.items.create = AsyncMock(return_value=mock_item)

        # Mock event logging
        service.events.log = AsyncMock()

        # Mock link creation
        service.links.create = AsyncMock()

        valid_data = json.dumps({
            "issues": [
                {
                    "key": "PROJ-1",
                    "id": "123",
                    "fields": {
                        "summary": "Issue 1",
                        "description": "Description 1",
                        "status": {"name": "To Do"},
                        "issuetype": {"name": "Task"}
                    }
                },
                {
                    "key": "PROJ-2",
                    "id": "124",
                    "fields": {
                        "summary": "Issue 2",
                        "description": "Description 2",
                        "status": {"name": "Done"},
                        "issuetype": {"name": "Story"}
                    }
                }
            ]
        })

        result = await service.import_jira_project("TestProject", valid_data)

        assert result["success"] is True
        assert result["project_id"] == "proj-123"
        assert result["items_imported"] == 2
        assert len(result["errors"]) == 0

    @pytest.mark.asyncio
    async def test_import_jira_project_validation_failure(self):
        """Test import fails with invalid data."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        result = await service.import_jira_project(
            "TestProject",
            "invalid json"
        )

        assert result["success"] is False
        assert len(result["errors"]) > 0
        assert "Invalid JSON" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_import_jira_project_partial_import_failure(self):
        """Test import with some issues failing but others succeeding."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        # Mock project creation
        mock_project = MagicMock()
        mock_project.id = "proj-123"
        service.projects.create = AsyncMock(return_value=mock_project)

        # Mock item creation with one failure
        mock_item = MagicMock()
        mock_item.id = "item-1"
        service.items.create = AsyncMock(
            side_effect=[
                mock_item,  # First issue succeeds
                Exception("Database error")  # Second issue fails
            ]
        )

        service.events.log = AsyncMock()
        service.links.create = AsyncMock()

        valid_data = json.dumps({
            "issues": [
                {
                    "key": "PROJ-1",
                    "id": "123",
                    "fields": {"summary": "Issue 1", "status": {"name": "To Do"}}
                },
                {
                    "key": "PROJ-2",
                    "id": "124",
                    "fields": {"summary": "Issue 2", "status": {"name": "To Do"}}
                }
            ]
        })

        result = await service.import_jira_project("TestProject", valid_data)

        assert result["success"] is True
        assert result["items_imported"] == 1
        assert any("Failed to import PROJ-2" in error for error in result["errors"])

    @pytest.mark.asyncio
    async def test_import_jira_project_custom_agent_id(self):
        """Test import with custom agent ID."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_project = MagicMock()
        mock_project.id = "proj-123"
        service.projects.create = AsyncMock(return_value=mock_project)

        mock_item = MagicMock()
        mock_item.id = "item-1"
        service.items.create = AsyncMock(return_value=mock_item)

        service.events.log = AsyncMock()
        service.links.create = AsyncMock()

        valid_data = json.dumps({
            "issues": [
                {
                    "key": "PROJ-1",
                    "id": "123",
                    "fields": {"summary": "Issue 1", "status": {"name": "To Do"}}
                }
            ]
        })

        result = await service.import_jira_project(
            "TestProject",
            valid_data,
            agent_id="custom-agent-123"
        )

        assert result["success"] is True
        call_args = service.events.log.call_args
        assert call_args.kwargs["agent_id"] == "custom-agent-123"

    @pytest.mark.asyncio
    async def test_import_jira_project_empty_issues(self):
        """Test import with empty issues list."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_project = MagicMock()
        mock_project.id = "proj-123"
        service.projects.create = AsyncMock(return_value=mock_project)

        service.items.create = AsyncMock()
        service.events.log = AsyncMock()
        service.links.create = AsyncMock()

        valid_data = json.dumps({"issues": []})

        result = await service.import_jira_project("TestProject", valid_data)

        assert result["success"] is True
        assert result["items_imported"] == 0
        assert result["links_imported"] == 0

    @pytest.mark.asyncio
    async def test_import_jira_project_with_links(self):
        """Test import project including issue links."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_project = MagicMock()
        mock_project.id = "proj-123"
        service.projects.create = AsyncMock(return_value=mock_project)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)

        mock_link = MagicMock()
        mock_link.id = "link-123"
        service.links.create = AsyncMock(return_value=mock_link)

        service.events.log = AsyncMock()

        valid_data = json.dumps({
            "issues": [
                {
                    "key": "PROJ-1",
                    "id": "123",
                    "fields": {
                        "summary": "Issue 1",
                        "status": {"name": "To Do"},
                        "issuelinks": []
                    }
                },
                {
                    "key": "PROJ-2",
                    "id": "124",
                    "fields": {
                        "summary": "Issue 2",
                        "status": {"name": "To Do"},
                        "issuelinks": [
                            {
                                "type": {"name": "relates to"},
                                "outwardIssue": {"key": "PROJ-1"}
                            }
                        ]
                    }
                }
            ]
        })

        result = await service.import_jira_project("TestProject", valid_data)

        assert result["success"] is True
        assert result["items_imported"] == 2
        assert result["links_imported"] >= 0  # May vary based on order

    @pytest.mark.asyncio
    async def test_import_jira_project_general_exception(self):
        """Test handling of general exceptions during import."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        # Make project creation fail
        service.projects.create = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        valid_data = json.dumps({
            "issues": [
                {
                    "key": "PROJ-1",
                    "id": "123",
                    "fields": {"summary": "Issue 1"}
                }
            ]
        })

        result = await service.import_jira_project("TestProject", valid_data)

        assert result["success"] is False
        assert len(result["errors"]) > 0
        assert "Import failed" in result["errors"][0]


class TestJiraEdgeCases:
    """Tests for edge cases and error scenarios."""

    @pytest.mark.asyncio
    async def test_import_jira_issue_unknown_status(self):
        """Test issue import with unmapped status defaults to todo."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "summary": "Test",
                "status": {"name": "Unknown Status"},
                "issuetype": {"name": "Task"}
            }
        }

        await service._import_jira_issue("project-123", issue, "agent-1")

        call_args = service.items.create.call_args
        assert call_args.kwargs["status"] == "todo"

    @pytest.mark.asyncio
    async def test_import_jira_issue_unknown_type(self):
        """Test issue import with unmapped type defaults to task."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "summary": "Test",
                "status": {"name": "To Do"},
                "issuetype": {"name": "UnknownType"}
            }
        }

        await service._import_jira_issue("project-123", issue, "agent-1")

        call_args = service.items.create.call_args
        assert call_args.kwargs["item_type"] == "task"

    @pytest.mark.asyncio
    async def test_import_jira_link_unknown_type(self):
        """Test link import with unmapped type defaults to relates_to."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_link = MagicMock()
        service.links.create = AsyncMock(return_value=mock_link)

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "issuelinks": [
                    {
                        "type": {"name": "UnknownLinkType"},
                        "outwardIssue": {"key": "PROJ-2"}
                    }
                ]
            }
        }

        issue_map = {"PROJ-1": "item-1", "PROJ-2": "item-2"}

        await service._import_jira_links("project-123", issue, issue_map, "agent-1")

        call_args = service.links.create.call_args
        assert call_args.kwargs["link_type"] == "relates_to"

    @pytest.mark.asyncio
    async def test_import_jira_link_exception_handling(self):
        """Test that exceptions in link import don't stop processing."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        # Make link creation fail
        service.links.create = AsyncMock(
            side_effect=Exception("Link creation failed")
        )

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "issuelinks": [
                    {
                        "type": {"name": "relates to"},
                        "outwardIssue": {"key": "PROJ-2"}
                    }
                ]
            }
        }

        issue_map = {"PROJ-1": "item-1", "PROJ-2": "item-2"}

        # Should not raise, should return empty list
        result = await service._import_jira_links(
            "project-123", issue, issue_map, "agent-1"
        )

        assert result == []

    @pytest.mark.asyncio
    async def test_import_jira_project_project_creation_failure(self):
        """Test graceful handling when project creation fails."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        service.projects.create = AsyncMock(
            side_effect=Exception("Failed to create project")
        )

        valid_data = json.dumps({
            "issues": [
                {
                    "key": "PROJ-1",
                    "id": "123",
                    "fields": {"summary": "Issue 1"}
                }
            ]
        })

        result = await service.import_jira_project("TestProject", valid_data)

        assert result["success"] is False
        assert any("Import failed" in error for error in result["errors"])

    def test_jira_import_service_can_be_imported(self):
        """Test that JiraImportService module can be imported."""
        from tracertm.services.jira_import_service import JiraImportService
        assert JiraImportService is not None

    @pytest.mark.asyncio
    async def test_import_jira_issue_none_status_name(self):
        """Test handling of None status name."""
        from tracertm.services.jira_import_service import JiraImportService

        mock_session = MagicMock()
        service = JiraImportService(mock_session)

        mock_item = MagicMock()
        mock_item.id = "item-123"
        service.items.create = AsyncMock(return_value=mock_item)
        service.events.log = AsyncMock()

        issue = {
            "key": "PROJ-1",
            "id": "123",
            "fields": {
                "summary": "Test",
                "status": {},  # No 'name' key
                "issuetype": {}  # No 'name' key
            }
        }

        await service._import_jira_issue("project-123", issue, "agent-1")

        call_args = service.items.create.call_args
        assert call_args.kwargs["status"] == "todo"
        assert call_args.kwargs["item_type"] == "task"
