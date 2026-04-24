"""Link management API endpoints for TraceRTM."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_cache_service, get_db
from tracertm.api.handlers.links import (
    LinkQueryParams,
    build_links_response,
    detect_link_columns,
    execute_links_query,
    parse_exclude_types,
    try_get_links_from_cache,
)
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.repositories import link_repository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from tracertm.services.cache_service import CacheService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/links", tags=["links"])


def ensure_project_access(project_id: str | None, claims: dict[str, object] | None) -> None:
    """Check if user has access to project."""
    from tracertm.api.security import ensure_project_access as _ensure_project_access

    _ensure_project_access(project_id, claims)


def ensure_write_permission(claims: dict[str, object] | None, action: str) -> None:
    """Check if user has write permission."""
    from tracertm.api.security import ensure_write_permission as _ensure_write_permission

    _ensure_write_permission(claims, action=action)


async def _maybe_await(result: object) -> object:
    """Await result if it's awaitable, otherwise return as-is."""
    from tracertm.api.security import _maybe_await as _maybe_await_impl

    return await _maybe_await_impl(result)


class LinkCreate(BaseModel):
    """Request payload for creating a link."""

    project_id: str
    source_id: str
    target_id: str
    type: str
    metadata: dict[str, Any] | None = None


class LinkUpdate(BaseModel):
    """Request payload for updating a link."""

    link_type: str | None = None
    metadata: dict[str, Any] | None = None


