# Testing Matrix

**Version:** 1.0.0
**Last Updated:** January 31, 2026
**Purpose:** Comprehensive testing framework for TracerTM development and deployment

## Overview

This testing matrix defines what to test at each phase of development, deployment criteria, performance benchmarks, and regression test procedures.

---

## Table of Contents

1. [Testing Phases](#testing-phases)
2. [Test Categories](#test-categories)
3. [Pass/Fail Criteria](#passfail-criteria)
4. [Performance Benchmarks](#performance-benchmarks)
5. [Regression Test Checklist](#regression-test-checklist)
6. [Test Coverage Requirements](#test-coverage-requirements)
7. [Test Execution Schedule](#test-execution-schedule)

---

## Testing Phases

### Phase 1: Development Testing (Continuous)

**When:** During active development
**Frequency:** Before each commit
**Duration:** < 5 minutes

| Test Type | What to Test | Tool/Command | Pass Criteria |
|-----------|--------------|--------------|---------------|
| Unit Tests | Go backend | `go test ./internal/...` | All pass, >80% coverage |
| Unit Tests | Frontend components | `bun test` | All pass, >85% coverage |
| Unit Tests | Python CLI | `pytest tests/` | All pass, >80% coverage |
| Linting | Go code | `golangci-lint run` | Zero errors, zero warnings |
| Linting | TypeScript | `bun run lint` | Zero errors, zero warnings |
| Linting | Python | `ruff check src/` | Zero errors |
| Type Check | TypeScript | `tsc --noEmit` | Zero errors |
| Format Check | All code | `bun run format:check` | All files formatted |

**Developer Actions:**
- [ ] Run tests before committing
- [ ] Fix all linting errors
- [ ] Maintain test coverage
- [ ] Update tests for new features

### Phase 2: Integration Testing (Pre-PR)

**When:** Before creating pull request
**Frequency:** Per feature completion
**Duration:** < 15 minutes

| Test Type | What to Test | Tool/Command | Pass Criteria |
|-----------|--------------|--------------|---------------|
| API Integration | All API endpoints | `go test -tags=integration` | All pass |
| Database Integration | Queries, migrations | `go test ./internal/db/...` | All pass, no timeouts |
| Service Integration | Go ↔ Python ↔ Frontend | Integration suite | All services communicate |
| WebSocket | Real-time connections | `bun run test:websocket` | Connect, send, receive, disconnect |
| Auth Flow | Login, logout, tokens | `bun run test:auth` | All auth scenarios work |

**Developer Actions:**
- [ ] Test feature end-to-end
- [ ] Verify database migrations
- [ ] Test API contracts
- [ ] Verify WebSocket events

### Phase 3: End-to-End Testing (Pre-Merge)

**When:** Before merging to main branch
**Frequency:** Per pull request
**Duration:** < 30 minutes

| Test Type | What to Test | Tool/Command | Pass Criteria |
|-----------|--------------|--------------|---------------|
| Critical Path | Core user journeys | `bun run test:e2e critical-path.spec.ts` | All critical flows work |
| UI/UX | All major features | `bun run test:e2e` | No visual regressions |
| Performance | Load times, responsiveness | `bun run test:performance` | Meets performance benchmarks |
| Cross-browser | Chrome, Firefox, Safari | Playwright tests | Works in all browsers |
| Mobile | Responsive design | Mobile emulation tests | Works on mobile viewports |
| Accessibility | WCAG 2.1 AA | `axe` tests | No violations |

**QA Actions:**
- [ ] Run full E2E test suite
- [ ] Test on multiple browsers
- [ ] Test on mobile devices
- [ ] Verify accessibility
- [ ] Check visual regressions

### Phase 4: Staging Testing (Pre-Deployment)

**When:** Before deploying to production
**Frequency:** Per release
**Duration:** < 2 hours

| Test Type | What to Test | Tool/Command | Pass Criteria |
|-----------|--------------|--------------|---------------|
| Smoke Tests | Critical functionality | Staging smoke test suite | All critical features work |
| Load Tests | Performance under load | `k6` or `artillery` | Handles expected load |
| Security Scan | Vulnerabilities | `npm audit`, `go-audit` | No critical/high vulnerabilities |
| Database Migration | Production-like data | Staging migration | Migration succeeds, no data loss |
| Environment Config | All env vars | Config verification | All required vars present |
| External Integrations | Third-party APIs | Integration tests | All integrations working |
| Monitoring | Logs, metrics, alerts | Check dashboards | All monitoring active |

**DevOps Actions:**
- [ ] Deploy to staging
- [ ] Run smoke tests
- [ ] Verify monitoring
- [ ] Test rollback procedure
- [ ] Sign off on deployment

### Phase 5: Production Testing (Post-Deployment)

**When:** After deploying to production
**Frequency:** Every deployment
**Duration:** < 30 minutes

| Test Type | What to Test | Tool/Command | Pass Criteria |
|-----------|--------------|--------------|---------------|
| Health Checks | All services | `curl /health` endpoints | All return 200 OK |
| Smoke Tests | Critical paths | Production smoke tests | All pass |
| Monitoring | Metrics, errors | Check dashboards | No anomalies |
| User Acceptance | Real user testing | Manual testing | No user complaints |
| Performance | Real-world performance | APM tools | Meets SLAs |

**Production Actions:**
- [ ] Verify deployment successful
- [ ] Run production smoke tests
- [ ] Monitor error rates
- [ ] Monitor performance
- [ ] Be ready for rollback

---

## Test Categories

### 1. Unit Tests

**Scope:** Individual functions, methods, components

**Go Backend:**
```bash
# Run all unit tests
go test ./internal/... -v

# Run with coverage
go test ./internal/... -cover -coverprofile=coverage.out

# View coverage report
go tool cover -html=coverage.out
```

**Frontend:**
```bash
# Run all unit tests
bun test

# Run with coverage
bun test --coverage

# Watch mode
bun test --watch
```

**Python CLI:**
```bash
# Run all unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

**Pass Criteria:**
- [ ] All tests pass
- [ ] Code coverage ≥ 80% (backend, Python)
- [ ] Code coverage ≥ 85% (frontend)
- [ ] No flaky tests
- [ ] Test execution time < 2 minutes

### 2. Integration Tests

**Scope:** Interactions between components, services, databases

**Database Integration:**
```bash
cd backend
go test ./internal/db/... -tags=integration -v
```

**API Integration:**
```bash
cd backend
go test ./internal/api/... -tags=integration -v
```

**Service Integration:**
```bash
# Requires running services
cd frontend/apps/web
bun run test:integration
```

**Pass Criteria:**
- [ ] All integration tests pass
- [ ] Services communicate correctly
- [ ] Database queries work
- [ ] No connection timeouts
- [ ] Test execution time < 5 minutes

### 3. End-to-End Tests

**Scope:** Complete user workflows from UI to database

**Critical Path Tests:**
```bash
cd frontend/apps/web
bun run test:e2e critical-path.spec.ts
```

**Full E2E Suite:**
```bash
cd frontend/apps/web
bun run test:e2e
```

**Specific Feature:**
```bash
bun run test:e2e auth-flow.spec.ts
bun run test:e2e graph-view.spec.ts
```

**Pass Criteria:**
- [ ] All E2E tests pass
- [ ] No visual regressions
- [ ] User flows complete successfully
- [ ] No console errors
- [ ] Test execution time < 10 minutes

### 4. Performance Tests

**Scope:** Response times, throughput, resource usage

**API Performance:**
```bash
# Test API endpoint response times
k6 run performance/api-load-test.js
```

**Frontend Performance:**
```bash
# Lighthouse CI
lhci autorun

# Or manual Lighthouse audit
lighthouse http://localhost:4000 --output json
```

**Load Testing:**
```bash
# Artillery load test
artillery run performance/load-test.yml
```

**Pass Criteria:**
- [ ] API response time p95 < 500ms
- [ ] Frontend initial load < 2s
- [ ] Time to interactive < 3s
- [ ] Lighthouse score > 90
- [ ] Handles expected concurrent users

### 5. Security Tests

**Scope:** Vulnerabilities, authentication, authorization

**Dependency Audit:**
```bash
# Frontend
cd frontend && bun audit

# Backend
go list -json -m all | nancy sleuth

# Python
pip-audit
```

**OWASP ZAP Scan:**
```bash
# Run security scan (requires OWASP ZAP)
zap-cli quick-scan http://localhost:4000
```

**Pass Criteria:**
- [ ] No critical vulnerabilities
- [ ] No high-severity vulnerabilities
- [ ] Auth/authz working correctly
- [ ] CORS configured properly
- [ ] CSRF protection active
- [ ] XSS prevention in place

### 6. Accessibility Tests

**Scope:** WCAG 2.1 AA compliance

**Automated Tests:**
```bash
# Run axe-core tests
cd frontend/apps/web
bun run test:a11y
```

**Manual Testing:**
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Color contrast meets WCAG AA
- [ ] Focus indicators visible
- [ ] Alt text on images

**Pass Criteria:**
- [ ] Zero axe violations (critical/serious)
- [ ] All interactive elements keyboard accessible
- [ ] ARIA labels correct
- [ ] Color contrast ratio ≥ 4.5:1

---

## Pass/Fail Criteria

### Development Phase

| Category | Pass Threshold | Failure Threshold |
|----------|----------------|-------------------|
| Unit Test Pass Rate | 100% | < 100% |
| Code Coverage | ≥ 80% | < 80% |
| Linting Errors | 0 | > 0 |
| Type Errors | 0 | > 0 |
| Build Success | Yes | No |

**Action if Failed:** Fix before committing

### Integration Phase

| Category | Pass Threshold | Failure Threshold |
|----------|----------------|-------------------|
| Integration Tests | 100% pass | < 100% |
| API Contract Tests | 100% pass | < 100% |
| Database Migrations | Success | Failure |
| Service Communication | All working | Any failing |

**Action if Failed:** Fix before creating PR

### E2E Phase

| Category | Pass Threshold | Failure Threshold |
|----------|----------------|-------------------|
| Critical Path Tests | 100% pass | < 100% |
| Full E2E Suite | ≥ 95% pass | < 95% |
| Visual Regression | 0 regressions | > 0 unexpected changes |
| Browser Compatibility | All browsers | Any browser fails |

**Action if Failed:** Fix before merging

### Staging Phase

| Category | Pass Threshold | Failure Threshold |
|----------|----------------|-------------------|
| Smoke Tests | 100% pass | < 100% |
| Load Tests | Meets targets | Below targets |
| Security Scan | No critical/high | Critical/high found |
| Migration | Success | Failure or data loss |

**Action if Failed:** Do not deploy to production

### Production Phase

| Category | Pass Threshold | Failure Threshold |
|----------|----------------|-------------------|
| Health Checks | All healthy | Any unhealthy |
| Error Rate | < 0.1% | > 1% |
| Response Time (p95) | < 500ms | > 1000ms |
| Uptime | > 99.9% | < 99.5% |

**Action if Failed:** Rollback immediately

---

## Performance Benchmarks

### API Performance Targets

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Response Time (p50) | < 100ms | > 200ms | > 500ms |
| Response Time (p95) | < 500ms | > 1000ms | > 2000ms |
| Response Time (p99) | < 1000ms | > 2000ms | > 5000ms |
| Throughput | > 1000 req/s | < 500 req/s | < 100 req/s |
| Error Rate | < 0.01% | > 0.1% | > 1% |
| Database Query Time | < 50ms | > 100ms | > 500ms |

### Frontend Performance Targets

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| First Contentful Paint | < 1s | > 2s | > 3s |
| Time to Interactive | < 3s | > 5s | > 8s |
| Total Blocking Time | < 200ms | > 500ms | > 1000ms |
| Cumulative Layout Shift | < 0.1 | > 0.25 | > 0.5 |
| Largest Contentful Paint | < 2.5s | > 4s | > 6s |
| Lighthouse Score | > 90 | < 80 | < 70 |

### Database Performance Targets

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Query Response Time | < 50ms | > 100ms | > 500ms |
| Connection Pool Usage | < 70% | > 80% | > 90% |
| Transaction Time | < 100ms | > 500ms | > 1000ms |
| Index Hit Rate | > 99% | < 95% | < 90% |

### Resource Usage Targets

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| CPU Usage | < 60% | > 70% | > 85% |
| Memory Usage | < 70% | > 80% | > 90% |
| Disk Usage | < 70% | > 80% | > 90% |
| Network I/O | < 50% capacity | > 70% | > 90% |

---

## Regression Test Checklist

Run this checklist after any significant change to ensure no existing functionality is broken.

### Core Functionality

#### Authentication & Authorization
- [ ] User can log in with username/password
- [ ] User can log in with OAuth (Google, GitHub)
- [ ] User can log out
- [ ] Session persists across page refreshes
- [ ] Expired tokens are handled correctly
- [ ] Unauthorized access is blocked

#### Project Management
- [ ] Can create new project
- [ ] Can edit project details
- [ ] Can delete project
- [ ] Can list all projects
- [ ] Can search projects
- [ ] Can filter projects by status

#### Item Management
- [ ] Can create new item (requirement, task, test)
- [ ] Can edit item details
- [ ] Can delete item
- [ ] Can link items together
- [ ] Can view item relationships
- [ ] Can assign items to users

#### Graph Visualization
- [ ] Graph loads with data
- [ ] Can zoom in/out
- [ ] Can pan around graph
- [ ] Can select nodes
- [ ] Can expand/collapse nodes
- [ ] Can filter by item type
- [ ] Layout algorithms work

#### Search Functionality
- [ ] Can search by text
- [ ] Can filter by type
- [ ] Can filter by status
- [ ] Can filter by date range
- [ ] Search results are accurate
- [ ] Search is performant (< 1s)

#### Real-Time Updates
- [ ] WebSocket connects successfully
- [ ] Updates appear in real-time
- [ ] Multiple clients stay in sync
- [ ] Handles connection drops gracefully
- [ ] Reconnects automatically

#### Import/Export
- [ ] Can export project data
- [ ] Can import project data
- [ ] Export format is valid
- [ ] Import handles errors gracefully
- [ ] Data integrity maintained

### UI/UX

#### Navigation
- [ ] All navigation links work
- [ ] Breadcrumbs are correct
- [ ] Back/forward browser buttons work
- [ ] Deep linking works
- [ ] 404 page shows for invalid routes

#### Forms
- [ ] Form validation works
- [ ] Error messages are clear
- [ ] Success messages appear
- [ ] Form submission works
- [ ] Form cancellation works
- [ ] Unsaved changes warning

#### Responsiveness
- [ ] Works on desktop (1920x1080)
- [ ] Works on laptop (1366x768)
- [ ] Works on tablet (768x1024)
- [ ] Works on mobile (375x667)
- [ ] No horizontal scrolling
- [ ] Touch targets are adequate

#### Accessibility
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Screen reader compatible
- [ ] Color contrast sufficient
- [ ] No flashing content

### Performance

#### Load Times
- [ ] Initial page load < 2s
- [ ] Subsequent navigation < 500ms
- [ ] API requests < 500ms
- [ ] Graph renders < 1s

#### Resource Usage
- [ ] Memory usage stable
- [ ] No memory leaks
- [ ] CPU usage reasonable
- [ ] Network usage optimized

### Data Integrity

#### Database
- [ ] Migrations run successfully
- [ ] Rollback works
- [ ] Foreign keys enforced
- [ ] Constraints validated
- [ ] Transactions work correctly

#### Consistency
- [ ] No orphaned records
- [ ] No duplicate data
- [ ] Timestamps accurate
- [ ] Audit logs complete

---

## Test Coverage Requirements

### Minimum Coverage by Component

| Component | Unit Test Coverage | Integration Test Coverage | E2E Test Coverage |
|-----------|-------------------|---------------------------|-------------------|
| Go API Handlers | 85% | 100% critical paths | - |
| Go Services | 80% | 80% | - |
| Go Repositories | 70% | 100% | - |
| Frontend Components | 85% | - | - |
| Frontend Hooks | 80% | - | - |
| Frontend Stores | 85% | - | - |
| Python CLI Commands | 80% | 80% | - |
| Python Services | 75% | 70% | - |
| Critical User Flows | - | - | 100% |
| Common User Flows | - | - | 80% |

### Coverage Calculation

```bash
# Go backend
go test ./internal/... -coverprofile=coverage.out
go tool cover -func=coverage.out | grep total

# Frontend
bun test --coverage
# Check coverage/lcov-report/index.html

# Python
pytest --cov=src --cov-report=term --cov-report=html
# Check htmlcov/index.html
```

---

## Test Execution Schedule

### Daily (Automated)

- [ ] Unit tests on every commit (CI)
- [ ] Linting on every commit (CI)
- [ ] Type checking on every commit (CI)

### Per Pull Request (Automated)

- [ ] Full unit test suite
- [ ] Integration tests
- [ ] E2E critical path tests
- [ ] Code coverage check
- [ ] Security scan

### Weekly (Automated)

- [ ] Full E2E test suite
- [ ] Performance benchmarks
- [ ] Accessibility audit
- [ ] Dependency updates check

### Pre-Release (Manual + Automated)

- [ ] Full regression test suite
- [ ] Load testing
- [ ] Security penetration testing
- [ ] User acceptance testing
- [ ] Documentation review

### Post-Release (Automated)

- [ ] Production smoke tests
- [ ] Performance monitoring
- [ ] Error rate monitoring
- [ ] User behavior analytics

---

## Test Result Tracking

### Test Run Documentation Template

```markdown
## Test Run: [Feature/Release Name]

**Date:** YYYY-MM-DD
**Tester:** [Name]
**Environment:** [Dev/Staging/Production]
**Build:** [Version/Commit SHA]

### Test Results Summary

| Phase | Tests Run | Passed | Failed | Skipped | Coverage |
|-------|-----------|--------|--------|---------|----------|
| Unit | 1234 | 1234 | 0 | 0 | 85% |
| Integration | 456 | 456 | 0 | 0 | - |
| E2E | 78 | 76 | 2 | 0 | - |

### Failed Tests

1. **test_name_here**
   - **Failure Reason:** [Description]
   - **Fix Required:** [Yes/No]
   - **Assigned To:** [Name]
   - **Issue:** [Link to issue]

### Performance Results

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| API p95 | < 500ms | 342ms | ✓ |
| Frontend LCP | < 2.5s | 1.8s | ✓ |

### Sign-off

- [ ] All tests passed or failures documented
- [ ] Performance meets benchmarks
- [ ] No critical issues found
- [ ] Ready for [next phase/deployment]

**Signature:** ________________
**Date:** ________________
```

---

## Continuous Improvement

### Test Review Schedule

- **Monthly:** Review test coverage and add missing tests
- **Quarterly:** Review test effectiveness and remove redundant tests
- **Per Release:** Review test failures and update test suite
- **Annually:** Complete test strategy review

### Metrics to Track

- Test execution time trends
- Test failure rate trends
- Code coverage trends
- Performance benchmark trends
- Bug escape rate (bugs found in production)

---

**End of Testing Matrix**
