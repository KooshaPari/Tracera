# Health & Observability: 85/100 → 100/100 Execution Plan

**Current:** 85/100 (A-) | **Target:** 100/100 (A+) | **Gap:** 15 points
**Timeline:** 2-3 hours with 3 parallel agents
**Agent Assignment:** Cursor (gemini-3-flash) for implementation, Gemini (gemini-3-flash) for analysis

---

## PHASED WBS

### Phase 1: Critical Gap Closure (90 min, +10 points)
**Goal:** Add missing health checks for NATS, MinIO, error aggregation

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| H1-01 | Add NATS health check to /health/ready | - | Cursor | 20min | NATS status in response |
| H1-02 | Add MinIO/S3 health check to /health/ready | - | Cursor | 20min | Storage status in response |
| H1-03 | Implement frontend error aggregation | - | Cursor | 30min | Errors sent to backend |
| H1-04 | Add error aggregation endpoint (backend) | H1-03 | Cursor | 20min | POST /api/errors endpoint |

**Acceptance:** /health/ready checks 5 dependencies (Postgres, Redis, NATS, MinIO, Temporal)

### Phase 2: Distributed Tracing (60 min, +5 points)
**Goal:** OpenTelemetry instrumentation

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| H2-01 | Add OpenTelemetry SDK to Go backend | - | Cursor | 20min | OTEL initialized |
| H2-02 | Add OpenTelemetry SDK to Python backend | - | Cursor | 20min | OTEL initialized |
| H2-03 | Configure trace export (Jaeger/Tempo) | H2-01, H2-02 | Cursor | 20min | Traces visible |

**Acceptance:** Distributed traces visible in Jaeger UI

### Phase 3: Enhanced Monitoring (60 min, +5 points bonus)
**Goal:** Service discovery, log aggregation backend

| Task ID | Description | Depends On | Agent | Time | Acceptance |
|---------|-------------|------------|-------|------|------------|
| H3-01 | Implement Consul service discovery | - | Gemini | 30min | Services auto-discovered |
| H3-02 | Configure Loki log aggregation | - | Cursor | 20min | Logs flowing to Loki |
| H3-03 | Add Grafana dashboards (3 dashboards) | H3-02 | Cursor | 10min | Dashboards importable |

**Acceptance:** Service discovery working, logs aggregated, dashboards available

---

## DEPENDENCY DAG

```
Phase 1: [H1-01, H1-02, H1-03] (parallel) → H1-04
            ↓
Phase 2: [H2-01, H2-02] (parallel) → H2-03
            ↓
Phase 3: [H3-01, H3-02] (parallel) → H3-03
```

---

## AGENT EXECUTION COMMANDS

### WP1: Critical Gaps (Cursor - 90 min)
```bash
~/.claude/skills/cursor-agent/scripts/run_cursor.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace \
  --prompt "Add 3 critical health checks:
1. NATS health check in backend/internal/health/handler.go
2. MinIO health check in backend/internal/health/handler.go
3. Frontend error aggregation: send errors to POST /api/errors
Target: All external dependencies monitored
Verify: curl /health/ready shows 5 checks (Postgres, Redis, NATS, MinIO, Temporal)" \
  --mode workspace-write &
```

### WP2: Distributed Tracing (Cursor - 60 min)
```bash
~/.claude/skills/cursor-agent/scripts/run_cursor.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace \
  --prompt "Add OpenTelemetry distributed tracing:
1. Go backend: Add OTEL SDK, instrument HTTP handlers
2. Python backend: Add OTEL SDK, instrument FastAPI
3. Configure Jaeger export
Target: End-to-end trace visibility
Verify: Traces visible in Jaeger UI" \
  --mode workspace-write &
```

### WP3: Service Discovery + Logs (Gemini - 60 min)
```bash
~/.claude/skills/gemini-agent/scripts/run_gemini.sh \
  --cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace \
  --prompt "Enhance observability infrastructure:
1. Add Consul service discovery (auto-discovery for k8s)
2. Configure Loki log aggregation backend
3. Create 3 Grafana dashboards (HTTP metrics, DB metrics, Business metrics)
Target: Production-grade observability
Verify: Services auto-discovered, logs aggregated, dashboards importable" &
```

---

## SUCCESS CRITERIA

**Phase 1:** ✅ 5 health checks (all dependencies monitored)
**Phase 2:** ✅ Distributed tracing operational
**Phase 3:** ✅ Service discovery + log aggregation

**Final Score:** **100/100 (A+)**

---

## TIMELINE

**Parallel Execution:**
- WP1: 90 min
- WP2: 60 min (parallel with WP1)
- WP3: 60 min (parallel with WP1+2)

**Total Wall-Clock:** ~90 min (1.5 hours)

**Ready to launch.**
