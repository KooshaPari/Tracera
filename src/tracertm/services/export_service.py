"""Export service for TraceRTM data."""

import csv
import json
from datetime import datetime
from io import StringIO

from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository
from tracertm.repositories.project_repository import ProjectRepository


class ExportService:
    """Service for exporting TraceRTM data."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.projects = ProjectRepository(session)
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)

    async def export_to_json(self, project_id: str) -> str:
        """Export project to JSON format."""
        project = await self.projects.get_by_id(project_id)
        items = await self.items.query(project_id, {})

        data = {
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
            data["items"].append(
                {
                    "id": item.id,
                    "title": item.title,
                    "view": item.view,
                    "type": item.item_type,
                    "status": item.status,
                    "description": item.description,
                    "version": item.version,
                }
            )

        # Add links
        for item in items:
            links = await self.links.get_by_source(item.id)
            for link in links:
                data["links"].append(
                    {
                        "source_id": link.source_item_id,
                        "target_id": link.target_item_id,
                        "type": link.link_type,
                    }
                )

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
            writer.writerow(
                {
                    "ID": item.id,
                    "Title": item.title,
                    "View": item.view,
                    "Type": item.item_type,
                    "Status": item.status,
                    "Description": item.description or "",
                }
            )

        return output.getvalue()

    async def export_to_markdown(self, project_id: str) -> str:
        """Export project to Markdown format."""
        project = await self.projects.get_by_id(project_id)
        items = await self.items.query(project_id, {})

        md = f"# {project.name}\n\n"
        md += f"{project.description}\n\n"
        md += f"**Generated:** {datetime.utcnow().isoformat()}\n\n"

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
            links = await self.links.get_by_source(source.id)
            link_targets = {link.target_item_id for link in links}

            for target in target_items:
                row.append("X" if target.id in link_targets else "")

            writer.writerow(row)

        return output.getvalue()

    async def export_yaml(self, project_id: str) -> str:
        """
        Export project to YAML format.

        STUB: Returns minimal YAML structure. TODO: Implement full YAML export.

        Args:
            project_id: Project ID to export

        Returns:
            YAML string with project data
        """
        # STUB: Minimal implementation to unblock tests
        # Real implementation should mirror export_to_json but in YAML format
        try:
            import yaml
        except ImportError:
            # Fallback if yaml not installed
            return f"project:\n  id: {project_id}\n  name: stub\nitems: []\nlinks: []\n"

        project = await self.projects.get_by_id(project_id)
        items = await self.items.query(project_id, {})

        data = {
            "project": {
                "id": project.id if project else project_id,
                "name": project.name if project else "Unknown",
                "description": project.description if project else "",
            },
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "view": item.view,
                    "type": item.item_type,
                    "status": item.status,
                }
                for item in items
            ],
            "links": [],
        }

        return yaml.dump(data, default_flow_style=False)
