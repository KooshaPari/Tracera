"""Chat and AI generation handlers for reducing main.py complexity."""

import json
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.schemas.chat import ChatRequest
from tracertm.services.agent_service import AgentService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SandboxStreamContext:
    """Bundled parameters for sandbox streaming."""

    agent_service: AgentService
    messages: list[dict[str, str]]
    session_id: str | None
    options: Any
    db_session: AsyncSession
    sandbox_config: Any | None


def _get_agent_service(request: Request | None = None) -> AgentService:
    """Get agent service from app state or global singleton.

    Args:
        request: Optional request object to access app state

    Returns:
        Agent service instance
    """
    from tracertm.agent import get_agent_service

    if request and hasattr(request.app.state, "agent_service"):
        return request.app.state.agent_service
    return get_agent_service()


def _build_sandbox_config(request_body: ChatRequest) -> dict[str, Any] | None:
    """Build sandbox configuration from chat request.

    Args:
        request_body: Chat request containing optional project context

    Returns:
        SandboxConfig if project_id is present, None otherwise
    """
    from tracertm.agent.types import SandboxConfig

    if request_body.context and request_body.context.project_id:
        return SandboxConfig(project_id=request_body.context.project_id)
    return None


def _build_stream_chat_options(request_body: ChatRequest) -> dict[str, Any]:
    """Build StreamChatOptions from request body.

    Args:
        request_body: Chat request with model/provider settings

    Returns:
        StreamChatOptions instance
    """
    from tracertm.agent.agent_service import StreamChatOptions

    return StreamChatOptions(
        provider=request_body.provider.value,
        model=request_body.model,
        system_prompt=request_body.system_prompt,
        max_tokens=request_body.max_tokens,
        enable_tools=True,
    )


def _get_working_directory(request_body: ChatRequest) -> str | None:
    """Get working directory from request context.

    Args:
        request_body: Chat request with optional project context

    Returns:
        Working directory path as string, or None
    """
    if request_body.context and request_body.context.project_id:
        return str(Path.cwd())
    return None


async def _stream_with_agent_sandbox(
    ctx: SandboxStreamContext,
) -> AsyncGenerator[str, None]:
    """Stream chat using agent sandbox.

    Args:
        ctx: Sandbox stream context

    Yields:
        SSE chunks
    """
    async for chunk in ctx.agent_service.stream_chat_with_sandbox(
        messages=ctx.messages,
        session_id=ctx.session_id,
        options=ctx.options,
        db_session=ctx.db_session,
        sandbox_config=ctx.sandbox_config,
    ):
        yield chunk


async def _stream_with_ai_service(
    messages: list[dict[str, str]],
    request_body: ChatRequest,
    db_session: AsyncSession,
    working_directory: str | None,
) -> AsyncGenerator[str, None]:
    """Stream chat using AI service without sandbox.

    Args:
        messages: Chat messages
        request_body: Original request body
        db_session: Database session
        working_directory: Optional working directory

    Yields:
        SSE chunks
    """
    from tracertm.services.ai_service import get_ai_service
    from tracertm.services.ai_tools import set_allowed_paths

    ai_service = get_ai_service()

    if working_directory:
        set_allowed_paths([working_directory])

    async for chunk in ai_service.stream_chat(
        messages=messages,
        provider=request_body.provider.value,
        model=request_body.model,
        system_prompt=request_body.system_prompt,
        max_tokens=request_body.max_tokens,
        enable_tools=True,
        working_directory=working_directory,
        db_session=db_session,
    ):
        yield chunk


def _format_error_sse(error_message: str) -> str:
    """Format error as SSE data chunk.

    Args:
        error_message: Error message to format

    Returns:
        SSE-formatted error string
    """
    error_data = json.dumps({"type": "error", "data": {"error": error_message}})
    return f"data: {error_data}\n\n"


