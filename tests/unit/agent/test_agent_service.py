from typing import Any

"""Unit tests for tracertm.agent.agent_service."""

import asyncio
import pathlib
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tracertm.agent import AgentService, get_agent_service
from tracertm.agent.sandbox.local_fs import LocalFilesystemSandboxProvider
from tracertm.agent.session_store import SessionSandboxStore
from tracertm.agent.types import SandboxConfig

pytestmark = pytest.mark.unit


class TestAgentServiceGetOrCreateSandbox:
    """Test AgentService.get_or_create_session_sandbox."""

    @pytest.fixture
    def base_dir(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            yield d

    @pytest.fixture
    def store(self, base_dir: Any) -> None:
        provider = LocalFilesystemSandboxProvider(base_dir=base_dir)
        return SessionSandboxStore(sandbox_provider=provider)

    @pytest.fixture
    def agent_service(self, store: Any) -> None:
        return AgentService(session_store=store)

    @pytest.mark.asyncio
    async def test_get_or_create_returns_path_and_created(self, agent_service: Any) -> None:
        path, created = await agent_service.get_or_create_session_sandbox("s1")
        assert path
        assert await asyncio.to_thread(pathlib.Path(path).is_dir)
        assert created is True
        path2, created2 = await agent_service.get_or_create_session_sandbox("s1")
        assert path == path2
        assert created2 is False

    @pytest.mark.asyncio
    async def test_get_or_create_empty_session_id_returns_none(self, agent_service: Any) -> None:
        path, created = await agent_service.get_or_create_session_sandbox("")
        assert path is None
        assert created is False
        path2, created2 = await agent_service.get_or_create_session_sandbox("   ")
        assert path2 is None
        assert created2 is False

    @pytest.mark.asyncio
    async def test_get_or_create_with_config_passes_to_store(self, agent_service: Any) -> None:
        config = SandboxConfig(project_id="proj-1")
        path, created = await agent_service.get_or_create_session_sandbox("s2", config=config)
        assert path
        assert created is True

    @pytest.mark.asyncio
    async def test_get_or_create_publishes_event_when_created(self, store: Any, _base_dir: Any) -> None:
        event_bus = AsyncMock()
        event_bus.publish = AsyncMock()
        agent_svc = AgentService(session_store=store, event_bus=event_bus)
        path, created = await agent_svc.get_or_create_session_sandbox("s3")
        assert created is True
        event_bus.publish.assert_called_once()
        call_args = event_bus.publish.call_args[0]
        assert call_args[0] == "agent.session.created"
        assert call_args[2] == "s3"  # entity_id = session_id
        assert call_args[3] == "agent_session"  # entity_type
        assert call_args[4]["session_id"] == "s3"
        assert call_args[4]["sandbox_root"] == path


class TestAgentServiceSimpleChatWithSandbox:
    """Test AgentService.simple_chat_with_sandbox with mocked AIService."""

    @pytest.fixture
    def base_dir(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            yield d

    @pytest.fixture
    def store(self, base_dir: Any) -> None:
        provider = LocalFilesystemSandboxProvider(base_dir=base_dir)
        return SessionSandboxStore(sandbox_provider=provider)

    @pytest.fixture
    def agent_service(self, store: Any) -> None:
        return AgentService(session_store=store)

    @pytest.mark.asyncio
    async def test_simple_chat_with_sandbox_calls_ai_and_returns_reply(self, agent_service: Any) -> None:
        messages = [{"role": "user", "content": "Hi"}]
        with patch("tracertm.services.ai_service.get_ai_service") as get_ai:
            mock_ai = MagicMock()
            mock_ai.simple_chat = AsyncMock(return_value="Hello!")
            get_ai.return_value = mock_ai
            reply = await agent_service.simple_chat_with_sandbox(
                messages=messages,
                session_id="chat-s1",
                provider="claude",
            )
            assert reply == "Hello!"
            mock_ai.simple_chat.assert_called_once()
            call_kw = mock_ai.simple_chat.call_args[1]
            assert call_kw["provider"] == "claude"
            assert call_kw["messages"] == messages

    @pytest.mark.asyncio
    async def test_simple_chat_without_session_id_uses_none_working_dir(self, agent_service: Any) -> None:
        messages = [{"role": "user", "content": "Hi"}]
        with patch("tracertm.services.ai_service.get_ai_service") as get_ai:
            mock_ai = MagicMock()
            mock_ai.simple_chat = AsyncMock(return_value="Hi")
            get_ai.return_value = mock_ai
            await agent_service.simple_chat_with_sandbox(
                messages=messages,
                session_id=None,
            )
            mock_ai.simple_chat.assert_called_once()


class TestGetAgentService:
    """Test get_agent_service singleton."""

    def test_get_agent_service_returns_agent_service(self) -> None:
        import tracertm.agent.agent_service as mod

        try:
            mod._agent_service = None
            svc = get_agent_service()
            assert isinstance(svc, AgentService)
            assert svc._store is not None
            assert get_agent_service() is svc
        finally:
            mod._agent_service = None
