"""
Webhook Integration model for CI/CD integration.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

import uuid as uuid_module
import secrets

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid_module.uuid4())


def generate_webhook_secret() -> str:
    """Generate a secure webhook secret."""
    return secrets.token_urlsafe(32)


class WebhookProvider(str, Enum):
    """Supported webhook providers."""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    AZURE_DEVOPS = "azure_devops"
    CIRCLECI = "circleci"
    TRAVIS_CI = "travis_ci"
    CUSTOM = "custom"


class WebhookStatus(str, Enum):
    """Status of a webhook integration."""
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class WebhookEventType(str, Enum):
    """Types of webhook events."""
    TEST_RUN_START = "test_run_start"
    TEST_RUN_COMPLETE = "test_run_complete"
    TEST_RESULT_SUBMIT = "test_result_submit"
    BULK_RESULTS = "bulk_results"


class WebhookIntegration(Base, TimestampMixin):
    """
    Webhook configuration for CI/CD integration.
    Allows external systems to submit test results.
    """

    __tablename__ = "webhook_integrations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Provider configuration
    provider: Mapped[WebhookProvider] = mapped_column(
        SQLEnum(WebhookProvider), nullable=False, default=WebhookProvider.CUSTOM
    )
    status: Mapped[WebhookStatus] = mapped_column(
        SQLEnum(WebhookStatus), nullable=False, default=WebhookStatus.ACTIVE
    )

    # Authentication
    webhook_secret: Mapped[str] = mapped_column(
        String(64), nullable=False, default=generate_webhook_secret
    )
    api_key: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    # Event configuration
    enabled_events: Mapped[Optional[list]] = mapped_column(JSONType, nullable=True)
    event_filters: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)

    # Target configuration (for outbound webhooks)
    callback_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    callback_headers: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)

    # Default mapping (which suite/run to associate results with)
    default_suite_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("test_suites.id", ondelete="SET NULL"), nullable=True
    )

    # Rate limiting
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    last_rate_limit_reset: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    requests_in_window: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Statistics
    total_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    successful_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_request_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_success_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_failure_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Settings
    auto_create_run: Mapped[bool] = mapped_column(Boolean, default=True)
    auto_complete_run: Mapped[bool] = mapped_column(Boolean, default=True)
    verify_signatures: Mapped[bool] = mapped_column(Boolean, default=True)

    # Extensible metadata
    webhook_metadata: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        Index("ix_webhook_integrations_project_id", "project_id"),
        Index("ix_webhook_integrations_provider", "provider"),
        Index("ix_webhook_integrations_status", "status"),
    )


class WebhookLog(Base):
    """Log of webhook requests for debugging and auditing."""

    __tablename__ = "webhook_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    webhook_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("webhook_integrations.id", ondelete="CASCADE"), nullable=False
    )

    # Request details
    request_id: Mapped[str] = mapped_column(String(36), nullable=False, default=generate_uuid)
    event_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    http_method: Mapped[str] = mapped_column(String(10), nullable=False, default="POST")
    source_ip: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Payload (truncated for large payloads)
    request_headers: Mapped[Optional[dict]] = mapped_column(JSONType, nullable=True)
    request_body_preview: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payload_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Processing result
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False, default=200)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Associated entities created/updated
    test_run_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    results_submitted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        Index("ix_webhook_logs_webhook_id", "webhook_id"),
        Index("ix_webhook_logs_created_at", "created_at"),
        Index("ix_webhook_logs_success", "success"),
        Index("ix_webhook_logs_event_type", "event_type"),
    )
