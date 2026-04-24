"""Project backup and restore service for Epic 6 (Story 6.6, FR53).

Provides enhanced backup/restore capabilities with templates and cloning.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from tracertm.models.agent import Agent
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class ProjectBackupService:
    """Service for project backup, restore, and template management (Story 6.6, FR53)."""

    def __init__(self, session: Session) -> None:
        """Initialize project backup service."""
        self.session = session

    def backup_project(
        self,
        project_id: str,
        include_history: bool = False,
        include_agents: bool = False,
    ) -> dict[str, Any]:
        """Create a complete backup of a project (Story 6.6, FR53).

        Args:
            project_id: Project ID to backup
            include_history: Include event history (default: False)
            include_agents: Include agent data (default: False)

        Returns:
            Backup data dictionary
        """
        project = self.session.query(Project).filter(Project.id == project_id).first()
        if not project:
            msg = f"Project not found: {project_id}"
            raise ValueError(msg)

        # Get all items
        items = self.session.query(Item).filter(Item.project_id == project_id, Item.deleted_at.is_(None)).all()

        # Get all links
        links = self.session.query(Link).filter(Link.project_id == project_id).all()

        backup_data = {
            "version": "1.0",
            "backup_date": datetime.now(UTC).isoformat(),
            "project": {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "metadata": project.project_metadata or {},
            },
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "view": item.view,
                    "type": item.item_type,
                    "status": item.status,
                    "priority": item.priority,
                    "owner": item.owner,
                    "parent_id": item.parent_id,
                    "metadata": item.item_metadata or {},
                }
                for item in items
            ],
            "links": [
                {
                    "id": link.id,
                    "source_id": link.source_item_id,
                    "target_id": link.target_item_id,
                    "type": link.link_type,
                    "metadata": link.link_metadata or {},
                }
                for link in links
            ],
        }

        # Include history if requested
        if include_history:
            from tracertm.models.event import Event

            events = self.session.query(Event).filter(Event.project_id == project_id).order_by(Event.created_at).all()
            backup_data["events"] = [
                {
                    "event_type": event.event_type,
                    "entity_type": event.entity_type,
                    "entity_id": event.entity_id,
                    "agent_id": event.agent_id,
                    "timestamp": event.created_at.isoformat() if event.created_at else None,
                    "data": event.data,
                }
                for event in events
            ]

        # Include agents if requested
        if include_agents:
            agents = self.session.query(Agent).filter(Agent.project_id == project_id).all()
            backup_data["agents"] = [
                {
                    "id": agent.id,
                    "name": agent.name,
                    "type": agent.agent_type,
                    "status": agent.status,
                    "metadata": agent.agent_metadata or {},
                }
                for agent in agents
            ]

        return backup_data

    def _get_or_create_project_from_backup(self, backup_data: dict[str, Any], project_name: str | None) -> str:
        """Create or find project from backup; return project_id."""
        target_name = project_name or backup_data["project"].get("name", "restored-project")
        project = self.session.query(Project).filter(Project.name == target_name).first()
        if project:
            project.description = backup_data["project"].get("description", project.description)
            project.project_metadata = backup_data["project"].get("metadata", {})
            return str(project.id)
        project = Project(
            name=target_name,
            description=backup_data["project"].get("description", f"Restored project: {target_name}"),
            project_metadata={
                **(backup_data["project"].get("metadata", {})),
                "restored_from_backup": backup_data.get("backup_date"),
            },
        )
        self.session.add(project)
        self.session.commit()
        return str(project.id)

    def _restore_items_from_backup(
        self,
        project_id: str,
        backup_data: dict[str, Any],
        preserve_ids: bool,
    ) -> dict[str, str]:
        """Restore items and return old_id -> new_id map."""
        item_id_map: dict[str, str] = {}
        for item_data in backup_data.get("items", []):
            old_id = item_data["id"]
            item = Item(
                project_id=project_id,
                title=item_data["title"],
                description=item_data.get("description"),
                view=item_data.get("view", "FEATURE").upper(),
                item_type=item_data.get("type", "feature"),
                status=item_data.get("status", "todo"),
                priority=item_data.get("priority", "medium"),
                owner=item_data.get("owner"),
                parent_id=None,
                item_metadata=item_data.get("metadata", {}),
            )
            self.session.add(item)
            self.session.flush()
            item_id_map[old_id] = str(item.id) if not preserve_ids else old_id
        self.session.commit()
        return item_id_map

    def _apply_parent_refs_from_backup(self, backup_data: dict[str, Any], item_id_map: dict[str, str]) -> None:
        """Update parent_id on restored items."""
        for item_data in backup_data.get("items", []):
            old_id = item_data["id"]
            old_parent_id = item_data.get("parent_id")
            if not old_parent_id or old_parent_id not in item_id_map:
                continue
            new_id = item_id_map.get(old_id)
            if new_id is None:
                continue
            item_to_update = self.session.query(Item).filter(Item.id == new_id).first()
            if item_to_update is not None:
                item_to_update.parent_id = item_id_map[old_parent_id]
        self.session.commit()

    def _restore_links_from_backup(
        self,
        project_id: str,
        backup_data: dict[str, Any],
        item_id_map: dict[str, str],
    ) -> None:
        """Restore links using id map."""
        for link_data in backup_data.get("links", []):
            new_source_id = item_id_map.get(link_data["source_id"], link_data["source_id"])
            new_target_id = item_id_map.get(link_data["target_id"], link_data["target_id"])
            link = Link(
                project_id=project_id,
                source_item_id=new_source_id,
                target_item_id=new_target_id,
                link_type=link_data.get("type", "related_to"),
                link_metadata=link_data.get("metadata", {}),
            )
            self.session.add(link)
        self.session.commit()

    def restore_project(
        self,
        backup_data: dict[str, Any],
        project_name: str | None = None,
        preserve_ids: bool = False,
    ) -> str:
        """Restore a project from backup (Story 6.6, FR53).

        Args:
            backup_data: Backup data dictionary
            project_name: Optional new project name
            preserve_ids: Preserve original IDs (default: False, generates new IDs)

        Returns:
            New project ID
        """
        if not backup_data or "project" not in backup_data:
            msg = "Invalid backup data: missing 'project' section"
            raise ValueError(msg)

        project_id = self._get_or_create_project_from_backup(backup_data, project_name)
        item_id_map = self._restore_items_from_backup(project_id, backup_data, preserve_ids)
        self._apply_parent_refs_from_backup(backup_data, item_id_map)
        self._restore_links_from_backup(project_id, backup_data, item_id_map)
        return project_id

    def clone_project(
        self,
        source_project_id: str,
        target_project_name: str,
        include_items: bool = True,
        include_links: bool = True,
    ) -> str:
        """Clone a project (Story 6.5, FR46).

        Args:
            source_project_id: Source project ID
            target_project_name: Name for new project
            include_items: Include items (default: True)
            include_links: Include links (default: True)

        Returns:
            New project ID
        """
        # Create backup
        backup_data = self.backup_project(
            source_project_id,
            include_history=False,  # Don't copy history
            include_agents=False,  # Don't copy agents
        )

        # Remove items/links if not requested
        if not include_items:
            backup_data["items"] = []
        if not include_links:
            backup_data["links"] = []

        # Restore as new project
        return self.restore_project(backup_data, project_name=target_project_name, preserve_ids=False)

    def create_template(
        self,
        project_id: str,
        template_name: str,
    ) -> str:
        """Create a project template (Story 6.5, FR46).

        Args:
            project_id: Project ID to use as template
            template_name: Template name

        Returns:
            Template project ID
        """
        # Clone project with template name
        template_id = self.clone_project(project_id, template_name)

        # Mark as template in metadata
        template = self.session.query(Project).filter(Project.id == template_id).first()
        if template:
            # Get existing metadata or create new dict
            metadata = (
                {} if template.project_metadata is None else dict(template.project_metadata)
            )  # Copy to avoid mutation issues

            metadata["is_template"] = True
            metadata["template_name"] = template_name
            template.project_metadata = metadata
            self.session.commit()

        return template_id

    def list_templates(self) -> list[dict[str, Any]]:
        """List all project templates (Story 6.5, FR46).

        Returns:
            List of template dictionaries
        """
        projects = self.session.query(Project).all()

        return [
            {
                "id": str(project.id),
                "name": project.name,
                "description": project.description,
                "template_name": project.project_metadata.get("template_name", project.name),
            }
            for project in projects
            if project.project_metadata and project.project_metadata.get("is_template")
        ]
