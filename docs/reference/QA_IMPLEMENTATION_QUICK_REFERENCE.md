# QA+QC Integration System - Quick Reference Guide

**Quick Navigation for Developers**

---

## Project Roadmap at a Glance

```
Phase 1 (W1-3): Core Execution Environment
├─ ExecutionEnvironment, ExecutionSession, ExecutionArtifact models
├─ Docker provisioning service
├─ Basic artifact capture (screenshots, logs)
└─ S3 storage integration

Phase 2 (W4-5): Frontend Visualization
├─ TestNodeMetadata model
├─ Enhanced RichNodePill components
├─ NodeExpandPopup with artifact gallery
└─ Metrics display panels

Phase 3 (W6-7): GitHub Integration
├─ GitHub Check Runs API integration
├─ PR comment posting
├─ Webhook handlers for push/PR events
└─ Integration configuration UI

Phase 4 (W8-9): Advanced Features
├─ Video recording support
├─ Test framework auto-detection
├─ Flaky test detection
└─ Performance metrics dashboard

Phase 5 (W10-11): Security & Optimization
├─ Execution environment hardening
├─ Credential encryption
├─ Artifact lifecycle management
└─ Performance optimization
```

---

## Key New Models

### 1. ExecutionEnvironment
**Purpose**: Configuration for code execution environment
**Key Fields**:
- `repo_url`, `repo_branch` - Repository to test
- `runtime` - Docker image (node:20, python:3.12)
- `package_manager` - npm, pip, cargo
- `capture_screenshots`, `capture_videos`, `capture_coverage` - Artifact flags
- `status` - active, error, needs_setup

**Relations**: 1→Many ExecutionSession

### 2. ExecutionSession
**Purpose**: Single test execution instance
**Key Fields**:
- `environment_id` - Which environment
- `test_run_id` - Links to TestRun model
- `status` - pending, provisioning, running, completed, failed
- `container_id` - Docker container ID
- `tests_executed`, `tests_passed`, `tests_failed`
- `git_commit_sha`, `github_pr_number` - GitHub integration

**Relations**: 1←Many ExecutionArtifact, Links to TestRun

### 3. ExecutionArtifact
**Purpose**: Stores artifact references (screenshots, videos, logs)
**Key Fields**:
- `artifact_type` - screenshot, video, log, coverage_report
- `storage_path` - S3 key or local path
- `captured_at`, `test_step_index` - Timing info
- `share_token` - For shareable links

**Relations**: Many←1 ExecutionSession, Many←1 TestResult

### 4. TestNodeMetadata (NEW!)
**Purpose**: QA metrics on graph nodes
**Key Fields**:
- `pass_rate`, `test_coverage_percent` - Metrics
- `primary_artifact_id` - Featured screenshot/video
- `test_status` - passed, failed, pending, flaky
- `node_display_config` - Rendering hints

**Relations**: 1←1 GraphNode, Many to ExecutionArtifact

---

## API Endpoints Cheat Sheet

```
┌─ EXECUTION MANAGEMENT
├─ POST   /api/projects/{pId}/test-suites/{tId}/execute
├─ GET    /api/projects/{pId}/execution/sessions/{sId}/status
├─ WS     /api/projects/{pId}/execution/sessions/{sId}/logs
└─ POST   /api/projects/{pId}/execution/sessions/{sId}/cancel

┌─ ARTIFACTS
├─ GET    /api/artifacts/{aId}/preview?size=64
├─ GET    /api/artifacts/{aId}/view
├─ POST   /api/artifacts/{aId}/share
└─ GET    /api/artifacts/share/{shareToken}

┌─ GITHUB INTEGRATION
├─ POST   /api/github/webhook
├─ GET    /api/github/sync-status/{trId}
└─ POST   /api/github/pr/{prNum}/sync-results

┌─ NODE METADATA
├─ GET    /api/graph-nodes/{nId}/metadata
├─ GET    /api/graph-nodes/{nId}/artifacts
└─ GET    /api/test-nodes/{nId}/metrics
```

