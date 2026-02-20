# Execution Environment Integration - Architecture Decisions

**Document Type:** Architecture Decision Record (ADR)
**Last Updated:** 2026-01-28
**Status:** Proposed for Implementation

---

## Decision 1: Docker Containers vs Serverless Functions

**Context:**
Need to execute arbitrary commands and scripts in a controlled environment while:
- Accessing codebase files
- Capturing terminal output as video/GIF
- Running long-duration tasks (testing, builds)
- Managing full process lifecycle

**Options Considered:**

| Factor | Docker Containers | AWS Lambda | Google Cloud Functions | Kubernetes Jobs |
|--------|-------------------|-----------|------------------------|-----------------|
| Codebase Access | Mount volume (native) | Via S3/artifact upload | Via Cloud Storage | Mount volume (native) |
| Duration | Up to 1+ hour | Max 15 minutes | Max 9 minutes | Unlimited |
| VHS/FFmpeg | Can install | Limited (time constraint) | Limited (time constraint) | Can install |
| Local Only | Yes (docker daemon) | No (requires AWS) | No (requires GCP) | No (requires k8s) |
| Cost | Cheap (local infra) | Pay per execution | Pay per execution | Pay per cluster |
| Complexity | Moderate | Low (managed) | Low (managed) | High (cluster mgmt) |
| Cold Start | 2-5 seconds | 500-5000ms | 500-5000ms | 1-2 seconds |

**Decision: Docker Containers**

**Rationale:**
1. **Requirement:** "NO paid cloud services" → eliminates Lambda, Cloud Functions
2. **Requirement:** "Local storage only" → Docker daemon local operations
3. **Duration:** Tasks may run 30+ minutes (builds, tests)
4. **Flexibility:** Full control over environment, can install any tools
5. **Existing Practice:** Project has docker-compose.test.yml setup
6. **Proven:** Widely used for CI/CD (GitHub Actions uses Docker)

**Consequences:**
- Must manage local Docker daemon (requires Docker installation on host)
- Container startup is slower than serverless (~2-5s vs 500ms)
- Manual scaling/resource management
- Mitigation: Pre-pull images, layer caching, optional container pool

---

## Decision 2: OAuth Credentials Only (No API Keys)

**Context:**
Need to authenticate executions and agent tasks with external systems (GitHub, Codex).

**Options Considered:**

| Factor | OAuth 2.0 + PKCE | API Keys | Personal Access Tokens | Basic Auth |
|--------|------------------|----------|------------------------|-----------|
| Setup Complexity | High (redirect flow) | Low | Medium (user generates) | Low |
| Security | Excellent (no shared creds) | Poor (exposed in config) | Good (token only) | Poor (password shared) |
| Scope Control | Fine-grained | Limited | Limited | Broad |
| Revocation | User controls in UI | Manual rotation | Manual rotation | N/A |
| Mobile Friendly | Yes (PKCE) | No | No | No |
| SSO/Org Support | Yes | No | Limited | Yes |
| Token Rotation | Yes (refresh token) | No | No | No |
| Terms of Service | GitHub allows | Vendor dependent | GitHub allows | GitHub disallows |

**Decision: OAuth 2.0 with PKCE**

**Rationale:**
1. **Existing Pattern:** System already implements GitHub OAuth for users
2. **Security:** OAuth tokens ≫ API keys (no credential exposure)
3. **Token Management:** Refresh tokens enable secure rotation
4. **GitHub Requirement:** GitHub disallows basic auth, prefers OAuth
5. **Scope Control:** Can request agent-specific scopes independently
6. **Audit Trail:** Provider tracks all token usage

**Codex Integration Specifics:**
- Reuse user's GitHub OAuth token for Codex (if sufficient scopes)
- Request agent-specific scopes if needed
- Store encrypted credentials in IntegrationCredential model
- Implement automatic token refresh before expiry

