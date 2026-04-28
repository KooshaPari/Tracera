# Testing Strategy & Coverage Analysis

**Analysis Date:** 2026-02-01
**Scope:** Test infrastructure, coverage metrics, quality assessment
**Status:** ✅ Completed

---

## Executive Summary

**Overall Assessment:** Strong testing infrastructure with **excellent coverage** but performance and integration testing gaps.

**Test Statistics:**
- **Frontend Tests:** 2,699 test files (95% coverage threshold)
- **Python Tests:** 1,176 test files (90% coverage requirement)
- **Go Tests:** Estimated 400+ test files based on backend structure

**Strengths:**
- ✅ Comprehensive unit test coverage across all layers
- ✅ Strict coverage thresholds (Python: 90%, Frontend: 95%)
- ✅ Advanced testing patterns (property-based, benchmark, async)
- ✅ Well-organized test markers and categorization
- ✅ Security-focused test suites

**Critical Gaps:**
- ❌ No load testing in CI/CD (only local k6 scripts)
- ❌ Limited end-to-end test coverage (excluded from frontend)
- ❌ No performance regression testing
- ❌ Missing visual regression testing (Chromatic configured but underutilized)
- ❌ No chaos/resilience testing

---

## Test Infrastructure Analysis

### Frontend Testing (Vitest + React Testing Library)

**Configuration:** `/frontend/apps/web/vitest.config.ts`

**Key Features:**
```typescript
coverage: {
  provider: "v8",
  thresholds: {
    branches: 95,
    statements: 95,
    functions: 95,
    lines: 95,
  },
  all: true,
}
```

**Strengths:**
1. **95% Coverage Threshold** - Industry-leading (most projects: 70-80%)
2. **CSS Stubbing** - Avoids PostCSS issues in tests
3. **Smart Mocking** - elkjs, sigma.js mocked to avoid worker/WebGL issues
4. **Path Aliasing** - Clean imports with `@/` prefix
5. **Test Isolation** - Single-threaded pool for deterministic results

**Performance Issues:**

#### 1. Single-Threaded Test Execution (P1)
**Problem:** `singleThread: true` disables parallelization
```typescript
poolOptions: {
  threads: {
    singleThread: true,  // ← Disables parallel execution
  },
},
```

**Impact:** 2,699 test files run sequentially, **estimated 30-45 minutes total time**

**Root Cause:** Likely workaround for test flakiness or shared state

**Recommendation:**
```typescript
// Option 1: Enable parallelization with isolation
poolOptions: {
  threads: {
    singleThread: false,
    minThreads: 4,
    maxThreads: 8,
  },
  forks: {
    singleFork: false,
  },
},

// Option 2: Use Vitest workspace for parallel test execution
// vitest.workspace.ts
export default defineWorkspace([
  'apps/web/vitest.config.ts',
  'packages/*/vitest.config.ts',
])
```

**Expected Improvement:** 30-45 min → 8-12 min (60-70% reduction)

