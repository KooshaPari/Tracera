from typing import Any

"""Link factory for generating test links between items."""


class LinkFactory:
    """Factory for creating test links."""

    def __init__(self, session: Any = None) -> None:
        self.session = session
        self.created_links = []

    def create(self, source_item_id: str, target_item_id: str, link_type: str = "implements", **kwargs: Any) -> None:
        """Create a single test link."""
        link_data = {
            "source_item_id": source_item_id,
            "target_item_id": target_item_id,
            "link_type": link_type,
            **kwargs,
        }

        if self.session:
            # Create in database
            pass

        return link_data

    def cleanup(self) -> None:
        """Delete all links created by this factory."""
        if self.session and self.created_links:
            self.created_links = []
