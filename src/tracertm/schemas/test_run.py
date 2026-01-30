"""
Pydantic schemas for Test Run API.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class TestResultCreate(BaseModel):
    """Schema for creating/submitting a test result."""

    test_case_id: str
    status: str = Field(..., pattern="^(passed|failed|skipped|blocked|error)$")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = Field(None, ge=0)
    executed_by: Optional[str] = Field(None, max_length=255)
    actual_result: Optional[str] = None
    failure_reason: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    screenshots: Optional[list[str]] = None
    logs_url: Optional[str] = Field(None, max_length=1000)
    attachments: Optional[list[dict[str, Any]]] = None
    step_results: Optional[list[dict[str, Any]]] = None
    linked_defect_ids: Optional[list[str]] = None
    created_defect_id: Optional[str] = None
    retry_count: int = 0
    is_flaky: bool = False
    notes: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class TestResultResponse(BaseModel):
    """Response schema for a test result."""

    id: str
    run_id: str
    test_case_id: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    executed_by: Optional[str]
    actual_result: Optional[str]
    failure_reason: Optional[str]
    error_message: Optional[str]
    stack_trace: Optional[str]
    screenshots: Optional[list[str]]
    logs_url: Optional[str]
    attachments: Optional[list[dict[str, Any]]]
    step_results: Optional[list[dict[str, Any]]]
    linked_defect_ids: Optional[list[str]]
    created_defect_id: Optional[str]
    retry_count: int
    is_flaky: bool
    notes: Optional[str]
    metadata: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestRunCreate(BaseModel):
    """Schema for creating a test run."""

    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    suite_id: Optional[str] = None
    run_type: str = Field(default="manual", pattern="^(manual|automated|ci_cd|scheduled)$")
    environment: Optional[str] = Field(None, max_length=255)
    build_number: Optional[str] = Field(None, max_length=255)
    build_url: Optional[str] = Field(None, max_length=1000)
    branch: Optional[str] = Field(None, max_length=255)
    commit_sha: Optional[str] = Field(None, max_length=64)
    scheduled_at: Optional[datetime] = None
    initiated_by: Optional[str] = Field(None, max_length=255)
    tags: Optional[list[str]] = None
    external_run_id: Optional[str] = Field(None, max_length=255)
    webhook_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    # Optionally include test case IDs to include in this run
    test_case_ids: Optional[list[str]] = None


class TestRunUpdate(BaseModel):
    """Schema for updating a test run."""

    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=5000)
    environment: Optional[str] = Field(None, max_length=255)
    build_number: Optional[str] = Field(None, max_length=255)
    build_url: Optional[str] = Field(None, max_length=1000)
    branch: Optional[str] = Field(None, max_length=255)
    commit_sha: Optional[str] = Field(None, max_length=64)
    notes: Optional[str] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None


class TestRunResponse(BaseModel):
    """Response schema for a test run."""

    id: str
    run_number: str
    project_id: str
    suite_id: Optional[str]
    name: str
    description: Optional[str]
    status: str
    run_type: str
    environment: Optional[str]
    build_number: Optional[str]
    build_url: Optional[str]
    branch: Optional[str]
    commit_sha: Optional[str]
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    initiated_by: Optional[str]
    executed_by: Optional[str]
    total_tests: int
    passed_count: int
    failed_count: int
    skipped_count: int
    blocked_count: int
    error_count: int
    pass_rate: Optional[float]
    notes: Optional[str]
    failure_summary: Optional[str]
    tags: Optional[list[str]]
    external_run_id: Optional[str]
    webhook_id: Optional[str]
    metadata: Optional[dict[str, Any]]
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

    executed_by: Optional[str] = Field(None, max_length=255)


class TestRunComplete(BaseModel):
    """Schema for completing a test run."""

    status: Optional[str] = Field(
        None, pattern="^(passed|failed|blocked|cancelled)$"
    )
    notes: Optional[str] = None
    failure_summary: Optional[str] = None


class BulkTestResultsSubmit(BaseModel):
    """Schema for submitting multiple test results at once."""

    results: list[TestResultCreate]


class TestRunActivityResponse(BaseModel):
    """Response schema for run activity log entry."""

    id: str
    run_id: str
    activity_type: str
    from_value: Optional[str]
    to_value: Optional[str]
    description: Optional[str]
    performed_by: Optional[str]
    metadata: Optional[dict[str, Any]]
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
    average_duration_seconds: Optional[float]
    average_pass_rate: Optional[float]
    recent_runs: list[TestRunResponse]
