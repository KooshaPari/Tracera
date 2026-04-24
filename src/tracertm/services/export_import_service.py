"""Service for export and import functionality.

Functional Requirements: FR-RPT-002, FR-RPT-003, FR-RPT-007
"""

from __future__ import annotations

import csv
import json
import uuid
from io import StringIO
from typing import TYPE_CHECKING, Any

from sqlalchemy.exc import OperationalError

from tracertm.core.concurrency import ConcurrencyError
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class ExportImportService:
    """Service for exporting and importing project data."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)
        self.projects = ProjectRepository(session)

    async def export_to_json(self, project_id: str | uuid.UUID) -> dict[str, Any]:
        """Export project to JSON format."""
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        project = await self.projects.get_by_id(pid)
        if not project:
            return {"error": "Project not found"}

        items = await self.items.query(pid, {})

        items_data = [
            {
                "id": item.id,
                "title": item.title if hasattr(item, "title") else "",
                "view": item.view if hasattr(item, "view") else "",
                "type": item.item_type if hasattr(item, "item_type") else "",
                "status": item.status if hasattr(item, "status") else "",
                "description": (item.description if hasattr(item, "description") else ""),
            }
            for item in items
        ]

        return {
            "format": "json",
            "project": {
                "id": project.id,
                "name": project.name if hasattr(project, "name") else "",
                "description": (project.description if hasattr(project, "description") else ""),
            },
            "items": items_data,
            "item_count": len(items_data),
        }

    async def export_to_csv(self, project_id: str | uuid.UUID) -> dict[str, Any]:
        """Export project to CSV format."""
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        items = await self.items.query(pid, {})

        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["ID", "Title", "View", "Type", "Status", "Description"])

        # Write items
        for item in items:
            writer.writerow([
                item.id,
                item.title if hasattr(item, "title") else "",
                item.view if hasattr(item, "view") else "",
                item.item_type if hasattr(item, "item_type") else "",
                item.status if hasattr(item, "status") else "",
                item.description if hasattr(item, "description") else "",
            ])

        return {
            "format": "csv",
            "content": output.getvalue(),
            "item_count": len(items),
        }

    async def export_to_markdown(self, project_id: str | uuid.UUID) -> dict[str, Any]:
        """Export project to Markdown format."""
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        project = await self.projects.get_by_id(pid)
        if not project:
            return {"error": "Project not found"}

        items = await self.items.query(pid, {})

        md = f"# {project.name if hasattr(project, 'name') else 'Project'}\n\n"
        md += f"{project.description if hasattr(project, 'description') else ''}\n\n"

        # Group by view
        by_view: dict[str, list[dict[str, Any]]] = {}
        for item in items:
            view = item.view if hasattr(item, "view") else "Unknown"
            if view not in by_view:
                by_view[view] = []
            by_view[view].append(item)

        for view, view_items in by_view.items():
            md += f"## {view}\n\n"
            for item in view_items:
                md += f"- **{item.title if hasattr(item, 'title') else 'Unknown'}** "
                md += f"({item.status if hasattr(item, 'status') else 'unknown'})\n"
                if hasattr(item, "description") and item.description:
                    md += f"  - {item.description}\n"
            md += "\n"

        return {
            "format": "markdown",
            "content": md,
            "item_count": len(items),
        }

    async def import_from_json(
        self,
        project_id: str | uuid.UUID,
        json_data: str,
    ) -> dict[str, Any]:
        """Import project from JSON format."""
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format"}

        if "items" not in data:
            return {"error": "Missing 'items' field"}

        imported_count = 0
        errors = []

        for item_data in data["items"]:
            try:
                await self.items.create(
                    project_id=pid,
                    title=item_data.get("title", ""),
                    view=item_data.get("view", "FEATURE"),
                    item_type=item_data.get("type", "feature"),
                    status=item_data.get("status", "todo"),
                )
                imported_count += 1
            except (ValueError, ConcurrencyError, OperationalError) as e:
                errors.append(str(e))

        return {
            "success": True,
            "imported_count": imported_count,
            "error_count": len(errors),
            "errors": errors,
        }

    async def import_from_csv(
        self,
        project_id: str | uuid.UUID,
        csv_data: str,
    ) -> dict[str, Any]:
        """Import project from CSV format."""
        pid = str(project_id) if isinstance(project_id, uuid.UUID) else project_id
        try:
            reader = csv.DictReader(StringIO(csv_data))
            rows = list(reader)
        except (csv.Error, ValueError) as e:
            return {"error": f"Invalid CSV format: {e!s}"}

        imported_count = 0
        errors = []

        for row in rows:
            try:
                await self.items.create(
                    project_id=pid,
                    title=row.get("Title", ""),
                    view=row.get("View", "FEATURE"),
                    item_type=row.get("Type", "feature"),
                    status=row.get("Status", "todo"),
                )
                imported_count += 1
            except (ValueError, ConcurrencyError, OperationalError) as e:
                errors.append(str(e))

        return {
            "success": True,
            "imported_count": imported_count,
            "error_count": len(errors),
            "errors": errors,
        }

    async def get_export_formats(self) -> list[str]:
        """Get available export formats."""
        return ["json", "csv", "markdown"]

    async def get_import_formats(self) -> list[str]:
        """Get available import formats."""
        return ["json", "csv"]
