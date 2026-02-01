# Execution Environment Integration - Technical Design Document

**Version:** 1.0
**Date:** 2026-01-28
**Status:** Design Phase
**Author:** Planning Architect

---

## Executive Summary

This document provides a comprehensive technical design for integrating execution environments into the TraceRTM system. The integration enables:

1. **Sandboxed Execution** - Docker-based environments mirroring codebase state
2. **Multimedia Capture** - VHS (CLI demos), Playwright (web UI), FFmpeg (video processing)
3. **Codex CLI Agent Integration** - OAuth-driven autonomous task execution and review
4. **Local Storage** - SQLite metadata + filesystem artifacts (no cloud dependencies)
5. **Webhook-Triggered Workflows** - Seamless execution triggered from external systems

The design extends the existing webhook and integration infrastructure while maintaining security, performance, and user control.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Design Principles](#core-design-principles)
3. [Execution Environment Architecture](#execution-environment-architecture)
4. [Database Schema Extensions](#database-schema-extensions)
5. [Service Layer Interfaces](#service-layer-interfaces)
6. [VHS Integration](#vhs-integration)
7. [Playwright Integration](#playwright-integration)
8. [FFmpeg Pipeline](#ffmpeg-pipeline)
9. [Codex CLI Agent Integration](#codex-cli-agent-integration)
10. [Storage Architecture](#storage-architecture)
11. [OAuth Credential Flow](#oauth-credential-flow)
12. [Security & Isolation](#security--isolation)
13. [Implementation Roadmap](#implementation-roadmap)

---

## Architecture Overview

### System Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    TraceRTM Frontend                           │
│  (User triggers execution via UI or webhook)                   │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                              │
│  • Webhook Endpoints                                            │
│  • Execution API (POST /executions)                             │
│  • Results API (GET /executions/{id}/results)                   │
└──────────────────────────┬─────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────────────┐
│          Execution Environment Orchestrator                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │ Execution Queue  │  │ VHS Service      │  │ Codex Agent  │ │
│  │ Management       │  │ Coordinator      │  │ Dispatcher   │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└──────────┬───────────────────────────────────────────┬─────────┘
           │                                           │
           ▼                                           ▼
┌─────────────────────────────┐         ┌──────────────────────────┐
│  Docker Container Pool      │         │  Codex CLI Process Pool   │
│  ┌────────────────────────┐ │         │  ┌────────────────────┐  │
│  │ Container 1 (Sandbox)  │ │         │  │ Codex Agent 1      │  │
│  │ • Mounted codebase     │ │         │  │ • OAuth session    │  │
│  │ • Network isolation    │ │         │  │ • Task queue       │  │
│  │ • Resource limits      │ │         │  │ • Review capability│  │
│  └────────────────────────┘ │         │  └────────────────────┘  │
│  ┌────────────────────────┐ │         │  ┌────────────────────┐  │
│  │ Container 2 (Sandbox)  │ │         │  │ Codex Agent 2      │  │
│  └────────────────────────┘ │         │  └────────────────────┘  │
└──────────┬──────────────────┘         └─────────┬────────────────┘
           │                                      │
           ▼                                      ▼
┌─────────────────────────────┐         ┌──────────────────────────┐
│  Media Capture & Processing │         │  OAuth Manager           │
│  • VHS .tape generation     │         │  • Credential rotation   │
│  • Playwright screenshots   │         │  • Token refresh         │
│  • FFmpeg GIF conversion    │         │  • Scope validation      │
└──────────┬──────────────────┘         └──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│  Local Storage (No Cloud Dependencies)                          │
│  ┌─────────────────┐  ┌──────────────────────────────────────┐ │
│  │  SQLite DB      │  │  Filesystem Artifacts                │ │
│  │ • Executions    │  │  ~/artifacts/                        │ │
│  │ • Results       │  │  ├─ {project_id}/                   │ │
│  │ • Metadata      │  │  │  ├─ {exec_id}/                   │ │
│  │ • Logs          │  │  │  │  ├─ vhs/                       │ │
│  │ • Artifacts     │  │  │  │  ├─ playwright/                │ │
│  │ • Links         │  │  │  │  ├─ ffmpeg/                    │ │
│  │                 │  │  │  │  └─ logs.txt                   │ │
│  └─────────────────┘  │  └──────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Sequence

```
1. User Trigger / Webhook Event
   │
   ├─► Validation & Authorization
   │
   └─► Execution Queue Entry Created
       │
       ├─► Docker Container Spawned
       │   └─► Codebase Mounted
       │       └─► VHS Service Initialized
       │
       └─► Codex Agent Session Initialized
           └─► OAuth Token Validated
               └─► Task Queue Populated
                   │
                   ├─► Codex performs actions (with images/videos)
                   │
                   └─► Results stored to SQLite + Filesystem
                       │
                       └─► Artifacts linked to Execution node
```

---

## Core Design Principles

### 1. Security First
- **Sandboxing**: All execution in isolated Docker containers
- **Least Privilege**: Containers run as non-root, resource-limited
- **OAuth Only**: No API keys, use GitHub OAuth token (already in system)
- **Credential Isolation**: Secrets encrypted at rest, never logged
- **Network Segmentation**: Containers only access needed endpoints

### 2. Zero Cloud Dependencies
- **Local Storage Only**: SQLite + filesystem, no external storage services
- **Self-Contained**: All processing happens locally or in Docker
- **Configurable Paths**: Artifact storage location configurable via env vars
- **Cleanup Policies**: Automatic artifact expiration (configurable TTL)

### 3. Extensible Webhook Integration
- **Event-Driven**: Execution triggered by existing webhook system
- **No Polling**: Direct trigger → execution start
- **Audit Trail**: All executions logged to integration_sync_logs model
- **Conflict Resolution**: Uses existing conflict resolution strategies

### 4. Graceful Degradation
- **Codex Optional**: System works without Codex (manual execution)
- **Container Fallback**: Run commands directly if Docker unavailable
- **Retry Logic**: Automatic retries with exponential backoff
- **Partial Results**: Incomplete executions still save artifacts

### 5. Observability
- **Execution Logging**: Every step logged with timestamps
- **Media Artifacts**: All captures stored for review and analysis
- **Agent Decisions**: Codex reasoning/responses logged
- **Performance Metrics**: Execution time, resource usage tracked

---

## Execution Environment Architecture

### 3.1 Docker Container Specifications

#### Base Image Strategy

```dockerfile
# Multi-stage build approach
FROM python:3.12-slim AS executor-base

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    openssh-client \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create execution user (non-root)
RUN groupadd -r execuser && useradd -r -g execuser execuser

WORKDIR /workspace

# Copy only necessary parts of codebase
COPY --chown=execuser:execuser ./src ./src
COPY --chown=execuser:execuser ./pyproject.toml ./pyproject.toml
COPY --chown=execuser:execuser ./requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

USER execuser

# Healthcheck
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

ENTRYPOINT ["python", "-m", "tracertm"]
```

#### Container Configuration Template

```yaml
# docker-compose.execution.yml - Template for execution containers

version: '3.9'

services:
  executor-template:
    build:
      context: .
      dockerfile: Dockerfile.executor

    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

    # Network isolation
    networks:
      - execution-network

    # Volume mounts
    volumes:
      # Read-only codebase mount
      - /path/to/codebase:/workspace/codebase:ro

      # Execution scratch space
      - type: tmpfs
        target: /tmp/execution
        tmpfs:
          size: 1G

      # Artifact output
      - /path/to/artifacts:/workspace/artifacts:rw

    # Environment variables
    environment:
      # Execution context
      EXECUTION_ID: "${EXECUTION_ID}"
      PROJECT_ID: "${PROJECT_ID}"
      TASK_TYPE: "${TASK_TYPE}"

      # Logging
      LOG_LEVEL: "INFO"
      LOG_PATH: "/workspace/artifacts/execution.log"

      # Resource tracking
      MEMORY_LIMIT_MB: "4096"
      CPU_LIMIT: "2"
      TIMEOUT_SECONDS: "3600"

      # Security
      CODEX_OAUTH_TOKEN: "${CODEX_OAUTH_TOKEN}"
      GIT_OAUTH_TOKEN: "${GIT_OAUTH_TOKEN}"

    # Security options
    security_opt:
      - no-new-privileges:true

    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE

    # Read-only filesystem except for specific paths
    read_only_rootfs: true

    tmpfs:
      - /run
      - /var/run

networks:
  execution-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

#### Container Lifecycle Management

```python
class ContainerManager:
    """Manages Docker container lifecycle for executions."""

    async def create_execution_container(
        self,
        execution_id: str,
        project_id: str,
        task_config: ExecutionTask,
        codebase_path: str,
        artifact_path: str,
    ) -> dict:
        """
        Create and start an isolated execution container.

        Returns: {
            'container_id': str,
            'execution_id': str,
            'status': 'starting' | 'running' | 'failed',
            'logs_path': str,
            'artifacts_path': str,
        }
        """

    async def stream_logs(
        self,
        container_id: str,
    ) -> AsyncGenerator[str, None]:
        """Stream execution logs in real-time."""

    async def get_resource_usage(
        self,
        container_id: str,
    ) -> dict:
        """
        Get current resource usage.

        Returns: {
            'cpu_percent': float,
            'memory_mb': int,
            'memory_limit_mb': int,
            'io_read_bytes': int,
            'io_write_bytes': int,
        }
        """

    async def stop_container(
        self,
        container_id: str,
        timeout_seconds: int = 30,
        force: bool = False,
    ) -> bool:
        """Gracefully stop container, force kill if needed."""

    async def cleanup_container(
        self,
        container_id: str,
        remove_volumes: bool = True,
    ) -> bool:
        """Remove container and associated resources."""
```

### 3.2 Execution Environment Components

#### VHS Service Coordinator

```python
class VHSServiceCoordinator:
    """Coordinates CLI recording via VHS (charmbracelet/vhs)."""

    async def generate_tape_file(
        self,
        execution_id: str,
        commands: List[str],
        config: VHSConfig,
    ) -> str:
        """
        Generate a .tape file for VHS CLI recording.

        .tape file format:
        ```
        Output video.gif
        Set FontSize 14
        Set Width 1200
        Set Height 800

        Type "command1"
        Sleep 1
        Enter
        Sleep 2

        Type "command2"
        Sleep 1
        Enter
        Sleep 3
        ```
        """

    async def execute_tape(
        self,
        tape_path: str,
        output_dir: str,
        container_id: str,
    ) -> ExecutionResult:
        """
        Execute .tape file within container using VHS.

        Produces:
        - output.gif (animated GIF of terminal)
        - output.mp4 (video recording)
        - timing.log (command timing data)
        """

    async def generate_thumbnail(
        self,
        recording_path: str,
        output_path: str,
        timestamp_ms: int = 0,
    ) -> str:
        """Extract single frame from recording as thumbnail."""
```

#### Playwright Coordinator

```python
class PlaywrightCoordinator:
    """Coordinates browser UI recording via Playwright."""

    async def start_browser_session(
        self,
        execution_id: str,
        headless: bool = False,
    ) -> BrowserSession:
        """
        Start Playwright browser session with recording.

        Records:
        - Video of browser viewport
        - Screenshots at key moments
        - HAR (HTTP Archive) of network
        - Trace file for timeline debugging
        """

    async def execute_flow(
        self,
        session: BrowserSession,
        flow_steps: List[FlowStep],
    ) -> ExecutionResult:
        """
        Execute a sequence of flow steps.

        FlowStep: {
            'action': 'navigate' | 'click' | 'fill' | 'wait',
            'selector': str,
            'value': str,
            'screenshot_after': bool,
        }
        """

    async def capture_screenshot(
        self,
        session: BrowserSession,
        name: str,
    ) -> str:
        """Capture named screenshot at current state."""

    async def stop_session(
        self,
        session: BrowserSession,
    ) -> dict:
        """
        Stop recording and collect all artifacts.

        Returns: {
            'video_path': str,
            'screenshots': List[str],
            'trace_path': str,
            'har_path': str,
        }
        """
```

#### FFmpeg Pipeline Service

```python
class FFmpegPipelineService:
    """Handles video/GIF processing and thumbnail generation."""

    async def video_to_gif(
        self,
        video_path: str,
        output_path: str,
        config: GIFConversionConfig,
    ) -> str:
        """
        Convert video to animated GIF.

        Config: {
            'fps': int,              # Frames per second (default: 10)
            'scale': str,            # Scale filter (default: '800:-1')
            'duration_seconds': int, # Total duration (default: 30)
            'quality': 'low' | 'medium' | 'high',
        }

        Command template:
        ffmpeg -i {video} -vf "fps=10,scale=800:-1:flags=lanczos[p];
                [p]split[a][b];[a]palettegen[pal];[b][pal]paletteuse"
                {output.gif}
        """

    async def generate_thumbnail(
        self,
        media_path: str,
        output_path: str,
        timestamp: str = '00:00:01',
        width: int = 400,
    ) -> str:
        """
        Extract single frame as thumbnail.

        Command template:
        ffmpeg -ss {timestamp} -i {media} -vf "scale=400:-1"
               -frames:v 1 {output}
        """

    async def extract_frames(
        self,
        video_path: str,
        output_dir: str,
        fps: int = 1,
        max_frames: int = 100,
    ) -> List[str]:
        """Extract frames from video at regular intervals."""

    async def create_slideshow(
        self,
        images: List[str],
        output_path: str,
        fps: int = 2,
        duration_per_image: float = 2.0,
    ) -> str:
        """Create video slideshow from images."""
```

---

## Database Schema Extensions

### 4.1 New Models for Execution Environment

```python
from enum import Enum
from datetime import datetime
from sqlalchemy import (
    DateTime, Enum as SQLEnum, ForeignKey, Index,
    Integer, String, Text, Boolean, JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from tracertm.models.base import Base, TimestampMixin


class ExecutionType(str, Enum):
    """Types of executions."""
    VHS_RECORDING = "vhs_recording"
    PLAYWRIGHT_FLOW = "playwright_flow"
    CODEX_AGENT_TASK = "codex_agent_task"
    COMBINED_WORKFLOW = "combined_workflow"
    CUSTOM = "custom"


class ExecutionStatus(str, Enum):
    """Execution lifecycle states."""
    QUEUED = "queued"
    PREPARING = "preparing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ExecutionResult(str, Enum):
    """Execution outcome."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    VALIDATION_ERROR = "validation_error"


class Execution(Base, TimestampMixin):
    """
    Represents a single execution environment instance.

    Executions can be:
    - VHS CLI recordings
    - Playwright browser flows
    - Codex agent tasks
    - Combined workflows
    """

    __tablename__ = "executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )

    # Execution metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_type: Mapped[str] = mapped_column(
        SQLEnum(ExecutionType), nullable=False
    )

    # Triggering source
    triggered_by: Mapped[str] = mapped_column(
        String(50), nullable=False  # 'webhook', 'ui', 'api', 'scheduled'
    )
    webhook_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("webhook_integrations.id", ondelete="SET NULL"),
        nullable=True
    )

    # Execution context
    execution_config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Status tracking
    status: Mapped[str] = mapped_column(
        SQLEnum(ExecutionStatus), default=ExecutionStatus.QUEUED, nullable=False
    )
    result: Mapped[str | None] = mapped_column(
        SQLEnum(ExecutionResult), nullable=True
    )

    # Container/environment
    container_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    environment_variables: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Execution timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)

    # Resource tracking
    cpu_limit: Mapped[int] = mapped_column(Integer, default=2, nullable=False)  # cores
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=4096, nullable=False)
    peak_memory_mb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    peak_cpu_percent: Mapped[float | None] = mapped_column(nullable=True)

    # Artifact storage
    artifacts_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    logs_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_traceback: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    results: Mapped[list["ExecutionResult"]] = relationship(
        "ExecutionResult", back_populates="execution", cascade="all, delete-orphan"
    )
    artifacts: Mapped[list["ExecutionArtifact"]] = relationship(
        "ExecutionArtifact", back_populates="execution", cascade="all, delete-orphan"
    )
    agent_interactions: Mapped[list["CodexAgentInteraction"]] = relationship(
        "CodexAgentInteraction", back_populates="execution",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_execution_project_status", "project_id", "status"),
        Index("ix_execution_webhook", "webhook_id"),
        Index("ix_execution_type", "execution_type"),
        Index("ix_execution_created", "created_at"),
        Index("ix_execution_container", "container_id"),
    )


class ExecutionArtifact(Base, TimestampMixin):
    """
    Stores metadata about artifacts generated during execution.

    Examples:
    - GIF from VHS recording
    - Video from Playwright
    - Screenshot collection
    - FFmpeg output
    """

    __tablename__ = "execution_artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    execution_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False
    )

    # Artifact metadata
    artifact_type: Mapped[str] = mapped_column(
        String(50), nullable=False  # 'gif', 'video', 'screenshot', 'log', 'trace', etc
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Storage location
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Metadata
    artifact_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # Example metadata:
    # {
    #   'gif': {
    #     'fps': 10,
    #     'duration_seconds': 30,
    #     'width': 800,
    #     'height': 600,
    #     'frame_count': 300,
    #   },
    #   'video': {
    #     'codec': 'h264',
    #     'bitrate_kbps': 5000,
    #     'duration_seconds': 60,
    #   },
    #   'screenshot': {
    #     'timestamp_ms': 1000,
    #     'width': 1920,
    #     'height': 1080,
    #   }
    # }

    # Artifact validity
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    execution: Mapped["Execution"] = relationship(
        "Execution", back_populates="artifacts"
    )

    __table_args__ = (
        Index("ix_artifact_execution", "execution_id"),
        Index("ix_artifact_type", "artifact_type"),
        Index("ix_artifact_expires", "expires_at"),
    )


class CodexAgentInteraction(Base, TimestampMixin):
    """
    Tracks interactions with Codex CLI agent during execution.

    Captures:
    - Task assignments
    - Agent decisions and reasoning
    - Image/video reviews
    - Results and artifacts
    """

    __tablename__ = "codex_agent_interactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    execution_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False
    )

    # Interaction context
    interaction_type: Mapped[str] = mapped_column(
        String(50), nullable=False  # 'task_assigned', 'decision_made', 'review_completed', etc
    )
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Task/prompt
    task_prompt: Mapped[str] = mapped_column(Text, nullable=False)

    # Input context (images/videos for review)
    input_artifacts: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )  # List of ExecutionArtifact IDs

    # Agent response
    agent_response: Mapped[str] = mapped_column(Text, nullable=False)
    agent_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Result
    action_taken: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_artifacts: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )  # List of ExecutionArtifact IDs

    # Metadata
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    interaction_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    execution: Mapped["Execution"] = relationship(
        "Execution", back_populates="agent_interactions"
    )

    __table_args__ = (
        Index("ix_agent_interaction_execution", "execution_id"),
        Index("ix_agent_interaction_type", "interaction_type"),
        Index("ix_agent_interaction_sequence", "execution_id", "sequence_number"),
    )


class ExecutionEnvironmentConfig(Base, TimestampMixin):
    """
    Configurable settings for execution environments per project.
    """

    __tablename__ = "execution_environment_configs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"),
        unique=True, nullable=False
    )

    # Docker settings
    docker_image: Mapped[str] = mapped_column(
        String(255), default="tracertm-executor:latest", nullable=False
    )
    cpu_limit: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=4096, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=3600, nullable=False)

    # VHS settings
    vhs_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    vhs_fps: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    vhs_scale: Mapped[str] = mapped_column(String(50), default="800:-1", nullable=False)

    # Playwright settings
    playwright_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    playwright_headless: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    playwright_timeout_ms: Mapped[int] = mapped_column(Integer, default=30000, nullable=False)

    # Codex settings
    codex_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    codex_model: Mapped[str] = mapped_column(
        String(100), default="gpt-4-vision", nullable=False
    )
    codex_max_tokens: Mapped[int] = mapped_column(Integer, default=4096, nullable=False)

    # Artifact storage
    artifacts_retention_days: Mapped[int] = mapped_column(
        Integer, default=30, nullable=False
    )
    artifacts_path_prefix: Mapped[str] = mapped_column(
        String(1000), default="~/tracertm_artifacts", nullable=False
    )

    # Additional config
    environment_variables: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_env_config_project", "project_id"),
    )
```

### 4.2 Schema Migration

```python
# alembic/versions/018_add_execution_environment.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    """Create execution environment tables."""

    # ExecutionEnvironmentConfig table
    op.create_table(
        'execution_environment_configs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('project_id', sa.String(36), nullable=False),
        sa.Column('docker_image', sa.String(255), nullable=False),
        sa.Column('cpu_limit', sa.Integer(), nullable=False),
        sa.Column('memory_limit_mb', sa.Integer(), nullable=False),
        # ... (full schema)
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id'),
    )

    # Execution table
    op.create_table(
        'executions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('project_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        # ... (full schema)
    )

    # ExecutionArtifact table
    op.create_table(
        'execution_artifacts',
        # ... (full schema)
    )

    # CodexAgentInteraction table
    op.create_table(
        'codex_agent_interactions',
        # ... (full schema)
    )

    # Create indexes
    op.create_index('ix_execution_project_status', 'executions', ['project_id', 'status'])
    op.create_index('ix_artifact_execution', 'execution_artifacts', ['execution_id'])
    # ... (more indexes)


def downgrade():
    """Drop execution environment tables."""
    op.drop_table('codex_agent_interactions')
    op.drop_table('execution_artifacts')
    op.drop_table('executions')
    op.drop_table('execution_environment_configs')
```

---

## Service Layer Interfaces

### 5.1 Core Execution Service

```python
# src/tracertm/services/execution_service.py

from dataclasses import dataclass
from typing import AsyncGenerator, Optional
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.execution_repository import ExecutionRepository
from tracertm.repositories.artifact_repository import ArtifactRepository
from tracertm.models.execution import (
    Execution, ExecutionStatus, ExecutionResult,
    ExecutionType, ExecutionArtifact,
)


@dataclass
class ExecutionConfig:
    """Configuration for an execution."""
    execution_type: ExecutionType
    vhs_commands: Optional[list[str]] = None
    playwright_flow: Optional[dict] = None
    codex_tasks: Optional[list[str]] = None
    timeout_seconds: int = 3600
    cpu_limit: int = 2
    memory_limit_mb: int = 4096


class ExecutionService:
    """
    High-level service for managing execution environment lifecycle.

    Coordinates:
    - Container creation and teardown
    - VHS CLI recording
    - Playwright browser flows
    - Codex agent interactions
    - Artifact collection and storage
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.execution_repo = ExecutionRepository(session)
        self.artifact_repo = ArtifactRepository(session)
        self.container_manager = ContainerManager()
        self.vhs_coordinator = VHSServiceCoordinator()
        self.playwright_coordinator = PlaywrightCoordinator()
        self.codex_dispatcher = CodexAgentDispatcher()
        self.ffmpeg_service = FFmpegPipelineService()

    async def create_execution(
        self,
        project_id: str,
        name: str,
        config: ExecutionConfig,
        triggered_by: str = "api",
        webhook_id: Optional[str] = None,
    ) -> Execution:
        """
        Create a new execution record.

        Args:
            project_id: Target project
            name: Human-readable execution name
            config: Execution configuration
            triggered_by: 'webhook', 'ui', 'api', 'scheduled'
            webhook_id: If triggered by webhook, the webhook ID

        Returns:
            Created Execution model
        """
        execution_id = str(uuid.uuid4())

        execution = Execution(
            id=execution_id,
            project_id=project_id,
            name=name,
            description=None,
            execution_type=config.execution_type,
            triggered_by=triggered_by,
            webhook_id=webhook_id,
            execution_config=config.dict(),
            status=ExecutionStatus.QUEUED,
            timeout_seconds=config.timeout_seconds,
            cpu_limit=config.cpu_limit,
            memory_limit_mb=config.memory_limit_mb,
            environment_variables={},
        )

        await self.execution_repo.create(execution)
        return execution

    async def execute(
        self,
        execution_id: str,
        codebase_path: str,
    ) -> AsyncGenerator[dict, None]:
        """
        Execute an execution and stream status updates.

        Yields progress events:
        {
            'type': 'status_change' | 'log' | 'artifact' | 'error',
            'data': {...}
        }
        """
        execution = await self.execution_repo.get_by_id(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")

        try:
            # Mark as preparing
            execution.status = ExecutionStatus.PREPARING
            await self.execution_repo.update(execution)
            yield {'type': 'status_change', 'data': {'status': 'preparing'}}

            # Create execution container
            container_id = await self._create_container(
                execution, codebase_path
            )
            execution.container_id = container_id
            await self.execution_repo.update(execution)
            yield {'type': 'log', 'data': {'message': f'Container created: {container_id}'}}

            # Execute workflow based on type
            if execution.execution_type == ExecutionType.VHS_RECORDING:
                async for event in self._execute_vhs(execution):
                    yield event

            elif execution.execution_type == ExecutionType.PLAYWRIGHT_FLOW:
                async for event in self._execute_playwright(execution):
                    yield event

            elif execution.execution_type == ExecutionType.CODEX_AGENT_TASK:
                async for event in self._execute_codex_task(execution):
                    yield event

            elif execution.execution_type == ExecutionType.COMBINED_WORKFLOW:
                async for event in self._execute_combined(execution):
                    yield event

            # Mark as completed
            execution.status = ExecutionStatus.COMPLETED
            execution.result = ExecutionResult.SUCCESS
            execution.completed_at = datetime.utcnow()
            await self.execution_repo.update(execution)
            yield {'type': 'status_change', 'data': {'status': 'completed'}}

        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.result = ExecutionResult.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            await self.execution_repo.update(execution)
            yield {'type': 'error', 'data': {'error': str(e)}}

        finally:
            # Cleanup
            if execution.container_id:
                await self.container_manager.cleanup_container(
                    execution.container_id
                )

    async def _execute_vhs(
        self,
        execution: Execution,
    ) -> AsyncGenerator[dict, None]:
        """Execute VHS CLI recording."""
        config = ExecutionConfig(**execution.execution_config)

        # Generate .tape file
        tape_file = await self.vhs_coordinator.generate_tape_file(
            execution.id,
            config.vhs_commands,
            VHSConfig(fps=10, width=1200, height=800),
        )
        yield {
            'type': 'artifact',
            'data': {
                'artifact_type': 'tape',
                'name': f'{execution.id}_commands.tape',
                'file_path': tape_file,
            }
        }

        # Execute recording
        result = await self.vhs_coordinator.execute_tape(
            tape_file,
            execution.artifacts_path,
            execution.container_id,
        )

        # Store GIF artifact
        gif_artifact = ExecutionArtifact(
            id=str(uuid.uuid4()),
            execution_id=execution.id,
            artifact_type='gif',
            name=f'{execution.id}_recording.gif',
            file_path=result['gif_path'],
            file_size_bytes=result['gif_size'],
            mime_type='image/gif',
            artifact_metadata=result['metadata'],
        )
        await self.artifact_repo.create(gif_artifact)
        yield {'type': 'artifact', 'data': {'artifact_id': gif_artifact.id}}

        # Generate thumbnail
        thumbnail_path = f"{execution.artifacts_path}/thumbnail.png"
        await self.ffmpeg_service.generate_thumbnail(
            result['gif_path'],
            thumbnail_path,
        )

        thumbnail_artifact = ExecutionArtifact(
            id=str(uuid.uuid4()),
            execution_id=execution.id,
            artifact_type='thumbnail',
            name=f'{execution.id}_thumbnail.png',
            file_path=thumbnail_path,
            mime_type='image/png',
        )
        await self.artifact_repo.create(thumbnail_artifact)
        yield {'type': 'log', 'data': {'message': 'VHS recording completed'}}

    async def _execute_playwright(
        self,
        execution: Execution,
    ) -> AsyncGenerator[dict, None]:
        """Execute Playwright browser flow."""
        # Implementation similar to VHS
        pass

    async def _execute_codex_task(
        self,
        execution: Execution,
    ) -> AsyncGenerator[dict, None]:
        """Execute Codex agent task."""
        config = ExecutionConfig(**execution.execution_config)

        for task_prompt in config.codex_tasks or []:
            # Dispatch to Codex agent
            result = await self.codex_dispatcher.execute_task(
                execution.id,
                task_prompt,
            )
            yield {'type': 'log', 'data': {'message': result['reasoning']}}

        yield {'type': 'log', 'data': {'message': 'Codex tasks completed'}}

    async def _execute_combined(
        self,
        execution: Execution,
    ) -> AsyncGenerator[dict, None]:
        """Execute combined workflow (VHS + Playwright + Codex)."""
        pass

    async def _create_container(
        self,
        execution: Execution,
        codebase_path: str,
    ) -> str:
        """Create execution container."""
        artifact_path = (
            f"{execution.project_id}/{execution.id}/artifacts"
        )

        result = await self.container_manager.create_execution_container(
            execution_id=execution.id,
            project_id=execution.project_id,
            task_config=execution.execution_config,
            codebase_path=codebase_path,
            artifact_path=artifact_path,
        )

        execution.artifacts_path = result['artifacts_path']
        execution.logs_path = result['logs_path']

        return result['container_id']

    async def list_executions(
        self,
        project_id: str,
        limit: int = 50,
        offset: int = 0,
        status: Optional[ExecutionStatus] = None,
    ) -> tuple[list[Execution], int]:
        """List executions for a project."""
        return await self.execution_repo.list_by_project(
            project_id, limit, offset, status
        )

    async def get_execution(
        self,
        execution_id: str,
    ) -> Optional[Execution]:
        """Get execution by ID."""
        return await self.execution_repo.get_by_id(execution_id)

    async def get_execution_artifacts(
        self,
        execution_id: str,
    ) -> list[ExecutionArtifact]:
        """Get all artifacts for an execution."""
        return await self.artifact_repo.list_by_execution(execution_id)

    async def cleanup_old_artifacts(
        self,
        retention_days: int = 30,
    ) -> int:
        """
        Clean up old artifacts exceeding retention policy.

        Returns number of artifacts deleted.
        """
        deleted_count = await self.artifact_repo.delete_expired(
            retention_days=retention_days
        )
        return deleted_count
```

---

## VHS Integration

### 6.1 .Tape File Generation

```python
# src/tracertm/services/vhs_service.py

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class VHSConfig:
    """Configuration for VHS recordings."""
    fps: int = 10                    # Frames per second
    width: int = 1200                # Terminal width in pixels
    height: int = 800                # Terminal height in pixels
    font_size: int = 14              # Font size
    delay: float = 500               # Delay between commands (ms)


class VHSServiceCoordinator:
    """
    Generates and executes VHS tape files for CLI recording.

    VHS is a tool that records terminal sessions as GIFs or videos.
    It uses a .tape file format to script the recording.
    """

    async def generate_tape_file(
        self,
        execution_id: str,
        commands: List[str],
        config: VHSConfig,
        output_dir: str,
    ) -> str:
        """
        Generate a .tape file from a list of commands.

        VHS tape format:
        ```
        Output output.gif
        Set FontSize 14
        Set Width 1200
        Set Height 800

        Type "command1"
        Sleep 1
        Enter
        Sleep 2

        Type "command2"
        Sleep 1
        Enter
        Sleep 3
        ```

        Args:
            execution_id: Unique execution ID
            commands: List of shell commands to execute
            config: VHS configuration
            output_dir: Directory to save .tape file

        Returns:
            Path to generated .tape file
        """
        tape_lines = []

        # Header
        tape_lines.append(f"Output {output_dir}/output.gif")
        tape_lines.append(f"Output {output_dir}/output.mp4")
        tape_lines.append(f"Set FontSize {config.font_size}")
        tape_lines.append(f"Set Width {config.width}")
        tape_lines.append(f"Set Height {config.height}")
        tape_lines.append(f"Set Framerate {config.fps}")
        tape_lines.append("")

        # Commands
        for i, cmd in enumerate(commands):
            # Escape quotes in commands
            escaped_cmd = cmd.replace('"', '\\"')

            tape_lines.append(f"Type \"{escaped_cmd}\"")
            tape_lines.append("Sleep 0.5")
            tape_lines.append("Enter")

            # Variable delay based on command type
            if any(x in cmd for x in ['build', 'test', 'deploy']):
                delay = 5
            elif any(x in cmd for x in ['git', 'npm', 'docker']):
                delay = 3
            else:
                delay = 1

            tape_lines.append(f"Sleep {delay}")
            tape_lines.append("")

        # Write tape file
        tape_path = Path(output_dir) / f"{execution_id}.tape"
        tape_path.parent.mkdir(parents=True, exist_ok=True)
        tape_path.write_text("\n".join(tape_lines))

        return str(tape_path)

    async def execute_tape(
        self,
        tape_path: str,
        container_id: str,
    ) -> dict:
        """
        Execute a .tape file inside a Docker container using VHS.

        Returns: {
            'gif_path': str,
            'mp4_path': str,
            'gif_size': int,
            'duration_seconds': float,
            'metadata': dict,
        }
        """
        # Copy tape file to container
        # Execute: docker exec {container_id} vhs {tape_path}
        # Wait for completion
        # Copy output files back

        return {
            'gif_path': f'/artifacts/output.gif',
            'mp4_path': f'/artifacts/output.mp4',
            'gif_size': 5242880,  # Example: 5MB
            'duration_seconds': 45.5,
            'metadata': {
                'fps': 10,
                'frame_count': 455,
                'width': 1200,
                'height': 800,
            }
        }
```

### 6.2 Docker VHS Integration

```dockerfile
# Dockerfile.executor - Includes VHS

FROM python:3.12-slim AS executor-base

# Install VHS (charmbracelet/vhs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install VHS binary
RUN wget -q -O /tmp/vhs.tar.gz \
    https://github.com/charmbracelet/vhs/releases/download/v0.9.0/vhs-linux-amd64.tar.gz && \
    tar -xz -C /usr/local/bin -f /tmp/vhs.tar.gz && \
    rm /tmp/vhs.tar.gz && \
    chmod +x /usr/local/bin/vhs

# ... rest of Dockerfile
```

---

## Playwright Integration

### 7.1 Browser Automation Coordinator

```python
# src/tracertm/services/playwright_service.py

from typing import List, Optional, AsyncGenerator
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from playwright.async_api import async_playwright, Browser, Page, BrowserContext


class FlowActionType(str, Enum):
    """Types of flow actions."""
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    SCROLL = "scroll"
    HOVER = "hover"
    PRESS = "press"


@dataclass
class FlowStep:
    """Single step in a browser flow."""
    action: FlowActionType
    selector: Optional[str] = None
    value: Optional[str] = None
    timeout_ms: int = 30000
    screenshot_after: bool = False
    screenshot_name: Optional[str] = None


@dataclass
class BrowserSession:
    """Active browser session with recording."""
    id: str
    browser: Browser
    context: BrowserContext
    page: Page
    video_path: str
    trace_path: str
    har_path: str
    screenshots_dir: str


class PlaywrightCoordinator:
    """
    Coordinates browser automation with video/screenshot capture.

    Features:
    - Headless or headed browser
    - Video recording of viewport
    - Screenshot capture at key moments
    - HAR file for network analysis
    - Trace file for timeline debugging
    """

    async def start_browser_session(
        self,
        execution_id: str,
        output_dir: str,
        headless: bool = True,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
    ) -> BrowserSession:
        """
        Start a Playwright browser session with recording.

        Args:
            execution_id: Unique execution ID
            output_dir: Directory for artifacts
            headless: Run in headless mode
            viewport_width: Browser viewport width
            viewport_height: Browser viewport height

        Returns:
            Active BrowserSession for executing flows
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)

            # Create context with recording
            context = await browser.new_context(
                viewport={"width": viewport_width, "height": viewport_height},
                record_video_dir=output_dir,
                record_har_path=f"{output_dir}/network.har",
            )

            # Enable tracing
            await context.tracing.start(
                screenshots=True,
                snapshots=True,
                sources=True,
            )

            page = await context.new_page()

            return BrowserSession(
                id=execution_id,
                browser=browser,
                context=context,
                page=page,
                video_path=f"{output_dir}/video.webm",
                trace_path=f"{output_dir}/trace.zip",
                har_path=f"{output_dir}/network.har",
                screenshots_dir=output_dir,
            )

    async def execute_flow(
        self,
        session: BrowserSession,
        flow_steps: List[FlowStep],
    ) -> List[str]:
        """
        Execute a sequence of flow steps.

        Args:
            session: Active browser session
            flow_steps: Steps to execute

        Returns:
            List of screenshot paths
        """
        screenshot_paths = []

        for i, step in enumerate(flow_steps):
            if step.action == FlowActionType.NAVIGATE:
                await session.page.goto(step.value, timeout=step.timeout_ms)

            elif step.action == FlowActionType.CLICK:
                await session.page.click(step.selector, timeout=step.timeout_ms)

            elif step.action == FlowActionType.FILL:
                await session.page.fill(
                    step.selector, step.value, timeout=step.timeout_ms
                )

            elif step.action == FlowActionType.SELECT:
                await session.page.select_option(
                    step.selector, step.value, timeout=step.timeout_ms
                )

            elif step.action == FlowActionType.WAIT:
                await session.page.wait_for_timeout(step.timeout_ms)

            elif step.action == FlowActionType.SCROLL:
                await session.page.evaluate(f"window.scrollBy(0, {step.value})")

            elif step.action == FlowActionType.HOVER:
                await session.page.hover(step.selector, timeout=step.timeout_ms)

            elif step.action == FlowActionType.PRESS:
                await session.page.press(step.selector, step.value)

            # Screenshot if requested
            if step.screenshot_after or step.action == FlowActionType.SCREENSHOT:
                screenshot_name = (
                    step.screenshot_name or
                    f"step_{i:03d}_{step.action.value}"
                )
                screenshot_path = await self.capture_screenshot(
                    session, screenshot_name
                )
                screenshot_paths.append(screenshot_path)

        return screenshot_paths

    async def capture_screenshot(
        self,
        session: BrowserSession,
        name: str,
    ) -> str:
        """Capture screenshot at current state."""
        screenshot_path = f"{session.screenshots_dir}/{name}.png"
        await session.page.screenshot(path=screenshot_path, full_page=True)
        return screenshot_path

    async def stop_session(
        self,
        session: BrowserSession,
    ) -> dict:
        """
        Stop recording and collect all artifacts.

        Returns: {
            'video_path': str,
            'screenshots': List[str],
            'trace_path': str,
            'har_path': str,
            'duration_seconds': float,
        }
        """
        # Stop tracing
        await session.context.tracing.stop(
            path=session.trace_path
        )

        # Close context (finalizes video recording)
        await session.context.close()
        await session.browser.close()

        return {
            'video_path': session.video_path,
            'trace_path': session.trace_path,
            'har_path': session.har_path,
            'duration_seconds': 60.0,  # Would be calculated from actual recording
        }
```

---

## FFmpeg Pipeline

### 8.1 Video Processing Service

```python
# src/tracertm/services/ffmpeg_service.py

import asyncio
import subprocess
from pathlib import Path
from typing import Optional


class FFmpegPipelineService:
    """
    Handles video/GIF processing using FFmpeg.

    Pipeline Operations:
    - MP4 → Animated GIF
    - WebM → Animated GIF
    - Any video → Thumbnail
    - Image sequence → Video/GIF
    """

    async def video_to_gif(
        self,
        video_path: str,
        output_path: str,
        fps: int = 10,
        scale: str = "800:-1",
        duration_seconds: Optional[int] = None,
    ) -> str:
        """
        Convert video to animated GIF.

        Optimizes for:
        - File size
        - Quality
        - Animation smoothness

        FFmpeg command:
        ffmpeg -i input.mp4 \
          -vf "fps=10,scale=800:-1:flags=lanczos[p];
               [p]split[a][b];
               [a]palettegen[pal];
               [b][pal]paletteuse" \
          output.gif
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f"fps={fps},scale={scale}:flags=lanczos[p];[p]split[a][b];[a]palettegen[pal];[b][pal]paletteuse",
            '-y',  # Overwrite output
            output_path,
        ]

        if duration_seconds:
            cmd = cmd[:4] + ['-t', str(duration_seconds)] + cmd[4:]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=300,  # 5 minute timeout
            )

            if process.returncode != 0:
                raise RuntimeError(
                    f"FFmpeg failed: {stderr.decode()}"
                )

            return output_path

        except asyncio.TimeoutError:
            raise TimeoutError(f"Video to GIF conversion exceeded timeout")

    async def generate_thumbnail(
        self,
        media_path: str,
        output_path: str,
        timestamp: str = "00:00:01",
        width: int = 400,
    ) -> str:
        """
        Extract single frame as thumbnail.

        FFmpeg command:
        ffmpeg -ss 00:00:01 -i input.mp4 \
          -vf "scale=400:-1" \
          -frames:v 1 \
          output.png
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            'ffmpeg',
            '-ss', timestamp,
            '-i', media_path,
            '-vf', f"scale={width}:-1",
            '-frames:v', '1',
            '-y',
            output_path,
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=60,
            )

            if process.returncode != 0:
                raise RuntimeError(
                    f"Thumbnail generation failed: {stderr.decode()}"
                )

            return output_path

        except asyncio.TimeoutError:
            raise TimeoutError("Thumbnail generation exceeded timeout")

    async def extract_frames(
        self,
        video_path: str,
        output_pattern: str,
        fps: int = 1,
        max_frames: Optional[int] = None,
    ) -> list[str]:
        """
        Extract frames from video at regular intervals.

        FFmpeg command:
        ffmpeg -i input.mp4 \
          -vf "fps=1" \
          output_%03d.png
        """
        Path(output_pattern).parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f"fps={fps}",
            '-y',
            output_pattern,
        ]

        if max_frames:
            cmd = cmd[:4] + ['-frames:v', str(max_frames)] + cmd[4:]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(
                process.communicate(),
                timeout=300,
            )

            # Collect generated files
            output_dir = Path(output_pattern).parent
            pattern = Path(output_pattern).name
            frames = sorted(output_dir.glob(pattern.replace('%03d', '*')))

            return [str(f) for f in frames]

        except asyncio.TimeoutError:
            raise TimeoutError("Frame extraction exceeded timeout")

    async def create_slideshow(
        self,
        images: list[str],
        output_path: str,
        fps: int = 2,
        duration_per_image: float = 2.0,
    ) -> str:
        """
        Create video slideshow from images.

        FFmpeg command (using concat demuxer):
        ffmpeg -f concat -safe 0 -i filelist.txt \
          -vf "scale=1920:-1" \
          -c:v libx264 -pix_fmt yuv420p \
          output.mp4
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Create concat file list
        concat_file = f"{output_path}.concat"
        with open(concat_file, 'w') as f:
            for img in images:
                f.write(f"file '{img}'\n")
                f.write(f"duration {duration_per_image}\n")

        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-vf', 'scale=1920:-1',
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-y',
            output_path,
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(
                process.communicate(),
                timeout=300,
            )

            # Cleanup concat file
            Path(concat_file).unlink()

            return output_path

        except asyncio.TimeoutError:
            raise TimeoutError("Slideshow creation exceeded timeout")
```

---

## Codex CLI Agent Integration

### 9.1 Agent Dispatcher and Communication

```python
# src/tracertm/services/codex_agent_service.py

import asyncio
import json
import os
import subprocess
from typing import Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum


class CodexTaskType(str, Enum):
    """Types of tasks Codex can perform."""
    CODE_REVIEW = "code_review"
    IMAGE_ANALYSIS = "image_analysis"
    VIDEO_ANALYSIS = "video_analysis"
    TEST_EXECUTION = "test_execution"
    DOCUMENTATION = "documentation"
    AUTONOMOUS_ACTION = "autonomous_action"


@dataclass
class CodexTask:
    """Task for Codex agent."""
    type: CodexTaskType
    prompt: str
    input_files: list[str]  # Paths to images/videos
    context: dict = None


@dataclass
class CodexResponse:
    """Response from Codex agent."""
    task_id: str
    status: str  # 'success', 'partial', 'failed'
    reasoning: str
    action_taken: str
    output_files: list[str]
    tokens_used: int


class CodexAgentDispatcher:
    """
    Dispatches tasks to Codex CLI agent.

    Codex CLI is an OpenAI agent tool that:
    - Uses OAuth (not API keys)
    - Can review images and videos
    - Performs autonomous actions
    - Returns structured responses

    Integration pattern:
    1. Create OAuth session using GitHub token
    2. Prepare task with input files
    3. Call codex CLI with task prompt
    4. Parse JSON response
    5. Log interaction to database
    """

    def __init__(self, oauth_token: str):
        """
        Initialize dispatcher with OAuth token.

        Args:
            oauth_token: GitHub OAuth token (from integration_credentials)
        """
        self.oauth_token = oauth_token
        self.session_id = None

    async def authenticate(self) -> bool:
        """
        Authenticate with Codex using OAuth token.

        Codex CLI expects:
        - CODEX_AUTH_TOKEN environment variable
        - Or OAuth callback from GitHub
        """
        try:
            # Set token in environment
            os.environ['CODEX_AUTH_TOKEN'] = self.oauth_token

            # Test authentication
            result = await self._run_codex_command(
                ['codex', 'auth', 'verify']
            )

            return result.returncode == 0
        except Exception as e:
            raise RuntimeError(f"Codex authentication failed: {e}")

    async def dispatch_task(
        self,
        task: CodexTask,
        execution_id: str,
    ) -> AsyncGenerator[dict, None]:
        """
        Dispatch a task to Codex agent.

        Yields progress updates:
        {
            'type': 'status' | 'log' | 'reasoning' | 'action' | 'result',
            'data': {...}
        }
        """
        try:
            yield {
                'type': 'status',
                'data': {'message': f'Dispatching {task.type} task'}
            }

            # Prepare task input
            task_input = {
                'type': task.type.value,
                'prompt': task.prompt,
                'input_files': task.input_files,
                'context': task.context or {},
            }

            yield {
                'type': 'log',
                'data': {'message': f'Task prompt: {task.prompt}'}
            }

            # Call Codex CLI
            response = await self._call_codex(task_input)

            yield {
                'type': 'reasoning',
                'data': {'reasoning': response.reasoning}
            }

            yield {
                'type': 'action',
                'data': {'action': response.action_taken}
            }

            yield {
                'type': 'result',
                'data': {
                    'status': response.status,
                    'tokens_used': response.tokens_used,
                    'output_files': response.output_files,
                }
            }

        except Exception as e:
            yield {
                'type': 'error',
                'data': {'error': str(e)}
            }

    async def _call_codex(
        self,
        task_input: dict,
    ) -> CodexResponse:
        """
        Call Codex CLI with task input.

        Codex CLI command format:
        codex execute \
          --task-type code_review \
          --prompt "Review this code..." \
          --input-files image1.png,image2.png \
          --output-format json
        """
        # Build command
        cmd = [
            'codex', 'execute',
            '--task-type', task_input['type'],
            '--prompt', task_input['prompt'],
            '--output-format', 'json',
        ]

        if task_input['input_files']:
            cmd.extend([
                '--input-files',
                ','.join(task_input['input_files'])
            ])

        # Run Codex
        result = await self._run_codex_command(cmd)

        if result.returncode != 0:
            raise RuntimeError(
                f"Codex execution failed: {result.stderr.decode()}"
            )

        # Parse response
        response_data = json.loads(result.stdout.decode())

        return CodexResponse(
            task_id=response_data.get('task_id'),
            status=response_data.get('status'),
            reasoning=response_data.get('reasoning'),
            action_taken=response_data.get('action_taken'),
            output_files=response_data.get('output_files', []),
            tokens_used=response_data.get('tokens_used', 0),
        )

    async def _run_codex_command(
        self,
        cmd: list[str],
        timeout_seconds: int = 300,
    ) -> subprocess.CompletedProcess:
        """Run Codex CLI command."""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout_seconds,
            )

            return subprocess.CompletedProcess(
                cmd=cmd,
                returncode=process.returncode,
                stdout=stdout,
                stderr=stderr,
            )

        except asyncio.TimeoutError:
            raise TimeoutError(f"Codex command exceeded {timeout_seconds}s timeout")
```

---

## Storage Architecture

### 10.1 Local Filesystem Layout

```
~/tracertm_artifacts/  (or ARTIFACTS_PATH environment variable)
├── {project_id}/
│   ├── {execution_id}/
│   │   ├── vhs/
│   │   │   ├── {execution_id}.tape
│   │   │   ├── output.gif
│   │   │   ├── output.mp4
│   │   │   └── timing.log
│   │   ├── playwright/
│   │   │   ├── video.webm
│   │   │   ├── trace.zip
│   │   │   ├── network.har
│   │   │   ├── screenshots/
│   │   │   │   ├── step_001_navigate.png
│   │   │   │   ├── step_002_click.png
│   │   │   │   └── ...
│   │   │   └── thumbnail.png
│   │   ├── ffmpeg/
│   │   │   ├── input.mp4
│   │   │   ├── output.gif
│   │   │   ├── thumbnail.png
│   │   │   └── frames/
│   │   │       ├── frame_001.png
│   │   │       └── ...
│   │   ├── codex/
│   │   │   ├── task_001_review.json
│   │   │   ├── task_002_analysis.json
│   │   │   └── outputs/
│   │   │       └── ...
│   │   ├── logs/
│   │   │   └── execution.log
│   │   └── metadata.json
│   └── ...
├── cleanup.log  (Artifact cleanup history)
└── .gitkeep
```

### 10.2 Artifact Storage Service

```python
# src/tracertm/services/artifact_storage_service.py

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Optional


class ArtifactStorageService:
    """
    Manages local filesystem storage for execution artifacts.

    Features:
    - Configurable base path
    - Automatic cleanup based on retention policies
    - Atomic operations (fail-safe)
    - Disk usage tracking
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize storage service.

        Args:
            base_path: Root directory for artifacts (default: ~/tracertm_artifacts)
        """
        if base_path is None:
            base_path = os.path.expanduser("~/tracertm_artifacts")

        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def get_execution_path(
        self,
        project_id: str,
        execution_id: str,
    ) -> Path:
        """Get artifact directory for an execution."""
        path = self.base_path / project_id / execution_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_artifact_path(
        self,
        project_id: str,
        execution_id: str,
        artifact_type: str,  # 'vhs', 'playwright', 'ffmpeg', 'codex', 'logs'
        filename: str,
    ) -> Path:
        """Get specific artifact file path."""
        artifact_dir = self.get_execution_path(project_id, execution_id) / artifact_type
        artifact_dir.mkdir(parents=True, exist_ok=True)
        return artifact_dir / filename

    def store_artifact(
        self,
        source_path: str,
        project_id: str,
        execution_id: str,
        artifact_type: str,
        filename: str,
    ) -> Path:
        """
        Store artifact file and return destination path.

        Atomic operation: copies to temp location first, then moves.
        """
        dest_path = self.get_artifact_path(
            project_id, execution_id, artifact_type, filename
        )

        # Copy to destination
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, str(dest_path))

        return dest_path

    def cleanup_old_artifacts(
        self,
        retention_days: int = 30,
        max_total_size_gb: Optional[float] = None,
    ) -> dict:
        """
        Clean up old artifacts exceeding retention policy.

        Returns: {
            'deleted_files': int,
            'freed_bytes': int,
            'deleted_executions': int,
        }
        """
        deleted_files = 0
        freed_bytes = 0
        deleted_executions = 0
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        cleanup_log = self.base_path / "cleanup.log"

        for project_dir in self.base_path.iterdir():
            if project_dir.name == "cleanup.log":
                continue

            for exec_dir in project_dir.iterdir():
                exec_mtime = datetime.fromtimestamp(exec_dir.stat().st_mtime)

                if exec_mtime < cutoff_date:
                    # Delete execution directory
                    size = self._get_dir_size(exec_dir)
                    shutil.rmtree(exec_dir)

                    freed_bytes += size
                    deleted_executions += 1
                    deleted_files += len(list(exec_dir.rglob('*')))

                    # Log deletion
                    with open(cleanup_log, 'a') as f:
                        f.write(
                            f"{datetime.now().isoformat()} | "
                            f"Deleted {exec_dir} ({size} bytes)\n"
                        )

        return {
            'deleted_files': deleted_files,
            'freed_bytes': freed_bytes,
            'deleted_executions': deleted_executions,
        }

    def get_disk_usage(self) -> dict:
        """Get disk usage statistics."""
        total_size = self._get_dir_size(self.base_path)

        return {
            'total_bytes': total_size,
            'total_mb': total_size / (1024 ** 2),
            'total_gb': total_size / (1024 ** 3),
        }

    @staticmethod
    def _get_dir_size(path: Path) -> int:
        """Calculate total directory size."""
        total = 0
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
        return total
```

---

## OAuth Credential Flow

### 11.1 OAuth Integration with Codex

```python
# src/tracertm/services/codex_oauth_service.py

from datetime import datetime, timedelta
import jwt
import aiohttp
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.integration_repository import IntegrationRepository
from tracertm.models.integration import IntegrationCredential, CredentialStatus


class CodexOAuthService:
    """
    Manages OAuth credentials for Codex CLI agent.

    Integration with existing GitHub OAuth flow:
    1. User already authenticated with GitHub (for TraceRTM)
    2. Reuse existing GitHub OAuth token for Codex
    3. Request additional scopes if needed (agent-specific permissions)
    4. Manage token refresh and rotation
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.integration_repo = IntegrationRepository(session)

    async def get_codex_oauth_token(
        self,
        project_id: str,
        user_id: str,
    ) -> Optional[IntegrationCredential]:
        """
        Get or refresh Codex OAuth token for a user/project.

        Flow:
        1. Look up existing credential
        2. Check if token is expired
        3. Refresh if needed
        4. Return valid token
        """
        # Look up existing Codex credential
        credential = await self.integration_repo.get_credential_by_provider(
            project_id=project_id,
            provider="codex_agent",
        )

        if not credential:
            raise ValueError(
                "No Codex OAuth credential found. User must authorize Codex agent."
            )

        # Check if token is expired
        if credential.token_expires_at and credential.token_expires_at < datetime.utcnow():
            # Refresh token
            credential = await self._refresh_token(credential)

        # Validate token
        is_valid = await self._validate_token(credential)
        if not is_valid:
            credential.status = CredentialStatus.INVALID
            await self.integration_repo.update_credential(credential)
            raise ValueError("Codex OAuth token is invalid")

        return credential

    async def authorize_codex_agent(
        self,
        project_id: str,
        user_id: str,
        github_oauth_token: str,
    ) -> IntegrationCredential:
        """
        Authorize Codex agent for a user.

        Can either:
        1. Reuse existing GitHub token (if sufficient scopes)
        2. Request new token with agent-specific scopes

        Agent-specific scopes needed:
        - repositories:read (for code review)
        - workflows:read (for test analysis)
        - actions:read (for CI/CD logs)
        """
        # Check if GitHub token has required scopes
        scopes = await self._get_token_scopes(github_oauth_token)
        required_scopes = {
            'repo',  # Full repo access
            'read:org',  # Read org info
        }

        if required_scopes.issubset(set(scopes)):
            # Can reuse GitHub token
            encrypted_token = await self._encrypt_token(github_oauth_token)
        else:
            # Request new token with agent scopes
            new_token = await self._request_agent_token(
                project_id, user_id, github_oauth_token
            )
            encrypted_token = await self._encrypt_token(new_token)

        # Create credential record
        credential = IntegrationCredential(
            id=str(uuid.uuid4()),
            project_id=project_id,
            provider="codex_agent",
            credential_type="oauth_token",
            encrypted_token=encrypted_token,
            scopes=list(required_scopes),
            status=CredentialStatus.ACTIVE,
            provider_user_id=user_id,
            created_by_user_id=user_id,
            token_expires_at=datetime.utcnow() + timedelta(days=365),
        )

        await self.integration_repo.create_credential(credential)
        return credential

    async def _refresh_token(
        self,
        credential: IntegrationCredential,
    ) -> IntegrationCredential:
        """Refresh expired OAuth token."""
        if not credential.refresh_token:
            raise ValueError("No refresh token available")

        # Call GitHub OAuth endpoint
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://github.com/login/oauth/access_token',
                json={
                    'client_id': os.getenv('GITHUB_CLIENT_ID'),
                    'client_secret': os.getenv('GITHUB_CLIENT_SECRET'),
                    'refresh_token': await self._decrypt_token(credential.refresh_token),
                    'grant_type': 'refresh_token',
                },
                headers={'Accept': 'application/json'},
            ) as resp:
                data = await resp.json()

                if 'error' in data:
                    raise ValueError(f"OAuth refresh failed: {data['error']}")

                # Update credential
                credential.encrypted_token = await self._encrypt_token(
                    data['access_token']
                )
                credential.token_expires_at = datetime.utcnow() + timedelta(
                    seconds=data.get('expires_in', 3600)
                )
                credential.status = CredentialStatus.ACTIVE

                await self.integration_repo.update_credential(credential)

        return credential

    async def _validate_token(
        self,
        credential: IntegrationCredential,
    ) -> bool:
        """Validate OAuth token is still valid."""
        token = await self._decrypt_token(credential.encrypted_token)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://api.github.com/user',
                headers={'Authorization': f'token {token}'},
            ) as resp:
                return resp.status == 200

    async def _get_token_scopes(self, token: str) -> list[str]:
        """Get scopes granted to a token."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://api.github.com/user',
                headers={'Authorization': f'token {token}'},
            ) as resp:
                scopes_header = resp.headers.get('X-OAuth-Scopes', '')
                return [s.strip() for s in scopes_header.split(',') if s.strip()]
```

---

## Security & Isolation

### 12.1 Security Architecture

```
┌─────────────────────────────────────────────────┐
│  Execution Security Layers                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  Layer 1: Authentication & Authorization        │
│  • OAuth credentials (no API keys)              │
│  • Per-project execution ACLs                   │
│  • User must have project write permission      │
│  • Webhook signature verification (HMAC-SHA256) │
│                                                 │
│  Layer 2: Sandbox Isolation                     │
│  • Docker containers (OS-level isolation)       │
│  • Read-only filesystem except /tmp             │
│  • Network isolation (bridge network)           │
│  • Resource limits (CPU, memory, disk)          │
│  • Non-root user (execuser:execuser)            │
│  • No privileged capabilities (--cap-drop=ALL)  │
│                                                 │
│  Layer 3: Secret Management                     │
│  • Secrets encrypted at rest (AES-256)          │
│  • Secrets never logged                         │
│  • Secrets only injected to containers          │
│  • Rotation policy (monthly)                    │
│  • Audit trail of credential access             │
│                                                 │
│  Layer 4: Data Isolation                        │
│  • Executions only access own codebase mount    │
│  • Artifacts stored in project-specific dir     │
│  • No cross-project artifact access             │
│  • Filesystem ACLs restrict access              │
│                                                 │
│  Layer 5: Agent Constraints                     │
│  • Codex agent actions logged                   │
│  • Agent can only review media (no code mod)    │
│  • Agent output validated before execution      │
│  • Rate limiting (max tasks per hour)           │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 12.2 Security Implementation

```python
# src/tracertm/services/execution_security_service.py

import hashlib
import hmac
import secrets
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from tracertm.repositories.project_repository import ProjectRepository
from tracertm.repositories.user_repository import UserRepository


class ExecutionSecurityService:
    """Enforces security policies for executions."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.user_repo = UserRepository(session)

    async def verify_webhook_signature(
        self,
        webhook_secret: str,
        payload: bytes,
        signature: str,
    ) -> bool:
        """
        Verify HMAC-SHA256 signature of webhook payload.

        Constant-time comparison prevents timing attacks.
        """
        expected = hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256,
        ).hexdigest()

        # Constant-time comparison
        return hmac.compare_digest(
            expected.lower(),
            signature.lower(),
        )

    async def verify_execution_authorization(
        self,
        user_id: str,
        project_id: str,
        execution_type: str,
    ) -> bool:
        """
        Verify user is authorized to create execution.

        Requirements:
        - User has write permission on project
        - Execution type is enabled for project
        - User hasn't exceeded rate limits
        """
        # Get user and project
        user = await self.user_repo.get_by_id(user_id)
        project = await self.project_repo.get_by_id(project_id)

        if not user or not project:
            return False

        # Check write permission
        if user.id not in project.members_with_write:
            return False

        # Check execution type enabled
        if execution_type not in project.enabled_execution_types:
            return False

        # Check rate limits
        executions_today = await self._count_user_executions_today(user_id)
        if executions_today >= 100:  # Max 100 per day
            return False

        return True

    async def create_container_security_config(
        self,
        execution_id: str,
    ) -> dict:
        """
        Create security configuration for execution container.

        Returns Docker configuration for secure container.
        """
        return {
            'security_opt': [
                'no-new-privileges:true',
            ],
            'cap_drop': ['ALL'],
            'cap_add': ['NET_BIND_SERVICE'],
            'read_only_rootfs': True,
            'user': 'execuser:execuser',
            'tmpfs': ['/run', '/var/run'],
            'pids_limit': 256,  # Max processes
        }

    async def encrypt_secret(self, secret: str) -> str:
        """Encrypt secret for storage."""
        # Using Fernet (symmetric encryption)
        from cryptography.fernet import Fernet

        key = os.getenv('ENCRYPTION_KEY').encode()
        f = Fernet(key)
        return f.encrypt(secret.encode()).decode()

    async def decrypt_secret(self, encrypted: str) -> str:
        """Decrypt stored secret."""
        from cryptography.fernet import Fernet

        key = os.getenv('ENCRYPTION_KEY').encode()
        f = Fernet(key)
        return f.decrypt(encrypted.encode()).decode()
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goal:** Core execution infrastructure

1. Database schema migrations (alembic)
   - ExecutionEnvironmentConfig
   - Execution
   - ExecutionArtifact
   - CodexAgentInteraction

2. Core Service Interfaces
   - ExecutionService
   - ContainerManager (stub)
   - ArtifactStorageService

3. API Endpoints
   - POST /projects/{id}/executions
   - GET /projects/{id}/executions
   - GET /executions/{id}
   - WebSocket /executions/{id}/stream

4. Testing
   - Unit tests for storage service
   - Integration tests for execution model

### Phase 2: Docker Integration (Weeks 3-4)

**Goal:** Sandboxed execution environments

1. Docker Setup
   - Dockerfile.executor
   - docker-compose.execution.yml
   - Container health checks

2. ContainerManager Implementation
   - create_execution_container
   - stream_logs
   - get_resource_usage
   - cleanup_container

3. Integration Tests
   - Create/start/stop containers
   - Mount codebase
   - Artifact capture

### Phase 3: VHS Integration (Weeks 5-6)

**Goal:** CLI recording capability

1. VHSServiceCoordinator
   - generate_tape_file
   - execute_tape
   - generate_thumbnail

2. FFmpeg Integration
   - video_to_gif
   - generate_thumbnail
   - extract_frames

3. End-to-End Test
   - Generate tape file
   - Execute in container
   - Convert to GIF
   - Verify output

### Phase 4: Playwright Integration (Weeks 7-8)

**Goal:** Browser automation & recording

1. PlaywrightCoordinator
   - start_browser_session
   - execute_flow
   - stop_session

2. Flow Definition Schema
   - FlowStep model
   - Flow execution engine

3. Integration Tests
   - Navigate website
   - Perform interactions
   - Capture screenshots/video

### Phase 5: Codex Agent Integration (Weeks 9-10)

**Goal:** AI agent task execution

1. CodexAgentDispatcher
   - authenticate
   - dispatch_task
   - parse_response

2. OAuth Integration
   - CodexOAuthService
   - Token refresh
   - Scope management

3. Agent Interaction Logging
   - Task tracking
   - Response storage
   - Decision audit trail

### Phase 6: Webhook Triggers (Weeks 11-12)

**Goal:** Event-driven execution

1. Webhook Extensions
   - execution_requested event type
   - Trigger configuration in WebhookIntegration

2. Execution Triggering
   - Validate webhook signature
   - Create execution from webhook
   - Queue for processing

3. Results Callback
   - POST results back to webhook URL
   - Artifact links in callback

### Phase 7: Security & Hardening (Weeks 13-14)

**Goal:** Production security readiness

1. Security Service
   - Credential encryption
   - Authorization checks
   - Rate limiting

2. Audit Logging
   - Execution access logs
   - Secret access audit trail
   - Error tracking

3. Penetration Testing
   - Container escape attempts
   - Secret exposure tests
   - Authorization bypass tests

### Phase 8: Performance & Optimization (Weeks 15-16)

**Goal:** Production scalability

1. Performance Testing
   - Load test execution queue
   - Container spin-up time
   - Artifact storage performance

2. Optimization
   - Container caching
   - Parallel execution (resource permitting)
   - Artifact compression

3. Monitoring
   - Execution metrics dashboard
   - Resource usage tracking
   - Error rate alerts

---

## Conclusion

This design provides a comprehensive, secure, and extensible architecture for integrating execution environments into TraceRTM. Key features:

1. **Security First:** Docker sandboxing, OAuth credentials, encrypted secrets
2. **Zero Cloud:** Local storage with configurable retention
3. **Extensible:** Pluggable VHS, Playwright, Codex agents
4. **Observable:** Full audit trail and media artifacts
5. **Pragmatic:** Graceful degradation, retry logic, partial results

The phased implementation approach allows for incremental delivery and validation, reducing risk while maintaining flexibility to adjust based on learnings.

