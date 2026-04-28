"""GitHub webhook endpoint handlers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.api.deps import get_db
from tracertm.repositories.integration_repository import IntegrationSyncQueueRepository
from tracertm.repositories.webhook_repository import WebhookRepository


async def receive_github_webhook(
    request: Request,
    webhook_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Receive GitHub webhook events."""
    from tracertm.models.webhook_integration import WebhookStatus

    webhook_repo = WebhookRepository(db)
    webhook = await webhook_repo.get_by_id(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    if webhook.status != WebhookStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Webhook is inactive")

    body = await request.body()
    signature_header = request.headers.get("X-Hub-Signature-256", "")

    if webhook.webhook_secret:
        import hashlib
        import hmac

        expected_signature = "sha256=" + hmac.new(
            webhook.webhook_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature_header, expected_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    event_type = request.headers.get("X-GitHub-Event", "unknown")
    payload = await request.json()

    metadata = webhook.webhook_metadata or {}
    raw_credential_id = metadata.get("credential_id")
    if not isinstance(raw_credential_id, str) or not raw_credential_id:
        raise HTTPException(status_code=400, detail="Webhook missing credential_id")
    raw_mapping_id = metadata.get("mapping_id")
    mapping_id = raw_mapping_id if isinstance(raw_mapping_id, str) and raw_mapping_id else webhook_id

    queue_repo = IntegrationSyncQueueRepository(db)
    await queue_repo.enqueue(
        credential_id=raw_credential_id,
        mapping_id=mapping_id,
        event_type=f"webhook:{event_type}",
        direction="pull",
        payload={
            "webhook_id": webhook_id,
            "event_type": event_type,
            "delivery_id": request.headers.get("X-GitHub-Delivery"),
            "data": payload,
        },
    )

    await webhook_repo.create_log(
        webhook_id=webhook_id,
        event_type=event_type,
        payload_size_bytes=len(body),
        success=True,
        status_code=200,
    )

    return {"received": True, "event": event_type}
