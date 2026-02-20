"""AI Service for TraceRTM chat assistant.

Provides async streaming chat with tool use using the Anthropic SDK.
Supports an agentic loop where the AI can call tools and continue reasoning.


Functional Requirements: FR-AI-001, FR-AI-004, FR-AI-005
"""

from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING, Any

from .ai_tools import TOOLS, execute_tool

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception for AI service errors."""


# SSE Event Types
class SSEEvent:
    """Server-Sent Event types for streaming."""

    TEXT = "text"
    TOOL_USE_START = "tool_use_start"
    TOOL_USE_INPUT = "tool_use_input"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    DONE = "done"


def format_sse(event_type: str, data: object) -> str:
    """Format data as an SSE event."""
    json_data = json.dumps({"type": event_type, "data": data})
    return f"data: {json_data}\n\n"


class AIService:
    """Service for interacting with AI providers with tool use support."""

    def __init__(self) -> None:
        """Initialize AI service with API clients."""
        self._anthropic_client: Any = None

    @property
    def anthropic_client(self) -> Any:
        """Lazy initialization of Anthropic client."""
        if self._anthropic_client is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                msg = "ANTHROPIC_API_KEY environment variable is not set"
                raise AIServiceError(msg)
            try:
                import anthropic

                self._anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
            except ImportError as e:
                msg = "anthropic package is not installed. Run: pip install anthropic"
                raise AIServiceError(msg) from e
        return self._anthropic_client

    async def stream_chat_with_tools(
        self,
        messages: list[dict],
        model: str = "claude-sonnet-4-20250514",
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        working_directory: str | None = None,
        db_session: Any = None,
        max_tool_iterations: int = 10,
    ) -> AsyncIterator[str]:
        """Stream chat completion with tool use support.

        This implements an agentic loop:
        1. Send message to Claude with tools
        2. If Claude wants to use a tool, execute it
        3. Send tool result back to Claude
        4. Repeat until Claude gives a final text response

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model ID
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            working_directory: Base directory for file operations
            db_session: Database session for TraceRTM operations
            max_tool_iterations: Maximum number of tool use cycles

        Yields:
            SSE-formatted strings for streaming to client
        """
        # Convert messages to Anthropic format
        anthropic_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in messages if msg["role"] in {"user", "assistant"}
        ]

        iteration = 0

        while iteration < max_tool_iterations:
            iteration += 1

            try:
                # Call Claude with tools
                response = await self.anthropic_client.messages.create(  # type: ignore[attr-defined]
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt or "",
                    messages=anthropic_messages,
                    tools=TOOLS,
                )

                # Process response content blocks
                assistant_content = []
                has_tool_use = False

                for block in response.content:
                    if block.type == "text":
                        # Stream text content
                        yield format_sse(SSEEvent.TEXT, {"content": block.text})
                        assistant_content.append(block)

                    elif block.type == "tool_use":
                        has_tool_use = True
                        tool_name = block.name
                        tool_input = block.input
                        tool_use_id = block.id

                        # Notify client about tool use
                        yield format_sse(
                            SSEEvent.TOOL_USE_START,
                            {
                                "tool_name": tool_name,
                                "tool_use_id": tool_use_id,
                            },
                        )
                        yield format_sse(
                            SSEEvent.TOOL_USE_INPUT,
                            {
                                "tool_use_id": tool_use_id,
                                "input": tool_input,
                            },
                        )

                        # Execute the tool
                        tool_result = await execute_tool(
                            tool_name=tool_name,
                            tool_input=tool_input,
                            working_directory=working_directory,
                            db_session=db_session,
                        )

                        # Send tool result to client
                        yield format_sse(
                            SSEEvent.TOOL_RESULT,
                            {
                                "tool_use_id": tool_use_id,
                                "result": tool_result,
                            },
                        )

                        assistant_content.append(block)

                # Add assistant message to conversation
                anthropic_messages.append({
                    "role": "assistant",
                    "content": [
                        {"type": b.type, "text": b.text}
                        if b.type == "text"
                        else {"type": "tool_use", "id": b.id, "name": b.name, "input": b.input}
                        for b in assistant_content
                    ],
                })

                # If there were tool uses, add tool results and continue loop
                if has_tool_use:
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            result = await execute_tool(
                                tool_name=block.name,
                                tool_input=block.input,
                                working_directory=working_directory,
                                db_session=db_session,
                            )
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(result),
                            })

                    anthropic_messages.append({
                        "role": "user",
                        "content": tool_results,
                    })
                    continue  # Continue the agentic loop

                # No tool use, we're done
                break

            except Exception as e:
                logger.exception("Claude API error")
                yield format_sse(SSEEvent.ERROR, {"error": str(e)})
                break

        yield format_sse(SSEEvent.DONE, {})

    async def run_chat_turn_with_tools(
        self,
        messages: list[dict],
        model: str = "claude-sonnet-4-20250514",
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        working_directory: str | None = None,
        db_session: Any = None,
        max_tool_iterations: int = 10,
    ) -> str:
        """Run one agentic turn with tool use (no streaming). Returns final assistant text.

        Same loop as stream_chat_with_tools but accumulates and returns the last text reply.
        Used by Temporal run_agent_turn for checkpointed agent runs.
        """
        anthropic_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in messages if msg["role"] in {"user", "assistant"}
        ]

        iteration = 0
        final_text = ""

        while iteration < max_tool_iterations:
            iteration += 1
            try:
                response = await self.anthropic_client.messages.create(  # type: ignore[attr-defined]
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt or "",
                    messages=anthropic_messages,
                    tools=TOOLS,
                )
                assistant_content = []
                has_tool_use = False
                text_parts = []

                for block in response.content:
                    if block.type == "text":
                        text_parts.append(block.text)
                        assistant_content.append(block)
                    elif block.type == "tool_use":
                        has_tool_use = True
                        assistant_content.append(block)

                anthropic_messages.append({
                    "role": "assistant",
                    "content": [
                        {"type": b.type, "text": b.text}
                        if b.type == "text"
                        else {"type": "tool_use", "id": b.id, "name": b.name, "input": b.input}
                        for b in assistant_content
                    ],
                })

                if has_tool_use:
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            r = await execute_tool(
                                tool_name=block.name,
                                tool_input=block.input,
                                working_directory=working_directory,
                                db_session=db_session,
                            )
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(r),
                            })
                    anthropic_messages.append({"role": "user", "content": tool_results})
                    continue

                final_text = "".join(text_parts)
                break
            except Exception as e:
                logger.exception("run_chat_turn_with_tools error")
                final_text = f"[Error: {e}]"
                break

        return final_text or ""

    async def stream_chat_with_tools_streaming(
        self,
        messages: list[dict],
        model: str = "claude-sonnet-4-20250514",
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        working_directory: str | None = None,
        db_session: Any = None,
        max_tool_iterations: int = 10,
    ) -> AsyncIterator[str]:
        """Stream chat with true streaming (token by token) and tool use.

        This provides real-time streaming of text while still supporting tools.
        """
        # Convert messages to Anthropic format
        anthropic_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in messages if msg["role"] in {"user", "assistant"}
        ]

        iteration = 0

        while iteration < max_tool_iterations:
            iteration += 1

            try:
                # Stream response from Claude
                tool_uses: list[Any] = []
                current_tool_use: dict[str, Any] | None = None

                async with self.anthropic_client.messages.stream(
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt or "",
                    messages=anthropic_messages,
                    tools=TOOLS,
                ) as stream:
                    async for event in stream:
                        if event.type == "content_block_start":
                            block = event.content_block
                            if block.type == "tool_use":
                                current_tool_use = {
                                    "id": block.id,
                                    "name": block.name,
                                    "input_json": "",
                                }
                                yield format_sse(
                                    SSEEvent.TOOL_USE_START,
                                    {
                                        "tool_name": block.name,
                                        "tool_use_id": block.id,
                                    },
                                )

                        elif event.type == "content_block_delta":
                            delta = event.delta
                            if delta.type == "text_delta":
                                yield format_sse(SSEEvent.TEXT, {"content": delta.text})
                            elif delta.type == "input_json_delta" and current_tool_use:
                                current_tool_use["input_json"] += delta.partial_json

                        elif event.type == "content_block_stop":
                            if current_tool_use:
                                # Parse the accumulated JSON input
                                try:
                                    tool_input = json.loads(current_tool_use["input_json"])
                                except json.JSONDecodeError:
                                    tool_input = {}

                                current_tool_use["input"] = tool_input
                                tool_uses.append(current_tool_use)

                                yield format_sse(
                                    SSEEvent.TOOL_USE_INPUT,
                                    {
                                        "tool_use_id": current_tool_use["id"],
                                        "input": tool_input,
                                    },
                                )

                                current_tool_use = None

                    # Get the final message for conversation history
                    final_message = await stream.get_final_message()

                # If there were tool uses, execute them and continue
                if tool_uses:
                    # Build assistant message content
                    assistant_content = []
                    for block in final_message.content:
                        if block.type == "text":
                            assistant_content.append({
                                "type": "text",
                                "text": block.text,
                            })
                        elif block.type == "tool_use":
                            assistant_content.append({
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input,
                            })

                    anthropic_messages.append({
                        "role": "assistant",
                        "content": assistant_content,
                    })

                    # Execute tools and build results
                    tool_results = []
                    for tool_use in tool_uses:
                        result = await execute_tool(
                            tool_name=tool_use["name"],
                            tool_input=tool_use["input"],
                            working_directory=working_directory,
                            db_session=db_session,
                        )

                        yield format_sse(
                            SSEEvent.TOOL_RESULT,
                            {
                                "tool_use_id": tool_use["id"],
                                "result": result,
                            },
                        )

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tool_use["id"],
                            "content": json.dumps(result),
                        })

                    # Add tool results as user message
                    anthropic_messages.append({
                        "role": "user",
                        "content": tool_results,
                    })

                    continue  # Continue agentic loop

                # No tool uses, we're done
                break

            except Exception as e:
                logger.exception("Streaming error")
                yield format_sse(SSEEvent.ERROR, {"error": str(e)})
                break

        yield format_sse(SSEEvent.DONE, {})

    async def stream_chat(
        self,
        messages: list[dict],
        provider: str = "claude",
        model: str | None = None,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        enable_tools: bool = True,
        working_directory: str | None = None,
        db_session: Any = None,
    ) -> AsyncIterator[str]:
        """Stream chat completion from the specified provider.

        Args:
            messages: List of message dicts with 'role' and 'content'
            provider: AI provider ('claude', 'codex', 'gemini')
            model: Model ID (provider-specific)
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            enable_tools: Whether to enable tool use
            working_directory: Base directory for file operations
            db_session: Database session for TraceRTM operations

        Yields:
            SSE-formatted strings

        Raises:
            AIServiceError: If provider is not supported or API fails
        """
        if provider == "claude":
            model = model or "claude-sonnet-4-20250514"

            if enable_tools:
                async for chunk in self.stream_chat_with_tools_streaming(
                    messages=messages,
                    model=model,
                    system_prompt=system_prompt,
                    max_tokens=max_tokens,
                    working_directory=working_directory,
                    db_session=db_session,
                ):
                    yield chunk
            else:
                # Simple streaming without tools
                async with self.anthropic_client.messages.stream(
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt or "",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in messages
                        if m["role"] in {"user", "assistant"}
                    ],
                ) as stream:
                    async for text in stream.text_stream:
                        yield format_sse(SSEEvent.TEXT, {"content": text})

                yield format_sse(SSEEvent.DONE, {})

        elif provider == "codex":
            msg = "Codex provider not yet implemented"
            raise AIServiceError(msg)
        elif provider == "gemini":
            msg = "Gemini provider not yet implemented"
            raise AIServiceError(msg)
        else:
            msg = f"Unknown provider: {provider}"
            raise AIServiceError(msg)

    async def simple_chat(
        self,
        messages: list[dict],
        provider: str = "claude",
        model: str | None = None,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
    ) -> str:
        """Non-streaming chat completion (for testing/simple use cases)."""
        chunks = []
        async for chunk in self.stream_chat(
            messages=messages,
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            enable_tools=False,
        ):
            try:
                data = json.loads(chunk.replace("data: ", "").strip())
                if data.get("type") == SSEEvent.TEXT:
                    chunks.append(data["data"]["content"])
            except (json.JSONDecodeError, KeyError):
                continue

        return "".join(chunks)


# Global service instance
_ai_service: AIService | None = None


def get_ai_service() -> AIService:
    """Get or create the global AI service instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
