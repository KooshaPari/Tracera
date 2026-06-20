# End-to-End Verification Checklist

**Version:** 1.0.0
**Last Updated:** January 31, 2026
**Purpose:** Complete verification of the unified development environment

## Overview

This checklist verifies all aspects of the TracerTM development environment, from cold start to production readiness. Complete each section in order.

---

## Phase 1: Cold Start Test

### Objective
Verify system can start from a completely stopped state.

### Prerequisites
- [ ] All services stopped: `rtm dev stop`
- [ ] No processes on ports 4000, 5173, 8080, 8000
- [ ] PostgreSQL and Neo4j running
- [ ] NATS running (if used)

### Cold Start Procedure

#### 1.1 Tool Installation Verification
```bash
# Verify all tools are installed
rtm dev install --verify
```

**Expected Output:**
```
✓ Go 1.21+ installed
✓ Bun 1.0+ installed
✓ Python 3.11+ installed
✓ Caddy 2.7+ installed
✓ Overmind 2.4+ installed
✓ PostgreSQL 14+ running
✓ Neo4j 5.0+ running (optional)
✓ NATS 2.9+ running (optional)
```

- [ ] All tools verified
- [ ] All required services running
- [ ] Environment variables configured

#### 1.2 First Start
```bash
# Start all services
rtm dev start
```

**Expected Output:**
```
system | Tmux socket name: overmind-TracerTM-xyz
system | Starting…
caddy  | started with pid 12345
api    | started with pid 12346
frontend | started with pid 12347
python | started with pid 12348

api    | API server starting on :8080
frontend | VITE ready in 234ms
caddy  | Caddy 2.7.0 serving on :4000
python | Python CLI server ready on :8000
```

**Verification:**
- [ ] All 4 services started (caddy, api, frontend, python)
- [ ] No error messages in startup logs
- [ ] Startup time < 30 seconds
- [ ] PIDs assigned to all services

#### 1.3 Port Availability Check
```bash
# Verify all services are listening
lsof -i :4000,5173,8080,8000 | grep LISTEN
```

**Expected Output:**
```
caddy     12345 user TCP *:4000 (LISTEN)
vite      12347 user TCP *:5173 (LISTEN)
api       12346 user TCP *:8080 (LISTEN)
python    12348 user TCP *:8000 (LISTEN)
```

- [ ] Caddy listening on 4000
- [ ] Vite listening on 5173
- [ ] Go API listening on 8080
- [ ] Python CLI listening on 8000

---

## Phase 2: Service Health Verification

### Objective
Verify all services are healthy and responding correctly.

#### 2.1 Frontend Health Check
```bash
# Access frontend
curl -f http://localhost:4000/
```

**Expected:**
- [ ] HTTP 200 response
- [ ] HTML content returned
- [ ] Response time < 500ms

**Browser Test:**
- [ ] Open http://localhost:4000
- [ ] Page loads without errors
- [ ] No console errors in browser dev tools
- [ ] React app mounts successfully

#### 2.2 Go API Health Check
```bash
# Check API health endpoint
curl -f http://localhost:4000/api/v1/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-31T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "neo4j": "connected",
    "nats": "connected"
  }
}
```

- [ ] HTTP 200 response
- [ ] Status is "healthy"
- [ ] Database connected
- [ ] Neo4j connected (if enabled)
- [ ] NATS connected (if enabled)

#### 2.3 Python CLI Health Check
```bash
# Check Python CLI health
curl -f http://localhost:4000/api/py/health
```

**Expected:**
- [ ] HTTP 200 response
- [ ] JSON response with status
- [ ] Response time < 500ms

#### 2.4 API Documentation Check
```bash
# Access API documentation
curl -f http://localhost:4000/docs
```

- [ ] HTTP 200 response
- [ ] Swagger/OpenAPI UI loads
- [ ] API endpoints listed
- [ ] Can interact with endpoints

---

## Phase 3: API Routing Tests

### Objective
Verify Caddy correctly routes requests to appropriate backend services.

#### 3.1 Go API Routes
```bash
# Test Go API routing through Caddy
curl -f http://localhost:4000/api/v1/projects
curl -f http://localhost:4000/api/v1/items
curl -f http://localhost:4000/api/v1/users
```

**For each endpoint:**
- [ ] HTTP 200 or 401 (auth required) response
- [ ] JSON response returned
- [ ] Correct content-type header
- [ ] Response time < 1000ms

