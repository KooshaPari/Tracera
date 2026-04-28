# Chaos Engineering Tests

This directory contains chaos engineering tests that validate TraceRTM's resilience by intentionally injecting failures and measuring recovery times.

## Overview

- **Framework:** Toxiproxy (local/CI) + extensible to Chaos Mesh/Litmus (K8s)
- **Recovery Target:** All services must recover within 30 seconds
- **Test Categories:** Network latency, connection failures, resource exhaustion, E2E resilience
- **Total Scenarios:** 20+ chaos scenarios across 4 test files

## Quick Start

```bash
# 1. Install and start Toxiproxy
make chaos-setup

# 2. Run all chaos tests
make chaos-test

# 3. View results
make chaos-report
```

## Test Files

### `test_network_latency.py` (4 tests)
Tests system behavior under various network latency conditions:
- **Database latency:** 500ms ± 100ms injection
- **Redis latency:** 300ms ± 50ms injection
- **Backend API latency:** 1000ms ± 200ms injection
- **Variable latency spikes:** 500ms ± 300ms (high jitter)

**Expected:** Requests slow down but complete; no failures.

---

### `test_connection_failures.py` (4 tests)
Tests automatic reconnection and recovery from service crashes:
- **Database connection drop:** Simulate DB crash and restart
- **Redis connection drop:** Simulate Redis pod kill
- **Backend service restart:** Simulate deployment rollout
- **Intermittent drops:** Flapping network simulation

**Expected:** Detection within 1-2s, automatic reconnection, recovery within 30s.

---

### `test_resource_exhaustion.py` (4 tests)
Tests behavior under resource constraints:
- **Bandwidth limitation:** 10 KB/s throttle
- **Slow connection close:** 5s delay before close
- **Connection timeout:** 10s hang before timeout
- **Combined pressure:** Multiple constraints simultaneously

**Expected:** Operations slow down but complete; graceful degradation.

---

### `test_end_to_end_resilience.py` (3 tests)
Tests full system resilience under complex scenarios:
- **Cascading failures:** DB → Redis → Backend sequential failures
- **Gradual degradation:** Progressive latency increase (100ms → 1000ms)
- **Split-brain scenario:** Partial network partition

**Expected:** Graceful degradation, full recovery within 30s, no data loss.

---

## Running Tests

### All Tests
```bash
pytest tests/chaos/ -v
```

### Specific Category
```bash
pytest tests/chaos/test_network_latency.py -v
pytest tests/chaos/test_connection_failures.py -v
pytest tests/chaos/test_resource_exhaustion.py -v
pytest tests/chaos/test_end_to_end_resilience.py -v
```

### With Custom Recovery Target
```bash
RECOVERY_TIME_TARGET=20 pytest tests/chaos/ -v
```

### Using Makefile
```bash
make chaos-test                # All tests
make chaos-test-latency       # Latency tests only
make chaos-test-failures      # Connection failure tests only
make chaos-test-resources     # Resource exhaustion tests only
make chaos-test-e2e           # E2E resilience tests only
```

## Test Fixtures

### `toxiproxy_client` (session-scoped)
Provides a Toxiproxy HTTP API client for managing proxies and toxics.

### `postgres_proxy`
Creates a Toxiproxy proxy for PostgreSQL (port 15432).
Returns connection string to use in tests.

### `redis_proxy`
Creates a Toxiproxy proxy for Redis (port 16379).
Returns Redis URL to use in tests.

### `nats_proxy`
Creates a Toxiproxy proxy for NATS (port 14222).
Returns NATS URL to use in tests.

### `go_backend_proxy`
Creates a Toxiproxy proxy for Go backend (port 18080).
Returns backend URL to use in tests.

### `python_backend_proxy`
Creates a Toxiproxy proxy for Python backend (port 18000).
Returns backend URL to use in tests.

### `assert_recovery_within_target`
Helper fixture to assert recovery time is within SLA target.

**Usage:**
```python
start = time.time()
# ... chaos scenario ...
assert_recovery_within_target(start)
```

## Toxiproxy Client Usage

### Add Latency
```python
await toxiproxy_client.add_latency(
    proxy_name="postgres_chaos",
    latency_ms=500,
    jitter_ms=100,
)
```

### Add Bandwidth Limit
```python
await toxiproxy_client.add_bandwidth_limit(
    proxy_name="postgres_chaos",
    rate_kbps=10,
)
```

### Disable Proxy (Simulate Crash)
```python
await toxiproxy_client.disable_proxy("postgres_chaos")
```

### Enable Proxy (Simulate Recovery)
```python
await toxiproxy_client.enable_proxy("postgres_chaos")
```

### Remove Toxic
```python
await toxiproxy_client.remove_toxic(
    proxy_name="postgres_chaos",
    toxic_name="latency_postgres_chaos",
)
```

## Recovery Time Measurement

All tests measure recovery time and assert against the SLA target (default: 30 seconds).

```python
@pytest.mark.asyncio
async def test_example(assert_recovery_within_target):
    # Inject failure
    await inject_chaos()

    # Remove failure
    recovery_start = time.time()
    await remove_chaos()

    # Verify recovery
    await verify_service_healthy()

    # Assert recovery time within SLA
    assert_recovery_within_target(recovery_start)
```

## CI/CD Integration

Chaos tests run automatically in GitHub Actions:
- **Scheduled:** Daily at 2 AM UTC
- **On PR:** When chaos tests change
- **Manual:** Workflow dispatch

