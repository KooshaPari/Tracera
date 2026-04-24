"""Auto-linking service for Epic 4 (FR18).

Automatically links code commits to stories via commit message parsing.
"""

import re
from typing import ClassVar

from sqlalchemy.orm import Session

from tracertm.models.item import Item
from tracertm.models.link import Link


class AutoLinkService:
    """Service for auto-linking items from commit messages.

    Functional Requirements:
    - FR-DISC-003

    User Stories:
    - US-AI-002

    Epics:
    - EPIC-003
    """

    # Patterns for matching story IDs in commit messages
    STORY_PATTERNS: ClassVar[list[str]] = [
        r"#(\w+-\d+)",  # #STORY-123
        r"STORY[-\s]?(\d+)",  # STORY-123 or STORY 123
        r"\[(\w+-\d+)\]",  # [STORY-123]
        r"\((\w+-\d+)\)",  # (STORY-123)
        r"story[-\s]?(\d+)",  # story-123 (case insensitive)
    ]

    def __init__(self, session: Session) -> None:
        """Initialize auto-linking service."""
        self.session = session

    def parse_commit_message(
        self,
        project_id: str,
        commit_message: str,
        _commit_hash: str | None = None,
    ) -> list[tuple[str, str]]:
        """Parse commit message to extract story/item IDs (FR18).

        Args:
            project_id: Project ID
            commit_message: Git commit message
            commit_hash: Optional commit hash for metadata

        Returns:
            List of (item_id, link_type) tuples
        """
        found_items: list[tuple[str, str]] = []

        # Extract potential item IDs from commit message
        item_ids = set()
        for pattern in self.STORY_PATTERNS:
            matches = re.findall(pattern, commit_message, re.IGNORECASE)
            item_ids.update(matches)

        # Also try to find full UUIDs
        uuid_pattern = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        uuid_matches = re.findall(uuid_pattern, commit_message, re.IGNORECASE)
        item_ids.update(uuid_matches)

        # Verify items exist and get their IDs
        for potential_id in item_ids:
            # Try exact match first
            item = (
                self.session
                .query(Item)
                .filter(
                    Item.project_id == project_id,
                    Item.deleted_at.is_(None),
                    (Item.id == potential_id) | (Item.id.like(f"{potential_id}%")),
                )
                .first()
            )

            if item:
                # Determine link type based on commit message keywords
                link_type = self._determine_link_type(commit_message)
                found_items.append((item.id, link_type))

        return found_items

    def create_auto_links(
        self,
        project_id: str,
        commit_message: str,
        code_item_id: str,
        commit_hash: str | None = None,
    ) -> list[Link]:
        """Create auto-links from commit message to code item (FR18).

        Args:
            project_id: Project ID
            commit_message: Git commit message
            code_item_id: ID of the code item being committed
            commit_hash: Optional commit hash for metadata

        Returns:
            List of created links
        """
        # Parse commit message
        linked_items = self.parse_commit_message(project_id, commit_message, commit_hash)

        created_links: list[Link] = []

        for item_id, link_type in linked_items:
            # Check if link already exists
            existing = (
                self.session
                .query(Link)
                .filter(
                    Link.project_id == project_id,
                    Link.source_item_id == item_id,
                    Link.target_item_id == code_item_id,
                    Link.link_type == link_type,
                )
                .first()
            )

            if not existing:
                # Create bidirectional link
                link: Link = Link(
                    project_id=project_id,
                    source_item_id=item_id,
                    target_item_id=code_item_id,
                    link_type=link_type,
                    link_metadata={
                        "auto_linked": True,
                        "commit_message": commit_message,
                        "commit_hash": commit_hash,
                    },
                )
                self.session.add(link)
                created_links.append(link)

        if created_links:
            self.session.commit()

        return created_links

    def _determine_link_type(self, commit_message: str) -> str:
        """Determine link type from commit message keywords.

        Args:
            commit_message: Commit message text

        Returns:
            Link type (implements, tests, etc.)
        """
        message_lower = commit_message.lower()

        # Check for test-related keywords
        if any(keyword in message_lower for keyword in ["test", "testing", "spec", "specification"]):
            return "tests"

        # Check for implementation keywords
        if any(keyword in message_lower for keyword in ["implement", "add", "create", "feat"]):
            return "implements"

        # Default to implements
        return "implements"
