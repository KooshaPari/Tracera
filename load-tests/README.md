# Load Tests

Comprehensive performance testing suite for TraceRTM using k6.

## Quick Start

```bash
# 1. Install k6
./scripts/install_k6.sh

# 2. Start backend services
docker-compose up -d

# 3. Run all tests
./scripts/run_load_tests.sh

# 4. View results
open load-test-results/report.html
```

## Test Files

### Go Backend Tests
- **go-items.js**: Items CRUD operations
  - Target: <50ms p95, 10k req/s
  - Load: 2000 concurrent users
  - Duration: 6 minutes

- **go-graph.js**: Graph analysis operations
  - Target: <100ms p95
  - Load: 100 concurrent users
  - Duration: 5 minutes

### Python Backend Tests
- **python-specs.js**: Specification analytics
  - Target: <500ms p95, 1k req/s
  - Load: 500 concurrent users
  - Duration: 4 minutes

- **python-ai.js**: AI streaming operations
  - Target: <10s p95
  - Load: 20 concurrent users
  - Duration: 4 minutes

### Infrastructure Tests
- **websocket.js**: WebSocket connections
  - Target: 1000+ concurrent connections
  - Connection time: <5s p95
  - Duration: 7 minutes

### Integration Tests
- **e2e-scenario.js**: Complete user journey
  - Realistic workflow across both backends
  - Load: 500 concurrent users
  - Duration: 9 minutes

## Environment Variables

```bash
# Override default URLs
export GO_BACKEND_URL=http://localhost:8080
export PYTHON_BACKEND_URL=http://localhost:8000
export WS_URL=ws://localhost/ws

# Run specific test
k6 run load-tests/go-items.js
```

## Performance Targets

| Component | Metric | Target |
|-----------|--------|--------|
| Go API | p95 Latency | <50ms |
| Go API | Throughput | 10,000 req/s |
| Python API | p95 Latency | <500ms |
| Python API | Throughput | 1,000 req/s |
| WebSocket | Connections | 1,000+ concurrent |
| WebSocket | Connection Time | <5s p95 |

## Running Individual Tests

```bash
# Go Items CRUD
k6 run --out json=load-test-results/go-items.json load-tests/go-items.js

# View summary
k6 run load-tests/go-items.js
```

## Continuous Monitoring

For production monitoring, integrate with:
- Prometheus (metrics collection)
- Grafana (visualization)
- k6 Cloud (distributed testing)

## Troubleshooting

**Connection Refused**:
```bash
# Check services are running
docker-compose ps

# Check health endpoints
curl http://localhost/health
```

**High Error Rates**:
```bash
# Check backend logs
docker-compose logs go-backend
docker-compose logs python-backend

# Reduce load
# Edit test file stages to lower target VUs
```

**Latency Too High**:
- Enable caching (Redis)
- Optimize database queries
- Add database indexes
- Scale horizontally

See `docs/testing/load_testing_guide.md` for detailed documentation.
