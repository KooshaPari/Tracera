# Phase 6: Production Hardening & Optimization

**Status:** LAUNCHING
**Date:** 2026-02-06 03:05 UTC
**Scope:** 4-track parallel execution (Python, Performance, Security, Deployment)
**Timeline:** 26 hours wall-clock (aggressive parallelization)
**Target:** Production-ready codebase with full hardening

---

## PHASE 6 SCOPE: 4 PARALLEL TRACKS

### Track 1: Python Code Quality (8h wall-clock)
**Responsible:** python-quality-lead

**6.1 TODO Resolution (4h)**
- Audit all 45+ TODO comments in Python codebase
- Classify: bug-fix vs optimization vs documentation
- Implement or document decision for each
- Target: 0 outstanding TODOs

**6.2 Docstring Coverage (2h)**
- Add docstrings to all public functions/classes
- Target: 100% coverage (currently ~70%)
- Format: Google-style docstrings

**6.3 Type Annotation Completion (2h)**
- Full type hints for all public APIs
- Target: 0 untyped returns/parameters
- mypy --strict validation

### Track 2: Performance Optimization (6h wall-clock)
**Responsible:** performance-optimizer

**6.4 Dashboard N+1 Query Fix (2h)**
- Audit GraphQL resolver patterns
- Implement dataloader caching
- Target: <200ms dashboard load (vs current ~800ms)

**6.5 React Query Optimization (2h)**
- Audit React Query cache keys
- Fix stale-while-revalidate patterns
- Target: LCP <2.5s (vs current ~3.2s)

**6.6 Backend Caching Strategy (2h)**
- Implement Redis caching for hot paths
- TTL strategy for different entity types
- Target: Cache hit rate >80%

### Track 3: Security Hardening (6h wall-clock)
**Responsible:** security-auditor

**6.7 CSRF Protection (1h)**
- Add CSRF tokens to all state-changing endpoints
- Validate on backend

**6.8 XSS Prevention (1.5h)**
- Audit all user-input handling
- Implement Content-Security-Policy headers
- DOMPurify integration for rich content

**6.9 Rate Limiting (1.5h)**
- Implement per-user rate limiting
- Redis-backed counter store
- Target: 100 req/min per user

**6.10 WebSocket Auth Refresh (1h)**
- Implement token refresh in WebSocket handler
- Prevent auth bypass via stale tokens

**6.11 Data Encryption (1.5h)**
- Encrypt PII in database (emails, names)
- Use AES-256-GCM with key rotation

### Track 4: Deployment Readiness (6h wall-clock)
**Responsible:** deployment-lead

**6.12 Config Validation (1h)**
- Create preflight checks for all required config vars
- Fail fast on startup if missing
- Document all env vars with examples

**6.13 Database Migrations (2h)**
- Create migration scripts for schema changes
- Test against staging environment
- Rollback procedures documented

**6.14 Health Check Endpoints (1h)**
- Implement /health endpoint with detailed status
- Check: DB, Redis, NATS connectivity
- Return 503 if any critical dependency unavailable

**6.15 Monitoring & Alerting (1.5h)**
- Add Prometheus metrics
- Alert rules for high error rate (>5%)
- Alert for performance degradation (>2x baseline)

**6.16 Orchestration & Scaling (0.5h)**
- Docker Compose for local dev
- Kubernetes deployment templates
- Helm charts for production scaling

---

## EXECUTION MODEL

### Track Independence
- ✅ All 4 tracks fully independent (no cross-blocking)
- ✅ Can execute in parallel
- ✅ No shared resources beyond codebase

### Timeline (Parallel)
```
Wall-Clock: 6 hours (max track duration)
- Track 1 (Python): 8h → runs longest
- Track 2 (Performance): 6h
- Track 3 (Security): 6h
- Track 4 (Deployment): 6h

Total Wall-Clock: 8 hours (vs 26h sequential = 70% faster)
```

### Resource Allocation
```
4 specialized teams:
- python-quality-lead (Track 1)
- performance-optimizer (Track 2)
- security-auditor (Track 3)
- deployment-lead (Track 4)

All executing in parallel with no dependencies
```

---

## TRACK 1: PYTHON CODE QUALITY (8h)

### 6.1 TODO Resolution (4h)

