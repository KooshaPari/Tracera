"""Generic session management for authentication flows.

This module provides abstract base classes and utilities for managing
authentication sessions across different storage backends (database, cache, memory).

Key Features:
- Abstract session store interface for different backends
- Session lifecycle management (create, validate, refresh, revoke)
- Configurable TTL and cleanup policies
- Extensible for database, Redis, memory, or custom stores

Usage:
    from pheno.auth.session_manager import SessionManager, SessionStore

    # Implement your storage backend
    class MySessionStore(SessionStore):
        async def save_session(self, session_id, data):
            ...

        async def get_session(self, session_id):
            ...

    # Use the session manager
    manager = SessionManager(store=MySessionStore(), ttl_hours=24)
    session_id = await manager.create_session(user_id, metadata)
    is_valid = await manager.validate_session(session_id)
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any
from uuid import uuid4


class SessionStore(ABC):
    """Abstract interface for session storage backends.

    Implement this interface to create custom session stores
    (e.g., database, Redis, file-based, in-memory).
    """

    @abstractmethod
    async def save_session(
        self,
        session_id: str,
        session_data: dict[str, Any],
    ) -> None:
        """Save or update a session.

        Args:
            session_id: Unique session identifier
            session_data: Session data to store (including metadata, expiry, etc.)
        """

    @abstractmethod
    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session data by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session data dict or None if not found
        """

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """

    @abstractmethod
    async def cleanup_expired_sessions(self) -> int:
        """Remove all expired sessions.

        Returns:
            Number of sessions cleaned up
        """


class InMemorySessionStore(SessionStore):
    """Simple in-memory session store for testing and development.

    NOT recommended for production use as sessions are lost on restart.
    """

    def __init__(self):
        """Initialize in-memory session store."""
        self._sessions: dict[str, dict[str, Any]] = {}

    async def save_session(
        self,
        session_id: str,
        session_data: dict[str, Any],
    ) -> None:
        """Save session to memory."""
        self._sessions[session_id] = session_data

    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Get session from memory."""
        return self._sessions.get(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """Delete session from memory."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    async def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions from memory."""
        now = time.time()
        expired = [
            sid
            for sid, data in self._sessions.items()
            if data.get("expires_at", float("inf")) < now
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)


class SessionManager:
    """Generic session manager for authentication flows.

    Manages session lifecycle including creation, validation, refresh,
    and cleanup using pluggable storage backends.

    Attributes:
        store: Session storage backend
        ttl_hours: Default session time-to-live in hours
        logger: Optional logger for debugging

    Examples:
        >>> store = InMemorySessionStore()
        >>> manager = SessionManager(store, ttl_hours=24)
        >>> session_id = await manager.create_session("user123", {"role": "admin"})
        >>> is_valid = await manager.validate_session(session_id)
        >>> await manager.revoke_session(session_id)
    """

    def __init__(
        self,
        store: SessionStore,
        ttl_hours: int = 24,
        logger: Any = None,
    ):
        """Initialize session manager.

        Args:
            store: Session storage backend
            ttl_hours: Session time-to-live in hours (default: 24)
            logger: Optional logger for debugging
        """
        self.store = store
        self.ttl_hours = ttl_hours
        self.logger = logger

    def _generate_session_id(self) -> str:
        """Generate unique session ID.

        Returns:
            UUID-based session identifier
        """
        return str(uuid4())

    def _calculate_expiry(self, ttl_hours: int | None = None) -> float:
        """Calculate session expiry timestamp.

        Args:
            ttl_hours: Override default TTL

        Returns:
            Unix timestamp for expiry
        """
        hours = ttl_hours if ttl_hours is not None else self.ttl_hours
        return time.time() + (hours * 3600)

    async def create_session(
        self,
        user_id: str,
        metadata: dict[str, Any] | None = None,
        ttl_hours: int | None = None,
    ) -> str:
        """Create a new session.

        Args:
            user_id: User identifier
            metadata: Optional metadata to store with session
            ttl_hours: Override default TTL for this session

        Returns:
            Generated session ID

        Examples:
            >>> session_id = await manager.create_session(
            ...     "user123",
            ...     metadata={"role": "admin", "org_id": "org456"}
            ... )
        """
        session_id = self._generate_session_id()
        expires_at = self._calculate_expiry(ttl_hours)

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": time.time(),
            "expires_at": expires_at,
            "metadata": metadata or {},
        }

        await self.store.save_session(session_id, session_data)

        if self.logger:
            self.logger.debug(f"Created session {session_id} for user {user_id}")

        return session_id

    async def validate_session(self, session_id: str) -> bool:
        """Validate if a session exists and is not expired.

        Args:
            session_id: Session identifier

        Returns:
            True if session is valid, False otherwise

        Examples:
            >>> if await manager.validate_session(session_id):
            ...     print("Session is valid")
        """
        session_data = await self.store.get_session(session_id)

        if not session_data:
            return False

        # Check expiry
        expires_at = session_data.get("expires_at", 0)
        if time.time() > expires_at:
            # Clean up expired session
            await self.store.delete_session(session_id)
            return False

        return True

    async def get_session_data(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session data.

        Args:
            session_id: Session identifier

        Returns:
            Session data dict or None if invalid/expired

        Examples:
            >>> data = await manager.get_session_data(session_id)
            >>> if data:
            ...     user_id = data["user_id"]
            ...     role = data["metadata"].get("role")
        """
        if not await self.validate_session(session_id):
            return None

        return await self.store.get_session(session_id)

    async def refresh_session(
        self,
        session_id: str,
        ttl_hours: int | None = None,
    ) -> bool:
        """Extend session expiry time.

        Args:
            session_id: Session identifier
            ttl_hours: New TTL from now (default: use manager's default)

        Returns:
            True if refreshed, False if session not found

        Examples:
            >>> await manager.refresh_session(session_id, ttl_hours=48)
        """
        session_data = await self.store.get_session(session_id)

        if not session_data:
            return False

        session_data["expires_at"] = self._calculate_expiry(ttl_hours)
        await self.store.save_session(session_id, session_data)

        if self.logger:
            self.logger.debug(f"Refreshed session {session_id}")

        return True

    async def revoke_session(self, session_id: str) -> bool:
        """Revoke (delete) a session.

        Args:
            session_id: Session identifier

        Returns:
            True if revoked, False if not found

        Examples:
            >>> await manager.revoke_session(session_id)
        """
        success = await self.store.delete_session(session_id)

        if success and self.logger:
            self.logger.debug(f"Revoked session {session_id}")

        return success

    async def cleanup_expired_sessions(self) -> int:
        """Remove all expired sessions from storage.

        Returns:
            Number of sessions cleaned up

        Examples:
            >>> count = await manager.cleanup_expired_sessions()
            >>> print(f"Cleaned up {count} expired sessions")
        """
        count = await self.store.cleanup_expired_sessions()

        if self.logger and count > 0:
            self.logger.info(f"Cleaned up {count} expired sessions")

        return count


__all__ = [
    "InMemorySessionStore",
    "SessionManager",
    "SessionStore",
]
