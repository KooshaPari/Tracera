"""Item management API endpoints for TraceRTM.

- Item listing (with filtering, pagination, view resolution)
- Item CRUD operations (Create, Read, Update, Delete)
- Bulk operations (bulk update)
- Item summaries (counts by status)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import func, select, update

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_cache_service, get_db
from tracertm.api.handlers.items import (
    ItemListParams,
    build_list_response,
    build_query_conditions,
    execute_item_query,
    resolve_view_matches,
    try_get_from_cache,
)
from tracertm.core.concurrency import ConcurrencyError
from tracertm.models.item import Item
from tracertm.repositories import item_repository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.services.cache_service import CacheService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/items", tags=["items"])


# ==================== HELPER FUNCTIONS ====================


def ensure_project_access(project_id: str, claims: dict[str, object] | None) -> None:
    """Check if user has access to project.

    Note: This function should be imported from main.py or moved to a shared module.
    For now, we import it from the parent scope.
    """
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


def ensure_write_permission(claims: dict[str, object] | None, action: str) -> None:
    """Check if user has write permission.

    Note: This function should be imported from main.py or moved to a shared module.
    For now, we import it from the parent scope.
    """
    from tracertm.api.security import ensure_write_permission as _ensure_write_permission

    _ensure_write_permission(claims, action=action)


async def _maybe_await(result: object) -> object:
    """Await result if it's awaitable, otherwise return as-is.

    Note: This function should be imported from main.py or moved to a shared module.
    For now, we import it from the parent scope.
    """
    from tracertm.api.security import _maybe_await as _maybe_await_impl

    return await _maybe_await_impl(result)


# ==================== PYDANTIC MODELS ====================


class ItemCreate(BaseModel):
    """Schema for creating a new item."""

    project_id: str
    title: str
    type: str
    description: str | None = None
    view: str | None = None
    status: str | None = "pending"
    priority: str | None = "medium"
    parent_id: str | None = None
    metadata: dict[str, object] | None = None


class ItemUpdate(BaseModel):
    """Schema for updating an existing item."""

    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    owner: str | None = None
    metadata: dict[str, object] | None = None
    expected_version: int | None = None


class ItemBulkUpdate(BaseModel):
    """Schema for bulk updating items."""

    project_id: str
    view: str | None = None
    status: str | None = None
    new_status: str
    preview: bool | None = None


# ==================== ENDPOINT IMPLEMENTATIONS ====================


def _serialize_item_for_response(item: object) -> dict[str, object]:
    """Build response dict for a single item; safe for None/missing attributes."""
    created_at = getattr(item, "created_at", None)
    updated_at = getattr(item, "updated_at", None)
    return {
        "id": str(getattr(item, "id", "")),
        "title": getattr(item, "title", ""),
        "description": getattr(item, "description", ""),
        "view": getattr(item, "view", ""),
        "type": getattr(item, "item_type", getattr(item, "view", "")),
        "status": getattr(item, "status", ""),
        "priority": getattr(item, "priority", "medium"),
        "project_id": str(getattr(item, "project_id", "") or ""),
        "created_at": created_at.isoformat() if created_at else None,
        "updated_at": updated_at.isoformat() if updated_at else None,
    }


async def _list_items_impl(
    project_id: str | None,
    view: str | None,
    status: str | None,
    parent_id: str | None,
    skip: int,
    limit: int,
    claims: dict[str, object],
    db: AsyncSession,
    cache: CacheService,
    request: Request | None,
) -> dict[str, object]:
    """Implementation of list items; errors are caught by list_items."""
    # Skip rate limiting for bulk operations (e.g., fetching counts)
    if not (request and request.headers.get("X-Bulk-Operation") == "true"):
        enforce_rate_limit(request, claims)
    if project_id:
        ensure_project_access(project_id, claims)

    # Try to get from cache (only for simple queries without view resolution)
    params = ItemListParams(
        project_id=project_id,
        view=view,
        status=status,
        parent_id=parent_id,
        skip=skip,
        limit=limit,
    )
    cache_key, cached = await try_get_from_cache(cache, params)
    if cached is not None:
        return cached

    # Resolve view name to actual view values
    matches = await resolve_view_matches(view, project_id, db)

    # Build query conditions
    conditions = build_query_conditions(params, matches)

    # Execute query
    total_count, items = await execute_item_query(db, conditions, params)

    # Build response
    result = build_list_response(items, total_count, project_id, limit)

    # Cache the result if we have a cache key
    if cache_key:
        await cache.set(cache_key, result, cache_type="items")

    return result


# ==================== ROUTER ENDPOINTS ====================


@router.get("")
async def list_items(
    request: Request,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
    project_id: str | None = None,
    view: str | None = None,
    status: str | None = None,
    parent_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> dict[str, object]:
    """List items in a project. Returns empty list on any backend error so callers (e.g. home loader) do not get 500.

    Functional Requirements:
    - FR-APP-005

    User Stories:
    - US-ITEM-005

    Epics:
    - EPIC-003
    """
    try:
        return await _list_items_impl(
            project_id=project_id,
            view=view,
            status=status,
            parent_id=parent_id,
            skip=skip,
            limit=limit,
            claims=claims,
            db=db,
            cache=cache,
            request=request,
        )
    except Exception as exc:
        logger.warning("list_items failed (returning empty): %s", exc, exc_info=True)
        return {"total": 0, "items": []}


@router.get("/{item_id}")
async def get_item(
    item_id: str,
    request: Request,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Get a specific item.

    Functional Requirements:
    - FR-APP-002

    User Stories:
    - US-ITEM-002

    Epics:
    - EPIC-003
    """
    try:
        enforce_rate_limit(request, claims)

        repo = item_repository.ItemRepository(db)
        item = await _maybe_await(repo.get_by_id(item_id))

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        return _serialize_item_for_response(item)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("GET /api/v1/items/%s failed", item_id)
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        ) from e


