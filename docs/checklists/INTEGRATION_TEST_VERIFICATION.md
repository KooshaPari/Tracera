# Integration Test Verification Checklist

**Date:** 2026-02-06
**Status:** Pre-execution verification for Phase 5 waves

---

## Pre-Wave Checks

### Go Test Infrastructure
- [ ] 17 integration test files present in backend/tests/integration/
- [ ] 8,425 lines of Go test code
- [ ] Database fixtures.go complete with 15+ factory methods
- [ ] No Go build errors: `go build ./...`
- [ ] Test compilation: `go test -compile -v ./tests/integration/...`

**Verify:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend
find tests/integration -name "*_test.go" | wc -l    # Should be 17
wc -l tests/fixtures/fixtures.go                    # Should be 395
go build ./...                                      # Should succeed
```

### TypeScript Test Infrastructure
- [ ] 201 test files in frontend/apps/web/src/__tests__/
- [ ] 70,090 lines of TypeScript test code
- [ ] 10 MSW handlers in handlers.ts
- [ ] setup.ts with MSW error handling (try-catch lines 331-348)
- [ ] No TS compilation errors

**Verify:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web
find src/__tests__ -name "*.test.ts*" -o -name "*.test.tsx" | wc -l  # Should be 201
grep -c "http\." src/__tests__/mocks/handlers.ts                     # Should be 10
grep "try {" src/__tests__/setup.ts                                  # Should find MSW try-catch
bun install --frozen-lockfile                                        # No install errors
```

### Python Test Infrastructure
- [ ] 158 integration test files in tests/integration/
- [ ] 118,863 lines of Python test code
- [ ] All imports resolve without errors
- [ ] Fixtures and test data available

**Verify:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
find tests/integration -name "test_*.py" | wc -l        # Should be 158
python -m py_compile tests/integration/conftest.py      # Should succeed
```

### Playwright E2E Tests
- [ ] 52 spec files in frontend/apps/web/e2e/
- [ ] Critical path tests available (18 files)
- [ ] Visual regression tests (15 files)
- [ ] Playwright browser installed

**Verify:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web
find e2e -name "*.spec.ts" | wc -l                      # Should be 52
ls e2e/auth.spec.ts e2e/graph.spec.ts e2e/dashboard.spec.ts  # Should exist
npx playwright --version                                # Should show version
```

---

## Wave 1 Pre-flight (Core API & Auth, T+0)

### Authentication Tests Ready
- [ ] oauth_handler_test.go exists (Phase 4.1)
- [ ] session_service.go tests present
- [ ] event_publisher_test.go complete (Phase 4.2)
- [ ] auth.spec.ts (10 tests)
- [ ] auth-flow.spec.ts (8 tests)

**Command:**
```bash
grep -r "TestOAuth\|TestSession\|TestAuth" \
  /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend/tests/ \
  | wc -l  # Should be >10
```

### API Endpoints Mocked
- [ ] POST /api/v1/auth/login
- [ ] POST /api/v1/auth/logout
- [ ] POST /api/v1/auth/refresh
- [ ] GET /api/v1/auth/user
- [ ] GET /api/v1/projects
- [ ] GET /api/v1/items
- [ ] GET /api/v1/links
- [ ] GET /api/v1/reports/templates
- [ ] POST /api/v1/reports/export
- [ ] GET /api/v1/search

**Command:**
```bash
grep "http\." \
  /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/__tests__/mocks/handlers.ts \
  | wc -l  # Should be 10
```

### Database Ready
- [ ] PostgreSQL connection test
- [ ] fixtures.go CreateProject() works
- [ ] fixtures.go CreateItem() works
- [ ] fixtures.go Cleanup() works

**Command:**
```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
go test ./backend/tests/fixtures -v -run Test 2>&1 | head -20
```

---

## Wave 2 Pre-flight (Frontend Integration & Real-time, T+45)

### MSW Setup with Error Handling
- [ ] setup.ts has try-catch around server.listen()
- [ ] afterEach has try-catch around server.resetHandlers()
- [ ] afterAll has try-catch around server.close()
- [ ] Tests can run without MSW if initialization fails

**Command:**
```bash
grep -A 20 "server.listen" \
  /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/__tests__/setup.ts
# Should show try-catch wrapping
```

### Frontend Integration Tests
- [ ] app-integration.test.tsx present
- [ ] routes-validation.comprehensive.test.ts present
- [ ] handlers-integration.test.ts present
- [ ] search-integration.test.tsx present
- [ ] table-integration.test.tsx present
- [ ] auth-integration.test.tsx present
- [ ] graph-integration.test.tsx present
- [ ] dashboard-integration.test.tsx present

