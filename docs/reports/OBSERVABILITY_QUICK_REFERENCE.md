# Observability Quick Reference

**Last Updated:** 2026-02-06
**Grade:** A- (8.5/10 - Production Ready)

---

## Health Endpoints

```bash
# Liveness (service running)
curl http://localhost:8080/health
curl http://localhost:8080/health/live

# Readiness (all dependencies healthy)
curl http://localhost:8080/health/ready
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-06T10:30:00Z",
  "checks": {
    "database": {"status": "healthy", "latency_ms": 5},
    "redis": {"status": "healthy", "latency_ms": 2},
    "temporal": {"status": "healthy", "latency_ms": 12}
  }
}
```

---

## Metrics Collection

**Endpoint:** `http://localhost:8080/metrics`

**Key Metrics:**
- `http_request_duration_seconds` - Request latency (P50, P95, P99)
- `http_requests_total` - Request count & error rate
- `tracertm_active_agents` - Agent coordination health
- `tracertm_cache_hits_total` - Cache efficiency
- `pg_stat_database_numbackends` - DB connection pool usage

**View specific metric:**
```bash
curl http://localhost:8080/metrics | grep tracertm_active_agents
```

---

## Alert Rules (37 Total)

**Critical Alerts (MTTR < 2 min):**
- ServiceDown
- CriticalAPILatency (P95 > 5s)
- CriticalErrorRate (> 20%)
- DatabaseConnectionPoolCritical (> 95%)
- NoActiveAgents
- AgentHeartbeatFailure

**Warning Alerts (MTTR < 5 min):**
- HighAPILatency (P95 > 1s)
- HighErrorRate (> 5%)
- DatabaseConnectionPoolExhausted (> 80%)
- LowCacheHitRatio (< 50%)

**View Active Alerts:**
```bash
curl http://localhost:9090/api/v1/alerts
```

---

## Logging

### Backend (Go/Python)
- **Console:** STDERR (colored, DEBUG level)
- **Files:** `./logs/tracertm.log` (DEBUG, rotated 500MB)
- **JSON:** `./logs/tracertm.json` (Loki-compatible)
- **Errors:** `./logs/tracertm_errors.log` (ERROR level)

### Frontend
- **Web Vitals:** `POST /api/v1/metrics/web-vitals`
- **Metrics Tracked:** LCP, FID, CLS, TTFB, INP
- **Reporting:** Batched every 10 items or 5 seconds

---

## SLO Targets & Monitoring

| SLO | Target | Current Check |
|-----|--------|---------------|
| Availability | 99.9% | `AvailabilitySLOWarning` (< 95%) |
| Latency (P95) | < 500ms | `LatencySLOWarning` (> 500ms) |

**View SLO Status:**
```bash
# Availability
curl 'http://localhost:9090/api/v1/query?query=1%20-%20sum(rate(http_requests_total%7Bstatus%3D~%225..%22%7D%5B30m%5D))%20%2F%20sum(rate(http_requests_total%5B30m%5D))'

# Latency P95
curl 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.95%2C%20rate(http_request_duration_seconds_bucket%5B30m%5D))'
```

---

## Prometheus Targets

**Configured Services (8):**
1. PostgreSQL (localhost:9187)
2. Redis (localhost:9121)
3. System/Node (localhost:9100)
4. Go Backend (localhost:8080)
5. Python Backend (localhost:8000)
6. Caddy (localhost:2019)
7. Prometheus (localhost:9090)

**View Target Status:**
```bash
curl http://localhost:9090/api/v1/targets
```

---

## Monitoring Score by Service

| Service | Health | Metrics | Logs | Traces | Alerts | Score |
|---------|--------|---------|------|--------|--------|-------|
| Go Backend | 10/10 | 9/10 | 8/10 | 7/10 | 9/10 | 9/10 |
| Python Backend | 8/10 | 8/10 | 9/10 | 7/10 | 8/10 | 8/10 |
| Frontend | 5/10 | 9/10 | 4/10 | 2/10 | 6/10 | 5/10 |
| PostgreSQL | 10/10 | 9/10 | 6/10 | 2/10 | 9/10 | 8/10 |
| Redis | 10/10 | 9/10 | 6/10 | 2/10 | 9/10 | 8/10 |

---

## Critical Gaps to Address

**Priority 1 (High Impact):**
1. ❌ NATS health check (workflow engine missing)
2. ❌ MinIO health check (storage failures cascade)
3. ❌ Frontend error aggregation (silent failures)

**Priority 2 (Medium Impact):**
1. ⚠ Service discovery (static config not scalable)
2. ⚠ Loki integration (centralized logging needed)
3. ⚠ Distributed tracing (OpenTelemetry not instrumented)

**Priority 3 (Nice to Have):**
1. Recording rules (pre-computed SLI queries)
2. More Grafana dashboards (latency heatmap, error rates)
3. Auto-remediation (runbook automation)

---

## Common Troubleshooting

### Check if service is healthy
```bash
curl -s http://localhost:8080/health/ready | jq .status
```

### View recent errors
```bash
curl 'http://localhost:9090/api/v1/query?query=rate(http_requests_total{status=~"5.."}[5m])'
```

### Check agent coordination
```bash
curl 'http://localhost:9090/api/v1/query?query=tracertm_active_agents'
```

### View database connection pool
```bash
curl 'http://localhost:9090/api/v1/query?query=pg_stat_database_numbackends'
```

### Check cache efficiency
```bash
curl 'http://localhost:9090/api/v1/query?query=sum(rate(tracertm_cache_hits_total[5m]))/sum(rate(tracertm_cache_hits_total[5m])+rate(tracertm_cache_misses_total[5m]))'
```

---

## Full Audit Report

See `/docs/reports/HEALTH_OBSERVABILITY_AUDIT_2026-02-06.md` for comprehensive analysis.