**Process:**
1. Find all TODOs: `grep -r "TODO\|FIXME" src/tracertm/`
2. Classify each:
   - Bug (fix now)
   - Optimization (optional, document)
   - Documentation (add docstring)
3. Implement or document decision
4. Verify: 0 outstanding TODOs

**Example Fix:**
```python
# Before
def process_graph(graph):
    # TODO: Add caching for large graphs
    return expensive_computation(graph)

# After
@cache.cached(timeout=3600)
def process_graph(graph):
    """Process graph with memoized caching for performance."""
    return expensive_computation(graph)
```

### 6.2 Docstring Coverage (2h)

**Target:** 100% of public APIs

**Format:**
```python
def create_project(name: str, description: str) -> Project:
    """Create a new project.

    Args:
        name: Project name (max 100 chars)
        description: Project description (optional)

    Returns:
        Created Project object with auto-generated ID

    Raises:
        ValueError: If name is empty or exceeds max length
        DuplicateProjectError: If project with this name exists
    """
```

### 6.3 Type Annotations (2h)

**Target:** mypy --strict clean

**Current State:** ~70% annotated
**Target:** 100% annotated

**Example:**
```python
from typing import Optional, List

def get_user_projects(
    user_id: str,
    include_archived: bool = False
) -> List[Project]:
    """Get all projects for a user."""
```

---

## TRACK 2: PERFORMANCE OPTIMIZATION (6h)

### 6.4 Dashboard N+1 Fix (2h)

**Problem:** Dashboard query fetches projects, then individual items for each
**Solution:** GraphQL dataloader pattern

**Implementation:**
```typescript
// Before: N+1 queries
const projects = await db.project.find({userId});
const items = projects.map(p => db.item.find({projectId: p.id}));

// After: Batched query
const loader = new DataLoader(async (projectIds) => {
  return db.item.find({projectId: {in: projectIds}});
});

for (const project of projects) {
  project.items = await loader.load(project.id);
}
```

**Target:** Dashboard load <200ms (vs current ~800ms)

### 6.5 React Query Cache (2h)

**Problem:** React Query cache keys not optimized
**Solution:** Implement proper cache key strategy

**Implementation:**
```typescript
// Before: Generic keys
useQuery(['projects'], fetchProjects);
useQuery(['items'], fetchItems);

// After: Scoped keys
useQuery(['projects', userId], () => fetchProjects(userId));
useQuery(['items', projectId], () => fetchItems(projectId));
```

**Target:** LCP <2.5s (vs current ~3.2s)

### 6.6 Redis Caching (2h)

**Caching Strategy:**
```
Hot paths:
- User profile: TTL 1h
- Project list: TTL 5min
- Recent items: TTL 1min
- Graph layout: TTL 15min

Target: 80%+ cache hit rate
```

---

## TRACK 3: SECURITY HARDENING (6h)

### 6.7 CSRF Protection (1h)

**Implementation:**
```typescript
// Generate CSRF token
app.get('/csrf-token', (req, res) => {
  res.json({ token: generateCSRFToken(req.session) });
});

// Validate on POST/PUT/DELETE
app.post('/projects', validateCSRFToken, (req, res) => {
  // Handle request
});
```

### 6.8 XSS Prevention (1.5h)

**Content-Security-Policy:**
```
default-src 'self'
script-src 'self' 'unsafe-inline' (remove unsafe)
style-src 'self' 'unsafe-inline'
img-src 'self' https:
connect-src 'self' wss:
```

**DOMPurify Integration:**
```typescript
import DOMPurify from 'dompurify';

// Sanitize user input
const cleanHTML = DOMPurify.sanitize(userInput);
```

### 6.9 Rate Limiting (1.5h)

**Per-User Limits:**
```
- API: 100 req/min
- WebSocket: 10 messages/sec
- File upload: 5 files/min (100MB total)
- Search: 20 queries/min
```

### 6.10 WebSocket Auth (1h)

**Token Refresh:**
```typescript
// Refresh token before expiry
const tokenRefresh = setInterval(() => {
  const newToken = await refreshToken();
  ws.send({type: 'AUTH_REFRESH', token: newToken});
}, 4*60*1000); // Every 4 minutes
```

### 6.11 Data Encryption (1.5h)

