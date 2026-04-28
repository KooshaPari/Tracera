# Quality Engineering/QA+QC Integration System
## Comprehensive Implementation Plan

**Project**: TraceRTM
**Date**: January 28, 2026
**Scope**: Code Execution Environment Integration + Enhanced Node Visualization + GitHub Workflow Integration
**Status**: Architecture & Design Document

---

## Executive Summary

This document outlines a comprehensive Quality Engineering system for TraceRTM that extends the existing test management infrastructure with:

1. **Code Execution Environment (CEE)**: Execute test suites and codebases programmatically with sandboxing
2. **Enhanced Node Visualization**: Rich graph nodes with embedded QA artifacts (screenshots, recordings, metrics)
3. **GitHub Workflow Integration**: PR/commit-triggered test execution with results posted back to GitHub

The system leverages existing models (TestCase, TestRun, TestSuite, TestCoverage) and integrates with established services (graph_service, webhook_service, integration repositories).

---

## Part 1: Current Architecture Analysis

### 1.1 Existing QA Infrastructure

#### Models (Already Implemented)
- **TestCase**: Comprehensive test specification with lifecycle (draft → approved → deprecated)
  - Supports multiple types: functional, integration, unit, e2e, performance, security, accessibility
  - Includes automation status tracking and execution history
  - Fields: preconditions, test_steps, expected_result, test_data, automation_script_path

- **TestRun**: Test execution instance with CI/CD integration
  - Tracks environment, build info, timing, and pass/fail metrics
  - Supports external CI integration (external_run_id, build_url, commit_sha)
  - Has TestResult children for individual test outcomes

- **TestResult**: Individual test outcome within a run
  - Already supports: screenshots, logs_url, attachments (JSON arrays)
  - Includes step_results and flaky test tracking
  - Has failure_reason, error_message, stack_trace fields

- **TestSuite**: Hierarchical collection of test cases
  - Supports parent/child relationships
  - Environment configuration: required_environment, environment_variables
  - Execution settings: is_parallel_execution, estimated_duration

- **TestCoverage**: Test-to-requirement traceability
  - Links test cases to items (requirements)
  - Coverage types: direct, partial, indirect, regression

#### Integration Infrastructure
- **IntegrationCredential**: Securely stores OAuth tokens, PAT, GitHub App credentials
- **IntegrationMapping**: Bidirectional sync between TraceRTM and external systems
- **IntegrationSyncQueue**: Async queue for sync operations
- **IntegrationSyncLog**: Audit trail for all sync operations

#### Graph & Visualization
- **GraphNode**: Join table mapping items into graphs
  - Currently simple: graph_id, item_id, project_id, is_primary
  - No embedded metadata for QA artifacts

- **FlowGraphView** (Frontend):
  - React Flow-based visualization
  - Custom RichNodePill components
  - Supports perspective selection and layout algorithms
  - NodeDetailPanel for additional info

#### Webhook & CI/CD Integration
- **WebhookIntegration**: Receives CI/CD events
  - Supports: GitHub Actions, GitLab CI, Jenkins, Azure DevOps, CircleCI
  - Event types: TEST_RUN_START, TEST_RUN_COMPLETE, TEST_RESULT_SUBMIT, BULK_RESULTS
  - WebhookService for signature verification and processing

### 1.2 Architecture Patterns

#### Repository Pattern
- Async SQLAlchemy repositories for data access
- Consistent CRUD patterns across TestRunRepository, TestCaseRepository, etc.
- Activity audit logs for lifecycle tracking

#### Service Pattern
- Layered services for business logic
- Example: GraphService for graph operations, WebhookService for event processing
- Dependency injection through async session management

#### Storage Layer
- SQLite/PostgreSQL support via SQLAlchemy
- S3-compatible storage for large files (via storage/ directory structure)
- JSON columns for flexible metadata

#### Frontend Integration
- TanStack Router for navigation
- React Flow for graph visualization
- tRPC for type-safe API calls
- Reactive hooks (useItems, useQAMetrics, etc.)

### 1.3 Gaps Identified

**QA Execution Gaps**:
- No code execution environment or sandboxing capability
- TestResult.screenshots/attachments are just JSON arrays (no real storage mechanism)
- No recording/video capture support for test execution
- No dynamic test execution triggering from the UI

**Visualization Gaps**:
- GraphNode model is too simple - no support for QA metadata
- No mechanism to attach execution logs, metrics, or images to graph nodes
- FlowGraphView nodes don't display test results or coverage metrics
- No interactive popup/expand behavior for node details with image galleries

**GitHub Integration Gaps**:
- IntegrationMapping exists but no GitHub-specific push-back of test results
- No webhook handlers for PR commits triggering test execution
- No mechanism to post PR comments with test results
- No GitHub check-run API integration

---

## Part 2: Code Execution Environment (CEE) Design

### 2.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Code Execution Environment Service Layer                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ExecutionRequest Handler                            │   │
│  │ - Validate test/suite/codebase reference            │   │
│  │ - Check environment prerequisites                   │   │
│  │ - Create execution session                          │   │
│  └──────────────────────────┬──────────────────────────┘   │
│                             │                                 │
│  ┌──────────────────────────┴──────────────────────────┐   │
│  │ Environment Manager (Sandbox)                       │   │
│  │ ┌─────────────────────────────────────────────────┐ │   │
│  │ │ Docker Container/Nix Flake Provisioner         │ │   │
│  │ │ - Clone/download repository                    │ │   │
│  │ │ - Install dependencies (npm/pip/cargo/etc)     │ │   │
│  │ │ - Setup environment variables                  │ │   │
│  │ │ - Resource limits (CPU, Memory, timeout)       │ │   │
│  │ └─────────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │ ┌─────────────────────────────────────────────────┐ │   │
│  │ │ Test Runner Adapter                            │ │   │
│  │ │ - Detect test framework (Jest, Pytest, etc)    │ │   │
│  │ │ - Execute tests with capturing flags           │ │   │
│  │ │ - Screenshot/video capture hooks               │ │   │
│  │ │ - Real-time output streaming                   │ │   │
│  │ └─────────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │ ┌─────────────────────────────────────────────────┐ │   │
│  │ │ Artifact Capture System                        │ │   │
│  │ │ - Screenshot collection (start/end/on-fail)    │ │   │
│  │ │ - Browser recording (Playwright/Cypress)       │ │   │
│  │ │ - Console logs and network traffic             │ │   │
│  │ │ - Performance metrics (timing, coverage)       │ │   │
│  │ └─────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                             │                                 │
│  ┌──────────────────────────┴──────────────────────────┐   │
│  │ Result Processor & Storage                         │   │
│  │ - Parse test results (JUnit XML, JSON)            │   │
│  │ - Compress and store artifacts                    │   │
│  │ - Generate coverage reports                       │   │
│  │ - Update TestRun/TestResult models               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 New Models Required

#### ExecutionEnvironment (New Model)

```python
class ExecutionEnvironment(Base, TimestampMixin):
    """Configuration for code execution environment."""

    __tablename__ = "execution_environments"

    id: str = mapped_column(String(36), primary_key=True)
    project_id: str = mapped_column(String(36), FK("projects.id"))

    # Basic Info
    name: str = mapped_column(String(255), nullable=False)
    description: Optional[str] = mapped_column(Text)

    # Environment Type & Configuration
    environment_type: str = mapped_column(String(50))  # "docker", "nix", "local"
    runtime: str = mapped_column(String(50))  # "node:20", "python:3.12", "rust:latest"

    # Repository Configuration
    repo_url: str = mapped_column(String(1000), nullable=False)
    repo_branch: str = mapped_column(String(255), default="main")
    repo_auth_type: Optional[str] = mapped_column(String(50))  # "ssh", "https", "gh_app"

    # Dependencies & Setup
    package_manager: str = mapped_column(String(50))  # "npm", "pip", "cargo", "go"
    setup_script: Optional[str] = mapped_column(Text)  # Shell commands to run
    environment_variables: dict = mapped_column(JSONType, default=dict)

    # Resource Limits
    cpu_cores_limit: int = mapped_column(Integer, default=2)
    memory_limit_mb: int = mapped_column(Integer, default=2048)
    timeout_seconds: int = mapped_column(Integer, default=3600)

    # Test Framework Detection
    detected_frameworks: list = mapped_column(JSONType)  # ["jest", "pytest", ...]
    test_command: Optional[str] = mapped_column(String(500))  # npm test, pytest, etc

    # Status & Health
    status: str = mapped_column(String(50), default="active")  # active, error, needs_setup
    last_tested_at: Optional[datetime] = mapped_column(DateTime(timezone=True))
    health_check_error: Optional[str] = mapped_column(Text)

    # Artifact Configuration
    capture_screenshots: bool = mapped_column(Boolean, default=True)
    capture_videos: bool = mapped_column(Boolean, default=False)
    capture_console_logs: bool = mapped_column(Boolean, default=True)
    capture_network_logs: bool = mapped_column(Boolean, default=False)
    capture_coverage: bool = mapped_column(Boolean, default=True)

    # Version & Credentials
    version: int = mapped_column(Integer, default=1)
    integration_credential_id: Optional[str] = mapped_column(String(36), FK("integration_credentials.id"))
```

