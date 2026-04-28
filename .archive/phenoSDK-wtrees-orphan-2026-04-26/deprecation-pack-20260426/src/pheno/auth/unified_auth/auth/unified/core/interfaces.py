"""Unified Authentication Interfaces.

Protocol-based interfaces for all authentication components. Consolidated from multiple
implementations.
"""

from abc import abstractmethod
from typing import Any, Protocol

from .types import AuthRequest, AuthResponse, AuthSession, AuthToken, AuthUser, MFAType


class AuthProviderProtocol(Protocol):
    """
    Protocol for authentication providers.
    """

    @abstractmethod
    async def authenticate(self, request: AuthRequest) -> AuthResponse:
        """
        Authenticate a user.
        """
        ...

    @abstractmethod
    async def get_user(self, user_id: str) -> AuthUser | None:
        """
        Get user by ID.
        """
        ...

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> AuthToken | None:
        """
        Refresh an access token.
        """
        ...


class OAuthProviderProtocol(Protocol):
    """
    Protocol for OAuth providers.
    """

    @abstractmethod
    def get_authorization_url(
        self, state: str | None = None, scope: str | None = None,
    ) -> str:
        """
        Get OAuth authorization URL.
        """
        ...

    @abstractmethod
    async def exchange_code(self, code: str, redirect_uri: str) -> AuthToken | None:
        """
        Exchange authorization code for token.
        """
        ...

    @abstractmethod
    async def get_user_info(self, token: AuthToken) -> AuthUser | None:
        """
        Get user information using token.
        """
        ...


class MFAProviderProtocol(Protocol):
    """
    Protocol for MFA providers.
    """

    @abstractmethod
    def get_mfa_type(self) -> MFAType:
        """
        Get the MFA type this provider handles.
        """
        ...

    @abstractmethod
    async def setup_mfa(self, user: AuthUser) -> dict[str, Any]:
        """
        Set up MFA for a user.
        """
        ...

    @abstractmethod
    async def verify_mfa(self, user: AuthUser, code: str) -> bool:
        """
        Verify MFA code for a user.
        """
        ...

    @abstractmethod
    async def disable_mfa(self, user: AuthUser) -> bool:
        """
        Disable MFA for a user.
        """
        ...


class SessionProviderProtocol(Protocol):
    """
    Protocol for session management.
    """

    @abstractmethod
    async def create_session(
        self, user: AuthUser, token: AuthToken, metadata: dict[str, Any] | None = None,
    ) -> AuthSession:
        """
        Create a new session.
        """
        ...

    @abstractmethod
    async def get_session(self, session_id: str) -> AuthSession | None:
        """
        Get session by ID.
        """
        ...

    @abstractmethod
    async def extend_session(self, session_id: str, minutes: int = 30) -> bool:
        """
        Extend session expiry.
        """
        ...

    @abstractmethod
    async def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a session.
        """
        ...

    @abstractmethod
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions, return count cleaned.
        """
        ...


class AuthStoreProtocol(Protocol):
    """
    Protocol for user/token storage.
    """

    @abstractmethod
    async def create_user(self, user: AuthUser) -> bool:
        """
        Create a new user.
        """
        ...

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> AuthUser | None:
        """
        Get user by ID.
        """
        ...

    @abstractmethod
    async def get_user_by_email(self, email: str) -> AuthUser | None:
        """
        Get user by email.
        """
        ...

    @abstractmethod
    async def update_user(self, user: AuthUser) -> bool:
        """
        Update user information.
        """
        ...

    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        """
        ...


class SecurityProviderProtocol(Protocol):
    """
    Protocol for security utilities.
    """

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """
        Hash a password securely.
        """
        ...

    @abstractmethod
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.
        """
        ...

    @abstractmethod
    def generate_token(self, payload: dict[str, Any], expires_in: int) -> str:
        """
        Generate a JWT token.
        """
        ...

    @abstractmethod
    def validate_token(self, token: str) -> dict[str, Any] | None:
        """
        Validate and decode a JWT token.
        """
        ...
