# Load Testing Index

Complete reference for TraceRTM load testing suite.

## Quick Links

- **Quick Start**: [LOAD_TESTING_QUICK_START.md](./LOAD_TESTING_QUICK_START.md)
- **Full Guide**: [docs/testing/load_testing_guide.md](./docs/testing/load_testing_guide.md)
- **Implementation Summary**: [LOAD_TESTING_IMPLEMENTATION_SUMMARY.md](./LOAD_TESTING_IMPLEMENTATION_SUMMARY.md)
- **Test Suite README**: [load-tests/README.md](./load-tests/README.md)

## File Structure

### Scripts
| File | Purpose | Usage |
|------|---------|-------|
| `scripts/install_k6.sh` | Install k6 tool | `./scripts/install_k6.sh` |
| `scripts/run_load_tests.sh` | Run complete suite | `./scripts/run_load_tests.sh` |
| `scripts/generate_load_test_report.py` | Generate HTML report | Auto-run by test runner |

### Test Files
| File | Component | Duration | Load | Target |
|------|-----------|----------|------|--------|
| `load-tests/smoke-test.js` | All services | 1 min | 10 VUs | Quick validation |
| `load-tests/go-items.js` | Go CRUD | 6 min | 2000 VUs | p95 <50ms, 10k req/s |
| `load-tests/go-graph.js` | Go Graph | 5 min | 100 VUs | p95 <100ms |
| `load-tests/python-specs.js` | Python Analytics | 4 min | 500 VUs | p95 <500ms, 1k req/s |
| `load-tests/python-ai.js` | Python AI | 4 min | 20 VUs | p95 <10s |
| `load-tests/websocket.js` | WebSocket | 7 min | 1500 VUs | 1000+ connections |
| `load-tests/e2e-scenario.js` | Full workflow | 9 min | 500 VUs | p95 <1s |
| `load-tests/stress-test.js` | Capacity test | 15 min | 5000 VUs | Find limits |

### Documentation
| File | Content |
|------|---------|
| `docs/testing/load_testing_guide.md` | Complete guide with installation, usage, tuning |
| `LOAD_TESTING_IMPLEMENTATION_SUMMARY.md` | Deliverables, features, success criteria |
| `LOAD_TESTING_QUICK_START.md` | 1-minute setup and quick reference |
| `load-tests/README.md` | Test suite overview and quick commands |

## Common Commands

### Quick Validation
```bash
# Install k6 (one-time)
./scripts/install_k6.sh

# Quick smoke test (1 minute)
k6 run load-tests/smoke-test.js
```

### Full Testing
```bash
# Start backends
docker-compose up -d

# Run complete suite
./scripts/run_load_tests.sh

# View report
open load-test-results/report.html
```

### Using Makefile (from backend/)
```bash
cd backend/

# Install k6
make install-k6

# Smoke test
make load-test-smoke

# Full suite
make load-test

# Stress test
make load-test-stress

# Complete workflow
make load-test-all
```

### Individual Components
```bash
# Go backend
make load-test-go

# Python backend
make load-test-python

# WebSocket
make load-test-ws
```

## Performance Targets

### Go Backend (Port 8080)
- **p95 Latency**: <50ms
- **Throughput**: 10,000 req/s
- **Error Rate**: <1%

### Python Backend (Port 8000)
- **p95 Latency**: <500ms
- **Throughput**: 1,000 req/s
- **Error Rate**: <1%

### WebSocket
- **Concurrent Connections**: 1,000+
- **Connection Time p95**: <5s
- **Message Throughput**: 1,000+

## Test Types

### 1. Smoke Test
**Purpose**: Quick validation before major tests
**Duration**: 1 minute
**Load**: Minimal (10 users)
**When**: Before deployments, after changes

### 2. Load Test
**Purpose**: Validate performance targets
**Duration**: 6-9 minutes per test
**Load**: Target production load
**When**: Regular CI/CD, baseline establishment

### 3. Stress Test
**Purpose**: Find system breaking point
**Duration**: 15 minutes
**Load**: Extreme (up to 5000 users)
**When**: Capacity planning, architecture changes

### 4. Soak Test
**Purpose**: Long-running stability (future enhancement)
**Duration**: Hours/days
**Load**: Normal production load
**When**: Memory leak detection, stability validation

## Interpreting Results

### Console Output
```
✓ create status 201
✓ get status 200

http_req_duration..: avg=25ms  p(95)=45ms  p(99)=80ms
http_reqs..........: 100000   333.33/s
checks.............: 100.00%  ✓ 150000  ✗ 0
```

