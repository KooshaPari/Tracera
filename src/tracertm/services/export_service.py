"""Export service for TraceRTM data."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from io import StringIO
from typing import TYPE_CHECKING, Any

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class ExportService:
    """Service for exporting TraceRTM data.

    Functional Requirements:
    - FR-COLLAB-003
    - FR-RPT-009

    User Stories:
    - US-EXPORT-001
    - US-MATRIX-003

    Epics:
    - EPIC-007
    - EPIC-008
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

    async def export_to_json(self, project_id: str) -> str:
        """Export project to JSON format."""
        project = await self.projects.get_by_id(project_id)
        if not project:
            msg = "Project not found"
            raise ValueError(msg)
        items = await self.items.query(project_id, {})

        data: dict[str, Any] = {
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "created_at": (
                    project.created_at.isoformat()
                    if hasattr(project.created_at, "isoformat")
                    else str(project.created_at)
                ),
            },
            "items": [],
            "links": [],
        }

        # Add items
        for item in items:
            data["items"].append({
                "id": item.id,
                "title": item.title,
                "view": item.view,
                "type": item.item_type,
                "status": item.status,
                "description": item.description,
                "version": item.version,
            })

        # Add links
        for item in items:
            links = await self.links.get_by_source(str(item.id))
            for link in links:
                data["links"].append({
                    "source_id": link.source_item_id,
                    "target_id": link.target_item_id,
                    "type": link.link_type,
                })

        return json.dumps(data, indent=2)

    async def export_to_csv(self, project_id: str) -> str:
        """Export project items to CSV format."""
        items = await self.items.query(project_id, {})

        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["ID", "Title", "View", "Type", "Status", "Description"],
        )

        writer.writeheader()
        for item in items:
            writer.writerow({
                "ID": item.id,
                "Title": item.title,
                "View": item.view,
                "Type": item.item_type,
                "Status": item.status,
                "Description": item.description or "",
            })

        return output.getvalue()

    async def export_to_markdown(self, project_id: str) -> str:
        """Export project to Markdown format."""
        project = await self.projects.get_by_id(project_id)
        if not project:
            msg = "Project not found"
            raise ValueError(msg)
        items = await self.items.query(project_id, {})

        md = f"# {project.name}\n\n"
        md += f"{project.description}\n\n"
        md += f"**Generated:** {datetime.now(UTC).isoformat()}\n\n"

        # Group items by view
        by_view: dict[str, list] = {}
        for item in items:
            if item.view not in by_view:
                by_view[item.view] = []
            by_view[item.view].append(item)

        # Generate sections
        for view, view_items in sorted(by_view.items()):
            md += f"## {view}\n\n"
            for item in view_items:
                md += f"### {item.title}\n"
                md += f"- **ID:** {item.id}\n"
                md += f"- **Type:** {item.item_type}\n"
                md += f"- **Status:** {item.status}\n"
                if item.description:
                    md += f"- **Description:** {item.description}\n"
                md += "\n"

        return md

    async def export_traceability_matrix(
        self,
        project_id: str,
        source_view: str,
        target_view: str,
    ) -> str:
        """Export traceability matrix as CSV."""
        source_items = await self.items.get_by_view(project_id, source_view)
        target_items = await self.items.get_by_view(project_id, target_view)

        output = StringIO()

        # Header row
        header = ["Source"] + [item.title for item in target_items]
        writer = csv.writer(output)
        writer.writerow(header)

        # Data rows
        for source in source_items:
            row = [source.title]
            links = await self.links.get_by_source(str(source.id))
            link_targets = {link.target_item_id for link in links}

            row.extend("X" if target.id in link_targets else "" for target in target_items)

            writer.writerow(row)

        return output.getvalue()

    async def export_yaml(self, project_id: str) -> str:
        """Export project to YAML format.

        Args:
            project_id: Project ID to export

        Returns:
            YAML string with project data
        """
        try:
            import yaml
        except ImportError:
            # Fallback if yaml not installed - return manual YAML format
            return await self._export_yaml_fallback(project_id)

        project = await self.projects.get_by_id(project_id)
        items = await self.items.query(project_id, {})

        # Build items list
        items_list = []
        for item in items:
            item_data = {
                "id": item.id,
                "title": item.title,
                "view": item.view,
                "type": item.item_type,
                "status": item.status,
                "description": item.description or "",
            }
            if hasattr(item, "version"):
                item_data["version"] = item.version
            items_list.append(item_data)

        # Build links list
        links_list = []
        for item in items:
            links = await self.links.get_by_source(str(item.id))
            links_list.extend([
                {"source_id": link.source_item_id, "target_id": link.target_item_id, "type": link.link_type}
                for link in links
            ])

        data = {
            "project": {
                "id": project.id if project else project_id,
                "name": project.name if project else "Unknown",
                "description": project.description if project else "",
                "export_date": datetime.now(UTC).isoformat(),
            },
            "items": items_list,
            "links": links_list,
        }

        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    async def _export_yaml_fallback(self, project_id: str) -> str:
        """Fallback YAML export when yaml library is not available.

        Args:
            project_id: Project ID to export

        Returns:
            Manual YAML format string
        """
        project = await self.projects.get_by_id(project_id)
        items = await self.items.query(project_id, {})

        yaml_lines: list[str] = []
        yaml_lines.extend((
            "project:",
            f"  id: {project.id if project else project_id}",
            f"  name: {project.name if project else 'Unknown'}",
            f"  description: {project.description if project else ''}",
            f"  export_date: {datetime.now(UTC).isoformat()}",
            "items:",
        ))

        for item in items:
            yaml_lines.extend((
                "  - id: " + str(item.id),
                "    title: " + str(item.title),
                "    view: " + str(item.view),
                "    type: " + str(item.item_type),
                "    status: " + str(item.status),
            ))
            if item.description:
                yaml_lines.append("    description: " + str(item.description))

        yaml_lines.append("links:")
        for item in items:
            links = await self.links.get_by_source(str(item.id))
            for link in links:
                yaml_lines.extend((
                    "  - source_id: " + str(link.source_item_id),
                    "    target_id: " + str(link.target_item_id),
                    "    type: " + str(link.link_type),
                ))

        return "\n".join(yaml_lines)
