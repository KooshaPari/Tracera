"""FastAPI routes for agent sessions and workflow."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_db, auth_guard
from tracertm.schemas.agent import (
    AgentRunRequest,
    AgentRunResponse,
    AgentSessionCreate,
    AgentSessionListResponse,
    AgentSessionResponse,
)
from tracertm.models.agent_session import AgentSession

router = APIRouter(prefix="/agent", tags=["Agent"])


def _agent_service(request: Request):
    """Use app-scoped agent service when available."""
    if hasattr(request.app.state, "agent_service"):
        return request.app.state.agent_service
    from tracertm.agent import get_agent_service
    return get_agent_service()


# ---------------------------------------------------------------------------
# Session lifecycle
# ---------------------------------------------------------------------------


@router.post("/sessions", response_model=AgentSessionResponse, status_code=201)
async def create_agent_session(
    body: AgentSessionCreate,
    claims: dict = Depends(auth_guard),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Create an agent session (sandbox). Returns session_id and sandbox_root for use in chat."""
    from datetime import datetime
    session_id = (body.session_id and body.session_id.strip()) or str(uuid.uuid4())
    agent_svc = _agent_service(request)
    from tracertm.agent.types import SandboxConfig
    config = SandboxConfig(project_id=body.project_id)
    path, _ = await agent_svc.get_or_create_session_sandbox(session_id, config=config, db_session=db)
    await db.commit()
    result = await db.execute(select(AgentSession).where(AgentSession.session_id == session_id))
    row = result.scalar_one_or_none()
    if not row:
        return AgentSessionResponse(
            session_id=session_id,
            sandbox_root=path,
            project_id=uuid.UUID(body.project_id) if body.project_id else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    return AgentSessionResponse.model_validate(row)


@router.get("/sessions/{session_id}", response_model=AgentSessionResponse)
async def get_agent_session(
    session_id: str,
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """Get agent session metadata by session_id."""
    result = await db.execute(select(AgentSession).where(AgentSession.session_id == session_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Agent session not found")
    return AgentSessionResponse.model_validate(row)


@router.get("/sessions", response_model=AgentSessionListResponse)
async def list_agent_sessions(
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List agent sessions, optionally filtered by project_id."""
    q = select(AgentSession).order_by(AgentSession.created_at.desc())
    count_q = select(func.count()).select_from(AgentSession)
    if project_id:
        try:
            pid = uuid.UUID(project_id)
            q = q.where(AgentSession.project_id == pid)
            count_q = count_q.where(AgentSession.project_id == pid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid project_id")
    total = (await db.execute(count_q)).scalar() or 0
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    rows = result.scalars().all()
    return AgentSessionListResponse(
        sessions=[AgentSessionResponse.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_agent_session(
    session_id: str,
    claims: dict = Depends(auth_guard),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Delete an agent session from DB and cache; sandbox directory may remain on disk unless cleanup is enabled."""
    result = await db.execute(select(AgentSession).where(AgentSession.session_id == session_id))
    row = result.scalar_one_or_none()
    if row:
        await db.delete(row)
        await db.commit()
    if request and hasattr(request.app.state, "agent_service"):
        store = request.app.state.agent_service._store
        if hasattr(store, "_cache") and store._cache is not None:
            from tracertm.agent.session_store import _agent_session_cache_key
            try:
                await store._cache.delete(_agent_session_cache_key(session_id))
            except Exception:
                pass
        if hasattr(store, "_store"):
            store._store.pop(session_id, None)
    return None


# ---------------------------------------------------------------------------
# Temporal workflow
# ---------------------------------------------------------------------------


@router.post("/run", response_model=AgentRunResponse)
async def start_agent_run(
    body: AgentRunRequest,
    claims: dict = Depends(auth_guard),
):
    """Start a checkpointed agent run workflow in Temporal. Use for long or resumable runs."""
    from tracertm.services.temporal_service import TemporalService
    service = TemporalService()
    workflow_id = f"agent-run-{body.session_id[:8]}-{uuid.uuid4().hex[:12]}"
    result = await service.start_workflow(
        workflow_name="AgentRunWorkflow",
        workflow_id=workflow_id,
        session_id=body.session_id,
        initial_messages_json=body.initial_messages_json,
        max_turns=body.max_turns,
    )
    return AgentRunResponse(
        workflow_id=workflow_id,
        run_id=result.get("run_id", ""),
        session_id=body.session_id,
        status="started",
    )
