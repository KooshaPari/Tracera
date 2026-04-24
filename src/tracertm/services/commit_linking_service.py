"""Service for auto-linking commits to items."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, ClassVar

from sqlalchemy.exc import OperationalError

from tracertm.core.concurrency import ConcurrencyError
from tracertm.repositories.event_repository import EventRepository
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.link_repository import LinkRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.models.item import Item


class CommitLinkingService:
    """Service for parsing commits and auto-linking to items.

    Functional Requirements:
    - FR-DISC-004

    User Stories:
    - US-CODE-001

    Epics:
    - EPIC-004
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.items = ItemRepository(session)
        self.links = LinkRepository(session)
        self.events = EventRepository(session)

    # Regex patterns for different commit message formats
    PATTERNS: ClassVar[dict[str, str]] = {
        "hash": r"#(\d+)",  # #123
        "jira": r"([A-Z]+-\d+)",  # FEAT-123
        "github": r"GH-(\d+)",  # GH-123
        "gitlab": r"GL-(\d+)",  # GL-123
        "custom": r"\[([A-Z]+-\d+)\]",  # [FEAT-123]
    }

    async def parse_commit_message(
        self,
        project_id: str,
        commit_message: str,
        _commit_hash: str,
        _author: str,
    ) -> dict[str, Any]:
        """Parse commit message and extract item references."""
        references: dict[str, list[Any]] = {
            "found": [],
            "linked": [],
            "errors": [],
        }

        # Try each pattern
        for pattern_name, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, commit_message)
            for match in matches:
                try:
                    # Try to find item by ID or reference
                    item = await self._find_item_by_reference(project_id, match)
                    if item:
                        references["found"].append({
                            "pattern": pattern_name,
                            "reference": match,
                            "item_id": item.id,
                            "item_title": item.title,
                        })
                except (ValueError, OperationalError) as e:
                    references["errors"].append(str(e))

        return references

    async def auto_link_commit(
        self,
        project_id: str,
        commit_message: str,
        commit_hash: str,
        author: str,
        agent_id: str = "system",
    ) -> dict[str, Any]:
        """Parse commit and auto-link to items."""
        # Parse commit message
        references = await self.parse_commit_message(project_id, commit_message, commit_hash, author)

        # Create links for found items
        for ref in references["found"]:
            try:
                # Create link from commit to item
                link = await self.links.create(
                    project_id=project_id,
                    source_item_id=commit_hash,  # Use commit hash as source
                    target_item_id=ref["item_id"],
                    link_type="implements",
                    metadata={
                        "commit_hash": commit_hash,
                        "commit_message": commit_message,
                        "author": author,
                    },
                )

                # Log event
                await self.events.log(
                    project_id=project_id,
                    event_type="commit_linked",
                    entity_type="link",
                    entity_id=str(link.id),
                    data={
                        "commit_hash": commit_hash,
                        "item_id": ref["item_id"],
                        "pattern": ref["pattern"],
                    },
                    agent_id=agent_id,
                )

                references["linked"].append(ref)
            except (ValueError, ConcurrencyError, OperationalError) as e:
                references["errors"].append(f"Failed to link {ref['reference']}: {e!s}")

        return references

    async def _find_item_by_reference(
        self,
        project_id: str,
        reference: str,
    ) -> Item | None:
        """Find item by reference (ID, hash, or custom format)."""
        # Try direct ID lookup
        item = await self.items.get_by_id(reference)
        if item and item.project_id == project_id:
            return item

        # Try query by metadata or custom field
        items = await self.items.query(project_id, {"metadata": reference})
        if items:
            return items[0]

        return None

    async def register_commit_hook(
        self,
        project_id: str,
        hook_type: str,  # "git", "github", "gitlab"
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Register a commit hook for auto-linking."""
        return {
            "project_id": project_id,
            "hook_type": hook_type,
            "config": config,
            "status": "registered",
        }