#### 3.2 Python CLI Routes
```bash
# Test Python CLI routing through Caddy
curl -f http://localhost:4000/api/py/cli/status
curl -f http://localhost:4000/api/py/cli/projects
```

**For each endpoint:**
- [ ] HTTP 200 response
- [ ] JSON response returned
- [ ] Correct content-type header
- [ ] Response time < 1000ms

#### 3.3 Static Asset Routing
```bash
# Test frontend static assets
curl -f http://localhost:4000/assets/index.css
curl -f http://localhost:4000/favicon.ico
```

- [ ] Static assets load correctly
- [ ] Correct content-type headers
- [ ] No 404 errors
- [ ] Assets cached appropriately

#### 3.4 WebSocket Routing
```bash
# Test WebSocket connection (requires wscat or similar)
wscat -c ws://localhost:4000/ws
```

**Expected:**
- [ ] Connection establishes successfully
- [ ] Can send/receive messages
- [ ] Connection stays alive
- [ ] No connection errors

---

## Phase 4: Auto-Reload Verification

### Objective
Verify hot module replacement and auto-reload work for all services.

#### 4.1 Frontend Hot Reload Test
```bash
# Make a change to a frontend component
echo "// Test change" >> frontend/apps/web/src/App.tsx
```

**Watch frontend logs:**
```bash
rtm dev logs frontend
```

**Expected:**
- [ ] Vite detects file change
- [ ] HMR update applied
- [ ] Page updates without full reload
- [ ] Update time < 500ms
- [ ] No errors in console

**Browser verification:**
- [ ] Changes appear immediately in browser
- [ ] No page refresh required
- [ ] Application state preserved

#### 4.2 Go API Auto-Reload Test
```bash
# Make a change to a Go file
echo "// Test change" >> backend/internal/api/handlers/health.go
```

**Watch API logs:**
```bash
rtm dev logs api
```

**Expected:**
- [ ] File watcher detects change
- [ ] Go service rebuilds
- [ ] Service restarts automatically
- [ ] Rebuild time < 5 seconds
- [ ] API accessible during restart (Caddy buffers)

**Verification:**
```bash
# API should still respond
curl -f http://localhost:4000/api/v1/health
```

- [ ] API responds after rebuild
- [ ] No downtime experienced

#### 4.3 Python CLI Auto-Reload Test
```bash
# Make a change to Python code
echo "# Test change" >> src/tracertm/cli/main.py
```

**Watch Python logs:**
```bash
rtm dev logs python
```

**Expected:**
- [ ] Python service detects change
- [ ] Service reloads automatically
- [ ] Reload time < 2 seconds
- [ ] No errors during reload

**Verification:**
```bash
curl -f http://localhost:4000/api/py/health
```

- [ ] Python service responds after reload

---

## Phase 5: Service Restart Test

### Objective
Verify services can be individually restarted without affecting others.

#### 5.1 Restart Individual Services
```bash
# Restart Go API
overmind restart api

# Verify other services still running
curl -f http://localhost:4000/
curl -f http://localhost:4000/api/py/health
```

- [ ] API restarts successfully
- [ ] Frontend remains accessible
- [ ] Python CLI remains accessible
- [ ] Caddy continues routing

```bash
# Restart Frontend
overmind restart frontend

# Verify other services still running
curl -f http://localhost:4000/api/v1/health
curl -f http://localhost:4000/api/py/health
```

- [ ] Frontend restarts successfully
- [ ] API remains accessible
- [ ] Python CLI remains accessible

```bash
# Restart Python CLI
overmind restart python

# Verify other services still running
curl -f http://localhost:4000/
curl -f http://localhost:4000/api/v1/health
```

- [ ] Python CLI restarts successfully
- [ ] Frontend remains accessible
- [ ] API remains accessible

#### 5.2 Graceful Shutdown Test
```bash
# Stop all services gracefully
rtm dev stop
```

**Expected:**
- [ ] All services receive shutdown signal
- [ ] Services shut down cleanly (no forced kills)
- [ ] Ports are released
- [ ] No orphaned processes
- [ ] Shutdown time < 10 seconds

**Verification:**
```bash
# Verify no processes remain
lsof -i :4000,5173,8080,8000
# Should return nothing
```

---

## Phase 6: Debug Workflow Test

### Objective
Verify debugging and troubleshooting tools work correctly.

