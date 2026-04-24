"""Integration management endpoints router.

Handles:
- OAuth flows (start/callback)
- Credential management (list/validate/delete)
- Integration mappings (CRUD)
- Sync management (status/trigger/queue)
- Conflict resolution
- External system discovery (GitHub repos, Linear teams, etc.)
- GitHub App installation management
- GitHub Projects linking
- Webhook receivers
- Integration statistics
"""

import os
import secrets
import urllib.parse
from datetime import UTC, datetime
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.clients.github_client import GitHubClient
from tracertm.clients.linear_client import LinearClient
from tracertm.models.integration import (
    IntegrationMapping,
    IntegrationSyncLog,
    IntegrationSyncQueue,
)
from tracertm.models.item import Item
from tracertm.repositories.integration_repository import (
    IntegrationConflictRepository,
    IntegrationCredentialRepository,
    IntegrationMappingRepository,
    IntegrationSyncQueueRepository,
)
from tracertm.repositories.item_repository import ItemRepository
from tracertm.repositories.project_repository import ProjectRepository
from tracertm.schemas.integration import IntegrationProvider
from tracertm.services.encryption_service import EncryptionService

router = APIRouter(prefix="/api/v1/integrations", tags=["integrations"])


def ensure_project_access_fn(project_id: str | None, claims: dict[str, Any] | None) -> None:
    """Check project access (injected from main)."""
    # This will be injected by main.py via dependency
    from tracertm.api.security import check_project_access, is_system_admin

    if not project_id:
        return
    if is_system_admin(claims):
        return
    if not check_project_access(claims.get("sub") if claims else None, project_id):
        raise HTTPException(status_code=403, detail="Project access denied")


def ensure_credential_access_fn(credential: object, claims: dict[str, Any]) -> None:
    """Check credential access (injected from main)."""
    from tracertm.api.security import ensure_credential_access

    ensure_credential_access(credential, claims)


# ==================== OAUTH ====================


