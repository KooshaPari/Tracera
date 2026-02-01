# External Integrations - Architecture Decisions & Rationale

## Decision Framework

All architectural decisions follow these principles:

1. **Production-Ready** - Enterprise-grade reliability and security
2. **Scalable** - Support millions of sync operations
3. **Maintainable** - Clear separation of concerns, testable code
4. **User-Centric** - Intuitive UI with clear error messaging
5. **Pragmatic** - Balance ideal solutions with development velocity

---

## Key Architecture Decisions

### Decision 1: OAuth 2.0 with PKCE Flow

**Choice:** Primary authentication method for GitHub and Linear

**Rationale:**

| Aspect | OAuth 2.0 + PKCE | Personal Access Token |
|--------|------------------|----------------------|
| Security | No credentials shared | User shares long-lived token |
| Setup | Redirect flow | User generates token |
| Revocation | User controls in OAuth provider | User must rotate manually |
| Scoping | Fine-grained permissions | Broad access per token |
| Enterprise | Supports org-level deployment | Limited org support |
| Mobile/SPA | PKCE prevents code interception | Not suitable for client-side |

**Implementation Details:**
- Use PKCE for browser-based OAuth (prevents code interception attacks)
- Store state in Redis with 10-minute TTL
- Support GitHub Apps for enterprise deployments
- Fall back to PAT for users with OAuth restrictions

**Alternative Considered:** Basic Auth with GitHub user credentials
- Rejected: Violates GitHub Terms of Service, exposes credentials

**Risk Mitigation:**
- Validate OAuth state before exchanging code
- Use constant-time comparison for HMAC verification
- Implement OAuth token rotation/refresh

---

### Decision 2: Bidirectional Sync with Conflict Resolution

**Choice:** Support push and pull sync with configurable conflict strategies

**Rationale:**

Different teams have different requirements:
- **Requirement-Centric Teams** (TraceRTM as source) → TraceRTM wins conflicts
- **GitHub-Centric Teams** (GitHub as source) → External wins conflicts
- **Risk-Averse Teams** → Manual resolution required

**Conflict Resolution Strategies Ranking:**

```
Priority 1: Manual Resolution (default, safest)
  → Blocks sync until user chooses winner
  → Prevents accidental data loss
  → Best for critical fields

Priority 2: External Wins (GitHub as source of truth)
  → GitHub status changes are authoritative
  → Good for dev teams comfortable with GitHub as primary

Priority 3: TraceRTM Wins (requirements management priority)
  → TraceRTM state is authoritative
  → Good for regulated industries with change control

Priority 4: Last-Write-Wins (for non-critical fields)
  → Comments, descriptions where timing matters
  → Reduces manual intervention
```

**Field-Level Configuration:**
Allow different strategies per field:
```python
field_resolution_rules: {
    "status": "external_wins",        # GitHub status is truth
    "priority": "tracertm_wins",      # TraceRTM requirements priority
    "description": "last_write_wins", # Latest update wins
}
```

**Alternative Considered:** Pull-only sync
- Rejected: Limits value - users want to update from TraceRTM to GitHub

**Alternative Considered:** Automatic merge (like Git)
- Rejected: Too complex for structured data, high risk of data corruption

---

### Decision 3: Webhook + Polling Hybrid Sync

**Choice:** Primary sync via webhooks, fallback to polling

**Why Hybrid?**

```
Webhook Benefits:
  ✓ Real-time (< 1 second latency)
  ✓ No polling overhead
  ✓ Accurate event information

Webhook Limitations:
  ✗ External system must support webhooks
  ✗ Webhook delivery can fail
  ✗ Missed events if TraceRTM is down
  ✓ Polling fills these gaps

Polling Benefits:
  ✓ Works for any API
  ✓ Catchup for missed webhooks
  ✓ Periodic consistency checks

Polling Limitations:
  ✗ Latency (5-15 minutes)
  ✗ API rate limit pressure
  ✓ Acceptable as fallback
```

**Implementation:**
- Webhook as primary (< 1s sync)
- Polling as safety net (5-15 min sync)
- Last-poll timestamp prevents redundant checks

