"""Unit tests for AIService - Streaming chat with tool use support.

Tests SSE streaming, agentic tool loops, and provider routing.
"""

import asyncio
import json
import pathlib
import tempfile
from typing import Any, ClassVar
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.test_constants import COUNT_THREE, COUNT_TWO
from tracertm.services.ai_service import (
    AIService,
    AIServiceError,
    SSEEvent,
    format_sse,
    get_ai_service,
)

pytestmark = pytest.mark.unit


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_anthropic_client() -> None:
    """Create a mock Anthropic client."""
    return AsyncMock()


@pytest.fixture
def ai_service(mock_anthropic_client: Any) -> None:
    """Create AIService with mocked Anthropic client."""
    service = AIService()
    service._anthropic_client = mock_anthropic_client
    return service


@pytest.fixture
def mock_db_session() -> None:
    """Create a mock database session."""
    return AsyncMock()


@pytest.fixture
def sample_messages() -> None:
    """Sample chat messages for testing."""
    return [
        {"role": "user", "content": "Hello, how are you?"},
    ]


@pytest.fixture
def sample_system_prompt() -> str:
    """Sample system prompt for testing."""
    return "You are a helpful assistant."


# =============================================================================
# SSEEvent and format_sse Tests
# =============================================================================


class TestSSEEvent:
    """Test SSE event type constants."""

    def test_sse_event_types_defined(self) -> None:
        """All SSE event types are defined."""
        assert SSEEvent.TEXT == "text"
        assert SSEEvent.TOOL_USE_START == "tool_use_start"
        assert SSEEvent.TOOL_USE_INPUT == "tool_use_input"
        assert SSEEvent.TOOL_RESULT == "tool_result"
        assert SSEEvent.ERROR == "error"
        assert SSEEvent.DONE == "done"


class TestFormatSSE:
    """Test the format_sse helper function."""

    def test_format_sse_text_event(self) -> None:
        """format_sse creates proper SSE format for text events."""
        result = format_sse(SSEEvent.TEXT, {"content": "Hello"})

        assert result.startswith("data: ")
        assert result.endswith("\n\n")

        # Parse the JSON
        json_str = result[6:-2]  # Remove "data: " and "\n\n"
        data = json.loads(json_str)
        assert data["type"] == "text"
        assert data["data"]["content"] == "Hello"

    def test_format_sse_tool_use_start(self) -> None:
        """format_sse creates proper format for tool_use_start."""
        result = format_sse(
            SSEEvent.TOOL_USE_START,
            {
                "tool_name": "read_file",
                "tool_use_id": "tool_123",
            },
        )

        data = json.loads(result[6:-2])
        assert data["type"] == "tool_use_start"
        assert data["data"]["tool_name"] == "read_file"
        assert data["data"]["tool_use_id"] == "tool_123"

    def test_format_sse_done_event(self) -> None:
        """format_sse creates proper format for done event."""
        result = format_sse(SSEEvent.DONE, {})

        data = json.loads(result[6:-2])
        assert data["type"] == "done"
        assert data["data"] == {}

    def test_format_sse_error_event(self) -> None:
        """format_sse creates proper format for error event."""
        result = format_sse(SSEEvent.ERROR, {"error": "Something went wrong"})

        data = json.loads(result[6:-2])
        assert data["type"] == "error"
        assert data["data"]["error"] == "Something went wrong"


# =============================================================================
# AIService Initialization Tests
# =============================================================================


class TestAIServiceInitialization:
    """Test AIService initialization and configuration."""

    def test_ai_service_creates_without_client(self) -> None:
        """AIService initializes with lazy client loading."""
        service = AIService()
        assert service._anthropic_client is None

    def test_ai_service_client_property_requires_api_key(self) -> None:
        """Accessing anthropic_client without API key raises error."""
        service = AIService()

        with (
            patch.dict("os.environ", {}, clear=True),
            patch("os.getenv", return_value=None),
            pytest.raises(AIServiceError) as exc_info,
        ):
            _ = service.anthropic_client

        assert "ANTHROPIC_API_KEY" in str(exc_info.value)

    def test_get_ai_service_returns_singleton(self) -> None:
        """get_ai_service returns the same instance."""
        # Reset the global instance for testing
        import tracertm.services.ai_service as ai_module

        ai_module._ai_service = None

        service1 = get_ai_service()
        service2 = get_ai_service()

        assert service1 is service2


