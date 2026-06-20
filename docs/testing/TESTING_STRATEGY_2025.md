# TraceRTM Testing Strategy 2025

Comprehensive testing strategy based on industry best practices, full-stack SDET principles, and holistic quality engineering approaches.

## Executive Summary

TraceRTM currently maintains **706 active tests** organized across a well-structured test pyramid. This document outlines enhancements to align with 2024-2025 testing best practices, including shift-left testing, distributed quality responsibility, and holistic quality engineering beyond traditional testing.

### Current State
- ✓ 706 tests passing (100% pass rate)
- ✓ Tests organized by layer (unit, integration, E2E)
- ✓ Security tests integrated (226 tests)
- ✓ Accessibility testing implemented (97 tests)
- ✓ API mocking infrastructure (React Query + MSW)

### Target State (2025)
- Fully distributed quality responsibility across team
- Shift-left testing with early quality gates
- Holistic quality beyond testing (code review automation, monitoring, security)
- AI-powered test generation for coverage gaps
- Real-time quality metrics and transparency

---

## Part 1: Test Pyramid Analysis

### Current Test Distribution

```
         E2E Tests (21)                  ▲
              ↑                          │  SLOWER
      Integration (47)                  │  FEWER
           ↑                            │
    Unit + Hooks (638)                 │  FASTER
                                       │  MORE
                                        ▼
```

**Test Breakdown by Category:**

| Layer | Category | Count | Execution | Strategy |
|-------|----------|-------|-----------|----------|
| **Unit** | Hooks (React Query) | 244 | Fast (0.1-0.3s) | Query keys, mutations, invalidation |
| **Unit** | Store Tests (Zustand) | 92 | Fast (0.05-0.2s) | State management, persistence |
| **Unit** | Utility Tests | 41 | Fast (0.05-0.1s) | Helper functions, formatters |
| **Integration** | Component Tests | 97 | Medium (1-7s) | React Testing Library, A11y |
| **Integration** | Security Tests | 226 | Medium (0.05-0.3s) | CSP, CSRF, auth, sanitization |
| **Integration** | API Integration | 47 | Medium (0.1-0.2s) | React Query hooks, data flows |
| **E2E** | API Endpoints | 21 | Skipped | Validated via integration tests |

**Current Ratio:** 90% Unit / Integration, 10% E2E

**Recommended Ratio:** 70% Unit, 20% Integration, 10% E2E

---

## Part 2: Full-Stack SDET Model

### Distributed Quality Responsibility

Move from siloed QA to distributed responsibility across all team members:

#### Developer Responsibilities
- ✓ Implement unit tests for all functions
- ✓ Write integration tests for features
- ✓ Perform peer code reviews
- ✓ Security-aware coding practices
- ✓ Documentation updates
- □ API contract testing (NEW)
- □ Performance testing (NEW)
- □ Visual regression testing (NEW)

#### Quality Engineer Responsibilities
- ✓ Test automation framework maintenance
- ✓ CI/CD pipeline optimization
- ✓ Test data management
- ✓ Accessibility compliance verification
- □ Shift-left gate implementation (NEW)
- □ Chaos engineering baseline (NEW)
- □ Quality metrics dashboards (NEW)

#### Product/Design Responsibilities
- ✓ Requirements clarity
- ✓ User flow documentation
- □ Early accessibility reviews (NEW)
- □ Performance budgets (NEW)
- □ User acceptance testing criteria (NEW)

### Skills Matrix for Full-Stack SDET

```
Required Competencies:
├── Programming (TypeScript, JavaScript, Python)
├── Testing Frameworks (Vitest, Playwright, Jest)
├── API Testing (REST, GraphQL, OpenAPI contracts)
├── Database Testing (Schema validation, data integrity)
├── Security Testing (OWASP, CSP, auth flows)
├── Performance Testing (Lighthouse, WebPageTest)
├── CI/CD Tools (GitHub Actions, Docker)
├── Monitoring & Observability (Error tracking, logs)
└── Problem-Solving & Logical Analysis
```

---

## Part 3: Holistic Quality Approach (Beyond Testing)

### Quality Engineering Pillar 1: Design Quality
```
Activities:
├── API contract design (OpenAPI/GraphQL schema validation)
├── Database schema versioning
├── Component API consistency
├── Accessibility compliance from design phase
└── Performance budget definition
```

### Quality Engineering Pillar 2: Code Quality
```
Activities:
├── Code review automation (semantic analysis)
├── Static analysis (ESLint, TypeScript strict mode)
├── Dependency vulnerability scanning
├── Code complexity analysis (cyclomatic complexity)
├── Type safety enforcement
└── Security policy enforcement
```