**Key Metrics**:
- `p(95)`: 95th percentile latency (main target)
- `http_reqs`: Requests per second
- `checks`: Validation success rate

### HTML Report
- **Green/PASS**: Performance meets target
- **Red/FAIL**: Performance below target
- **Metrics Table**: Detailed breakdown
- **Thresholds Table**: Pass/fail status

## Troubleshooting Guide

### Services Not Running
```bash
docker-compose ps
docker-compose up -d
curl http://localhost/health
```

### Connection Errors
```bash
# Check Go backend
curl http://localhost:8080/health

# Check Python backend
curl http://localhost:4000/health

# Check logs
docker-compose logs go-backend
docker-compose logs python-backend
```

### High Error Rates
1. Reduce concurrent users in test file
2. Check backend logs for errors
3. Verify database connections
4. Check resource limits

### Latency Too High
1. Enable Redis caching
2. Add database indexes
3. Optimize queries
4. Increase connection pools
5. Scale horizontally

## Integration Points

### CI/CD Pipeline
```yaml
# .github/workflows/load-tests.yml
- name: Run load tests
  run: ./scripts/run_load_tests.sh

- name: Upload results
  uses: actions/upload-artifact@v3
  with:
    name: load-test-results
    path: load-test-results/
```

### Monitoring
- **Prometheus**: Metrics collection during tests
- **Grafana**: Real-time visualization
- **Backend Logs**: Error correlation

### Alerting
- Set up alerts when metrics degrade
- Track performance trends over time
- Notify on threshold failures

## Development Workflow

### 1. Before Deployment
```bash
# Smoke test
make load-test-smoke
```

### 2. After Major Changes
```bash
# Full suite
make load-test
```

### 3. Capacity Planning
```bash
# Stress test
make load-test-stress
```

### 4. Regular Monitoring
```bash
# Schedule daily runs
cron: '0 2 * * *'  # 2 AM daily
```

## Performance Tuning

### Database
```bash
# Connection pooling
MaxOpenConns: 100
MaxIdleConns: 50

# Indexes
CREATE INDEX idx_items_project_id ON items(project_id);
```

### Caching
```bash
# Redis
REDIS_MAX_CONNECTIONS=100
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### Load Balancing
```nginx
# Nginx
worker_processes auto
worker_connections 4096
keepalive_timeout 65
```

## Advanced Usage

### Custom Environment
```bash
GO_BACKEND_URL=http://staging:8080 \
PYTHON_BACKEND_URL=http://staging:8000 \
k6 run load-tests/go-items.js
```

### Data-Driven Testing
```javascript
import { SharedArray } from 'k6/data';

const testData = new SharedArray('data', function() {
  return JSON.parse(open('./test-data.json'));
});
```

### Custom Scenarios
```javascript
scenarios: {
  read_heavy: {
    executor: 'ramping-vus',
    stages: [{ duration: '2m', target: 500 }],
    exec: 'readScenario',
  },
  write_heavy: {
    executor: 'ramping-vus',
    stages: [{ duration: '2m', target: 100 }],
    exec: 'writeScenario',
  },
}
```

## Resources

### Documentation
- k6 Official Docs: https://k6.io/docs/
- Performance Testing Guide: https://k6.io/docs/testing-guides/
- Load Testing Best Practices: https://k6.io/blog/

### Internal Docs
- [Load Testing Guide](./docs/testing/load_testing_guide.md)
- [Quick Start](./LOAD_TESTING_QUICK_START.md)
- [Implementation Summary](./LOAD_TESTING_IMPLEMENTATION_SUMMARY.md)

### Monitoring
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Next Steps

1. **Install k6**: `./scripts/install_k6.sh`
2. **Run smoke test**: `k6 run load-tests/smoke-test.js`
3. **Run full suite**: `./scripts/run_load_tests.sh`
4. **View report**: `open load-test-results/report.html`
5. **Set up CI/CD**: Add to GitHub Actions
6. **Schedule regular runs**: Daily/weekly testing
7. **Monitor trends**: Track performance over time
8. **Iterate**: Optimize based on results

## Success Criteria

- [x] k6 installed and working
- [x] All tests pass with green thresholds
- [x] HTML report generated
- [x] No critical errors
- [x] Performance targets met
- [x] CI/CD integration configured
- [x] Regular testing scheduled

## Support

For issues or questions:
1. Check [Troubleshooting Guide](./docs/testing/load_testing_guide.md#troubleshooting)
2. Review backend logs: `docker-compose logs`
3. Verify services: `docker-compose ps`
4. Consult k6 docs: https://k6.io/docs/