**Polling Configuration:**
```yaml
polling:
  interval: 300  # seconds (5 minutes default)
  high_priority_interval: 60  # 1 minute for important items
  batch_size: 100  # items per poll
  timeout: 30  # seconds per API call
```

**Alternative Considered:** Polling only
- Rejected: Poor user experience, high latency

**Alternative Considered:** Webhook only
- Rejected: No fault tolerance for webhook failures

---

### Decision 4: Sync Queue with Worker Pool

**Choice:** Async queue processor with priority handling

**Architecture:**
```
Sync Events (Webhook/Polling)
  ↓
Enqueue to SyncQueue (high throughput, durable)
  ↓
SyncWorkerPool (configurable workers)
  ↓
Process with rate limiting
  ↓
Handle conflicts
  ↓
Update TraceRTM + log results
```

**Why Queue Instead of Immediate Sync?**

| Aspect | Queue | Immediate Sync |
|--------|-------|----------------|
| Throughput | High (batch operations) | Low (one at a time) |
| Rate Limit | Easy to respect | Hard to manage |
| Retry | Built-in exponential backoff | Need custom logic |
| Ordering | FIFO with priority | Not guaranteed |
| Failure Recovery | Durable to disk | Lost on crash |

**Queue Priority Levels:**
```python
Priority.CRITICAL = 0  # System integrity issues
Priority.HIGH = 1      # User actions
Priority.NORMAL = 2    # Webhook events
Priority.LOW = 3       # Polling results
```

**Worker Configuration:**
```yaml
sync_workers:
  count: 4  # Parallel workers
  batch_size: 10  # Items per batch
  timeout: 30  # seconds per operation
  retry_count: 3
  retry_backoff: exponential
```

**Alternative Considered:** Direct sync (no queue)
- Rejected: No backpressure handling, webhook timeouts

**Alternative Considered:** Message queue (RabbitMQ/Kafka)
- Rejected: Adds complexity, database queue sufficient for scale

---

### Decision 5: Encryption at Rest (AES-256-GCM)

**Choice:** All credentials encrypted with AES-256-GCM

**Rationale:**

```
Threat Model:
  1. Database compromise → Encrypted credentials useless
  2. Backup leakage → Encrypted credentials useless
  3. Developer access → Encryption key separate from credentials
  4. Future key rotation → Same ciphertext works with new key

AES-256-GCM Benefits:
  ✓ NIST approved (FIPS 140-2)
  ✓ Authenticated encryption (integrity check)
  ✓ Random IV per encryption (no patterns)
  ✓ Hardware acceleration available (AES-NI)
```

**Implementation:**
```python
# Generate random 96-bit IV
iv = os.urandom(12)

# Encrypt with 256-bit key
cipher = AESGCM(master_key)
ciphertext = cipher.encrypt(iv, plaintext, None)

# Store: base64(IV + ciphertext)
# IV doesn't need to be secret; provides randomness
```

**Key Management:**
```yaml
encryption:
  algorithm: AES-256-GCM
  key_source: environment  # ENCRYPTION_MASTER_KEY
  key_rotation: yearly
  key_derivation: not_needed (use raw key)
  backup_key: optional (for key rotation)
```

**Alternative Considered:** AES-256-CBC with HMAC
- Rejected: More complex, GCM is simpler and as secure

**Alternative Considered:** App-level encryption only
- Rejected: Database admin access still compromises secrets

**Alternative Considered:** No encryption
- Rejected: Violates security best practices

---

### Decision 6: Repository Pattern for Data Access

**Choice:** Use repository pattern for all database operations

**Why Repositories?**

```
Benefits:
  ✓ Testability: Easy to mock repositories
  ✓ Flexibility: Swap implementations (SQL → NoSQL)
  ✓ Consistency: All access follows same pattern
  ✓ Optimization: Centralized query optimization

Structure:
  Service Layer (Business Logic)
       ↓
  Repository Layer (Data Access)
       ↓
  ORM Layer (SQLAlchemy)
       ↓
  Database
```