### Quality Engineering Pillar 3: Testing & Verification
```
Activities:
├── Unit testing (100% critical paths)
├── Integration testing (component contracts)
├── End-to-end testing (user critical flows)
├── Security testing (OWASP coverage)
├── Accessibility testing (WCAG compliance)
├── Performance testing (lighthouse, metrics)
├── Visual regression testing (screenshot comparison)
└── Contract testing (API contracts)
```

### Quality Engineering Pillar 4: Production Quality
```
Activities:
├── Error tracking & alerting (Sentry, DataDog)
├── Performance monitoring (real user metrics)
├── Security monitoring (intrusion detection)
├── Accessibility monitoring (real user experiences)
├── Business metric monitoring (conversion funnels)
├── Log aggregation & analysis
├── Chaos engineering (resilience testing)
└── User feedback loops
```

### Quality Engineering Pillar 5: Process Quality
```
Activities:
├── Shift-left quality gates (pre-commit hooks)
├── Automated code review workflows
├── Test coverage enforcement
├── Performance regression detection
├── Security policy automation
├── Documentation currency checks
└── Knowledge sharing & continuous learning
```

---

## Part 4: Shift-Left Testing Strategy

Move quality checks as early as possible in development:

### Pre-Commit Hooks
```bash
./rtm check              # Pre-commit checks
├── Lint (ESLint, Biome)
├── Type check (TypeScript)
├── Format check
├── Security scan (basic)
├── Spell check (comments/docs)
└── Test affected files
```

### Branch Validation
```bash
./rtm test:branch        # On branch creation
├── All unit tests
├── Type checking
├── Lint checking
├── Security tests
└── Accessibility tests
```

### PR Validation
```bash
./rtm test:pr            # On PR creation
├── All tests from branch
├── Performance comparison (vs main)
├── Coverage enforcement (>80%)
├── Security scanning (SAST, dependency)
├── Accessibility compliance
├── API contract validation
└── Visual regression (if UI changed)
```

### Merge Validation
```bash
./rtm test:merge         # Before merge to main
├── Full test suite
├── Chaos engineering baseline
├── Production readiness checks
├── Documentation completeness
└── Security sign-off
```

---

## Part 5: Recommended Enhancements

### High Priority (Next Sprint)
- [ ] Add pre-commit hooks for lint/type/basic tests
- [ ] Implement GitHub branch protection rules with quality gates
- [ ] Create performance baseline testing (Lighthouse, Core Web Vitals)
- [ ] Add visual regression testing (Percy or similar)
- [ ] Implement error tracking setup (Sentry)

### Medium Priority (Next Quarter)
- [ ] Contract testing for API endpoints
- [ ] Chaos engineering baseline scenarios
- [ ] API performance testing (response times, throughput)
- [ ] Real user monitoring (RUM) integration
- [ ] Automated security scanning in CI/CD

### Low Priority (Next 6 Months)
- [ ] AI-powered test generation for coverage gaps
- [ ] Advanced analytics dashboard
- [ ] Cross-browser testing automation (BrowserStack)
- [ ] Load testing baseline
- [ ] Accessibility monitoring in production

---

## Part 6: Implementation Roadmap

### Month 1: Foundation (Shift-Left)
```
Week 1-2: Setup quality gates
  └── Pre-commit hooks (lint, type, format)
  └── Branch protection rules

Week 2-3: Early testing
  └── GitHub Actions workflows for PR checks
  └── Coverage enforcement

Week 3-4: Baseline metrics
  └── Performance baseline (Lighthouse)
  └── Error tracking setup (Sentry)
```

### Month 2: Expansion (Holistic Quality)
```
Week 1-2: Visual regression
  └── Percy or similar integration
  └── Screenshot baselines

Week 2-3: Contract testing
  └── OpenAPI contract validation
  └── API integration tests

Week 3-4: Advanced testing
  └── Performance testing (API benchmarks)
  └── Security scanning (SAST, dependencies)
```

### Month 3: Maturity (Observability)
```
Week 1-2: Production monitoring
  └── Real User Monitoring (RUM)
  └── Error tracking dashboards

Week 2-3: Chaos engineering
  └── Resilience testing baseline
  └── Failure scenario testing

Week 3-4: Analytics & Improvement
  └── Quality metrics dashboard
  └── Continuous improvement process
```

---

## Part 7: Testing Best Practices by Layer

### Unit Tests (Base Layer)
```typescript
// ✓ DO: Test pure functions and isolated logic
describe('calculateProgress', () => {
  it('should calculate percentage of completed items', () => {
    const items = [
      { status: 'done' },
      { status: 'done' },
      { status: 'pending' }
    ]
    expect(calculateProgress(items)).toBe(66.67)
  })
})

// ✗ DON'T: Mock everything and test implementation
describe('calculateProgress', () => {
  it('should call .filter() and .length', () => {
    // Testing implementation details is brittle
  })
})
```

