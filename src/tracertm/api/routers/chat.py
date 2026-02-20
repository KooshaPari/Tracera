"""Chat and AI API endpoints for TraceRTM.

Implements:
- Streaming chat completion with SSE
- Non-streaming chat completion
- AI provider support (Claude, Codex, Gemini)
- Tool use for filesystem operations and CLI commands
- Session-based sandboxing
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Request

from tracertm.api.deps import auth_guard, get_db
from tracertm.api.handlers.chat import simple_chat, stream_chat

if TYPE_CHECKING:
    from fastapi.responses import StreamingResponse
    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.schemas.chat import ChatRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat", "ai"])


# ==================== STREAMING CHAT ====================


@router.post("/stream")
async def stream_chat_endpoint(
    request: Request,
    request_body: ChatRequest,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StreamingResponse:
    """Stream AI chat completion using Server-Sent Events.

    This endpoint streams responses from AI providers (Claude, Codex, Gemini)
    using SSE format for real-time message delivery. Supports tool use for
    filesystem operations, CLI commands, and TraceRTM API operations.
    When session_id is provided, tools run in a per-session sandbox (persisted with chat).

    Request Body:
        messages: List of chat messages with role and content
        provider: AI provider (claude, codex, gemini)
        model: Model identifier (e.g., claude-3-5-sonnet-20241022)
        system_prompt: Optional system prompt
        max_tokens: Maximum tokens in response
        session_id: Optional session ID for sandbox persistence
        context: Optional project context

    Response:
        Server-Sent Events stream with:
        - type: "content" | "tool_use" | "error"
        - data: Response content or tool information

    Rate Limits:
        - 20 requests per minute per user
        - Based on JWT claims

    Example:
        ```python
        import httpx

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "/api/v1/chat/stream",
                json={
                    "messages": [{"role": "user", "content": "Hello"}],
                    "provider": "claude",
                    "model": "claude-3-5-sonnet-20241022",
                },
                headers={"Authorization": f"Bearer {token}"},
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        print(data)
        ```
    """
    return await stream_chat(request, request_body, claims, db)


# ==================== NON-STREAMING CHAT ====================


@router.post("")
async def simple_chat_endpoint(
    request: Request,
    request_body: ChatRequest,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Non-streaming chat completion (for testing/simple use cases).

    This endpoint provides a simple request-response chat interface
    without streaming. Useful for testing, simple integrations, or
    when streaming is not required.

    Request Body:
        messages: List of chat messages with role and content
        provider: AI provider (claude, codex, gemini)
        model: Model identifier
        system_prompt: Optional system prompt
        max_tokens: Maximum tokens in response
        session_id: Optional session ID for sandbox persistence
        context: Optional project context

    Response:
        ```json
        {
            "content": "AI response text",
            "model": "claude-3-5-sonnet-20241022",
            "provider": "claude"
        }
        ```

    Rate Limits:
        - 20 requests per minute per user
        - Based on JWT claims

    Errors:
        - 500: AI service error or unexpected error
        - 429: Rate limit exceeded
        - 401: Invalid or missing authentication

    Example:
        ```python
        import httpx

        response = httpx.post(
            "/api/v1/chat",
            json={
                "messages": [{"role": "user", "content": "Hello"}],
                "provider": "claude",
                "model": "claude-3-5-sonnet-20241022",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        print(response.json()["content"])
        ```
    """
    return await simple_chat(request, request_body, claims, db)
