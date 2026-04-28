# Chaos Engineering - Quick Reference

**Framework:** Toxiproxy (local/CI) + Chaos Mesh (K8s)
**Recovery Target:** 30 seconds for all services
**Documentation:** See `docs/guides/CHAOS_ENGINEERING_GUIDE.md` for details

---

## Quick Start

```bash
# 1. Install and start Toxiproxy
make chaos-setup

# 2. Run all chaos tests
make chaos-test

# 3. View results
make chaos-report
```

---

## Makefile Commands

| Command                  | Description                              |
|--------------------------|------------------------------------------|
| `make chaos-setup`       | Install and start Toxiproxy              |
| `make chaos-start`       | Start Toxiproxy server                   |
| `make chaos-stop`        | Stop Toxiproxy server                    |
| `make chaos-status`      | Check Toxiproxy status                   |
| `make chaos-test`        | Run all chaos tests                      |
| `make chaos-test-latency`| Run network latency tests                |
| `make chaos-test-failures`| Run connection failure tests            |
| `make chaos-test-resources`| Run resource exhaustion tests          |
| `make chaos-test-e2e`    | Run end-to-end resilience tests          |
| `make chaos-report`      | Open HTML test report                    |

---

## Manual Commands

### Toxiproxy Management

```bash
# Install Toxiproxy
./scripts/toxiproxy-setup.sh install

# Start Toxiproxy
./scripts/toxiproxy-setup.sh start

# Check status
./scripts/toxiproxy-setup.sh status

# Stop Toxiproxy
./scripts/toxiproxy-setup.sh stop

# Verify running
curl http://localhost:8474/version
```

### Running Tests

```bash
# All chaos tests
pytest tests/chaos/ -v

# Specific test file
pytest tests/chaos/test_network_latency.py -v

# With custom recovery target (seconds)
RECOVERY_TIME_TARGET=20 pytest tests/chaos/ -v

# Using test runner script
./scripts/run-chaos-tests.sh
```

### Docker Compose

```bash
# Start with Toxiproxy
docker-compose -f docker-compose.yml -f docker-compose.chaos.yml up -d

# Run tests
pytest tests/chaos/ -v

# Stop
docker-compose -f docker-compose.yml -f docker-compose.chaos.yml down
```

---

## Test Scenarios

### Network Latency (`test_network_latency.py`)
- Database latency: 500ms
- Redis latency: 300ms
- Backend API latency: 1000ms
- Variable latency spikes: 200ms-800ms

### Connection Failures (`test_connection_failures.py`)
- Database crash and recovery
- Redis crash and recovery
- Backend service restart
- Intermittent connection drops

### Resource Exhaustion (`test_resource_exhaustion.py`)
- Bandwidth limitation: 10 KB/s
- Slow connection close: 5s delay
- Connection timeout: 10s hang
- Combined pressure scenarios

### E2E Resilience (`test_end_to_end_resilience.py`)
- Cascading failures (DB → Redis → Backend)
- Gradual degradation (100ms → 1000ms)
- Split-brain scenarios

---

## Recovery Procedures

### Quick Recovery Commands

```bash
# PostgreSQL
brew services restart postgresql@17
# Recovery time: 5-10s

# Redis
brew services restart redis
# Recovery time: 2-5s

# NATS
brew services restart nats-server
# Recovery time: 3-7s

# Go Backend
process-compose project restart go-backend
# Recovery time: 10-15s

# Python Backend
process-compose project restart python-backend
# Recovery time: 5-10s

# Full system
./scripts/recovery-all-services.sh
# Total recovery: <30s
```

### Health Checks

```bash
# Check all services
curl http://localhost:8080/health  # Go backend
curl http://localhost:8000/health  # Python backend
curl http://localhost:5173/        # Frontend
pg_isready -h localhost -p 5432    # PostgreSQL
redis-cli ping                     # Redis
curl http://localhost:8222/healthz # NATS
```

---

## Proxy Configuration

| Service        | Actual Port | Proxy Port | Upstream          |
|----------------|-------------|------------|-------------------|
| PostgreSQL     | 5432        | 15432      | localhost:5432    |
| Redis          | 6379        | 16379      | localhost:6379    |
| NATS           | 4222        | 14222      | localhost:4222    |
| Go Backend     | 8080        | 18080      | localhost:8080    |
| Python Backend | 8000        | 18000      | localhost:8000    |

---

## Toxiproxy API Examples

### Create Proxy

```bash
curl -X POST http://localhost:8474/proxies \
  -H "Content-Type: application/json" \
  -d '{
    "name": "postgres_chaos",
    "listen": "0.0.0.0:15432",
    "upstream": "localhost:5432",
    "enabled": true
  }'
```

### Add Latency Toxic

```bash
curl -X POST http://localhost:8474/proxies/postgres_chaos/toxics \
  -H "Content-Type: application/json" \
  -d '{
    "name": "latency_toxic",
    "type": "latency",
    "attributes": {
      "latency": 500,
      "jitter": 100
    }
  }'
```

### Disable Proxy (Simulate Crash)

