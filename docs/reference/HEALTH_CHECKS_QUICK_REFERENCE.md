# Health Checks & Integration Tests - Quick Reference

## Quick Start

### Run All Integration Tests
```bash
./scripts/run_integration_tests.sh
```

### Check Health Endpoints

**Go Backend:**
```bash
curl http://localhost:8080/health | jq
```

**Python Backend:**
```bash
curl http://localhost:4000/health | jq
```

## File Locations

| Component | Path |
|-----------|------|
| Go Health Handler | `/backend/internal/handlers/health_handler.go` |
| Python Health Router | `/src/tracertm/api/routers/health.py` |
| Go Integration Tests | `/backend/tests/integration/python/python_integration_test.go` |
| Python Integration Tests | `/tests/integration/test_go_integration.py` |
| NATS Flow Tests | `/tests/integration/test_nats_flow_mock.py` |
| Test Orchestration | `/scripts/run_integration_tests.sh` |

## Test Commands

### Go Tests
```bash
# Run Go integration tests
cd backend/tests/integration/python
go test -v .

# Run specific test
go test -v -run TestPythonClientBasicCall

# Run with coverage
go test -v -cover .
```

### Python Tests
```bash
# Run Python integration tests
pytest tests/integration/test_go_integration.py -v

# Run specific test
pytest tests/integration/test_go_integration.py::test_go_client_basic_call -v

# Run with coverage
pytest tests/integration/test_go_integration.py --cov=tracertm.clients
```

### NATS Tests
```bash
# Run NATS flow tests
pytest tests/integration/test_nats_flow_mock.py -v

# Run specific test
pytest tests/integration/test_nats_flow_mock.py::test_python_to_nats_flow -v
```

## Health Status Codes

| Status | HTTP Code | Meaning |
|--------|-----------|---------|
| healthy | 200 | All components functioning normally |
| degraded | 200 | Components functioning with reduced performance |
| unhealthy | 503 | One or more critical components failing |

## Component Health Levels

### Critical Components (cause unhealthy status)
- **Database**: PostgreSQL connection and query performance
  - Threshold: >1000ms = degraded

### Optional Components (cause degraded status)
- **Redis**: Cache availability
  - Threshold: >500ms = degraded
- **NATS**: Message broker connectivity
  - Threshold: >500ms = degraded
- **Python Backend**: Cross-backend communication
  - Threshold: >2000ms = degraded

## Environment Variables

### Required
```bash
DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"
```

### Optional
```bash
REDIS_URL="redis://localhost:6379"
NATS_URL="nats://localhost:4222"
NATS_BRIDGE_ENABLED="true"
PYTHON_BACKEND_URL="http://localhost:8000"
GO_BACKEND_URL="http://localhost:8080"
APP_VERSION="1.0.0"
```

## Response Examples

### Healthy System
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-30T12:00:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "latency_ms": 5.2,
      "last_check": "2025-01-30T12:00:00Z"
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1.8,
      "last_check": "2025-01-30T12:00:00Z"
    }
  }
}
```

### Degraded System
```json
{
  "status": "degraded",
  "components": {
    "database": {
      "status": "degraded",
      "message": "High latency detected",
      "latency_ms": 1200.5,
      "last_check": "2025-01-30T12:00:00Z"
    }
  }
}
```

### Unhealthy System
```json
{
  "status": "unhealthy",
  "components": {
    "database": {
      "status": "unhealthy",
      "message": "Database ping failed: connection refused",
      "latency_ms": 5000.0,
      "last_check": "2025-01-30T12:00:00Z"
    }
  }
}
```

## Integration Setup

### Go Server
```go
healthHandler := handlers.NewHealthHandler(
    infra.DB,
    infra.Redis,
    infra.NATS,
    infra.Cache,
    infra.PythonClient,
    os.Getenv("PYTHON_BACKEND_URL"),
)
e.GET("/health", healthHandler.GetHealth)
```

### Python Server
```python
from tracertm.api.routers import health

app.include_router(health.router)
```

## Common Issues

### Issue: Health check times out
**Cause:** Component timeout too long
**Fix:** Reduce timeout in health check code (default: 3-5s)

### Issue: Circuit breaker always open
**Cause:** Too many failures
**Fix:** Check service health, adjust circuit breaker threshold

### Issue: Tests fail with "connection refused"
**Cause:** Test infrastructure not running
**Fix:**
```bash
docker-compose -f docker-compose.test.yml up -d
./scripts/run_integration_tests.sh
```

### Issue: Integration health not showing
**Cause:** `NATS_BRIDGE_ENABLED` not set
**Fix:**
```bash
export NATS_BRIDGE_ENABLED=true
```

## Monitoring Integration

### Prometheus
```yaml
- job_name: 'tracertm-health'
  metrics_path: '/health'
  static_configs:
    - targets: ['localhost:8080', 'localhost:8000']
```

### Health Check Loop
```bash
# Simple monitoring loop
while true; do
  STATUS=$(curl -s http://localhost:8080/health | jq -r .status)
  echo "$(date): Health status = $STATUS"
  if [ "$STATUS" != "healthy" ]; then
    # Alert or take action
    echo "WARNING: System not healthy!"
  fi
  sleep 60
done
```

## Performance Benchmarks

Expected latencies under normal load:
- Database health check: 2-10ms
- Redis health check: 1-5ms
- NATS health check: 2-8ms
- Cross-backend health check: 10-100ms
- Total health check: <200ms

## Testing Best Practices

1. **Always run tests locally before pushing**
   ```bash
   ./scripts/run_integration_tests.sh
   ```

2. **Use test fixtures for consistent setup**
   - Mock clients for unit tests
   - Real services for integration tests

3. **Clean up resources after tests**
   - Tests automatically cleanup via fixtures
   - Orchestration script handles Docker cleanup

4. **Test both happy and error paths**
   - Normal operation
   - Network failures
   - Timeout scenarios
   - Degraded performance

5. **Keep tests fast**
   - Use mocks when possible
   - Parallel execution where safe
   - Appropriate timeouts

## Additional Resources

- Full implementation details: `PHASE_1_HEALTH_CHECKS_IMPLEMENTATION.md`
- Go client documentation: `/backend/internal/clients/python_client.go`
- Python client documentation: `/src/tracertm/clients/go_client.py`
- NATS infrastructure: `/src/tracertm/infrastructure/nats_client.py`
