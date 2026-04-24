"""Streaming chat handler for TraceRTM."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.api.handlers.chat_shared import (
    SandboxStreamContext,
    _build_sandbox_config,
    _build_stream_chat_options,
    _format_error_sse,
    _get_agent_service,
    _get_working_directory,
    _stream_with_agent_sandbox,
    _stream_with_ai_service,
)
from tracertm.schemas.chat import ChatRequest


async def _generate_sse_stream(
    messages: list[dict[str, str]],
    request_body: ChatRequest,
    db_session: AsyncSession,
    use_agent_sandbox: bool,
    request: Request | None = None,
) -> AsyncGenerator[str, None]:
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
    except Exception:
        from tracertm.api.handlers.chat_shared import logger

        logger.exception("Chat streaming error")
        yield _format_error_sse("An unexpected error occurred")


async def stream_chat(
    request: Request,
    request_body: ChatRequest,
    claims: dict[str, object] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
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
            "X-Accel-Buffering": "no",
        },
    )