@router.post("")
async def create_item_endpoint(
    request: Request,
    payload: ItemCreate,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
) -> dict[str, object]:
    """Create an item with simple permission checks.

    Functional Requirements:
    - FR-APP-001

    User Stories:
    - US-ITEM-001

    Epics:
    - EPIC-003
    """
    ensure_write_permission(claims, action="create")
    # Skip rate limiting for bulk operations
    if not (request and request.headers.get("X-Bulk-Operation") == "true"):
        enforce_rate_limit(request, claims)
    ensure_project_access(payload.project_id, claims)

    try:
        repo = item_repository.ItemRepository(db)
        # Determine view from type if not provided
        view = payload.view or (payload.type.upper() if payload.type else "")
        item = await repo.create(
            project_id=payload.project_id,
            title=payload.title,
            view=view.upper(),
            item_type=payload.type,
            description=payload.description,
            status=payload.status or "pending",
            parent_id=payload.parent_id,
            metadata=payload.metadata,
            priority=payload.priority or "medium",
        )
        await db.commit()

        # Invalidate caches for this project
        await cache.invalidate_project(payload.project_id)

        return {
            "id": str(item.id),
            "title": item.title,
            "view": item.view,
            "status": item.status,
            "type": item.item_type,
            "description": item.description,
            "priority": item.priority,
        }
    except Exception as exc:
        await db.rollback()
        logger.exception("Error creating item")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{item_id}")
async def update_item_endpoint(
    request: Request,
    item_id: str,
    payload: ItemUpdate,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
) -> dict[str, object]:
    """Update an item with optimistic locking (if expected_version provided).

    Functional Requirements:
    - FR-APP-003

    User Stories:
    - US-ITEM-003

    Epics:
    - EPIC-003
    """
    ensure_write_permission(claims, action="update")
    enforce_rate_limit(request, claims)

    repo = item_repository.ItemRepository(db)
    existing = await _maybe_await(repo.get_by_id(item_id))
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")

    ensure_project_access(str(getattr(existing, "project_id", "")), claims)

    update_fields = {
        key: value for key, value in payload.model_dump().items() if key != "expected_version" and value is not None
    }
    expected_version = payload.expected_version
    if expected_version is None:
        expected_version = getattr(existing, "version", 0)

    try:
        updated = await repo.update(item_id, expected_version, **update_fields)
        await db.commit()
        await cache.invalidate_project(str(getattr(updated, "project_id", "")))
        return {
            "id": str(updated.id),
            "title": updated.title,
            "description": updated.description,
            "view": updated.view,
            "type": getattr(updated, "item_type", updated.view),
            "status": updated.status,
            "priority": updated.priority,
            "owner": getattr(updated, "owner", None),
            "project_id": str(getattr(updated, "project_id", "")),
            "version": getattr(updated, "version", None),
            "updated_at": updated.updated_at.isoformat() if getattr(updated, "updated_at", None) else None,
        }
    except ConcurrencyError as exc:
        await db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        await db.rollback()
        logger.exception("Error updating item")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{item_id}")
async def delete_item_endpoint(
    request: Request,
    item_id: str,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Delete an item (permission-gated).

    Functional Requirements:
    - FR-APP-004

    User Stories:
    - US-ITEM-004

    Epics:
    - EPIC-003
    """
    ensure_write_permission(claims, action="delete")
    enforce_rate_limit(request, claims)
    repo = item_repository.ItemRepository(db)
    existing = await _maybe_await(repo.get_by_id(item_id))
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    ensure_project_access(str(getattr(existing, "project_id", "")), claims)
    deleted = await repo.delete(item_id, soft=True)
    await db.commit()
    return {"status": "deleted" if deleted else "not_found", "id": item_id}


@router.post("/bulk-update")
async def bulk_update_items_endpoint(
    request: Request,
    payload: ItemBulkUpdate,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
) -> dict[str, object]:
    """Bulk update item status with optional preview."""
    ensure_write_permission(claims, action="bulk_update")
    enforce_rate_limit(request, claims)
    ensure_project_access(payload.project_id, claims)

    conditions = [Item.project_id == payload.project_id, Item.deleted_at.is_(None)]
    if payload.view:
        conditions.append(Item.view == payload.view.upper())
    if payload.status:
        conditions.append(Item.status == payload.status)

    count_query = select(func.count(Item.id)).where(*conditions)
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    if payload.preview:
        return {
            "project_id": payload.project_id,
            "matched": total,
            "updated": 0,
            "preview": True,
        }

    update_query = update(Item).where(*conditions).values(status=payload.new_status, updated_at=func.now())
    await db.execute(update_query)
    await db.commit()
    await cache.invalidate_project(payload.project_id)

    return {
        "project_id": payload.project_id,
        "matched": total,
        "updated": total,
        "new_status": payload.new_status,
        "preview": False,
    }