#### ExecutionSession (New Model)

```python
class ExecutionSession(Base, TimestampMixin):
    """Tracks a single execution run of tests in an environment."""

    __tablename__ = "execution_sessions"

    id: str = mapped_column(String(36), primary_key=True)
    environment_id: str = mapped_column(String(36), FK("execution_environments.id"))
    test_run_id: str = mapped_column(String(36), FK("test_runs.id"))

    # Session State
    status: str = mapped_column(String(50))  # pending, provisioning, running, completed, failed

    # Execution Details
    started_at: Optional[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Optional[datetime] = mapped_column(DateTime(timezone=True))
    duration_seconds: Optional[int] = mapped_column(Integer)

    # Environment Instance
    container_id: Optional[str] = mapped_column(String(255))  # Docker container ID
    container_status: Optional[str] = mapped_column(String(50))

    # Execution Output
    stdout_log_url: Optional[str] = mapped_column(String(1000))
    stderr_log_url: Optional[str] = mapped_column(String(1000))

    # Resource Usage
    cpu_used_percent: Optional[float] = mapped_column(Float)
    memory_used_mb: Optional[int] = mapped_column(Integer)
    peak_memory_mb: Optional[int] = mapped_column(Integer)

    # Results
    tests_executed: int = mapped_column(Integer, default=0)
    tests_passed: int = mapped_column(Integer, default=0)
    tests_failed: int = mapped_column(Integer, default=0)
    test_coverage_percent: Optional[float] = mapped_column(Float)

    # Error Tracking
    error_message: Optional[str] = mapped_column(Text)
    error_code: Optional[str] = mapped_column(String(50))

    # Session Metadata
    git_commit_sha: Optional[str] = mapped_column(String(64))
    git_branch: Optional[str] = mapped_column(String(255))
    session_metadata: dict = mapped_column(JSONType, default=dict)
```

#### ExecutionArtifact (New Model)

```python
class ExecutionArtifact(Base, TimestampMixin):
    """Stores references to test execution artifacts (screenshots, videos, logs)."""

    __tablename__ = "execution_artifacts"

    id: str = mapped_column(String(36), primary_key=True)
    test_result_id: str = mapped_column(String(36), FK("test_results.id"))
    execution_session_id: str = mapped_column(String(36), FK("execution_sessions.id"))

    # Artifact Identification
    artifact_type: str = mapped_column(String(50))  # screenshot, video, log, coverage_report, trace
    artifact_name: str = mapped_column(String(255), nullable=False)
    mime_type: str = mapped_column(String(100))  # image/png, video/mp4, text/plain, etc

    # Storage Location
    storage_path: str = mapped_column(String(1000), nullable=False)  # S3 key or local path
    storage_backend: str = mapped_column(String(50))  # s3, gcs, local, etc
    file_size_bytes: int = mapped_column(Integer)

    # Content Metadata
    width: Optional[int] = mapped_column(Integer)  # For images/videos
    height: Optional[int] = mapped_column(Integer)
    duration_seconds: Optional[float] = mapped_column(Float)  # For videos

    # Capture Timing
    captured_at: datetime = mapped_column(DateTime(timezone=True), nullable=False)
    test_step_index: Optional[int] = mapped_column(Integer)  # Which step captured this

    # Content Processing
    is_processed: bool = mapped_column(Boolean, default=False)  # OCR'd, compressed, etc
    processing_metadata: dict = mapped_column(JSONType, default=dict)  # OCR text, dimensions, etc

    # Accessibility
    is_public: bool = mapped_column(Boolean, default=False)
    share_token: Optional[str] = mapped_column(String(255), unique=True)  # For sharing links

    version: int = mapped_column(Integer, default=1)
```

#### TestNodeMetadata (Enhancement to GraphNode)

```python
class TestNodeMetadata(Base, TimestampMixin):
    """Enhanced metadata for graph nodes related to QA."""

    __tablename__ = "test_node_metadata"

    id: str = mapped_column(String(36), primary_key=True)
    graph_node_id: str = mapped_column(String(36), FK("graph_nodes.graph_id", "graph_nodes.item_id"))

    # QA Metrics
    last_test_result: Optional[str] = mapped_column(String(50))  # passed, failed, etc
    last_execution_at: Optional[datetime] = mapped_column(DateTime(timezone=True))
    execution_count: int = mapped_column(Integer, default=0)
    pass_count: int = mapped_column(Integer, default=0)
    fail_count: int = mapped_column(Integer, default=0)
    pass_rate: Optional[float] = mapped_column(Float)

    # Coverage
    test_coverage_percent: Optional[float] = mapped_column(Float)
    coverage_status: Optional[str] = mapped_column(String(50))  # good, warning, critical

    # Primary Artifact
    primary_artifact_id: Optional[str] = mapped_column(String(36), FK("execution_artifacts.id"))

    # Linked Artifacts (JSON array of artifact IDs)
    artifact_ids: list = mapped_column(JSONType, default=list)

    # Status Indicators
    test_status: str = mapped_column(String(50), default="untested")  # untested, passing, failing, flaky
    is_flaky: bool = mapped_column(Boolean, default=False)
    flaky_indicator: Optional[float] = mapped_column(Float)  # 0-1 flakiness score

    # Node Display Hints
    node_display_config: dict = mapped_column(JSONType, default=dict)
    # {
    #   "icon": "passed|failed|pending|flaky",
    #   "badge_color": "green|red|yellow|orange",
    #   "show_metrics": true,
    #   "metric_labels": ["pass_rate", "coverage"]
    # }
```

### 2.3 New Services Required

#### ExecutionEnvironmentService

```python
class ExecutionEnvironmentService:
    """Manages execution environment setup, health checks, and provisioning."""

    async def create_environment(
        self,
        project_id: str,
        repo_url: str,
        runtime: str,
        package_manager: str,
        # ... other config
    ) -> ExecutionEnvironment:
        """Create and validate new execution environment."""

    async def detect_test_frameworks(
        self,
        environment_id: str,
    ) -> list[str]:
        """Clone repo and detect test frameworks (Jest, Pytest, etc)."""

    async def health_check(
        self,
        environment_id: str,
    ) -> dict[str, bool]:
        """Verify environment is properly configured and accessible."""

    async def update_dependencies(
        self,
        environment_id: str,
    ) -> bool:
        """Update package dependencies in the environment."""
```

#### ExecutionSessionService

```python
class ExecutionSessionService:
    """Manages test execution sessions and orchestration."""

    async def create_session(
        self,
        environment_id: str,
        test_run_id: str,
        git_commit_sha: Optional[str] = None,
        git_branch: Optional[str] = None,
    ) -> ExecutionSession:
        """Create new execution session."""

    async def start_execution(
        self,
        session_id: str,
        test_suite_id: Optional[str] = None,
        test_case_ids: Optional[list[str]] = None,
    ) -> asyncio.Task:
        """Start test execution (async task)."""

    async def get_execution_status(
        self,
        session_id: str,
    ) -> dict[str, Any]:
        """Get real-time execution status (streaming-ready)."""

    async def cancel_execution(
        self,
        session_id: str,
    ) -> bool:
        """Cancel running execution."""

    async def collect_execution_logs(
        self,
        session_id: str,
    ) -> str:
        """Retrieve complete execution logs."""
```