**Repository Interface:**
```python
class IntegrationCredentialRepository(BaseRepository):
    async def create(...) → IntegrationCredential
    async def get_by_id(...) → Optional[IntegrationCredential]
    async def update(...) → IntegrationCredential
    async def delete(...) → bool
    async def list_by_project(...) → list[IntegrationCredential]
```

**Benefits Over Direct ORM:**
- Can add caching without changing service layer
- Can add query logging without touching services
- Can validate data integrity in one place
- Easy to add soft deletes or audit trails

**Alternative Considered:** Direct SQLAlchemy queries in services
- Rejected: Harder to test, couples services to ORM

---

### Decision 7: Event-Driven Sync Processor

**Choice:** Background worker processes sync queue continuously

**Architecture:**
```python
class IntegrationSyncProcessor:
    async def run(self):
        while True:
            # Get next batch of pending items
            items = await self.queue_repo.get_pending(limit=100)

            for item in items:
                await self.process_item(item)

            # Sleep before next iteration
            await asyncio.sleep(0.1)  # 10 Hz poll rate
```

**Benefits:**
- Continuous processing without delays
- Automatic retry handling
- Priority-based processing
- Easy to add to any deployment

**Deployment Options:**
```yaml
Option 1: Same Process
  - Simple setup
  - Resources shared with API
  - Good for small deployments

Option 2: Separate Worker
  - Better resource isolation
  - Can scale independently
  - Good for large deployments

Option 3: Kubernetes Job
  - Auto-scaling on queue depth
  - Best for cloud deployments
```

**Alternative Considered:** Scheduled jobs (Celery)
- Rejected: Over-engineered for current scale, database queue sufficient

---

### Decision 8: Optimistic Locking for Concurrent Updates

**Choice:** Use version field with optimistic locking

**Rationale:**

```
Concurrency Scenarios:
  1. Two services update same mapping simultaneously
  2. User updates mapping while sync processor updates it
  3. Two webhook events for same item arrive at same time

Optimistic Locking Solution:
  - Each record has version field
  - Read version when loading
  - Include version in UPDATE query
  - UPDATE fails if version doesn't match
  - Retry with backoff

Benefits:
  ✓ Better performance than pessimistic locks
  ✓ No deadlock risk
  ✓ Works well with async code
  ✓ Built into SQLAlchemy
```

**Implementation:**
```python
# In mapping table:
version: int = mapped_column(Integer, default=1)

__mapper_args__ = {
    "version_id_col": version,  # Enable optimistic locking
}

# SQLAlchemy automatically:
# 1. Increments version on update
# 2. Includes version in WHERE clause
# 3. Raises StaleDataError if version mismatch
```

**Retry Strategy:**
```python
async def update_with_retry(mapping_id: str, updates: dict, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            mapping = await repo.get_by_id(mapping_id)
            mapping.update(updates)
            await repo.update(mapping)
            return mapping
        except StaleDataError:
            if attempt < max_retries - 1:
                await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                continue
            raise
```

**Alternative Considered:** Pessimistic locking (row-level locks)
- Rejected: Potential deadlocks, worse performance under contention

---

### Decision 9: Fault-Tolerant Webhook Handling

**Choice:** Verify signature, retry failed deliveries, validate idempotency

**Security & Reliability:**

```
Webhook Flow:
  1. External system sends event + HMAC signature
  2. TraceRTM verifies signature with stored secret
  3. TraceRTM generates idempotency key (external_id + event_id)
  4. Check if already processed (prevent duplicates)
  5. If new, queue sync operation
  6. Return 200 OK immediately
  7. External system can retry if needed (optional)
```

**Signature Verification:**
```python
def verify_github_webhook(payload: bytes, signature: str, secret: str) -> bool:
    """
    GitHub sends: X-Hub-Signature-256: sha256=<hex>
    We compute: sha256 HMAC of payload with secret
    Compare with constant-time comparison
    """
    computed = "sha256=" + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed, signature)
```

