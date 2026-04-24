"""Item summary API endpoints for TraceRTM."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select

from tracertm.api.deps import auth_guard, get_db
from tracertm.api.routers.items import enforce_rate_limit, ensure_project_access
from tracertm.models.item import Item

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/items", tags=["items"])


@router.get("/summary")
async def summarize_items_endpoint(
    request: Request,
    project_id: str,
    view: str,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, object]:
    """Summarize items in a view (counts by status + samples)."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    view_upper = view.upper()

    status_counts = (
        await db.execute(
            select(Item.status, func.count(Item.id))
            .where(
                Item.project_id == project_id,
                Item.view == view_upper,
                Item.deleted_at.is_(None),
            )
            .group_by(Item.status),
        )
    ).all()

    samples = (
        (
            await db.execute(
                select(Item)
                .where(
                    Item.project_id == project_id,
                    Item.view == view_upper,
                    Item.deleted_at.is_(None),
                )
                .order_by(Item.updated_at.desc())
                .limit(5),
            )
        )
        .scalars()
        .all()
    )

    return {
        "project_id": project_id,
        "view": view_upper,
        "status_counts": {str(row[0]): int(row[1]) for row in status_counts},
        "total": sum(int(row[1]) for row in status_counts),
        "samples": [
            {
                "id": str(item.id),
                "external_id": getattr(item, "external_id", None),
                "title": item.title,
                "status": item.status,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in samples
        ],
    }
