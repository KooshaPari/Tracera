"""
Session storage backends for AuthKit credentials.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import aiofiles


class SessionStorage(ABC):
    """
    Abstract session storage interface.
    """

    @abstractmethod
    async def save(self, credentials: dict[str, Any]):
        """
        Save credentials.
        """

    @abstractmethod
    async def load(self) -> dict[str, Any] | None:
        """
        Load credentials.
        """

    @abstractmethod
    async def clear(self):
        """
        Clear stored credentials.
        """

    @classmethod
    def filesystem(cls, path: str = "~/.authkit/session.json") -> FilesystemStorage:
        """Create filesystem storage.

        Args:
            path: Path to session file

        Returns:
            FilesystemStorage instance
        """
        return FilesystemStorage(path)

    @classmethod
    def memory(cls) -> MemoryStorage:
        """Create in-memory storage (for testing).

        Returns:
            MemoryStorage instance
        """
        return MemoryStorage()


class FilesystemStorage(SessionStorage):
    """
    Store credentials in local filesystem.
    """

    def __init__(self, path: str = "~/.authkit/session.json"):
        """Initialize filesystem storage.

        Args:
            path: Path to session file
        """
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def save(self, credentials: dict[str, Any]):
        """
        Save credentials to file.
        """
        async with aiofiles.open(self.path, "w") as f:
            await f.write(json.dumps(credentials, indent=2))

    async def load(self) -> dict[str, Any] | None:
        """
        Load credentials from file.
        """
        if not self.path.exists():
            return None

        try:
            async with aiofiles.open(self.path) as f:
                content = await f.read()
                return json.loads(content)
        except Exception:
            return None

    async def clear(self):
        """
        Delete session file.
        """
        if self.path.exists():
            self.path.unlink()


class MemoryStorage(SessionStorage):
    """
    Store credentials in memory (for testing).
    """

    def __init__(self):
        """
        Initialize memory storage.
        """
        self._data: dict[str, Any] | None = None

    async def save(self, credentials: dict[str, Any]):
        """
        Save credentials to memory.
        """
        self._data = credentials

    async def load(self) -> dict[str, Any] | None:
        """
        Load credentials from memory.
        """
        return self._data

    async def clear(self):
        """
        Clear stored credentials.
        """
        self._data = None