@router.get("")
async def list_links(
    request: Request,
    project_id: str | None = None,
    source_id: str | None = None,
    target_id: str | None = None,
    skip: int = 0,
    limit: int = 100,
    exclude_types: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> dict[str, Any]:
    """List links with filtering, cache lookup, and schema-aware queries."""
    try:
        if not (request and request.headers.get("X-Bulk-Operation") == "true"):
            enforce_rate_limit(request, claims)

        if project_id:
            ensure_project_access(project_id, claims)

        exclude_types_list = parse_exclude_types(exclude_types)
        params = LinkQueryParams(
            project_id=project_id,
            source_id=source_id,
            target_id=target_id,
            exclude_types=exclude_types_list,
            skip=skip,
            limit=limit,
        )
        cache_key, cached = await try_get_links_from_cache(cache, params)
        if cached is not None:
            return cached

        columns = await detect_link_columns(db)
        total_count, links_result = await execute_links_query(db, params, columns)
        result = build_links_response(links_result, total_count, project_id)

        if cache_key:
            await cache.set(cache_key, result, cache_type="links")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(
            "GET /api/v1/links failed project_id=%s exclude_types=%s",
            project_id,
            exclude_types,
        )
        raise HTTPException(status_code=500, detail="Internal server error") from exc
    else:
        return result


@router.get("/grouped")
async def list_links_grouped(
    request: Request,
    project_id: str,
    item_id: str,
    view: str | None = None,
    claims: dict[str, Any] = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Show links for an item grouped as incoming/outgoing."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    resolved = await db.execute(
        select(Item.id)
        .where(
            Item.project_id == project_id,
            Item.deleted_at.is_(None),
            (Item.id == item_id) | Item.external_id.ilike(f"{item_id}%"),
        )
        .limit(1),
    )
    resolved_id = resolved.scalar_one_or_none()
    if not resolved_id:
        raise HTTPException(status_code=404, detail="Item not found")

    item_row = (await db.execute(select(Item).where(Item.id == resolved_id))).scalar_one_or_none()
    view_upper = view.upper() if view else None

    outgoing = (
        (
            await db.execute(
                select(Link)
                .join(Item, Link.target_item_id == Item.id)
                .where(
                    Link.project_id == project_id,
                    Link.source_item_id == resolved_id,
                    Item.deleted_at.is_(None),
                    *([Item.view == view_upper] if view_upper else []),
                ),
            )
        )
        .scalars()
        .all()
    )

    incoming = (
        (
            await db.execute(
                select(Link)
                .join(Item, Link.source_item_id == Item.id)
                .where(
                    Link.project_id == project_id,
                    Link.target_item_id == resolved_id,
                    Item.deleted_at.is_(None),
                    *([Item.view == view_upper] if view_upper else []),
                ),
            )
        )
        .scalars()
        .all()
    )

    async def _item_brief(item_id_value: str) -> dict[str, Any]:
        row = await db.execute(select(Item).where(Item.id == item_id_value))
        found = row.scalar_one_or_none()
        return {
            "id": str(found.id) if found else item_id_value,
            "external_id": getattr(found, "external_id", None) if found else None,
            "title": getattr(found, "title", None) if found else None,
            "view": getattr(found, "view", None) if found else None,
            "status": getattr(found, "status", None) if found else None,
        }

    return {
        "item": {
            "id": str(item_row.id) if item_row else resolved_id,
            "external_id": getattr(item_row, "external_id", None) if item_row else None,
            "title": getattr(item_row, "title", None) if item_row else None,
            "view": getattr(item_row, "view", None) if item_row else None,
        },
        "outgoing": [
            {
                "link_id": str(link.id),
                "link_type": link.link_type,
                "direction": "outgoing",
                "item": await _item_brief(link.target_item_id),
            }
            for link in outgoing
        ],
        "incoming": [
            {
                "link_id": str(link.id),
                "link_type": link.link_type,
                "direction": "incoming",
                "item": await _item_brief(link.source_item_id),
            }
            for link in incoming
        ],
    }


@router.post("")
async def create_link(
    request: Request,
    payload: LinkCreate,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
) -> dict[str, Any]:
    """Create a new link."""
    ensure_write_permission(claims, action="create")
    if not (request and request.headers.get("X-Bulk-Operation") == "true"):
        enforce_rate_limit(request, claims)
    ensure_project_access(payload.project_id, claims)

    repo = link_repository.LinkRepository(db)
    link = await repo.create(
        project_id=payload.project_id,
        source_item_id=payload.source_id,
        target_item_id=payload.target_id,
        link_type=payload.type,
        link_metadata=payload.metadata,
    )

    await cache.invalidate_project(payload.project_id)
    return {
        "id": str(link.id),
        "source_id": str(link.source_item_id),
        "target_id": str(link.target_item_id),
        "type": link.link_type,
        "metadata": link.link_metadata if hasattr(link, "link_metadata") else {},
    }


@router.put("/{link_id}")
async def update_link(
    request: Request,
    link_id: str,
    request_body: LinkUpdate,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Update link fields."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, action="update")

    repo = link_repository.LinkRepository(db)
    link_obj = await _maybe_await(repo.get_by_id(link_id))
    if not link_obj:
        raise HTTPException(status_code=404, detail="Link not found")
    link = cast("Link", link_obj)

    if request_body.link_type:
        link.link_type = request_body.link_type
    if request_body.metadata is not None:
        setattr(link, "metadata", request_body.metadata)

    flush = getattr(db, "flush", None)
    if callable(flush):
        await _maybe_await(flush())
    refresh = getattr(db, "refresh", None)
    if callable(refresh):
        await _maybe_await(refresh(link))

    return {
        "id": str(getattr(link, "id", link_id)),
        "source_id": getattr(link, "source_item_id", None),
        "target_id": getattr(link, "target_item_id", None),
        "type": getattr(link, "link_type", request_body.link_type),
        "metadata": getattr(link, "metadata", request_body.metadata),
    }


@router.delete("/{link_id}")
async def delete_link(
    request: Request,
    link_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Delete link."""
    enforce_rate_limit(request, claims)
    ensure_write_permission(claims, action="delete")
    repo = link_repository.LinkRepository(db)
    link = await _maybe_await(repo.get_by_id(link_id))
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    ensure_project_access(str(getattr(link, "project_id", "")), claims)
    deleted = await repo.delete(link_id)
    await db.commit()
    return {"deleted": bool(deleted), "id": link_id}
