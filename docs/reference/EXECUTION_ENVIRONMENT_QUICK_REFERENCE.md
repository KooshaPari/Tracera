# Execution Environment Integration - Quick Reference Guide

**Document Purpose:** Quick lookup guide for developers implementing execution environments

---

## Key Architectural Decisions

### 1. Docker Containers (not serverless)

**Why:** Need filesystem access to codebase, full process control, resource isolation

**Constraints:** Local only, no cloud functions

### 2. OAuth Only (no API keys)

**Why:** Reuses existing GitHub OAuth flow, better security, token rotation

**Implementation:** Use IntegrationCredential model, extend with codex_agent provider

### 3. SQLite + Local Filesystem (no cloud storage)

**Why:** Zero dependencies, simple deployment, self-contained

**Trade-off:** Manual cleanup/retention management, disk space monitoring

### 4. Event-Driven via Webhooks

**Why:** Real-time triggers, integrates with existing infrastructure

**Pattern:** WebhookIntegration → ExecutionService → Container → Results

---

## Data Flow Cheat Sheet

```
User/Webhook Event
    ↓
ExecutionService.create_execution()
    → Creates Execution record (QUEUED)
    ↓
ExecutionService.execute()
    → ContainerManager.create_execution_container()
    → Sets status to PREPARING/RUNNING
    ↓
Execution Type Handler
    ├─ VHS: VHSServiceCoordinator → tape file → execute → GIF
    ├─ Playwright: PlaywrightCoordinator → browser → screenshot/video
    └─ Codex: CodexAgentDispatcher → task → response → action
    ↓
FFmpegPipelineService (optional)
    → video_to_gif, thumbnails, frame extraction
    ↓
ExecutionArtifact records created
    → Stored in ~/tracertm_artifacts/{project_id}/{execution_id}/
    ↓
Execution marked COMPLETED
    → Results available via ExecutionService.get_execution_artifacts()
```

---

## File Organization

### Models

```
src/tracertm/models/
├── execution.py (NEW)
│   ├── Execution
│   ├── ExecutionArtifact
│   ├── CodexAgentInteraction
│   └── ExecutionEnvironmentConfig
```

### Services

```
src/tracertm/services/
├── execution_service.py (NEW)
│   └── ExecutionService (main orchestrator)
├── container_manager.py (NEW)
│   └── ContainerManager (Docker lifecycle)
├── vhs_service.py (NEW)
│   └── VHSServiceCoordinator (tape generation + execution)
├── playwright_service.py (NEW)
│   └── PlaywrightCoordinator (browser automation)
├── ffmpeg_service.py (NEW)
│   └── FFmpegPipelineService (video processing)
├── codex_agent_service.py (NEW)
│   └── CodexAgentDispatcher (agent tasks)
├── codex_oauth_service.py (NEW)
│   └── CodexOAuthService (OAuth credential management)
├── execution_security_service.py (NEW)
│   └── ExecutionSecurityService (auth + encryption)
└── artifact_storage_service.py (NEW)
    └── ArtifactStorageService (local filesystem)
```

### Repositories

```
src/tracertm/repositories/
├── execution_repository.py (NEW)
│   ├── ExecutionRepository (CRUD + queries)
└── artifact_repository.py (NEW)
    └── ArtifactRepository (artifact metadata)
```

### API Endpoints

```
src/tracertm/api/
├── executions.py (NEW)
│   ├── POST /projects/{id}/executions (create)
│   ├── GET /projects/{id}/executions (list)
│   ├── GET /executions/{id} (get)
│   ├── GET /executions/{id}/artifacts (list artifacts)
│   ├── GET /executions/{id}/stream (WebSocket)
│   └── POST /executions/{id}/cancel (cancel)
```

### Docker

```
├── Dockerfile.executor (NEW)
│   └── Base image with Python, VHS, FFmpeg, Playwright
├── docker-compose.execution.yml (NEW)
│   └── Template for execution containers
```

### Migrations

```
alembic/versions/
└── 018_add_execution_environment.py (NEW)
```

---

## Quick Start: Adding a New Execution Type

### 1. Add Type to Enum

```python
class ExecutionType(str, Enum):
    MY_NEW_TYPE = "my_new_type"
```

### 2. Create Coordinator Service

```python
class MyCoordinator:
    async def execute(self, execution: Execution) -> ExecutionResult:
        # Your implementation
        pass
```

### 3. Wire in ExecutionService

```python
# In ExecutionService.execute()
elif execution.execution_type == ExecutionType.MY_NEW_TYPE:
    async for event in self._execute_my_type(execution):
        yield event

async def _execute_my_type(self, execution: Execution):
    coordinator = MyCoordinator()
    # Execute and yield events
```

### 4. Create Artifact

```python
artifact = ExecutionArtifact(
    id=str(uuid.uuid4()),
    execution_id=execution.id,
    artifact_type='my_type',
    name='artifact_name',
    file_path=str(file_path),
    mime_type='application/octet-stream',
)
await self.artifact_repo.create(artifact)
```

