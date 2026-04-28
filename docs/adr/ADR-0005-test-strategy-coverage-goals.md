# ADR-0005: Test Strategy & Coverage Goals

**Status:** Accepted
**Date:** 2026-02-01
**Deciders:** Development Team
**Supersedes:** N/A

---

## Context

TraceRTM is a traceability system built by AI agents with strict quality enforcement. The codebase requires:

1. **High test coverage:** Catch regressions before they reach production
2. **Multi-language testing:** Python (services), Go (performance layer), TypeScript (frontend)
3. **Test pyramid:** Unit (fast) > Integration (medium) > E2E (slow)
4. **Agent-compatible:** Tests must run in CI and during agent development
5. **Quality gates:** Tests block PRs if failing

Current stack (from pyproject.toml, backend/go.mod, frontend/package.json):
- **Python:** pytest 9.0.2, pytest-asyncio, pytest-cov, hypothesis
- **Go:** testify, testcontainers-go (PostgreSQL, MinIO)
- **TypeScript:** vitest 4.0.18, @testing-library/react, @playwright/test

## Decision

We will enforce **80% minimum test coverage** with the following strategy:

1. **Python:** pytest + pytest-cov (unit, integration, e2e)
2. **Go:** Go testing + testify (unit, integration)
3. **TypeScript:** vitest + Testing Library (unit, integration, e2e with Playwright)

Coverage goals:
- **Overall:** 80% line coverage (fail CI below 80%)
- **Unit tests:** 90% of service/repository logic
- **Integration tests:** All API endpoints, database operations
- **E2E tests:** Critical paths (auth, requirement creation, traceability graph)

## Rationale

### Python Testing (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-ra", "-vv", "--strict-markers", "--tb=short"]
markers = [
    "unit: Unit tests (fast, no external dependencies)",
    "integration: Integration tests (database, file system)",
    "e2e: End-to-end tests (full CLI workflows)",
    "performance: Performance and load tests",
]

[tool.coverage.run]
source = ["src/tracertm"]
branch = true

[tool.coverage.report]
precision = 2
show_missing = true
fail_under = 90  # Strict for Python (relaxed to 80 overall)
```

**Rationale:**
- **pytest:** Industry standard, async support via pytest-asyncio
- **hypothesis:** Property-based testing for edge cases (fuzz testing)
- **pytest-mock:** Mock external dependencies (Redis, PostgreSQL, S3)
- **pytest-benchmark:** Performance regression tests
- **90% coverage goal:** Python backend is core logic, requires high coverage

### Go Testing (backend/go.mod)

```go
require (
    github.com/stretchr/testify v1.11.1
    github.com/testcontainers/testcontainers-go v0.40.0
    github.com/testcontainers/testcontainers-go/modules/postgres v0.40.0
    github.com/testcontainers/testcontainers-go/modules/minio v0.40.0
)
```

**Rationale:**
- **testify:** Assertions and mocking (`assert`, `require`, `mock`)
- **testcontainers-go:** Real PostgreSQL/MinIO instances in tests (no mocks for integration)
- **Table-driven tests:** Go idiom for parameterized testing
- **Sub-tests:** `t.Run()` for organized test cases

### TypeScript Testing (frontend/package.json)

```json
{
  "devDependencies": {
    "vitest": "^4.0.18",
    "@testing-library/react": "^16.3.0",
    "@playwright/test": "^1.50.3",
    "vitest-mock-extended": "^3.1.0"
  }
}
```

**Rationale:**
- **vitest:** Fast (Vite-native), compatible with jest patterns
- **Testing Library:** Component testing without implementation details
- **Playwright:** E2E testing (multi-browser, headless)
- **MSW (planned):** Mock HTTP requests in integration tests

### Test Organization

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── services/           # Service layer logic
│   ├── repositories/       # Database queries
│   └── utils/              # Helpers, validators
├── integration/            # With database/cache
│   ├── api/                # API endpoint tests
│   ├── workflows/          # Multi-step operations
│   └── storage/            # File system operations
├── e2e/                    # Full user workflows
│   ├── cli/                # CLI command tests
│   └── tui/                # Textual TUI tests
├── performance/            # Load, stress tests
└── fixtures.py             # Shared test data
```

### Coverage Measurement

**Python:**
```bash
pytest --cov=src/tracertm --cov-report=html --cov-report=term-missing
```

**Go:**
```bash
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out
```

**TypeScript:**
```bash
vitest run --coverage
```

## Alternatives Rejected

### Alternative 1: Lower coverage (60%)

