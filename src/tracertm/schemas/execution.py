"""Pydantic schemas for Execution API.

Covers executions, artifacts, codex agent interactions, and environment config.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# === Execution Schemas ===


class ExecutionCreate(BaseModel):
    """Schema for creating an execution."""

    execution_type: str = Field(..., pattern="^(vhs|playwright|codex|custom)$", description="Type of execution")
    trigger_source: str = Field(
        default="manual",
        pattern="^(github_pr|github_push|webhook|manual)$",
        description="What triggered this execution",
    )
    trigger_ref: str | None = Field(None, max_length=255, description="PR number, commit SHA, etc.")
    test_run_id: str | None = Field(None, description="Associated test run")
    item_id: str | None = Field(None, description="Associated graph node/item")
    config: dict[str, object] | None = Field(None, description="Execution configuration")
    container_image: str | None = Field(None, max_length=255, description="Docker image override")


class ExecutionUpdate(BaseModel):
    """Schema for updating an execution."""

    status: str | None = Field(None, pattern="^(pending|running|passed|failed|cancelled)$")
    error_message: str | None = None
    output_summary: str | None = None


class ExecutionResponse(BaseModel):
    """Response schema for an execution."""

    id: str
    project_id: str
    test_run_id: str | None
    item_id: str | None
    execution_type: str
    trigger_source: str
    trigger_ref: str | None
    status: str
    container_id: str | None
    container_image: str | None
    config: dict[str, object] | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    exit_code: int | None
    error_message: str | None
    output_summary: str | None
    created_at: datetime
    updated_at: datetime

    # Computed fields
    artifact_count: int = 0

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ExecutionListResponse(BaseModel):
    """Response schema for listing executions."""

    executions: list[ExecutionResponse]
    total: int


class ExecutionStart(BaseModel):
    """Schema for starting an execution."""

    container_id: str | None = Field(None, max_length=64)


class ExecutionComplete(BaseModel):
    """Schema for completing an execution."""

    status: str = Field(..., pattern="^(passed|failed|cancelled)$")
    exit_code: int | None = None
    error_message: str | None = None
    output_summary: str | None = None
    duration_ms: int | None = Field(None, ge=0)


# === Execution Artifact Schemas ===


class ExecutionArtifactCreate(BaseModel):
    """Schema for creating an execution artifact."""

    artifact_type: str = Field(
        ...,
        pattern="^(screenshot|video|gif|log|trace|tape)$",
        description="Type of artifact",
    )
    file_path: str = Field(..., max_length=500, description="Local filesystem path")
    thumbnail_path: str | None = Field(None, max_length=500)
    item_id: str | None = Field(None, description="Associated graph node/item")
    file_size: int | None = Field(None, ge=0)
    mime_type: str | None = Field(None, max_length=100)
    metadata: dict[str, object] | None = Field(None, description="Dimensions, duration, etc.")
    captured_at: datetime | None = Field(None, description="When artifact was captured")


class ExecutionArtifactResponse(BaseModel):
    """Response schema for an execution artifact."""

    id: str
    execution_id: str
    item_id: str | None
    artifact_type: str
    file_path: str
    thumbnail_path: str | None
    file_size: int | None
    mime_type: str | None
    metadata: dict[str, object] | None
    captured_at: datetime
    created_at: datetime

    # Computed URL for frontend
    url: str | None = None
    thumbnail_url: str | None = None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ExecutionArtifactListResponse(BaseModel):
    """Response schema for listing artifacts."""

    artifacts: list[ExecutionArtifactResponse]
    total: int


# === Codex Agent Interaction Schemas ===


class CodexAgentTaskCreate(BaseModel):
    """Schema for creating a Codex agent task."""

    task_type: str = Field(
        ...,
        pattern="^(review_image|review_video|code_review|generate_test|analyze_logs)$",
        description="Type of AI task",
    )
    execution_id: str | None = Field(None, description="Associated execution")
    artifact_id: str | None = Field(None, description="Artifact to analyze")
    prompt: str | None = Field(None, description="Custom prompt for the task")
    input_data: dict[str, object] | None = Field(None, description="Additional input")


class CodexAgentTaskResponse(BaseModel):
    """Response schema for a Codex agent task."""

    id: str
    project_id: str
    execution_id: str | None
    artifact_id: str | None
    task_type: str
    status: str
    prompt: str | None
    response: str | None
    input_data: dict[str, object] | None
    output_data: dict[str, object] | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    tokens_used: int | None
    model_used: str | None
    error_message: str | None
    retry_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class CodexAgentTaskListResponse(BaseModel):
    """Response schema for listing Codex tasks."""

    tasks: list[CodexAgentTaskResponse]
    total: int


# === Execution Environment Config Schemas ===


class ExecutionEnvironmentConfigCreate(BaseModel):
    """Schema for creating/updating environment config."""

    # Docker settings
    docker_image: str = Field(default="node:20-alpine", max_length=255)
    resource_limits: dict[str, object] | None = Field(None, description="CPU, memory limits")
    working_directory: str | None = Field(None, max_length=500)
    network_mode: str = Field(default="bridge", pattern="^(bridge|host|none)$")

    # Feature toggles
    vhs_enabled: bool = True
    playwright_enabled: bool = True
    codex_enabled: bool = True
    auto_screenshot: bool = True
    auto_video: bool = False

    # VHS settings
    vhs_theme: str = Field(default="Dracula", max_length=100)
    vhs_font_size: int = Field(default=14, ge=8, le=72)
    vhs_width: int = Field(default=1200, ge=320, le=3840)
    vhs_height: int = Field(default=600, ge=240, le=2160)
    vhs_framerate: int = Field(default=30, ge=10, le=60)

    # Playwright settings
    playwright_browser: str = Field(default="chromium", pattern="^(chromium|firefox|webkit)$")
    playwright_headless: bool = True
    playwright_viewport_width: int = Field(default=1280, ge=320, le=3840)
    playwright_viewport_height: int = Field(default=720, ge=240, le=2160)
    playwright_video_size: dict[str, object] | None = None

    # Codex settings
    codex_sandbox_mode: str = Field(
        default="workspace-write",
        pattern="^(read-only|workspace-write|danger-full-access)$",
    )
    codex_full_auto: bool = False
    codex_timeout: int = Field(default=300, ge=30, le=1800)

    # Storage settings
    artifact_retention_days: int = Field(default=30, ge=1, le=365)
    storage_path: str | None = Field(None, max_length=500)
    max_artifact_size_mb: int = Field(default=100, ge=1, le=1000)

    # Execution limits
    max_concurrent_executions: int = Field(default=3, ge=1, le=10)
    execution_timeout: int = Field(default=600, ge=60, le=3600)


class ExecutionEnvironmentConfigUpdate(BaseModel):
    """Schema for partially updating environment config."""

    docker_image: str | None = Field(None, max_length=255)
    resource_limits: dict[str, object] | None = None
    working_directory: str | None = Field(None, max_length=500)
    network_mode: str | None = Field(None, pattern="^(bridge|host|none)$")

    vhs_enabled: bool | None = None
    playwright_enabled: bool | None = None
    codex_enabled: bool | None = None
    auto_screenshot: bool | None = None
    auto_video: bool | None = None

    vhs_theme: str | None = Field(None, max_length=100)
    vhs_font_size: int | None = Field(None, ge=8, le=72)
    vhs_width: int | None = Field(None, ge=320, le=3840)
    vhs_height: int | None = Field(None, ge=240, le=2160)
    vhs_framerate: int | None = Field(None, ge=10, le=60)

    playwright_browser: str | None = Field(None, pattern="^(chromium|firefox|webkit)$")
    playwright_headless: bool | None = None
    playwright_viewport_width: int | None = Field(None, ge=320, le=3840)
    playwright_viewport_height: int | None = Field(None, ge=240, le=2160)
    playwright_video_size: dict[str, object] | None = None

    codex_sandbox_mode: str | None = Field(None, pattern="^(read-only|workspace-write|danger-full-access)$")
    codex_full_auto: bool | None = None
    codex_timeout: int | None = Field(None, ge=30, le=1800)

    artifact_retention_days: int | None = Field(None, ge=1, le=365)
    storage_path: str | None = Field(None, max_length=500)
    max_artifact_size_mb: int | None = Field(None, ge=1, le=1000)

    max_concurrent_executions: int | None = Field(None, ge=1, le=10)
    execution_timeout: int | None = Field(None, ge=60, le=3600)


class ExecutionEnvironmentConfigResponse(BaseModel):
    """Response schema for environment config."""

    id: str
    project_id: str

    docker_image: str
    resource_limits: dict[str, object] | None
    working_directory: str | None
    network_mode: str

    vhs_enabled: bool
    playwright_enabled: bool
    codex_enabled: bool
    auto_screenshot: bool
    auto_video: bool

    vhs_theme: str
    vhs_font_size: int
    vhs_width: int
    vhs_height: int
    vhs_framerate: int

    playwright_browser: str
    playwright_headless: bool
    playwright_viewport_width: int
    playwright_viewport_height: int
    playwright_video_size: dict[str, object] | None

    codex_sandbox_mode: str
    codex_full_auto: bool
    codex_timeout: int

    artifact_retention_days: int
    storage_path: str | None
    max_artifact_size_mb: int

    max_concurrent_executions: int
    execution_timeout: int

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# === VHS Tape Schemas ===


class VHSTapeGenerateRequest(BaseModel):
    """Request schema for generating a VHS tape file."""

    commands: list[str] = Field(..., min_length=1, description="Shell commands to record")
    output_format: str = Field(default="gif", pattern="^(gif|mp4|webm)$")
    theme: str | None = Field(None, max_length=100)
    font_size: int | None = Field(None, ge=8, le=72)
    width: int | None = Field(None, ge=320, le=3840)
    height: int | None = Field(None, ge=240, le=2160)
    typing_speed: str | None = Field(None, pattern="^\\d+ms$", description="e.g., '50ms'")
    shell: str = Field(default="bash", pattern="^(bash|zsh|sh|fish)$")
    working_directory: str | None = Field(None, max_length=500)


class VHSTapeResponse(BaseModel):
    """Response schema for generated VHS tape."""

    tape_content: str = Field(..., description="Generated .tape file content")
    execution_id: str | None = None


# === Execution Stats ===


class ExecutionStats(BaseModel):
    """Statistics for executions in a project."""

    project_id: str
    total_executions: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    by_trigger: dict[str, int]
    average_duration_ms: float | None
    artifact_count: int
    total_artifact_size_bytes: int
    recent_executions: list[ExecutionResponse]