**Consequences:**
- Requires OAuth setup/redirect flow (one-time per user)
- Must handle token refresh logic
- Need to store refresh tokens (encrypted)
- Mitigation: Leverage existing OAuth infrastructure

---

## Decision 3: SQLite + Local Filesystem (No Cloud Storage)

**Context:**
Need to store:
- Execution metadata (status, timing, logs)
- Artifact references (GIFs, videos, screenshots)
- Agent interaction history
- Configuration data

**Options Considered:**

| Factor | SQLite + Local FS | PostgreSQL + S3 | MongoDB + Cloud Storage | Redis (ephemeral) |
|--------|-------------------|-----------------|------------------------|-------------------|
| Setup | Included (Python) | External DB + S3 | External DB + storage | External cache |
| Cost | Free (local disk) | Paid (storage, bandwidth) | Paid (storage, bandwidth) | Paid (if managed) |
| Scalability | Limited (~10GB) | Unlimited | Unlimited | Not persistent |
| Query Performance | SQLite (fast locally) | PostgreSQL (faster) | MongoDB (slower) | Very fast (cache) |
| Backup Simplicity | File copy | Managed snapshots | Managed backups | Not applicable |
| Cloud Dependencies | 0 | 1 (S3) | 2 (DB + storage) | 1 (Redis) |
| ACID Guarantees | Yes (SQLite) | Yes (PostgreSQL) | Yes (MongoDB) | No (cache) |
| Existing Integration | No | Project uses PostgreSQL | No | Project uses Redis |

**Decision: SQLite for Metadata + Local Filesystem for Artifacts**

**Rationale:**
1. **Requirement:** "NO paid cloud services" → eliminates S3, MongoDB Cloud, managed Redis
2. **Scalability:** Most executions have small metadata, large binary artifacts
3. **Simplicity:** No external services to configure/monitor
4. **Backup:** Simple rsync/tar approach
5. **Deployment:** Single-machine deployment (file-based)

**Artifact Storage Details:**
```
~/tracertm_artifacts/
├── {project_id}/
│   └── {execution_id}/
│       ├── vhs/         # VHS tape + GIF/video
│       ├── playwright/  # Browser videos + screenshots
│       ├── ffmpeg/      # Processed media
│       ├── codex/       # Agent interactions
│       └── logs/        # Execution logs
```

**Retention Policy:**
- Default: 30 days (configurable per project)
- Cleanup: Daily batch job (2 AM)
- Monitoring: Track disk usage, alert if >90%

**Consequences:**
- Single-machine limitations (eventual horizontal scaling challenges)
- Manual disk space management
- Simple backup/restore (file system backups)
- No query optimization needed (metadata is small)
- Mitigation: Implement cleanup policies, monitoring

---

## Decision 4: Event-Driven via Webhooks (Not Polling)

**Context:**
Need to trigger executions from external systems (CI/CD, user actions, scheduled tasks).

**Options Considered:**

| Factor | Webhooks | Polling | Message Queue | Cron + Pull |
|--------|----------|---------|---------------|------------|
| Latency | Immediate | 1-5 min intervals | Immediate | Delayed |
| Reliability | Requires retry logic | Always catches up | Excellent (broker) | Medium |
| Complexity | Moderate | Simple | High | Simple |
| Overhead | Only triggered | Constant polling | Requires broker | Minimal |
| Integration | External system initiates | App watches external | Both via queue | App pulls |
| Existing Pattern | WebhookIntegration exists | No polling service | No broker | Scheduled job |
| Scaling | Better (event-driven) | Worse (constant polling) | Better (async) | Medium |

**Decision: Event-Driven via Webhooks (Primary) + Scheduled Cleanup (Secondary)**

**Rationale:**
1. **Existing Infrastructure:** WebhookIntegration model already exists
2. **Real-time:** Immediate trigger on events (CI/CD completion, manual request)
3. **Efficiency:** No continuous polling overhead
4. **Integration Pattern:** Matches existing sync system (sync queue, webhooks)
5. **Audit:** Each trigger logged to integration_sync_logs