# =============================================================================
# stream_chat Tests
# =============================================================================


class TestStreamChat:
    """Test the main stream_chat method."""

    @pytest.mark.asyncio
    async def test_stream_chat_unsupported_provider(self, ai_service: Any, sample_messages: Any) -> None:
        """stream_chat raises error for unsupported providers."""
        with pytest.raises(AIServiceError) as exc_info:
            async for _ in ai_service.stream_chat(
                messages=sample_messages,
                provider="unsupported_provider",
            ):
                pass

        assert "Unknown provider" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_stream_chat_codex_not_implemented(self, ai_service: Any, sample_messages: Any) -> None:
        """stream_chat raises error for codex provider (not implemented)."""
        with pytest.raises(AIServiceError) as exc_info:
            async for _ in ai_service.stream_chat(
                messages=sample_messages,
                provider="codex",
            ):
                pass

        assert "not yet implemented" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_stream_chat_gemini_not_implemented(self, ai_service: Any, sample_messages: Any) -> None:
        """stream_chat raises error for gemini provider (not implemented)."""
        with pytest.raises(AIServiceError) as exc_info:
            async for _ in ai_service.stream_chat(
                messages=sample_messages,
                provider="gemini",
            ):
                pass

        assert "not yet implemented" in str(exc_info.value)


# =============================================================================
# stream_chat_with_tools Tests
# =============================================================================


class TestStreamChatWithTools:
    """Test streaming chat with tool use (non-streaming API)."""

    @pytest.mark.asyncio
    async def test_stream_chat_text_only_response(
        self, ai_service: Any, mock_anthropic_client: Any, sample_messages: Any
    ) -> None:
        """stream_chat handles text-only responses without tool use."""
        # Mock a simple text response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="Hello! I'm doing well, thank you for asking.")]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        events = [
            e
            async for e in ai_service.stream_chat_with_tools(
                messages=sample_messages,
                model="claude-sonnet-4-20250514",
            )
        ]

        # Should have text event and done event
        assert len(events) >= COUNT_TWO

        # Check for text event
        text_events = [e for e in events if SSEEvent.TEXT in e]
        assert len(text_events) >= 1

        # Check for done event
        done_events = [e for e in events if SSEEvent.DONE in e]
        assert len(done_events) == 1

    @pytest.mark.asyncio
    async def test_stream_chat_with_tool_use(
        self, ai_service: Any, mock_anthropic_client: Any, sample_messages: Any, mock_db_session: Any
    ) -> None:
        """stream_chat handles tool use and continues after tool result."""

        # First response with tool use - use real values, not MagicMock
        class ToolUseBlock:
            type = "tool_use"
            id = "tool_123"
            name = "read_file"
            input: ClassVar[dict] = {"path": "/test/file.txt"}

        class TextBlock:
            type = "text"
            text = "The file contains test content."

        tool_use_response = MagicMock()
        tool_use_response.content = [ToolUseBlock()]

        # Second response with text (after tool result)
        text_response = MagicMock()
        text_response.content = [TextBlock()]

        mock_anthropic_client.messages.create = AsyncMock(side_effect=[tool_use_response, text_response])

        # Mock tool execution
        with patch("tracertm.services.ai_service.execute_tool") as mock_execute:
            mock_execute.return_value = {"success": True, "result": {"content": "test content"}}

            events = [
                e
                async for e in ai_service.stream_chat_with_tools(
                    messages=sample_messages,
                    model="claude-sonnet-4-20250514",
                    db_session=mock_db_session,
                )
            ]

        # Should have tool_use_start, tool_use_input, tool_result events
        event_types = [json.loads(e[6:-2])["type"] for e in events if e.startswith("data: ")]

        assert SSEEvent.TOOL_USE_START in event_types
        assert SSEEvent.TOOL_USE_INPUT in event_types
        assert SSEEvent.TOOL_RESULT in event_types
        assert SSEEvent.DONE in event_types

    @pytest.mark.asyncio
    async def test_stream_chat_max_iterations(
        self,
        ai_service: Any,
        mock_anthropic_client: Any,
        sample_messages: Any,
        mock_db_session: Any,
    ) -> None:
        """stream_chat respects max_tool_iterations limit."""
        # Always return tool use (infinite loop scenario)
        tool_use_response = MagicMock()
        tool_use_block = MagicMock(
            type="tool_use",
            id="tool_123",
            name="read_file",
            input={"path": "/test/file.txt"},
        )
        tool_use_response.content = [tool_use_block]

        mock_anthropic_client.messages.create = AsyncMock(return_value=tool_use_response)

        with patch("tracertm.services.ai_service.execute_tool") as mock_execute:
            mock_execute.return_value = {"success": True, "result": {}}

            events = [
                e
                async for e in ai_service.stream_chat_with_tools(
                    messages=sample_messages,
                    model="claude-sonnet-4-20250514",
                    max_tool_iterations=3,
                    db_session=mock_db_session,
                )
            ]

        # Should stop after max iterations
        # Count tool use starts
        tool_starts = sum(1 for e in events if SSEEvent.TOOL_USE_START in e)
        assert tool_starts <= COUNT_THREE

    @pytest.mark.asyncio
    async def test_stream_chat_handles_api_error(
        self, ai_service: Any, mock_anthropic_client: Any, sample_messages: Any
    ) -> None:
        """stream_chat handles API errors gracefully."""
        mock_anthropic_client.messages.create = AsyncMock(side_effect=Exception("API Error: Rate limit exceeded"))

        events = [
            e
            async for e in ai_service.stream_chat_with_tools(
                messages=sample_messages,
                model="claude-sonnet-4-20250514",
            )
        ]

        # Should have error event and done event
        error_events = [e for e in events if SSEEvent.ERROR in e]
        assert len(error_events) >= 1

        error_data = json.loads(error_events[0][6:-2])
        assert "Rate limit" in error_data["data"]["error"]


