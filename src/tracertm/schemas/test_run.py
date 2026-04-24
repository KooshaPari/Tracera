"""Pydantic schemas for Test Run API."""

from datetime import datetime

from pydantic import BaseModel, Field


class TestResultCreate(BaseModel):
    """Schema for creating/submitting a test result."""

    test_case_id: str
    status: str = Field(..., pattern="^(passed|failed|skipped|blocked|error)$")
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: int | None = Field(None, ge=0)
    executed_by: str | None = Field(None, max_length=255)
    actual_result: str | None = None
    failure_reason: str | None = None
    error_message: str | None = None
    stack_trace: str | None = None
    screenshots: list[str] | None = None
    logs_url: str | None = Field(None, max_length=1000)
    attachments: list[dict[str, object]] | None = None
    step_results: list[dict[str, object]] | None = None
    linked_defect_ids: list[str] | None = None
    created_defect_id: str | None = None
    retry_count: int = 0
    is_flaky: bool = False
    notes: str | None = None
    metadata: dict[str, object] | None = None


class TestResultResponse(BaseModel):
    """Response schema for a test result."""

    id: str
    run_id: str
    test_case_id: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: int | None
    executed_by: str | None
    actual_result: str | None
    failure_reason: str | None
    error_message: str | None
    stack_trace: str | None
    screenshots: list[str] | None
    logs_url: str | None
    attachments: list[dict[str, object]] | None
    step_results: list[dict[str, object]] | None
    linked_defect_ids: list[str] | None
    created_defect_id: str | None
    retry_count: int
    is_flaky: bool
    notes: str | None
    metadata: dict[str, object] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestRunCreate(BaseModel):
    """Schema for creating a test run."""

    name: str = Field(..., min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    suite_id: str | None = None
    run_type: str = Field(default="manual", pattern="^(manual|automated|ci_cd|scheduled)$")
    environment: str | None = Field(None, max_length=255)
    build_number: str | None = Field(None, max_length=255)
    build_url: str | None = Field(None, max_length=1000)
    branch: str | None = Field(None, max_length=255)
    commit_sha: str | None = Field(None, max_length=64)
    scheduled_at: datetime | None = None
    initiated_by: str | None = Field(None, max_length=255)
    tags: list[str] | None = None
    external_run_id: str | None = Field(None, max_length=255)
    webhook_id: str | None = None
    metadata: dict[str, object] | None = None
    # Optionally include test case IDs to include in this run
    test_case_ids: list[str] | None = None


class TestRunUpdate(BaseModel):
    """Schema for updating a test run."""

    name: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = Field(None, max_length=5000)
    environment: str | None = Field(None, max_length=255)
    build_number: str | None = Field(None, max_length=255)
    build_url: str | None = Field(None, max_length=1000)
    branch: str | None = Field(None, max_length=255)
    commit_sha: str | None = Field(None, max_length=64)
    notes: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, object] | None = None


class TestRunResponse(BaseModel):
    """Response schema for a test run."""

    id: str
    run_number: str
    project_id: str
    suite_id: str | None
    name: str
    description: str | None
    status: str
    run_type: str
    environment: str | None
    build_number: str | None
    build_url: str | None
    branch: str | None
    commit_sha: str | None
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: int | None
    initiated_by: str | None
    executed_by: str | None
    total_tests: int
    passed_count: int
    failed_count: int
    skipped_count: int
    blocked_count: int
    error_count: int
    pass_rate: float | None
    notes: str | None
    failure_summary: str | None
    tags: list[str] | None
    external_run_id: str | None
    webhook_id: str | None
    metadata: dict[str, object] | None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestRunListResponse(BaseModel):
    """Response schema for listing test runs."""

    test_runs: list[TestRunResponse]
    total: int


class TestRunStart(BaseModel):
    """Schema for starting a test run."""

    executed_by: str | None = Field(None, max_length=255)


class TestRunComplete(BaseModel):
    """Schema for completing a test run."""

    status: str | None = Field(None, pattern="^(passed|failed|blocked|cancelled)$")
    notes: str | None = None
    failure_summary: str | None = None


class BulkTestResultsSubmit(BaseModel):
    """Schema for submitting multiple test results at once."""

    results: list[TestResultCreate]


class TestRunActivityResponse(BaseModel):
    """Response schema for run activity log entry."""

    id: str
    run_id: str
    activity_type: str
    from_value: str | None
    to_value: str | None
    description: str | None
    performed_by: str | None
    metadata: dict[str, object] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TestRunActivitiesResponse(BaseModel):
    """Response schema for run activities list."""

    run_id: str
    activities: list[TestRunActivityResponse]


class TestRunStats(BaseModel):
    """Statistics for test runs in a project."""

    project_id: str
    total_runs: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    by_environment: dict[str, int]
    average_duration_seconds: float | None
    average_pass_rate: float | None
    recent_runs: list[TestRunResponse]