---

## Service Layer Overview

### Backend Services

```python
# Core Orchestration
TestEnvironmentOrchestrator
  ├─ execute_test_suite()
  ├─ execute_single_test()
  └─ trigger_execution_from_webhook()

# Environment Management
ExecutionEnvironmentService
  ├─ create_environment()
  ├─ detect_test_frameworks()
  └─ health_check()

# Session Orchestration
ExecutionSessionService
  ├─ create_session()
  ├─ start_execution()
  ├─ get_execution_status()
  └─ stream_execution_logs()

# Artifact Handling
ArtifactCaptureService
  ├─ capture_screenshot()
  ├─ start_video_recording()
  ├─ process_artifact()
  └─ generate_artifact_url()

# Container Execution
DockerTestRunner
  ├─ provision_container()
  ├─ execute_tests()
  └─ cleanup_container()

# GitHub Integration
GitHubCheckRunsService
  ├─ create_check_run()
  ├─ update_check_run()
  └─ post_test_results_comment()

GitHubWebhookHandler
  ├─ handle_push_event()
  ├─ handle_pull_request_event()
  └─ verify_signature()
```

### Frontend Hooks

```typescript
// Real-time execution monitoring
useExecutionStatus(sessionId)
  ├─ status: 'pending'|'running'|'completed'|'failed'
  ├─ testsExecuted: number
  ├─ testsPassed: number
  └─ progress: number (0-100)

// Artifact management
useArtifacts(sessionId)
  ├─ artifacts: ExecutionArtifact[]
  ├─ isLoading: boolean
  └─ refetch()

// Node metadata
useTestNodeMetadata(nodeId)
  ├─ passRate: number
  ├─ coveragePercent: number
  ├─ testStatus: 'passed'|'failed'|'pending'|'flaky'
  └─ primaryArtifactId: string
```

---

## Frontend Component Hierarchy

```
FlowGraphViewEnhanced
├── NodeDetailPanel (existing, enhanced)
│
├── RichNodePill (ENHANCED)
│   ├── NodeHeader
│   │   ├── Title (left)
│   │   └── Metrics/Badges (right)
│   ├── NodeImage (NEW)
│   │   ├── Rounded Pill Screenshot
│   │   ├── Play Overlay (for videos)
│   │   └── Click: Open Expanded View
│   └── NodeFooter (NEW)
│       ├── Status Badge
│       ├── Coverage Badge
│       └── Flaky Indicator
│
└── NodeExpandPopup (NEW - Modal)
    ├── Header
    │   └── Close Button
    ├── Main Layout (Flex)
    │   ├── Sidebar (Vertical Pills)
    │   │   ├── Screenshots Tab
    │   │   ├── Videos Tab
    │   │   ├── Logs Tab
    │   │   └── Metrics Tab
    │   │
    │   └── Content Area
    │       ├── ScreenshotGallery (W/ thumbnails)
    │       ├── VideoPlayer
    │       ├── LogsViewer (Syntax highlight)
    │       └── MetricsPanel
    │
    └── Footer
        ├── Run Tests Button
        ├── Download Artifacts
        └── Share Link
```

---

## Database Migration Order

1. **Migration 018**: `execution_environments`, `execution_sessions`, `execution_artifacts`, `test_node_metadata`
   - Add indexes for performance
   - Add foreign keys to test_runs, test_results
   - Add unique constraints where needed

2. **Extend TestResult** (existing table):
   - Add `github_check_run_id` (nullable)
   - Add `execution_session_id` (foreign key)

3. **Extend GraphNode** (existing table):
   - No changes to GraphNode itself
   - Create TestNodeMetadata join table instead

---

## Docker Strategy

