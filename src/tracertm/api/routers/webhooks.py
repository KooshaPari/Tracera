"""Webhook management and receiver router."""

from __future__ import annotations

import hashlib
import hmac
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.config.rate_limiting import enforce_rate_limit
from tracertm.api.deps import auth_guard, get_db
from tracertm.api.routers.oauth import ensure_project_access
from tracertm.models.webhook_integration import WebhookStatus
from tracertm.repositories.integration_repository import IntegrationSyncQueueRepository
from tracertm.repositories.webhook_repository import WebhookRepository
from tracertm.services.webhook_service import WebhookService

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])
project_router = APIRouter(prefix="/api/v1/projects", tags=["webhooks"])


class WebhookCreateRequest(BaseModel):
    """Request schema for creating a webhook."""

    project_id: str
    name: str
    description: str | None = None
    provider: str = "custom"
    enabled_events: list[str] | None = None
    event_filters: dict[str, Any] | None = None
    callback_url: str | None = None
    callback_headers: dict[str, Any] | None = None
    default_suite_id: str | None = None
    rate_limit_per_minute: int = 60
    auto_create_run: bool = True
    auto_complete_run: bool = True
    verify_signatures: bool = True
    metadata: dict[str, Any] | None = None


class WebhookUpdateRequest(BaseModel):
    """Request schema for updating a webhook."""

    name: str | None = None
    description: str | None = None
    enabled_events: list[str] | None = None
    event_filters: dict[str, Any] | None = None
    callback_url: str | None = None
    callback_headers: dict[str, Any] | None = None
    default_suite_id: str | None = None
    rate_limit_per_minute: int | None = None
    auto_create_run: bool | None = None
    auto_complete_run: bool | None = None
    verify_signatures: bool | None = None
    metadata: dict[str, Any] | None = None


class WebhookStatusRequest(BaseModel):
    """Request schema for updating webhook status."""

    status: str


def _serialize_webhook(
    webhook: Any,
    *,
    include_api_key: bool = False,
    include_metadata: bool = False,
    include_request_stats: bool = True,
) -> dict[str, Any]:
    payload = {
        "id": webhook.id,
        "project_id": webhook.project_id,
        "name": webhook.name,
        "description": webhook.description,
        "provider": webhook.provider.value,
        "status": webhook.status.value,
        "webhook_secret": webhook.webhook_secret,
        "enabled_events": webhook.enabled_events,
        "callback_url": webhook.callback_url,
        "default_suite_id": webhook.default_suite_id,
        "rate_limit_per_minute": webhook.rate_limit_per_minute,
        "auto_create_run": webhook.auto_create_run,
        "auto_complete_run": webhook.auto_complete_run,
        "verify_signatures": webhook.verify_signatures,
        "version": webhook.version,
        "created_at": webhook.created_at.isoformat() if webhook.created_at else None,
        "updated_at": webhook.updated_at.isoformat() if webhook.updated_at else None,
    }
    if include_api_key:
        payload["api_key"] = webhook.api_key
    if include_metadata:
        payload["event_filters"] = webhook.event_filters
        payload["callback_headers"] = webhook.callback_headers
        payload["webhook_metadata"] = webhook.webhook_metadata
    if include_request_stats:
        payload.update(
            {
                "total_requests": webhook.total_requests,
                "successful_requests": webhook.successful_requests,
                "failed_requests": webhook.failed_requests,
                "last_request_at": webhook.last_request_at.isoformat() if webhook.last_request_at else None,
                "last_success_at": webhook.last_success_at.isoformat() if webhook.last_success_at else None,
                "last_failure_at": webhook.last_failure_at.isoformat() if webhook.last_failure_at else None,
                "last_error_message": webhook.last_error_message,
            },
        )
    return payload


def _serialize_log(log: Any) -> dict[str, Any]:
    return {
        "id": log.id,
        "webhook_id": log.webhook_id,
        "request_id": log.request_id,
        "event_type": log.event_type,
        "http_method": log.http_method,
        "source_ip": log.source_ip,
        "user_agent": log.user_agent,
        "request_headers": log.request_headers,
        "request_body_preview": log.request_body_preview,
        "payload_size_bytes": log.payload_size_bytes,
        "success": log.success,
        "status_code": log.status_code,
        "error_message": log.error_message,
        "processing_time_ms": log.processing_time_ms,
        "test_run_id": log.test_run_id,
        "results_submitted": log.results_submitted,
        "created_at": log.created_at.isoformat(),
    }