**Webhook Integration:**

```python
# WebhookIntegration extended with:
enabled_events = [
    WebhookEventType.EXECUTION_REQUESTED,  # NEW
    # ... existing events
]

# Webhook payload triggers:
POST /webhooks/{webhook_id}
{
    "event": "execution_requested",
    "execution_config": { ... }
}
```

**UI/Manual Trigger:**
```
POST /projects/{id}/executions
{
    "name": "Manual VHS Recording",
    "execution_type": "vhs_recording",
    "execution_config": { ... }
}
```

**Scheduled Cleanup:**
```python
# Background job (APScheduler)
@scheduler.scheduled_job('cron', hour=2)
async def cleanup_old_artifacts():
    # Runs daily at 2 AM
```

**Consequences:**
- Webhook endpoints must be idempotent (re-delivery)
- Need retry logic for failed webhook deliveries
- Database queue (execution_sync_queue analog) for reliability
- Mitigation: Use idempotency keys, persist queue state

---

## Decision 5: Codex CLI Agent (Not OpenAI API)

**Context:**
Need AI capabilities to:
- Review media (images, videos)
- Make autonomous decisions
- Generate reports from artifacts

**Options Considered:**

| Factor | Codex CLI | OpenAI API | Anthropic API | Local LLM |
|--------|-----------|-----------|---------------|-----------|
| Auth Method | OAuth | API Key | API Key | N/A |
| Vision Capability | Yes (GPT-4V) | Yes (GPT-4V) | Yes (Claude 3V) | Limited |
| Cost | Included in Codex | Pay per call | Pay per call | Free (self-hosted) |
| Ease of Use | Agent tool | Raw API | Raw API | Complex setup |
| Autonomous Actions | Yes (built-in) | No (framework needed) | No (framework needed) | No |
| Integration | CLI interface | Python library | Python library | Custom |
| Latency | Agent decides | Immediate | Immediate | Variable |
| Observability | Logging built-in | Manual logging needed | Manual logging needed | Custom |

**Decision: Codex CLI Agent**

**Rationale:**
1. **No Cloud Dependencies:** Codex works with OAuth tokens (no API key exposure)
2. **Autonomous:** Built-in agent loop (vs raw API requiring framework)
3. **CLI Native:** Fits execution container pattern perfectly
4. **Vision:** Codex can review images/videos from artifacts
5. **Logging:** Agent interactions logged natively
6. **Flexibility:** Can extend with custom tools later

**Important Note:**
Codex CLI is designed to work like an agent that receives instructions, reviews media, and takes actions. It's not a simple API call but a full agent loop.

**Integration Pattern:**
```python
# In container, dispatch task to Codex CLI
task = {
    'type': 'code_review',
    'prompt': 'Review the test results in these screenshots',
    'input_files': ['/artifacts/screenshot_1.png', '/artifacts/screenshot_2.png'],
}

# Codex CLI runs, reviews images, makes decisions
# Output: JSON response with reasoning and actions
```

**Consequences:**
- Codex must be installed in execution container
- Agent decisions need validation before execution
- May take longer than raw API calls (agent loop)
- Mitigation: Timeout limits, action whitelist, audit trail

---

## Decision 6: VHS (charmbracelet/vhs) for CLI Recording

**Context:**
Need to record terminal sessions as GIFs/videos for documentation and testing evidence.

**Options Considered:**

| Factor | VHS | asciinema | ttyrec | terminalizer | Custom Script |
|--------|-----|-----------|--------|-------------|---------------|
| Output Formats | GIF, MP4, WebM | ASCIICAST (text) | ASCIICAST (binary) | GIF, WebM | Flexible |
| Ease of Use | Tape files (declarative) | Recording mode | Recording mode | Recording mode | Complex |
| Quality | Excellent (pixel-perfect) | Text-based (simple) | Text-based | Good | Varies |
| File Size | Large (binary) | Small (text) | Medium | Medium | Varies |
| Headless Support | Yes | Yes | Yes | Yes | Varies |
| Editor Support | VSCode plugin | Web player | None | Web player | None |
| Setup | Binary install | npm install | Binary | npm install | N/A |
| Playback | Standalone GIF/video | Web player only | Terminal only | Web player | Browser |
| Active Development | Active | Active | Archived | Inactive | N/A |

