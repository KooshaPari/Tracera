# Load Testing Setup Checklist

Use this checklist to verify your load testing setup is complete and ready to use.

## Prerequisites

- [ ] Docker and docker-compose installed
- [ ] Backend services can run (`docker-compose up -d`)
- [ ] Python 3.x installed (for report generator)
- [ ] Terminal/shell access

## Installation

- [ ] Run `./scripts/shell/install_k6.sh`
- [ ] Verify with `k6 version`
- [ ] Check all scripts are executable: `ls -l scripts/*.sh`

## File Verification

### Scripts
- [ ] `scripts/shell/install_k6.sh` exists and is executable
- [ ] `scripts/shell/run_load_tests.sh` exists and is executable
- [ ] `scripts/python/generate_load_test_report.py` exists and is executable
- [ ] `scripts/shell/validate_load_tests.sh` exists and is executable

### Test Files
- [ ] `load-tests/smoke-test.js` exists
- [ ] `load-tests/go-items.js` exists
- [ ] `load-tests/go-graph.js` exists
- [ ] `load-tests/python-specs.js` exists
- [ ] `load-tests/python-ai.js` exists
- [ ] `load-tests/websocket.js` exists
- [ ] `load-tests/e2e-scenario.js` exists
- [ ] `load-tests/stress-test.js` exists

### Documentation
- [ ] `docs/testing/load_testing_guide.md` exists
- [ ] `load-tests/README.md` exists
- [ ] `LOAD_TESTING_QUICK_START.md` exists
- [ ] `LOAD_TESTING_INDEX.md` exists
- [ ] `LOAD_TESTING_IMPLEMENTATION_SUMMARY.md` exists
- [ ] `LOAD_TESTING_COMPLETION_REPORT.md` exists
- [ ] `LOAD_TESTING_README.md` exists

### Directories
- [ ] `load-tests/` directory exists
- [ ] `load-tests/results/` directory exists
- [ ] `docs/testing/` directory exists

## Service Verification

- [ ] Start services: `docker-compose up -d`
- [ ] Check nginx: `curl http://localhost/health`
- [ ] Check Go backend: `curl http://localhost:8080/health`
- [ ] Check Python backend: `curl http://localhost:8000/health`

## Quick Test

- [ ] Run validation: `./scripts/shell/validate_load_tests.sh`
- [ ] Run smoke test: `k6 run load-tests/smoke-test.js`
- [ ] Verify smoke test passes (all checks green)
- [ ] No connection errors

## Makefile Integration (Optional)

- [ ] `cd backend/`
- [ ] Run `make install-k6`
- [ ] Run `make load-test-smoke`
- [ ] Verify Makefile targets work

## Full Suite Test

- [ ] Run `./scripts/shell/run_load_tests.sh`
- [ ] Wait for completion (~30 minutes)
- [ ] Check `load-tests/results/` for JSON files
- [ ] Verify `load-tests/results/report.html` generated
- [ ] Open HTML report: `open load-tests/results/report.html`
- [ ] Review all test results

## Performance Targets

Verify these targets in the HTML report:

### Go Backend
- [ ] Items CRUD p95 latency <50ms
- [ ] Items CRUD throughput >10k req/s
- [ ] Graph operations p95 <100ms

### Python Backend
- [ ] Spec analytics p95 latency <500ms
- [ ] Spec analytics throughput >1k req/s
- [ ] AI streaming p95 <10s

### WebSocket
- [ ] Concurrent connections >1000
- [ ] Connection time p95 <5s

## Troubleshooting

If any items fail, check:

### k6 Not Installed
```bash
./scripts/shell/install_k6.sh
k6 version
```

### Services Not Running
```bash
docker-compose ps
docker-compose up -d
docker-compose logs
```

### Permission Errors
```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### Connection Refused
```bash
# Check if ports are available
netstat -an | grep LISTEN | grep -E "(8080|8000|80)"

# Restart services
docker-compose restart
```

### High Error Rates
```bash
# Check logs
docker-compose logs go-backend
docker-compose logs python-backend

# Reduce load (edit test files)
# Lower target VUs in stages
```

## Next Steps

After completing this checklist:

1. [ ] Establish baseline metrics (save first run results)
2. [ ] Schedule regular testing (daily/weekly)
3. [ ] Set up monitoring alerts
4. [ ] Integrate with CI/CD pipeline
5. [ ] Document any performance issues
6. [ ] Plan optimization cycles

## Resources

- **Quick Start**: `LOAD_TESTING_QUICK_START.md`
- **Full Guide**: `docs/testing/load_testing_guide.md`
- **Index**: `LOAD_TESTING_INDEX.md`
- **Validation**: `./scripts/shell/validate_load_tests.sh`

## Status

Mark your overall status:

- [ ] Setup Complete
- [ ] Tests Running Successfully
- [ ] Performance Targets Met
- [ ] CI/CD Integrated
- [ ] Regular Testing Scheduled

---

**Date Completed**: _______________

**Completed By**: _______________

**Notes**:
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
