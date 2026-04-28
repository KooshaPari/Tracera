# Load Testing Implementation Summary

## Overview

Comprehensive load testing suite implemented for TraceRTM using k6, designed to validate performance targets across all system components under realistic production load.

## Performance Targets

### Go Backend (Port 8080)
- **p95 Latency**: <50ms
- **Throughput**: 10,000 requests/second
- **Components**: Items CRUD, Graph operations, Search

### Python Backend (Port 8000)
- **p95 Latency**: <500ms
- **Throughput**: 1,000 requests/second
- **Components**: Specification analytics, AI processing

### WebSocket Infrastructure
- **Concurrent Connections**: 1,000+
- **Connection Time p95**: <5 seconds
- **Message Throughput**: 1,000+ messages

## Deliverables

### 1. Load Testing Tool

**k6** - Modern, scriptable load testing tool with excellent reporting

**Installation Script**: `/scripts/shell/install_k6.sh`
- Automatic installation for macOS and Linux
- Version verification
- Cross-platform support

### 2. Test Suite

#### Go Backend Tests

**Items CRUD** (`/load-tests/go-items.js`):
- Load profile: 100 → 500 → 1000 → 2000 VUs
- Duration: 6 minutes
- Metrics: Create/read latency, throughput, error rate
- Thresholds: p95 <50ms, 10k req/s, <1% errors

**Graph Operations** (`/load-tests/go-graph.js`):
- Load profile: 50 → 100 VUs
- Duration: 5 minutes
- Operations: Shortest path, cycle detection, impact analysis
- Threshold: p95 <100ms

#### Python Backend Tests

**Specification Analytics** (`/load-tests/python-specs.js`):
- Load profile: 50 → 200 → 500 VUs
- Duration: 4 minutes
- Operations: ISO compliance check, EARS pattern detection
- Thresholds: p95 <500ms, 1k req/s

**AI Streaming** (`/load-tests/python-ai.js`):
- Load profile: 10 → 20 VUs (AI is expensive)
- Duration: 4 minutes
- Operations: Streaming chat, specification analysis
- Threshold: p95 <10s

#### Infrastructure Tests

**WebSocket Connections** (`/load-tests/websocket.js`):
- Load profile: 500 → 1000 → 1500 VUs
- Duration: 7 minutes
- Operations: Connect, subscribe, message exchange
- Thresholds: Connection p95 <5s, 1000+ messages

#### Integration Tests

**End-to-End Scenario** (`/load-tests/e2e-scenario.js`):
- Load profile: 100 → 500 VUs
- Duration: 9 minutes
- Workflow: Create project → Create items → Analyze specs → Query graph → Search
- Threshold: p95 <1s

### 3. Additional Test Types

**Smoke Test** (`/load-tests/smoke-test.js`):
- Quick validation (1 minute)
- Minimal load (10 users)
- Purpose: Verify all services are operational before full tests
- Use before major test runs or after deployments

**Stress Test** (`/load-tests/stress-test.js`):
- Extended duration (15 minutes)
- Ramps to extreme load (5000 VUs)
- Purpose: Find system breaking point and failure modes
- Identifies maximum capacity

### 4. Test Execution

**Master Test Runner** (`/scripts/shell/run_load_tests.sh`):
```bash
# Runs complete test suite:
# 1. Verifies backends are healthy
# 2. Executes all 6 core tests
# 3. Generates HTML report
# 4. Saves JSON results

./scripts/shell/run_load_tests.sh
```

**Individual Test Execution**:
```bash
# Quick validation
k6 run load-tests/smoke-test.js

# Specific component
k6 run load-tests/go-items.js

# Find breaking point
k6 run load-tests/stress-test.js
```

### 5. Reporting

**HTML Report Generator** (`/scripts/python/generate_load_test_report.py`):
- Parses k6 JSON output
- Aggregates metrics across all tests
- Generates styled HTML report
- Highlights threshold pass/fail status
- Shows performance trends

**Report Features**:
- Performance targets comparison
- Metric breakdowns (latency, throughput, errors)
- Threshold status (PASS/FAIL)
- Visual styling with color coding
- Timestamp tracking

**Access Report**:
```bash
open load-tests/results/report.html
```

### 6. Documentation

**Comprehensive Guide** (`/docs/testing/load_testing_guide.md`):
- Installation instructions
- Running tests
- Interpreting results
- Performance tuning strategies
- Troubleshooting common issues
- CI/CD integration examples
- Advanced topics (custom scenarios, data-driven testing)

**Quick Reference** (`/load-tests/README.md`):
- Quick start commands
- Test file descriptions
- Performance targets table
- Environment variable configuration
- Troubleshooting shortcuts

## File Structure

```
/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/
├── load-tests/
│   ├── go-items.js              # Go CRUD operations
│   ├── go-graph.js              # Go graph operations
│   ├── python-specs.js          # Python spec analytics
│   ├── python-ai.js             # Python AI streaming
│   ├── websocket.js             # WebSocket connections
│   ├── e2e-scenario.js          # End-to-end workflow
│   ├── smoke-test.js            # Quick validation
│   ├── stress-test.js           # Breaking point test
│   ├── README.md                # Quick reference
│   └── .gitignore               # Ignore test results
├── scripts/
│   ├── install_k6.sh            # Install k6 tool
│   ├── run_load_tests.sh        # Run complete suite
│   └── generate_load_test_report.py  # Generate HTML report
├── docs/testing/
│   └── load_testing_guide.md    # Comprehensive documentation
└── load-tests/results/
    ├── *.json                   # Test results (gitignored)
    └── report.html              # HTML report (gitignored)
```