```dockerfile
FROM node:20-alpine  # or python:3.12, rust:latest, etc
WORKDIR /workspace
RUN apk add --no-cache git

# Volume mounting strategy:
# - /workspace: Repository (RO or RW)
# - /results: Test results output
# - /artifacts: Screenshots/videos output

# Environment variables:
# - CI=true (for test frameworks)
# - NODE_OPTIONS (for Node.js)
# - PYTHONUNBUFFERED=1 (for Python)
```

**Resource Limits**:
- Memory: 2GB default (configurable per environment)
- CPU: 2 cores default
- Timeout: 1 hour default
- Disk: Ephemeral, cleaned after execution

---

## GitHub Integration Flow

```
GitHub Event (Push/PR)
    ↓
GitHub Webhook → /api/github/webhook
    ↓
Verify Signature (HMAC SHA256)
    ↓
Extract: Repo, Branch, Commit SHA, PR#
    ↓
Find IntegrationMapping
    ↓
Create ExecutionSession
    ↓
ExecutionEnvironmentOrchestrator.execute_test_suite()
    ↓
Create GitHub Check Run (status: in_progress)
    ↓
Stream logs in real-time
    ↓
Execution Completes
    ↓
Update Check Run (status: completed, conclusion: pass/fail)
    ↓
Post PR Comment with Results
    ↓
Update Integration Mapping (last_sync_at)
```

---

## File Structure to Create

```
src/tracertm/
├── models/
│   ├── execution_environment.py (NEW)
│   ├── execution_session.py (NEW)
│   └── execution_artifact.py (NEW)
│
├── repositories/
│   ├── execution_environment_repository.py (NEW)
│   ├── execution_session_repository.py (NEW)
│   └── execution_artifact_repository.py (NEW)
│
├── services/
│   ├── execution_environment_service.py (NEW)
│   ├── execution_session_service.py (NEW)
│   ├── artifact_capture_service.py (NEW)
│   ├── artifact_processor_service.py (NEW)
│   ├── test_environment_orchestrator.py (NEW)
│   ├── docker_test_runner.py (NEW)
│   ├── github_webhook_handler.py (NEW)
│   ├── github_check_runs_service.py (NEW)
│   └── artifact_storage_service.py (NEW)
│
├── api/
│   └── routes/
│       ├── execution.py (NEW)
│       ├── artifacts.py (NEW)
│       └── github_webhooks.py (NEW)
│
└── utils/
    ├── docker_utils.py (NEW)
    ├── artifact_utils.py (NEW)
    └── github_utils.py (NEW)

frontend/apps/web/src/
├── components/
│   ├── execution/
│   │   ├── ExecutionControlPanel.tsx (NEW)
│   │   ├── ExecutionMonitor.tsx (NEW)
│   │   └── ArtifactGallery.tsx (NEW)
│   ├── graph/
│   │   ├── RichNodePill.tsx (ENHANCE)
│   │   ├── NodeExpandPopup.tsx (NEW)
│   │   ├── MetricsPanel.tsx (NEW)
│   │   └── LogsViewer.tsx (NEW)
│
├── hooks/
│   ├── useExecutionSession.ts (NEW)
│   ├── useArtifacts.ts (NEW)
│   ├── useTestNodeMetadata.ts (NEW)
│   └── useExecutionLogs.ts (NEW)
│
└── pages/
    └── projects/
        └── views/
            └── ExecutionHistoryView.tsx (NEW)

tests/
├── unit/
│   └── services/
│       ├── test_execution_environment_service.py
│       ├── test_execution_session_service.py
│       └── test_artifact_capture_service.py
│
└── integration/
    ├── test_end_to_end_execution.py
    ├── test_github_integration.py
    └── test_artifact_storage.py
```

---

## Key Dependencies to Add

```toml
# pyproject.toml additions
docker = "^6.0.0"              # Docker client
boto3 = "^1.28.0"              # AWS S3
pillow = "^10.0.0"             # Image processing
python-magic = "^0.4.27"       # MIME type detection
aiofiles = "^23.1.0"           # Async file I/O
pygithub = "^2.1.1"            # GitHub API
```