### Integration Tests (Middle Layer)
```typescript
// ✓ DO: Test feature workflows and component interactions
describe('Item Creation Flow', () => {
  it('should create item and update store', async () => {
    const { result } = renderHook(() => useCreateItem())
    await act(async () => {
      result.current.mutate({ title: 'New Item' })
    })
    expect(result.current.isSuccess).toBe(true)
    expect(itemsStore.getState().items).toHaveLength(1)
  })
})

// ✗ DON'T: Test each layer in isolation without real interactions
describe('createItem', () => {
  it('should call API endpoint', () => {
    // Testing that network request was made without real flow
  })
})
```

### E2E Tests (Top Layer)
```typescript
// ✓ DO: Test critical user journeys from start to finish
test('user can create and view item', async ({ page }) => {
  await page.goto('/')
  await page.click('[data-test="create-item"]')
  await page.fill('[data-test="item-title"]', 'My Item')
  await page.click('[data-test="submit"]')
  await expect(page.locator('text=My Item')).toBeVisible()
})

// ✗ DON'T: Test every possible interaction
test('all form validation rules', async ({ page }) => {
  // Testing every edge case belongs in integration tests
})
```

---

## Part 8: Quality Metrics to Track

### Code Quality Metrics
- **Test Coverage:** Target 80%+ for source code
- **Type Safety:** 0% `any` types in production code
- **Complexity:** Max cyclomatic complexity 10 per function
- **Duplication:** <5% code duplication
- **Security Issues:** 0 high/critical vulnerabilities

### Testing Metrics
- **Pass Rate:** 100% (0 flaky tests)
- **Test Execution Speed:** <30 seconds for full suite
- **Test Distribution:** 70/20/10 (unit/integration/E2E)
- **Coverage Trend:** >80% maintained/improved
- **Regression Rate:** <2% of PRs cause regressions

### Performance Metrics
- **Lighthouse Score:** >90 (performance)
- **Core Web Vitals:** LCP <2.5s, FID <100ms, CLS <0.1
- **API Response Time:** p95 <200ms
- **Bundle Size:** <100KB gzipped for main app
- **Test Execution:** <1min full suite, <5s affected tests

### Production Quality Metrics
- **Error Rate:** <0.1% of requests
- **Uptime:** >99.9%
- **MTTR:** <30 minutes for critical issues
- **Accessibility Score:** >95 (axe-core)
- **Security Score:** A+ (Mozilla Observatory)

---

## Part 9: Tools & Infrastructure

### Current Stack
- **Test Runner:** Vitest 4.0.14+
- **Browser Testing:** Playwright
- **API Mocking:** MSW (Mock Service Worker)
- **Component Testing:** React Testing Library
- **Accessibility:** jest-axe
- **State Management:** Zustand
- **HTTP Client:** openapi-fetch (typed API)

### Recommended Additions

| Purpose | Tool | Priority | Effort |
|---------|------|----------|--------|
| Performance Testing | Lighthouse CI | High | Low |
| Visual Regression | Percy or BackstopJS | High | Medium |
| Error Tracking | Sentry | High | Low |
| API Contract Testing | Pact or Swagger Contract | Medium | Medium |
| Chaos Engineering | Chaos Toolkit | Medium | High |
| Real User Monitoring | Vercel Analytics or Mixpanel | Medium | Low |
| Security Scanning | Snyk or Dependabot | High | Low |
| Code Coverage | CodeCov or Codecov | High | Low |
| PR Automation | Renovate | Medium | Low |
| Performance Monitoring | WebPageTest | Low | Medium |

---

## Part 10: Documentation & Knowledge Sharing

### Create These Documents
- [ ] **API Contract Specification** - OpenAPI schema with examples
- [ ] **Test Design Guide** - When to write which test type
- [ ] **Performance Budget** - Target metrics for each page
- [ ] **Security Checklist** - Pre-deployment security review
- [ ] **Accessibility Guidelines** - WCAG compliance checklist
- [ ] **CI/CD Pipeline Guide** - How quality gates work
- [ ] **Troubleshooting Guide** - Common test failures and fixes

### Regular Knowledge Sharing
- Weekly test review meetings (30 min)
- Monthly quality metrics review
- Quarterly retrospectives on testing effectiveness
- Internal knowledge base for test patterns
- Open discussion on quality challenges

---

## Part 11: Success Criteria

### Month 1 (Shift-Left Foundation)
- [ ] Pre-commit hooks prevent >90% of lint/type errors
- [ ] PR validation runs in <2 minutes
- [ ] Coverage stays >80% on all PRs
- [ ] 0 regressions from main branch

