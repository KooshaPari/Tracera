"""Project sync and search utility API endpoints for TraceRTM."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_db

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


def ensure_project_access(project_id: str, claims: dict[str, Any] | None) -> None:
    """Check if user has access to project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


def ensure_write_permission(claims: dict[str, Any] | None, action: str) -> None:
    """Check if user has write permission."""
    from tracertm.api.security import ensure_write_permission as _ensure_write_permission

    _ensure_write_permission(claims, action=action)


class AdvancedSearchRequest(BaseModel):
    """Request model for advanced search endpoint."""

    query: str | None = None
    filters: dict[str, Any] | None = None


@router.get("/{project_id}/sync/status")
async def get_sync_status(
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get sync status for a project."""
    ensure_project_access(project_id, claims)
    from tracertm.services.sync_service import SyncService

    SyncService(db)
    # In a real implementation, this would check actual sync status
    # For now, return a mock status
    return {
        "project_id": project_id,
        "status": "synced",
        "last_synced": None,
        "pending_changes": 0,
    }


@router.post("/{project_id}/sync")
async def sync_project(
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Execute sync for a project."""
    ensure_project_access(project_id, claims)
    ensure_write_permission(claims, action="sync_project")
    from tracertm.services.sync_service import SyncService

    service = SyncService(db)
    result = await service.sync()

    return {
        "project_id": project_id,
        "status": "synced",
        "result": result,
    }


@router.post("/{project_id}/search/advanced")
async def advanced_search(
    project_id: str,
    request: AdvancedSearchRequest,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Advanced search with filters and query."""
    ensure_project_access(project_id, claims)
    from tracertm.services.search_service import SearchService

    service = SearchService(db)
    results = await service.search(_query=request.query, _filters=request.filters or {})

    return {
        "project_id": project_id,
        "query": request.query,
        "filters": request.filters,
        "results": results,
        "total": len(results),
    }