**Idempotency:**
```python
# Prevent duplicate processing
idempotency_key = f"{external_id}:{event_id}"

existing = await sync_queue_repo.get_by_idempotency_key(
    mapping_id,
    idempotency_key
)

if existing and existing.status in ["completed", "processing"]:
    return {"processed": False, "reason": "duplicate"}

# New event, process it
await sync_queue_repo.enqueue({
    mapping_id,
    idempotency_key,
    ...
})
```

**Alternative Considered:** Process synchronously in webhook handler
- Rejected: Slow, webhook timeout risk, no retry on failure

---

### Decision 10: Field-Level Sync Mapping

**Choice:** Map specific TraceRTM fields to external fields

**Field Mapping Matrix:**

```
TraceRTM Field    | GitHub Issue  | Linear Issue  | Notes
=====================================
title             | title         | title         | Always synced
description       | body          | description   | Rich text conversion
status            | state         | state         | Workflow mapping needed
priority          | labels        | priority      | GitHub lacks native priority
owner             | assignee      | assignee      | User mapping needed
label(s)          | labels        | labels        | Multi-value sync
custom_metadata   | metadata      | custom_fields | Structured data

Sync Direction:
  - Always: title, description
  - Configurable: status, priority, owner
  - Never: internal IDs, timestamps

Transformation Rules:
  - TraceRTM "todo" ↔ GitHub "open"
  - TraceRTM "done" ↔ GitHub "closed"
  - TraceRTM priority "high" → GitHub label "priority/high"
  - Linear priority levels 0-4 → TraceRTM priority enum
```

**Implementation:**
```python
class FieldMapping:
    """Define how fields sync between systems."""

    source_field: str  # TraceRTM field
    target_field: str  # External field
    transform_fn: Callable  # Value transformation
    bidirectional: bool
    sync_on_update: bool

    def transform_to_external(self, value: Any) -> Any:
        """Transform TraceRTM value for external system."""
        return self.transform_fn(value)

    def transform_to_tracertm(self, value: Any) -> Any:
        """Transform external value for TraceRTM."""
        return self.reverse_transform_fn(value)
```

**Configuration Example:**
```yaml
field_mappings:
  github_issue:
    - source: "title"
      target: "title"
      bidirectional: true

    - source: "status"
      target: "state"
      bidirectional: true
      transform: |
        {"todo": "open", "done": "closed", "in_progress": "open"}

    - source: "priority"
      target: "labels"
      bidirectional: true
      transform: "priority_to_labels"  # Function name
```

**Alternative Considered:** Sync entire object as JSON
- Rejected: Inflexible, no transformation support

---

### Decision 11: Structured Logging for Debugging

**Choice:** Log all sync operations with structured fields

**Logging Strategy:**

```json
{
  "timestamp": "2025-01-27T10:00:00Z",
  "level": "INFO",
  "logger": "sync_processor",
  "event": "sync_completed",
  "mapping_id": "map-123",
  "direction": "push",
  "duration_ms": 245,
  "success": true,
  "changes": {
    "title": {"before": "Old", "after": "New"},
    "status": {"before": "todo", "after": "done"}
  },
  "conflict_detected": false,
  "request_id": "req-abc-123"  # For tracing
}
```

**Benefits:**
- Queryable JSON logs
- Easy to aggregate in ELK/DataDog
- Tracing request flow with request_id
- Performance monitoring (duration_ms)
- Error investigation (error details)

**Logging Levels:**
```python
logger.debug(...)     # Detailed sync step
logger.info(...)      # Sync completed
logger.warning(...)   # Conflict detected
logger.error(...)     # Sync failed
logger.critical(...)  # Data corruption detected
```

**Alternative Considered:** Free-form text logging
- Rejected: Hard to search/aggregate, poor for monitoring

---