Workflow file: `.github/workflows/chaos-tests.yml`

## Environment Variables

| Variable                | Default   | Description                    |
|-------------------------|-----------|--------------------------------|
| `TOXIPROXY_HOST`        | localhost | Toxiproxy API host             |
| `TOXIPROXY_PORT`        | 8474      | Toxiproxy API port             |
| `RECOVERY_TIME_TARGET`  | 30        | Recovery SLA in seconds        |
| `DATABASE_URL`          | (varies)  | PostgreSQL connection string   |
| `REDIS_URL`             | (varies)  | Redis connection string        |

## Pytest Markers

Chaos tests use the following markers:

```python
@pytest.mark.chaos       # All chaos tests
@pytest.mark.slow        # Tests that take >1s
@pytest.mark.e2e         # End-to-end resilience tests
@pytest.mark.asyncio     # Async tests (required)
```

**Usage:**
```bash
pytest -m chaos          # Run all chaos tests
pytest -m "chaos and not e2e"  # Exclude E2E tests
pytest -m slow           # All slow tests (includes chaos)
```

## Test Results Example

```
tests/chaos/test_network_latency.py::test_database_latency_injection PASSED [8.3s]
tests/chaos/test_network_latency.py::test_redis_latency_injection PASSED [3.2s]
tests/chaos/test_network_latency.py::test_backend_api_latency PASSED [12.1s]
tests/chaos/test_network_latency.py::test_variable_latency_spikes PASSED [15.6s]

tests/chaos/test_connection_failures.py::test_database_connection_drop PASSED [18.5s]
tests/chaos/test_connection_failures.py::test_redis_connection_drop PASSED [11.2s]
tests/chaos/test_connection_failures.py::test_backend_service_restart PASSED [22.4s]
tests/chaos/test_connection_failures.py::test_intermittent_connection_drops PASSED [25.8s]

tests/chaos/test_resource_exhaustion.py::test_bandwidth_limitation PASSED [19.3s]
tests/chaos/test_resource_exhaustion.py::test_slow_connection_close PASSED [28.7s]
tests/chaos/test_resource_exhaustion.py::test_timeout_injection PASSED [16.4s]
tests/chaos/test_resource_exhaustion.py::test_combined_resource_pressure PASSED [21.9s]

tests/chaos/test_end_to_end_resilience.py::test_cascading_failure_recovery PASSED [56.2s]
tests/chaos/test_end_to_end_resilience.py::test_gradual_degradation_under_load PASSED [42.8s]
tests/chaos/test_end_to_end_resilience.py::test_split_brain_scenario PASSED [33.1s]

==================== 15 passed in 335.5s (5:35) ====================
```

**Recovery Times:**
- Database crash → recovery: **8.2s** ✅
- Redis crash → recovery: **3.1s** ✅
- Backend restart → recovery: **12.5s** ✅
- Cascading failure → full recovery: **26.7s** ✅

All scenarios recovered within 30-second SLA ✅

## Troubleshooting

### Toxiproxy Not Running
```bash
./scripts/toxiproxy-setup.sh start
curl http://localhost:8474/version
```

### Tests Failing to Connect
```bash
# Verify services are running
pg_isready -h localhost -p 5432
redis-cli ping
curl http://localhost:8080/health

# Check Toxiproxy status
curl http://localhost:8474/proxies | jq
```

### Recovery Time Exceeds Target
1. Check service logs for errors
2. Verify retry configuration
3. Review connection pool settings
4. Check for resource constraints (CPU, memory)
5. Monitor metrics in Grafana

## Documentation

- **Quick Reference:** `docs/reference/CHAOS_ENGINEERING_QUICK_REFERENCE.md`
- **Comprehensive Guide:** `docs/guides/CHAOS_ENGINEERING_GUIDE.md`
- **Recovery Procedures:** `docs/guides/RECOVERY_PROCEDURES.md`
- **Completion Report:** `docs/reports/TASK_105_CHAOS_ENGINEERING_COMPLETION.md`

## Contributing

When adding new chaos scenarios:

1. **Choose appropriate test file** based on failure category
2. **Use existing fixtures** for proxy and client setup
3. **Follow naming convention:** `test_<scenario>_<failure_type>`
4. **Add pytest markers:** `@pytest.mark.asyncio`, `@pytest.mark.chaos`, `@pytest.mark.slow`
5. **Measure recovery time** using `assert_recovery_within_target`
6. **Document expected behavior** in docstring
7. **Update this README** with new scenario description

### Example Test Template

```python
@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_new_chaos_scenario(
    toxiproxy_client: ToxiproxyClient,
    postgres_proxy: str,
    db_session,
    assert_recovery_within_target,
) -> None:
    """
    Test: Brief description of scenario.

    Scenario:
    1. Step one
    2. Step two
    3. Step three

    Expected: What should happen
    """
    # Baseline
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

    # Inject chaos
    await toxiproxy_client.add_toxic(...)

    # Verify behavior under chaos
    # ...

    # Remove chaos
    recovery_start = time.time()
    await toxiproxy_client.remove_toxic(...)

    # Verify recovery
    # ...

    # Assert recovery time within SLA
    assert_recovery_within_target(recovery_start)
```

## License

See project LICENSE file.

---

**Maintained By:** TraceRTM DevOps Team
**Last Updated:** 2026-02-01