@router.post("/oauth/start")
async def start_oauth_flow(
    request: Request,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    _db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Start OAuth flow for an external integration provider."""
    enforce_rate_limit(request, claims)

    project_id = data.get("project_id")
    provider = data.get("provider")
    redirect_uri = data.get("redirect_uri")
    scopes = data.get("scopes", [])
    credential_scope = data.get("credential_scope", "project")

    if project_id:
        ensure_project_access_fn(cast("str", project_id), claims)

    # Validate provider
    valid_providers = [p.value for p in IntegrationProvider]
    if provider not in valid_providers:
        raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}")

    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state in session or temporary storage (in production, use Redis/DB)
    # For now, encode project_id and provider in state
    state_data = f"{credential_scope}:{project_id or ''}:{provider}:{state}"

    # Build OAuth URL based on provider
    if provider == "github":
        client_id = os.environ.get("GITHUB_CLIENT_ID", "")
        oauth_url = "https://github.com/login/oauth/authorize"
        default_scopes = ["repo", "read:org", "read:user", "project"]
        scope_str = " ".join(cast("list[str]", scopes) or default_scopes)
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope_str,
            "state": state_data,
        }
    elif provider == "linear":
        client_id = os.environ.get("LINEAR_CLIENT_ID", "")
        oauth_url = "https://linear.app/oauth/authorize"
        default_scopes = ["read", "write", "issues:create", "comments:create"]
        scope_str = ",".join(cast("list[str]", scopes) or default_scopes)
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope_str,
            "state": state_data,
            "response_type": "code",
        }
    else:
        raise HTTPException(status_code=400, detail=f"OAuth not supported for {provider}")

    auth_url = f"{oauth_url}?{urllib.parse.urlencode(params)}"

    return {
        "auth_url": auth_url,
        "state": state_data,
        "provider": provider,
    }


@router.post("/oauth/callback")
async def oauth_callback(
    request: Request,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Handle OAuth callback and store credentials."""
    from tracertm.api.handlers.oauth import oauth_callback as oauth_callback_handler

    return await oauth_callback_handler(
        request=request,
        data=data,
        claims=claims,
        db=db,
        ensure_project_access_fn=ensure_project_access_fn,
    )


# ==================== CREDENTIALS ====================


@router.get("/credentials")
async def list_credentials(
    request: Request,
    project_id: str | None = None,
    include_global: bool = True,
    claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> dict[str, Any]:
    """List integration credentials for a project."""
    enforce_rate_limit(request, claims)
    if project_id:
        ensure_project_access_fn(project_id, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    repo = IntegrationCredentialRepository(db, encryption_service)

    if project_id:
        sub = claims.get("sub") if include_global else None
        credentials = await repo.get_by_project(
            project_id,
            include_global_user_id=sub if isinstance(sub, str) else None,
        )
    else:
        sub = claims.get("sub")
        if not isinstance(sub, str):
            credentials = []
        else:
            credentials = await repo.list_by_user(sub)

    return {
        "credentials": [
            {
                "id": c.id,
                "provider": c.provider,
                "credential_type": c.credential_type,
                "status": c.status,
                "scopes": c.scopes,
                "provider_user_id": c.provider_user_id,
                "provider_metadata": c.provider_metadata,
                "last_validated_at": c.last_validated_at.isoformat() if c.last_validated_at else None,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in credentials
        ],
        "total": len(credentials),
    }


@router.post("/credentials/{credential_id}/validate")
async def validate_credential(
    request: Request,
    credential_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Validate an integration credential."""
    enforce_rate_limit(request, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    if not encryption_key:
        raise HTTPException(status_code=500, detail="Encryption key not configured")

    encryption_service = EncryptionService(encryption_key)
    repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access_fn(credential, claims)

    # Decrypt token and validate
    token = repo.decrypt_token(credential)
    valid = False
    user_info: dict[str, Any] = {}
    error = None

    try:
        if credential.provider == "github":
            gh_client = GitHubClient(token)
            try:
                user_info = await gh_client.get_authenticated_user()
                valid = True
            finally:
                await gh_client.close()
        elif credential.provider == "linear":
            lin_client = LinearClient(token)
            try:
                user_info = await lin_client.get_viewer()
                valid = True
            finally:
                await lin_client.close()
    except Exception as e:
        error = str(e)

    # Update validation status
    await repo.update_validation_status(
        credential_id,
        valid=valid,
        error=error,
    )

    return {
        "valid": valid,
        "credential_id": credential_id,
        "provider": credential.provider,
        "user": user_info if valid else None,
        "error": error,
        "validated_at": datetime.now(UTC).isoformat(),
    }


@router.delete("/credentials/{credential_id}")
async def delete_credential(
    request: Request,
    credential_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Delete an integration credential."""
    enforce_rate_limit(request, claims)

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await repo.get_by_id(credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access_fn(credential, claims)

    await repo.delete(credential_id)

    return {"success": True, "deleted_id": credential_id}


# ==================== MAPPINGS ====================


@router.get("/mappings")
async def list_mappings(
    request: Request,
    project_id: str,
    provider: str | None = None,
    claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> dict[str, Any]:
    """List integration mappings for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access_fn(project_id, claims)

    repo = IntegrationMappingRepository(db)
    mappings, _total = await repo.list_by_project(project_id, external_system=provider)

    return {
        "mappings": [
            {
                "id": m.id,
                "credential_id": m.integration_credential_id,
                "provider": m.external_system,
                "direction": m.direction,
                "local_item_id": m.project_id if m.tracertm_item_type == "project_root" else m.tracertm_item_id,
                "local_item_type": "project" if m.tracertm_item_type == "project_root" else m.tracertm_item_type,
                "external_id": m.external_id,
                "external_type": m.external_system,
                "external_url": m.external_url,
                "external_key": (m.mapping_metadata or {}).get("external_key"),
                "mapping_metadata": m.mapping_metadata or {},
                "status": m.status,
                "sync_enabled": m.auto_sync,
                "last_synced_at": m.last_sync_at.isoformat() if m.last_sync_at else None,
                "field_mappings": (m.mapping_metadata or {}).get("field_mappings"),
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in mappings
        ],
        "total": len(mappings),
    }


@router.post("/mappings")
async def create_mapping(
    request: Request,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Create a new integration mapping."""
    enforce_rate_limit(request, claims)

    credential_id = data.get("credential_id")
    local_item_id = data.get("local_item_id")
    local_item_type = data.get("local_item_type")
    project_id = data.get("project_id")
    external_id = data.get("external_id")
    external_type = data.get("external_type")
    direction = data.get("direction", "bidirectional")
    mapping_metadata = data.get("mapping_metadata") or {}

    if not project_id and local_item_type == "project":
        project_id = local_item_id

    if not project_id:
        raise HTTPException(status_code=400, detail="project_id required")

    # Validate credential
    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    if not credential_id:
        raise HTTPException(status_code=400, detail="credential_id required")

    credential = await cred_repo.get_by_id(str(credential_id))
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access_fn(credential, claims)

    ensure_project_access_fn(cast("str", project_id), claims)

    tracertm_item_id = local_item_id
    tracertm_item_type = local_item_type
    if local_item_type == "project":
        result = await db.execute(
            select(Item).where(
                Item.project_id == project_id,
                Item.item_type == "project_root",
                Item.title == "Integration Root",
            ),
        )
        root_item = result.scalar_one_or_none()
        if not root_item:
            project_repo = ProjectRepository(db)
            project = await project_repo.get_by_id(project_id)
            title = f"{project.name} Integration Root" if project else "Integration Root"
            item_repo = ItemRepository(db)
            root_item = await item_repo.create(
                project_id=project_id,
                title=title,
                view="configuration",
                item_type="project_root",
                description="Synthetic root item for project-level integrations.",
                status="active",
                priority="low",
            )
        tracertm_item_id = root_item.id
        tracertm_item_type = "project_root"

    # Create mapping
    repo = IntegrationMappingRepository(db)
    mapping = await repo.create(
        project_id=project_id,
        credential_id=str(credential_id),
        tracertm_item_id=str(tracertm_item_id),
        tracertm_item_type=str(tracertm_item_type),
        external_system=str(external_type),
        external_id=str(external_id),
        external_url=data.get("external_url") or "",
        direction=direction,
        auto_sync=data.get("sync_enabled", True),
        mapping_metadata={
            **cast("dict[str, Any]", mapping_metadata),
            "external_key": data.get("external_key"),
            "field_mappings": data.get("field_mappings"),
        },
    )

    return {
        "id": mapping.id,
        "credential_id": mapping.integration_credential_id,
        "provider": mapping.external_system,
        "direction": mapping.direction,
        "local_item_id": local_item_id,
        "local_item_type": local_item_type,
        "external_id": mapping.external_id,
        "external_url": mapping.external_url,
        "status": mapping.status,
        "mapping_metadata": mapping.mapping_metadata or {},
        "created_at": mapping.created_at.isoformat() if mapping.created_at else None,
    }


@router.put("/mappings/{mapping_id}")
async def update_mapping(
    request: Request,
    mapping_id: str,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Update an integration mapping."""
    enforce_rate_limit(request, claims)

    repo = IntegrationMappingRepository(db)
    mapping = await repo.get_by_id(mapping_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")

    # Validate access via credential
    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await cred_repo.get_by_id(mapping.integration_credential_id)
    if credential:
        ensure_credential_access_fn(credential, claims)

    # Update mapping (store field mappings inside mapping_metadata)
    updates: dict[str, Any] = {
        "direction": data.get("direction"),
        "status": data.get("status"),
    }
    if "sync_enabled" in data:
        updates["auto_sync"] = data.get("sync_enabled")
    if "field_mappings" in data:
        mapping_metadata = mapping.mapping_metadata or {}
        mapping_metadata["field_mappings"] = data.get("field_mappings")
        updates["mapping_metadata"] = mapping_metadata
    if "mapping_metadata" in data:
        mapping_metadata = mapping.mapping_metadata or {}
        mapping_metadata.update(cast("dict[str, Any]", data.get("mapping_metadata")) or {})
        updates["mapping_metadata"] = mapping_metadata

    await repo.update(mapping_id, **updates)
    updated = await repo.get_by_id(mapping_id)

    if not updated:
        raise HTTPException(status_code=404, detail="Updated mapping not found")

    return {
        "id": updated.id,
        "direction": updated.direction,
        "sync_enabled": updated.auto_sync,
        "status": updated.status,
        "updated_at": updated.updated_at.isoformat() if updated.updated_at else None,
    }


@router.delete("/mappings/{mapping_id}")
async def delete_mapping(
    request: Request,
    mapping_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Delete an integration mapping."""
    enforce_rate_limit(request, claims)

    repo = IntegrationMappingRepository(db)
    mapping = await repo.get_by_id(mapping_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")

    # Validate access via credential
    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    credential = await cred_repo.get_by_id(mapping.integration_credential_id)
    if credential:
        ensure_credential_access_fn(credential, claims)

    await repo.delete(mapping_id)

    return {"success": True, "deleted_id": mapping_id}


# ==================== SYNC ====================


@router.get("/sync/status")
async def get_sync_status(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Get sync status summary for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access_fn(project_id, claims)

    # Get credentials for this project
    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    cred_repo = IntegrationCredentialRepository(db, encryption_service)
    credentials = await cred_repo.get_by_project(project_id, include_global_user_id=claims.get("sub"))

    # Get queue stats
    queue_result = await db.execute(
        select(IntegrationSyncQueue.status, func.count().label("count"))
        .join(IntegrationMapping)
        .where(IntegrationMapping.project_id == project_id)
        .group_by(IntegrationSyncQueue.status),
    )

    queue_stats = {"pending": 0, "processing": 0, "failed": 0, "completed": 0}
    for row in queue_result.all():
        status_val: object = row[0]
        count_val: object = row[1]
        queue_stats[str(status_val)] = int(cast("int", count_val))

    # Get recent sync logs
    log_result = await db.execute(
        select(IntegrationSyncLog)
        .join(IntegrationMapping)
        .where(IntegrationMapping.project_id == project_id)
        .order_by(IntegrationSyncLog.created_at.desc())
        .limit(10),
    )

    recent_syncs = [
        {
            "id": log.id,
            "provider": log.source_system,
            "event_type": log.operation,
            "direction": log.direction,
            "status": "completed" if log.success else "failed",
            "items_processed": 1 if log.success else 0,
            "items_failed": 0 if log.success else 1,
            "error_message": log.error_message,
            "started_at": log.created_at.isoformat() if log.created_at else None,
            "completed_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in log_result.scalars().all()
    ]

    # Provider summary
    providers = [
        {
            "provider": c.provider,
            "status": c.status,
            "last_validated": c.last_validated_at.isoformat() if c.last_validated_at else None,
        }
        for c in credentials
    ]

    return {
        "project_id": project_id,
        "queue": queue_stats,
        "recent_syncs": recent_syncs,
        "providers": providers,
    }


@router.post("/sync/trigger")
async def trigger_sync(
    request: Request,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Trigger a manual sync for a mapping or credential."""
    enforce_rate_limit(request, claims)

    mapping_id = data.get("mapping_id")
    credential_id = data.get("credential_id")
    direction = data.get("direction", "pull")

    if not mapping_id:
        raise HTTPException(status_code=400, detail="mapping_id required")

    encryption_key = os.environ.get("ENCRYPTION_KEY", "")
    encryption_service = EncryptionService(encryption_key) if encryption_key else None
    cred_repo = IntegrationCredentialRepository(db, encryption_service)

    mapping_repo = IntegrationMappingRepository(db)
    mapping = await mapping_repo.get_by_id(mapping_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    credential_id = mapping.integration_credential_id

    if not credential_id:
        raise HTTPException(status_code=400, detail="credential_id required")

    credential = await cred_repo.get_by_id(str(credential_id))
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    ensure_credential_access_fn(credential, claims)

    # Create sync queue item
    queue_repo = IntegrationSyncQueueRepository(db)
    queue_item = await queue_repo.enqueue(
        credential_id=credential_id,
        mapping_id=mapping_id,
        event_type="manual_sync",
        direction=direction,
        payload=data.get("payload", {}),
        priority="high",
    )

    return {
        "queued": True,
        "queue_id": queue_item.id,
        "provider": credential.provider,
        "direction": direction,
    }


@router.get("/sync/queue")
async def get_sync_queue(
    request: Request,
    project_id: str,
    status: str | None = None,
    limit: int = 50,
    claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> dict[str, Any]:
    """Get sync queue items for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access_fn(project_id, claims)

    queue_repo = IntegrationSyncQueueRepository(db)
    items, _total = await queue_repo.list_by_project(project_id, status=status, limit=limit)

    priority_map = {"low": 0, "normal": 1, "high": 2, "critical": 3}
    mapping_lookup = {}
    if items:
        mapping_ids = list({item.mapping_id for item in items})
        result = await db.execute(select(IntegrationMapping).where(IntegrationMapping.id.in_(mapping_ids)))
        mapping_lookup = {m.id: m for m in result.scalars().all()}

    return {
        "items": [
            {
                "id": item.id,
                "provider": getattr(mapping_lookup.get(item.mapping_id), "external_system", "unknown"),
                "event_type": item.event_type,
                "direction": item.direction,
                "status": item.status,
                "priority": priority_map.get(item.priority, 1),
                "retry_count": item.attempts,
                "error_message": item.error_message,
                "scheduled_at": item.next_retry_at.isoformat() if item.next_retry_at else None,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in items
        ],
        "total": len(items),
    }


# ==================== CONFLICTS ====================


@router.get("/conflicts")
async def list_conflicts(
    request: Request,
    project_id: str,
    status: str = "pending",
    claims: Annotated[dict[str, Any], Depends(auth_guard)] = Depends(auth_guard),
    db: Annotated[AsyncSession, Depends(get_db)] = Depends(get_db),
) -> dict[str, Any]:
    """List sync conflicts for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access_fn(project_id, claims)

    conflict_repo = IntegrationConflictRepository(db)
    if status != "pending":
        return {"conflicts": [], "total": 0}
    conflicts, _total = await conflict_repo.list_pending_by_project(project_id)

    mapping_repo = IntegrationMappingRepository(db)
    mappings = {}
    if conflicts:
        mapping_ids = list({c.mapping_id for c in conflicts})
        for mapping_id in mapping_ids:
            mapping = await mapping_repo.get_by_id(mapping_id)
            if mapping:
                mappings[mapping_id] = mapping

    return {
        "conflicts": [
            {
                "id": c.id,
                "mapping_id": c.mapping_id,
                "provider": getattr(mappings.get(c.mapping_id), "external_system", "unknown"),
                "conflict_type": "field_mismatch",
                "field_name": c.field,
                "local_value": c.tracertm_value,
                "external_value": c.external_value,
                "status": c.resolution_status,
                "resolved_value": c.resolved_value,
                "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
                "created_at": c.detected_at.isoformat() if c.detected_at else None,
            }
            for c in conflicts
        ],
        "total": len(conflicts),
    }


@router.post("/conflicts/{conflict_id}/resolve")
async def resolve_conflict(
    request: Request,
    conflict_id: str,
    data: dict[str, Any],
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Resolve a sync conflict."""
    enforce_rate_limit(request, claims)

    resolution = data.get("resolution")  # "local", "external", "merge", "skip"
    merged_value = data.get("merged_value")

    if resolution not in {"local", "external", "merge", "skip"}:
        raise HTTPException(status_code=400, detail="Invalid resolution strategy")

    if resolution == "merge" and not merged_value:
        raise HTTPException(status_code=400, detail="Merged value required for merge resolution")

    conflict_repo = IntegrationConflictRepository(db)
    conflict = await conflict_repo.get_by_id(conflict_id)
    if not conflict:
        raise HTTPException(status_code=404, detail="Conflict not found")

    # Validate access via mapping
    mapping_repo = IntegrationMappingRepository(db)
    mapping = await mapping_repo.get_by_id(conflict.mapping_id)
    if mapping:
        encryption_key = os.environ.get("ENCRYPTION_KEY", "")
        encryption_service = EncryptionService(encryption_key) if encryption_key else None
        cred_repo = IntegrationCredentialRepository(db, encryption_service)
        credential = await cred_repo.get_by_id(mapping.integration_credential_id)
        if credential:
            ensure_credential_access_fn(credential, claims)

    # Resolve conflict
    if resolution == "skip":
        await conflict_repo.ignore(conflict_id)
    else:
        resolved_value = (
            merged_value
            if resolution == "merge"
            else (conflict.tracertm_value if resolution == "local" else conflict.external_value)
        )
        await conflict_repo.resolve(
            conflict_id,
            resolved_value=str(resolved_value) if resolved_value is not None else "",
            strategy_used=resolution,
        )

    resolved = await conflict_repo.get_by_id(conflict_id)

    return {
        "resolved": True,
        "conflict_id": conflict_id,
        "resolution": resolution,
        "resolved_at": resolved.resolved_at.isoformat() if resolved and resolved.resolved_at else None,
    }


# This file continues in part 2 due to size...