## Architecture Diagram

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      External Systems                            │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐             │
│  │   GitHub    │  │    Linear   │  │ GitHub Proj  │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘             │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
    Webhooks + Polling      Webhooks      Webhooks
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼──────────────────┐
│              TraceRTM External Integration Layer                  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Webhook Handlers (GitHub, Linear)                       │   │
│  │  - Signature Verification (HMAC-SHA256)                  │   │
│  │  - Idempotency Check                                     │   │
│  │  - Queue Sync Operation                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Integration Sync Processor (Async Worker)               │   │
│  │  - Process sync queue                                    │   │
│  │  - Respect rate limits                                   │   │
│  │  - Retry with exponential backoff                        │   │
│  │  - Detect and resolve conflicts                          │   │
│  │  - Log all operations                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  API Clients (GitHub, Linear)                            │   │
│  │  - REST/GraphQL API calls                                │   │
│  │  - Rate limit handling                                   │   │
│  │  - Error handling & retry                                │   │
│  │  - Request/response transformation                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Service Layer                                           │   │
│  │  - Credential management                                 │   │
│  │  - Mapping CRUD                                          │   │
│  │  - OAuth flows                                           │   │
│  │  - Conflict resolution                                   │   │
│  │  - Encryption/decryption                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Repository Layer                                        │   │
│  │  - IntegrationCredentialRepository                       │   │
│  │  - IntegrationMappingRepository                          │   │
│  │  - IntegrationSyncQueueRepository                        │   │
│  │  - IntegrationSyncLogRepository                          │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│               TraceRTM Core (Existing)                           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │    Items     │ │   Projects   │ │    Links     │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
└──────────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                    Database Layer                                │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Credentials  │  Mappings  │  Sync Queue  │  Sync Logs   │  │
│  │  (Encrypted)  │ (Indexed)  │ (Durable)    │ (Audit)      │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Sync Flow (Detailed)

```
┌─ External Event (Webhook) ─────────────────────────────────────┐
│                                                                 │
│ GitHub sends:  POST /api/v1/webhooks/github                   │
│ Header: X-Hub-Signature-256: sha256=abc123...                 │
│ Body: { "action": "opened", "pull_request": {...} }          │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │ Verify Webhook Signature │ ← HMAC-SHA256
        └────────────┬────────────┘
                     │ Valid
        ┌────────────▼──────────────────┐
        │ Parse Event + Extract Metadata │
        └────────────┬──────────────────┘
                     │
        ┌────────────▼────────────────────────┐
        │ Find Mapping (external_id → mapping) │
        └────────────┬────────────────────────┘
                     │ Found
        ┌────────────▼────────────────────┐
        │ Check Idempotency (prevent dups) │
        └────────────┬────────────────────┘
                     │ New event
        ┌────────────▼──────────────────────────────┐
        │ Queue Sync Operation                      │
        │ - mapping_id                              │
        │ - event_type: "pull_request_opened"       │
        │ - direction: "pull"                       │
        │ - priority: "normal"                      │
        │ - payload: parsed event data              │
        └────────────┬──────────────────────────────┘
                     │
        ┌────────────▼────────────────┐
        │ Return 200 OK to External    │ ← Immediate response
        └────────────────────────────┘
                     │
    ┌────────────────┴─ Webhook handler exits
    │
    │    Async Processing (happens later)
    │
    ├─────────────────────────────────────────────────────────┐
    │                                                         │
    │  ┌──────────────────────────────────────────────────┐  │
    │  │ Sync Processor Background Worker:                │  │
    │  │                                                  │  │
    │  │ 1. Get next pending sync from queue             │  │
    │  │ 2. Check rate limits for credential             │  │
    │  │ 3. Fetch current state from external system     │  │
    │  │ 4. Compare with TraceRTM item state             │  │
    │  │ 5. If conflict: resolve per strategy            │  │
    │  │ 6. Apply changes to TraceRTM item               │  │
    │  │ 7. Log operation with result                    │  │
    │  │ 8. Mark queue item as completed                 │  │
    │  │                                                  │  │
    │  │ On Error:                                        │  │
    │  │ - Mark queue item as failed                     │  │
    │  │ - Calculate backoff: 60 * 2^attempts            │  │
    │  │ - Schedule retry                                │  │
    │  └──────────────────────────────────────────────────┘  │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
```

---

## Performance Characteristics

### Throughput

