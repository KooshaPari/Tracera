# Phase 6 Track 4: Deployment Readiness (2h wall-clock execution)

**Status:** EXECUTION ACTIVE
**Timeline:** 120 min wall-clock (aggressive parallelization, 5 subtracks)
**Target:** Production-ready deployment infrastructure verified
**Coordination Model:** 5 parallel agents executing subtracks + coordinator

---

## Executive Summary

This document outlines Phase 6 Track 4: Deployment Readiness execution. Five independent subtracks execute in parallel to deliver:

1. **6.12: Config Validation** - Preflight checks, env var enforcement, fail-fast
2. **6.13: DB Migrations** - Migration scripts with rollback verification
3. **6.14: Health Checks** - GET /health endpoint, dependency status reporting
4. **6.15: Monitoring** - Prometheus metrics, alert rules, SLOs
5. **6.16: Orchestration** - Docker Compose + Kubernetes templates

---

## Subtrack 6.12: Config Validation (20 min)

**Deliverable:** Preflight validation system that enforces all required env vars at startup

### Requirements
- ✅ Validate all required env vars present
- ✅ Fail loudly with clear, actionable error messages
- ✅ List each missing var explicitly (no silent degradation)
- ✅ Validate env var formats (URLs, ports, etc.)
- ✅ Check directory/file permissions
- ✅ Verify service connectivity (DB, Redis, NATS)

### Implementation Files
- **Go Backend:** `cmd/tracertm/preflight.go` (new, ~200 lines)
  - EnvConfig struct with validation
  - Required vars: DB_*, REDIS_*, NATS_*, JWT_*, CORS_*, etc.
  - Format validation for URLs, ports, secrets
  - Database connectivity check (dry run of connection)
  - Explicit fail on missing critical vars

- **Python Backend:** `src/tracertm/preflight.py` (update, ~150 lines)
  - Reuse existing preflight module, verify completeness
  - Check PYTHONPATH, module imports, database connectivity
  - Fail on missing TEMPORAL_HOST, DATABASE_URL, etc.

- **Frontend:** Env var validation in build process
  - Vite build fails if VITE_API_URL not set
  - Runtime check for critical config

### Success Criteria
- ✅ All required vars listed in .env.example with comments
- ✅ Preflight runs at startup (before service starts)
- ✅ Clear error messages: "Missing required env var: DB_PASSWORD (format: postgres://user:pass@host:5432/db)"
- ✅ Timeout on DB/Redis/NATS connectivity (5s per check)
- ✅ Tests verify preflight catches missing vars

### Commands
```bash
# Test preflight with missing vars
unset DB_PASSWORD && go run cmd/tracertm/main.go  # Should fail immediately with clear message

# Test preflight validation
cd backend && go test ./cmd/... -run TestPreflight -v
```

---

## Subtrack 6.13: Migrations (25 min)

**Deliverable:** Robust database migration system with rollback verification

### Requirements
- ✅ Migration scripts for all schema changes
- ✅ Rollback scripts that fully revert schema
- ✅ Transaction safety (all-or-nothing semantics)
- ✅ Timeout protection (max 30s per migration)
- ✅ Version tracking in database

### Implementation Files
- **Go Backend:** `internal/db/migrations.go` (update, ~200 lines)
  - atlas-based migrations (already integrated)
  - Verify all pending migrations included
  - Rollback handler (reverse order, single transaction)
  - Migration status query

- **SQL Migrations:** `migrations/202602*.sql` (create/update ~5 files)
  - 20260206_001_create_sessions_table.sql
  - 20260206_002_add_oauth_tokens_table.sql
  - 20260206_003_add_indexes.sql
  - Each must be independently rollbackable

- **Tests:** `internal/db/migrations_test.go`
  - Test forward migration
  - Test rollback migration
  - Verify schema state after each

### Success Criteria
- ✅ All pending migrations listed via `atlas migrate status`
- ✅ Forward migration: `atlas migrate apply --env prod`
- ✅ Rollback migration: `atlas migrate down --env prod --amount 1`
- ✅ Schema reverts to previous state after rollback
- ✅ Tests verify migration reversibility

### Commands
```bash
# View pending migrations
cd backend && atlas migrate status --env prod

# Test forward migration (dry-run)
atlas migrate apply --env prod --dry-run

# Test rollback
atlas migrate down --env prod --amount 1 --auto-approve

# Run migration tests
go test ./internal/db -run TestMigration -v
```

---

## Subtrack 6.14: Health Checks (20 min)

**Deliverable:** GET /health endpoint with comprehensive dependency status

### Requirements
- ✅ GET /health returns 200 only if all critical dependencies healthy
- ✅ Response includes status for: DB, Redis, NATS, gRPC, Temporal
- ✅ Graceful timeout on any dependency check (5s max)
- ✅ Detailed error messages for each failing dependency
- ✅ Readiness vs Liveness distinction (K8s probes)

### Implementation Files
- **Go Backend:** `internal/health/handler.go` (new, ~150 lines)
  - /health (liveness) - basic checks
  - /health/ready (readiness) - full dependency checks
  - JSON response with component status
  - 5s context timeout per dependency

