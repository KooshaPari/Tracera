"""Session Manager Port.

Defines the protocol for MCP session lifecycle management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:  # Avoid runtime import cycle with pheno.mcp.__init__
    from pheno.mcp.types import McpServer, McpSession


class SessionManager(Protocol):
    """Protocol for MCP session lifecycle management.

    Manages the creation, tracking, and cleanup of MCP sessions.
    Handles connection pooling and session state.

    Example:
        >>> manager = get_session_manager()
        >>>
        >>> # Create session
        >>> session = await manager.create_session(server)
        >>>
        >>> # Use session
        >>> result = await execute_tool(session, tool, params)
        >>>
        >>> # Close session
        >>> await manager.close_session(session)
    """

    async def create_session(
        self, server: McpServer, metadata: dict[str, Any] | None = None,
    ) -> McpSession:
        """Create a new MCP session.

        Args:
            server: MCP server to connect to
            metadata: Optional session metadata

        Returns:
            New MCP session

        Raises:
            ConnectionError: If connection fails

        Example:
            >>> server = McpServer(url="http://localhost:8000")
            >>> session = await manager.create_session(server)
        """
        ...

    async def close_session(self, session: McpSession) -> None:
        """Close an MCP session.

        Args:
            session: Session to close

        Example:
            >>> await manager.close_session(session)
        """
        ...

    async def close_all_sessions(self) -> None:
        """Close all active sessions.

        Example:
            >>> await manager.close_all_sessions()
        """
        ...

    def get_session(self, session_id: str) -> McpSession | None:
        """Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session if found, None otherwise

        Example:
            >>> session = manager.get_session("session-123")
        """
        ...

    def list_sessions(
        self, server: McpServer | None = None, active_only: bool = True,
    ) -> list[McpSession]:
        """List sessions.

        Args:
            server: Optional server filter
            active_only: Only return active sessions

        Returns:
            List of sessions

        Example:
            >>> # All active sessions
            >>> sessions = manager.list_sessions()
            >>>
            >>> # Sessions for specific server
            >>> sessions = manager.list_sessions(server=my_server)
        """
        ...

    def is_active(self, session: McpSession) -> bool:
        """Check if a session is active.

        Args:
            session: Session to check

        Returns:
            True if active

        Example:
            >>> if manager.is_active(session):
            ...     print("Session is active")
        """
        ...

    async def refresh_session(self, session: McpSession) -> None:
        """Refresh a session (e.g., renew authentication).

        Args:
            session: Session to refresh

        Example:
            >>> await manager.refresh_session(session)
        """
        ...

    def get_session_metadata(self, session: McpSession) -> dict[str, Any]:
        """Get metadata for a session.

        Args:
            session: Session

        Returns:
            Session metadata

        Example:
            >>> metadata = manager.get_session_metadata(session)
            >>> print(f"Created: {metadata['created_at']}")
        """
        ...

    def set_session_metadata(self, session: McpSession, metadata: dict[str, Any]) -> None:
        """Set metadata for a session.

        Args:
            session: Session
            metadata: Metadata to set

        Example:
            >>> manager.set_session_metadata(session, {"user_id": "123"})
        """
        ...

    async def get_or_create_session(self, server: McpServer, reuse: bool = True) -> McpSession:
        """Get existing session or create new one.

        Args:
            server: MCP server
            reuse: Reuse existing session if available

        Returns:
            MCP session

        Example:
            >>> # Reuse existing session if available
            >>> session = await manager.get_or_create_session(server)
        """
        ...

    def get_session_count(self, active_only: bool = True) -> int:
        """Get count of sessions.

        Args:
            active_only: Only count active sessions

        Returns:
            Session count

        Example:
            >>> count = manager.get_session_count()
            >>> print(f"Active sessions: {count}")
        """
        ...


__all__ = ["SessionManager"]
