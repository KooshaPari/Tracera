"""Service for API and webhooks management.

Functional Requirements: FR-COLLAB-004
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any


@dataclass
class WebhookEvent:
    """Webhook event definition."""

    event_type: str
    resource_id: str
    resource_type: str
    action: str
    timestamp: str
    data: dict[str, Any]


class APIWebhooksService:
    """Service for managing API and webhooks."""

    def __init__(self) -> None:
        """Initialize."""
        self.webhooks: dict[str, dict[str, Any]] = {}
        self.webhook_events: list[WebhookEvent] = []
        self.api_keys: dict[str, dict[str, Any]] = {}
        self.rate_limits: dict[str, dict[str, Any]] = {}

    def create_api_key(
        self,
        name: str,
        permissions: list[str],
        expires_in_days: int | None = None,
    ) -> dict[str, Any]:
        """Create an API key."""
        key = hashlib.sha256(f"{name}{datetime.now(UTC)}".encode()).hexdigest()

        api_key = {
            "key": key,
            "name": name,
            "permissions": permissions,
            "created_at": datetime.now(UTC).isoformat(),
            "expires_at": (
                (datetime.now(UTC) + timedelta(days=expires_in_days)).isoformat() if expires_in_days else None
            ),
            "active": True,
        }

        self.api_keys[key] = api_key
        return api_key

    def validate_api_key(self, key: str) -> dict[str, Any]:
        """Validate an API key."""
        if key not in self.api_keys:
            return {"valid": False, "error": "Invalid API key"}

        api_key = self.api_keys[key]

        if not api_key["active"]:
            return {"valid": False, "error": "API key is inactive"}

        if api_key["expires_at"]:
            expires_at = datetime.fromisoformat(api_key["expires_at"])
            if datetime.now(UTC) > expires_at:
                return {"valid": False, "error": "API key has expired"}

        return {
            "valid": True,
            "key": key,
            "permissions": api_key["permissions"],
        }

    def revoke_api_key(self, key: str) -> dict[str, Any]:
        """Revoke an API key."""
        if key not in self.api_keys:
            return {"error": "API key not found"}

        self.api_keys[key]["active"] = False
        return {"revoked": True, "key": key}

    def register_webhook(
        self,
        url: str,
        events: list[str],
        secret: str | None = None,
    ) -> dict[str, Any]:
        """Register a webhook."""
        webhook_id = hashlib.sha256(f"{url}{datetime.now(UTC)}".encode()).hexdigest()[:16]

        webhook = {
            "id": webhook_id,
            "url": url,
            "events": events,
            "secret": secret,
            "active": True,
            "created_at": datetime.now(UTC).isoformat(),
            "last_triggered": None,
            "delivery_count": 0,
        }

        self.webhooks[webhook_id] = webhook
        return webhook

    def unregister_webhook(self, webhook_id: str) -> dict[str, Any]:
        """Unregister a webhook."""
        if webhook_id not in self.webhooks:
            return {"error": "Webhook not found"}

        del self.webhooks[webhook_id]
        return {"unregistered": True, "webhook_id": webhook_id}

    def trigger_webhook_event(
        self,
        event_type: str,
        resource_id: str,
        resource_type: str,
        action: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Trigger a webhook event."""
        event = WebhookEvent(
            event_type=event_type,
            resource_id=resource_id,
            resource_type=resource_type,
            action=action,
            timestamp=datetime.now(UTC).isoformat(),
            data=data,
        )

        self.webhook_events.append(event)

        # Find matching webhooks
        triggered_count = 0
        for webhook in self.webhooks.values():
            if webhook["active"] and event_type in webhook["events"]:
                webhook["last_triggered"] = datetime.now(UTC).isoformat()
                webhook["delivery_count"] += 1
                triggered_count += 1

        return {
            "event_id": len(self.webhook_events),
            "event_type": event_type,
            "webhooks_triggered": triggered_count,
        }

    def get_webhook_events(
        self,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get webhook events."""
        events = self.webhook_events

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return [
            {
                "event_type": e.event_type,
                "resource_id": e.resource_id,
                "resource_type": e.resource_type,
                "action": e.action,
                "timestamp": e.timestamp,
            }
            for e in events[-limit:]
        ]

    def set_rate_limit(
        self,
        api_key: str,
        requests_per_minute: int,
    ) -> dict[str, Any]:
        """Set rate limit for API key."""
        self.rate_limits[api_key] = {
            "requests_per_minute": requests_per_minute,
            "requests_made": 0,
            "reset_at": (datetime.now(UTC) + timedelta(minutes=1)).isoformat(),
        }

        return {
            "api_key": api_key,
            "requests_per_minute": requests_per_minute,
        }

    def check_rate_limit(self, api_key: str) -> dict[str, Any]:
        """Check rate limit for API key."""
        if api_key not in self.rate_limits:
            return {"allowed": True, "reason": "No rate limit set"}

        limit = self.rate_limits[api_key]

        if datetime.now(UTC).isoformat() > limit["reset_at"]:
            limit["requests_made"] = 0
            limit["reset_at"] = (datetime.now(UTC) + timedelta(minutes=1)).isoformat()

        if limit["requests_made"] >= limit["requests_per_minute"]:
            return {"allowed": False, "reason": "Rate limit exceeded"}

        limit["requests_made"] += 1
        return {
            "allowed": True,
            "requests_remaining": limit["requests_per_minute"] - limit["requests_made"],
        }

    def get_api_stats(self) -> dict[str, Any]:
        """Get API statistics."""
        return {
            "total_api_keys": len(self.api_keys),
            "active_api_keys": len([k for k in self.api_keys.values() if k["active"]]),
            "total_webhooks": len(self.webhooks),
            "active_webhooks": len([w for w in self.webhooks.values() if w["active"]]),
            "total_webhook_events": len(self.webhook_events),
        }