**Decision: VHS (charmbracelet/vhs)**

**Rationale:**
1. **Output Quality:** GIF/video output is ideal for documentation
2. **Declarative:** .tape files describe exactly what to record (reproducible)
3. **Headless:** Runs in containers without TTY
4. **Active Project:** charmbracelet/vhs is well-maintained
5. **File Formats:** GIF is universally supported (no player needed)
6. **Performance:** Efficient encoder, reasonable file sizes

**VHS Tape File Pattern:**
```
Output output.gif
Set FontSize 14
Set Width 1200
Set Height 800

Type "npm test"
Sleep 0.5
Enter
Sleep 5
```

**Advantages Over asciinema:**
- Binary output (GIF/video) vs text-based (must use web player)
- Better for non-technical audiences
- Easier distribution/embedding

**Consequences:**
- VHS binary must be installed in Docker image
- GIF files larger than text recordings
- Need to generate .tape files (not record interactively)
- Mitigation: FFmpeg can compress GIFs, automate .tape generation

---

## Decision 7: Playwright for Browser Automation

**Context:**
Need to automate web UI interactions and capture screenshots/video evidence.

**Options Considered:**

| Factor | Playwright | Selenium | Puppeteer | Cypress | E2E Testing Framework |
|--------|-----------|----------|-----------|---------|----------------------|
| Languages | Python, JS, Java, C# | Many | JavaScript/Node | JavaScript | Many |
| Browsers | Chrome, Firefox, Safari | All | Chrome, Edge | Chrome | All |
| Video Recording | Yes (native) | No | Plugin | Yes | Variable |
| HAR Support | Yes (network) | No | Yes | Limited | Some |
| Trace Support | Yes (timeline) | No | No | Yes | Some |
| Headless Performance | Excellent | Good | Excellent | Good | Variable |
| Debugging | Excellent tools | Basic | Good | Excellent | Variable |
| Python Support | First-class | Excellent | No (JS only) | No (JS only) | Some |
| Screenshots | Full page | Yes | Yes | Yes | Yes |
| Cost | Free | Free | Free | Free | Free |

**Decision: Playwright**

**Rationale:**
1. **Python Native:** First-class Python support (project is Python-based)
2. **Video Recording:** Native video + HAR + trace support
3. **Cross-browser:** Chrome, Firefox, Safari
4. **Debugging:** Exceptional tools (trace files, visual debugging)
5. **Async Support:** Excellent async/await patterns for Python
6. **Active Development:** Well-maintained by Microsoft

**Capabilities:**
- Video recording (WebM format)
- HAR file (network analysis)
- Trace file (visual timeline debugging)
- Full-page screenshots
- Network interception

**Consequences:**
- Playwright requires browser installation (can be headless)
- Video files are WebM (need FFmpeg to convert to other formats)
- Trace files require VSCode extension to analyze
- Mitigation: Include browser installation in Docker, include FFmpeg

---

## Decision 8: FFmpeg for Video Processing

**Context:**
Need to process recorded videos:
- Convert MP4/WebM to animated GIF
- Generate thumbnails
- Extract frames for analysis
- Create slideshows

**Options Considered:**