#### 6.1 Interactive Console Test
```bash
# Connect to API service
overmind connect api
```

**Expected:**
- [ ] Terminal attaches to API process
- [ ] Can see live logs
- [ ] Can send signals (Ctrl+C captured by Overmind, not service)
- [ ] Can detach cleanly (Ctrl+B, D)

#### 6.2 Log Viewing Test
```bash
# View logs for each service
rtm dev logs api
rtm dev logs frontend
rtm dev logs python
rtm dev logs caddy
```

**For each service:**
- [ ] Logs are visible and readable
- [ ] Log levels are appropriate
- [ ] Timestamps are present
- [ ] Can scroll through history

#### 6.3 Real-Time Log Tailing
```bash
# Follow logs in real-time
rtm dev logs --follow api
```

**Expected:**
- [ ] New log entries appear immediately
- [ ] No delay in log output
- [ ] Can stop with Ctrl+C
- [ ] Logs are properly formatted

#### 6.4 Service Status Check
```bash
# Check status of all services
rtm dev status
```

**Expected Output:**
```
Service   | PID   | Status  | Uptime
----------|-------|---------|--------
caddy     | 12345 | running | 00:15:32
api       | 12346 | running | 00:15:31
frontend  | 12347 | running | 00:15:30
python    | 12348 | running | 00:15:29
```

- [ ] All services show "running"
- [ ] PIDs are valid
- [ ] Uptimes are reasonable

---

## Phase 7: Error Handling Test

### Objective
Verify system handles errors gracefully.

#### 7.1 Service Crash Recovery
```bash
# Force kill the API service
kill -9 $(pgrep -f "go run.*api")
```

**Expected:**
- [ ] Overmind detects crash
- [ ] Service automatically restarts
- [ ] Restart logged clearly
- [ ] Other services unaffected
- [ ] Recovery time < 5 seconds

**Verification:**
```bash
curl -f http://localhost:4000/api/v1/health
```

- [ ] API responds after recovery

#### 7.2 Port Conflict Handling
```bash
# Stop services
rtm dev stop

# Start a conflicting process on port 4000
python -m http.server 4000 &

# Try to start services
rtm dev start
```

**Expected:**
- [ ] Clear error message about port conflict
- [ ] Suggests how to resolve
- [ ] Doesn't hang or crash
- [ ] Other services don't start (fail-fast)

**Cleanup:**
```bash
pkill -f "http.server 4000"
rtm dev start
```

#### 7.3 Database Connection Loss
```bash
# Stop PostgreSQL temporarily
pg_ctl stop -D /usr/local/var/postgresql@14

# Check API health
curl http://localhost:4000/api/v1/health
```

**Expected:**
- [ ] API returns error status
- [ ] Error message is clear
- [ ] Service doesn't crash
- [ ] Logs show connection error

**Restart database:**
```bash
pg_ctl start -D /usr/local/var/postgresql@14
```

**Verification:**
- [ ] API reconnects automatically
- [ ] Health endpoint returns healthy
- [ ] No manual restart required

---

## Phase 8: Performance Baseline Tests

### Objective
Establish performance baselines for the development environment.

#### 8.1 API Response Time Test
```bash
# Test API endpoint response times (100 requests)
for i in {1..100}; do
  curl -w "%{time_total}\n" -o /dev/null -s http://localhost:4000/api/v1/health
done | awk '{sum+=$1} END {print "Average: " sum/NR " seconds"}'
```

**Expected:**
- [ ] Average response time < 100ms
- [ ] No timeouts
- [ ] No errors

#### 8.2 Frontend Load Time Test
```bash
# Measure frontend initial load time
curl -w "Time: %{time_total}s\n" -o /dev/null -s http://localhost:4000/
```

**Expected:**
- [ ] Initial load < 500ms
- [ ] HTML rendered
- [ ] No errors

#### 8.3 WebSocket Connection Test
```bash
# Test WebSocket connection stability (requires custom script)
# python test_websocket.py
```

**Expected:**
- [ ] Connection establishes < 1s
- [ ] Messages sent/received reliably
- [ ] No connection drops
- [ ] Ping/pong works

#### 8.4 Concurrent Request Test
```bash
# Send 10 concurrent requests
seq 10 | xargs -n1 -P10 curl -s http://localhost:4000/api/v1/health | jq -r .status
```

**Expected:**
- [ ] All requests succeed
- [ ] All return "healthy"
- [ ] No rate limiting in dev
- [ ] Response time < 500ms each

