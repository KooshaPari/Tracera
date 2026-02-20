"""Service for importing projects from GitHub."""

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


class GitHubImportService:
    """Service for importing GitHub Projects.

    Functional Requirements:
    - FR-DISC-001

    User Stories:
    - US-INT-001

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

    # GitHub to TraceRTM status mapping
    STATUS_MAP: ClassVar[dict[str, str]] = {
        "open": "todo",
        "in_progress": "in_progress",
        "in review": "in_progress",
        "closed": "complete",
        "done": "complete",
    }

    # GitHub to TraceRTM type mapping
    TYPE_MAP: ClassVar[dict[str, str]] = {
        "issue": "task",
        "pull_request": "task",
        "discussion": "task",
    }

    async def validate_github_export(self, json_data: str) -> list[str]:
        """Validate GitHub export JSON format."""
        errors = []

        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            return [f"Invalid JSON: {e!s}"]

        # Check required fields
        if "items" not in data and "issues" not in data:
            errors.append("Missing 'items' or 'issues' field")

        return errors

    async def import_github_project(
        self,
        project_name: str,
        json_data: str,
        agent_id: str = "system",
    ) -> dict[str, Any]:
        """Import GitHub project."""
        # Validate
        errors = await self.validate_github_export(json_data)
        if errors:
            return {"success": False, "errors": errors}

        try:
            data = json.loads(json_data)

            # Create project
            project = await self.projects.create(
                name=project_name,
                description="Imported from GitHub",
            )

            # Import items
            item_map = {}  # GitHub ID -> TraceRTM ID
            items_imported = 0

            items_list = data.get("items", data.get("issues", []))
            for item_data in items_list:
                try:
                    project_id = str(project.id)
                    item = await self._import_github_item(project_id, item_data, agent_id)
                    item_map[item_data.get("id", item_data.get("number"))] = item.id
                    items_imported += 1
                except (ValueError, KeyError, ConcurrencyError, OperationalError) as e:
                    logger.warning("Failed to import item %s: %s", item_data.get("id", "unknown"), e)
                    errors.append(f"Failed to import item: {e!s}")

            # Import links (PRs linked to issues)
            links_imported = 0
            for item_data in items_list:
                try:
                    links = await self._import_github_links(project_id, item_data, item_map, agent_id)
                    links_imported += len(links)
                except (ValueError, KeyError, ConcurrencyError, OperationalError) as e:
                    logger.warning("Failed to import links for item %s: %s", item_data.get("id", "unknown"), e)
                    errors.append(f"Failed to import links: {e!s}")

        except (json.JSONDecodeError, ValueError, KeyError, OperationalError) as e:
            logger.exception("GitHub import failed")
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

    async def _import_github_item(
        self,
        project_id: str,
        item_data: dict[str, Any],
        agent_id: str,
    ) -> object:
        """Import single GitHub item."""
        # Map fields
        title = item_data.get("title", "Untitled")
        description = item_data.get("body", "")
        status = self.STATUS_MAP.get(item_data.get("state", "open").lower(), "todo")
        item_type = self.TYPE_MAP.get(item_data.get("type", "issue").lower(), "task")

        # Create item
        item = await self.items.create(
            project_id=project_id,
            title=title,
            description=description,
            view="FEATURE",
            item_type=item_type,
            status=status,
            metadata={
                "github_id": item_data.get("id"),
                "github_number": item_data.get("number"),
                "github_url": item_data.get("url"),
            },
        )

        # Log event
        await self.events.log(
            project_id=project_id,
            event_type="github_item_imported",
            entity_type="item",
            entity_id=str(item.id),
            data={"github_number": item_data.get("number")},
            agent_id=agent_id,
        )

        return item

    async def _import_github_links(
        self,
        project_id: str,
        item_data: dict[str, Any],
        item_map: dict[str, str],
        _agent_id: str,
    ) -> list[object]:
        """Import GitHub item links (PRs to issues)."""
        links = []

        # Link PRs to related issues
        if item_data.get("type") == "pull_request":
            related_issues = item_data.get("related_issues", [])
            item_id = item_data.get("id")
            source_id = item_map.get(item_id) if isinstance(item_id, str) else None

            for issue_id in related_issues:
                target_id = item_map.get(issue_id)
                if source_id and target_id:
                    try:
                        link = await self.links.create(
                            project_id=project_id,
                            source_item_id=source_id,
                            target_item_id=target_id,
                            link_type="implements",
                        )
                        links.append(link)
                    except (ValueError, ConcurrencyError, OperationalError) as e:
                        logger.debug("Link creation skipped: %s", e)

        return links