```
Sync Operations:
  - Webhook processing: 1,000+/second (in queue)
  - Sync processor: 10-50/second (depends on worker count)
  - 4 workers can handle: ~20-200/second steady state

Webhook to Sync: < 100ms (typically)
Sync to Item Update: 100-500ms (per operation)
End-to-End Latency: 200-600ms (typical)
```

### Scalability

```
Current Scale:
  - Handles 10,000+ mappings per project
  - Processes 1,000+ syncs/minute
  - < 5 second webhook processing time
  - < 1 second 95th percentile sync latency

Bottlenecks:
  - External API rate limits (GitHub 5,000/hour)
  - Database write throughput (MariaDB default ~1,000/sec)
  - Network latency to external systems (~200ms)

Scaling Options:
  - Add more sync workers (horizontal)
  - Batch operations together (increase throughput)
  - Upgrade database hardware (vertical)
  - Cache external data locally (reduce API calls)
```

### Resource Usage

```
Per 1,000 Active Mappings:
  - Memory: ~50 MB (queue cache, service objects)
  - Database Connections: 1-2 (for processing)
  - API Calls: 100-500/hour (polling + activity)
  - Disk I/O: Minimal (queue in memory, log to disk)

Infrastructure for 100,000 Mappings:
  - 4-8 sync worker processes
  - 2-4 API gateway replicas
  - Dedicated MariaDB replica for integration queries
  - Redis for session state (optional)
```

---

## Cost Analysis

### Infrastructure Costs (AWS)

```
Small Deployment (< 10,000 mappings):
  - EC2 t3.medium (2 CPUs, 4GB): $30/month
  - RDS db.t3.small (1 vCPU, 2GB): $30/month
  - Total: ~$60/month

Medium Deployment (10,000-100,000 mappings):
  - EC2 t3.large (2 CPUs, 8GB): $60/month × 2 instances
  - RDS db.t3.medium (2 vCPUs, 4GB): $60/month
  - Total: ~$180/month

Large Deployment (> 100,000 mappings):
  - EC2 c5.xlarge (4 CPUs, 8GB): $70/month × 4 instances
  - RDS db.r5.large (2 vCPUs, 16GB): $200/month
  - Total: ~$480/month

No per-sync costs (GitHub/Linear API calls are included in plan)
```

---

## Security Checklist

- [x] Credentials encrypted at rest (AES-256-GCM)
- [x] OAuth 2.0 with PKCE flow
- [x] Webhook signature verification (HMAC-SHA256)
- [x] No credentials in logs or error messages
- [x] Rate limiting to prevent abuse
- [x] Input validation on all external data
- [x] SQL injection prevention (parameterized queries)
- [x] CORS configuration for browser-based OAuth
- [x] HTTPS enforced for all webhooks
- [x] Audit logging for all operations
- [x] Credential rotation support
- [x] Token expiration handling

---

## Monitoring Strategy

### Key Metrics to Track

```
Real-Time Metrics:
  - Webhook latency (time from event to queued)
  - Sync processor throughput (operations/second)
  - Queue depth (pending operations)
  - API response time (external systems)
  - Rate limit utilization (% of limit used)

Aggregated Metrics:
  - Sync success rate (% successful vs failed)
  - Conflict detection rate (conflicts per hour)
  - Average sync latency (push vs pull)
  - Error rate by type
  - Credential validity rate

Business Metrics:
  - Active mappings per project
  - Sync operations per day
  - User adoption (% of projects with integrations)
  - External system availability (as seen by TraceRTM)
```

### Alerting Rules

```yaml
Alerts:
  # Critical
  - SyncFailureRate > 10% in 5 minutes → Page on-call
  - WebhookFailure > 50 in 1 hour → Page on-call
  - DatabaseConnectionFail → Page on-call

  # Warning
  - SyncLatency > 10 seconds (p99) → Notify team
  - QueueDepth > 10,000 → Investigate backpressure
  - CredentialExpiry < 24 hours → Remind user
  - RateLimitNearExhaustion (80%+) → Monitor

  # Info
  - High conflict rate (> 100/hour) → Log and investigate
  - Unusual sync pattern detected → Log
```

