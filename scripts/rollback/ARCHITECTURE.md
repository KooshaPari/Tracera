# Rollback System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Automated Rollback System                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Health Monitoring                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐ │
│  │ Prometheus │  │   Health   │  │  Service   │  │  Memory   │ │
│  │   Queries  │  │  Endpoints │  │   Status   │  │   Usage   │ │
│  └────────────┘  └────────────┘  └────────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Trigger Detection                           │
│  • Error Rate >5%                                               │
│  • Latency >2x baseline                                         │
│  • Service Down                                                 │
│  • Database Failure                                             │
│  • Cascading Failures                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Rollback Orchestrator                          │
│                     (rollback.sh)                                │
│  • State Management                                             │
│  • Component Coordination                                       │
│  • Timing Tracking                                              │
│  • Health Verification                                          │
└─────────────────────────────────────────────────────────────────┘
              │               │               │
              ▼               ▼               ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  Frontend   │  │   Backend   │  │  Database   │
    │  Rollback   │  │  Rollback   │  │  Rollback   │
    └─────────────┘  └─────────────┘  └─────────────┘
              │               │               │
              ▼               ▼               ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │   Restore   │  │   Restore   │  │   Restore   │
    │  Snapshot   │  │  Binary +   │  │  Database   │
    │             │  │    Code     │  │   Backup    │
    └─────────────┘  └─────────────┘  └─────────────┘
              │               │               │
              └───────────────┴───────────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │  Health Verification      │
              │  • Service Endpoints      │
              │  • Critical Routes        │
              │  • Database Connectivity  │
              └───────────────────────────┘
```

## Component Architecture

### 1. Health Monitor Daemon

```
┌───────────────────────────────────────────┐
│     health-monitor.sh (daemon)            │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │  Monitoring Loop (every 30s)        │ │
│  │                                     │ │
│  │  1. Query Prometheus                │ │
│  │  2. Check Service Health            │ │
│  │  3. Evaluate Thresholds             │ │
│  │  4. Check Cooldown Period           │ │
│  │  5. Trigger Rollback if Needed      │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  Metrics:                                 │
│  • Error Rate (5m window)                 │
│  • P95 Latency vs Baseline                │
│  • Service Up/Down Status                 │
│  • Memory Usage                           │
│  • Disk Usage                             │
└───────────────────────────────────────────┘
```

### 2. Rollback Orchestrator

```
┌───────────────────────────────────────────┐
│         rollback.sh (orchestrator)        │
│                                           │
│  Main Functions:                          │
│  ┌─────────────────────────────────────┐ │
│  │ check()                             │ │
│  │  → Evaluate health metrics          │ │
│  │  → Return rollback needed status    │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │ perform_rollback(component)         │ │
│  │  → Initialize state tracking        │ │
│  │  → Call component rollback scripts  │ │
│  │  → Measure timing                   │ │
│  │  → Verify health                    │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  ┌─────────────────────────────────────┐ │
│  │ create_deployment_snapshot()        │ │
│  │  → Backup current deployment        │ │
│  │  → Mark as stable version           │ │
│  └─────────────────────────────────────┘ │
│                                           │
│  State File: rollback-state.json          │
│  {                                        │
│    "rollback_start": "timestamp",         │
│    "trigger_reason": "reason",            │
│    "status": "in_progress|completed",     │
│    "components": {...}                    │
│  }                                        │
└───────────────────────────────────────────┘
```

### 3. Component Rollback Scripts

#### Frontend Rollback
```
┌────────────────────────────────┐
│  rollback-frontend.sh          │
│                                │
│  1. Get stable version         │
│  2. Verify snapshot exists     │
│  3. Backup current deployment  │
│  4. Stop frontend service      │
│  5. Extract snapshot           │
│  6. Restart service            │
│  7. Wait for health (60s max)  │
│                                │
│  Artifacts:                    │
│  • dist/ build directory       │
│  • Compressed tar.gz snapshot  │
│                                │
│  Target: <30 seconds           │
└────────────────────────────────┘
```

#### Backend Rollback
```
┌────────────────────────────────┐
│  rollback-backend.sh           │
│                                │
│  Go Backend:                   │
│  1. Get stable version         │
│  2. Verify binary snapshot     │
│  3. Stop service               │
│  4. Restore binary             │
│  5. Restart service            │
│                                │
│  Python Backend:               │
│  1. Get stable version         │
│  2. Verify code snapshot       │
│  3. Stop service               │
│  4. Restore code               │
│  5. Reinstall dependencies     │
│  6. Restart service            │
│                                │
│  7. Verify both healthy        │
│                                │
│  Target: <60 seconds           │
└────────────────────────────────┘
```

#### Database Rollback
```
┌────────────────────────────────┐
│  rollback-database.sh          │
│                                │
│  1. Create pre-rollback backup │
│  2. Get stable version         │
│                                │
│  Migration-based (fast):       │
│  3a. Use Alembic downgrade     │
│  3b. Verify success            │
│                                │
│  Snapshot-based (fallback):    │
│  4a. Terminate connections     │
│  4b. Drop database             │
│  4c. Create database           │
│  4d. Restore from backup       │
│                                │
│  5. Verify critical tables     │
│                                │
│  Target: <45 seconds           │
└────────────────────────────────┘
```

## Data Flow

### Deployment Flow (Normal)

```
Developer                  CI/CD                System
    │                        │                    │
    │  git push              │                    │
    ├───────────────────────>│                    │
    │                        │                    │
    │                        │  Build & Test      │
    │                        │                    │
    │                        │  Create Snapshots  │
    │                        ├───────────────────>│
    │                        │                    │ .deployments/snapshots/
    │                        │                    │   frontend/v1.2.3.tar.gz
    │                        │                    │   backend/go-v1.2.3
    │                        │                    │   database/v1.2.3.sql
    │                        │                    │
    │                        │  Deploy            │
    │                        ├───────────────────>│
    │                        │                    │
    │                        │  Mark Stable       │
    │                        ├───────────────────>│
    │                        │                    │ *-stable-version.txt
    │                        │                    │   → v1.2.3