async def _get_webhook_or_404(repo: WebhookRepository, webhook_id: str) -> Any:
    webhook = await repo.get_by_id(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    return webhook


@router.get("")
async def list_webhooks(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    provider: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    """List webhooks for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    repo = WebhookRepository(db)
    webhooks, total = await repo.list_by_project(
        project_id=project_id,
        provider=provider,
        status=status,
        skip=skip,
        limit=limit,
    )

    return {
        "webhooks": [_serialize_webhook(webhook) for webhook in webhooks],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("")
async def create_webhook(
    request: Request,
    payload: WebhookCreateRequest,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Create a new webhook integration."""
    enforce_rate_limit(request, claims)
    ensure_project_access(payload.project_id, claims)

    repo = WebhookRepository(db)
    webhook = await repo.create(
        project_id=payload.project_id,
        name=payload.name,
        description=payload.description,
        provider=payload.provider,
        enabled_events=payload.enabled_events,
        event_filters=payload.event_filters,
        callback_url=payload.callback_url,
        callback_headers=payload.callback_headers,
        default_suite_id=payload.default_suite_id,
        rate_limit_per_minute=payload.rate_limit_per_minute,
        auto_create_run=payload.auto_create_run,
        auto_complete_run=payload.auto_complete_run,
        verify_signatures=payload.verify_signatures,
        metadata=payload.metadata,
    )
    await db.commit()
    return {
        "id": webhook.id,
        "project_id": webhook.project_id,
        "name": webhook.name,
        "description": webhook.description,
        "provider": webhook.provider.value,
        "status": webhook.status.value,
        "webhook_secret": webhook.webhook_secret,
        "enabled_events": webhook.enabled_events,
        "callback_url": webhook.callback_url,
        "default_suite_id": webhook.default_suite_id,
        "rate_limit_per_minute": webhook.rate_limit_per_minute,
        "auto_create_run": webhook.auto_create_run,
        "auto_complete_run": webhook.auto_complete_run,
        "verify_signatures": webhook.verify_signatures,
        "total_requests": webhook.total_requests,
        "successful_requests": webhook.successful_requests,
        "failed_requests": webhook.failed_requests,
        "version": webhook.version,
        "created_at": webhook.created_at.isoformat(),
        "updated_at": webhook.updated_at.isoformat(),
    }


@router.get("/{webhook_id}")
async def get_webhook(
    request: Request,
    webhook_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Get a webhook by ID."""
    enforce_rate_limit(request, claims)

    repo = WebhookRepository(db)
    webhook = await _get_webhook_or_404(repo, webhook_id)
    ensure_project_access(webhook.project_id, claims)

    return _serialize_webhook(webhook, include_api_key=True, include_metadata=True)


@router.put("/{webhook_id}")
async def update_webhook(
    request: Request,
    webhook_id: str,
    payload: WebhookUpdateRequest,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Update a webhook."""
    enforce_rate_limit(request, claims)

    repo = WebhookRepository(db)
    webhook = await _get_webhook_or_404(repo, webhook_id)
    ensure_project_access(webhook.project_id, claims)

    updates = payload.model_dump(exclude_unset=True)
    if "metadata" in updates:
        updates["webhook_metadata"] = updates.pop("metadata")

    updated_webhook = await repo.update(webhook_id, **updates)
    await db.commit()

    if updated_webhook is None:
        raise HTTPException(status_code=404, detail="Webhook not found after update")
    return _serialize_webhook(updated_webhook, include_request_stats=False)


@router.post("/{webhook_id}/status")
async def set_webhook_status(
    request: Request,
    webhook_id: str,
    payload: WebhookStatusRequest,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Update webhook status."""
    enforce_rate_limit(request, claims)

    if payload.status not in {"active", "paused", "disabled"}:
        raise HTTPException(status_code=400, detail="Invalid status")

    repo = WebhookRepository(db)
    webhook = await _get_webhook_or_404(repo, webhook_id)
    ensure_project_access(webhook.project_id, claims)

    updated_webhook = await repo.set_status(webhook_id, payload.status)
    await db.commit()

    if updated_webhook is None:
        raise HTTPException(status_code=404, detail="Webhook not found after status update")
    return {"id": updated_webhook.id, "status": updated_webhook.status.value, "version": updated_webhook.version}


@router.post("/{webhook_id}/regenerate-secret")
async def regenerate_webhook_secret(
    request: Request,
    webhook_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Regenerate the webhook secret."""
    enforce_rate_limit(request, claims)

    repo = WebhookRepository(db)
    webhook = await _get_webhook_or_404(repo, webhook_id)
    ensure_project_access(webhook.project_id, claims)

    updated_webhook = await repo.regenerate_secret(webhook_id)
    await db.commit()

    if updated_webhook is None:
        raise HTTPException(status_code=404, detail="Webhook not found after secret regeneration")
    return {"id": updated_webhook.id, "webhook_secret": updated_webhook.webhook_secret, "version": updated_webhook.version}


@router.delete("/{webhook_id}")
async def delete_webhook(
    request: Request,
    webhook_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Delete a webhook."""
    enforce_rate_limit(request, claims)

    repo = WebhookRepository(db)
    webhook = await _get_webhook_or_404(repo, webhook_id)
    ensure_project_access(webhook.project_id, claims)

    await repo.delete(webhook_id)
    await db.commit()
    return {"success": True}


@router.get("/{webhook_id}/logs")
async def get_webhook_logs(
    request: Request,
    webhook_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
    success: bool | None = None,
    event_type: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> dict[str, Any]:
    """Get webhook logs."""
    enforce_rate_limit(request, claims)

    repo = WebhookRepository(db)
    webhook = await _get_webhook_or_404(repo, webhook_id)
    ensure_project_access(webhook.project_id, claims)

    logs, total = await repo.get_logs(
        webhook_id=webhook_id,
        success=success,
        event_type=event_type,
        skip=skip,
        limit=limit,
    )

    return {"logs": [_serialize_log(log) for log in logs], "total": total, "skip": skip, "limit": limit}


@project_router.get("/{project_id}/webhooks/stats")
async def get_webhook_stats(
    request: Request,
    project_id: str,
    claims: Annotated[dict[str, Any], Depends(auth_guard)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Get webhook statistics for a project."""
    enforce_rate_limit(request, claims)
    ensure_project_access(project_id, claims)

    repo = WebhookRepository(db)
    return await repo.get_stats(project_id)


@router.post("/inbound/{webhook_id}")
async def receive_inbound_webhook(
    request: Request,
    webhook_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Receive inbound webhook from CI/CD systems."""
    raw_body = await request.body()

    try:
        payload = await request.json()
    except ValueError:
        return {
            "success": False,
            "message": "Invalid JSON payload",
            "error": "Could not parse request body as JSON",
        }

    headers: dict[str, Any] = dict(request.headers)
    signature = (
        headers.get("x-hub-signature-256")
        or headers.get("x-hub-signature")
        or headers.get("x-signature")
        or headers.get("x-webhook-signature")
    )
    source_ip = request.client.host if request.client else None
    user_agent = headers.get("user-agent")

    service = WebhookService(db)
    result = await service.process_inbound_webhook(
        webhook_id=webhook_id,
        payload=payload,
        raw_payload=raw_body,
        signature=signature,
        headers=headers,
        source_ip=source_ip,
        user_agent=user_agent,
    )
    await db.commit()

    if not result["success"]:
        message = str(result.get("message", ""))
        if "Rate limit" in message:
            raise HTTPException(status_code=429, detail=result)
        if "signature" in message.lower() or "not found" in message.lower():
            raise HTTPException(status_code=401, detail=result)
        raise HTTPException(status_code=400, detail=result)

    return result


@router.post("/linear/{webhook_id}")
async def receive_linear_webhook(
    request: Request,
    webhook_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Receive Linear webhook events."""
    body = await request.body()

    repo = WebhookRepository(db)
    webhook = await _get_webhook_or_404(repo, webhook_id)
    if webhook.status != WebhookStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Webhook is inactive")

    signature_header = request.headers.get("Linear-Signature", "")
    if webhook.webhook_secret:
        expected_signature = hmac.new(webhook.webhook_secret.encode(), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature_header, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event_type = payload.get("type", "unknown")
    action = payload.get("action", "")

    credential_id = getattr(webhook, "credential_id", None)
    if not credential_id:
        raise HTTPException(status_code=400, detail="Webhook missing credential_id")

    queue_repo = IntegrationSyncQueueRepository(db)
    await queue_repo.enqueue(
        credential_id=str(credential_id),
        mapping_id=str(getattr(webhook, "mapping_id", None) or webhook_id),
        event_type=f"webhook:{event_type}:{action}",
        direction="pull",
        payload={
            "webhook_id": webhook_id,
            "event_type": event_type,
            "action": action,
            "data": payload.get("data", {}),
        },
    )

    await repo.create_log(
        webhook_id=webhook_id,
        event_type=f"{event_type}:{action}",
        payload_size_bytes=len(body),
        success=True,
        status_code=200,
    )

    await db.commit()
    return {"received": True, "event": event_type, "action": action}
