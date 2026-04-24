"""External integration models for GitHub, Linear, and GitHub Projects."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


class IntegrationProvider(StrEnum):
    """Supported external integration providers."""

    GITHUB = "github"
    GITHUB_PROJECTS = "github_projects"
    LINEAR = "linear"


class CredentialType(StrEnum):
    """Type of credential stored."""

    OAUTH_TOKEN = "oauth_token"
    PAT = "personal_access_token"
    GITHUB_APP = "github_app"


class CredentialStatus(StrEnum):
    """Status of a credential."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    INVALID = "invalid"


class MappingDirection(StrEnum):
    """Sync direction for mappings."""

    BIDIRECTIONAL = "bidirectional"
    TRACERTM_TO_EXTERNAL = "tracertm_to_external"
    EXTERNAL_TO_TRACERTM = "external_to_tracertm"


class MappingStatus(StrEnum):
    """Status of a mapping."""

    ACTIVE = "active"
    PAUSED = "paused"
    SYNC_ERROR = "sync_error"


class SyncEventType(StrEnum):
    """Types of sync events."""

    ITEM_CREATED = "item_created"
    ITEM_UPDATED = "item_updated"
    ITEM_DELETED = "item_deleted"
    STATUS_CHANGED = "status_changed"
    LINKED = "linked"
    UNLINKED = "unlinked"


class SyncDirection(StrEnum):
    """Direction of sync."""

    PUSH = "push"  # TraceRTM -> External
    PULL = "pull"  # External -> TraceRTM


class SyncPriority(StrEnum):
    """Priority of sync event."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class SyncQueueStatus(StrEnum):
    """Status of sync queue item."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRIED = "retried"


class ConflictResolutionStrategy(StrEnum):
    """Conflict resolution strategy."""

    MANUAL = "manual"
    TRACERTM_WINS = "tracertm_wins"
    EXTERNAL_WINS = "external_wins"
    LAST_WRITE_WINS = "last_write_wins"


class ConflictResolutionStatus(StrEnum):
    """Status of conflict resolution."""

    PENDING = "pending"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class IntegrationCredential(Base, TimestampMixin):
    """Secure storage of external integration credentials."""

    __tablename__ = "integration_credentials"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    account_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    project_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
    )
    github_app_installation_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("github_app_installations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    linear_app_installation_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("linear_app_installations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Credential metadata
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    credential_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Authentication details (encrypted)
    encrypted_token: Mapped[str] = mapped_column(String(1024), nullable=False)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # OAuth scope tracking
    scopes: Mapped[list[object]] = mapped_column(JSONType, default=list, nullable=False)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    # Validation tracking
    last_validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validation_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Provider-specific metadata
    provider_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, default=dict, nullable=False)
    provider_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Rotation tracking
    created_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rotation_required_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    mappings: Mapped[list["IntegrationMapping"]] = relationship(
        "IntegrationMapping",
        back_populates="credential",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_integration_credentials_account_provider", "account_id", "provider"),
        Index("ix_integration_credentials_project_provider", "project_id", "provider"),
        Index("ix_integration_credentials_created_by_user", "created_by_user_id"),
        Index("ix_integration_credentials_status", "status"),
        Index("ix_integration_credentials_expires", "token_expires_at"),
    )


class IntegrationMapping(Base, TimestampMixin):
    """Maps TraceRTM items to external system identifiers."""

    __tablename__ = "integration_mappings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    integration_credential_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integration_credentials.id", ondelete="CASCADE"),
        nullable=False,
    )

    # TraceRTM side
    tracertm_item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
    )
    tracertm_item_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # External side
    external_system: Mapped[str] = mapped_column(String(100), nullable=False)
    external_id: Mapped[str] = mapped_column(String(500), nullable=False)
    external_url: Mapped[str] = mapped_column(String(2000), nullable=False)

    # Mapping metadata
    mapping_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, default=dict, nullable=False)

    # Sync configuration
    direction: Mapped[str] = mapped_column(String(50), default="bidirectional", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    auto_sync: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Sync tracking
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_direction: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sync_error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Conflict tracking
    last_conflict_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    conflict_resolution_strategy: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)
    field_resolution_rules: Mapped[dict[str, object]] = mapped_column(JSONType, default=dict, nullable=False)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    credential: Mapped["IntegrationCredential"] = relationship("IntegrationCredential", back_populates="mappings")
    sync_queue_items: Mapped[list["IntegrationSyncQueue"]] = relationship(
        "IntegrationSyncQueue",
        back_populates="mapping",
        cascade="all, delete-orphan",
    )
    sync_logs: Mapped[list["IntegrationSyncLog"]] = relationship(
        "IntegrationSyncLog",
        back_populates="mapping",
        cascade="all, delete-orphan",
    )
    conflicts: Mapped[list["IntegrationConflict"]] = relationship(
        "IntegrationConflict",
        back_populates="mapping",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("project_id", "external_id", name="uc_mapping_external"),
        Index("ix_integration_mappings_credential", "integration_credential_id"),
        Index("ix_integration_mappings_item", "tracertm_item_id"),
        Index("ix_integration_mappings_external_id", "external_id"),
        Index("ix_integration_mappings_status", "status"),
        Index("ix_integration_mappings_last_sync", "last_sync_at"),
    )


