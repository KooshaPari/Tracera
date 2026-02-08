"""Python API client for TraceRTM (FR36-FR45).

Provides programmatic access for AI agents to interact with TraceRTM.
"""

from typing import Any, Self

from tracertm.api.client_activity import ClientActivityMixin
from tracertm.api.client_agent import ClientAgentMixin
from tracertm.api.client_analysis import ClientAnalysisMixin
from tracertm.api.client_batch import ClientBatchMixin
from tracertm.api.client_items import ClientItemsMixin
from tracertm.api.client_links import ClientLinksMixin
from tracertm.api.client_project import ClientProjectMixin
from tracertm.api.client_session import ClientSessionMixin
from tracertm.api.client_types import ItemView
from tracertm.config.manager import ConfigManager


class TraceRTMClient(
    ClientSessionMixin,
    ClientAgentMixin,
    ClientItemsMixin,
    ClientLinksMixin,
    ClientBatchMixin,
    ClientProjectMixin,
    ClientAnalysisMixin,
    ClientActivityMixin,
):
    """Python API client for TraceRTM (FR36).

    Provides programmatic access for AI agents to interact with TraceRTM.
    """

    def __init__(self, agent_id: str | None = None, agent_name: str | None = None) -> None:
        """Initialize TraceRTM client.

        Args:
            agent_id: Optional agent ID (if already registered)
            agent_name: Optional agent name for registration
        """
        self.config_manager = ConfigManager()
        self.agent_id = agent_id
        self.agent_name = agent_name
        self._db: Any = None
        self._session: Any = None
        self._patched_session: bool = False

    def __enter__(self) -> Self:
        """Enter context manager and return self."""
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: Any) -> None:
        """Exit context manager and best-effort cleanup resources."""
        self.cleanup()

    def _as_item_view(self, item: Any) -> ItemView | None:
        """Return a detached, dict-friendly view of an item."""
        if item is None:
            return None
        if isinstance(item, ItemView):
            return item
        return ItemView(item)

    def close(self) -> None:
        """Close database connection."""
        self.cleanup()