| Factor | FFmpeg | ImageMagick | GStreamer | OpenCV | Python Video Libs |
|--------|--------|------------|-----------|--------|-------------------|
| GIF Support | Excellent | Good | Good | No | Limited |
| Performance | Excellent | Good | Good | Varies | Slow |
| Format Support | 100+ | 100+ | 80+ | 30+ | Limited |
| Library Size | ~50MB | ~50MB | Large | Small | Varies |
| Batch Processing | Yes (CLI) | Yes (CLI) | Yes (CLI) | No | No |
| Customization | High (filters) | Medium | Medium | High | Medium |
| Ease of Use | CLI (standard) | CLI (standard) | CLI (complex) | API (code) | Varies |
| Active Development | Very active | Active | Active | Very active | Varies |
| Licensing | LGPL | Apache 2.0 | LGPL | Apache 2.0 | Varies |

**Decision: FFmpeg**

**Rationale:**
1. **Industry Standard:** Used everywhere for video processing
2. **GIF Quality:** Excellent GIF encoding with palette optimization
3. **Flexibility:** 100+ filters and effects
4. **Performance:** Highly optimized C code
5. **CLI Native:** Integrates perfectly with async subprocess pattern
6. **No Dependencies:** Standalone binary

**FFmpeg Commands in Codebase:**
```python
# Video to GIF (optimized palette)
ffmpeg -i video.mp4 \
  -vf "fps=10,scale=800:-1:flags=lanczos[p];
       [p]split[a][b];
       [a]palettegen[pal];
       [b][pal]paletteuse" \
  output.gif

# Thumbnail extraction
ffmpeg -ss 00:00:01 -i video.mp4 -vf "scale=400:-1" -frames:v 1 output.png

# Frame extraction
ffmpeg -i video.mp4 -vf "fps=1" frame_%03d.png
```

**Consequences:**
- FFmpeg binary required in Docker image (~50MB)
- Learning curve for advanced filters
- Async subprocess handling needed
- Mitigation: Use simple, well-tested command patterns

---

## Decision 9: Extend WebhookIntegration vs New Execution Trigger Model

**Context:**
Need to trigger executions from webhooks. Question: Use existing WebhookIntegration or create separate ExecutionTrigger model?

**Options Considered:**

| Aspect | Extend WebhookIntegration | New ExecutionTrigger Model |
|--------|---------------------------|--------------------------|
| Code Reuse | High (existing validation, auth) | Low (new model) |
| Semantic Clarity | Slight overload (webhooks ≠ execution) | Clearer purpose |
| Database Design | Simple (one table) | More tables, joins |
| Backwards Compatibility | Fully compatible | Needs migration |
| Future Flexibility | Limited (coupled to webhook) | Flexible (execution-specific) |
| Testing | Leverages webhook tests | Needs new tests |

**Decision: Extend Existing WebhookIntegration**

**Rationale:**
1. **Maximal Reuse:** Signature verification, auth, rate limiting all present
2. **Integration Pattern:** Matches existing design (webhook → sync queue pattern)
3. **Simplicity:** One model vs multiple models
4. **Migration Path:** Can refactor later if needed
5. **Backwards Compatibility:** Doesn't break existing functionality

**Implementation Approach:**
```python
# Add to WebhookEventType enum
class WebhookEventType(str, Enum):
    # Existing
    TEST_RUN_START = "test_run_start"
    # New
    EXECUTION_REQUESTED = "execution_requested"

# Add to WebhookIntegration
execution_config: dict = Field(None)  # NEW execution params
execution_type: str = Field(None)     # NEW execution type
```

**Webhook Payload Example:**
```json
{
    "event": "execution_requested",
    "execution_type": "vhs_recording",
    "execution_config": {
        "vhs_commands": ["npm test", "npm build"]
    }
}
```

**Consequences:**
- WebhookIntegration gains execution-specific fields
- Semantic overload (webhooks used for multiple purposes)
- Clear separation in endpoint routing
- Mitigation: Document purpose clearly, future refactoring possible

---

## Decision 10: Synchronous vs Asynchronous Execution

**Context:**
How should executions run? Sync (block caller) or async (queue and stream)?

**Options Considered:**

