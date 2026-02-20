"""Import service for TraceRTM data.

Functional Requirements: FR-DISC-003, FR-DISC-007
"""

import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository


class ImportService:
    """Service for importing TraceRTM data."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.projects = ProjectRepository(session)
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)

    async def import_from_json(self, json_data: str) -> dict[str, Any]:
        """Import project from JSON format."""
        data = json.loads(json_data)

        # Create or get project
        project_data = data.get("project", {})
        project = await self.projects.get_by_name(project_data.get("name"))

        if not project:
            project = await self.projects.create(
                name=project_data.get("name"),
                description=project_data.get("description"),
            )

        # Import items
        item_map = {}
        for item_data in data.get("items", []):
            item = await self.items.create(
                project_id=str(project.id),
                title=item_data.get("title"),
                view=item_data.get("view"),
                item_type=item_data.get("type"),
                status=item_data.get("status"),
                description=item_data.get("description"),
            )
            item_map[item_data.get("id")] = item.id

        # Import links
        for link_data in data.get("links", []):
            source_id = item_map.get(link_data.get("source_id"))
            target_id = item_map.get(link_data.get("target_id"))

            if source_id and target_id:
                await self.links.create(
                    project_id=str(project.id),
                    source_item_id=str(source_id),
                    target_item_id=str(target_id),
                    link_type=link_data.get("type", "relates_to"),
                )

        return {
            "project_id": project.id,
            "items_imported": len(item_map),
            "links_imported": len(data.get("links", [])),
        }

    async def import_items_from_csv(
        self,
        project_id: str,
        csv_data: str,
    ) -> dict[str, Any]:
        """Import items from CSV format."""
        import csv
        from io import StringIO

        reader = csv.DictReader(StringIO(csv_data))
        imported = 0

        for row in reader:
            title = row.get("Title", "")
            view = row.get("View", "FEATURE")
            item_type = row.get("Type", "task")
            status = row.get("Status", "todo")
            await self.items.create(
                project_id=project_id,
                title=title if isinstance(title, str) else "",
                view=view if isinstance(view, str) else "FEATURE",
                item_type=item_type if isinstance(item_type, str) else "task",
                status=status if isinstance(status, str) else "todo",
                description=row.get("Description"),
            )
            imported += 1

        return {"items_imported": imported}

    def _validate_project_section(self, data: dict) -> list[str]:
        """Validate project section; return list of errors."""
        errors: list[str] = []
        if "project" not in data:
            errors.append("Missing 'project' section")
            return errors
        project = data["project"]
        if not project.get("name"):
            errors.append("Project name is required")
        return errors

    def _validate_items_section(self, items: list[dict]) -> list[str]:
        """Validate items list; return list of errors."""
        errors: list[str] = []
        for i, item in enumerate(items):
            if not item.get("title"):
                errors.append(f"Item {i}: title is required")
            if not item.get("view"):
                errors.append(f"Item {i}: view is required")
        return errors

    def _validate_links_section(self, links: list[dict], item_ids: set[str | None]) -> list[str]:
        """Validate links reference existing items; return list of errors."""
        errors: list[str] = []
        for i, link in enumerate(links):
            source = link.get("source_id")
            target = link.get("target_id")
            if source not in item_ids:
                errors.append(f"Link {i}: source_id '{source}' not found in items")
            if target not in item_ids:
                errors.append(f"Link {i}: target_id '{target}' not found in items")
        return errors

    async def validate_import_data(self, json_data: str) -> list[str]:
        """Validate import data and return list of errors."""
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            return [f"Invalid JSON: {e!s}"]

        errors: list[str] = []
        errors.extend(self._validate_project_section(data))

        items = data.get("items", [])
        errors.extend(self._validate_items_section(items))

        item_ids = {item.get("id") for item in items}
        links = data.get("links", [])
        errors.extend(self._validate_links_section(links, item_ids))

        return errors