```

### Rollback Flow (Failure)

```
Monitor                 Orchestrator            Components
    │                        │                        │
    │  Detect Issue          │                        │
    │  (error rate >5%)      │                        │
    │                        │                        │
    │  Trigger Rollback      │                        │
    ├───────────────────────>│                        │
    │                        │                        │
    │                        │  Init State            │
    │                        │  (rollback-state.json) │
    │                        │                        │
    │                        │  Rollback Frontend     │
    │                        ├───────────────────────>│
    │                        │                        │ 1. Stop service
    │                        │                        │ 2. Restore snapshot
    │                        │<───────────────────────│ 3. Restart
    │                        │  Success               │
    │                        │                        │
    │                        │  Rollback Backend      │
    │                        ├───────────────────────>│
    │                        │                        │ 1. Stop services
    │                        │                        │ 2. Restore binaries
    │                        │<───────────────────────│ 3. Restart
    │                        │  Success               │
    │                        │                        │
    │                        │  Rollback Database     │
    │                        ├───────────────────────>│
    │                        │                        │ 1. Backup current
    │                        │                        │ 2. Restore snapshot
    │                        │<───────────────────────│ 3. Verify
    │                        │  Success               │
    │                        │                        │
    │                        │  Verify Health         │
    │                        │                        │
    │  Notification          │                        │
    │<───────────────────────│                        │
    │  (Rollback Complete)   │                        │
```

## Storage Architecture

```
.deployments/
├── snapshots/
│   ├── frontend/
│   │   ├── v1.2.3.tar.gz       (Current stable)
│   │   ├── v1.2.2.tar.gz       (Previous)
│   │   └── v1.2.1.tar.gz       (Older)
│   ├── backend/
│   │   ├── go-v1.2.3           (Go binary)
│   │   ├── python-v1.2.3.tar.gz (Python code)
│   │   └── ...
│   └── database/
│       ├── v1.2.3.sql.gz       (Compressed backup)
│       ├── v1.2.2.sql.gz
│       └── ...
│
├── backups/                    (Pre-rollback safety)
│   ├── frontend/
│   │   └── 20240201120000.tar.gz
│   ├── backend/
│   │   ├── go/
│   │   └── python/
│   └── database/
│       └── pre-rollback-20240201120000.sql.gz
│
├── frontend-stable-version.txt  → "v1.2.3"
├── backend-stable-version.txt   → "v1.2.3"
└── database-stable-version.txt  → "v1.2.3"