# =============================================================================
# stream_chat_with_tools_streaming Tests
# =============================================================================


class TestStreamChatWithToolsStreaming:
    """Test true streaming with tool use support."""

    @pytest.mark.asyncio
    async def test_streaming_text_deltas(
        self, ai_service: Any, mock_anthropic_client: Any, sample_messages: Any
    ) -> None:
        """Streaming mode yields text deltas as they arrive."""
        # Mock the streaming context manager
        mock_stream = AsyncMock()

        # Create async iterator for stream events
        async def mock_stream_events() -> None:
            await asyncio.sleep(0)
            # Text content block
            yield MagicMock(type="content_block_start", content_block=MagicMock(type="text"))
            yield MagicMock(type="content_block_delta", delta=MagicMock(type="text_delta", text="Hello"))
            yield MagicMock(type="content_block_delta", delta=MagicMock(type="text_delta", text=" World"))
            yield MagicMock(type="content_block_stop")

        mock_stream.__aiter__ = lambda self: mock_stream_events()

        # Mock get_final_message
        final_message = MagicMock()
        final_message.content = [MagicMock(type="text", text="Hello World")]
        mock_stream.get_final_message = AsyncMock(return_value=final_message)

        # Create async context manager
        async_cm = AsyncMock()
        async_cm.__aenter__.return_value = mock_stream
        async_cm.__aexit__.return_value = None

        mock_anthropic_client.messages.stream = MagicMock(return_value=async_cm)

        events = [
            e
            async for e in ai_service.stream_chat_with_tools_streaming(
                messages=sample_messages,
                model="claude-sonnet-4-20250514",
            )
        ]

        # Should have multiple text events (one per delta)
        text_events = [e for e in events if SSEEvent.TEXT in e]
        assert len(text_events) >= COUNT_TWO

    @pytest.mark.asyncio
    async def test_streaming_tool_use(
        self, ai_service: Any, mock_anthropic_client: Any, sample_messages: Any, mock_db_session: Any
    ) -> None:
        """Streaming mode handles tool use with JSON input deltas."""

        # Define proper event objects with real attribute values
        class ToolUseBlock:
            type = "tool_use"
            id = "tool_123"
            name = "read_file"
            input: ClassVar[dict] = {"path": "/test.txt"}

        class TextBlock:
            type = "text"
            text = "Done"

        class ContentBlockToolUse:
            type = "tool_use"
            id = "tool_123"
            name = "read_file"

        class ToolBlockStart:
            type = "content_block_start"
            content_block = ContentBlockToolUse

        class InputJsonDeltaPart1:
            type = "input_json_delta"
            partial_json = '{"path"'

        class InputJsonDelta1:
            type = "content_block_delta"
            delta = InputJsonDeltaPart1

        class InputJsonDeltaPart2:
            type = "input_json_delta"
            partial_json = ': "/test.txt"}'

        class InputJsonDelta2:
            type = "content_block_delta"
            delta = InputJsonDeltaPart2

        class BlockStop:
            type = "content_block_stop"

        class ContentBlockText:
            type = "text"

        class TextBlockStart:
            type = "content_block_start"
            content_block = ContentBlockText

        class TextDeltaInner:
            type = "text_delta"
            text = "Done"

        class TextDelta:
            type = "content_block_delta"
            delta = TextDeltaInner

        # First iteration: tool use
        mock_stream1 = AsyncMock()

        async def mock_tool_events() -> None:
            await asyncio.sleep(0)
            yield ToolBlockStart()
            yield InputJsonDelta1()
            yield InputJsonDelta2()
            yield BlockStop()

        mock_stream1.__aiter__ = lambda self: mock_tool_events()

        final_message1 = MagicMock()
        final_message1.content = [ToolUseBlock()]
        mock_stream1.get_final_message = AsyncMock(return_value=final_message1)

        # Second iteration: text response
        mock_stream2 = AsyncMock()

        async def mock_text_events() -> None:
            await asyncio.sleep(0)
            yield TextBlockStart()
            yield TextDelta()
            yield BlockStop()

        mock_stream2.__aiter__ = lambda self: mock_text_events()

        final_message2 = MagicMock()
        final_message2.content = [TextBlock()]
        mock_stream2.get_final_message = AsyncMock(return_value=final_message2)

        # Create context managers
        async_cm1 = AsyncMock()
        async_cm1.__aenter__.return_value = mock_stream1
        async_cm1.__aexit__.return_value = None

        async_cm2 = AsyncMock()
        async_cm2.__aenter__.return_value = mock_stream2
        async_cm2.__aexit__.return_value = None

        mock_anthropic_client.messages.stream = MagicMock(side_effect=[async_cm1, async_cm2])

        with patch("tracertm.services.ai_service.execute_tool") as mock_execute:
            mock_execute.return_value = {"success": True, "result": {"content": "test"}}

            events = [
                e
                async for e in ai_service.stream_chat_with_tools_streaming(
                    messages=sample_messages,
                    model="claude-sonnet-4-20250514",
                    db_session=mock_db_session,
                )
            ]

        event_types = [json.loads(e[6:-2])["type"] for e in events if e.startswith("data: ")]

        assert SSEEvent.TOOL_USE_START in event_types
        assert SSEEvent.TOOL_USE_INPUT in event_types
        assert SSEEvent.TOOL_RESULT in event_types

    @pytest.mark.asyncio
    async def test_streaming_handles_error(
        self, ai_service: Any, mock_anthropic_client: Any, sample_messages: Any
    ) -> None:
        """Streaming mode handles errors gracefully."""
        async_cm = AsyncMock()
        async_cm.__aenter__.side_effect = Exception("Connection error")

        mock_anthropic_client.messages.stream = MagicMock(return_value=async_cm)

        events = [
            e
            async for e in ai_service.stream_chat_with_tools_streaming(
                messages=sample_messages,
                model="claude-sonnet-4-20250514",
            )
        ]

        error_events = [e for e in events if SSEEvent.ERROR in e]
        assert len(error_events) >= 1