#### ArtifactCaptureService

```python
class ArtifactCaptureService:
    """Handles artifact capture, compression, and storage."""

    async def capture_screenshot(
        self,
        session_id: str,
        test_result_id: str,
        test_step_index: Optional[int] = None,
        capture_context: Optional[dict] = None,
    ) -> ExecutionArtifact:
        """Capture and store a screenshot."""

    async def start_video_recording(
        self,
        session_id: str,
    ) -> str:
        """Start recording test execution video."""

    async def stop_video_recording(
        self,
        session_id: str,
    ) -> ExecutionArtifact:
        """Stop recording and process video."""

    async def capture_coverage_report(
        self,
        session_id: str,
        coverage_format: str = "lcov",  # lcov, json, html
    ) -> ExecutionArtifact:
        """Capture and store coverage report."""

    async def process_artifact(
        self,
        artifact_id: str,
        # OCR, compression, thumbnail generation, etc
    ) -> ExecutionArtifact:
        """Post-process artifact (compression, OCR, etc)."""

    async def generate_artifact_url(
        self,
        artifact_id: str,
        expiry_minutes: int = 60,
    ) -> str:
        """Generate signed/shareable URL for artifact."""
```

#### TestEnvironmentOrchestrator

```python
class TestEnvironmentOrchestrator:
    """High-level orchestration of test execution with environment management."""

    async def execute_test_suite(
        self,
        test_suite_id: str,
        environment_id: Optional[str] = None,
        git_commit_sha: Optional[str] = None,
        github_pr_id: Optional[str] = None,
    ) -> ExecutionSession:
        """Execute entire test suite with environment provisioning."""
        # 1. Validate inputs
        # 2. Provision environment
        # 3. Start execution session
        # 4. Monitor execution
        # 5. Collect artifacts
        # 6. Update TestRun and TestResult
        # 7. Post results to GitHub if PR
        # 8. Cleanup environment

    async def execute_single_test(
        self,
        test_case_id: str,
        environment_id: Optional[str] = None,
    ) -> TestResult:
        """Execute single test case with full artifact capture."""

    async def trigger_execution_from_webhook(
        self,
        webhook_payload: dict,
    ) -> ExecutionSession:
        """Trigger test execution from GitHub webhook (PR/push)."""
```

### 2.4 Docker/Container Strategy

#### Execution Environment Options

**Option A: Docker Containers** (Recommended for flexibility)
- Pros: Language-agnostic, good isolation, easy CI/CD integration
- Cons: Requires Docker daemon, overhead per execution
- Implementation: Docker SDK (docker-py), containerized test runners

**Option B: Nix Flakes** (Alternative for reproducibility)
- Pros: Deterministic, lightweight, pure
- Cons: Requires Nix knowledge, steeper learning curve
- Implementation: nix flake config + direnv integration

**Option C: Subprocess/Local** (Development/testing)
- Pros: Fast, no external dependencies
- Cons: No isolation, security risks
- Implementation: subprocess with timeout/resource monitoring

#### Recommended Implementation Approach

```python
# service_containers/test_runner.py
class DockerTestRunner:
    """Executes tests within Docker containers."""

    async def provision_container(
        self,
        environment: ExecutionEnvironment,
        session: ExecutionSession,
    ) -> str:
        """Pull image, create container, run setup commands."""
        # 1. Detect/pull base image (node:20, python:3.12, etc)
        # 2. Create Docker container
        # 3. Copy repo/mount volume
        # 4. Run setup script
        # 5. Set resource limits (CPU, memory)
        # 6. Return container ID

    async def execute_tests(
        self,
        container_id: str,
        test_command: str,
        capture_config: dict,
    ) -> dict[str, Any]:
        """Execute test command in container with artifact capture."""
        # 1. Attach to container streams
        # 2. Run test command
        # 3. Capture output (real-time streaming)
        # 4. Screenshot/video hooks via test framework adapters
        # 5. Collect metrics
        # 6. Return results

    async def cleanup_container(self, container_id: str) -> bool:
        """Stop and remove container, cleanup resources."""
```

### 2.5 Test Framework Adapters

```python
# Framework detection and adaptation
class TestFrameworkAdapter:
    """Detects and adapts to different test frameworks."""

    @staticmethod
    def detect_framework(repo_path: str) -> Optional[str]:
        """Detect framework from package.json, requirements.txt, Cargo.toml, etc."""

    async def get_test_command(
        self,
        framework: str,
        test_selector: Optional[str] = None,  # file, pattern, single test
        with_coverage: bool = True,
        with_screenshots: bool = True,
    ) -> str:
        """Generate test command for framework."""
        # Jest: jest --coverage --json --outputFile=results.json
        # Pytest: pytest --cov --cov-report=json --json-report
        # Playwright: playwright test --reporter=json

class ScreenshotCaptureAdapter:
    """Framework-specific screenshot capturing."""

    async def setup_capture_hooks(
        self,
        framework: str,
        container: DockerClient,
    ) -> None:
        """Setup hooks for automatic screenshot capture."""
        # Jest: Custom reporter or beforeEach/afterEach
        # Playwright: Built-in screenshot API
        # Cypress: Built-in screenshot API
```

### 2.6 Integration with Existing Services

#### Webhook Service Enhancement

```python
# Add to WebhookService
async def process_github_workflow_webhook(
    self,
    payload: dict,  # GitHub webhook payload
) -> ExecutionSession:
    """
    Handle GitHub workflow/action webhook.

    Triggers test execution when:
    - PR is opened/updated
    - Push to specific branch
    - Scheduled workflow
    """
    # 1. Extract repo info from payload
    # 2. Find or create ExecutionEnvironment
    # 3. Create ExecutionSession
    # 4. Start async execution
    # 5. Setup callback to post results back to GitHub
```

#### GraphService Enhancement

```python
# Add to GraphService
async def enrich_nodes_with_qa_metrics(
    self,
    graph_id: str,
) -> None:
    """
    Enrich graph nodes with TestNodeMetadata.
    Called when rendering graph to include QA status/metrics.
    """
    # 1. Get all items in graph
    # 2. For each item, check if it's linked to test cases
    # 3. Get latest test results and coverage
    # 4. Create/update TestNodeMetadata
```

---

## Part 3: Enhanced Node Visualization Design

### 3.1 Component Architecture

```
FlowGraphViewEnhanced
├── NodeDetailPanel (existing, enhanced)
├── RichNodePill (existing, enhanced)
│   ├── NodeHeader
│   │   ├── Title + Status Icon
│   │   └── Right-aligned Metrics/Badges
│   │
│   ├── NodeImage (NEW)
│   │   ├── Rounded Pill Screenshot
│   │   ├── Play Button (for videos/demos)
│   │   └── Hover: Preview tooltip
│   │
│   └── NodeFooter (NEW)
│       ├── Test Status Badge (pass/fail/pending)
│       ├── Coverage Badge
│       └── Flaky Indicator
│
└── NodeExpandPopup (NEW)
    ├── Header
    │   ├── Title & Close Button
    │   └── Execution Status
    │
    ├── Sidebar (NEW)
    │   ├── Pill Tab Buttons (screenshots, videos, logs, metrics)
    │   └── Sticky vertical pill selection
    │
    ├── Main Content Area
    │   ├── Gallery/Carousel (for multiple artifacts)
    │   ├── Video Player (for recordings)
    │   ├── Logs Viewer (syntax-highlighted)
    │   ├── Metrics Display
    │   │   ├── Pass Rate
    │   │   ├── Coverage %
    │   │   ├── Execution Time
    │   │   └── Flakiness Score
    │   │
    │   └── Action Buttons
    │       ├── Run Tests
    │       ├── View Full Report
    │       ├── Download Artifacts
    │       └── Share (with expiring link)
    │
    └── Footer
        ├── Last Execution Time
        └── Environment Info
```

