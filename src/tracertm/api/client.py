"""
Python API client for TraceRTM (FR36-FR45).

Provides programmatic access for AI agents to interact with TraceRTM.
"""

import json
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from tracertm.config.manager import ConfigManager
from tracertm.database.connection import DatabaseConnection
from tracertm.models.agent import Agent
from tracertm.models.event import Event
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.services.concurrent_operations_service import (
    retry_with_backoff,
)

# Helper factory functions (patched in tests)
def get_session(database_url: str | None = None) -> Session:
    db = DatabaseConnection(database_url or ConfigManager().get("database_url"))
    db.connect()
    return Session(db.engine)


def get_async_session(database_url: str | None = None) -> AsyncSession:
    db = DatabaseConnection(database_url or ConfigManager().get("database_url"))
    db.connect()
    if hasattr(db, "async_session"):
        return db.async_session
    # Fallback: wrap sync engine
    return AsyncSession(db.engine)


class TraceRTMClient:
    """
    Python API client for TraceRTM (FR36).

    Provides programmatic access for AI agents to interact with TraceRTM.
    """

    def __init__(self, agent_id: str | None = None, agent_name: str | None = None):
        """
        Initialize TraceRTM client.

        Args:
            agent_id: Optional agent ID (if already registered)
            agent_name: Optional agent name for registration
        """
        self.config_manager = ConfigManager()
        self.agent_id = agent_id
        self.agent_name = agent_name
        self._db: DatabaseConnection | None = None
        self._session: Session | AsyncSession | None = None

    # Context manager support for tests
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            self.cleanup()
        except Exception:
            pass
        return False

    def cleanup(self) -> None:
        """Close any open session/connection."""
        try:
            if self._session is not None:
                close = getattr(self._session, "close", None)
                if callable(close):
                    close()
            if self._db is not None and hasattr(self._db, "disconnect"):
                try:
                    self._db.disconnect()
                except Exception:
                    pass
        finally:
            self._session = None
            self._db = None

    def get_agent_info(self):
        """Return the Agent record for the current agent_id, if set."""
        if not self.agent_id:
            return None
        session = self._get_session()
        try:
            stmt = select(Agent).filter(Agent.id == self.agent_id)
            result = session.execute(stmt)
            agent = result.scalars().first() if hasattr(result, "scalars") else None
        except Exception:
            agent = None

        if agent is None and hasattr(session, "query"):
            try:
                agent = session.query(Agent).filter_by(id=self.agent_id).first()
            except Exception:
                agent = None

        return agent

    def _get_session(self) -> Session | AsyncSession:
        """Get database session."""
        if self._session is None:
            try:
                import asyncio

                asyncio.get_running_loop()
                use_async = True
            except RuntimeError:
                use_async = False

            if use_async:
                self._session = get_async_session()
            else:
                self._session = get_session()

        return self._session

    def _is_async_session(self) -> bool:
        """Check if the session is async."""
        return isinstance(self._session, AsyncSession)

    def _ensure_sync_session(self) -> Session:
        """
        Return a synchronous Session, using sync_session when AsyncSession is patched in tests.
        """
        session = self._get_session()
        if isinstance(session, Session):
            return session
        if hasattr(session, "sync_session"):
            return session.sync_session
        raise ValueError("Synchronous session required for this operation")

    def _execute_query(self, stmt):
        """Execute a select statement compatible with both sync and async sessions."""
        try:
            return self._session.execute(stmt)
        except Exception:
            # Fallback for AsyncSession in non-async context
            if self._is_async_session() and hasattr(self._session, 'sync_session'):
                return self._session.sync_session.execute(stmt)
            raise

    def _get_project_id(self) -> str:
        """Get current project ID."""
        project_id = self.config_manager.get("current_project_id")
        if not project_id:
            raise ValueError("No project selected. Run 'rtm project switch <name>' first.")
        return project_id

    def _log_operation(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        data: dict[str, Any],
    ) -> None:
        """Log agent operation (FR41)."""
        if not self.agent_id:
            return  # Skip logging if no agent registered

        try:
            session = self._get_session()
            project_id = self._get_project_id()

            event = Event(
                project_id=project_id,
                event_type=event_type,
                entity_type=entity_type,
                entity_id=entity_id,
                data=data or {},  # Ensure data is always a dict
                agent_id=self.agent_id,
            )
            session.add(event)
            session.flush()  # Flush to get ID, but don't commit yet
            session.commit()
        except Exception:
            # Rollback on error and silently fail logging to not break operations
            try:
                if 'session' in locals():
                    session.rollback()
            except Exception:
                pass
            # In production, this could be logged to a separate error log
            pass

    def register_agent(
        self,
        name: str,
        capabilities: list[str] | None = None,
        config: dict | None = None,
        agent_type: str = "ai_agent",
        project_ids: list[str] | None = None,
    ) -> str:
        """
        Register an agent (FR41, FR51).

        Supports the test harness signature with capabilities/config.
        """
        session = self._get_session()
        capabilities = capabilities or []
        config = config or {}
        project_id = self.config_manager.get("current_project_id")

        existing = None
        if self.agent_id:
            existing = session.query(Agent).filter(Agent.id == self.agent_id).first()

        if existing:
            existing.name = name or existing.name
            existing.capabilities = capabilities
            existing.config = config
            existing.agent_metadata = config
            session.commit()
            return existing.id

        # Ensure we always have an ID even before flush (unit tests rely on it)
        from tracertm.models.agent import generate_agent_uuid

        agent_id = generate_agent_uuid()

        agent = Agent(
            id=agent_id,
            project_id=project_id,
            name=name,
            agent_type=agent_type,
            status="active",
            capabilities=capabilities,
            config=config,
            agent_metadata=config,
            last_activity_at=datetime.utcnow().isoformat(),
        )
        session.add(agent)
        session.flush()
        session.commit()

        self.agent_id = agent.id or agent_id
        self.agent_name = name

        self._log_operation(
            "agent_registered",
            "agent",
            agent.id,
            {"name": name, "type": agent_type, "projects": project_ids or ([project_id] if project_id else [])},
        )

        return agent.id

    def assign_agent_to_projects(self, agent_id: str, project_ids: list[str]) -> None:
        """
        Assign agent to multiple projects (FR51, FR52).

        Args:
            agent_id: Agent ID
            project_ids: List of project IDs
        """
        session = self._get_session()

        stmt = select(Agent).filter(Agent.id == agent_id)
        agent = None

        # Prefer modern execute/scalars path, but fall back to query() for
        # compatibility with mocked sessions used in unit tests.
        try:
            result = session.execute(stmt)
            if hasattr(result, "scalars"):
                agent = result.scalars().first()
        except Exception:
            agent = None

        if (not agent or not isinstance(agent, Agent)) and hasattr(session, "query"):
            try:
                agent = session.query(Agent).filter(Agent.id == agent_id).first()
            except Exception:
                agent = None

        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")

        # Update metadata with assigned projects
        if agent.agent_metadata is None:
            agent.agent_metadata = {}
        agent.agent_metadata["assigned_projects"] = project_ids

        # Mark metadata as modified for SQLAlchemy to detect change
        from sqlalchemy.orm import attributes

        attributes.flag_modified(agent, "agent_metadata")
        session.commit()

        # Log assignment
        self._log_operation(
            "agent_assigned",
            "agent",
            agent_id,
            {"project_ids": project_ids},
        )

    def get_agent_projects(self, agent_id: str) -> list[str]:
        """
        Get projects assigned to an agent (FR52).

        Args:
            agent_id: Agent ID

        Returns:
            List of project IDs
        """
        session = self._get_session()

        if self._is_async_session():
            stmt = select(Agent).filter(Agent.id == agent_id)
            try:
                result = session.execute(stmt)
                agent = result.scalars().first()
            except Exception:
                agent = None
        else:
            agent = (
                session.query(Agent)
                .filter(Agent.id == agent_id)
                .first()
            )

        if not agent:
            return []

        # Get assigned projects from metadata
        assigned = agent.agent_metadata.get("assigned_projects", [])
        # Include primary project
        primary = [agent.project_id]
        return list(set(primary + assigned))

    # FR37: Query project state
    def query_items(
        self,
        view: str | None = None,
        status: str | None = None,
        item_type: str | None = None,
        limit: int = 100,
        **filters
    ) -> list[dict[str, Any]]:
        """
        Query items in project (FR37, FR44).

        Args:
            view: Filter by view
            status: Filter by status
            item_type: Filter by item type
            limit: Maximum results
            **filters: Additional filters (FR44 - structured filter language)

        Returns:
            List of item dictionaries
        """
        session = self._get_session()
        project_id = self._get_project_id()

        if self._is_async_session():
            stmt = select(Item).filter(
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )

            if view:
                stmt = stmt.filter(Item.view == view.upper())
            if status:
                stmt = stmt.filter(Item.status == status)
            if item_type:
                stmt = stmt.filter(Item.item_type == item_type)

            if "priority" in filters:
                stmt = stmt.filter(Item.priority == filters["priority"])
            if "owner" in filters:
                stmt = stmt.filter(Item.owner == filters["owner"])
            if "parent_id" in filters:
                stmt = stmt.filter(Item.parent_id == filters["parent_id"])

            stmt = stmt.limit(limit)

            try:
                result = session.execute(stmt)
                items = result.scalars().all()
            except Exception:
                if hasattr(session, 'sync_session_class'):
                    sync_session = session.sync_session_class(bind=session.sync_session.bind)
                    result = sync_session.execute(stmt)
                    items = result.scalars().all()
                else:
                    items = []
        else:
            query = (
                session.query(Item)
                .filter(Item.project_id == project_id, Item.deleted_at.is_(None))
            )

            if view:
                query = query.filter(Item.view == view.upper())
            if status:
                query = query.filter(Item.status == status)
            if item_type:
                query = query.filter(Item.item_type == item_type)
            if "priority" in filters:
                query = query.filter(Item.priority == filters["priority"])
            if "owner" in filters:
                query = query.filter(Item.owner == filters["owner"])
            if "parent_id" in filters:
                query = query.filter(Item.parent_id == filters["parent_id"])

            items = query.limit(limit).all()

        # Log query operation
        self._log_operation(
            "items_queried",
            "query",
            "multiple",
            {"view": view, "status": status, "count": len(items)},
        )

        return items

    def get_item(self, item_id: str) -> Item | None:
        """
        Get a specific item (FR37).

        Args:
            item_id: Item ID

        Returns:
            Item dictionary or None (returns None if item is soft-deleted)
        """
        session = self._get_session()
        project_id = self._get_project_id()

        if self._is_async_session():
            stmt = select(Item).filter(
                Item.id.like(f"{item_id}%"),
                Item.project_id == project_id,
                Item.deleted_at.is_(None),
            )
            try:
                result = session.execute(stmt)
                item = result.scalars().first()
            except Exception:
                if hasattr(session, 'sync_session_class'):
                    sync_session = session.sync_session_class(bind=session.sync_session.bind)
                    result = sync_session.execute(stmt)
                    item = result.scalars().first()
                else:
                    item = None
        else:
            item = (
                session.query(Item)
                .filter(
                    Item.id.like(f"{item_id}%"),
                    Item.project_id == project_id,
                    Item.deleted_at.is_(None),
                )
                .first()
            )

        if not item:
            return None

        return item

    async def get_item_async(self, item_id: str) -> Item | None:
        """Async wrapper for get_item."""
        return self.get_item(item_id)

    # FR38: Create/update/delete items
    def create_item(
        self,
        title: str,
        view: str,
        item_type: str | None = None,
        description: str | None = None,
        status: str = "todo",
        priority: str = "medium",
        owner: str | None = None,
        parent_id: str | None = None,
        metadata: dict | None = None,
        project_id: str | None = None,
        **kwargs,
    ) -> Item:
        """
        Create a new item (FR38).

        Args:
            title: Item title
            view: View (FEATURE, CODE, etc.)
            item_type: Item type
            description: Optional description
            status: Status (default: todo)
            priority: Priority (default: medium)
            owner: Optional owner
            parent_id: Optional parent item ID
            metadata: Optional metadata

        Returns:
            Created item
        """
        session = self._ensure_sync_session()
        project_id = project_id or self._get_project_id()
        item_type = item_type or kwargs.get("type")

        item = Item(
            project_id=project_id,
            title=title,
            description=description,
            view=view.upper(),
            item_type=item_type,
            status=status,
            priority=priority,
            owner=owner,
            parent_id=parent_id,
            item_metadata=metadata or {},
        )
        session.add(item)
        session.commit()

        # Log operation (FR41)
        self._log_operation(
            "item_created",
            "item",
            item.id,
            {"title": title, "view": view, "type": item_type},
        )

        return item

    async def create_item_async(
        self,
        title: str,
        view: str,
        item_type: str | None = None,
        description: str | None = None,
        status: str = "todo",
        priority: str = "medium",
        owner: str | None = None,
        parent_id: str | None = None,
        metadata: dict | None = None,
        project_id: str | None = None,
        **kwargs,
    ) -> Item:
        """Async wrapper for item creation used in tests."""
        return self.create_item(
            title=title,
            view=view,
            item_type=item_type,
            description=description,
            status=status,
            priority=priority,
            owner=owner,
            parent_id=parent_id,
            metadata=metadata,
            project_id=project_id,
            **kwargs,
        )

    @retry_with_backoff(max_retries=3, initial_delay=0.1)
    def update_item(
        self,
        item_id: str,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        owner: str | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        """
        Update an item with optimistic locking and retry logic (FR38, FR42, Story 5.3).

        Args:
            item_id: Item ID
            title: Optional new title
            description: Optional new description
            status: Optional new status
            priority: Optional new priority
            owner: Optional new owner
            metadata: Optional new metadata

        Returns:
            Updated item dictionary

        Raises:
            ValueError: If item not found
            ConcurrencyError: If conflict detected after retries (FR43)
        """
        session = self._ensure_sync_session()
        project_id = self._get_project_id()

        if self._is_async_session():
            stmt = select(Item).filter(Item.id.like(f"{item_id}%"), Item.project_id == project_id)
            try:
                result = session.execute(stmt)
                item = result.scalars().first()
            except Exception:
                item = None
        else:
            item = (
                session.query(Item)
                .filter(Item.id.like(f"{item_id}%"), Item.project_id == project_id)
                .first()
            )

        if not item:
            raise ValueError(f"Item not found: {item_id}")

        # Store original version for conflict detection
        original_version = item.version

        # Update fields
        if title is not None:
            item.title = title
        if description is not None:
            item.description = description
        if status is not None:
            item.status = status
        if priority is not None:
            item.priority = priority
        if owner is not None:
            item.owner = owner
        if metadata is not None:
            item.item_metadata = metadata

        # Optimistic locking (FR42) - version will be incremented automatically
        try:
            session.commit()

            # Log operation (FR41)
            self._log_operation(
                "item_updated",
                "item",
                item.id,
                {
                    "title": item.title,
                    "status": item.status,
                    "version": original_version,
                    "new_version": item.version,
                },
            )

            return item
        except StaleDataError:
            # Conflict detected (FR43) - will be retried by decorator
            session.rollback()

            # Log conflict (FR41)
            self._log_operation(
                "conflict_detected",
                "item",
                item.id,
                {
                    "agent_id": self.agent_id,
                    "item_id": item.id,
                    "version": original_version,
                },
            )

            # Re-raise for retry decorator
            raise

    async def update_item_async(
        self,
        item_id: str,
        title: str | None = None,
        description: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        owner: str | None = None,
        metadata: dict | None = None,
    ) -> Item:
        """Async wrapper for update_item."""
        return self.update_item(
            item_id=item_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            owner=owner,
            metadata=metadata,
        )

    def delete_item(self, item_id: str) -> bool:
        """
        Delete an item (soft delete) (FR38).

        Args:
            item_id: Item ID

        Raises:
            ValueError: If item not found
        """
        session = self._get_session()
        project_id = self._get_project_id()

        item = (
            session.query(Item)
            .filter(Item.id.like(f"{item_id}%"), Item.project_id == project_id)
            .first()
        )

        if not item:
            raise ValueError(f"Item not found: {item_id}")

        # Soft delete
        from datetime import datetime
        item.deleted_at = datetime.utcnow()
        session.commit()

        # Log operation (FR41)
        self._log_operation(
            "item_deleted",
            "item",
            item.id,
            {"title": item.title},
        )
        return True

    async def delete_item_async(self, item_id: str) -> bool:
        """Async wrapper for delete_item."""
        return self.delete_item(item_id)

    # =========================
    # Link operations
    # =========================
    def create_link(
        self,
        source_id: str,
        target_id: str,
        link_type: str,
        metadata: dict | None = None,
        project_id: str | None = None,
    ) -> Link:
        session = self._ensure_sync_session()
        project_id = project_id or self._get_project_id()
        link = Link(
            project_id=project_id,
            source_item_id=source_id,
            target_item_id=target_id,
            link_type=link_type,
            link_metadata=metadata or {},
        )
        session.add(link)
        session.commit()
        return link

    async def create_link_async(
        self,
        source_id: str,
        target_id: str,
        link_type: str,
        metadata: dict | None = None,
        project_id: str | None = None,
    ) -> Link:
        return self.create_link(
            source_id=source_id,
            target_id=target_id,
            link_type=link_type,
            metadata=metadata,
            project_id=project_id,
        )

    def create_bidirectional_link(
        self,
        source_id: str,
        target_id: str,
        forward_type: str,
        reverse_type: str,
        metadata: dict | None = None,
        project_id: str | None = None,
    ) -> list[Link]:
        forward = self.create_link(
            source_id=source_id,
            target_id=target_id,
            link_type=forward_type,
            metadata=metadata,
            project_id=project_id,
        )
        reverse = self.create_link(
            source_id=target_id,
            target_id=source_id,
            link_type=reverse_type,
            metadata=metadata,
            project_id=project_id,
        )
        return [forward, reverse]

    def get_link(self, link_id: str) -> Link | None:
        session = self._ensure_sync_session()
        project_id = self._get_project_id()
        link = (
            session.query(Link)
            .filter(
                Link.id.like(f"{link_id}%"),
                Link.project_id == project_id,
            )
            .first()
        )
        return link

    async def get_link_async(self, link_id: str) -> Link | None:
        return self.get_link(link_id)

    def update_link(
        self,
        link_id: str,
        link_type: str | None = None,
        metadata: dict | None = None,
    ) -> Link:
        session = self._ensure_sync_session()
        link = session.query(Link).filter(Link.id.like(f"{link_id}%")).first()
        if not link:
            raise ValueError(f"Link not found: {link_id}")
        if link_type is not None:
            link.link_type = link_type
        if metadata is not None:
            link.link_metadata = metadata
        session.commit()
        return link

    def delete_link(self, link_id: str) -> bool:
        session = self._ensure_sync_session()
        link = session.query(Link).filter(Link.id.like(f"{link_id}%")).first()
        if not link:
            return False
        session.delete(link)
        session.commit()
        return True

    def query_links(
        self,
        source_id: str | None = None,
        target_id: str | None = None,
        link_type: str | None = None,
        project_id: str | None = None,
    ) -> list[Link]:
        session = self._ensure_sync_session()
        project_id = project_id or self._get_project_id()
        query = session.query(Link).filter(Link.project_id == project_id)
        if source_id:
            query = query.filter(Link.source_item_id == source_id)
        if target_id:
            query = query.filter(Link.target_item_id == target_id)
        if link_type:
            query = query.filter(Link.link_type == link_type)
        return query.all()

    # FR39: Export project data
    def export_project(self, format: str = "json") -> str:
        """
        Export project data (FR39).

        Args:
            format: Export format (json or yaml)

        Returns:
            Exported data as string
        """
        session = self._get_session()
        project_id = self._get_project_id()

        from tracertm.models.project import Project
        project = session.query(Project).filter(Project.id == project_id).first()

        items = (
            session.query(Item)
            .filter(Item.project_id == project_id, Item.deleted_at.is_(None))
            .all()
        )

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
        else:
            return json.dumps(data, indent=2, default=str)

    # FR40: Import bulk data
    def import_data(self, data: dict[str, Any]) -> dict[str, int]:
        """
        Import bulk data from JSON/YAML (FR40).

        Args:
            data: Dictionary with 'items' and optionally 'links' keys

        Returns:
            Dictionary with import statistics
        """
        session = self._get_session()
        project_id = self._get_project_id()

        items_created = 0
        links_created = 0

        # Import items
        for item_data in data.get("items", []):
            item = Item(
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

        # Import links (after items are created)
        for link_data in data.get("links", []):
            link = Link(
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

        # Log import operation (FR41)
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

    # FR45: Agent activity monitoring
    def get_agent_activity(self, agent_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get agent activity history (FR45).

        Args:
            agent_id: Agent ID (default: current agent)
            limit: Maximum events to return

        Returns:
            List of activity events
        """
        session = self._get_session()
        project_id = self._get_project_id()

        target_agent_id = agent_id or self.agent_id
        if not target_agent_id:
            return []

        events = (
            session.query(Event)
            .filter(
                Event.project_id == project_id,
                Event.agent_id == target_agent_id,
            )
            .order_by(Event.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "event_type": event.event_type,
                "entity_type": event.entity_type,
                "entity_id": event.entity_id,
                "timestamp": event.created_at.isoformat() if event.created_at else None,
                "data": event.data,
            }
            for event in events
        ]

    def get_all_agents_activity(self, limit: int = 100) -> dict[str, list[dict[str, Any]]]:
        """
        Get activity for all agents in project (FR45).

        Args:
            limit: Maximum events per agent

        Returns:
            Dictionary mapping agent_id to activity list
        """
        session = self._get_session()
        project_id = self._get_project_id()

        # Get all agents
        agents = session.query(Agent).filter(Agent.project_id == project_id).all()

        result = {}
        for agent in agents:
            result[agent.id] = self.get_agent_activity(agent.id, limit)

        return result

    # Story 5.5: Batch Operations (FR44)
    def batch_create_items(
        self,
        items: list[dict[str, Any]],
    ) -> dict[str, int]:
        """
        Create multiple items in a single transaction (Story 5.5, FR44).

        Args:
            items: List of item dictionaries with title, view, item_type, etc.

        Returns:
            Dictionary with items_created count
        """
        session = self._get_session()
        project_id = self._get_project_id()

        items_created = 0

        try:
            for item_data in items:
                item = Item(
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

            # Log batch operation (FR41)
            self._log_operation(
                "batch_items_created",
                "batch",
                "multiple",
                {"count": items_created},
            )

            return {"items_created": items_created}
        except Exception:
            session.rollback()
            raise

    def batch_update_items(
        self,
        updates: list[dict[str, Any]],
    ) -> dict[str, int]:
        """
        Update multiple items in a single transaction (Story 5.5, FR44).

        Args:
            updates: List of update dictionaries with item_id and fields to update

        Returns:
            Dictionary with items_updated count
        """
        session = self._get_session()
        project_id = self._get_project_id()

        items_updated = 0

        try:
            for update_data in updates:
                item_id = update_data.get("item_id")
                if not item_id:
                    continue

                item = (
                    session.query(Item)
                    .filter(Item.id.like(f"{item_id}%"), Item.project_id == project_id)
                    .first()
                )

                if not item:
                    continue

                # Update fields
                if "title" in update_data:
                    item.title = update_data["title"]
                if "description" in update_data:
                    item.description = update_data.get("description")
                if "status" in update_data:
                    item.status = update_data["status"]
                if "priority" in update_data:
                    item.priority = update_data["priority"]
                if "owner" in update_data:
                    item.owner = update_data.get("owner")
                if "metadata" in update_data:
                    item.item_metadata = update_data["metadata"]

                items_updated += 1

            session.commit()

            # Log batch operation (FR41)
            self._log_operation(
                "batch_items_updated",
                "batch",
                "multiple",
                {"count": items_updated},
            )

            return {"items_updated": items_updated}
        except Exception:
            session.rollback()
            raise

    def batch_delete_items(
        self,
        item_ids: list[str],
    ) -> dict[str, int]:
        """
        Delete multiple items in a single transaction (Story 5.5, FR44).

        Args:
            item_ids: List of item IDs to delete

        Returns:
            Dictionary with items_deleted count
        """
        session = self._get_session()
        project_id = self._get_project_id()

        items_deleted = 0

        try:
            from datetime import datetime

            for item_id in item_ids:
                item = (
                    session.query(Item)
                    .filter(Item.id.like(f"{item_id}%"), Item.project_id == project_id)
                    .first()
                )

                if not item:
                    continue

                # Soft delete
                item.deleted_at = datetime.utcnow()
                items_deleted += 1

            session.commit()

            # Log batch operation (FR41)
            self._log_operation(
                "batch_items_deleted",
                "batch",
                "multiple",
                {"count": items_deleted},
            )

            return {"items_deleted": items_deleted}
        except Exception:
            session.rollback()
            raise

    # Story 5.6: Task Assignment (FR45)
    def get_assigned_items(self, agent_id: str | None = None) -> list[dict[str, Any]]:
        """
        Get items assigned to an agent (Story 5.6, FR45).

        Args:
            agent_id: Agent ID (default: current agent)

        Returns:
            List of assigned items
        """
        session = self._get_session()
        project_id = self._get_project_id()

        target_agent_id = agent_id or self.agent_id
        if not target_agent_id:
            return []

        items = (
            session.query(Item)
            .filter(
                Item.project_id == project_id,
                Item.owner == target_agent_id,
                Item.deleted_at.is_(None),
            )
            .all()
        )

        return [
            {
                "id": item.id,
                "title": item.title,
                "status": item.status,
                "view": item.view,
                "type": item.item_type,
                "owner": item.owner,
            }
            for item in items
        ]

    def close(self) -> None:
        """Close database connection."""
        if self._session:
            self._session.close()
        if self._db:
            self._db.close()