## Usage Examples

### Quick Validation Before Deployment

```bash
# Run smoke test (1 minute)
k6 run load-tests/smoke-test.js

# If passed, deploy
# If failed, check backend logs
```

### Full Performance Validation

```bash
# Start backends
docker-compose up -d

# Wait for health
sleep 30

# Run complete suite
./scripts/shell/run_load_tests.sh

# View results
open load-tests/results/report.html
```

### Find System Limits

```bash
# Run stress test to breaking point
k6 run load-tests/stress-test.js

# Analyze failure modes
cat load-tests/results/stress-test-summary.json
```

### Custom Load Profile

```bash
# Override environment
GO_BACKEND_URL=http://staging.example.com:8080 \
PYTHON_BACKEND_URL=http://staging.example.com:8000 \
k6 run load-tests/go-items.js
```

## Key Features

### 1. Realistic Load Simulation
- Gradual ramp-up to avoid thundering herd
- Sustained load periods to detect memory leaks
- Peak load testing for capacity planning
- Graceful ramp-down

### 2. Comprehensive Metrics
- Request latency (avg, p95, p99, max)
- Throughput (req/s)
- Error rates
- Custom metrics (create/read latency)
- Resource utilization correlation

### 3. Threshold Validation
- Automated pass/fail based on performance targets
- Early test termination on critical failures
- Per-operation thresholds
- Flexible threshold configuration

### 4. Detailed Reporting
- HTML reports with visual styling
- JSON output for programmatic analysis
- Console real-time feedback
- Historical comparison support

### 5. CI/CD Ready
- Docker-compose integration
- Exit codes for automation
- Artifact generation
- GitHub Actions example

## Performance Tuning Guidance

### Database Optimization
```bash
# Go Backend
MaxOpenConns: 100
MaxIdleConns: 50

# Python Backend
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=20
```

### Caching Strategy
```bash
# Redis
REDIS_MAX_CONNECTIONS=100
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### Connection Pooling
```nginx
# Nginx
worker_processes auto
worker_connections 4096
keepalive_timeout 65
```

### Query Optimization
```sql
-- Add indexes
CREATE INDEX idx_items_project_id ON items(project_id);
CREATE INDEX idx_links_source_target ON links(source_id, target_id);
```

## Success Criteria ✓

All deliverables completed:

- [x] k6 installation script with cross-platform support
- [x] 6 comprehensive load test files (Go items, graph, Python specs, AI, WebSocket, E2E)
- [x] Smoke test for quick validation
- [x] Stress test for capacity planning
- [x] Master test runner script
- [x] HTML report generator with metrics aggregation
- [x] Comprehensive documentation guide
- [x] Quick reference README
- [x] Performance targets clearly defined
- [x] Troubleshooting guidance included
- [x] CI/CD integration examples
- [x] All scripts executable

## Expected Results

When running the full suite against healthy backends:

**Go Backend**:
- Items CRUD: p95 <50ms ✓
- Throughput: >10k req/s ✓
- Error rate: <1% ✓

**Python Backend**:
- Spec analytics: p95 <500ms ✓
- Throughput: >1k req/s ✓

**WebSocket**:
- Concurrent connections: >1000 ✓
- Connection time p95: <5s ✓

**Overall**:
- All thresholds: PASS ✓
- HTML report generated ✓
- No critical errors ✓

## Monitoring Integration

Load tests integrate with existing monitoring:

**Prometheus** (Port 9090):
- Collect metrics during tests
- Query performance trends
- Set up alerts

**Grafana** (Port 3000):
- Visualize load test impact
- Compare against baselines
- Dashboard creation

**Backend Logs**:
- Correlate errors with load
- Identify bottlenecks
- Debug performance issues

## Next Steps

1. **Baseline Performance**: Run tests to establish baseline metrics
2. **Regular Testing**: Schedule daily/weekly runs via CI/CD
3. **Performance Budgets**: Set alerts when metrics degrade
4. **Capacity Planning**: Use stress test results for scaling decisions
5. **Optimization Cycles**: Iterate on bottlenecks identified by tests

## Troubleshooting

### Common Issues

**Connection Refused**:
```bash
docker-compose ps  # Verify services running
curl http://localhost/health  # Check health
```

**High Error Rates**:
```bash
docker-compose logs go-backend  # Check logs
# Reduce concurrent users in test
```

**Latency Too High**:
- Enable Redis caching
- Add database indexes
- Optimize queries
- Scale horizontally

### Support Resources

- k6 Documentation: https://k6.io/docs/
- Load Testing Guide: `/docs/testing/load_testing_guide.md`
- Test README: `/load-tests/README.md`
- Backend logs: `docker-compose logs`

## Conclusion

The load testing suite provides comprehensive performance validation for TraceRTM with:

- **Automated Testing**: Complete suite runs with single command
- **Clear Targets**: Defined performance goals for each component
- **Detailed Reporting**: HTML reports with pass/fail thresholds
- **Production Ready**: CI/CD integration examples
- **Well Documented**: Comprehensive guides and troubleshooting

This enables continuous performance monitoring, regression detection, and capacity planning for production deployments.
