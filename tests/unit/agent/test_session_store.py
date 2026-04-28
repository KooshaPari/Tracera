from typing import Any

"""Unit tests for tracertm.agent.session_store."""

import asyncio
import pathlib
import tempfile
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from tracertm.agent.sandbox.local_fs import LocalFilesystemSandboxProvider
from tracertm.agent.session_store import (
    AGENT_SESSION_CACHE_PREFIX,
    SessionSandboxStore,
    SessionSandboxStoreDB,
    _agent_session_cache_key,
)
from tracertm.agent.types import SandboxMetadata, SandboxStatus

pytestmark = pytest.mark.unit


class TestCacheKey:
    """Test cache key helper."""

    def test_agent_session_cache_key(self) -> None:
        assert _agent_session_cache_key("s1") == f"{AGENT_SESSION_CACHE_PREFIX}:s1"
        assert _agent_session_cache_key("abc-123") == f"{AGENT_SESSION_CACHE_PREFIX}:abc-123"


class TestSessionSandboxStore:
    """Test in-memory SessionSandboxStore."""

    @pytest.fixture
    def base_dir(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            yield d

    @pytest.fixture
    def store(self, base_dir: Any) -> None:
        provider = LocalFilesystemSandboxProvider(base_dir=base_dir)
        return SessionSandboxStore(sandbox_provider=provider)

    @pytest.mark.asyncio
    async def test_get_or_create_creates_sandbox(self, store: Any) -> None:
        path, created = await store.get_or_create("session-1")
        assert created is True
        assert path
        assert await asyncio.to_thread(pathlib.Path(path).is_dir)
        assert "session-1" in path

    @pytest.mark.asyncio
    async def test_get_or_create_idempotent(self, store: Any) -> None:
        path1, created1 = await store.get_or_create("session-2")
        path2, created2 = await store.get_or_create("session-2")
        assert path1 == path2
        assert created1 is True
        assert created2 is False

    @pytest.mark.asyncio
    async def test_get_returns_metadata_after_create(self, store: Any) -> None:
        path, _ = await store.get_or_create("session-3")
        meta = store.get("session-3")
        assert meta is not None
        assert meta.sandbox_id == "session-3"
        assert meta.sandbox_root == path
        assert meta.status == SandboxStatus.READY

    def test_get_missing_returns_none(self, store: Any) -> None:
        assert store.get("nonexistent") is None

    def test_delete_removes_from_store(self, store: Any) -> None:
        # Create via get_or_create first (sync test only checks delete of in-memory)
        # We need to populate _store manually for a sync test, or run async get_or_create then delete
        store._store["session-x"] = SandboxMetadata(
            sandbox_id="session-x",
            status=SandboxStatus.READY,
            created_at=datetime.now(UTC),
            sandbox_root="/tmp/x",
        )
        out = store.delete("session-x")
        assert out is True
        assert store.get("session-x") is None
        assert store.delete("session-x") is False


class TestSessionSandboxStoreDB:
    """Test DB-backed SessionSandboxStoreDB (with mocked DB and optional cache)."""

    @pytest.fixture
    def base_dir(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            yield d

    @pytest.mark.asyncio
    async def test_get_or_create_without_db_uses_provider(self, base_dir: Any) -> None:
        """When db_session is None, behaves like base store (provider only)."""
        provider = LocalFilesystemSandboxProvider(base_dir=base_dir)
        store = SessionSandboxStoreDB(sandbox_provider=provider, cache_service=None)
        path, created = await store.get_or_create("session-db1", db_session=None)
        assert created is True
        assert path
        assert await asyncio.to_thread(pathlib.Path(path).is_dir)

    @pytest.mark.asyncio
    async def test_get_or_create_with_cache_miss_then_provider(self, base_dir: Any) -> None:
        """When cache is present but returns None, falls through to provider when no DB."""
        provider = LocalFilesystemSandboxProvider(base_dir=base_dir)
        cache = AsyncMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()
        store = SessionSandboxStoreDB(sandbox_provider=provider, cache_service=cache)
        path, created = await store.get_or_create("session-c1", db_session=None)
        assert created is True
        assert path
        cache.get.assert_called_once()
        cache.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_or_create_with_cache_hit_returns_cached_path(self, base_dir: Any) -> None:
        """When cache returns a path, return it without creating sandbox."""
        provider = LocalFilesystemSandboxProvider(base_dir=base_dir)
        cache = AsyncMock()
        cache.get = AsyncMock(return_value="/cached/path")
        store = SessionSandboxStoreDB(sandbox_provider=provider, cache_service=cache)
        path, created = await store.get_or_create("session-c2", db_session=None)
        assert path == "/cached/path"
        assert created is False
        cache.get.assert_called_once()
        cache.set.assert_not_called()