| Aspect | Synchronous | Asynchronous (Queue-based) | Hybrid |
|--------|------------|---------------------------|--------|
| API Response | Blocks until complete | Immediate (job ID) | Immediate, stream updates |
| Execution Duration | Caller waits (timeout risk) | Decoupled from API | Caller can disconnect |
| Scalability | Single request blocks | Unlimited concurrent | Excellent |
| Simplicity | Simple (blocking) | Complex (queue) | Moderate |
| User Experience | Blocking progress | Polling required | Real-time updates |
| Error Handling | Synchronous exceptions | Async error queue | Can catch both |
| Container Resource | Tied to request | Independent | Optimal |

**Decision: Asynchronous with WebSocket Streaming**

**Rationale:**
1. **Scalability:** Decouples execution from HTTP request lifetime
2. **Long-Running:** Executions can exceed HTTP timeout limits
3. **Real-time Updates:** WebSocket streaming provides live progress
4. **Multiple Triggers:** API + webhook + scheduled can all queue
5. **Resource Efficiency:** Containers not tied to request/response

**Architecture:**
```
POST /projects/{id}/executions
    ↓
Create Execution record (QUEUED)
    ↓
Return execution ID immediately
    ↓
WebSocket /executions/{id}/stream
    ↓
Real-time progress events
```

**Queue Implementation:**
```python
# Execution status flow:
QUEUED → PREPARING → RUNNING → COMPLETED/FAILED

# Background worker processes queue:
while True:
    execution = await execution_repo.get_next_queued()
    async for event in execution_service.execute(execution.id):
        # Stream via WebSocket to connected clients
        await websocket.send_json(event)
```

**Consequences:**
- Need background worker/queue processor
- WebSocket handling complexity
- Polling not required (clients get pushed updates)
- Mitigation: Use established async patterns (APScheduler, asyncio)

---

## Decision 11: Security: Container Sandbox Level

**Context:**
How restrictive should execution container sandboxing be?

**Options Considered:**

| Level | Security | Flexibility | Risk | Use Case |
|-------|----------|------------|------|----------|
| 1: Full Privilege | Low | High | Critical | N/A (not acceptable) |
| 2: Root User | Low | High | Critical | N/A (not acceptable) |
| 3: Standard User + Capabilities | Medium | Medium | Medium | Default execution |
| 4: Read-only FS + User | High | Low | Low | Strict enforcement |
| 5: VM Isolation + Nested Containers | Maximum | None | Minimum | Only if needed |

**Decision: Level 4 (Read-only FS + Non-root User)**

**Rationale:**
1. **Sufficient Security:** Prevents accidental filesystem contamination
2. **Good UX:** Allows necessary operations (mounts, tmpfs)
3. **Performance:** No VM overhead
4. **Escaping Difficult:** Read-only root + non-root user + network isolation
5. **Auditable:** Can log all artifacts/changes

**Docker Configuration:**
```dockerfile
USER execuser:execuser
RUN chmod 755 /tmp /var/run
```

```yaml
# docker-compose
security_opt:
  - no-new-privileges:true
cap_drop:
  - ALL
cap_add:
  - NET_BIND_SERVICE
read_only_rootfs: true
tmpfs:
  - /run
  - /var/run
```

**Mounted Volumes:**
- `/codebase`: read-only (codebase access)
- `/tmp/execution`: tmpfs (scratch space)
- `/artifacts`: writable (output collection)

**Consequences:**
- Some tools/libraries might fail (require writable /opt, etc)
- tmpfs limited to container memory (not persistent)
- May need custom Dockerfiles for specific tools
- Mitigation: Test tooling in advance, document limitations

---

## Decision 12: Artifact Retention: Time-based vs Usage-based

**Context:**
Artifacts accumulate on disk. When should they be deleted?

**Options Considered:**