```bash
curl -X POST http://localhost:8474/proxies/postgres_chaos \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Remove Toxic

```bash
curl -X DELETE http://localhost:8474/proxies/postgres_chaos/toxics/latency_toxic
```

### List All Proxies

```bash
curl http://localhost:8474/proxies | jq
```

---

## CI/CD Integration

### GitHub Actions

```bash
# Trigger chaos tests workflow
gh workflow run chaos-tests.yml

# Run in staging environment
gh workflow run chaos-tests.yml -f environment=staging

# View workflow runs
gh run list --workflow=chaos-tests.yml
```

### Scheduled Runs

Chaos tests run automatically:
- **Daily:** 2 AM UTC (scheduled)
- **On PR:** When chaos tests change
- **Manual:** Via workflow dispatch

---

## Kubernetes Deployment

### Toxiproxy

```bash
# Deploy Toxiproxy
kubectl apply -f k8s/chaos/toxiproxy-deployment.yml

# Verify deployment
kubectl get pods -n tracertm-staging -l app=toxiproxy

# Port forward for testing
kubectl port-forward -n tracertm-staging svc/toxiproxy 8474:8474
```

### Chaos Mesh

```bash
# Install Chaos Mesh
kubectl create ns chaos-testing
helm install chaos-mesh chaos-mesh/chaos-mesh -n chaos-testing

# Apply chaos scenarios
kubectl apply -f k8s/chaos/chaos-mesh-example.yml

# List chaos experiments
kubectl get networkchaos -A
kubectl get podchaos -A

# View experiment details
kubectl describe networkchaos backend-network-delay -n tracertm-staging
```

---

## Monitoring

### Prometheus Queries

```promql
# Service recovery time
increase(service_recovery_duration_seconds[5m])

# Failed requests during chaos
rate(http_requests_total{status=~"5.."}[1m])

# Connection pool utilization
pg_stat_database_numbackends / pg_settings_max_connections

# Redis errors
rate(redis_commands_failed_total[1m])
```

### Grafana Dashboard

1. Navigate to http://localhost:3000
2. Select **Chaos Engineering Metrics**
3. View:
   - Service recovery times
   - Error rates
   - Connection pool status
   - Circuit breaker state

---

## Troubleshooting

### Toxiproxy Won't Start

```bash
# Check if port is in use
lsof -ti :8474

# Kill conflicting process
kill -9 $(lsof -ti :8474)

# Restart
./scripts/toxiproxy-setup.sh restart
```

### Tests Fail to Connect

```bash
# Verify services running
pg_isready -h localhost -p 5432
redis-cli ping
curl http://localhost:8080/health

# Check Toxiproxy proxies
curl http://localhost:8474/proxies | jq
```

### Recovery Time Exceeds Target

1. Check service logs: `tail -f .process-compose/logs/*.log`
2. Verify connection pools: `psql -U tracertm -c "SELECT * FROM pg_stat_activity"`
3. Review retry config in service code
4. Check circuit breaker thresholds
5. Monitor resource usage: `top`, `htop`

---

## Environment Variables

| Variable                 | Default    | Description                    |
|--------------------------|------------|--------------------------------|
| `TOXIPROXY_HOST`         | localhost  | Toxiproxy API host             |
| `TOXIPROXY_PORT`         | 8474       | Toxiproxy API port             |
| `RECOVERY_TIME_TARGET`   | 30         | Recovery SLA in seconds        |
| `DATABASE_URL`           | (varies)   | PostgreSQL connection string   |
| `REDIS_URL`              | (varies)   | Redis connection string        |

---

## Test Markers

```bash
# Run only chaos tests
pytest -m chaos

# Run chaos tests excluding E2E
pytest -m "chaos and not e2e"

# Run slow tests (includes chaos)
pytest -m slow
```

---

## Common Workflows

### Before Deployment

```bash
# 1. Run chaos tests locally
make chaos-test

# 2. Verify all pass
# 3. Review recovery times in report
make chaos-report

# 4. Deploy to staging
# 5. Run chaos tests in staging
gh workflow run chaos-tests.yml -f environment=staging
```

### After Incident

```bash
# 1. Reproduce incident with chaos test
# 2. Implement fix
# 3. Verify fix with chaos test
pytest tests/chaos/test_<scenario>.py -v

# 4. Add new chaos scenario if needed
# 5. Update recovery procedures
```

### Weekly Maintenance

```bash
# 1. Review chaos test results
gh run list --workflow=chaos-tests.yml --limit 7

# 2. Check for slow recovery times
# 3. Update recovery procedures if needed
# 4. Add new scenarios based on incidents
```

---

## Related Documentation

- **Comprehensive Guide:** `docs/guides/CHAOS_ENGINEERING_GUIDE.md`
- **Recovery Procedures:** `docs/guides/RECOVERY_PROCEDURES.md`
- **Completion Report:** `docs/reports/TASK_105_CHAOS_ENGINEERING_COMPLETION.md`
- **Toxiproxy Docs:** https://github.com/Shopify/toxiproxy
- **Chaos Mesh Docs:** https://chaos-mesh.org/docs/

---

## Support

- **Issues:** Create issue in repository
- **Questions:** #tracertm-ops Slack channel
- **On-Call:** See PagerDuty rotation

---

**Last Updated:** 2026-02-01
**Maintained By:** TraceRTM DevOps Team
