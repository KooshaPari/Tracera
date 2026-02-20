"""Process model for TraceRTM.

Represents high-level processes that define workflows, procedures,
and operational patterns. Supports versioning and BPMN visualization.
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from tracertm.models.base import Base, TimestampMixin
from tracertm.models.types import JSONType


def generate_process_uuid() -> str:
    """Generate a UUID string for process ID."""
    return str(uuid.uuid4())


class ProcessStatus(StrEnum):
    """Valid process lifecycle statuses."""

    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"
    ARCHIVED = "archived"


class ProcessCategory(StrEnum):
    """Categories of processes."""

    OPERATIONAL = "operational"
    SUPPORT = "support"
    MANAGEMENT = "management"
    DEVELOPMENT = "development"
    INTEGRATION = "integration"
    COMPLIANCE = "compliance"
    OTHER = "other"


class Process(Base, TimestampMixin):
    """Process model representing a defined workflow or procedure.

    Processes have a lifecycle from Draft through Active to eventual
    retirement. They support:
    - Version control for process definitions
    - BPMN diagram storage
    - Swimlane definitions
    - Stage-based workflows
    - Links to items they trigger or manage
    """

    __tablename__ = "processes"

    __table_args__ = (
        Index("idx_processes_project_status", "project_id", "status"),
        Index("idx_processes_project_category", "project_id", "category"),
        Index("idx_processes_is_active", "is_active_version"),
        Index("idx_processes_owner", "owner"),
        {"extend_existing": True},
    )

    # Core Identification
    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_process_uuid)
    process_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Lifecycle Status
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=ProcessStatus.DRAFT.value, index=True)

    # Classification
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    tags: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # Versioning
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active_version: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    parent_version_id: Mapped[str | None] = mapped_column(
        String(255),
        ForeignKey("processes.id", ondelete="SET NULL"),
        nullable=True,
    )
    version_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Process Definition
    stages: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)
    """
    Stages define the sequential steps in the process.
    Example: [
        {"id": "1", "name": "Initiate", "description": "...", "order": 1},
        {"id": "2", "name": "Review", "description": "...", "order": 2},
        {"id": "3", "name": "Approve", "description": "...", "order": 3}
    ]
    """

    swimlanes: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)
    """
    Swimlanes define the actors/roles involved in the process.
    Example: [
        {"id": "1", "name": "Requester", "role": "user"},
        {"id": "2", "name": "Approver", "role": "manager"},
        {"id": "3", "name": "Executor", "role": "engineer"}
    ]
    """

    # BPMN Support
    bpmn_xml: Mapped[str | None] = mapped_column(Text, nullable=True)
    """BPMN 2.0 XML definition for visual process diagrams."""

    bpmn_diagram_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    """URL to rendered BPMN diagram image."""

    # Inputs/Outputs
    inputs: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)
    """
    Expected inputs to the process.
    Example: [{"name": "Request Form", "type": "document", "required": true}]
    """

    outputs: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)
    """
    Expected outputs from the process.
    Example: [{"name": "Approval Record", "type": "document"}]
    """

    # Triggers and Conditions
    triggers: Mapped[list[dict[str, object]] | None] = mapped_column(JSONType, nullable=True)
    """
    What initiates this process.
    Example: [{"type": "event", "name": "New Request Submitted"}]
    """

    exit_criteria: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    """Conditions that must be met to complete the process."""

    # Ownership
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    responsible_team: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Metrics
    expected_duration_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sla_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Activation/Deactivation
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    activated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    deprecated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deprecated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    deprecation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Related entities
    related_process_ids: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)
    """IDs of related/dependent processes."""

    # Flexible metadata
    process_metadata: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)

    # Optimistic locking
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Soft delete
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    __mapper_args__ = {  # noqa: RUF012
        "version_id_col": version,
    }

    def __init__(self, **kwargs: object) -> None:
        """Initialize Process instance.

        Handles metadata field aliasing for backward compatibility.

        Args:
            **kwargs: Keyword arguments for model fields.
        """
        # Map friendly aliases
        if "metadata" in kwargs and "process_metadata" not in kwargs:
            kwargs["process_metadata"] = kwargs.pop("metadata")
        super().__init__(**kwargs)

    def __getattribute__(self, name: str) -> object:
        """__getattribute__ implementation."""
        if name == "metadata":
            return object.__getattribute__(self, "process_metadata")
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        """__setattr__ implementation."""
        if name == "metadata":
            name = "process_metadata"
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<Process(id={self.id!r}, number={self.process_number!r}, name={self.name!r})>"


class ProcessExecution(Base, TimestampMixin):
    """Tracks individual executions/instances of a process.

    Each time a process is initiated, an execution record is created
    to track its progress through the stages.
    """

    __tablename__ = "process_executions"

    __table_args__ = (
        Index("idx_process_executions_process_id", "process_id"),
        Index("idx_process_executions_status", "status"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_process_uuid)
    process_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("processes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    execution_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )  # pending, in_progress, completed, failed, cancelled

    # Progress
    current_stage_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    completed_stages: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Actors
    initiated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    completed_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Context
    trigger_item_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    """ID of the item that triggered this execution."""

    context_data: Mapped[dict[str, object]] = mapped_column(JSONType, nullable=False, default=dict)
    """Execution-specific context and data."""

    # Output
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_item_ids: Mapped[list[str] | None] = mapped_column(JSONType, nullable=True)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<ProcessExecution(id={self.id!r}, number={self.execution_number!r})>"