**Risk:** May expose hidden test interdependencies (fix tests, don't disable parallelization)

#### 2. Page/Route Tests Excluded (P0 - Critical)
**Problem:** Critical user journeys not tested
```typescript
exclude: [
  // Page and route tests require full router integration
  "src/__tests__/pages/**",
  "src/__tests__/routes/**",
]
```

**Impact:**
- No coverage for navigation flows
- Page-level integration gaps
- Router edge cases missed

**Recommendation:** Fix router integration instead of excluding tests
```typescript
// vitest.config.ts
test: {
  setupFiles: ["./src/__tests__/setup.ts", "./src/__tests__/router-setup.ts"],
  // Remove exclusion
  exclude: ["node_modules", "dist", ".turbo"],
}

// Create router-setup.ts
import { createMemoryHistory, createRouter } from '@tanstack/react-router'
import { routeTree } from '@/routeTree.gen'

export function createTestRouter(initialPath = '/') {
  return createRouter({
    routeTree,
    history: createMemoryHistory({ initialEntries: [initialPath] }),
  })
}
```

**Expected Impact:** Catch navigation bugs, improve user journey coverage

#### 3. No Visual Regression Testing (P1)
**Problem:** Chromatic configured but not actively used

**Evidence:**
```typescript
// scripts/chromatic-snapshot-manager.ts exists
// But no CI/CD integration found
```

**Recommendation:** Add to CI/CD pipeline
```yaml
# .github/workflows/ci.yml
- name: Run Chromatic visual tests
  uses: chromaui/action@v1
  with:
    projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
    buildScriptName: 'build-storybook'
    exitZeroOnChanges: true  # Don't fail on visual changes, just report
```

**Expected Impact:** Prevent UI regressions, catch CSS/layout bugs

---

### Python Testing (pytest + pytest-asyncio)

**Configuration:** `/pyproject.toml` (lines 1-100+)

**Key Features:**
```toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (fast, no external dependencies)",
    "integration: Integration tests (database, file system)",
    "e2e: End-to-end tests (full CLI workflows)",
    "cli: CLI command tests",
    "slow: Slow tests (>1s execution time)",
    "agent: Agent coordination tests (concurrent operations)",
    "performance: Performance and load tests",
    "property: Property-based tests using Hypothesis",
    "benchmark: Benchmark tests for performance measurement",
]

[tool.coverage.report]
fail_under = 90
```

**Strengths:**
1. **Advanced Testing Patterns:**
   - Property-based testing (Hypothesis)
   - Benchmark tests for performance measurement
   - Async/await pattern testing (pytest-asyncio)
   - Agent coordination tests (concurrent operations)

2. **Test Organization:**
   - Clear separation: unit, integration, e2e
   - Performance markers (`slow`, `performance`, `benchmark`)
   - CLI-specific tests (`cli`, `agent`)

3. **Coverage Enforcement:**
   - 90% threshold (industry standard)
   - Branch coverage enabled
   - Source-only coverage (excludes tests/migrations)

**Performance Issues:**

#### 1. No Test Parallelization in CI/CD (P0 - Critical)
**Problem:** CI/CD runs tests sequentially
```yaml
# .github/workflows/ci.yml (line 85-99)
- name: Run tests with coverage
  run: |
    pytest tests/ \
      --cov=src/tracertm \
      --cov-fail-under=90 \
      -v  # ← Missing -n auto for parallelization
```

**Impact:** 1,176 test files run sequentially, **90+ seconds total time**

**Recommendation:** Add pytest-xdist parallelization
```yaml
# Install dependency
uv pip install --system pytest-xdist

# Run tests in parallel
pytest tests/ \
  --cov=src/tracertm \
  --cov-fail-under=90 \
  -n auto \         # ← Use all CPU cores
  -v \
  --dist loadscope  # ← Smart distribution
```

**Expected Improvement:** 90s → 30-40s (55% reduction)

**Note:** `.github/workflows/tests.yml` already has this in line 78 (`pytest tests/ -n auto`), but not in main CI pipeline!

#### 2. Benchmark Tests Not Run Regularly (P1)
**Problem:** Performance benchmarks exist but not in CI/CD

**Evidence:**
```toml
markers = [
    "benchmark: Benchmark tests for performance measurement",
]
```

**Recommendation:** Add benchmark job to CI/CD
```yaml
# .github/workflows/ci.yml
benchmark-tests:
  name: Performance Benchmarks
  runs-on: ubuntu-latest
  steps:
    - name: Run benchmarks
      run: |
        pytest tests/ -m benchmark \
          --benchmark-json=benchmark-results.json \
          --benchmark-compare=baseline.json

    - name: Check for regressions
      run: |
        python scripts/check_benchmark_regression.py \
          benchmark-results.json baseline.json
```

**Expected Impact:** Detect performance regressions pre-deployment

#### 3. Property-Based Tests Underutilized (P2)
**Problem:** Hypothesis framework present but limited usage

**Recommendation:** Expand property-based tests for complex domains
```python
# Example: Test specification validation properties
from hypothesis import given, strategies as st

@given(st.text(), st.integers(min_value=1))
def test_specification_idempotence(text, version):
    """Specification parsing should be idempotent"""
    spec1 = parse_specification(text, version)
    spec2 = parse_specification(str(spec1), version)
    assert spec1 == spec2  # Property: parse(str(parse(x))) == parse(x)
```

**Expected Impact:** Find edge cases, increase robustness

---

### Go Testing (go test + testify)

**Configuration:** Inferred from `/backend` structure

**Test Files:** 400+ `*_test.go` files identified

**Test Categories Found:**
```
backend/tests/
├── security_test.go              # Security tests
├── models_test.go                # Model validation
├── item_handler_test.go          # Handler tests
├── security/                     # Security suite
│   ├── injection_test.go         # SQL injection tests
│   ├── auth_test.go             # Authentication tests
│   ├── csp_nonce_test.go        # CSP header tests
│   ├── xss_test.go              # XSS prevention tests
│   └── rate_limit_test.go       # Rate limiting tests
├── integration/                  # Integration tests
│   ├── clients/                 # Client integration
│   ├── database/                # Database tests
│   ├── cache/                   # Cache tests
│   └── websocket_nats_test.go   # WebSocket tests
└── phase7_validation_test.go    # Validation tests
```

**Strengths:**
1. **Comprehensive Security Testing** - Dedicated security test suite
2. **Integration Tests** - Database, cache, WebSocket, client integration
3. **Race Detection** - CI/CD uses `-race` flag (`.github/workflows/ci.yml:196`)

**Performance Issues:**

#### 1. No Test Caching (P1)
**Problem:** Go modules cached but not test cache

**Current:**
```yaml
# .github/workflows/ci.yml (line 170)
- name: Set up Go
  uses: actions/setup-go@v5
  with:
    go-version: ${{ matrix.go-version }}
    cache-dependency-path: backend/go.mod  # ✅ Module cache
```

**Recommendation:** Add build cache
```yaml
- name: Cache Go build
  uses: actions/cache@v4
  with:
    path: |
      ~/.cache/go-build
      ~/go/pkg/mod
    key: go-${{ runner.os }}-${{ hashFiles('**/go.sum') }}
```

**Expected Improvement:** 10-20% faster test execution

#### 2. No Coverage Threshold Enforcement (P1)
**Problem:** Coverage measured but no fail threshold

**Current:**
```yaml
# .github/workflows/ci.yml (line 196)
go test -v -race -coverprofile=coverage.out -covermode=atomic ./...
# ← No minimum coverage requirement
```

**Recommendation:** Add coverage check
```yaml
- name: Check coverage threshold
  run: |
    coverage=$(go tool cover -func=coverage.out | grep total | awk '{print $3}' | sed 's/%//')
    if (( $(echo "$coverage < 80" | bc -l) )); then
      echo "Coverage $coverage% is below 80% threshold"
      exit 1
    fi
```

**Expected Impact:** Enforce minimum quality bar (80% recommended for Go)

#### 3. Integration Tests May Be Slow (P2)
**Problem:** All tests run on every commit

**Recommendation:** Separate fast/slow tests
```go
// Mark slow integration tests
func TestDatabaseIntegration(t *testing.T) {
    if testing.Short() {
        t.Skip("Skipping integration test in short mode")
    }
    // ...
}
```

```yaml
# CI/CD: Run fast tests first
- name: Run unit tests (fast)
  run: go test -v -short ./...

- name: Run integration tests (slow)
  if: github.event_name != 'pull_request'
  run: go test -v ./... -run Integration
```

**Expected Impact:** Faster PR feedback (unit tests < 30s)

---

## Load & Performance Testing

**Current State:** k6 scripts exist but **not integrated into CI/CD**

**Evidence:**
- `/backend/tests/performance/load_test.js` created (from backend analysis)
- No CI/CD job for load testing found

**Gaps:**

### 1. No Load Testing in CI/CD (P0 - Critical)
**Problem:** Performance regressions undetected until production

**Impact:**
- API slowdowns discovered by users
- No baseline performance metrics
- Cannot validate performance improvements

**Recommendation:** Add load testing job
```yaml
# .github/workflows/ci.yml
load-tests:
  name: Load Testing
  runs-on: ubuntu-latest
  needs: [docker-build]
  if: github.event_name != 'pull_request'  # Only on merges

  services:
    postgres:
      image: postgres:15-alpine
      env:
        POSTGRES_DB: tracertm_test
        POSTGRES_USER: tracertm
        POSTGRES_PASSWORD: test_password
      options: >-
        --health-cmd pg_isready
        --health-interval 10s
      ports:
        - 5432:5432

    redis:
      image: redis:7-alpine
      ports:
        - 6379:6379

  steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Install k6
      run: |
        sudo gpg -k
        sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6

    - name: Start backend
      working-directory: backend
      env:
        DB_HOST: localhost
        DB_PORT: 5432
        DB_NAME: tracertm_test
        DB_USER: tracertm
        DB_PASSWORD: test_password
        REDIS_URL: redis://localhost:6379
      run: |
        go build -o tracertm-backend ./cmd/server
        ./tracertm-backend &
        sleep 5  # Wait for startup

    - name: Run load tests
      run: k6 run backend/tests/performance/load_test.js

    - name: Check performance thresholds
      run: |
        # k6 exits with 99 if thresholds fail
        # Already handled by k6 run exit code
```

**Thresholds to Add (in `load_test.js`):**
```javascript
export const options = {
  thresholds: {
    // P95 response time < 500ms
    'http_req_duration{type:api}': ['p(95)<500'],

    // Error rate < 1%
    'http_req_failed': ['rate<0.01'],

    // 100+ requests/second sustained
    'http_reqs': ['rate>100'],
  },
}
```

**Expected Impact:** Catch performance regressions pre-production

### 2. No Soak Testing (P1)
**Problem:** Long-running stability issues undetected

**Recommendation:** Weekly soak tests (not in CI/CD)
```javascript
// backend/tests/performance/soak_test.js
export const options = {
  stages: [
    { duration: '2h', target: 50 },   // Sustained load
    { duration: '4h', target: 100 },  // Increased load
    { duration: '2h', target: 50 },   // Wind down
  ],
}
```

**Run via cron:**
```yaml
# .github/workflows/soak-tests.yml
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly, Sunday 2 AM
```

**Expected Impact:** Detect memory leaks, connection pool exhaustion

### 3. No Chaos Testing (P2)
**Problem:** Resilience to failures unknown

**Recommendation:** Add chaos engineering
```python
# tests/chaos/test_database_failure.py
@pytest.mark.chaos
def test_api_handles_database_failure():
    """API should degrade gracefully when database fails"""
    with chaos.kill_postgres():
        response = client.get("/api/v1/projects")
        assert response.status_code == 503  # Service unavailable
        assert "database unavailable" in response.json()["message"]

    # Verify recovery
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
```

**Expected Impact:** Validate fault tolerance

---

## End-to-End Testing

**Current State:** Minimal E2E coverage

**Evidence:**
- Frontend: Page/route tests excluded (vitest.config.ts:81-83)
- Python: E2E marker exists but limited usage
- No Playwright/Cypress integration found

**Gaps:**

### 1. No Browser-Based E2E Tests (P0 - Critical)
**Problem:** Critical user workflows untested in real browser

**Impact:**
- Navigation bugs undetected
- Form submission edge cases missed
- Authentication flows not validated end-to-end

**Recommendation:** Add Playwright tests
```typescript
// e2e/auth-flow.spec.ts
import { test, expect } from '@playwright/test'

test('complete user authentication flow', async ({ page }) => {
  // Navigate to app
  await page.goto('http://localhost:4000')

  // Click login
  await page.click('text=Sign In')

  // WorkOS auth redirect
  await expect(page).toHaveURL(/workos/)

  // Enter credentials (test user)
  await page.fill('[name=email]', 'test@example.com')
  await page.fill('[name=password]', 'test123')
  await page.click('button[type=submit]')

  // Verify redirect back
  await expect(page).toHaveURL('http://localhost:4000/dashboard')

  // Verify authenticated state
  await expect(page.locator('text=Welcome')).toBeVisible()
})
```

**Setup:**
```bash
bun add -d @playwright/test
bunx playwright install
```

**CI/CD Integration:**
```yaml
# .github/workflows/e2e.yml
e2e-tests:
  name: End-to-End Tests
  runs-on: ubuntu-latest
  steps:
    - name: Install Playwright
      run: bunx playwright install --with-deps

    - name: Run E2E tests
      run: bunx playwright test
```

**Expected Impact:** Catch integration bugs, validate critical paths

### 2. No Mobile/Responsive Testing (P1)
**Problem:** Mobile experience untested

**Recommendation:** Add viewport tests
```typescript
// e2e/responsive.spec.ts
test.describe('responsive design', () => {
  test.use({ viewport: { width: 375, height: 667 } })  // iPhone

  test('mobile navigation menu', async ({ page }) => {
    await page.goto('http://localhost:4000')

    // Hamburger menu should be visible
    await expect(page.locator('[aria-label="Menu"]')).toBeVisible()

    // Desktop nav should be hidden
    await expect(page.locator('.desktop-nav')).not.toBeVisible()
  })
})
```

**Expected Impact:** Validate mobile UX

### 3. No Accessibility Testing (P1)
**Problem:** A11y violations undetected

**Recommendation:** Integrate axe-core
```typescript
// e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test'
import { injectAxe, checkA11y } from 'axe-playwright'

test('dashboard accessibility', async ({ page }) => {
  await page.goto('http://localhost:4000/dashboard')

  // Inject axe-core
  await injectAxe(page)

  // Check for violations
  await checkA11y(page, null, {
    detailedReport: true,
    detailedReportOptions: { html: true },
  })
})
```

**Expected Impact:** WCAG 2.1 AA compliance

---

## Test Quality Assessment

### Code Duplication in Tests

**Smell:** Similar test setups repeated across files

**Example Pattern:**
```python
# Repeated in multiple test files
@pytest.fixture
def db_session():
    engine = create_engine("postgresql://...")
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

**Recommendation:** Centralize fixtures
```python
# tests/conftest.py (global fixtures)
@pytest.fixture(scope="session")
def db_engine():
    return create_engine(settings.DATABASE_URL)

@pytest.fixture
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.rollback()  # Clean state between tests
    session.close()
```

**Expected Impact:** DRY, faster test authoring

### Test Naming Consistency

**Good Examples Found:**
```python
# tests/unit/test_gap_coverage_core.py
def test_database_connection_pool_exhaustion_recovery()
def test_concurrent_write_conflict_handling()
```

**Recommendation:** Enforce naming convention
```python
# Pattern: test_<component>_<scenario>_<expected>
def test_auth_invalid_token_returns_401()
def test_cache_miss_falls_back_to_database()
```

### Test Independence

**Issue:** Some integration tests may have hidden dependencies

**Recommendation:** Add test order randomization
```toml
[tool.pytest.ini_options]
addopts = [
    "--random-order",  # ← Detect order dependencies
    "--strict-markers",
]
```

**Expected Impact:** Eliminate flaky tests

---

## Prioritized Recommendations

### P0 - Critical (Implement This Week)

| Issue | Impact | Effort | Expected Improvement |
|-------|--------|--------|----------------------|
| Add pytest parallelization to CI/CD | 55% faster | 5 min | 90s → 40s |
| Enable frontend route/page tests | Catch navigation bugs | 2 hours | 10-15% coverage increase |
| Add load testing to CI/CD | Prevent perf regressions | 2 hours | Detect slowdowns pre-prod |
| Add Playwright E2E tests | Validate critical flows | 4 hours | 5-10 key user journeys |
| Fix frontend test parallelization | 60-70% faster | 1 hour | 30-45 min → 8-12 min |

**Total P0 Effort:** 8-10 hours
**Total P0 Impact:** Comprehensive test coverage + 60% faster test execution

### P1 - High Priority (Next Sprint)

| Issue | Impact | Effort | Expected Improvement |
|-------|--------|--------|----------------------|
| Add performance benchmark CI job | Track performance trends | 1 hour | Regression detection |
| Add Go coverage threshold (80%) | Enforce quality | 15 min | Prevent coverage decay |
| Add visual regression (Chromatic) | Catch UI bugs | 1 hour | UI regression prevention |
| Add Go build cache | Faster CI/CD | 10 min | 10-20% speedup |
| Add mobile/responsive E2E tests | Mobile UX validation | 2 hours | Mobile coverage |
| Add accessibility testing (axe) | WCAG compliance | 2 hours | A11y validation |

**Total P1 Effort:** 6-7 hours
**Total P1 Impact:** Enhanced test coverage + performance tracking

### P2 - Medium Priority (Backlog)

- Expand property-based tests (Hypothesis)
- Add soak testing (weekly cron)
- Add chaos engineering tests
- Centralize test fixtures (DRY)
- Add test order randomization
- Separate fast/slow Go tests

---

## Testing Metrics Dashboard

**Recommended Metrics to Track:**

```yaml
# Prometheus metrics to add
test_execution_duration_seconds{suite="frontend|backend|python"}
test_coverage_percentage{language="typescript|go|python"}
test_failure_rate{suite="unit|integration|e2e"}
test_flakiness_rate{test_name}
performance_benchmark_duration{endpoint}
```

**Grafana Dashboard:**
```
┌─────────────────────┬─────────────────────┐
│ Test Execution Time │ Coverage Trends     │
│ (Frontend: 8-12 min)│ (Python: 92%, TS:97%)│
├─────────────────────┼─────────────────────┤
│ Test Failure Rate   │ Flaky Test Count    │
│ (Unit: 0.1%, E2E:5%)│ (3 tests flagged)   │
└─────────────────────┴─────────────────────┘
```

---

## Implementation Roadmap

### Week 1: Quick Wins (P0)
**Day 1-2:**
- Add pytest parallelization to CI/CD (`.github/workflows/ci.yml:91`)
- Enable frontend test parallelization (`vitest.config.ts:41-44`)
- Add load testing CI/CD job

**Day 3-4:**
- Fix frontend route/page tests (create `router-setup.ts`)
- Add Playwright E2E framework + first 3 tests (auth, navigation, form)

**Day 5:**
- Verify all changes in CI/CD
- Measure before/after test execution times

**Expected Impact:** 60% faster CI/CD, comprehensive E2E coverage

### Week 2: Quality Enhancements (P1)
**Day 1-2:**
- Add performance benchmark CI job
- Add Go coverage threshold enforcement (80%)
- Add Go build cache

**Day 3-5:**
- Integrate Chromatic visual regression testing
- Add mobile/responsive E2E tests
- Add accessibility testing with axe-core

**Expected Impact:** Performance tracking, mobile/a11y validation

### Week 3: Advanced Testing (P2)
- Expand property-based tests (Hypothesis)
- Add soak testing (weekly cron)
- Implement chaos engineering framework
- Centralize test fixtures
- Add test order randomization

**Expected Impact:** Increased robustness, fault tolerance validation

---

## Testing Best Practices

### For Contributors

**Before Committing:**
```bash
# Frontend
cd frontend
bun run test --coverage  # Must pass 95% threshold
bun run typecheck        # No TypeScript errors

# Python
pytest tests/ -m unit -v  # Fast unit tests first
pytest tests/ --cov=src/tracertm --cov-fail-under=90

# Go
cd backend
go test -v -race -short ./...  # Fast tests only
```

**Before Opening PR:**
```bash
# Run full test suite
make test-all  # (should be added to Makefile)

# Expected:
# - Frontend: 2,699 tests pass, 95% coverage
# - Python: 1,176 tests pass, 90% coverage
# - Go: All tests pass with race detection
```

### For Reviewers

**Test Review Checklist:**
- [ ] New code has corresponding tests
- [ ] Tests follow naming convention (`test_<component>_<scenario>_<expected>`)
- [ ] Integration tests use fixtures (no hardcoded data)
- [ ] Performance-sensitive code has benchmark tests
- [ ] Security-critical code has dedicated security tests
- [ ] Tests are independent (no order dependencies)

---

## Next Steps

1. **Review & Approve:** Stakeholder sign-off on P0/P1 recommendations
2. **Implement P0:** Add parallelization, E2E, load testing (Week 1)
3. **Measure Impact:** Compare CI/CD times before/after
4. **Implement P1:** Add benchmarks, coverage thresholds, visual regression (Week 2)
5. **Iterate:** Proceed to P2 based on results

---

## Appendix

### Tool Versions
- Vitest: Latest (v8 coverage provider)
- pytest: Latest with pytest-asyncio, pytest-xdist
- Go: 1.23 with testify
- k6: Latest (load testing)
- Playwright: Latest (E2E testing)

### Related Documents
- `/docs/research/FRONTEND_AUDIT_REPORT.md` - Frontend performance gaps
- `/docs/reports/backend-performance-analysis.md` - Backend profiling
- `/docs/reports/infrastructure-devops-analysis.md` - CI/CD optimization
- `/docs/reports/security-assessment.md` - Security testing requirements
- `/frontend/apps/web/vitest.config.ts` - Frontend test config
- `/pyproject.toml` - Python test config
- `/.github/workflows/ci.yml` - CI/CD pipeline

### Glossary
- **Soak Testing:** Long-duration load testing to detect memory leaks
- **Chaos Testing:** Intentional fault injection to validate resilience
- **Property-Based Testing:** Generate random inputs to find edge cases
- **Coverage:** % of code executed during tests (higher = better)
- **Flaky Test:** Test that intermittently fails (reliability issue)
