"""Codex agent API endpoints for TraceRTM."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_db
from tracertm.schemas.execution import CodexAgentTaskListResponse, CodexAgentTaskResponse

router = APIRouter(prefix="/api/v1/projects/{project_id}/codex", tags=["codex"])


def ensure_project_access(project_id: str, claims: dict[str, object] | None) -> None:
    """Check if user has access to project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


@router.post("/review-image")
async def codex_review_image(
    project_id: str,
    body: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Have Codex review an image artifact."""
    ensure_project_access(project_id, claims)
    from tracertm.services.agents import CodexAgentService
    from tracertm.services.execution import ExecutionService

    execution_service = ExecutionService(db)
    codex_service = CodexAgentService(db, execution_service)

    artifact_id = body.get("artifact_id")
    prompt = body.get("prompt", "Review this image and provide feedback")
    execution_id = body.get("execution_id")

    if not artifact_id:
        raise HTTPException(status_code=400, detail="artifact_id required")

    interaction = await codex_service.review_image(artifact_id, prompt, project_id, execution_id=execution_id)
    await db.commit()

    return CodexAgentTaskResponse(
        id=interaction.id,
        execution_id=interaction.execution_id,
        project_id=interaction.project_id,
        artifact_id=interaction.artifact_id,
        task_type=interaction.task_type,
        input_data=interaction.input_data,
        output_data=interaction.output_data,
        prompt=interaction.prompt,
        response=interaction.response,
        status=interaction.status,
        started_at=interaction.started_at,
        completed_at=interaction.completed_at,
        duration_ms=interaction.duration_ms,
        tokens_used=interaction.tokens_used,
        model_used=interaction.model_used,
        error_message=interaction.error_message,
        retry_count=interaction.retry_count,
        created_at=interaction.created_at,
    )


@router.post("/review-video")
async def codex_review_video(
    project_id: str,
    body: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Have Codex review a video artifact."""
    ensure_project_access(project_id, claims)
    from tracertm.services.agents import CodexAgentService
    from tracertm.services.execution import ExecutionService

    execution_service = ExecutionService(db)
    codex_service = CodexAgentService(db, execution_service)

    artifact_id = body.get("artifact_id")
    prompt = body.get("prompt", "Review this video and provide feedback")
    execution_id = body.get("execution_id")
    max_frames = body.get("max_frames", 10)

    if not artifact_id:
        raise HTTPException(status_code=400, detail="artifact_id required")

    interaction = await codex_service.review_video(
        artifact_id,
        prompt,
        project_id,
        execution_id=execution_id,
        max_frames=max_frames,
    )
    await db.commit()

    return CodexAgentTaskResponse(
        id=interaction.id,
        execution_id=interaction.execution_id,
        project_id=interaction.project_id,
        artifact_id=interaction.artifact_id,
        task_type=interaction.task_type,
        input_data=interaction.input_data,
        output_data=interaction.output_data,
        prompt=interaction.prompt,
        response=interaction.response,
        status=interaction.status,
        started_at=interaction.started_at,
        completed_at=interaction.completed_at,
        duration_ms=interaction.duration_ms,
        tokens_used=interaction.tokens_used,
        model_used=interaction.model_used,
        error_message=interaction.error_message,
        retry_count=interaction.retry_count,
        created_at=interaction.created_at,
    )


@router.get("/interactions")
async def list_codex_interactions(
    project_id: str,
    limit: int = 20,
    offset: int = 0,
    status: str | None = None,
    task_type: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    """List Codex agent interactions for a project."""
    ensure_project_access(project_id, claims)
    from tracertm.models.codex_agent import CodexAgentInteraction

    q = select(CodexAgentInteraction).where(CodexAgentInteraction.project_id == project_id)
    if status:
        q = q.where(CodexAgentInteraction.status == status)
    if task_type:
        q = q.where(CodexAgentInteraction.task_type == task_type)
    q = q.order_by(CodexAgentInteraction.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(q)
    interactions = list(result.scalars().all())

    return CodexAgentTaskListResponse(
        tasks=[
            CodexAgentTaskResponse(
                id=i.id,
                execution_id=i.execution_id,
                project_id=i.project_id,
                artifact_id=i.artifact_id,
                task_type=i.task_type,
                input_data=i.input_data,
                output_data=i.output_data,
                prompt=i.prompt,
                response=i.response,
                status=i.status,
                started_at=i.started_at,
                completed_at=i.completed_at,
                duration_ms=i.duration_ms,
                tokens_used=i.tokens_used,
                model_used=i.model_used,
                error_message=i.error_message,
                retry_count=i.retry_count,
                created_at=i.created_at,
            )
            for i in interactions
        ],
        total=len(interactions),
    )


@router.get("/auth-status")
async def codex_auth_status(
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Check Codex CLI authentication status."""
    ensure_project_access(project_id, claims)
    from tracertm.services.agents import CodexAgentService
    from tracertm.services.execution import ExecutionService

    execution_service = ExecutionService(db)
    codex_service = CodexAgentService(db, execution_service)

    available, version = await codex_service.check_availability()
    authenticated, status = await codex_service.check_auth_status()

    return {
        "available": available,
        "version": version if available else None,
        "authenticated": authenticated,
        "status": status,
    }
