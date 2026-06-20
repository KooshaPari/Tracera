"""Token management for TraceRTM MCP.

Handles:
- Token storage and retrieval
- Token refresh
- Token validation
- Scope management
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TokenInfo:
    """Token information."""

    access_token: str
    token_type: str = "bearer"
    expires_at: int | None = None
    refresh_token: str | None = None
    scopes: list[str] | None = None
    user_id: str | None = None
    email: str | None = None

    def __post_init__(self) -> None:
        """Initialize list of scopes if not provided."""
        if self.scopes is None:
            self.scopes = []

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for JSON serialization."""
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_at": self.expires_at,
            "refresh_token": self.refresh_token,
            "scopes": self.scopes,
            "user_id": self.user_id,
            "email": self.email,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> TokenInfo:
        """Create TokenInfo from dictionary."""
        access_token = data.get("access_token", "")
        token_type = data.get("token_type", "bearer")
        expires_at = data.get("expires_at")
        refresh_token = data.get("refresh_token")
        scopes = data.get("scopes", [])
        user_id = data.get("user_id")
        email = data.get("email")

        return cls(
            access_token=str(access_token) if access_token else "",
            token_type=str(token_type) if token_type else "bearer",
            expires_at=int(expires_at) if isinstance(expires_at, (int, float)) else None,
            refresh_token=str(refresh_token) if refresh_token else None,
            scopes=list(scopes) if isinstance(scopes, list) else None,
            user_id=str(user_id) if user_id else None,
            email=str(email) if email else None,
        )

    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return time.time() > self.expires_at

    def is_expiring_soon(self, threshold_seconds: int = 300) -> bool:
        """Check if token is expiring soon."""
        if not self.expires_at:
            return False
        return self.expires_at - time.time() < threshold_seconds

    def has_scope(self, scope: str) -> bool:
        """Check if token has a specific scope."""
        return scope in (self.scopes or [])

    def has_scopes(self, scopes: list[str]) -> bool:
        """Check if token has all scopes."""
        return all(s in (self.scopes or []) for s in scopes)


class TokenManager:
    """Manages tokens for MCP operations."""

    def __init__(self, config_dir: Path | None = None) -> None:
        """Initialize token manager.

        Args:
            config_dir: Directory for storing tokens (default: ~/.tracertm/mcp)
        """
        self.config_dir = config_dir or (Path.home() / ".tracertm" / "mcp")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._token_file = self.config_dir / "token.json"
        self._current_token: TokenInfo | None = None

    def save_token(self, token: TokenInfo) -> None:
        """Save token to storage.

        Args:
            token: Token information
        """
        try:
            data = token.to_dict()
            self._token_file.write_text(json.dumps(data, indent=2))
            self._token_file.chmod(0o600)
            self._current_token = token
            logger.debug("Token saved to %s", self._token_file)
        except Exception:
            logger.exception("Failed to save token")
            raise

    def load_token(self) -> TokenInfo | None:
        """Load token from storage.

        Returns:
            Token information or None
        """
        if self._current_token:
            return self._current_token

        try:
            if not self._token_file.exists():
                return None

            data = json.loads(self._token_file.read_text())
            token = TokenInfo.from_dict(data)
            self._current_token = token
        except Exception as e:
            logger.warning("Failed to load token: %s", e)
            return None
        else:
            return token

    def get_valid_token(self) -> str | None:
        """Get a valid (non-expired) token.

        Returns:
            Access token string or None
        """
        token = self.load_token()
        if not token:
            return None

        if token.is_expired():
            logger.debug("Token is expired")
            return None

        return token.access_token

    def clear_token(self) -> None:
        """Clear stored token."""
        try:
            if self._token_file.exists():
                self._token_file.unlink()
            self._current_token = None
            logger.debug("Token cleared")
        except Exception:
            logger.exception("Failed to clear token")

    def is_authenticated(self) -> bool:
        """Check if MCP is authenticated.

        Returns:
            True if valid token exists
        """
        return self.get_valid_token() is not None


def get_token_manager() -> TokenManager:
    """Get the global token manager instance."""
    return TokenManager()
