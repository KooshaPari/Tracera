"""
AuthKit token manager built on top of the shared pheno.auth token storage.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ...token_manager import FileTokenManager
from ...types import AuthTokens
from ..storage.session import SessionStorage

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


class TokenManager:
    """
    Manage OAuth tokens for AuthKit using the shared FileTokenManager.
    """

    def __init__(
        self,
        storage: SessionStorage | None = None,
        *,
        storage_path: str | Path | None = None,
        storage_key: str = "authkit",
        refresh_handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any] | None]] | None = None,
    ):
        self.storage = storage or SessionStorage.filesystem()
        self.storage_key = storage_key
        self.refresh_handler = refresh_handler
        self._lock = asyncio.Lock()

        path_hint: Path | None = None
        if storage_path is not None:
            path_hint = Path(storage_path)
        else:
            path_attr = getattr(self.storage, "path", None)
            if path_attr:
                path_hint = Path(path_attr).with_name("tokens.json")

        if path_hint is None:
            self._token_store = FileTokenManager(storage_path=None)
        else:
            self._token_store = FileTokenManager(path_hint)

    async def get_access_token(self) -> str | None:
        """
        Return a valid access token; refresh if possible.
        """
        async with self._lock:
            tokens = await self._token_store.retrieve(self.storage_key)

        if tokens is None:
            return None

        if tokens.is_expired():
            refreshed = await self.refresh_tokens()
            if not refreshed:
                return None
            return refreshed.get("access_token")

        return tokens.access_token

    async def refresh_tokens(self) -> dict[str, Any] | None:
        """
        Refresh tokens using the provided refresh handler.
        """
        async with self._lock:
            tokens = await self._token_store.retrieve(self.storage_key)

        if tokens is None or not tokens.refresh_token:
            return None

        if not self.refresh_handler:
            return None

        metadata = tokens.metadata or {}
        metadata.setdefault("refresh_token", tokens.refresh_token)
        metadata.setdefault("access_token", tokens.access_token)

        try:
            refreshed = await self.refresh_handler(metadata)
        except Exception:
            return None

        if not refreshed:
            return None

        await self.save_tokens(refreshed)
        return refreshed

    async def save_tokens(self, credentials: dict[str, Any]) -> None:
        """
        Persist token response data.
        """
        expires_at = credentials.get("expires_at")
        dt_expires = None
        if isinstance(expires_at, str):
            dt_expires = datetime.fromisoformat(expires_at)
            if dt_expires.tzinfo is None:
                dt_expires = dt_expires.replace(tzinfo=UTC)
        elif isinstance(expires_at, datetime):
            dt_expires = (
                expires_at if expires_at.tzinfo else expires_at.replace(tzinfo=UTC)
            )
        elif (expires_in := credentials.get("expires_in")) is not None:
            dt_expires = datetime.now(UTC) + timedelta(seconds=int(expires_in))

        tokens = AuthTokens(
            access_token=credentials["access_token"],
            refresh_token=credentials.get("refresh_token"),
            id_token=credentials.get("id_token"),
            token_type=credentials.get("token_type", "Bearer"),
            expires_at=dt_expires,
            scope=credentials.get("scope"),
            metadata=credentials,
        )

        async with self._lock:
            await self._token_store.store(self.storage_key, tokens)

        await self.storage.save(credentials)

    async def load_tokens(self) -> dict[str, Any] | None:
        """
        Load raw credentials from storage.
        """
        return await self.storage.load()

    async def clear(self) -> None:
        """
        Clear stored credentials and tokens.
        """
        async with self._lock:
            await self._token_store.revoke(self.storage_key)
        await self.storage.clear()