### Month 2 (Expanded Coverage)
- [ ] Visual regression testing integrated
- [ ] API performance baseline established
- [ ] Security scanning catches all known vulnerability patterns
- [ ] Team reports improved confidence in code changes

### Month 3 (Production Observability)
- [ ] Production error tracking operational
- [ ] Chaos engineering baseline defined
- [ ] Quality metrics dashboard live
- [ ] <1% production incidents from code changes

### Ongoing (Continuous Improvement)
- [ ] Test execution time remains <30s
- [ ] Coverage maintained at >80%
- [ ] 100% test pass rate maintained
- [ ] Team velocity increases (fewer production bugs)

---

## Part 12: References & Further Reading

### Industry Standards
- [The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html) - Martin Fowler
- [Test Automation Pyramid Guide](https://www.leapwork.com/blog/testing-pyramid) - LeapWork
- [Full-Stack SDET Role](https://blogs.halodoc.io/full-stack-sdet/) - HaloDOC Engineering
- [Modern Test Pyramid 2025](https://fullscale.io/blog/modern-test-pyramid-guide/) - FullScale

### Testing Frameworks
- [Vitest Documentation](https://vitest.dev/)
- [Playwright Testing](https://playwright.dev/)
- [React Testing Library](https://testing-library.com/)
- [Mock Service Worker](https://mswjs.io/)

### Quality Engineering Resources
- [Shift-Left Testing Approach](https://myridius.com/blog/getting-your-shift-on-a-holistic-approach-to-shift-left-quality-assurance-software-testing)
- [Holistic QA Practices](https://www.vuonogroup.com/blog/holistic-quality-assurance-practices-for-software-development)
- [Software Quality Pyramid](https://medium.com/@ss-tech/redefining-software-quality-a-holistic-approach-with-the-software-quality-pyramid-bf470565d168)

---

## Appendix: Quick Reference

### Run Tests by Category
```bash
./rtm test              # All tests
./rtm test:unit        # Unit only
./rtm test:integration # Integration only
./rtm test:e2e         # E2E only
./rtm test:security    # Security tests
./rtm test:a11y        # Accessibility tests
./rtm test:watch       # Watch mode
./rtm test:ui          # Visual dashboard
```

### Quality Gates
```bash
./rtm check            # Pre-commit validation
./rtm test:branch      # Branch validation
./rtm test:pr          # PR validation
./rtm test:merge       # Merge validation
```

### Metrics & Reporting
```bash
./rtm test:coverage    # Coverage report
./rtm health           # System health check
./rtm info             # Project information
```

---

## Part 13: Test-Driven Development (TDD) & Behavior-Driven Development (BDD)

### TDD: Red-Green-Refactor Cycle

**TDD Methodology** ([Katalon Reference](https://katalon.com/resources-center/blog/tdd-vs-bdd)):

```
Red Phase    → Write failing test first
   ↓
Green Phase  → Write minimal code to pass test
   ↓
Refactor     → Improve code while maintaining passing tests
   ↓
Repeat       → Move to next feature/behavior
```

#### TDD Best Practices

1. **Start Small**
   - Focus on one behavior at a time
   - Write one failing test per iteration
   - Implement only what's needed to pass

2. **Test Naming**
   ```go
   // ✓ Good: describes the behavior
   func TestCalculateTotalReturnsZeroForEmptyCart(t *testing.T)

   // ✗ Poor: unclear what's being tested
   func TestCalculate(t *testing.T)
   ```

3. **Test Independence**
   - Each test should be executable independently
   - No shared state between tests
   - Setup and teardown for each test

4. **Assertions Should Be Explicit**
   ```go
   // ✓ Clear assertion
   assert.Equal(t, 100, total, "total should be 100 for items worth $100")

   // ✗ Implicit assertion
   if total != 100 {
       t.Fail()
   }
   ```

#### TDD Workflow for TraceRTM

```
1. Write Feature Test (Integration)
   └─ Defines user-visible behavior

2. Write Unit Tests (Red)
   └─ Specific implementation tests fail initially

3. Implement Feature (Green)
   └─ Write code to make tests pass

4. Refactor (Optimize)
   └─ Improve code quality and performance

5. Security Review
   └─ Verify no new vulnerabilities introduced

6. Accessibility Check
   └─ Ensure feature is usable by all users
```

### BDD: Behavior-Driven Development

**BDD Methodology** ([Cucumber Reference](https://cucumber.io/blog/bdd/bdd-vs-tdd/)):

BDD bridges the gap between developers, testers, and business stakeholders using **Gherkin syntax** with Given-When-Then statements.

#### Gherkin Syntax

```gherkin
Feature: Item Creation
  As a user
  I want to create new items
  So that I can track my work

  Scenario: Create item with valid title
    Given I am on the items page
    When I enter "Complete project report" as the title
    And I click the Create button
    Then a new item should appear with title "Complete project report"
    And the item status should be "pending"

  Scenario: Create item with empty title
    Given I am on the items page
    When I enter "" as the title
    And I click the Create button
    Then an error message should appear
    And no new item should be created
```

#### BDD Best Practices

1. **Declarative over Imperative** ([Cucumber Guide](https://cucumber.io/docs/bdd/better-gherkin/))
   ```gherkin
   # ✓ Declarative: describes WHAT not HOW
   When I create an item with title "Review design"

   # ✗ Imperative: over-specifies HOW
   When I click the input field at coordinates 123, 456
   And I type "Review design" one character at a time
   And I click the button with id "create-btn"
   ```

2. **Reusable Step Definitions**
   ```typescript
   // Single step definition for multiple scenarios
   Given('I have {int} items', (count: number) => {
     // reusable for count=1, count=5, count=10, etc.
   })
   ```

3. **Proper Organization**
   ```
   features/
   ├── items/
   │   ├── create-item.feature
   │   ├── update-item.feature
   │   └── delete-item.feature
   ├── projects/
   │   └── project-management.feature
   └── step-definitions/
       ├── items.steps.ts
       └── projects.steps.ts
   ```

4. **Collaborative Requirements**
   - Three Amigos: Developer, Tester, Product Owner
   - Define acceptance criteria during planning
   - Use scenarios as living documentation
   - Update scenarios when behavior changes

#### Combining TDD + BDD

```
BDD (High Level)        TDD (Low Level)
Feature Scenarios    ←→  Unit Tests
User Journey         ←→  Component Logic
Business Rules       ←→  Function Behavior
Acceptance Criteria  ←→  Implementation Details
```

**Implementation Sequence for TraceRTM:**

1. Product writes scenario (BDD)
2. Developer breaks into unit tests (TDD)
3. Developer implements code (Red → Green → Refactor)
4. QA verifies scenario passes (BDD validation)
5. Iterate on feedback

---

## Part 14: Language-Specific Testing Guide

### TypeScript/JavaScript Testing

**Primary Stack for Frontend:**
- **Test Runner:** Vitest 4.0.14+ ([Vitest Documentation](https://vitest.dev/))
- **Component Testing:** React Testing Library ([RTL Guide](https://testing-library.com/))
- **E2E Testing:** Playwright ([Playwright Docs](https://playwright.dev/))
- **API Mocking:** MSW (Mock Service Worker) ([MSW Documentation](https://mswjs.io/))
- **Accessibility:** jest-axe ([jest-axe](https://github.com/nickcolley/jest-axe))

**Test Structure:**

```typescript
// Unit Test Example
import { describe, it, expect } from 'vitest'
import { calculateProgress } from './helpers'

describe('calculateProgress', () => {
  it('should calculate percentage of completed items', () => {
    const items = [
      { status: 'done' },
      { status: 'done' },
      { status: 'pending' }
    ]
    const result = calculateProgress(items)
    expect(result).toBe(66.67)
  })

  it('should return 0 for empty array', () => {
    expect(calculateProgress([])).toBe(0)
  })
})
```

### Go Testing

**Backend Testing Frameworks** ([Go Wiki: TableDrivenTests](https://go.dev/wiki/TableDrivenTests)):

- **Testing:** Built-in `testing` package
- **Assertions:** Testify (stretchr/testify) ([Testify GitHub](https://github.com/stretchr/testify))
- **Mocking:** GoMock ([GoMock](https://github.com/golang/mock))
- **HTTP Testing:** `httptest` (standard library)
- **BDD:** Godog ([Godog GitHub](https://github.com/cucumber/godog))

**Table-Driven Tests (Go Standard):**

```go
// Table-driven testing pattern
func TestCalculateProgress(t *testing.T) {
  tests := []struct {
    name    string
    items   []Item
    want    float64
    wantErr bool
  }{
    {
      name: "calculate_percentage_correctly",
      items: []Item{
        {Status: "done"},
        {Status: "done"},
        {Status: "pending"},
      },
      want:    66.67,
      wantErr: false,
    },
    {
      name:    "return_zero_for_empty_list",
      items:   []Item{},
      want:    0,
      wantErr: false,
    },
    {
      name:    "error_for_nil_items",
      items:   nil,
      want:    0,
      wantErr: true,
    },
  }

  for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
      got, err := calculateProgress(tt.items)
      if (err != nil) != tt.wantErr {
        t.Errorf("calculateProgress() error = %v, wantErr %v", err, tt.wantErr)
        return
      }
      if got != tt.want {
        t.Errorf("calculateProgress() got = %v, want %v", got, tt.want)
      }
    })
  }
}
```

**Go HTTP Testing:**

```go
func TestItemHandler(t *testing.T) {
  // Setup
  handler := http.HandlerFunc(GetItems)

  // Create test request
  req := httptest.NewRequest("GET", "/api/v1/items", nil)
  w := httptest.NewRecorder()

  // Execute
  handler.ServeHTTP(w, req)

  // Assert
  assert.Equal(t, http.StatusOK, w.Code)
  assert.Contains(t, w.Body.String(), "items")
}
```

**Go Mocking with GoMock:**

```go
// Generate mocks from interfaces
//go:generate mockgen -destination=mocks/mock_item_repo.go -package=mocks . ItemRepository

func TestCreateItem(t *testing.T) {
  ctrl := gomock.NewController(t)
  defer ctrl.Finish()

  // Create mock
  mockRepo := mocks.NewMockItemRepository(ctrl)

  // Set expectations
  mockRepo.EXPECT().
    Save(gomock.Any()).
    Return(nil).
    Times(1)

  // Test
  service := NewItemService(mockRepo)
  err := service.CreateItem(context.Background(), item)

  assert.NoError(t, err)
}
```

**Go BDD with Godog** ([Godog Guide](https://github.com/cucumber/godog)):

```gherkin
# features/items.feature
Feature: Item Management
  Scenario: Create a new item
    Given I have no items
    When I create an item with title "Fix bug"
    Then the item should be created
    And I should have 1 item
```

```go
// steps.go
func iHaveNoItems() error {
  items = []Item{}
  return nil
}

func iCreateAnItemWithTitle(title string) error {
  item := Item{
    Title:  title,
    Status: "pending",
  }
  items = append(items, item)
  return nil
}

func theItemShouldBeCreated() error {
  if len(items) == 0 {
    return fmt.Errorf("no items created")
  }
  return nil
}
```

### Python Testing

**Testing Frameworks** ([Python Testing Best Practices](https://www.browserstack.com/guide/top-python-testing-frameworks)):

- **Test Framework:** pytest ([pytest Documentation](https://docs.pytest.org/))
- **BDD:** Behave ([Behave Documentation](https://behave.readthedocs.io/))
- **BDD Alternative:** pytest-bdd ([pytest-bdd](https://pypi.org/project/pytest-bdd/))
- **Mocking:** unittest.mock (standard library)
- **Testing Utilities:** pytest-asyncio (for async code)

**pytest Unit Tests:**

```python
# test_helpers.py
import pytest
from helpers import calculate_progress

class TestCalculateProgress:
    def test_calculate_percentage_correctly(self):
        items = [
            {"status": "done"},
            {"status": "done"},
            {"status": "pending"},
        ]
        result = calculate_progress(items)
        assert result == 66.67

    def test_return_zero_for_empty_list(self):
        assert calculate_progress([]) == 0

    @pytest.mark.parametrize("items,expected", [
        ([{"status": "done"}], 100),
        ([{"status": "pending"}], 0),
        ([{"status": "done"}, {"status": "pending"}], 50),
    ])
    def test_various_counts(self, items, expected):
        assert calculate_progress(items) == expected
```

**Python BDD with Behave** ([Behave Guide](https://behave.readthedocs.io/)):

```gherkin
# features/items.feature
Feature: Item Management
  Scenario: Create a new item
    Given I have no items
    When I create an item with title "Fix bug"
    Then the item should be created
    And I should have 1 item
```

```python
# features/steps/items.py
from behave import given, when, then

@given('I have no items')
def step_no_items(context):
    context.items = []

@when('I create an item with title "{title}"')
def step_create_item(context, title):
    item = {"title": title, "status": "pending"}
    context.items.append(item)

@then('the item should be created')
def step_verify_created(context):
    assert len(context.items) > 0

@then('I should have {count} item')
def step_count_items(context, count):
    assert len(context.items) == int(count)
```

**Python Async Testing:**

```python
import pytest
import pytest_asyncio

@pytest_asyncio.fixture
async def db():
    # Setup async database
    yield db
    # Cleanup

@pytest.mark.asyncio
async def test_fetch_item(db):
    item = await db.fetch_item(1)
    assert item is not None
    assert item.title == "Expected Title"
```

### Rust Testing (If Applicable)

**Testing Features** ([Rust Testing Guide](https://doc.rust-lang.org/book/ch11-03-test-organization.html)):

- **Unit Tests:** Inline in modules
- **Integration Tests:** Separate `tests/` directory
- **Documentation Tests:** In doc comments
- **Benchmarks:** Built-in `#[bench]` attribute

**Rust Unit Tests:**

```rust
#[cfg(test)]
mod tests {
  use super::*;

  #[test]
  fn test_calculate_progress_correctly() {
    let items = vec![
      Item { status: "done".to_string() },
      Item { status: "done".to_string() },
      Item { status: "pending".to_string() },
    ];

    let result = calculate_progress(&items);
    assert_eq!(result, 66.67);
  }

  #[test]
  fn test_empty_list_returns_zero() {
    let items = vec![];
    assert_eq!(calculate_progress(&items), 0.0);
  }
}
```

**Rust Integration Tests:**

```rust
// tests/integration_test.rs
use myapp::calculate_progress;

#[test]
fn test_api_endpoint() {
  // Tests public API only
  let items = vec![/* ... */];
  let result = calculate_progress(&items);
  assert!(result >= 0.0 && result <= 100.0);
}
```

**Rust Benchmarks:**

```rust
#![feature(test)]
extern crate test;

#[cfg(test)]
mod bench {
  use super::*;
  use test::Bencher;

  #[bench]
  fn bench_calculate_progress(b: &mut Bencher) {
    let items = vec![/* large dataset */];
    b.iter(|| calculate_progress(&items));
  }
}
```

---

## Part 15: Contract Testing Strategy

### What is Contract Testing?

Contract testing validates communication agreements between services without requiring both services to be running. [API Contract Testing Guide](https://redocly.com/learn/testing/contract-testing-101/)

### Consumer-Driven Contracts (CDC)

```
Consumer                    Provider
  ├─ Generates contract ──→ (Agreement)
  └─ Verifies locally       Provider verifies contract
```

**Benefits:**
- Early detection of breaking changes
- Reduced E2E test dependencies
- Faster feedback loops
- Better documentation of API contracts

### Implementation with Pact

**Pact Framework** ([Pact Documentation](https://pact.foundation/)):

Works across: Go, TypeScript/JavaScript, Python, Rust, Java, etc.

**Consumer Side (Frontend):**

```typescript
import { pact } from '@pact-foundation/pact'

describe('Item API Contract', () => {
  const provider = new Pact({
    consumer: 'TraceRTM Web',
    provider: 'TraceRTM API',
  })

  it('should fetch items', async () => {
    // Define contract
    await provider.addInteraction({
      state: 'items exist',
      uponReceiving: 'a request for items',
      withRequest: {
        method: 'GET',
        path: '/api/v1/items',
      },
      willRespondWith: {
        status: 200,
        body: Matchers.eachLike({
          id: Matchers.uuid(),
          title: Matchers.string('Fix bug'),
          status: Matchers.term({
            matcher: 'pending|done|in_progress',
            value: 'pending',
          }),
        }),
      },
    })

    // Test contract
    const items = await fetchItems()
    expect(items).toHaveLength(1)
    expect(items[0]).toHaveProperty('id')
    expect(items[0]).toHaveProperty('title')
  })
})
```

**Provider Side (Backend - Go):**

```go
import "github.com/pact-foundation/pact-go/v2/verifier"

func TestItemProviderContract(t *testing.T) {
  opts := verifier.VerifyRequest{
    ProviderBaseURL:  "http://localhost:8000",
    PactFiles:        []string{"./pacts/tracertm_web-tracertm_api.json"},
    ProviderVersion:  "1.0.0",
  }

  _, err := verifier.NewVerifier().Verify(opts)
  if err != nil {
    t.Error(err)
  }
}
```

### OpenAPI Contract Testing

```bash
# Validate API spec
npx swagger-cli validate openapi.yaml

# Generate contract tests
npx openapi-mock-generator openapi.yaml
```

### Contract Testing Workflow

```
1. Consumer writes contract (what it expects)
   ↓
2. Consumer tests contract locally (mocked provider)
   ↓
3. Provider implements according to contract
   ↓
4. Provider tests contract (real implementation)
   ↓
5. Contract published to broker
   ↓
6. Can-I-Deploy check (no breaking changes)
   ↓
7. Deploy with confidence
```

---

## Part 16: Polyglot Microservices Testing

### Multi-Language Testing Strategy

TraceRTM's architecture spans multiple languages:
- **Frontend:** TypeScript/React
- **Backend:** Go
- **Data Layer:** Python (optional analytics)
- **Infrastructure:** Bash/YAML

### Unified Testing Approach

#### 1. Layer-Based Testing

```
API Contracts (Pact)
        ↓
Service Tests (Language-Specific)
        ├─ Go: httptest + Testify
        ├─ TypeScript: Vitest
        └─ Python: pytest
        ↓
Integration Tests (Docker Compose)
        ├─ Services running together
        └─ Real network communication
        ↓
E2E Tests (Playwright)
        └─ User perspective across all services
```

#### 2. Contract Testing Bridge

```
TypeScript      Go          Python
  ├─ HTTP    ←─────────→   REST API
  └─ gRPC    ←─────────→   Protocol Buffer
             ↓
        Pact Contracts
        (Language Agnostic)
```

#### 3. Docker Compose for Integration Testing

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgres://db/testdb

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: testdb

  redis:
    image: redis:7-alpine

  app:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api
```

```bash
# Run all services and tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

#### 4. Cross-Language Test Coordination

```bash
#!/bin/bash
# scripts/test-all.sh

set -e

echo "🧪 Testing TypeScript Frontend..."
cd frontend && bun run test && cd ..

echo "🧪 Testing Go Backend..."
cd backend && go test ./... && cd ..

echo "🧪 Testing Python (if exists)..."
if [ -d "analytics" ]; then
  cd analytics && pytest && cd ..
fi

echo "🧪 Testing Contracts (Pact)..."
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

echo "🧪 Testing E2E..."
cd frontend && bun run test:e2e && cd ..

echo "✅ All tests passed!"
```

#### 5. Shared Test Data Strategy

```
test-fixtures/
├── items.json         # Shared test data across languages
├── projects.json
├── users.json
└── seeds.sql          # Database initialization

# Python can load
import json
with open('test-fixtures/items.json') as f:
    test_items = json.load(f)

# Go can load
var testItems []Item
data, _ := os.ReadFile("test-fixtures/items.json")
json.Unmarshal(data, &testItems)

# TypeScript can load
import testItems from './test-fixtures/items.json'
```

#### 6. Standardized Logging & Metrics

```
All services log to stdout with standard format:
[timestamp] [service] [level] message

Example:
[2025-12-02T10:30:45.123Z] [api] [INFO] Created item: item-123
[2025-12-02T10:30:46.456Z] [web] [DEBUG] Fetching items from API
```

---

## Part 17: Extended References & Framework Comparison

### Go Testing Resources
- [Go Wiki: Table-Driven Tests](https://go.dev/wiki/TableDrivenTests) - Official Go documentation
- [Testify GitHub](https://github.com/stretchr/testify) - Assertions and mocks
- [GoMock](https://github.com/golang/mock) - Mock code generator
- [Godog](https://github.com/cucumber/godog) - Cucumber for Go
- [httptest Package](https://pkg.go.dev/net/http/httptest) - HTTP testing

### Python Testing Resources
- [pytest Documentation](https://docs.pytest.org/)
- [Top Python Testing Frameworks](https://www.browserstack.com/guide/top-python-testing-frameworks)
- [Behave Documentation](https://behave.readthedocs.io/)
- [pytest-bdd](https://pypi.org/project/pytest-bdd/)

### TypeScript/JavaScript Resources
- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/)
- [Playwright Testing](https://playwright.dev/)
- [Mock Service Worker](https://mswjs.io/)

### Rust Testing Resources
- [Rust Testing - Official Book](https://doc.rust-lang.org/book/ch11-03-test-organization.html)
- [Rust Unit and Integration Testing](https://blog.jetbrains.com/rust/2024/04/02/rust-unit-and-integration-testing-in-rustrover/)

### BDD & TDD Resources
- [TDD vs BDD Comparison](https://katalon.com/resources-center/blog/tdd-vs-bdd)
- [Cucumber BDD Guide](https://cucumber.io/blog/bdd/bdd-vs-tdd/)
- [Better Gherkin Syntax](https://cucumber.io/docs/bdd/better-gherkin/)

### Contract Testing Resources
- [Pact Foundation](https://pact.foundation/)
- [API Contract Testing Guide](https://redocly.com/learn/testing/contract-testing-101/)
- [Contract Testing for GraphQL](https://pactflow.io/blog/contract-testing-for-graphql/)

### Polyglot Testing Resources
- [Testing Polyglot Ecosystems](https://www.slideshare.net/DavidWorth5/integration-testing-for-polyglot-ecosystems)
- [Polyglot Microservices](https://www.javapedia.net/Microservices/2933)
- [AWS Polyglot Application Testing](https://aws.amazon.com/blogs/devops/building-and-testing-polyglot-applications-using-aws-codebuild/)

### Framework Comparison Table

| Aspect | Go | Python | TypeScript | Rust |
|--------|----|---------|-----------|----|
| **Unit Testing** | `testing` pkg | pytest | Vitest | `#[test]` |
| **Mocking** | GoMock | unittest.mock | Vitest mocks | Doesn't need mocks |
| **BDD** | Godog | Behave | Cucumber.js | N/A |
| **Assertions** | Testify | pytest | Vitest matchers | assert! macro |
| **Performance** | Fast | Medium | Very Fast | Fastest |
| **Learning Curve** | Easy | Easy | Easy | Moderate |
| **Community** | Large | Very Large | Very Large | Growing |

---

**Document Version:** 2.0 (Extended with Language-Specific & Polyglot Testing)
**Last Updated:** December 2024
**Next Review:** March 2025
