"""Link-related operations for the TraceRTM Python API client."""

from typing import Any

from tracertm.models.link import Link


class ClientLinksMixin:
    """Mixin for TraceRTMClient to handle link-related operations."""

    def create_link(
        self,
        source_id: str,
        target_id: str,
        link_type: str,
        metadata: dict[str, Any] | None = None,
        project_id: str | None = None,
    ) -> Link:
        """Create a link between two items."""
        session = self._ensure_sync_session()
        project_id = project_id or self._get_project_id()
        link: Link = Link(
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
        metadata: dict[str, Any] | None = None,
        project_id: str | None = None,
    ) -> Link:
        """Async wrapper for create_link."""
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
        metadata: dict[str, Any] | None = None,
        project_id: str | None = None,
    ) -> list[Link]:
        """Create forward and reverse links between two items."""
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
        """Return a link by id (prefix match) for the current project."""
        session = self._ensure_sync_session()
        project_id = self._get_project_id()
        return (
            session
            .query(Link)
            .filter(
                Link.id.like(f"{link_id}%"),
                Link.project_id == project_id,
            )
            .first()
        )

    async def get_link_async(self, link_id: str) -> Link | None:
        """Async wrapper for get_link."""
        return self.get_link(link_id)

    def update_link(
        self,
        link_id: str,
        link_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Link:
        """Update a link's type and/or metadata."""
        session = self._ensure_sync_session()
        link = session.query(Link).filter(Link.id.like(f"{link_id}%")).first()
        if not link:
            msg = f"Link not found: {link_id}"
            raise ValueError(msg)
        if link_type is not None:
            link.link_type = link_type
        if metadata is not None:
            link.link_metadata = metadata
        session.commit()
        return link

    def delete_link(self, link_id: str) -> bool:
        """Delete a link by id (prefix match)."""
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
        """Query links for a project."""
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