### 3.2 RichNodePill Enhancement

```typescript
// Component structure
interface TestNodePillProps extends RichNodePillProps {
  // QA Enhancements
  testStatus?: 'passed' | 'failed' | 'pending' | 'flaky';
  passRate?: number;  // 0-100
  coveragePercent?: number;  // 0-100
  primaryArtifactId?: string;  // Screenshot/video ID
  artifactCount?: number;
  lastExecutionTime?: Date;
  isFlaky?: boolean;

  // Callbacks
  onArtifactClick?: (artifactId: string) => void;
  onExecuteTests?: () => void;
  onExpandDetails?: () => void;
}

const TestNodePill: React.FC<TestNodePillProps> = ({
  // ... existing props
  testStatus,
  passRate,
  coveragePercent,
  primaryArtifactId,
}) => {
  return (
    <div className="node-container">
      {/* Header with title and right-aligned badges */}
      <div className="node-header">
        <h3>{item.title}</h3>
        <div className="right-badges">
          {coveragePercent !== undefined && (
            <Badge variant="outline">
              Coverage: {coveragePercent}%
            </Badge>
          )}
          {testStatus && (
            <StatusBadge status={testStatus} />
          )}
        </div>
      </div>

      {/* Primary artifact image - rounded pill, separate click handler */}
      {primaryArtifactId && (
        <div
          className="artifact-pill"
          onClick={(e) => {
            e.stopPropagation();
            onArtifactClick?.(primaryArtifactId);
          }}
        >
          <img
            src={`/api/artifacts/${primaryArtifactId}/preview`}
            alt="Test execution screenshot"
            className="rounded-full w-12 h-12"
          />
          {/* Play overlay for videos */}
          {artifacts.get(primaryArtifactId)?.type === 'video' && (
            <PlayIcon className="play-overlay" />
          )}
        </div>
      )}

      {/* Sub-header with metrics */}
      <div className="node-subheader">
        {passRate !== undefined && (
          <Metric label="Pass Rate" value={`${passRate}%`} />
        )}
        {artifactCount && (
          <Metric label="Evidence" value={artifactCount} />
        )}
      </div>
    </div>
  );
};
```

### 3.3 NodeExpandPopup Component

```typescript
interface NodeExpandPopupProps {
  nodeId: string;
  testNodeMetadata: TestNodeMetadata;
  artifacts: ExecutionArtifact[];
  testResults: TestResult[];
  onClose: () => void;
}

const NodeExpandPopup: React.FC<NodeExpandPopupProps> = ({
  nodeId,
  testNodeMetadata,
  artifacts,
  testResults,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'screenshots' | 'videos' | 'logs' | 'metrics'>('screenshots');
  const [selectedArtifact, setSelectedArtifact] = useState<ExecutionArtifact | null>(
    artifacts[0] || null
  );

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh]">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold">{nodeId}</h2>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Main Layout: Sidebar + Content */}
        <div className="flex gap-4 mt-6">

          {/* Vertical Sidebar with Pill Tabs */}
          <div className="flex flex-col gap-2 w-20">
            <PillTab
              label="Screenshots"
              count={artifacts.filter(a => a.artifact_type === 'screenshot').length}
              isActive={activeTab === 'screenshots'}
              onClick={() => setActiveTab('screenshots')}
              icon={<Camera />}
            />
            <PillTab
              label="Videos"
              count={artifacts.filter(a => a.artifact_type === 'video').length}
              isActive={activeTab === 'videos'}
              onClick={() => setActiveTab('videos')}
              icon={<Video />}
            />
            <PillTab
              label="Logs"
              count={artifacts.filter(a => a.artifact_type === 'log').length}
              isActive={activeTab === 'logs'}
              onClick={() => setActiveTab('logs')}
              icon={<FileText />}
            />
            <PillTab
              label="Metrics"
              isActive={activeTab === 'metrics'}
              onClick={() => setActiveTab('metrics')}
              icon={<BarChart />}
            />
          </div>

          {/* Main Content Area */}
          <div className="flex-1">
            {activeTab === 'screenshots' && (
              <ScreenshotGallery
                artifacts={artifacts.filter(a => a.artifact_type === 'screenshot')}
                selectedArtifact={selectedArtifact}
                onSelect={setSelectedArtifact}
              />
            )}

            {activeTab === 'videos' && (
              <VideoPlayer
                artifacts={artifacts.filter(a => a.artifact_type === 'video')}
                selectedArtifact={selectedArtifact}
                onSelect={setSelectedArtifact}
              />
            )}

            {activeTab === 'logs' && (
              <LogsViewer
                logs={testResults.map(r => r.actual_result)}
                artifactUrl={selectedArtifact?.storage_path}
              />
            )}

            {activeTab === 'metrics' && (
              <MetricsPanel
                metadata={testNodeMetadata}
                results={testResults}
              />
            )}
          </div>
        </div>

        {/* Footer with Actions */}
        <div className="flex gap-2 mt-6 pt-4 border-t">
          <Button
            onClick={onRunTests}
            className="gap-2"
          >
            <Play className="w-4 h-4" />
            Run Tests Now
          </Button>
          <Button
            variant="outline"
            onClick={onViewFullReport}
          >
            View Full Report
          </Button>
          <Button
            variant="outline"
            onClick={onDownloadArtifacts}
          >
            Download All
          </Button>
          <Button
            variant="outline"
            onClick={onShare}
          >
            <Share2 className="w-4 h-4" />
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Pill Tab Component for sidebar
const PillTab: React.FC<{
  label: string;
  count?: number;
  isActive: boolean;
  onClick: () => void;
  icon: React.ReactNode;
}> = ({ label, count, isActive, onClick, icon }) => (
  <button
    onClick={onClick}
    className={`
      relative group
      flex items-center justify-center
      w-16 h-16 rounded-full
      transition-all
      ${isActive ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}
    `}
    title={label}
  >
    {icon}
    {count !== undefined && count > 0 && (
      <Badge className="absolute -top-2 -right-2 bg-red-500">
        {count}
      </Badge>
    )}

    {/* Tooltip on hover */}
    <div className="hidden group-hover:block absolute left-full ml-2 bg-black text-white px-2 py-1 rounded whitespace-nowrap text-sm">
      {label}
      {count !== undefined && ` (${count})`}
    </div>
  </button>
);
```

### 3.4 Gallery/Carousel for Artifacts

```typescript
const ScreenshotGallery: React.FC<{
  artifacts: ExecutionArtifact[];
  selectedArtifact: ExecutionArtifact | null;
  onSelect: (artifact: ExecutionArtifact) => void;
}> = ({ artifacts, selectedArtifact, onSelect }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const current = selectedArtifact || artifacts[0];

  return (
    <div className="space-y-4">
      {/* Main Display */}
      <div className="relative bg-gray-100 rounded-lg overflow-hidden">
        <img
          src={`/api/artifacts/${current.id}/view`}
          alt={current.artifact_name}
          className="w-full h-auto max-h-[500px] object-contain"
        />
        <div className="absolute top-2 right-2 flex gap-2">
          <Button size="sm" variant="outline">
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => window.open(`/api/artifacts/${current.id}/download`)}
          >
            <Download className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Metadata */}
      <div className="text-sm text-gray-600">
        <p><strong>Captured at:</strong> {new Date(current.captured_at).toLocaleString()}</p>
        {current.test_step_index !== undefined && (
          <p><strong>Test Step:</strong> {current.test_step_index}</p>
        )}
      </div>

      {/* Thumbnail Strip */}
      <div className="flex gap-2 overflow-x-auto">
        {artifacts.map((artifact, idx) => (
          <button
            key={artifact.id}
            onClick={() => onSelect(artifact)}
            className={`flex-shrink-0 ${current.id === artifact.id ? 'ring-2 ring-blue-500' : ''}`}
          >
            <img
              src={`/api/artifacts/${artifact.id}/preview?size=64`}
              alt={artifact.artifact_name}
              className="w-16 h-16 object-cover rounded"
            />
          </button>
        ))}
      </div>

      {/* Navigation */}
      {artifacts.length > 1 && (
        <div className="flex items-center justify-between">
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              const idx = artifacts.indexOf(current);
              onSelect(artifacts[idx === 0 ? artifacts.length - 1 : idx - 1]);
            }}
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <span className="text-sm text-gray-600">
            {artifacts.indexOf(current) + 1} / {artifacts.length}
          </span>
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              const idx = artifacts.indexOf(current);
              onSelect(artifacts[idx === artifacts.length - 1 ? 0 : idx + 1]);
            }}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      )}
    </div>
  );
};
```