- **Python Backend:** `src/tracertm/api/routers/health.py` (update, ~100 lines)
  - Mirror Go health checks
  - Database connection test
  - Redis ping
  - Temporal workflow client test

- **Tests:** Health check tests in respective packages
  - Test healthy state (all deps up)
  - Test degraded state (one dep down)
  - Test timeout handling

### Response Schema
```json
{
  "status": "healthy",  // healthy, degraded, unhealthy
  "timestamp": "2026-02-06T10:00:00Z",
  "checks": {
    "database": {
      "status": "healthy",
      "latency_ms": 2,
      "message": null
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1,
      "message": null
    },
    "nats": {
      "status": "healthy",
      "latency_ms": 5,
      "message": null
    },
    "temporal": {
      "status": "degraded",
      "latency_ms": null,
      "message": "Connection timeout after 5s"
    }
  }
}
```

### Success Criteria
- ✅ GET /health/ready returns 200 when all deps healthy
- ✅ Response includes latency metrics for each dependency
- ✅ No response takes >5s (timeout enforced)
- ✅ Clear error messages on failures
- ✅ K8s readiness probe uses /health/ready endpoint

### Commands
```bash
# Test health check endpoint
curl -s http://localhost:8080/health/ready | jq .

# Monitor health with interval
watch -n 2 'curl -s http://localhost:8080/health/ready | jq .checks'

# Run health check tests
go test ./internal/health -v
```

---

## Subtrack 6.15: Monitoring (25 min)

**Deliverable:** Prometheus metrics + alert rules + SLO tracking

### Requirements
- ✅ Prometheus metrics for: requests, errors, latency, database, memory
- ✅ Alert rules for: error rate >5%, latency >2s, memory >80%, DB connections >20
- ✅ SLO definitions: 99.9% availability, p95 latency <500ms
- ✅ Grafana dashboard template for visualization
- ✅ Alert routing rules (Slack/PagerDuty)

### Implementation Files
- **Go Backend:** Prometheus instrumentation (update, ~100 lines)
  - HTTP request metrics (request count, duration, size)
  - Database query metrics (count, duration)
  - Cache hit/miss rates
  - Worker queue metrics

- **Python Backend:** Prometheus instrumentation (update, ~80 lines)
  - Activity execution metrics
  - Workflow completion metrics
  - Task queue metrics

- **Prometheus Config:** `deploy/monitoring/prometheus.yml` (update, ~50 lines)
  - Scrape configs for Go/Python/Node exporters
  - Scrape interval: 15s
  - Evaluation interval: 15s

- **Alert Rules:** `deploy/monitoring/alerting/production-alerts.yml` (new, ~120 lines)
  - Alert: HTTP 5xx error rate >5% for 5min
  - Alert: API latency p95 >2s for 10min
  - Alert: Database connection pool >20
  - Alert: Memory usage >80%
  - Alert: Temporal workflow failure rate >10%

- **SLO Definitions:** `deploy/monitoring/alerting/slo-alerts.yml` (update, ~80 lines)
  - Availability SLO: 99.9% (43.2s downtime/month)
  - Latency SLO: p95 <500ms
  - Error budget tracking

### Success Criteria
- ✅ Prometheus scrapes all targets successfully (9090/targets shows 100% up)
- ✅ Custom metrics appear in Prometheus UI
- ✅ AlertManager receives and routes alerts correctly
- ✅ Grafana dashboard displays SLO tracking
- ✅ Alert rules evaluate to firing/pending appropriately

### Commands
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'

# Query custom metrics
curl 'http://localhost:9090/api/v1/query?query=http_requests_total' | jq .

# Test alert rules
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.alert != null)'

# Simulate high error rate
for i in {1..100}; do curl -s http://localhost:8080/invalid-endpoint; done
```

---

## Subtrack 6.16: Orchestration (30 min)

**Deliverable:** Docker Compose + Kubernetes templates for production deployment

### Requirements
- ✅ Docker Compose for local production-like testing
- ✅ Kubernetes manifests (deployment, service, configmap, ingress)
- ✅ Multi-environment support (dev, staging, production)
- ✅ Resource limits and requests
- ✅ Health probes (liveness, readiness, startup)
- ✅ Rolling updates strategy
- ✅ Persistent volume claims for databases

### Implementation Files
- **Docker Compose:** `docker-compose.prod.yml` (new, ~150 lines)
  - Services: postgres, redis, neo4j, nats, temporal, go-backend, python-backend, frontend, caddy
  - Volumes for data persistence
  - Health checks for all services
  - Resource limits per service
  - Network isolation

- **Kubernetes Base:** `deploy/k8s/base/` (create/update ~8 files)
  - deployment.yaml - Go/Python/Frontend deployments
  - service.yaml - ClusterIP for internal, LoadBalancer for frontend
  - configmap.yaml - Environment variables
  - secret.yaml (template) - Sensitive config
  - ingress.yaml - HTTP routing
  - persistentvolume.yaml - Database volumes
  - networkpolicy.yaml - Traffic rules

- **Kubernetes Overlays:** `deploy/k8s/overlays/` (create ~3)
  - production/ - HA, 3 replicas, resource limits
  - staging/ - 2 replicas, medium resources
  - development/ - 1 replica, low resources

- **Helm Chart:** `deploy/helm/tracertm/` (new, optional, ~200 lines)
  - Chart.yaml, values.yaml, templates/
  - Simplifies multi-environment deployments

### Success Criteria
- ✅ Docker Compose stack starts all services: `docker-compose -f docker-compose.prod.yml up`
- ✅ Services are healthy: `docker-compose ps` shows all "healthy"
- ✅ Frontend accessible at http://localhost
- ✅ K8s manifests validate: `kubectl apply -f deploy/k8s/overlays/production --dry-run=client`
- ✅ Rolling updates work: `kubectl set image deployment/go-backend go-backend=...`
- ✅ Persistent data survives pod restarts

### Commands
```bash
# Test Docker Compose
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml ps
curl http://localhost

