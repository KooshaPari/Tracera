"""Token manager implementations for the pheno auth stack.

Provides a file-backed token manager that satisfies the TokenManager
interface defined in :mod:`pheno.auth.interfaces`, combining an in-memory
cache with optional encrypted persistence.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .interfaces import AuthProvider, TokenManager
from .types import AuthTokens


@dataclass
class _StoredTokens:
    """
    Serializable representation of :class:`AuthTokens`.
    """

    access_token: str
    refresh_token: str | None = None
    id_token: str | None = None
    token_type: str = "Bearer"
    expires_at: str | None = None
    scope: str | None = None
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_auth_tokens(cls, tokens: AuthTokens) -> _StoredTokens:
        expires_at = tokens.expires_at.isoformat() if tokens.expires_at else None
        return cls(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            id_token=tokens.id_token,
            token_type=tokens.token_type,
            expires_at=expires_at,
            scope=tokens.scope,
            metadata=tokens.metadata or {},
        )

    def to_auth_tokens(self) -> AuthTokens:
        expires_at = None
        if self.expires_at:
            expires_at = datetime.fromisoformat(self.expires_at)
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=UTC)
        return AuthTokens(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            id_token=self.id_token,
            token_type=self.token_type,
            expires_at=expires_at,
            scope=self.scope,
            metadata=self.metadata or {},
        )


class _TokenStorage:
    """
    Lightweight encrypted JSON storage.
    """

    def __init__(self, path: Path, encryption_key: str | None = None):
        self._path = Path(path).expanduser()
        self._encryption_key = encryption_key

    def load_all(self) -> dict[str, dict[str, Any]]:
        if not self._path.exists():
            return {}
        try:
            raw = self._path.read_text(encoding="utf-8")
            data = self._decrypt(raw)
            return json.loads(data)
        except (OSError, json.JSONDecodeError):
            return {}

    def save_all(self, payload: dict[str, dict[str, Any]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(payload, indent=2)
        encoded = self._encrypt(raw)
        self._path.write_text(encoded, encoding="utf-8")
        try:
            import os

            os.chmod(self._path, 0o600)
        except (OSError, AttributeError):
            pass

    def delete(self) -> None:
        try:
            self._path.unlink()
        except FileNotFoundError:
            return

    def _encrypt(self, data: str) -> str:
        if not self._encryption_key:
            return data
        key_bytes = self._encryption_key.encode("utf-8")
        data_bytes = data.encode("utf-8")
        encrypted = bytearray()
        for idx, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key_bytes[idx % len(key_bytes)])
        import base64

        return base64.b64encode(encrypted).decode("ascii")

    def _decrypt(self, data: str) -> str:
        if not self._encryption_key:
            return data
        import base64

        encrypted = base64.b64decode(data)
        key_bytes = self._encryption_key.encode("utf-8")
        decoded = bytearray()
        for idx, byte in enumerate(encrypted):
            decoded.append(byte ^ key_bytes[idx % len(key_bytes)])
        return decoded.decode("utf-8")


class FileTokenManager(TokenManager):
    """Token manager backed by an in-memory cache with optional disk persistence.

    Parameters
    ----------
    storage_path:
        Location of the JSON file used to persist tokens. When omitted,
        only the in-memory cache is used.
    encryption_key:
        Optional XOR key used to obfuscate the JSON on disk.
    """

    def __init__(
        self,
        storage_path: str | Path | None = None,
        *,
        encryption_key: str | None = None,
    ):
        self._storage = _TokenStorage(Path(storage_path), encryption_key) if storage_path else None
        self._memory: dict[str, AuthTokens] = {}
        self._lock = asyncio.Lock()

        if self._storage:
            for key, payload in self._storage.load_all().items():
                self._memory[key] = _StoredTokens(**payload).to_auth_tokens()

    async def store(self, key: str, tokens: AuthTokens) -> None:
        stored = _StoredTokens.from_auth_tokens(tokens)
        async with self._lock:
            self._memory[key] = stored.to_auth_tokens()
            if self._storage:
                payload = {
                    k: asdict(_StoredTokens.from_auth_tokens(val))
                    for k, val in self._memory.items()
                }
                self._storage.save_all(payload)

    async def retrieve(self, key: str) -> AuthTokens | None:
        async with self._lock:
            return self._memory.get(key)

    async def refresh_if_needed(
        self,
        key: str,
        provider: AuthProvider,
    ) -> AuthTokens | None:
        async with self._lock:
            tokens = self._memory.get(key)

        if tokens is None:
            return None

        if not tokens.is_expired():
            return tokens

        if not provider.supports_refresh() or not tokens.refresh_token:
            return tokens

        try:
            refreshed = await provider.refresh(tokens)
        except Exception:
            return None

        await self.store(key, refreshed)
        return refreshed

    async def revoke(self, key: str) -> None:
        async with self._lock:
            self._memory.pop(key, None)
            if self._storage:
                payload = {
                    k: asdict(_StoredTokens.from_auth_tokens(val))
                    for k, val in self._memory.items()
                }
                if payload:
                    self._storage.save_all(payload)
                else:
                    self._storage.delete()

    async def list_keys(self) -> list[str]:
        async with self._lock:
            return list(self._memory.keys())


__all__ = ["FileTokenManager"]
