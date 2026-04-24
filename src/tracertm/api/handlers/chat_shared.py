"""Shared helpers for chat and AI generation handlers."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.agent.agent_service import AgentService
from tracertm.schemas.chat import ChatRequest

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SandboxStreamContext:
    """Bundled parameters for sandbox streaming."""

    agent_service: AgentService
    messages: list[dict[str, str]]
    session_id: str | None
    options: object
    db_session: AsyncSession
    sandbox_config: object | None


def _get_agent_service(request: Request | None = None) -> AgentService:
    from tracertm.agent import get_agent_service

    if request and hasattr(request.app.state, "agent_service"):
        return request.app.state.agent_service
    return get_agent_service()


def _build_sandbox_config(request_body: ChatRequest) -> dict[str, Any] | None:
    from tracertm.agent.types import SandboxConfig

    if request_body.context and request_body.context.project_id:
        return SandboxConfig(project_id=request_body.context.project_id)
    return None


def _build_stream_chat_options(request_body: ChatRequest) -> dict[str, Any]:
    from tracertm.agent.agent_service import StreamChatOptions

    return StreamChatOptions(
        provider=request_body.provider.value,
        model=request_body.model,
        system_prompt=request_body.system_prompt,
        max_tokens=request_body.max_tokens,
        enable_tools=True,
    )


def _get_working_directory(request_body: ChatRequest) -> str | None:
    if request_body.context and request_body.context.project_id:
        return str(Path.cwd())
    return None


async def _stream_with_agent_sandbox(
    ctx: SandboxStreamContext,
) -> AsyncGenerator[str, None]:
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
    error_data = json.dumps({"type": "error", "data": {"error": error_message}})
    return f"data: {error_data}\n\n"


async def _chat_with_agent_sandbox(
    agent_service: AgentService,
    messages: list[dict[str, str]],
    session_id: str | None,
    db_session: AsyncSession,
    request_body: ChatRequest,
) -> str:
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
    from tracertm.services.ai_service import get_ai_service

    ai_service = get_ai_service()
    return await ai_service.simple_chat(
        messages=messages,
        provider=request_body.provider.value,
        model=request_body.model,
        system_prompt=request_body.system_prompt,
        max_tokens=request_body.max_tokens,
    )
