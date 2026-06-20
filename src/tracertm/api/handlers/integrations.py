"""Integration statistics and handlers for reducing complexity.

Functional Requirements: FR-COLLAB-006, FR-COLLAB-007, FR-COLLAB-008
"""

import os
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from fastapi import HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.constants import (
    DECIMAL_PRECISION_DEFAULT,
    HTTP_FORBIDDEN,
    PERCENTAGE_MAX,
    TIME_WINDOW_WEEK,
    ZERO,
)
from tracertm.models.integration import (
    IntegrationConflict,
    IntegrationCredential,
    IntegrationMapping,
    IntegrationSyncLog,
    IntegrationSyncQueue,
)
from tracertm.repositories.integration_repository import IntegrationCredentialRepository
from tracertm.services.encryption_service import EncryptionService


def ensure_project_access(project_id: str | None, claims: dict[str, Any] | None) -> None:
    """Check project access using injected helper when available. System admins bypass checks."""
    from tracertm.api.security import check_project_access, is_system_admin

    if not project_id:
        return
    if is_system_admin(claims):
        return
    if not check_project_access(claims.get("sub") if claims else None, project_id):
        raise HTTPException(status_code=HTTP_FORBIDDEN, detail="Project access denied")


def _build_provider_stats(credentials: list[IntegrationCredential]) -> list[dict[str, Any]]:
    """Build provider statistics from credentials."""
    return [
        {
            "provider": c.provider,
            "status": c.status,
            "credential_type": c.credential_type,
        }
        for c in credentials
    ]


async def _get_mapping_stats(db: AsyncSession, project_id: str) -> dict[str, Any]:
    """Get mapping statistics for a project."""
    mapping_result = await db.execute(
        select(
            IntegrationMapping.external_system,
            IntegrationMapping.status,
            func.count().label("count"),
        )
        .where(IntegrationMapping.project_id == project_id)
        .group_by(IntegrationMapping.external_system, IntegrationMapping.status),
    )

    total = ZERO
    active = ZERO
    by_provider: dict[str, int] = {}
    for row in mapping_result.all():
        cnt: object = row[2]
        status_val: object = row[1]
        ext: object = row[0]
        total += int(cast("int", cnt))
        if str(status_val) == "active":
            active += int(cast("int", cnt))
        ext_key = str(ext)
        by_provider[ext_key] = by_provider.get(ext_key, ZERO) + int(cast("int", cnt))

    return {"total": total, "active": active, "by_provider": by_provider}


async def _get_sync_stats(db: AsyncSession, project_id: str) -> dict[str, Any]:
    """Get sync statistics for a project."""
    # Queue pending count
    queue_pending = await db.scalar(
        select(func.count())
        .select_from(IntegrationSyncQueue)
        .join(IntegrationMapping)
        .where(
            IntegrationMapping.project_id == project_id,
            IntegrationSyncQueue.status == "pending",
        ),
    )

    # Recent sync logs (last 7 days)
    week_ago = datetime.now(UTC) - timedelta(days=TIME_WINDOW_WEEK)

    sync_logs_result = await db.execute(
        select(
            IntegrationSyncLog.success,
            func.count().label("count"),
        )
        .join(IntegrationMapping)
        .where(
            IntegrationMapping.project_id == project_id,
            IntegrationSyncLog.created_at >= week_ago,
        )
        .group_by(IntegrationSyncLog.success),
    )

    sync_counts = {"total": ZERO, "success": ZERO}
    for row in sync_logs_result.all():
        cnt: object = row[1]
        success_val: object = row[0]
        sync_counts["total"] += int(cast("int", cnt))
        if bool(success_val):
            sync_counts["success"] += int(cast("int", cnt))

    success_rate = (
        round(sync_counts["success"] / sync_counts["total"] * PERCENTAGE_MAX, DECIMAL_PRECISION_DEFAULT)
        if sync_counts["total"] > ZERO
        else ZERO
    )

    return {
        "queue_pending": queue_pending or ZERO,
        "recent_syncs": sync_counts["total"],
        "success_rate": success_rate,
    }


async def _get_conflict_stats(db: AsyncSession, project_id: str) -> dict[str, int]:
    """Get conflict statistics for a project."""
    conflict_result = await db.execute(
        select(
            IntegrationConflict.resolution_status,
            func.count().label("count"),
        )
        .join(IntegrationMapping)
        .where(IntegrationMapping.project_id == project_id)
        .group_by(IntegrationConflict.resolution_status),
    )

    conflict_stats = {"pending": ZERO, "resolved": ZERO}
    for row in conflict_result.all():
        cnt: object = row[1]
        status_val: object = row[0]
        if str(status_val) == "pending":
            conflict_stats["pending"] = int(cast("int", cnt))
        elif str(status_val) == "resolved":
            conflict_stats["resolved"] = int(cast("int", cnt))

    return conflict_stats


def _get_encryption_service() -> EncryptionService | None:
    """Get encryption service if encryption key is available."""
    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    return EncryptionService(encryption_key) if encryption_key else None


async def get_integration_stats_handler(
    request: Request,
    project_id: str,
    claims: dict[str, Any],
    db: AsyncSession,
) -> dict[str, Any]:
    """Get integration statistics for a project.

    Complexity reduced by extracting helper functions for each stats category.
    """
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    # Get credentials
    encryption_service = _get_encryption_service()
    cred_repo = IntegrationCredentialRepository(db, encryption_service)
    credentials = await cred_repo.get_by_project(project_id, include_global_user_id=claims.get("sub"))

    # Build all stats in parallel-friendly structure
    providers = _build_provider_stats(credentials)
    mapping_stats = await _get_mapping_stats(db, project_id)
    sync_stats = await _get_sync_stats(db, project_id)
    conflict_stats = await _get_conflict_stats(db, project_id)

    return {
        "project_id": project_id,
        "providers": providers,
        "mappings": mapping_stats,
        "sync": sync_stats,
        "conflicts": conflict_stats,
    }