### 3.5 Metrics Display Component

```typescript
const MetricsPanel: React.FC<{
  metadata: TestNodeMetadata;
  results: TestResult[];
}> = ({ metadata, results }) => {
  const recentResults = results.slice(-10);

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Pass Rate Metric */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Pass Rate</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            {metadata.pass_rate?.toFixed(1) || 'N/A'}%
          </div>
          <Progress value={metadata.pass_rate || 0} className="mt-2" />
          <p className="text-xs text-gray-600 mt-2">
            {metadata.pass_count} passed / {metadata.execution_count} executed
          </p>
        </CardContent>
      </Card>

      {/* Coverage Metric */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Code Coverage</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">
            {metadata.test_coverage_percent?.toFixed(1) || 'N/A'}%
          </div>
          <Progress value={metadata.test_coverage_percent || 0} className="mt-2" />
          <p className="text-xs text-gray-600 mt-2">
            {metadata.coverage_status || 'unknown'}
          </p>
        </CardContent>
      </Card>

      {/* Flakiness */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Flakiness</CardTitle>
        </CardHeader>
        <CardContent>
          {metadata.is_flaky ? (
            <div>
              <Badge variant="destructive" className="mb-2">Flaky</Badge>
              <div className="text-2xl font-bold">
                {(metadata.flaky_indicator * 100).toFixed(0)}%
              </div>
              <p className="text-xs text-gray-600 mt-2">
                Test passes intermittently
              </p>
            </div>
          ) : (
            <div>
              <Badge variant="default" className="mb-2">Stable</Badge>
              <p className="text-xs text-gray-600 mt-2">
                Consistent results
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Execution History Chart */}
      <Card className="col-span-2">
        <CardHeader>
          <CardTitle className="text-sm">Last 10 Executions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-1 h-12">
            {recentResults.map((result) => (
              <div
                key={result.id}
                className={`flex-1 rounded ${
                  result.status === 'passed' ? 'bg-green-500' :
                  result.status === 'failed' ? 'bg-red-500' :
                  result.status === 'skipped' ? 'bg-gray-300' :
                  'bg-yellow-500'
                }`}
                title={`${result.status} - ${new Date(result.created_at).toLocaleString()}`}
              />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
```

---

## Part 4: GitHub Integration Enhancement

### 4.1 Architecture

```
GitHub Events
│
├─ Push Event
│  └─→ Hook Processor
│      ├─ Check if tests exist
│      ├─ Find ExecutionEnvironment for branch
│      ├─ Create ExecutionSession
│      └─ Start async test execution
│
├─ Pull Request Event
│  └─→ Hook Processor
│      ├─ Check if tests exist
│      ├─ Create ExecutionSession
│      ├─ Start test execution
│      └─ Setup result callback
│          └─ POST to GitHub Check Runs API
│             ├─ Post PR comment with results
│             └─ Update status checks
│
└─ Workflow Dispatch (Manual Trigger)
   └─→ Hook Processor
       └─ Start execution
```

### 4.2 GitHub Check Runs Integration

```python
class GitHubCheckRunsService:
    """Integrate with GitHub Check Runs API for PR status reporting."""

    async def create_check_run(
        self,
        mapping: IntegrationMapping,  # TraceRTM → GitHub mapping
        execution_session: ExecutionSession,
    ) -> dict[str, str]:
        """
        Create GitHub Check Run for test execution.

        Returns check_run_id and head_sha from GitHub response.
        """
        github_client = GitHubClient(mapping.credential)

        check_run = await github_client.api.checks.create(
            owner=repo.owner,
            repo=repo.name,
            name="TraceRTM Tests",
            head_sha=execution_session.git_commit_sha,
            status="in_progress",
            started_at=execution_session.started_at.isoformat(),
        )

        # Store check_run_id for later updates
        execution_session.github_check_run_id = check_run['id']
        await self.session.flush()

        return {
            "check_run_id": check_run['id'],
            "check_run_url": check_run['html_url'],
        }

    async def update_check_run(
        self,
        execution_session: ExecutionSession,
        status: str,  # queued, in_progress, completed
        conclusion: Optional[str] = None,  # success, failure, neutral, cancelled, skipped
    ) -> None:
        """Update GitHub Check Run with execution status."""
        mapping = await self.get_mapping(execution_session.test_run_id)
        github_client = GitHubClient(mapping.credential)

        # Build conclusion details
        summary = self._build_summary(execution_session)
        annotations = self._build_annotations(execution_session)

        await github_client.api.checks.update(
            check_run_id=execution_session.github_check_run_id,
            status=status,
            conclusion=conclusion,
            completed_at=execution_session.completed_at.isoformat() if conclusion else None,
            output={
                "title": f"Test Results - {execution_session.tests_passed}/{execution_session.tests_executed} passed",
                "summary": summary,
                "annotations": annotations,  # Per-test failures
            },
        )

    def _build_summary(self, session: ExecutionSession) -> str:
        """Build markdown summary for check run."""
        return f"""
## Test Execution Summary

- **Total Tests**: {session.tests_executed}
- **Passed**: {session.tests_passed} ✅
- **Failed**: {session.tests_failed} ❌
- **Pass Rate**: {(session.tests_passed/session.tests_executed*100):.1f}%
- **Duration**: {session.duration_seconds}s
- **Coverage**: {session.test_coverage_percent:.1f}%

[View Full Report](https://tracertm.local/projects/{session.project_id}/test-runs/{session.test_run_id})
        """

    def _build_annotations(self, session: ExecutionSession) -> list[dict]:
        """Build annotations for failed tests."""
        annotations = []

        for result in session.failed_results:
            annotations.append({
                "path": result.test_case.automation_script_path or "tests",
                "start_line": 1,
                "title": f"Test Failed: {result.test_case.title}",
                "message": result.failure_reason or "Test failed",
                "annotation_level": "failure",
            })

        return annotations
```

### 4.3 PR Comment Posting

```python
class GitHubPRCommentService:
    """Post detailed test results as PR comments."""

    async def post_test_results_comment(
        self,
        execution_session: ExecutionSession,
        mapping: IntegrationMapping,
        pr_number: int,
    ) -> str:
        """Post comprehensive test results comment on PR."""
        github_client = GitHubClient(mapping.credential)

        # Build comment markdown
        comment_body = self._build_comment_markdown(execution_session)

        comment = await github_client.api.issues.create_comment(
            owner=mapping.external_id.split('/')[0],
            repo=mapping.external_id.split('/')[1],
            issue_number=pr_number,
            body=comment_body,
        )

        return comment['html_url']

    def _build_comment_markdown(self, session: ExecutionSession) -> str:
        """Build detailed markdown comment."""
        failed_tests = session.failed_results[:5]  # Show top 5 failures

        markdown = f"""
## 🧪 Test Results

| Metric | Value |
|--------|-------|
| **Status** | {'✅ All Tests Passed' if session.tests_failed == 0 else f'❌ {session.tests_failed} Failed'} |
| **Pass Rate** | {(session.tests_passed/session.tests_executed*100):.1f}% ({session.tests_passed}/{session.tests_executed}) |
| **Duration** | {session.duration_seconds}s |
| **Coverage** | {session.test_coverage_percent:.1f}% |

"""

        if failed_tests:
            markdown += "### Failed Tests\n\n"
            for result in failed_tests:
                markdown += f"- **{result.test_case.title}**\n"
                markdown += f"  {result.failure_reason}\n\n"

        # Add artifact links
        artifacts = session.artifacts
        if artifacts:
            markdown += "### Evidence\n\n"
            screenshots = [a for a in artifacts if a.artifact_type == 'screenshot']
            if screenshots:
                markdown += f"- Screenshots: {len(screenshots)} captured\n"
            videos = [a for a in artifacts if a.artifact_type == 'video']
            if videos:
                markdown += f"- Recordings: {len(videos)} captured\n"
            logs = [a for a in artifacts if a.artifact_type == 'log']
            if logs:
                markdown += f"- Logs: Available in report\n"

        markdown += f"\n[📊 View Full Report](https://tracertm.local/projects/{session.project_id}/test-runs/{session.test_run_id})\n"

        return markdown
```