**PII Encryption:**
```python
from cryptography.fernet import Fernet

cipher = Fernet(key)

# Encrypt on write
user.email = cipher.encrypt(user.email)

# Decrypt on read
email = cipher.decrypt(user.email)
```

---

## TRACK 4: DEPLOYMENT READINESS (6h)

### 6.12 Config Validation (1h)

**Preflight Checks:**
```go
func validateConfig() error {
  required := []string{
    "DATABASE_URL",
    "REDIS_URL",
    "NATS_URL",
    "JWT_SECRET",
    "OAUTH_CLIENT_ID",
  }

  for _, env := range required {
    if os.Getenv(env) == "" {
      return fmt.Errorf("missing required config: %s", env)
    }
  }
  return nil
}
```

### 6.13 Database Migrations (2h)

**Migration Framework:**
```go
// Run migrations
func runMigrations(db *sql.DB) error {
  return goose.Up(db, "./migrations")
}

// Migration file: migrations/001_initial.sql
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.14 Health Checks (1h)

**Endpoint:** `/health`

**Response:**
```json
{
  "status": "healthy",
  "checks": {
    "database": "up",
    "redis": "up",
    "nats": "up"
  },
  "timestamp": "2026-02-06T03:05:00Z"
}
```

### 6.15 Monitoring (1.5h)

**Prometheus Metrics:**
```
- http_requests_total (counter)
- http_request_duration_seconds (histogram)
- db_query_duration_seconds (histogram)
- websocket_connections_active (gauge)
- cache_hit_rate (gauge)
```

**Alert Rules:**
```
- ErrorRate > 5% for 5 minutes
- ResponseTime > 2x baseline for 10 minutes
- DiskUsage > 85%
- MemoryUsage > 90%
```

### 6.16 Orchestration (0.5h)

**Docker Compose:**
```yaml
services:
  app:
    build: .
    ports: ["3000:3000"]
  postgres:
    image: postgres:15
  redis:
    image: redis:7
  nats:
    image: nats:2.9
```

---

## SUCCESS CRITERIA

### Track 1: Python Quality ✅
- [ ] 0 outstanding TODOs
- [ ] 100% docstring coverage
- [ ] mypy --strict clean (0 errors)

### Track 2: Performance ✅
- [ ] Dashboard load <200ms
- [ ] LCP <2.5s
- [ ] Cache hit rate >80%

### Track 3: Security ✅
- [ ] CSRF protection on all state changes
- [ ] CSP headers deployed
- [ ] Rate limiting active
- [ ] WebSocket auth refresh working
- [ ] PII encrypted in database

### Track 4: Deployment ✅
- [ ] Preflight checks passing
- [ ] Migrations validated
- [ ] Health checks returning proper status
- [ ] Prometheus metrics flowing
- [ ] Docker/Kubernetes ready

---

## TIMELINE

| Phase | Duration | Activities |
|-------|----------|-----------|
| Setup | 30 min | Agent briefing, environment setup |
| Execution | 6-8h | 4 tracks in parallel |
| Validation | 1h | Cross-track verification |
| **Total** | **7-9h** | Complete production readiness |

**Comparison:**
- Sequential: 26 hours
- Parallel: 7-9 hours
- Savings: **70% time reduction**

---

## RESOURCE COORDINATION

**Respect Active Agents:**
- Avoid modifying files actively being edited (Gaps 5.3, 5.5, 5.6-5.8)
- Phase 6 tracks operate on separate codebase areas:
  - Track 1: Python (src/tracertm/)
  - Track 2: Frontend/Backend performance
  - Track 3: Security (auth, middleware, encryption)
  - Track 4: Deployment (config, orchestration)

**Non-Blocking:**
- All tracks can proceed simultaneously
- No cross-dependencies between tracks
- Zero risk of merge conflicts (different areas)

---

## NEXT STEPS

1. ✅ Create Phase 6 tasks (4 for each track)
2. ✅ Assign specialized agents
3. ✅ Execute in parallel (4 tracks, 6-8h total)
4. ✅ Validate completion
5. ✅ Production deployment ready

---

**PHASE 6 STATUS: READY FOR LAUNCH** 🚀

Awaiting go-ahead to spawn 4 parallel teams.
