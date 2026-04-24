"""Pydantic schemas for Test Suite API."""

from datetime import datetime

from pydantic import BaseModel, Field


class TestSuiteTestCaseCreate(BaseModel):
    """Schema for adding a test case to a suite."""

    test_case_id: str
    order_index: int = 0
    is_mandatory: bool = True
    skip_reason: str | None = None
    custom_parameters: dict[str, object] | None = None


class TestSuiteTestCaseResponse(BaseModel):
    """Response schema for suite test case association."""

    id: str
    suite_id: str
    test_case_id: str
    order_index: int
    is_mandatory: bool
    skip_reason: str | None
    custom_parameters: dict[str, object] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestSuiteCreate(BaseModel):
    """Schema for creating a test suite."""

    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    objective: str | None = Field(None, max_length=2000)
    parent_id: str | None = None
    order_index: int = 0
    category: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    is_parallel_execution: bool = False
    estimated_duration_minutes: int | None = Field(None, ge=1)
    required_environment: str | None = Field(None, max_length=255)
    environment_variables: dict[str, str] | None = None
    setup_instructions: str | None = None
    teardown_instructions: str | None = None
    owner: str | None = Field(None, max_length=255)
    responsible_team: str | None = Field(None, max_length=255)
    metadata: dict[str, object] | None = None


class TestSuiteUpdate(BaseModel):
    """Schema for updating a test suite."""

    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    objective: str | None = Field(None, max_length=2000)
    parent_id: str | None = None
    order_index: int | None = None
    category: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    is_parallel_execution: bool | None = None
    estimated_duration_minutes: int | None = Field(None, ge=1)
    required_environment: str | None = Field(None, max_length=255)
    environment_variables: dict[str, str] | None = None
    setup_instructions: str | None = None
    teardown_instructions: str | None = None
    owner: str | None = Field(None, max_length=255)
    responsible_team: str | None = Field(None, max_length=255)
    metadata: dict[str, object] | None = None


class TestSuiteResponse(BaseModel):
    """Response schema for a test suite."""

    id: str
    suite_number: str
    project_id: str
    name: str
    description: str | None
    objective: str | None
    status: str
    parent_id: str | None
    order_index: int
    category: str | None
    tags: list[str] | None
    is_parallel_execution: bool
    estimated_duration_minutes: int | None
    required_environment: str | None
    environment_variables: dict[str, str] | None
    setup_instructions: str | None
    teardown_instructions: str | None
    owner: str | None
    responsible_team: str | None
    total_test_cases: int
    automated_count: int
    last_run_at: datetime | None
    last_run_result: str | None
    pass_rate: float | None
    metadata: dict[str, object] | None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestSuiteListResponse(BaseModel):
    """Response schema for listing test suites."""

    test_suites: list[TestSuiteResponse]
    total: int


class TestSuiteStatusTransition(BaseModel):
    """Schema for transitioning suite status."""

    new_status: str = Field(..., pattern="^(draft|active|deprecated|archived)$")
    reason: str | None = None


class TestSuiteActivityResponse(BaseModel):
    """Response schema for suite activity log entry."""

    id: str
    suite_id: str
    activity_type: str
    from_value: str | None
    to_value: str | None
    description: str | None
    performed_by: str | None
    metadata: dict[str, object] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TestSuiteActivitiesResponse(BaseModel):
    """Response schema for suite activities list."""

    suite_id: str
    activities: list[TestSuiteActivityResponse]


class TestSuiteStats(BaseModel):
    """Statistics for test suites in a project."""

    project_id: str
    total: int
    by_status: dict[str, int]
    by_category: dict[str, int]
    total_test_cases: int
    automated_test_cases: int