### 4.4 Webhook Handler Enhancement

```python
class WebhookService:
    # ... existing code ...

    async def process_github_webhook(
        self,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Process GitHub webhook (push, PR, workflow dispatch)."""
        event_type = headers.get('X-GitHub-Event')

        if event_type == 'push':
            return await self._handle_push_event(payload)
        elif event_type == 'pull_request':
            return await self._handle_pr_event(payload)
        elif event_type == 'workflow_run':
            return await self._handle_workflow_event(payload)

        return {"success": False, "error": "Unknown event type"}

    async def _handle_push_event(self, payload: dict) -> dict[str, Any]:
        """Handle push event - trigger test execution."""
        repo = payload['repository']
        branch = payload['ref'].split('/')[-1]
        commit_sha = payload['after']

        # Find or create mapping
        mapping = await self.integration_repo.get_or_create_mapping(
            repo_url=repo['clone_url'],
            branch=branch,
        )

        if not mapping:
            return {"success": False, "error": "No integration mapping found"}

        # Create execution session
        environment_id = mapping.environment_id
        session = await self.execution_orchestrator.execute_test_suite(
            test_suite_id=mapping.test_suite_id,
            environment_id=environment_id,
            git_commit_sha=commit_sha,
            git_branch=branch,
        )

        return {
            "success": True,
            "execution_session_id": session.id,
            "status": "started",
        }

    async def _handle_pr_event(self, payload: dict) -> dict[str, Any]:
        """Handle PR event - trigger tests and post results."""
        action = payload['action']

        if action not in ['opened', 'synchronize', 'reopened']:
            return {"success": True, "message": f"Action {action} ignored"}

        pr = payload['pull_request']
        repo = payload['repository']

        # Similar to push, but also setup GitHub callback
        session = await self.execution_orchestrator.execute_test_suite(
            git_commit_sha=pr['head']['sha'],
            git_branch=pr['head']['ref'],
            github_pr_id=pr['number'],
            github_repo=repo['full_name'],
        )

        # Setup async callback to post results
        asyncio.create_task(
            self._post_github_results(session, pr, repo)
        )

        return {
            "success": True,
            "execution_session_id": session.id,
        }

    async def _post_github_results(
        self,
        session: ExecutionSession,
        pr: dict,
        repo: dict,
    ) -> None:
        """Wait for execution to complete, then post results."""
        # Wait for execution to complete
        while session.status in ['pending', 'provisioning', 'running']:
            await asyncio.sleep(5)
            session = await self.session_repo.get_by_id(session.id)

        # Post check run update
        await self.github_service.update_check_run(
            session,
            status='completed',
            conclusion='success' if session.tests_failed == 0 else 'failure',
        )

        # Post comment
        await self.github_service.post_test_results_comment(
            session,
            mapping=...,  # Get from session.mapping_id
            pr_number=pr['number'],
        )
```

### 4.5 Configuration Schema

```python
# GitHub integration configuration
class GitHubIntegrationConfig(BaseModel):
    """Configuration for GitHub integration."""

    provider: Literal["github"] = "github"

    # Repository mapping
    repo_owner: str
    repo_name: str
    repo_clone_url: str

    # Test execution
    test_suite_id: str  # TraceRTM test suite to run
    environment_id: str  # TraceRTM execution environment

    # Trigger configuration
    trigger_on_push: bool = True
    trigger_on_pull_request: bool = True
    trigger_branches: list[str] = ["main", "develop"]  # Regex patterns

    # GitHub App / Token
    app_id: Optional[str] = None  # Preferred for better permissions
    oauth_token: Optional[str] = None  # Fallback

    # Result posting
    post_check_runs: bool = True
    post_pr_comments: bool = True
    post_commit_status: bool = False

    # Artifacts
    upload_artifacts_to_github: bool = False
    artifact_retention_days: int = 30
```

---

## Part 5: Data Storage & Artifact Management

### 5.1 Artifact Storage Strategy

#### S3-Compatible Backend (Recommended)
```python
class S3ArtifactStorage:
    """Store artifacts in S3 or S3-compatible storage (MinIO, etc)."""

    async def store_artifact(
        self,
        artifact_id: str,
        file_content: bytes,
        content_type: str,
        metadata: dict,
    ) -> str:
        """Store artifact and return storage path."""
        # Path: s3://tracertm-artifacts/{project_id}/{session_id}/{artifact_id}
        s3_key = f"artifacts/{self.project_id}/{artifact_id}"

        await self.s3_client.put_object(
            Bucket='tracertm-artifacts',
            Key=s3_key,
            Body=file_content,
            ContentType=content_type,
            Metadata=metadata,
        )

        return s3_key

    async def generate_presigned_url(
        self,
        artifact_id: str,
        expiry_seconds: int = 3600,
    ) -> str:
        """Generate temporary download URL."""
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': 'tracertm-artifacts',
                'Key': f"artifacts/{self.project_id}/{artifact_id}",
            },
            ExpiresIn=expiry_seconds,
        )
```

#### Local Storage (Development)
```python
class LocalArtifactStorage:
    """Store artifacts locally for development."""

    def __init__(self, base_path: Path = Path("./artifacts")):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def store_artifact(
        self,
        artifact_id: str,
        file_content: bytes,
        content_type: str,
        metadata: dict,
    ) -> str:
        """Store artifact locally."""
        artifact_path = self.base_path / artifact_id
        artifact_path.write_bytes(file_content)

        # Store metadata separately
        metadata_path = self.base_path / f"{artifact_id}.meta.json"
        metadata_path.write_text(json.dumps(metadata, indent=2))

        return str(artifact_path.relative_to(Path.cwd()))
```

### 5.2 Artifact Compression & Optimization

```python
class ArtifactProcessor:
    """Process artifacts: compress, resize, optimize."""

    async def process_image(
        self,
        image_bytes: bytes,
        target_format: str = 'webp',
    ) -> tuple[bytes, dict]:
        """Compress and optimize image."""
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_bytes))

        # Store original dimensions
        metadata = {
            'original_width': img.width,
            'original_height': img.height,
            'original_format': img.format,
        }

        # Convert and compress
        output = io.BytesIO()
        img.save(output, format=target_format, quality=85)

        optimized_bytes = output.getvalue()
        compression_ratio = len(optimized_bytes) / len(image_bytes)

        metadata['compression_ratio'] = compression_ratio
        metadata['format'] = target_format

        return optimized_bytes, metadata

    async def generate_thumbnail(
        self,
        image_bytes: bytes,
        size: tuple[int, int] = (128, 128),
    ) -> bytes:
        """Generate thumbnail for gallery preview."""
        from PIL import Image
        import io

        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail(size, Image.Resampling.LANCZOS)

        output = io.BytesIO()
        img.save(output, format='webp', quality=80)

        return output.getvalue()

    async def process_video(
        self,
        video_bytes: bytes,
    ) -> dict:
        """Extract metadata and generate thumbnail from video."""
        # Use ffmpeg to:
        # 1. Extract metadata (duration, codec, resolution)
        # 2. Generate thumbnail (middle frame)
        # 3. Optionally compress with H.265 for smaller file size
        pass
```

### 5.3 Retention & Cleanup Policies