# Test Kubernetes manifests
kubectl apply -f deploy/k8s/overlays/production --dry-run=client -o yaml | kubectl apply -f -

# Check K8s deployment status
kubectl rollout status deployment/go-backend -n tracertm

# View pod logs
kubectl logs -n tracertm deployment/go-backend --tail=50 -f

# Simulate rolling update
kubectl set image deployment/go-backend go-backend=tracertm/backend:v2.0.0 --record
```

---

## Parallel Execution Timeline

### T+0-5 min: Setup
- All 5 agents receive task assignments
- Coordinators set up monitoring
- Verify tooling available (atlas, kubectl, docker-compose)

### T+5-30 min: Phase 1 (Implementation)
- 6.12: Build preflight validation (Go + Python)
- 6.13: Create migration scripts + tests
- 6.14: Implement /health endpoints
- 6.15: Add Prometheus instrumentation
- 6.16: Create Docker Compose + K8s manifests

### T+30-60 min: Phase 2 (Integration Testing)
- 6.12: Test preflight with missing vars
- 6.13: Test migration forward/rollback
- 6.14: Test /health endpoints at various states
- 6.15: Verify Prometheus scrapes + alerts fire
- 6.16: Test Docker Compose stack startup

### T+60-90 min: Phase 3 (System Validation)
- Run full deployment scenario
- Verify all endpoints accessible
- Simulate failure scenarios (dependency down)
- Check monitoring captures issues
- Validate rollback procedures

### T+90-120 min: Phase 4 (Documentation + Cleanup)
- Create deployment runbooks
- Document troubleshooting procedures
- Commit all changes
- Generate deployment readiness report

---

## Success Criteria Summary

| Track | Success Metric | Target |
|-------|----------------|--------|
| 6.12  | Preflight catches all missing vars | 100% |
| 6.13  | Forward + rollback migration tests | 100% passing |
| 6.14  | /health endpoint latency | <5s all deps |
| 6.15  | Prometheus targets healthy | 100% |
| 6.16  | Docker Compose + K8s validation | Pass dry-run |

---

## Deliverables Checklist

- [ ] Preflight validation system (Go + Python)
- [ ] Database migration scripts + rollback tests
- [ ] Health check endpoints (/health, /health/ready)
- [ ] Prometheus metrics + alert rules
- [ ] Docker Compose production config
- [ ] Kubernetes manifests (base + overlays)
- [ ] Helm chart (optional)
- [ ] Deployment runbook
- [ ] Troubleshooting guide
- [ ] Deployment readiness verification report

---

## Known Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Env var misconfigs | Service won't start | Comprehensive preflight checks, clear error messages |
| Migration blockers | Data loss on rollback | Test all migrations reversibly, transaction safety |
| Health check timeouts | False positives | Separate liveness/readiness probes, reasonable timeouts |
| Alert fatigue | Operator burnout | SLO-based alerts, appropriate thresholds |
| K8s YAML drift | Production issues | GitOps, policy validation, drift detection |

---

## Post-Deployment Validation

After deployment:

1. ✅ Run preflight checks on every service start
2. ✅ Verify migrations applied successfully: `atlas migrate status`
3. ✅ Check health endpoints: `curl /health/ready`
4. ✅ Verify Prometheus scrapes all targets
5. ✅ Test alert routing by creating a test alert
6. ✅ Simulate failure scenarios and verify recovery
7. ✅ Validate K8s rolling updates work
8. ✅ Check persistent data survives restarts

---

## Next Phase Handoff

Upon completion of Track 4:

- **Track 5:** Security Hardening (HTTPS, TLS, OAuth, secrets management)
- **Track 6:** Performance Optimization (caching, compression, CDN)
- **Track 7:** Documentation & Training (runbooks, dashboards, on-call guides)

---

**Execution Status:** Ready for agent deployment
**Coordinator:** Monitoring all 5 subtracks
**Target Completion:** 120 min wall-clock