---

## VHS Tape File Syntax

```
# Output specification
Output output.gif
Output output.mp4

# Configuration
Set FontSize 14
Set Width 1200
Set Height 800
Set Framerate 10

# Type text
Type "ls -la"

# Wait for effect
Sleep 1

# Press Enter
Enter

# Wait for command to complete
Sleep 2
```

### Common Sleep Times
- Quick commands (ls, echo): 1-2 seconds
- Build/test commands: 5-10 seconds
- API calls: 3-5 seconds

---

## FFmpeg Common Commands

### MP4 to GIF (optimized)
```bash
ffmpeg -i input.mp4 \
  -vf "fps=10,scale=800:-1:flags=lanczos[p];[p]split[a][b];[a]palettegen[pal];[b][pal]paletteuse" \
  output.gif
```

### Thumbnail from video
```bash
ffmpeg -ss 00:00:01 -i input.mp4 \
  -vf "scale=400:-1" \
  -frames:v 1 output.png
```

### Extract frames
```bash
ffmpeg -i input.mp4 \
  -vf "fps=1" \
  frame_%03d.png
```

### Create video from images
```bash
ffmpeg -f concat -safe 0 -i filelist.txt \
  -c:v libx264 -pix_fmt yuv420p \
  output.mp4
```

---

## Docker Container Environment

### Mounted Volumes
```yaml
volumes:
  - /path/to/codebase:/workspace/codebase:ro  # Read-only
  - /tmp/execution:/tmp/execution:rw          # Scratch space
  - /artifacts:/workspace/artifacts:rw        # Output artifacts
```

### Environment Variables
```bash
EXECUTION_ID              # Unique execution ID
PROJECT_ID                # Project context
TASK_TYPE                 # Type of task
LOG_LEVEL                 # INFO/DEBUG/ERROR
MEMORY_LIMIT_MB           # Resource constraint
CPU_LIMIT                 # Core count limit
TIMEOUT_SECONDS           # Execution timeout
CODEX_OAUTH_TOKEN         # OAuth token (encrypted)
```

### Resource Limits
```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      cpus: '1'
      memory: 2G
```

---

## OAuth Token Flow

```
1. User logs in with GitHub
   ├─ IntegrationCredential stored (GitHub provider)
   └─ Scopes: repo, read:org

2. User requests Codex authorization
   └─ CodexOAuthService.authorize_codex_agent()
      ├─ Check if GitHub token has sufficient scopes
      └─ Create IntegrationCredential (codex_agent provider)

3. Execution needs Codex
   └─ ExecutionService.execute()
      └─ CodexOAuthService.get_codex_oauth_token()
         ├─ Retrieve credential
         ├─ Check expiration
         ├─ Refresh if needed
         └─ Validate token

4. Token Refresh (automatic)
   └─ CodexOAuthService._refresh_token()
      └─ GitHub OAuth refresh endpoint
         └─ New token stored, TTL updated
```

---

## Artifact Storage Layout

```
~/ tracertm_artifacts/
├── {project_id}/
│   ├── {execution_id1}/
│   │   ├── vhs/
│   │   │   ├── execution_id1.tape
│   │   │   ├── output.gif
│   │   │   └── output.mp4
│   │   ├── playwright/
│   │   │   ├── video.webm
│   │   │   ├── screenshots/
│   │   │   │   └── *.png
│   │   │   └── trace.zip
│   │   ├── ffmpeg/
│   │   │   ├── output.gif
│   │   │   └── thumbnail.png
│   │   ├── codex/
│   │   │   └── interactions.jsonl
│   │   ├── logs/
│   │   │   └── execution.log
│   │   └── metadata.json
│   └── {execution_id2}/
│       └── ... (same structure)
└── cleanup.log
```

---

## Cleanup Policy

```python
# In ExecutionService or background job
await artifact_service.cleanup_old_artifacts(
    retention_days=30,  # Delete artifacts older than 30 days
    max_total_size_gb=100,  # Optional: delete oldest if >100GB
)
```

### Cleanup Log
```
2026-01-28T10:30:15+00:00 | Deleted {project}/exec_1 (512.5 MB)
2026-01-28T10:31:20+00:00 | Deleted {project}/exec_2 (256.3 MB)
2026-01-28T10:32:45+00:00 | Cleaned up 2 executions, freed 768.8 MB
```

---

## Security Checklist

- [ ] Webhook signature verified (HMAC-SHA256)
- [ ] User authorized for project (write permission)
- [ ] Container running as non-root (execuser)
- [ ] Filesystem read-only except /tmp, /artifacts
- [ ] OAuth tokens encrypted at rest
- [ ] No secrets in logs
- [ ] Rate limiting enforced (max executions/day)
- [ ] Execution timeouts set
- [ ] Network isolation (Docker bridge)
- [ ] Resource limits enforced (CPU, memory, PIDs)