```python
class ArtifactRetentionPolicy:
    """Manage artifact lifecycle and cleanup."""

    async def apply_retention_policies(
        self,
        project_id: str,
    ) -> dict[str, int]:
        """Apply retention policies and return cleanup stats."""
        stats = {
            'artifacts_deleted': 0,
            'space_freed_mb': 0,
        }

        # Policy 1: Delete artifacts older than 90 days
        old_artifacts = await self.artifact_repo.find_older_than_days(90)
        for artifact in old_artifacts:
            await self.delete_artifact(artifact.id)
            stats['artifacts_deleted'] += 1
            stats['space_freed_mb'] += artifact.file_size_bytes / (1024 * 1024)

        # Policy 2: Keep only 10 most recent artifacts per test
        for test_id in get_all_test_ids(project_id):
            recent = await self.artifact_repo.get_recent_for_test(test_id, limit=10)
            older = await self.artifact_repo.get_older_for_test(test_id, limit=None)

            for artifact in older:
                await self.delete_artifact(artifact.id)
                stats['artifacts_deleted'] += 1
                stats['space_freed_mb'] += artifact.file_size_bytes / (1024 * 1024)

        return stats

    async def delete_artifact(self, artifact_id: str) -> None:
        """Delete artifact and storage."""
        artifact = await self.artifact_repo.get_by_id(artifact_id)

        # Delete from storage
        await self.storage.delete(artifact.storage_path)

        # Delete from database
        await self.artifact_repo.delete(artifact_id)
```

---

## Part 6: Implementation Roadmap

### Phase 1: Foundation (Weeks 1-3)

**Objective**: Build core execution environment and basic test execution

- [ ] Create ExecutionEnvironment, ExecutionSession, ExecutionArtifact models
- [ ] Implement ExecutionEnvironmentService with Docker provisioning
- [ ] Create TestEnvironmentOrchestrator for high-level orchestration
- [ ] Add test execution endpoints to API (POST /api/test-runs/{id}/execute)
- [ ] Implement basic artifact capture (screenshots, logs)
- [ ] Add S3 storage integration for artifacts
- [ ] Create TestRunRepository methods for artifact management

**Deliverables**:
- Code execution working end-to-end (test suite → execution → results)
- Basic artifacts stored and retrievable
- Execution status API for real-time monitoring

### Phase 2: Frontend Integration (Weeks 4-5)

**Objective**: Build enhanced node visualization and artifact viewing

- [ ] Create TestNodeMetadata model and database migration
- [ ] Enhance GraphNode with QA metadata
- [ ] Build RichNodePill component with artifact preview
- [ ] Create NodeExpandPopup with sidebar tabs
- [ ] Implement ScreenshotGallery and MetricsPanel components
- [ ] Add artifact preview endpoints (thumbnails, full views)
- [ ] Build artifact upload/share functionality

**Deliverables**:
- Enhanced graph nodes showing test status and metrics
- Click-to-expand popup with full artifact viewing
- Artifact gallery with navigation

### Phase 3: GitHub Integration (Weeks 6-7)

**Objective**: Connect test execution to GitHub workflows

- [ ] Implement GitHubCheckRunsService for check run integration
- [ ] Create GitHubPRCommentService for result commenting
- [ ] Enhance WebhookService to handle GitHub events
- [ ] Add webhook handlers for push and PR events
- [ ] Implement async callback system for posting results
- [ ] Build GitHub configuration UI
- [ ] Add integration mapping for GitHub repos

**Deliverables**:
- GitHub check runs showing test status
- PR comments with test results
- Automatic test triggering on push/PR
- Integration UI for setup

### Phase 4: Advanced Features (Weeks 8-9)

**Objective**: Polish and extend capabilities

- [ ] Add video recording support (Playwright, Cypress integration)
- [ ] Implement test framework auto-detection
- [ ] Add coverage report integration
- [ ] Build performance metrics dashboard
- [ ] Implement flaky test detection and analysis
- [ ] Add artifact retention policies
- [ ] Create test execution history dashboard

**Deliverables**:
- Video recording of test execution
- Advanced metrics and analytics
- Performance tracking and optimization recommendations

### Phase 5: Security & Optimization (Weeks 10-11)

**Objective**: Security hardening and performance tuning

- [ ] Implement resource limits and sandboxing
- [ ] Add credential encryption for GitHub/repo access
- [ ] Security audit of execution environment
- [ ] Performance optimization of artifact storage
- [ ] Implement artifact lifecycle management
- [ ] Add rate limiting and quota management
- [ ] Security testing and penetration testing

**Deliverables**:
- Hardened execution environment
- Security audit report
- Performance benchmarks

---

## Part 7: Technology Stack & Dependencies

### Backend Extensions

```toml
# New dependencies for pyproject.toml

[execution-environment]
docker = "^6.0.0"  # Docker SDK for Python
docker-py = "^1.10.6"  # Alternative: Docker bindings
nix-flake = "^1.0.0"  # Nix flake support
asyncio-contextmanager = "^1.0.0"  # Async context helpers

[artifact-storage]
boto3 = "^1.28.0"  # AWS S3 client
aiofiles = "^23.1.0"  # Async file operations
pillow = "^10.0.0"  # Image processing
python-magic = "^0.4.27"  # File type detection

[github-integration]
pygithub = "^2.1.1"  # GitHub API client
github-webhook = "^1.0.0"  # Webhook parsing

[video-processing]
opencv-python = "^4.8.0"  # Video processing
pydub = "^0.25.1"  # Audio processing
ffmpeg-python = "^0.2.1"  # FFmpeg wrapper

[logging-monitoring]
prometheus-client = "^0.18.0"  # Already included
opentelemetry-instrumentation-fastapi = "^0.39b0"
opentelemetry-instrumentation-sqlalchemy = "^0.39b0"
```

### Frontend Extensions

```json
{
  "dependencies": {
    "react-flow-lib": "latest",
    "zustand": "^4.0.0",  // State management for execution UI
    "react-query": "^4.0.0",  // Already using
    "socket.io-client": "^4.5.0",  // Real-time execution updates
    "react-player": "^2.13.0",  // Video playback
    "react-syntax-highlighter": "^15.5.0",  // Log viewing
    "recharts": "^2.10.0",  // Metrics charts
    "video.js": "^8.0.0"  // Video player
  },
  "devDependencies": {
    "playwright": "^1.40.0",  // E2E test recording
    "@testing-library/react": "^14.0.0",
    "@testing-library/user-event": "^14.0.0"
  }
}
```

---

## Part 8: API Endpoints Summary

### Execution Management

```
POST   /api/projects/{projectId}/execution-environments
GET    /api/projects/{projectId}/execution-environments
GET    /api/execution-environments/{envId}
PUT    /api/execution-environments/{envId}
POST   /api/execution-environments/{envId}/health-check

POST   /api/test-runs/{testRunId}/execute
GET    /api/execution-sessions/{sessionId}
GET    /api/execution-sessions/{sessionId}/status
POST   /api/execution-sessions/{sessionId}/cancel
GET    /api/execution-sessions/{sessionId}/logs

POST   /api/artifacts
GET    /api/artifacts/{artifactId}/preview
GET    /api/artifacts/{artifactId}/view
GET    /api/artifacts/{artifactId}/download
POST   /api/artifacts/{artifactId}/share
GET    /api/artifacts/share/{shareToken}
```

### GitHub Integration

```
POST   /api/github-integrations
GET    /api/github-integrations/{integrationId}
PUT    /api/github-integrations/{integrationId}
POST   /api/github/webhook
GET    /api/github/sync-status/{testRunId}
POST   /api/github/pr/{prNumber}/sync-results
```

### Node Metadata & Metrics

```
GET    /api/graph-nodes/{nodeId}/metadata
PUT    /api/graph-nodes/{nodeId}/metadata
GET    /api/graph-nodes/{nodeId}/artifacts
GET    /api/test-nodes/{nodeId}/metrics
GET    /api/test-nodes/{nodeId}/execution-history
```

---

## Part 9: Security Considerations

### 1. Code Execution Sandboxing