# =============================================================================
# simple_chat Tests
# =============================================================================


class TestSimpleChat:
    """Test non-streaming simple_chat method."""

    @pytest.mark.asyncio
    async def test_simple_chat_returns_text(
        self, ai_service: Any, mock_anthropic_client: Any, sample_messages: Any
    ) -> None:
        """simple_chat returns concatenated text response."""

        # Mock the streaming method to return text events
        async def mock_stream(*args: Any, **kwargs: Any) -> None:
            await asyncio.sleep(0)
            yield format_sse(SSEEvent.TEXT, {"content": "Hello "})
            yield format_sse(SSEEvent.TEXT, {"content": "World"})
            yield format_sse(SSEEvent.DONE, {})

        ai_service.stream_chat = MagicMock(return_value=mock_stream())

        result = await ai_service.simple_chat(
            messages=sample_messages,
            provider="claude",
        )

        assert result == "Hello World"

    @pytest.mark.asyncio
    async def test_simple_chat_handles_empty_response(
        self, ai_service: Any, mock_anthropic_client: Any, sample_messages: Any
    ) -> None:
        """simple_chat handles empty responses."""

        async def mock_stream(*args: Any, **kwargs: Any) -> None:
            await asyncio.sleep(0)
            yield format_sse(SSEEvent.DONE, {})

        ai_service.stream_chat = MagicMock(return_value=mock_stream())

        result = await ai_service.simple_chat(
            messages=sample_messages,
            provider="claude",
        )

        assert result == ""