---

## Testing Strategy

### Unit Tests
```python
# VHS service
test_vhs_tape_generation()
test_vhs_execution()

# Playwright
test_playwright_session()
test_playwright_flow_execution()

# FFmpeg
test_video_to_gif()
test_thumbnail_generation()

# Storage
test_artifact_storage()
test_cleanup_policy()
```

### Integration Tests
```python
# End-to-end
test_execution_lifecycle()
test_vhs_pipeline()
test_playwright_pipeline()
test_codex_integration()

# Webhook trigger
test_webhook_execution_trigger()
```

### Security Tests
```python
# Authorization
test_unauthorized_execution_rejected()

# Isolation
test_container_isolation()
test_artifact_access_control()

# Secrets
test_no_secrets_logged()
test_token_encryption()
```

---

## Debugging Tips

### Container Logs
```bash
docker logs {container_id}
docker exec {container_id} tail -f /workspace/artifacts/execution.log
```

### VHS Issues
```bash
# Check tape file syntax
cat {tape_path}

# Run VHS directly
vhs < {tape_path}

# Verify GIF output
file output.gif
```

### Playwright Issues
```bash
# Enable debug logging
PWDEBUG=1 python -m pytest test_playwright.py

# Trace file analysis
playwright show-trace trace.zip
```

### FFmpeg Issues
```bash
# Check input video
ffprobe input.mp4

# Verbose conversion
ffmpeg -v debug -i input.mp4 output.gif
```

---

## Environment Variables

```bash
# Storage
ARTIFACTS_PATH=~/tracertm_artifacts
ARTIFACTS_RETENTION_DAYS=30

# Docker
DOCKER_HOST=unix:///var/run/docker.sock

# VHS
VHS_ENABLED=true
VHS_FPS=10

# Playwright
PLAYWRIGHT_ENABLED=true
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT_MS=30000

# Codex
CODEX_ENABLED=true
CODEX_MODEL=gpt-4-vision
CODEX_MAX_TOKENS=4096

# Security
ENCRYPTION_KEY={base64_encoded_fernet_key}
```

---

## Common Patterns

### Creating and Running Execution

```python
# Create
execution = await execution_service.create_execution(
    project_id='proj-123',
    name='Test VHS Recording',
    config=ExecutionConfig(
        execution_type=ExecutionType.VHS_RECORDING,
        vhs_commands=['echo "Hello"', 'ls -la'],
    ),
    triggered_by='api',
)

# Execute with streaming
async for event in execution_service.execute(execution.id, '/path/to/codebase'):
    if event['type'] == 'artifact':
        print(f"Artifact created: {event['data']['artifact_id']}")
    elif event['type'] == 'error':
        print(f"Error: {event['data']['error']}")

# Get results
artifacts = await execution_service.get_execution_artifacts(execution.id)
for artifact in artifacts:
    print(f"{artifact.artifact_type}: {artifact.file_path}")
```

### Webhook Trigger

```python
# In webhook endpoint
execution = await execution_service.create_execution(
    project_id=webhook.project_id,
    name=f'Webhook: {webhook.name}',
    config=ExecutionConfig(...),
    triggered_by='webhook',
    webhook_id=webhook.id,
)

# Track in integration_sync_logs
await sync_log_repo.create(
    operation='execution_triggered',
    source_system='webhook',
    target_system='execution_env',
    success=True,
)
```

### Artifact Cleanup

```python
# Schedule daily cleanup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=2, minute=0)
async def cleanup_artifacts():
    result = await artifact_service.cleanup_old_artifacts(
        retention_days=30
    )
    logger.info(
        f"Cleanup: deleted {result['deleted_executions']} executions, "
        f"freed {result['freed_bytes'] / (1024**3):.1f} GB"
    )
```

---

## Performance Tuning

### Container Startup
- Pre-pull Docker image to reduce startup time
- Use layer caching for dependencies
- Consider warm container pool

### Video Processing
- GIF quality vs file size trade-off: fps=10, scale=800:-1
- Extract key frames only for large videos
- Compress artifacts post-generation

### Database
- Index execution_project_status for fast filtering
- Partition artifact table by project_id (if very large)
- Archive old execution records

---

## Troubleshooting

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| Container won't start | Check Docker daemon | `docker ps`, `docker logs` |
| VHS tape invalid | Syntax error in tape file | Validate escaping, quotes |
| GIF too large | Video duration, resolution | Reduce fps, scale, or duration |
| Codex timeout | Agent overloaded or network | Increase timeout, retry |
| Artifacts not found | Wrong path format | Check ARTIFACTS_PATH config |
| OAuth token invalid | Token expired or revoked | Trigger refresh, re-authorize |

---

## Next Steps

1. Implement Phase 1: Database & core services
2. Get feedback on database schema
3. Implement Phase 2: Docker integration
4. Begin integration testing
5. Iterate based on learnings

