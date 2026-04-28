"""Item listing handlers and helpers for reducing complexity.

Functional Requirements: FR-APP-001
"""

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tracertm.models.item import Item

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.item import Item
from tracertm.services.cache_service import CacheService

# View alias mapping for resolving different view names
VIEW_ALIAS_MAP = {
    "feature": ["features", "requirements", "user-requirements", "user_stories", "user-stories"],
    "requirements": ["requirements", "user-requirements", "user_requirements"],
    "user-requirements": ["user-requirements", "user_requirements", "requirements"],
    "technical": ["technical-requirements", "technical_requirements"],
    "technical-requirements": ["technical-requirements", "technical_requirements"],
    "ui": ["ui-components", "ui_components", "wireframe", "wireframes", "ui"],
    "ui-components": ["ui-components", "ui_components", "wireframe", "wireframes"],
    "api": ["api_endpoints", "api-endpoints", "api"],
    "database": ["database", "data-model", "data_model"],
    "data-model": ["data-model", "data_model", "database"],
    "journey": ["journey"],
    "test": ["tests", "qa", "test"],
    "qa": ["qa", "tests", "test"],
    "infra": ["infra", "infrastructure"],
    "performance": ["performance"],
    "security": ["security"],
}


@dataclass(frozen=True)
class ItemListParams:
    """Parameters for item list queries."""

    project_id: str | None
    view: str | None
    status: str | None
    parent_id: str | None
    skip: int
    limit: int


def normalize_view_name(name: str) -> str:
    """Normalize view name by removing non-alphanumeric characters and lowercasing."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def view_matches(requested: str, candidate: str) -> bool:
    """Check if a view name matches the requested view name.

    Handles plural forms and prefix matching.
    """
    if not requested or not candidate:
        return False

    req = normalize_view_name(requested)
    cand = normalize_view_name(candidate)

    if not req or not cand:
        return False
    if cand == req:
        return True
    if cand == f"{req}s" or req == f"{cand}s":
        return True

    return bool(cand.startswith(req) or req.startswith(cand))


async def resolve_view_matches(
    view: str | None,
    project_id: str | None,
    db: AsyncSession,
) -> list[str]:
    """Resolve view name to actual view values in the database.

    Handles aliases and plural forms. If project_id is provided, queries
    the database for actual view values. Otherwise, generates simple
    plural/singular variants.
    """
    if not view:
        return []

    if project_id:
        # Query database for actual view values
        result = await db.execute(
            select(Item.view).where(Item.project_id == project_id, Item.deleted_at.is_(None)).distinct(),
        )
        candidates = [row[0] for row in result.all()]

        # Add alias candidates
        requested = normalize_view_name(view)
        alias_candidates = VIEW_ALIAS_MAP.get(view, VIEW_ALIAS_MAP.get(requested, []))
        if alias_candidates:
            for alias in alias_candidates:
                if alias in candidates:
                    candidates.append(alias)

        # Filter matches
        matches = [candidate for candidate in candidates if view_matches(view, candidate)]
        return matches or [view]

    # Fallback: simple plural/singular handling
    if view.endswith("s"):
        return [view, view[:-1]]
    return [view, f"{view}s"]


def generate_cache_key(cache: CacheService, params: ItemListParams) -> str:
    """Generate cache key for item list query."""
    return cache._generate_key(
        "items",
        project_id=params.project_id,
        status=params.status or "",
        parent_id=params.parent_id or "",
        skip=params.skip,
        limit=params.limit,
    )


async def try_get_from_cache(
    cache: CacheService,
    params: ItemListParams,
) -> tuple[str | None, dict[str, Any] | None]:
    """Attempt to get cached result for simple queries.

    Returns (cache_key, cached_result) tuple. Both may be None if caching
    is not applicable or cache miss.
    """
    # Only cache simple queries without view resolution
    if not params.project_id or params.view:
        return None, None

    cache_key = generate_cache_key(cache, params)
    cached = await cache.get(cache_key)
    return cache_key, cached


def build_query_conditions(params: ItemListParams, view_matches: list[str]) -> list[object]:
    """Build SQLAlchemy filter conditions for item query."""
    conditions = [Item.deleted_at.is_(None)]

    if params.project_id:
        conditions.append(Item.project_id == params.project_id)
    if params.status:
        conditions.append(Item.status == params.status)
    if params.parent_id:
        conditions.append(Item.parent_id == params.parent_id)
    if view_matches:
        conditions.append(Item.view.in_(view_matches))

    return conditions


async def execute_item_query(
    db: AsyncSession,
    conditions: list[object],
    params: ItemListParams,
) -> tuple[int, list[object]]:
    """Execute count and items query with given conditions.

    Returns (total_count, items) tuple.
    """
    try:
        # Count query
        count_query = select(func.count(Item.id)).where(*conditions)
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Items query
        items_query = select(Item).where(*conditions).order_by(Item.created_at.desc()).offset(params.skip)
        if params.limit is not None and params.limit > 0:
            items_query = items_query.limit(params.limit)

        items_result = await db.execute(items_query)
        items = list(items_result.scalars().all())

    except (OperationalError, ProgrammingError) as exc:
        # Required dependency: fail clearly; do not return empty (CLAUDE.md).
        raise HTTPException(
            status_code=503,
            detail=f"Database/schema not ready: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    else:
        return total_count, items


def serialize_item_for_list(item: Item, project_id: str | None) -> dict[str, Any]:
    """Serialize a single item for list response."""
    created_at = getattr(item, "created_at", None)
    return {
        "id": str(getattr(item, "id", "")),
        "project_id": str(getattr(item, "project_id", project_id)),
        "title": getattr(item, "title", ""),
        "view": getattr(item, "view", ""),
        "type": getattr(item, "item_type", getattr(item, "view", "")),
        "status": getattr(item, "status", ""),
        "priority": getattr(item, "priority", "medium"),
        "created_at": (created_at.isoformat() if hasattr(item, "created_at") and created_at else None),
    }


def build_list_response(
    items: list[object],
    total_count: int,
    project_id: str | None,
    limit: int,
) -> dict[str, Any]:
    """Build the final list response with serialized items."""
    items = items or []
    sliced = items if limit is not None and limit > 0 else items

    return {
        "total": total_count,
        "items": [serialize_item_for_list(item, project_id) for item in sliced],
    }