.rollback-logs/
├── rollback.log                (Operations log)
├── health-monitor.log          (Monitor daemon log)
├── rollback-state.json         (Current state)
└── last-rollback-time          (Cooldown tracking)
```

## Integration Points

### Prometheus Integration

```
Health Monitor ──Query API──> Prometheus
                              │
                              ├─> http_requests_total{status=~"5.."}
                              ├─> http_request_duration_seconds_bucket
                              ├─> up{job="go-backend"}
                              └─> process_resident_memory_bytes

Prometheus ──Alert Rules──> Alertmanager
                            │
                            └─> Notifications
                                (PagerDuty, Slack, etc.)
```

### Service Management

```
Rollback Scripts ──Control──> Process Compose
                              │
                              ├─> process-compose restart frontend
                              ├─> process-compose stop go-backend
                              └─> process-compose start python-backend

                  ──OR──────> Systemd
                              │
                              ├─> systemctl restart tracertm-frontend
                              └─> systemctl restart tracertm-backend
```

## Timing Breakdown

```
Total Rollback: <2 minutes
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Detection        │████████│ 15-30s                         │
│  Decision         │██│ 2-5s                                 │
│  Frontend         │███████│ 20-30s                          │
│  Backend          │███████████████│ 40-60s                  │
│  Database         │████████████│ 30-45s                     │
│  Verification     │█████│ 10-20s                            │
│                                                             │
│  0        30        60        90       120      150    180s │
└─────────────────────────────────────────────────────────────┘
                                        └─ Target: 120s

Typical: 100-140s
Maximum: 190s
```

## Security Model

```
┌───────────────────────────────────────────┐
│         Security Layers                   │
│                                           │
│  1. Access Control                        │
│     • Script execution permissions        │
│     • Operator group membership           │
│     • Sudo requirements (production)      │
│                                           │
│  2. Credential Protection                 │
│     • Environment variables               │
│     • Vault integration (optional)        │
│     • No hardcoded passwords              │
│                                           │
│  3. Audit Logging                         │
│     • All operations logged               │
│     • Timestamped state changes           │
│     • Syslog/journald integration         │
│                                           │
│  4. Snapshot Integrity                    │
│     • SHA256 checksums (future)           │
│     • Encryption at rest (future)         │
│     • Access logging                      │
│                                           │
│  5. Approval Workflow (production)        │
│     • Manual approval for critical        │
│     • Multi-factor authentication         │
│     • Emergency break-glass procedures    │
└───────────────────────────────────────────┘
```

## Failure Modes & Recovery

### Rollback Failure Scenarios

1. **Snapshot Not Found**
   - Fallback: Use previous stable version
   - Alert: Page on-call team
   - Manual: Deploy last known good version

2. **Service Won't Start**
   - Retry: 3 attempts with backoff
   - Fallback: Manual intervention
   - Escalation: On-call engineer

3. **Database Corruption**
   - Pre-rollback backup exists
   - Manual restore procedure
   - Point-in-time recovery option

4. **Cascading Failures**
   - Cooldown period prevents loops
   - Manual override available
   - Emergency procedures documented

## Performance Characteristics

### Resource Usage

```
Health Monitor:
  CPU: <10% (30s intervals)
  Memory: <256MB
  Disk I/O: Minimal (log writing)

Rollback Operation:
  CPU: Spike during archive extraction
  Memory: Proportional to snapshot size
  Disk I/O: High during restore
  Network: Minimal (local operations)
```

### Scalability

- Supports single-instance deployments
- Multi-instance requires coordination (future)
- Database rollback assumes single primary
- Frontend/backend can scale independently

## Future Architecture Enhancements

1. **Multi-Region Support**
   - Coordinated rollbacks across regions
   - Regional snapshot replication
   - Cross-region health aggregation

2. **Canary Rollback**
   - Partial rollback to subset of instances
   - Progressive rollback strategy
   - A/B testing integration

3. **Predictive Rollback**
   - Machine learning anomaly detection
   - Pre-emptive rollback triggers
   - Automated root cause analysis

4. **Blue-Green Integration**
   - Zero-downtime rollbacks
   - Traffic shifting
   - Automated smoke tests