```json
{
  "dependencies": {
    "react-player": "^2.13.0",
    "zustand": "^4.0.0",
    "socket.io-client": "^4.5.0",
    "recharts": "^2.10.0",
    "react-syntax-highlighter": "^15.5.0"
  }
}
```

---

## Critical Security Checkpoints

- [ ] Verify GitHub webhook signature (HMAC-SHA256)
- [ ] Validate all repo URLs (prevent SSRF)
- [ ] Encrypt GitHub tokens at rest (fernet)
- [ ] Sandbox Docker containers (resource limits)
- [ ] Validate artifact paths (prevent path traversal)
- [ ] Rate limit execution requests
- [ ] Scan artifacts for sensitive data
- [ ] Validate test framework commands (prevent RCE)

---

## Success Criteria Checklist

### Phase 1 Complete When:
- [ ] Can execute test suite via API
- [ ] Screenshots captured and stored
- [ ] Execution status trackable in real-time
- [ ] Logs retrievable

### Phase 2 Complete When:
- [ ] Graph nodes display test status
- [ ] Click to expand shows artifacts
- [ ] Metrics visible on nodes
- [ ] Artifact gallery works

### Phase 3 Complete When:
- [ ] GitHub PR triggers tests automatically
- [ ] Check runs appear on GitHub
- [ ] PR comments with results posted
- [ ] Manual integration config works

### Phase 4 Complete When:
- [ ] Video recordings captured
- [ ] Framework auto-detection works
- [ ] Flaky test detection active
- [ ] Historical metrics dashboard works

### Phase 5 Complete When:
- [ ] Security audit passed
- [ ] Performance benchmarks met
- [ ] Artifact cleanup working
- [ ] 99.5% uptime achieved

---

## Common Patterns

### Creating a New Service

```python
class MyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = MyRepository(session)

    async def do_something(self, id: str) -> Model:
        entity = await self.repo.get_by_id(id)
        if not entity:
            raise ValueError(f"Not found: {id}")

        # Do work
        entity.field = value
        await self.session.flush()
        return entity
```

### Creating an API Endpoint

```python
@router.post("/path")
async def endpoint(request: RequestModel) -> ResponseModel:
    try:
        async with get_session() as session:
            service = MyService(session)
            result = await service.do_something(request.id)
            await session.commit()
            return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Creating a React Hook

```typescript
export function useMyData(id: string) {
  const [data, setData] = useState<Data | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetch = useCallback(async () => {
    try {
      setLoading(true);
      const res = await fetch(`/api/path/${id}`);
      setData(await res.json());
    } catch (e) {
      setError(e as Error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetch();
  }, [id, fetch]);

  return { data, loading, error, refetch: fetch };
}
```

---

## Useful Commands

```bash
# Create migration
alembic revision --autogenerate -m "Add execution models"

# Apply migrations
alembic upgrade head

# Run tests
pytest tests/unit -v
pytest tests/integration -v

# Build Docker image
docker build -t tracertm-test-runner:latest .

# Format code
ruff format src/

# Type check
mypy src/

# Frontend dev
cd frontend && bun install && bun run dev
```

---

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Docker socket permission denied | `sudo chmod 666 /var/run/docker.sock` |
| Tests timeout | Increase `timeout_seconds` in ExecutionEnvironment |
| S3 artifacts not loading | Check bucket policy and CORS configuration |
| GitHub webhook not triggering | Verify signature, check webhook delivery logs |
| Screenshots blurry | Adjust screenshot compression ratio in ArtifactProcessor |
| PR comment not posting | Check GitHub token scopes (issues, pull_requests) |

---

**Last Updated**: Jan 28, 2026
**Status**: Ready for Development
**Owner**: Architecture Team