---

## Phase 9: Integration Test Suite

### Objective
Run automated integration tests to verify system functionality.

#### 9.1 Backend Integration Tests
```bash
cd backend
go test ./internal/... -tags=integration -v
```

**Expected:**
- [ ] All tests pass
- [ ] No skipped tests
- [ ] Coverage > 80%
- [ ] Test time < 60s

#### 9.2 Frontend E2E Tests
```bash
cd frontend/apps/web
bun run test:e2e critical-path.spec.ts
```

**Expected:**
- [ ] All critical path tests pass
- [ ] No flaky tests
- [ ] Test time < 120s
- [ ] Screenshots captured on failure

#### 9.3 API Contract Tests
```bash
# Test API contracts against OpenAPI spec
# (requires prism or similar tool)
prism mock openapi.yaml &
npm run test:contract
```

**Expected:**
- [ ] All endpoints match spec
- [ ] Request/response schemas valid
- [ ] No breaking changes detected

---

## Phase 10: Production Readiness Checks

### Objective
Verify system is ready for production deployment.

#### 10.1 Security Checks
```bash
# Check for security vulnerabilities
cd frontend && bun audit
cd backend && go list -json -m all | nancy sleuth
cd .. && pip-audit
```

**Expected:**
- [ ] No critical vulnerabilities
- [ ] No high-severity issues
- [ ] Dependencies up to date

#### 10.2 Build Verification
```bash
# Build production artifacts
cd frontend && bun run build
cd backend && go build -o bin/api ./cmd/api
cd .. && python -m build
```

**Expected:**
- [ ] Frontend builds without errors
- [ ] Backend compiles successfully
- [ ] Python package builds correctly
- [ ] Build time < 5 minutes
- [ ] Artifacts are optimized

#### 10.3 Environment Variable Check
```bash
# Verify all required env vars are documented
diff <(grep -o 'os.Getenv("[^"]*")' backend/**/*.go | cut -d'"' -f2 | sort -u) \
     <(grep -o '^[A-Z_]*=' .env.example | cut -d'=' -f1 | sort -u)
```

**Expected:**
- [ ] All env vars documented in .env.example
- [ ] No undocumented variables
- [ ] Sensible defaults provided

#### 10.4 Documentation Completeness
- [ ] README.md up to date
- [ ] API documentation complete
- [ ] Installation guide accurate
- [ ] Troubleshooting guide helpful
- [ ] Architecture documented

---

## Sign-off

### Verification Results

**Date:** ________________
**Tested By:** ________________
**Environment:** ________________

### Phase Results

- [ ] Phase 1: Cold Start Test - PASS/FAIL
- [ ] Phase 2: Service Health - PASS/FAIL
- [ ] Phase 3: API Routing - PASS/FAIL
- [ ] Phase 4: Auto-Reload - PASS/FAIL
- [ ] Phase 5: Service Restart - PASS/FAIL
- [ ] Phase 6: Debug Workflow - PASS/FAIL
- [ ] Phase 7: Error Handling - PASS/FAIL
- [ ] Phase 8: Performance Baseline - PASS/FAIL
- [ ] Phase 9: Integration Tests - PASS/FAIL
- [ ] Phase 10: Production Readiness - PASS/FAIL

### Issues Found

| Issue | Severity | Status |
|-------|----------|--------|
|       |          |        |
|       |          |        |

### Overall Status

- [ ] **APPROVED** - System ready for next phase
- [ ] **CONDITIONALLY APPROVED** - Minor issues, proceed with caution
- [ ] **REJECTED** - Critical issues, do not proceed

### Notes

_Additional comments and observations:_

---

## Appendix A: Common Issues and Solutions

### Issue: Services won't start
**Solution:** Check ports, verify tools installed, check logs

### Issue: Hot reload not working
**Solution:** Restart service, check file watchers, verify config

### Issue: API routes return 404
**Solution:** Check Caddy config, verify service is running, check logs

### Issue: Database connection fails
**Solution:** Verify PostgreSQL running, check credentials, check firewall

---

## Appendix B: Test Data

### Sample API Request
```bash
curl -X POST http://localhost:4000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Project", "description": "E2E test"}'
```

### Sample WebSocket Message
```json
{
  "type": "subscribe",
  "channel": "project:123",
  "token": "test-token"
}
```

---

**End of Checklist**