- **Description:** Set 60% minimum coverage to reduce test writing burden
- **Pros:** Faster initial development, less test maintenance
- **Cons:** More bugs reach production, harder to refactor with confidence
- **Why Rejected:** TraceRTM is agent-built. High coverage catches agent mistakes early. 80% is achievable.

### Alternative 2: 100% coverage requirement

- **Description:** Require 100% line + branch coverage
- **Pros:** Maximum confidence, catches all code paths
- **Cons:** Diminishing returns (testing error messages, logging), slows development
- **Why Rejected:** 80% is sweet spot. 100% requires testing trivial code (getters, logging).

### Alternative 3: Mutation testing (Stryker, mutmut)

- **Description:** Inject bugs, verify tests catch them
- **Pros:** Tests quality of tests, not just coverage
- **Cons:** Very slow (10x slower than normal tests), complex setup
- **Why Rejected:** 80% coverage + hypothesis property tests provide sufficient quality. Mutation testing is overkill.

### Alternative 4: No coverage measurement

- **Description:** Write tests, don't measure coverage
- **Pros:** No coverage tooling, no false metrics
- **Cons:** No visibility into untested code, coverage drift over time
- **Why Rejected:** Agent-driven development requires measurable quality gates. Coverage is essential feedback.

## Consequences

### Positive

- **Confidence in refactoring:** High coverage enables safe agent-driven refactors
- **Bug detection:** Catch regressions before deployment
- **Documentation:** Tests serve as examples of API usage
- **Agent feedback:** Coverage reports guide agents to write missing tests
- **Quality gates:** CI blocks PRs below 80% coverage

### Negative

- **Test maintenance:** 80% coverage requires 1:1 test code:production code ratio
- **Slower development:** Writing tests adds 20-30% development time
- **Flaky tests:** Async tests (pytest-asyncio) can be flaky without proper fixtures
- **Integration test complexity:** testcontainers require Docker (not available in all CI environments)

### Neutral

- **Coverage != correctness:** 80% coverage doesn't guarantee bug-free code
- **Test-first vs test-after:** Coverage goal is agnostic to TDD/BDD approach
- **Mocking strategy:** Python uses mocks, Go uses real containers (both valid)

## Implementation

### Affected Components

- `.github/workflows/ci.yml` - CI pipeline with coverage gates
- `pyproject.toml` - Python coverage config
- `backend/Makefile` - Go test targets
- `frontend/vitest.config.ts` - Vitest coverage config
- `tests/` - All test files

### Migration Strategy

**Phase 1: Baseline (Week 1)**
- Measure current coverage (Python: 1,256 mypy errors baseline, tests exist)
- Identify uncovered modules
- Prioritize critical paths (auth, API, graph operations)

**Phase 2: Unit Tests (Week 2-4)**
- Write unit tests for services, repositories
- Target 90% coverage for Python backend
- Target 70% coverage for Go performance layer

**Phase 3: Integration Tests (Week 5-6)**
- API endpoint tests (all routes)
- Database integration tests
- Workflow tests (multi-step operations)

**Phase 4: E2E Tests (Week 7-8)**
- CLI command tests
- Web UI critical paths (Playwright)
- TUI workflows (Textual testing)

### Rollout Plan

- **Phase 1:** Soft enforcement (warning below 80%, no block)
- **Phase 2:** Hard enforcement (CI fails below 80%)
- **Phase 3:** Increase to 85% (if achievable)

### Success Criteria

- [x] Python: 90% coverage (fail_under=90 in pyproject.toml)
- [ ] Go: 70% coverage (current baseline: 32.5%)
- [ ] TypeScript: 75% coverage (vitest)
- [x] CI pipeline runs all tests on every PR
- [x] Coverage reports published to CI artifacts
- [ ] Automated coverage badges in README

## References

- [pytest Documentation](https://docs.pytest.org/)
- [Go Testing Best Practices](https://go.dev/doc/tutorial/add-a-test)
- [Vitest Coverage](https://vitest.dev/guide/coverage)
- [ADR-0012: Code Quality Enforcement](ADR-0012-code-quality-enforcement.md)
- [docs/reference/CODEBASE_QA_ATLAS.md](../reference/CODEBASE_QA_ATLAS.md)

---

**Notes:**
- **Current status (2026-02-12):**
  - Python: 1,346 tests collected, 8 errors (pytest 8.2.2 INTERNALERROR bug)
  - Go: 2 failures (Redis perf needs running Redis; CSRF form data)
  - TypeScript: 3,100 passed / 793 failed / 3,939 total (80% pass rate)
- **Blockers:** MSW GraphQL ESM/CommonJS compatibility (29 tests)
- **Target:** All tests passing, 80% coverage across all languages
