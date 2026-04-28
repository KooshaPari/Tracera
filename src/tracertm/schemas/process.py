"""Process schemas for TraceRTM."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


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


class ProcessStage(BaseModel):
    """Schema for a process stage."""

    id: str
    name: str
    description: str | None = None
    order: int
    required: bool = True
    estimated_duration_minutes: int | None = None
    assigned_role: str | None = None


class ProcessSwimlane(BaseModel):
    """Schema for a process swimlane (actor/role)."""

    id: str
    name: str
    role: str | None = None
    description: str | None = None


class ProcessInput(BaseModel):
    """Schema for a process input."""

    name: str
    type: str  # document, data, approval, etc.
    required: bool = True
    description: str | None = None


class ProcessOutput(BaseModel):
    """Schema for a process output."""

    name: str
    type: str
    description: str | None = None


class ProcessTrigger(BaseModel):
    """Schema for what initiates a process."""

    type: str  # event, schedule, manual, condition
    name: str
    description: str | None = None
    condition: str | None = None


class ProcessCreate(BaseModel):
    """Schema for creating a process."""

    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    purpose: str | None = None

    # Classification
    category: ProcessCategory | None = None
    tags: list[str] | None = None

    # Definition
    stages: list[ProcessStage] | None = None
    swimlanes: list[ProcessSwimlane] | None = None
    inputs: list[ProcessInput] | None = None
    outputs: list[ProcessOutput] | None = None
    triggers: list[ProcessTrigger] | None = None
    exit_criteria: list[str] | None = None

    # BPMN
    bpmn_xml: str | None = None

    # Ownership
    owner: str | None = None
    responsible_team: str | None = None

    # Metrics
    expected_duration_hours: int | None = None
    sla_hours: int | None = None

    # Related
    related_process_ids: list[str] | None = None

    # Metadata
    metadata: dict[str, object] = Field(default_factory=dict)


class ProcessUpdate(BaseModel):
    """Schema for updating a process."""

    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    purpose: str | None = None

    # Classification
    category: ProcessCategory | None = None
    tags: list[str] | None = None

    # Definition
    stages: list[ProcessStage] | None = None
    swimlanes: list[ProcessSwimlane] | None = None
    inputs: list[ProcessInput] | None = None
    outputs: list[ProcessOutput] | None = None
    triggers: list[ProcessTrigger] | None = None
    exit_criteria: list[str] | None = None

    # BPMN
    bpmn_xml: str | None = None

    # Ownership
    owner: str | None = None
    responsible_team: str | None = None

    # Metrics
    expected_duration_hours: int | None = None
    sla_hours: int | None = None

    # Related
    related_process_ids: list[str] | None = None

    # Metadata
    metadata: dict[str, object] | None = None


class ProcessVersionCreate(BaseModel):
    """Schema for creating a new version of a process."""

    version_notes: str | None = None
    changes: dict[str, object] | None = Field(None, description="Specific changes to apply to create new version")


class ProcessActivation(BaseModel):
    """Schema for activating a process version."""

    activated_by: str | None = None
    notes: str | None = None


class ProcessDeprecation(BaseModel):
    """Schema for deprecating a process."""

    deprecated_by: str | None = None
    deprecation_reason: str | None = None
    replacement_process_id: str | None = None


class ProcessResponse(BaseModel):
    """Schema for process response."""

    id: str
    process_number: str
    project_id: str
    name: str
    description: str | None
    purpose: str | None

    # Status
    status: str

    # Classification
    category: str | None
    tags: list[str] | None

    # Versioning
    version_number: int
    is_active_version: bool
    parent_version_id: str | None
    version_notes: str | None

    # Definition
    stages: list[dict[str, object]] | None
    swimlanes: list[dict[str, object]] | None
    inputs: list[dict[str, object]] | None
    outputs: list[dict[str, object]] | None
    triggers: list[dict[str, object]] | None
    exit_criteria: list[str] | None

    # BPMN
    bpmn_xml: str | None
    bpmn_diagram_url: str | None

    # Ownership
    owner: str | None
    responsible_team: str | None

    # Metrics
    expected_duration_hours: int | None
    sla_hours: int | None

    # Activation/Deprecation
    activated_at: datetime | None
    activated_by: str | None
    deprecated_at: datetime | None
    deprecated_by: str | None
    deprecation_reason: str | None

    # Related
    related_process_ids: list[str] | None

    # Metadata
    metadata: dict[str, object]
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ProcessListResponse(BaseModel):
    """Schema for process list item (condensed)."""

    id: str
    process_number: str
    project_id: str
    name: str
    status: str
    category: str | None
    owner: str | None
    version_number: int
    is_active_version: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Process Execution schemas


class ExecutionStatus(StrEnum):
    """Valid execution statuses."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessExecutionCreate(BaseModel):
    """Schema for starting a process execution."""

    process_id: str
    initiated_by: str | None = None
    trigger_item_id: str | None = None
    context_data: dict[str, object] = Field(default_factory=dict)


class ProcessExecutionUpdate(BaseModel):
    """Schema for updating a process execution."""

    current_stage_id: str | None = None
    context_data: dict[str, object] | None = None


class ProcessExecutionComplete(BaseModel):
    """Schema for completing a process execution."""

    completed_by: str | None = None
    result_summary: str | None = None
    output_item_ids: list[str] | None = None


class ProcessExecutionResponse(BaseModel):
    """Schema for process execution response."""

    id: str
    process_id: str
    execution_number: str
    status: str
    current_stage_id: str | None
    completed_stages: list[str] | None
    started_at: datetime | None
    completed_at: datetime | None
    initiated_by: str | None
    completed_by: str | None
    trigger_item_id: str | None
    context_data: dict[str, object]
    result_summary: str | None
    output_item_ids: list[str] | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