- **Isolation**: Use Docker containers with resource limits (CPU, memory, filesystem)
- **Network Isolation**: Disable outbound network access or whitelist specific hosts
- **Filesystem Isolation**: Mount only necessary directories as read-only
- **Time Limits**: Enforce strict execution timeouts to prevent DoS
- **Resource Limits**: Set memory limits, CPU shares, disk quotas

### 2. Credential Management

- **GitHub Tokens**: Use GitHub App with minimal required scopes
- **Repository Access**: Use SSH keys or Deploy Keys (read-only)
- **Encryption**: Encrypt credentials at rest using fernet or KMS
- **Rotation**: Implement token rotation policies
- **Audit**: Log all credential access

### 3. Artifact Security

- **Access Control**: Implement fine-grained permissions for artifact viewing
- **Encryption**: Encrypt artifacts at rest and in transit
- **Retention**: Auto-delete artifacts after retention period
- **Integrity**: Use checksums/digital signatures for artifact verification
- **Content Scanning**: Scan artifacts for sensitive data (API keys, passwords)

### 4. API Security

- **Rate Limiting**: Limit execution requests per user/IP
- **Authentication**: Require API keys for execution endpoints
- **Validation**: Validate all inputs (repo URLs, test IDs, etc)
- **CORS**: Restrict webhook endpoints appropriately
- **HTTPS**: Enforce HTTPS for all external communication

### 5. GitHub Integration Security

- **Webhook Validation**: Verify GitHub webhook signatures
- **PR Permissions**: Only post results to PRs from trusted sources
- **Rate Limits**: Respect GitHub API rate limits
- **Token Scope**: Use minimal required GitHub App permissions
- **Audit Trail**: Log all GitHub API calls

---

## Part 10: Testing Strategy

### Unit Tests

```python
# tests/unit/services/test_execution_environment_service.py
class TestExecutionEnvironmentService:
    async def test_create_environment_validates_repo_url(self):
        """Test that invalid repo URLs are rejected."""

    async def test_detect_frameworks_recognizes_jest(self):
        """Test Jest framework detection."""

    async def test_health_check_returns_error_for_missing_deps(self):
        """Test health check reports missing dependencies."""

# tests/unit/services/test_artifact_capture_service.py
class TestArtifactCaptureService:
    async def test_capture_screenshot_creates_artifact_record(self):
        """Test screenshot capture creates database record."""

    async def test_video_recording_calls_docker_api(self):
        """Test video recording uses Docker API."""

    async def test_process_artifact_compresses_image(self):
        """Test image compression."""

# tests/unit/services/test_github_service.py
class TestGitHubCheckRunsService:
    async def test_create_check_run_posts_to_github(self):
        """Test check run creation calls GitHub API."""

    async def test_verify_webhook_signature_rejects_invalid(self):
        """Test webhook signature verification."""
```

### Integration Tests

```python
# tests/integration/test_end_to_end_execution.py
class TestEndToEndExecution:
    async def test_execute_test_suite_complete_flow(self):
        """Test full execution flow: provision → run → capture → cleanup."""

    async def test_execution_with_github_webhook(self):
        """Test GitHub webhook triggers execution and posts results."""

    async def test_artifact_storage_and_retrieval(self):
        """Test artifacts are stored and retrieved correctly."""

# tests/integration/test_github_integration.py
class TestGitHubIntegration:
    async def test_pr_webhook_creates_check_run(self):
        """Test PR webhook creates GitHub check run."""

    async def test_results_posted_to_pr_comment(self):
        """Test test results are posted as PR comment."""

    async def test_webhook_signature_validation(self):
        """Test webhook signature is validated."""
```

### E2E Tests

```typescript
// frontend/apps/web/e2e/execution.spec.ts
test.describe('Test Execution UI', () => {
  test('can trigger test execution from graph node', async ({ page }) => {
    // Navigate to graph view
    // Find test node
    // Click execute button
    // Verify execution starts
    // Monitor progress
    // Verify results display
  });

  test('node expand popup displays artifacts', async ({ page }) => {
    // Navigate to graph
    // Click node to expand
    // Verify sidebar tabs
    // Verify artifacts load in main area
    // Test gallery navigation
  });

  test('github results displayed in pr comment', async ({ page }) => {
    // Trigger webhook
    // Monitor execution
    // Verify GitHub PR comment posted
  });
});
```

---

## Part 11: Deployment & Operations

### Docker Deployment

```dockerfile
# Dockerfile for execution environment service
FROM python:3.12-slim

# Install system dependencies for Docker-in-Docker
RUN apt-get update && apt-get install -y \
    docker.io \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml pyproject.toml
RUN pip install -e .

# Copy application
COPY src/ src/

CMD ["python", "-m", "tracertm.services.execution_orchestrator"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tracertm-execution-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tracertm-execution
  template:
    metadata:
      labels:
        app: tracertm-execution
    spec:
      containers:
      - name: execution-service
        image: tracertm:latest
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
          limits:
            cpu: "2"
            memory: "4Gi"
      # Enable Docker socket mounting for Docker-in-Docker
      volumes:
      - name: docker-socket
        hostPath:
          path: /var/run/docker.sock
      volumeMounts:
      - name: docker-socket
        mountPath: /var/run/docker.sock
```

### Monitoring & Observability

```python
# Prometheus metrics
execution_duration_seconds = Histogram(
    'execution_duration_seconds',
    'Execution duration',
    buckets=[10, 30, 60, 300, 600, 1800],
)

artifacts_stored_bytes = Counter(
    'artifacts_stored_bytes',
    'Artifacts stored',
)

tests_executed_total = Counter(
    'tests_executed_total',
    'Total tests executed',
    ['status'],  # passed, failed, skipped
)

# Logging
logger.info(f"Execution started: {session.id}", extra={
    'execution_session_id': session.id,
    'test_run_id': session.test_run_id,
    'environment_id': session.environment_id,
    'docker_container_id': session.container_id,
})
```

---

## Part 12: Risk Assessment & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Code injection via test execution | Critical | Medium | Sandboxing, input validation, security review |
| Resource exhaustion (DoS) | High | Medium | Resource limits, rate limiting, quotas |
| Credential exposure | Critical | Low | Encryption, secret scanning, audit logs |
| GitHub API rate limiting | Medium | High | Retry logic, caching, request batching |
| Container image vulnerabilities | High | Medium | Image scanning, automated updates, security advisories |
| Storage space limits | Medium | High | Retention policies, compression, cleanup automation |
| Network failures during execution | Medium | High | Retry mechanisms, partial result recovery |
| Test framework compatibility | Medium | High | Extensive testing, framework adapters, fallbacks |

---

## Part 13: Success Metrics

### Technical Metrics

- **Execution Speed**: Average test suite execution time < 5 minutes
- **Artifact Processing**: Screenshots processed/stored in < 2 seconds
- **GitHub Integration**: PR status updated within 30 seconds of completion
- **Uptime**: 99.5% availability for execution service
- **Storage Efficiency**: Artifact compression ratio > 60%

### User Experience Metrics

- **Graph Node Clarity**: Users can identify test status at a glance
- **Artifact Accessibility**: All artifacts loadable in < 3 seconds
- **Execution Triggering**: One-click execution from UI or automatic via GitHub
- **Result Visibility**: PR comments with test results visible within 1 minute

### Quality Metrics

- **Code Coverage**: Execution service > 80% coverage
- **Error Rate**: < 0.1% of executions fail due to system errors
- **Flaky Test Detection**: Correctly identify flaky tests with > 95% accuracy

---

## Conclusion

This comprehensive implementation plan provides a roadmap for building a production-grade Quality Engineering system for TraceRTM. The phased approach allows for incremental delivery while maintaining system stability.

Key success factors:
1. **Security first**: Sandboxing and credential management are non-negotiable
2. **User experience**: Visualization enhancements make QA data actionable
3. **Integration**: GitHub webhook integration closes the feedback loop
4. **Scalability**: Asynchronous execution and cloud storage support growth
5. **Extensibility**: Service architecture allows adding more test frameworks and CI/CD platforms

The proposed architecture leverages existing TraceRTM patterns (repositories, services, models) while introducing new capabilities that significantly enhance the platform's QA capabilities.