# =============================================================================
# run_chat_turn_with_tools Tests
# =============================================================================


class TestRunChatTurnWithTools:
    """Test non-streaming run_chat_turn_with_tools (tool loop, returns final text)."""

    @pytest.mark.asyncio
    async def test_run_chat_turn_with_tools_returns_text(
        self, ai_service: Any, mock_anthropic_client: Any, sample_messages: Any
    ) -> None:
        """run_chat_turn_with_tools returns final assistant text when no tool use."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="Here is the answer.")]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        result = await ai_service.run_chat_turn_with_tools(
            messages=sample_messages,
            model="claude-sonnet-4-20250514",
        )

        assert result == "Here is the answer."
        mock_anthropic_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_chat_turn_with_tools_tool_use_then_text(
        self,
        ai_service: Any,
        mock_anthropic_client: Any,
        sample_messages: Any,
    ) -> None:
        """run_chat_turn_with_tools runs tool loop and returns final text after tool result."""
        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.id = "tu_1"
        tool_block.name = "read_file"
        work_dir = tempfile.mkdtemp(prefix="trace_test_")
        tool_block.input = {"path": str(pathlib.Path(work_dir) / "foo.txt")}

        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "File content: hello"

        # First call: tool use
        response1 = MagicMock()
        response1.content = [tool_block]
        # Second call: text (after tool result)
        response2 = MagicMock()
        response2.content = [text_block]

        mock_anthropic_client.messages.create = AsyncMock(side_effect=[response1, response2])

        with patch("tracertm.services.ai_service.execute_tool", new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {"success": True, "result": {"content": "hello"}}

            result = await ai_service.run_chat_turn_with_tools(
                messages=sample_messages,
                model="claude-sonnet-4-20250514",
                working_directory=work_dir,
            )

        assert result == "File content: hello"
        assert mock_anthropic_client.messages.create.call_count == COUNT_TWO
        mock_execute.assert_called()

    @pytest.mark.asyncio
    async def test_run_chat_turn_with_tools_handles_error(
        self, ai_service: Any, mock_anthropic_client: Any, sample_messages: Any
    ) -> None:
        """run_chat_turn_with_tools returns error message on API exception."""
        mock_anthropic_client.messages.create = AsyncMock(side_effect=Exception("API error"))

        result = await ai_service.run_chat_turn_with_tools(
            messages=sample_messages,
            model="claude-sonnet-4-20250514",
        )

        assert "[Error:" in result
        assert "API error" in result


# =============================================================================
# Message Conversion Tests
# =============================================================================


class TestMessageConversion:
    """Test message format conversion for Anthropic API."""

    @pytest.mark.asyncio
    async def test_filters_system_messages(self, ai_service: Any, mock_anthropic_client: Any) -> None:
        """System messages are filtered out (handled separately)."""
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
        ]

        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="Hi")]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        _ = [
            e
            async for e in ai_service.stream_chat_with_tools(
                messages=messages,
                model="claude-sonnet-4-20250514",
                system_prompt="You are helpful",
            )
        ]

        # Verify the call was made without system role in messages
        call_kwargs = mock_anthropic_client.messages.create.call_args[1]
        message_roles = [m["role"] for m in call_kwargs["messages"]]
        assert "system" not in message_roles

    @pytest.mark.asyncio
    async def test_preserves_message_order(self, ai_service: Any, mock_anthropic_client: Any) -> None:
        """Message order is preserved in conversion."""
        messages = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Response"},
            {"role": "user", "content": "Second"},
        ]

        mock_response = MagicMock()
        mock_response.content = [MagicMock(type="text", text="Final")]
        mock_anthropic_client.messages.create = AsyncMock(return_value=mock_response)

        _ = [
            e
            async for e in ai_service.stream_chat_with_tools(
                messages=messages,
                model="claude-sonnet-4-20250514",
            )
        ]

        call_kwargs = mock_anthropic_client.messages.create.call_args[1]
        assert call_kwargs["messages"][0]["content"] == "First"
        assert call_kwargs["messages"][1]["content"] == "Response"
        assert call_kwargs["messages"][2]["content"] == "Second"


# =============================================================================
# Integration Tests with Tools
# =============================================================================


class TestToolIntegration:
    """Test integration between AI service and tool execution."""

    @pytest.mark.asyncio
    async def test_tool_result_format(
        self, ai_service: Any, mock_anthropic_client: Any, sample_messages: Any, mock_db_session: Any
    ) -> None:
        """Tool results are properly formatted for API."""

        # Define proper block classes
        class ToolUseBlock:
            type = "tool_use"
            id = "tool_123"
            name = "read_file"
            input: ClassVar[dict] = {"path": "/test.txt"}

        class TextBlock:
            type = "text"
            text = "Done"

        # Response with tool use
        tool_response = MagicMock()
        tool_response.content = [ToolUseBlock()]

        # Final response
        text_response = MagicMock()
        text_response.content = [TextBlock()]

        mock_anthropic_client.messages.create = AsyncMock(side_effect=[tool_response, text_response])

        with patch("tracertm.services.ai_service.execute_tool") as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "result": {"content": "file content", "path": "/test.txt"},
            }

            _ = [
                e
                async for e in ai_service.stream_chat_with_tools(
                    messages=sample_messages,
                    model="claude-sonnet-4-20250514",
                    db_session=mock_db_session,
                )
            ]

        # Verify tool was called with correct parameters
        mock_execute.assert_called()
        call_kwargs = mock_execute.call_args[1]
        assert call_kwargs["tool_name"] == "read_file"
        assert call_kwargs["tool_input"]["path"] == "/test.txt"

    @pytest.mark.asyncio
    async def test_failed_tool_continues_conversation(
        self,
        ai_service: Any,
        mock_anthropic_client: Any,
        sample_messages: Any,
        mock_db_session: Any,
    ) -> None:
        """Failed tool execution continues conversation with error result."""

        class ToolUseBlock:
            type = "tool_use"
            id = "tool_123"
            name = "read_file"
            input: ClassVar[dict] = {"path": "/missing.txt"}

        class TextBlock:
            type = "text"
            text = "File not found, let me help."

        tool_response = MagicMock()
        tool_response.content = [ToolUseBlock()]

        text_response = MagicMock()
        text_response.content = [TextBlock()]

        mock_anthropic_client.messages.create = AsyncMock(side_effect=[tool_response, text_response])

        with patch("tracertm.services.ai_service.execute_tool") as mock_execute:
            mock_execute.return_value = {
                "success": False,
                "error": "File not found: /missing.txt",
            }

            events = [
                e
                async for e in ai_service.stream_chat_with_tools(
                    messages=sample_messages,
                    model="claude-sonnet-4-20250514",
                    db_session=mock_db_session,
                )
            ]

        # Should still complete with done event
        done_events = [e for e in events if SSEEvent.DONE in e]
        assert len(done_events) == 1

        # Tool result should contain error
        result_events = [e for e in events if SSEEvent.TOOL_RESULT in e]
        assert len(result_events) >= 1
        result_data = json.loads(result_events[0][6:-2])
        assert result_data["data"]["result"]["success"] is False
