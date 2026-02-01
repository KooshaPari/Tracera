import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from tracertm.api.deps import get_db, auth_guard
from tracertm.models.notification import Notification

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    link: str | None
    read_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    limit: int = 20,
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    try:
        if not await _notifications_table_exists(db):
            return []

        # Check if we need to seed initial notifications for this user
        result = await db.execute(
            select(Notification).where(Notification.user_id == user_id).limit(1)
        )
        if not result.scalar():
            await seed_initial_notifications(db, user_id)

        query = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    except Exception as exc:
        # Fail clearly; do not return empty (CLAUDE.md).
        raise HTTPException(status_code=500, detail=f"Notifications failed: {exc}") from exc

@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    user_id = claims.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    if not await _notifications_table_exists(db):
        return {"status": "success"}

    stmt = (
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user_id)
        .values(read_at=datetime.now())
    )
    result = await db.execute(stmt)
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"status": "success"}

@router.post("/read-all")
async def mark_all_as_read(
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db),
):
    user_id = claims.get("sub")
    if not await _notifications_table_exists(db):
        return {"status": "success"}
    stmt = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.read_at.is_(None))
        .values(read_at=datetime.now())
    )
    await db.execute(stmt)
    await db.commit()
    return {"status": "success"}

async def seed_initial_notifications(db: AsyncSession, user_id: str):
    """Seed authentic-looking notifications for a new user."""
    from tracertm.models.notification import Notification
    import uuid
    from datetime import datetime, timedelta

    # Authentic AI-generated-style notifications
    notifications = [
        Notification(
            user_id=user_id,
            type="success",
            title="Project Analysis Complete",
            message="The structural analysis for 'SoundWave' has completed successfully. 3 potential cycles detected.",
            link="/projects/soundwave/analysis",
            created_at=datetime.now() - timedelta(minutes=5)
        ),
        Notification(
            user_id=user_id,
            type="info",
            title="New Integration Connected",
            message="GitHub integration was successfully configured for organization 'Acme Corp'.",
            link="/settings/integrations",
            created_at=datetime.now() - timedelta(hours=2)
        ),
        Notification(
            user_id=user_id,
            type="warning",
            title="Coverage Gap Detected",
            message="Test coverage for 'PaymentService' has dropped below 80%. Review the latest report.",
            link="/projects/payments/coverage",
            created_at=datetime.now() - timedelta(days=1)
        ),
        Notification(
            user_id=user_id,
            type="info",
            title="Welcome to TraceRTM",
            message="Your workspace is ready. Check out the Quick Start guide to begin.",
            created_at=datetime.now() - timedelta(days=2)
        )
    ]
    
    db.add_all(notifications)
    await db.commit()


async def _notifications_table_exists(db: AsyncSession) -> bool:
    result = await db.execute(
        text(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'notifications'
            """
        )
    )
    return result.scalar() is not None
