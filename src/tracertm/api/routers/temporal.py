"""Temporal summary router for TraceRTM."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from tracertm.api.deps import auth_guard
from tracertm.services.temporal_service import TemporalService

router = APIRouter(prefix="/api/v1", tags=["temporal"])


@router.get("/temporal/summary")
async def get_temporal_summary(
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    workflow_limit: int = 100,
    schedule_limit: int = 200,
):
    """Get Temporal health and summary metrics for dashboards."""
    from tracertm.api.security import check_permissions

    check_permissions(claims=claims, action="temporal_summary")
    service = TemporalService()
    try:
        return await service.get_summary(
            workflow_limit=workflow_limit,
            schedule_limit=schedule_limit,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
