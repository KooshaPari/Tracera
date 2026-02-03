# Load Testing Quick Start

## 1-Minute Setup

```bash
# Install k6
./scripts/shell/install_k6.sh

# Start backends
docker-compose up -d

# Run smoke test (1 min)
k6 run load-tests/smoke-test.js
```

## Run Full Suite

```bash
./scripts/shell/run_load_tests.sh
open load-tests/results/report.html
```

## Individual Tests

| Test | Command | Duration | Load |
|------|---------|----------|------|
| Smoke | `k6 run load-tests/smoke-test.js` | 1 min | 10 VUs |
| Go Items | `k6 run load-tests/go-items.js` | 6 min | 2000 VUs |
| Go Graph | `k6 run load-tests/go-graph.js` | 5 min | 100 VUs |
| Python Specs | `k6 run load-tests/python-specs.js` | 4 min | 500 VUs |
| Python AI | `k6 run load-tests/python-ai.js` | 4 min | 20 VUs |
| WebSocket | `k6 run load-tests/websocket.js` | 7 min | 1500 VUs |
| E2E | `k6 run load-tests/e2e-scenario.js` | 9 min | 500 VUs |
| Stress | `k6 run load-tests/stress-test.js` | 15 min | 5000 VUs |

## Performance Targets

| Component | Metric | Target | Test File |
|-----------|--------|--------|-----------|
| Go API | p95 Latency | <50ms | go-items.js |
| Go API | Throughput | 10k req/s | go-items.js |
| Python API | p95 Latency | <500ms | python-specs.js |
| Python API | Throughput | 1k req/s | python-specs.js |
| WebSocket | Connections | 1000+ | websocket.js |

## Reading Results

### Console Output
```
http_req_duration..............: avg=25ms  p(95)=45ms  p(99)=80ms
http_reqs......................: 100000   333.33/s
checks.........................: 100.00%  ✓ 150000  ✗ 0
```

**Key Metrics**:
- `p(95)`: 95% of requests faster than this (main target)
- `http_reqs`: Total requests and rate (req/s)
- `checks`: Validation pass rate (should be 100%)

### HTML Report
```bash
open load-tests/results/report.html
```

Look for:
- ✓ **Green** thresholds = Performance targets met
- ✗ **Red** thresholds = Performance below target

## Troubleshooting

**Services Not Running**:
```bash
docker-compose ps
docker-compose up -d
```

**Connection Errors**:
```bash
curl http://localhost/health
curl http://localhost:8080/health
curl http://localhost:4000/health
```

**Check Logs**:
```bash
docker-compose logs go-backend
docker-compose logs python-backend
```

**High Error Rates**: Reduce load by editing test stages

## Environment Variables

```bash
export GO_BACKEND_URL=http://localhost:8080
export PYTHON_BACKEND_URL=http://localhost:8000
export WS_URL=ws://localhost/ws

k6 run load-tests/go-items.js
```

## Documentation

- **Full Guide**: `/docs/testing/load_testing_guide.md`
- **Tests README**: `/load-tests/README.md`
- **Summary**: `/LOAD_TESTING_IMPLEMENTATION_SUMMARY.md`

## CI/CD Integration

Add to `.github/workflows/load-tests.yml`:

```yaml
- name: Run load tests
  run: ./scripts/shell/run_load_tests.sh

- name: Upload results
  uses: actions/upload-artifact@v3
  with:
    name: load-tests/results
    path: load-tests/results/
```

## Next Steps

1. Run smoke test to verify setup
2. Run full suite to establish baseline
3. Schedule regular runs (daily/weekly)
4. Set up monitoring alerts
5. Iterate on performance improvements
