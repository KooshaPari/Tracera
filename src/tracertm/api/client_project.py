"""Project and data-related operations for the TraceRTM Python API client."""

import json
from typing import Any

from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


class ClientProjectMixin:
    """Mixin for TraceRTMClient to handle project and data operations."""

    def list_projects(self) -> list[Project]:
        """List projects visible to the current client."""
        session = self._ensure_sync_session()
        return session.query(Project).all()

    def _get_project_id(self) -> str:
        """Get current project ID."""
        project_id = self.config_manager.get("current_project_id")
        if not isinstance(project_id, str) or not project_id:
            msg = "No project selected. Run 'rtm project switch <name>' first."
            raise ValueError(msg)
        return project_id

    def export_items(self, format: str = "json") -> str:
        """Export items for the current project."""
        items = self.query_items()
        data = [
            {
                "id": item.get("id") if isinstance(item, dict[str, Any]) else item["id"],
                "title": item.get("title") if isinstance(item, dict[str, Any]) else item["title"],
                "view": item.get("view") if isinstance(item, dict[str, Any]) else item["view"],
                "type": item.get("type") if isinstance(item, dict[str, Any]) else item["type"],
                "description": item.get("description") if isinstance(item, dict[str, Any]) else item["description"],
                "project_id": item.get("project_id") if isinstance(item, dict[str, Any]) else item["project_id"],
                "metadata": item.get("metadata") if isinstance(item, dict[str, Any]) else item["metadata"],
            }
            for item in items
        ]
        return json.dumps(data)

    def import_items(self, data: str, project_id: str | None = None) -> Any:
        """Import items from a serialized payload."""
        items_data = json.loads(data)
        return self.batch_create_items(items_data, project_id=project_id)

    def export_project(self, format: str = "json") -> str:
        """Export project data (FR39)."""
        session = self._ensure_sync_session()
        project_id = self._get_project_id()

        project = session.query(Project).filter(Project.id == project_id).first()
        items = session.query(Item).filter(Item.project_id == project_id, Item.deleted_at.is_(None)).all()
        links = session.query(Link).filter(Link.project_id == project_id).all()

        data = {
            "project": {
                "id": project.id if project else project_id,
                "name": project.name if project else "Unknown",
            },
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "view": item.view,
                    "type": item.item_type,
                    "status": item.status,
                    "metadata": item.item_metadata,
                }
                for item in items
            ],
            "links": [
                {
                    "id": link.id,
                    "source_id": link.source_item_id,
                    "target_id": link.target_item_id,
                    "type": link.link_type,
                }
                for link in links
            ],
        }

        if format == "yaml":
            import yaml
            return yaml.dump(data, default_flow_style=False)
        return json.dumps(data, indent=2, default=str)

    def import_data(self, data: dict[str, Any]) -> dict[str, int]:
        """Import bulk data from JSON/YAML (FR40)."""
        session = self._ensure_sync_session()
        project_id = self._get_project_id()

        items_created = 0
        links_created = 0

        for item_data in data.get("items", []):
            item: Item = Item(
                project_id=project_id,
                title=item_data.get("title", ""),
                description=item_data.get("description"),
                view=item_data.get("view", "FEATURE").upper(),
                item_type=item_data.get("type", "feature"),
                status=item_data.get("status", "todo"),
                priority=item_data.get("priority", "medium"),
                owner=item_data.get("owner"),
                parent_id=item_data.get("parent_id"),
                item_metadata=item_data.get("metadata", {}),
            )
            session.add(item)
            items_created += 1

        session.commit()

        for link_data in data.get("links", []):
            link: Link = Link(
                project_id=project_id,
                source_item_id=link_data["source_id"],
                target_item_id=link_data["target_id"],
                link_type=link_data.get("type", "related_to"),
                link_metadata=link_data.get("metadata", {}),
            )
            session.add(link)
            links_created += 1

        if links_created > 0:
            session.commit()

        self._log_operation(
            "data_imported",
            "import",
            "bulk",
            {"items": items_created, "links": links_created},
        )

        return {
            "items_created": items_created,
            "links_created": links_created,
        }
