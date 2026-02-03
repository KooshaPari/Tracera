# Load Testing Suite for TraceRTM

Comprehensive performance testing with k6 to validate system performance targets.

## 🚀 Quick Start (3 Steps)

```bash
# 1. Install k6
./scripts/shell/install_k6.sh

# 2. Start backends
docker-compose up -d

# 3. Run tests
./scripts/shell/run_load_tests.sh
```

## 📊 Performance Targets

| Component | Metric | Target |
|-----------|--------|--------|
| Go API | p95 Latency | <50ms |
| Go API | Throughput | 10k req/s |
| Python API | p95 Latency | <500ms |
| Python API | Throughput | 1k req/s |
| WebSocket | Connections | 1000+ |

## 🧪 Test Suite

| Test | Duration | Load | Command |
|------|----------|------|---------|
| Smoke | 1 min | 10 | `k6 run load-tests/smoke-test.js` |
| Go Items | 6 min | 2000 | `k6 run load-tests/go-items.js` |
| Go Graph | 5 min | 100 | `k6 run load-tests/go-graph.js` |
| Python Specs | 4 min | 500 | `k6 run load-tests/python-specs.js` |
| Python AI | 4 min | 20 | `k6 run load-tests/python-ai.js` |
| WebSocket | 7 min | 1500 | `k6 run load-tests/websocket.js` |
| E2E | 9 min | 500 | `k6 run load-tests/e2e-scenario.js` |
| Stress | 15 min | 5000 | `k6 run load-tests/stress-test.js` |

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [Quick Start](./LOAD_TESTING_QUICK_START.md) | Get started in 1 minute |
| [Index](./LOAD_TESTING_INDEX.md) | Navigate all resources |
| [Guide](./docs/testing/load_testing_guide.md) | Comprehensive documentation |
| [Summary](./LOAD_TESTING_IMPLEMENTATION_SUMMARY.md) | Implementation details |
| [Completion](./LOAD_TESTING_COMPLETION_REPORT.md) | Final status report |

## 🛠️ Using Makefile

```bash
cd backend/

# Quick commands
make install-k6           # Install k6
make load-test-smoke      # Smoke test (1 min)
make load-test            # Full suite (30 min)
make load-test-stress     # Stress test (15 min)

# Component-specific
make load-test-go         # Go backend only
make load-test-python     # Python backend only
make load-test-ws         # WebSocket only

# Complete workflow
make load-test-all        # Smoke + Full + Report
```

## 📊 View Results

```bash
# HTML Report
open load-tests/results/report.html

# Console Output
k6 run load-tests/smoke-test.js
```

## 🔍 Validation

```bash
# Verify setup
./scripts/shell/validate_load_tests.sh

# Check services
curl http://localhost/health
curl http://localhost:8080/health
curl http://localhost:4000/health
```

## 🐛 Troubleshooting

**Services not running?**
```bash
docker-compose up -d
```

**High error rates?**
```bash
docker-compose logs go-backend
docker-compose logs python-backend
```

**Need help?**
- See [Troubleshooting Guide](./docs/testing/load_testing_guide.md#troubleshooting)
- Check [Quick Reference](./LOAD_TESTING_QUICK_START.md)

## 📁 File Structure

```
.
├── load-tests/               # Test files
│   ├── smoke-test.js        # Quick validation
│   ├── go-items.js          # Go CRUD
│   ├── go-graph.js          # Go Graph
│   ├── python-specs.js      # Python Analytics
│   ├── python-ai.js         # Python AI
│   ├── websocket.js         # WebSocket
│   ├── e2e-scenario.js      # E2E workflow
│   └── stress-test.js       # Capacity test
├── scripts/
│   ├── install_k6.sh        # Install k6
│   ├── run_load_tests.sh    # Run all tests
│   └── generate_load_test_report.py  # HTML report
└── docs/testing/
    └── load_testing_guide.md  # Full documentation
```

## ✅ Success Criteria

All deliverables completed:
- ✅ 8 test scenarios
- ✅ 4 automation scripts
- ✅ 5 documentation files
- ✅ 10 Makefile targets
- ✅ Validation script
- ✅ Performance targets defined

## 🔗 Resources

- **k6 Docs**: https://k6.io/docs/
- **Performance Guide**: https://k6.io/docs/testing-guides/
- **GitHub**: https://github.com/grafana/k6

## 📝 License

Part of TraceRTM project.

---

**Status**: ✅ Production Ready
**Last Updated**: January 30, 2026
