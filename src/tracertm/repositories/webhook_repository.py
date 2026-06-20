"""Repository for Webhook Integration operations."""

import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.models.webhook_integration import (
    WebhookIntegration,
    WebhookLog,
    WebhookProvider,
    WebhookStatus,
)


class WebhookRepository:
    """Repository for webhook CRUD and operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        project_id: str,
        name: str,
        description: str | None = None,
        provider: str = "custom",
        enabled_events: list[str] | None = None,
        event_filters: dict[str, Any] | None = None,
        callback_url: str | None = None,
        callback_headers: dict[str, str] | None = None,
        default_suite_id: str | None = None,
        rate_limit_per_minute: int = 60,
        auto_create_run: bool = True,
        auto_complete_run: bool = True,
        verify_signatures: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> WebhookIntegration:
        """Create a new webhook integration."""
        webhook = WebhookIntegration(
            id=str(uuid.uuid4()),
            project_id=project_id,
            name=name,
            description=description,
            provider=WebhookProvider(provider),
            status=WebhookStatus.ACTIVE,
            enabled_events=enabled_events
            or [
                "test_run_start",
                "test_run_complete",
                "test_result_submit",
                "bulk_results",
            ],
            event_filters=event_filters,
            callback_url=callback_url,
            callback_headers=callback_headers,
            default_suite_id=default_suite_id,
            rate_limit_per_minute=rate_limit_per_minute,
            auto_create_run=auto_create_run,
            auto_complete_run=auto_complete_run,
            verify_signatures=verify_signatures,
            webhook_metadata=metadata or {},
        )
        self.session.add(webhook)
        await self.session.flush()
        return webhook

    async def get_by_id(self, webhook_id: str) -> WebhookIntegration | None:
        """Get a webhook by ID."""
        result = await self.session.execute(select(WebhookIntegration).where(WebhookIntegration.id == webhook_id))
        return result.scalar_one_or_none()

    async def list_by_project(
        self,
        project_id: str,
        provider: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[WebhookIntegration], int]:
        """List webhooks for a project with filtering."""
        query = select(WebhookIntegration).where(WebhookIntegration.project_id == project_id)

        if provider:
            query = query.where(WebhookIntegration.provider == provider)
        if status:
            query = query.where(WebhookIntegration.status == status)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.order_by(WebhookIntegration.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        webhooks = list(result.scalars().all())

        return webhooks, total

    async def update(
        self,
        webhook_id: str,
        **updates: Any,
    ) -> WebhookIntegration | None:
        """Update a webhook."""
        webhook = await self.get_by_id(webhook_id)
        if not webhook:
            return None

        for key, value in updates.items():
            if hasattr(webhook, key) and value is not None:
                setattr(webhook, key, value)

        webhook.version += 1
        await self.session.flush()
        return webhook

    async def set_status(
        self,
        webhook_id: str,
        status: str,
    ) -> WebhookIntegration | None:
        """Update webhook status."""
        webhook = await self.get_by_id(webhook_id)
        if not webhook:
            return None

        webhook.status = WebhookStatus(status)
        webhook.version += 1
        await self.session.flush()
        return webhook

    async def regenerate_secret(
        self,
        webhook_id: str,
    ) -> WebhookIntegration | None:
        """Regenerate the webhook secret."""
        webhook = await self.get_by_id(webhook_id)
        if not webhook:
            return None

        webhook.webhook_secret = secrets.token_urlsafe(32)
        webhook.version += 1
        await self.session.flush()
        return webhook

    async def delete(self, webhook_id: str) -> bool:
        """Delete a webhook."""
        webhook = await self.get_by_id(webhook_id)
        if not webhook:
            return False
        await self.session.delete(webhook)
        await self.session.flush()
        return True

    async def check_rate_limit(
        self,
        webhook_id: str,
    ) -> tuple[bool, int]:
        """Check if webhook is within rate limit. Returns (allowed, remaining)."""
        webhook = await self.get_by_id(webhook_id)
        if not webhook:
            return False, 0

        now = datetime.now(UTC)

        # Reset window if needed
        if webhook.last_rate_limit_reset is None or now - webhook.last_rate_limit_reset > timedelta(minutes=1):
            webhook.last_rate_limit_reset = now
            webhook.requests_in_window = 0

        remaining = webhook.rate_limit_per_minute - webhook.requests_in_window
        allowed = remaining > 0

        if allowed:
            webhook.requests_in_window += 1

        await self.session.flush()
        return allowed, max(0, remaining - 1)

    async def record_request(
        self,
        webhook_id: str,
        success: bool,
        error_message: str | None = None,
    ) -> None:
        """Record a webhook request for statistics."""
        webhook = await self.get_by_id(webhook_id)
        if not webhook:
            return

        now = datetime.now(UTC)
        webhook.total_requests += 1
        webhook.last_request_at = now

        if success:
            webhook.successful_requests += 1
            webhook.last_success_at = now
        else:
            webhook.failed_requests += 1
            webhook.last_failure_at = now
            webhook.last_error_message = error_message

        await self.session.flush()

    async def create_log(
        self,
        webhook_id: str,
        event_type: str | None = None,
        http_method: str = "POST",
        source_ip: str | None = None,
        user_agent: str | None = None,
        request_headers: dict[str, Any] | None = None,
        request_body_preview: str | None = None,
        payload_size_bytes: int | None = None,
        success: bool = False,
        status_code: int = 200,
        error_message: str | None = None,
        processing_time_ms: int | None = None,
        test_run_id: str | None = None,
        results_submitted: int = 0,
    ) -> WebhookLog:
        """Create a webhook log entry."""
        log = WebhookLog(
            id=str(uuid.uuid4()),
            webhook_id=webhook_id,
            request_id=str(uuid.uuid4()),
            event_type=event_type,
            http_method=http_method,
            source_ip=source_ip,
            user_agent=user_agent,
            request_headers=request_headers,
            request_body_preview=request_body_preview,
            payload_size_bytes=payload_size_bytes,
            success=success,
            status_code=status_code,
            error_message=error_message,
            processing_time_ms=processing_time_ms,
            test_run_id=test_run_id,
            results_submitted=results_submitted,
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def get_logs(
        self,
        webhook_id: str,
        success: bool | None = None,
        event_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[WebhookLog], int]:
        """Get webhook logs with filtering."""
        query = select(WebhookLog).where(WebhookLog.webhook_id == webhook_id)

        if success is not None:
            query = query.where(WebhookLog.success == success)
        if event_type:
            query = query.where(WebhookLog.event_type == event_type)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        query = query.order_by(WebhookLog.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    async def get_stats(self, project_id: str) -> dict[str, Any]:
        """Get webhook statistics for a project."""
        # Total webhooks
        total_result = await self.session.execute(
            select(func.count()).where(WebhookIntegration.project_id == project_id),
        )
        total = total_result.scalar() or 0

        # By status
        status_result = await self.session.execute(
            select(WebhookIntegration.status, func.count())
            .where(WebhookIntegration.project_id == project_id)
            .group_by(WebhookIntegration.status),
        )
        by_status = {str(row[0].value): row[1] for row in status_result}

        # By provider
        provider_result = await self.session.execute(
            select(WebhookIntegration.provider, func.count())
            .where(WebhookIntegration.project_id == project_id)
            .group_by(WebhookIntegration.provider),
        )
        by_provider = {str(row[0].value): row[1] for row in provider_result}

        # Total requests
        requests_result = await self.session.execute(
            select(
                func.sum(WebhookIntegration.total_requests),
                func.sum(WebhookIntegration.successful_requests),
                func.sum(WebhookIntegration.failed_requests),
            ).where(WebhookIntegration.project_id == project_id),
        )
        requests_row = requests_result.one()

        return {
            "project_id": project_id,
            "total": total,
            "by_status": by_status,
            "by_provider": by_provider,
            "total_requests": requests_row[0] or 0,
            "successful_requests": requests_row[1] or 0,
            "failed_requests": requests_row[2] or 0,
        }
