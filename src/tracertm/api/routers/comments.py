"""Item comments API endpoints.

GET  /api/v1/items/{item_id}/comments        - list comments for an item
POST /api/v1/items/{item_id}/comments        - create a new comment
DELETE /api/v1/items/{item_id}/comments/{id} - delete own comment
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import auth_guard, get_db
from tracertm.models.item_comment import ItemComment

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items/{item_id}/comments", tags=["comments"])

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class CommentResponse(BaseModel):
    """Serialised comment returned to clients."""

    id: str
    item_id: str
    author_id: str
    author: str  # display name alias
    content: str
    edited: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm_row(cls, row: ItemComment) -> "CommentResponse":
        """Map ORM row to response schema."""
        return cls(
            id=row.id,
            item_id=row.item_id,
            author_id=row.author_id,
            author=row.author_name or row.author_id,
            content=row.content,
            edited=row.edited,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class CreateCommentBody(BaseModel):
    """Request body for comment creation."""

    content: str = Field(..., min_length=1, max_length=10_000)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _table_exists(db: AsyncSession) -> bool:
    """Return True if the item_comments table exists in the DB."""
    try:
        result = await db.execute(
            text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_name = 'item_comments' LIMIT 1"
            )
        )
        return result.scalar() is not None
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/", response_model=list[CommentResponse])
async def list_comments(
    item_id: str,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[Any]:
    """Return all comments for *item_id*, newest last."""
    if not await _table_exists(db):
        return []
    try:
        result = await db.execute(
            select(ItemComment)
            .where(ItemComment.item_id == item_id)
            .order_by(ItemComment.created_at.asc())
        )
        rows = list(result.scalars().all())
        return [CommentResponse.from_orm_row(r) for r in rows]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch comments: {exc}") from exc


@router.post("/", response_model=CommentResponse, status_code=201)
async def create_comment(
    item_id: str,
    body: CreateCommentBody,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Create a new comment on *item_id*."""
    if not await _table_exists(db):
        raise HTTPException(status_code=503, detail="Comments table not yet migrated")

    user_id = str(claims.get("sub", "anonymous"))
    # Prefer the display name stored in the JWT if present
    author_name = str(claims.get("name") or claims.get("email") or user_id)

    try:
        comment = ItemComment(
            item_id=item_id,
            author_id=user_id,
            author_name=author_name,
            content=body.content.strip(),
        )
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return CommentResponse.from_orm_row(comment)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create comment: {exc}") from exc


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    item_id: str,
    comment_id: str,
    claims: Annotated[dict[str, object], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete own comment. Non-owners receive 403."""
    if not await _table_exists(db):
        raise HTTPException(status_code=503, detail="Comments table not yet migrated")

    user_id = str(claims.get("sub", "anonymous"))
    result = await db.execute(
        select(ItemComment).where(
            ItemComment.id == comment_id,
            ItemComment.item_id == item_id,
        )
    )
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != user_id:
        raise HTTPException(status_code=403, detail="Cannot delete another user's comment")

    try:
        await db.delete(comment)
        await db.commit()
    except Exception as exc:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {exc}") from exc