async def _generate_sse_stream(
    messages: list[dict[str, str]],
    request_body: ChatRequest,
    db_session: AsyncSession,
    use_agent_sandbox: bool,
    request: Request | None = None,
) -> AsyncGenerator[str, None]:
    """Generate SSE stream with tool use support.

    Args:
        messages: Chat messages
        request_body: Chat request body
        db_session: Database session
        use_agent_sandbox: Whether to use agent sandbox
        request: Optional request object for app state

    Yields:
        SSE chunks
    """
    from tracertm.services.ai_service import AIServiceError

    try:
        if use_agent_sandbox:
            sandbox_config = _build_sandbox_config(request_body)
            agent_service = _get_agent_service(request)
            options = _build_stream_chat_options(request_body)

            async for chunk in _stream_with_agent_sandbox(
                SandboxStreamContext(
                    agent_service=agent_service,
                    messages=messages,
                    session_id=request_body.session_id,
                    options=options,
                    db_session=db_session,
                    sandbox_config=sandbox_config,
                ),
            ):
                yield chunk
        else:
            working_directory = _get_working_directory(request_body)
            async for chunk in _stream_with_ai_service(
                messages=messages,
                request_body=request_body,
                db_session=db_session,
                working_directory=working_directory,
            ):
                yield chunk

    except AIServiceError as e:
        yield _format_error_sse(str(e))
    except Exception as e:
        logger.exception("Chat streaming error: %s", e)
        yield _format_error_sse("An unexpected error occurred")


async def stream_chat(
    request: Request,
    request_body: ChatRequest,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Stream AI chat completion using Server-Sent Events.

    This endpoint streams responses from AI providers (Claude, Codex, Gemini)
    using SSE format for real-time message delivery. Supports tool use for
    filesystem operations, CLI commands, and TraceRTM API operations.
    When session_id is provided, tools run in a per-session sandbox (persisted with chat).

    Args:
        request: FastAPI request object
        request_body: Chat request with messages and settings
        claims: Auth claims from JWT token
        db: Database session

    Returns:
        StreamingResponse with SSE data
    """
    enforce_rate_limit(request, claims)

    messages = [{"role": msg.role.value, "content": msg.content} for msg in request_body.messages]
    use_agent_sandbox = bool(request_body.session_id and request_body.session_id.strip())

    return StreamingResponse(
        _generate_sse_stream(
            messages=messages,
            request_body=request_body,
            db_session=db,
            use_agent_sandbox=use_agent_sandbox,
            request=request,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


async def _chat_with_agent_sandbox(
    agent_service: AgentService,
    messages: list[dict[str, str]],
    session_id: str | None,
    db_session: AsyncSession,
    request_body: ChatRequest,
) -> str:
    """Execute chat using agent sandbox.

    Args:
        agent_service: Agent service instance
        messages: Chat messages
        session_id: Session ID for sandbox
        db_session: Database session
        request_body: Original chat request

    Returns:
        Response content string
    """
    from tracertm.agent.agent_service import StreamChatOptions

    sandbox_config = _build_sandbox_config(request_body)
    options = StreamChatOptions(
        provider=request_body.provider.value,
        model=request_body.model,
        system_prompt=request_body.system_prompt,
        max_tokens=request_body.max_tokens,
    )

    return await agent_service.simple_chat_with_sandbox(
        messages=messages,
        session_id=session_id,
        options=options,
        db_session=db_session,
        sandbox_config=sandbox_config,
    )


async def _chat_with_ai_service(
    messages: list[dict[str, str]],
    request_body: ChatRequest,
) -> str:
    """Execute chat using AI service without sandbox.

    Args:
        messages: Chat messages
        request_body: Chat request with model/provider settings

    Returns:
        Response content string
    """
    from tracertm.services.ai_service import get_ai_service

    ai_service = get_ai_service()
    return await ai_service.simple_chat(
        messages=messages,
        provider=request_body.provider.value,
        model=request_body.model,
        system_prompt=request_body.system_prompt,
        max_tokens=request_body.max_tokens,
    )


async def simple_chat(
    request: Request,
    request_body: ChatRequest,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Non-streaming chat completion (for testing/simple use cases).

    Args:
        request: FastAPI request object
        request_body: Chat request with messages and settings
        claims: Auth claims from JWT token
        db: Database session

    Returns:
        Dict with content, model, and provider

    Raises:
        HTTPException: On AI service errors
    """
    from tracertm.services.ai_service import AIServiceError

    enforce_rate_limit(request, claims)

    messages = [{"role": msg.role.value, "content": msg.content} for msg in request_body.messages]
    use_agent_sandbox = bool(request_body.session_id and request_body.session_id.strip())

    try:
        if use_agent_sandbox:
            agent_service = _get_agent_service(request)
            response = await _chat_with_agent_sandbox(
                agent_service=agent_service,
                messages=messages,
                session_id=request_body.session_id,
                db_session=db,
                request_body=request_body,
            )
        else:
            response = await _chat_with_ai_service(
                messages=messages,
                request_body=request_body,
            )

        return {
            "content": response,
            "model": request_body.model,
            "provider": request_body.provider.value,
        }

    except AIServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Chat error: %s", e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
