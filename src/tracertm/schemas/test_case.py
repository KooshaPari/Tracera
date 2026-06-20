"""Pydantic schemas for Test Case management."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TestCaseStatus(StrEnum):
    """Valid test case statuses."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class TestCaseType(StrEnum):
    """Types of test cases."""

    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    UNIT = "unit"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ACCESSIBILITY = "accessibility"
    REGRESSION = "regression"
    SMOKE = "smoke"
    EXPLORATORY = "exploratory"


class TestCasePriority(StrEnum):
    """Priority levels for test case execution order."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AutomationStatus(StrEnum):
    """Automation implementation status."""

    NOT_AUTOMATED = "not_automated"
    IN_PROGRESS = "in_progress"
    AUTOMATED = "automated"
    CANNOT_AUTOMATE = "cannot_automate"


class TestStep(BaseModel):
    """A single test step."""

    step_number: int = Field(..., ge=1)
    action: str = Field(..., min_length=1)
    expected_result: str | None = None
    test_data: str | None = None


class TestCaseCreate(BaseModel):
    """Schema for creating a test case."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    objective: str | None = None

    # Classification
    test_type: TestCaseType = TestCaseType.FUNCTIONAL
    priority: TestCasePriority = TestCasePriority.MEDIUM
    category: str | None = Field(None, max_length=100)
    tags: list[str] | None = None

    # Test Definition
    preconditions: str | None = None
    test_steps: list[TestStep] | None = None
    expected_result: str | None = None
    postconditions: str | None = None
    test_data: dict[str, object] | None = None

    # Automation
    automation_status: AutomationStatus = AutomationStatus.NOT_AUTOMATED
    automation_script_path: str | None = Field(None, max_length=500)
    automation_framework: str | None = Field(None, max_length=100)
    automation_notes: str | None = None

    # Estimates
    estimated_duration_minutes: int | None = Field(None, ge=1)

    # Assignment
    assigned_to: str | None = Field(None, max_length=255)

    # Flexible metadata
    metadata: dict[str, object] = Field(default_factory=dict)


class TestCaseUpdate(BaseModel):
    """Schema for updating a test case."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    objective: str | None = None

    # Classification (can't change status directly via update)
    test_type: TestCaseType | None = None
    priority: TestCasePriority | None = None
    category: str | None = None
    tags: list[str] | None = None

    # Test Definition
    preconditions: str | None = None
    test_steps: list[TestStep] | None = None
    expected_result: str | None = None
    postconditions: str | None = None
    test_data: dict[str, object] | None = None

    # Automation
    automation_status: AutomationStatus | None = None
    automation_script_path: str | None = None
    automation_framework: str | None = None
    automation_notes: str | None = None

    # Estimates
    estimated_duration_minutes: int | None = Field(None, ge=1)

    # Assignment
    assigned_to: str | None = None

    # Flexible metadata
    metadata: dict[str, object] | None = None


class TestCaseResponse(BaseModel):
    """Schema for test case response."""

    id: str
    test_case_number: str
    project_id: str
    title: str
    description: str | None = None
    objective: str | None = None
    status: str
    test_type: str
    priority: str
    category: str | None = None
    tags: list[str] | None = None

    # Test Definition
    preconditions: str | None = None
    test_steps: list[dict[str, object]] | None = None
    expected_result: str | None = None
    postconditions: str | None = None
    test_data: dict[str, object] | None = None

    # Automation
    automation_status: str
    automation_script_path: str | None = None
    automation_framework: str | None = None
    automation_notes: str | None = None

    # Estimates
    estimated_duration_minutes: int | None = None

    # Assignment
    created_by: str | None = None
    assigned_to: str | None = None
    reviewed_by: str | None = None
    approved_by: str | None = None

    # Dates
    reviewed_at: datetime | None = None
    approved_at: datetime | None = None
    deprecated_at: datetime | None = None
    deprecation_reason: str | None = None

    # Execution history
    last_executed_at: datetime | None = None
    last_execution_result: str | None = None
    total_executions: int = 0
    pass_count: int = 0
    fail_count: int = 0

    # Metadata
    metadata: dict[str, object]
    version: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TestCaseListResponse(BaseModel):
    """Schema for list of test cases response."""

    total: int
    test_cases: list[TestCaseResponse]


class TestCaseStatusTransition(BaseModel):
    """Schema for transitioning test case status."""

    new_status: TestCaseStatus
    reason: str | None = None
    performed_by: str | None = None


class TestCaseReview(BaseModel):
    """Schema for submitting a test case for review or recording review result."""

    reviewer: str = Field(..., min_length=1, max_length=255)
    notes: str | None = None
    approved: bool = False


class TestCaseDeprecation(BaseModel):
    """Schema for deprecating a test case."""

    reason: str = Field(..., min_length=1)
    deprecated_by: str | None = None
    replacement_test_case_id: str | None = None


class TestCaseActivityResponse(BaseModel):
    """Schema for test case activity response."""

    id: str
    test_case_id: str
    activity_type: str
    from_value: str | None = None
    to_value: str | None = None
    description: str | None = None
    performed_by: str | None = None
    metadata: dict[str, object]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TestCaseStats(BaseModel):
    """Schema for test case statistics."""

    project_id: str
    total: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    by_priority: dict[str, int]
    by_automation_status: dict[str, int]
    execution_summary: dict[str, int]  # total_runs, total_passed, total_failed