class IntegrationSyncQueue(Base, TimestampMixin):
    """Queue for pending sync operations."""

    __tablename__ = "integration_sync_queue"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    integration_credential_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integration_credentials.id", ondelete="CASCADE"),
        nullable=False,
    )
    mapping_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integration_mappings.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Event details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    direction: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(50), default="normal", nullable=False)

    # Payload
    payload: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False)

    # Processing state
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Idempotency
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Processing tracking
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    mapping: Mapped["IntegrationMapping"] = relationship("IntegrationMapping", back_populates="sync_queue_items")
    sync_logs: Mapped[list["IntegrationSyncLog"]] = relationship("IntegrationSyncLog", back_populates="sync_queue_item")

    __table_args__ = (
        UniqueConstraint("mapping_id", "idempotency_key", name="uc_idempotency"),
        Index("ix_sync_queue_credential_status", "integration_credential_id", "status"),
        Index("ix_sync_queue_mapping", "mapping_id"),
        Index("ix_sync_queue_priority_status", "priority", "status"),
        Index("ix_sync_queue_retry", "status", "next_retry_at"),
        Index("ix_sync_queue_created", "created_at"),
    )


class IntegrationSyncLog(Base):
    """Audit log for all sync operations."""

    __tablename__ = "integration_sync_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sync_queue_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("integration_sync_queue.id", ondelete="SET NULL"),
        nullable=True,
    )
    mapping_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integration_mappings.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Operation details
    operation: Mapped[str] = mapped_column(String(50), nullable=False)
    direction: Mapped[str] = mapped_column(String(50), nullable=False)

    # Source and target
    source_system: Mapped[str] = mapped_column(String(100), nullable=False)
    source_id: Mapped[str] = mapped_column(String(255), nullable=False)
    target_system: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Changes
    changes: Mapped[dict[str, object]] = mapped_column(JSONType, default=dict, nullable=False)

    # Result
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # Metadata
    sync_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, default=dict, nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    sync_queue_item: Mapped[Optional["IntegrationSyncQueue"]] = relationship(
        "IntegrationSyncQueue",
        back_populates="sync_logs",
    )
    mapping: Mapped["IntegrationMapping"] = relationship("IntegrationMapping", back_populates="sync_logs")

    __table_args__ = (
        Index("ix_sync_log_mapping", "mapping_id"),
        Index("ix_sync_log_queue", "sync_queue_id"),
        Index("ix_sync_log_success", "success"),
        Index("ix_sync_log_created", "created_at"),
        Index("ix_sync_log_operation", "operation"),
    )


class IntegrationConflict(Base):
    """Detected sync conflicts awaiting resolution."""

    __tablename__ = "integration_conflicts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    mapping_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integration_mappings.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Conflict details
    field: Mapped[str] = mapped_column(String(100), nullable=False)
    tracertm_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_value: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Resolution
    resolution_status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    resolved_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution_strategy_used: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Timestamps
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    mapping: Mapped["IntegrationMapping"] = relationship("IntegrationMapping", back_populates="conflicts")

    __table_args__ = (
        Index("ix_integration_conflicts_mapping", "mapping_id"),
        Index("ix_integration_conflicts_status", "resolution_status"),
        Index("ix_integration_conflicts_detected", "detected_at"),
    )


class IntegrationRateLimit(Base, TimestampMixin):
    """Track rate limit usage per credential."""

    __tablename__ = "integration_rate_limits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    integration_credential_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("integration_credentials.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Provider rate limit info
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    api_endpoint: Mapped[str] = mapped_column(String(255), nullable=False)

    # Current usage in window
    requests_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    requests_limit: Mapped[int] = mapped_column(Integer, nullable=False)

    # Window management
    window_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Backoff info
    is_rate_limited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    backoff_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("integration_credential_id", "api_endpoint", name="uc_credential_endpoint"),
        Index("ix_rate_limits_backoff", "backoff_until"),
    )
