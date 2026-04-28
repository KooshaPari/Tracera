"""Service for importing projects from Jira."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, ClassVar

from sqlalchemy.exc import OperationalError

from tracertm.core.concurrency import ConcurrencyError
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class JiraImportService:
    """Service for importing Jira projects.

    Functional Requirements:
    - FR-COLLAB-002

    User Stories:
    - US-INT-002

    Epics:
    - EPIC-001
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.projects = ProjectRepository(session)
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)
        self.events = EventRepository(session)

    # Jira to TraceRTM status mapping
    STATUS_MAP: ClassVar[dict[str, str]] = {
        "To Do": "todo",
        "In Progress": "in_progress",
        "In Review": "in_progress",
        "Done": "complete",
        "Closed": "complete",
    }

    # Jira to TraceRTM type mapping
    TYPE_MAP: ClassVar[dict[str, str]] = {
        "Epic": "epic",
        "Story": "story",
        "Task": "task",
        "Bug": "bug",
        "Sub-task": "subtask",
    }

    # Jira to TraceRTM link type mapping
    LINK_TYPE_MAP: ClassVar[dict[str, str]] = {
        "relates to": "relates_to",
        "blocks": "blocks",
        "is blocked by": "blocked_by",
        "duplicates": "duplicates",
        "is duplicated by": "duplicated_by",
        "implements": "implements",
        "is implemented by": "implemented_by",
    }

    async def validate_jira_export(self, json_data: str) -> list[str]:
        """Validate Jira export JSON format."""
        errors = []

        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            return [f"Invalid JSON: {e!s}"]

        # Check required fields
        if "issues" not in data:
            errors.append("Missing 'issues' field")

        if not isinstance(data.get("issues"), list):
            errors.append("'issues' must be a list")

        # Validate each issue
        for i, issue in enumerate(data.get("issues", [])):
            if "key" not in issue:
                errors.append(f"Issue {i} missing 'key' field")
            if "fields" not in issue:
                errors.append(f"Issue {i} missing 'fields' field")

        return errors

    async def import_jira_project(
        self,
        project_name: str,
        json_data: str,
        agent_id: str = "system",
    ) -> dict[str, Any]:
        """Import Jira project."""
        # Validate
        errors = await self.validate_jira_export(json_data)
        if errors:
            return {"success": False, "errors": errors}

        try:
            data = json.loads(json_data)

            # Create project
            project = await self.projects.create(
                name=project_name,
                description="Imported from Jira",
            )

            # Import issues
            issue_map = {}  # Jira key -> TraceRTM ID
            items_imported = 0

            for issue in data.get("issues", []):
                try:
                    project_id = str(project.id)
                    item = await self._import_jira_issue(project_id, issue, agent_id)
                    issue_map[issue["key"]] = item.id
                    items_imported += 1
                except (ValueError, KeyError, ConcurrencyError, OperationalError) as e:
                    logger.warning("Failed to import issue %s: %s", issue.get("key", "unknown"), e)
                    errors.append(f"Failed to import {issue['key']}: {e!s}")

            # Import links
            links_imported = 0
            for issue in data.get("issues", []):
                try:
                    links = await self._import_jira_links(str(project.id), issue, issue_map, agent_id)
                    links_imported += len(links)
                except (ValueError, KeyError, ConcurrencyError, OperationalError) as e:
                    logger.warning("Failed to import links for issue %s: %s", issue.get("key", "unknown"), e)
                    errors.append(f"Failed to import links for {issue['key']}: {e!s}")

        except (json.JSONDecodeError, ValueError, KeyError, OperationalError) as e:
            logger.exception("Jira import failed")
            return {
                "success": False,
                "errors": [f"Import failed: {e!s}"],
            }
        else:
            return {
                "success": True,
                "project_id": project.id,
                "items_imported": items_imported,
                "links_imported": links_imported,
                "errors": errors,
            }

    async def _import_jira_issue(
        self,
        project_id: str,
        issue: dict[str, Any],
        agent_id: str,
    ) -> object:
        """Import single Jira issue."""
        fields = issue.get("fields", {})

        # Map fields
        title = fields.get("summary", "Untitled")
        description = fields.get("description", "")
        status = self.STATUS_MAP.get(fields.get("status", {}).get("name", "To Do"), "todo")
        item_type = self.TYPE_MAP.get(fields.get("issuetype", {}).get("name", "Task"), "task")

        # Create item
        item = await self.items.create(
            project_id=project_id,
            title=title,
            description=description,
            view="FEATURE",
            item_type=item_type,
            status=status,
            metadata={
                "jira_key": issue["key"],
                "jira_id": issue["id"],
            },
        )

        # Log event
        await self.events.log(
            project_id=project_id,
            event_type="jira_issue_imported",
            entity_type="item",
            entity_id=str(item.id),
            data={"jira_key": issue["key"]},
            agent_id=agent_id,
        )

        return item

    async def _import_jira_links(
        self,
        project_id: str,
        issue: dict[str, Any],
        issue_map: dict[str, str],
        _agent_id: str,
    ) -> list[object]:
        """Import Jira issue links."""
        links = []
        fields = issue.get("fields", {})

        for link in fields.get("issuelinks", []):
            try:
                link_type = self.LINK_TYPE_MAP.get(link.get("type", {}).get("name", "relates to"), "relates_to")

                # Determine source and target
                if "outwardIssue" in link:
                    target_key = link["outwardIssue"]["key"]
                elif "inwardIssue" in link:
                    target_key = link["inwardIssue"]["key"]
                else:
                    continue

                # Check if target exists
                if target_key not in issue_map:
                    continue

                source_id = issue_map.get(issue["key"])
                target_id = issue_map.get(target_key)

                if source_id and target_id:
                    link_obj = await self.links.create(
                        project_id=project_id,
                        source_item_id=source_id,
                        target_item_id=target_id,
                        link_type=link_type,
                    )
                    links.append(link_obj)
            except (ValueError, ConcurrencyError, OperationalError) as e:
                logger.debug("Link creation skipped: %s", e)

        return links