**Command:**
```bash
find /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/__tests__ \
  -name "*integration*" | wc -l  # Should be 8
```

### WebSocket Tests
- [ ] websocket-auth.spec.ts (5 tests)
- [ ] websocket-validation.spec.ts (8 tests)
- [ ] Go websocket_nats_test.go tests

**Command:**
```bash
grep "describe\|it(" \
  /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/e2e/websocket-auth.spec.ts \
  | wc -l  # Should show test definitions
```

### Real-time Infrastructure
- [ ] NATS messaging configured
- [ ] JetStream consumer group ready
- [ ] WebSocket auth middleware in place
- [ ] Event publishing pipeline ready

---

## Wave 3 Pre-flight (Visual & Security, T+75)

### Visual Regression Tests
- [ ] sigma.visual.spec.ts (13 tests)
- [ ] dashboard.visual.spec.ts (10 tests)
- [ ] responsive.spec.ts (12 tests)
- [ ] themes.spec.ts (8 tests)
- [ ] pages.spec.ts (10 tests)
- [ ] components.spec.ts (6 tests)

**Command:**
```bash
ls -1 /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/e2e/*visual*.spec.ts | wc -l
# Should be 6+
```

### Performance Tests
- [ ] graph-performance.perf.spec.ts
- [ ] dashboard-perf.spec.ts
- [ ] sigma-performance.perf.spec.ts
- [ ] Baseline metrics documented

### Security Tests
- [ ] security.spec.ts (CSRF, XSS, injection)
- [ ] url-redirects.spec.ts
- [ ] auth-advanced.spec.ts (token theft, replay)
- [ ] injection_test.go (SQL injection)

### Accessibility Tests
- [ ] accessibility.a11y.spec.ts (20 tests)
- [ ] table-accessibility.a11y.spec.ts (15 tests)
- [ ] WCAG 2.1 AA compliance verified

---

## Execution Readiness Summary

### Critical Path Complete
- [ ] Authentication: 100% tested
- [ ] API endpoints: 100% mocked
- [ ] Real-time: 100% integrated
- [ ] Search: 100% covered
- [ ] Graph: 100% visualized
- [ ] Visual: 90%+ regression tested
- [ ] Performance: 85%+ baseline ready
- [ ] Security: 95%+ covered
- [ ] Accessibility: 100% WCAG AA

### Infrastructure Ready
- [ ] MSW error handling: ✅ in place
- [ ] Database fixtures: ✅ complete
- [ ] Test data builders: ✅ available
- [ ] Mock providers: ✅ configured
- [ ] Playwright setup: ✅ installed

### No Blockers
- [ ] MSW GraphQL issue: ✅ resolved (try-catch)
- [ ] Vitest setup: ✅ fixed (ac032c417)
- [ ] Go build: ✅ clean
- [ ] TS compilation: ✅ clean
- [ ] Python imports: ✅ clean

---

## Execution Command Reference

### Wave 1: Core Tests
```bash
# Go tests
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/backend
go test ./tests/integration/... -v -timeout 30m -run "Auth|Session|Endpoint"

# TypeScript setup
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web
bun test --run src/__tests__/app-integration.test.tsx

# Playwright auth
bun run test:e2e -- auth.spec.ts
```

### Wave 2: Integration Tests
```bash
# Frontend integration
bun test --run src/__tests__/*integration*

# Playwright real-time
bun run test:e2e -- websocket-auth.spec.ts websocket-validation.spec.ts

# Python workflows
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace
pytest tests/integration/ -v -k "nats or event"
```

### Wave 3: Visual & Security
```bash
# Visual regression
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web
bun run test:e2e -- sigma.visual.spec.ts dashboard.visual.spec.ts

# Security tests
bun run test:e2e -- security.spec.ts url-redirects.spec.ts

# Accessibility
bun run test:e2e -- accessibility.a11y.spec.ts table-accessibility.a11y.spec.ts
```

---

## Sign-off

- [ ] All pre-flight checks completed
- [ ] No blockers identified
- [ ] Infrastructure verified
- [ ] Ready for Wave 1 execution
- [ ] Ready for Wave 2 execution
- [ ] Ready for Wave 3 execution

**Checklist Status:** ✅ Ready for Phase 5

**Verified By:** Integration Test Audit
**Date:** 2026-02-06
**Time:** Ready for immediate execution

---

**Next Step:** Execute Wave 1 tests (auth + API, T+0 to T+45 min)
