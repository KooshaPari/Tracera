"""Non-streaming chat handler for TraceRTM."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.api.handlers.chat_shared import (
    _chat_with_agent_sandbox,
    _chat_with_ai_service,
    _get_agent_service,
)
from tracertm.schemas.chat import ChatRequest


async def simple_chat(
    request: Request,
    request_body: ChatRequest,
    claims: dict[str, object] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
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
    except AIServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        from tracertm.api.handlers.chat_shared import logger

        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    else:
        return {
            "content": response,
            "model": request_body.model,
            "provider": request_body.provider.value,
        }