| Strategy | Simplicity | Cost Efficiency | User Control | Debugging Friendly |
|----------|-----------|-----------------|---------------|--------------------|
| No Deletion | Simple | Worst | None | Excellent (all history) |
| Time-based (TTL) | Simple | Good | Partial (config) | Good (recent) |
| Size-based | Moderate | Excellent | Auto (by policy) | Medium (oldest deleted) |
| Hybrid (time + size) | Complex | Excellent | Good | Good |
| On-demand (user deletes) | Simple | Worst | Excellent | Excellent |

**Decision: Time-based with Size Monitoring**

**Rationale:**
1. **Simplicity:** Single configuration (retention_days)
2. **Predictability:** Users know when artifacts expire
3. **Cost Control:** Prevents unbounded disk usage
4. **Debugging:** Sufficient retention for retrospective analysis
5. **Monitoring:** Can alert when disk usage high

**Default Policy:**
```python
retention_days = 30  # Configurable per project

# Daily cleanup (2 AM)
deleted = await artifact_service.cleanup_old_artifacts(
    retention_days=30
)

# Monitoring
if disk_usage > 90%:
    alert("Disk usage high")
    # Optional: aggressive cleanup, reduce retention
```

**Lifecycle:**
```
Execution created
    ↓ (T=0)
Artifacts stored
    ↓ (T=30 days)
Cleanup job runs
    ↓
Artifacts deleted
    ↓
Metadata retained (6 months)
```

**Consequences:**
- Old artifacts eventually deleted (not permanent)
- Cleanup can take time on large artifact stores
- Can't recover deleted artifacts
- Mitigation: Document retention policy, recommend archival exports

---

## Cross-Cutting Concerns

### Logging & Observability

**Pattern:** All execution steps logged with timestamps and status
```python
await logger.info("Execution started", extra={
    'execution_id': execution.id,
    'container_id': container.id,
    'type': execution.execution_type,
})
```

### Error Handling & Resilience

**Pattern:** Graceful degradation, partial results acceptable
```python
try:
    # Execute flow
except TimeoutError:
    # Mark as partial, save what we have
    execution.status = COMPLETED
    execution.result = PARTIAL
```

### Testing Strategy

**Unit Tests:** Services in isolation (mocked containers, APIs)
**Integration Tests:** Real containers, real media processing
**E2E Tests:** Full workflows (webhook → execution → artifacts)

### Monitoring & Alerts

**Metrics:**
- Execution success rate
- Average execution time
- Artifact storage usage
- Container resource usage

**Alerts:**
- Execution failure rate > 5%
- Disk usage > 90%
- Container startup timeout
- OAuth token refresh failure

---

## Implementation Priority

Based on dependencies:

1. **Critical Path:** Database schema → Execution service → Container manager
2. **High Value:** VHS integration → FFmpeg → Artifacts
3. **Enhancement:** Playwright → Codex CLI → Webhook triggers
4. **Polish:** Monitoring → Security hardening → Performance tuning

---

## Future Considerations

### Horizontal Scaling
- Currently: Single machine (Docker daemon)
- Future: Distributed execution (multiple hosts)
- Approach: Execution coordinator service, distributed queue

### Advanced Security
- Currently: Docker sandboxing
- Future: Nested VMs for execution isolation
- Approach: KVM/QEMU per execution (significant overhead)

### Artifact Management
- Currently: Local filesystem with TTL cleanup
- Future: Configurable backends (S3, GCS)
- Approach: Pluggable storage interface

### Agent Capabilities
- Currently: Codex CLI for code review, analysis
- Future: Autonomous action execution (with whitelist)
- Approach: Action validation framework, audit logging

---

## Conclusion

These architectural decisions provide a solid foundation for a local, secure, extensible execution environment system. Key tradeoffs:

1. **Security vs Convenience:** Prioritize user control, audit trails
2. **Simplicity vs Flexibility:** Start simple, extend incrementally
3. **Performance vs Cost:** Docker over serverless (local > cloud)
4. **Coupling vs Reuse:** Extend webhooks (existing patterns)

Next phase: Detailed implementation planning and Phase 1 execution.

