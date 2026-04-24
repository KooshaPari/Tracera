# Test Configuration - Mock vs Live (COMPREHENSIVE)

**Date**: 2025-11-22  
**Version**: 1.0 (TEST CONFIGURATION)  
**Status**: APPROVED

---

## 🧪 **TEST CONFIGURATION MATRIX**

### Environment Variables

```bash
# .env.test.mock
TEST_MODE=mock
API_URL=http://localhost:3000
DATABASE_URL=mock://memory
REALTIME_URL=mock://memory
SEARCH_URL=mock://memory
AUTH_URL=mock://memory
STORAGE_URL=mock://memory

# .env.test.live
TEST_MODE=live
API_URL=http://localhost:8000
DATABASE_URL=postgresql://test:test@localhost:5432/trace_test
REALTIME_URL=ws://localhost:8000/realtime
SEARCH_URL=http://localhost:9200
AUTH_URL=http://localhost:3000/auth
STORAGE_URL=http://localhost:9000

# .env.test.hybrid
TEST_MODE=hybrid
API_URL=http://localhost:8000
DATABASE_URL=postgresql://test:test@localhost:5432/trace_test
REALTIME_URL=mock://memory
SEARCH_URL=mock://memory
AUTH_URL=http://localhost:3000/auth
STORAGE_URL=mock://memory
```

---

## 🎯 **TEST EXECUTION STRATEGIES**

### Strategy 1: Development (Fast Feedback)

```bash
# Run mock tests only (< 20 seconds)
npm run test:mock

# Configuration
TEST_MODE=mock
MOCK_API=true
MOCK_DATABASE=true
MOCK_REALTIME=true
MOCK_SEARCH=true
MOCK_STORAGE=true

# Tests Run
- Unit Tests (Mock-Mock): 200+ tests
- Integration Tests (Mock-Mock): 100+ tests
- E2E Tests (Mock): 30+ tests
- Total: 330+ tests in < 20 seconds
```

### Strategy 2: Pre-Commit (Comprehensive)

```bash
# Run all tests (< 30 minutes)
npm run test

# Configuration
TEST_MODE=hybrid
MOCK_API=false
MOCK_DATABASE=false
MOCK_REALTIME=true
MOCK_SEARCH=true
MOCK_STORAGE=true

# Tests Run
- Unit Tests (All variations): 500+ tests
- Integration Tests (All variations): 300+ tests
- E2E Tests (Hybrid): 50+ tests
- Total: 850+ tests in < 30 minutes
```

### Strategy 3: CI/CD (Full Coverage)

```bash
# Run full test suite (< 45 minutes)
npm run test:ci

# Configuration
TEST_MODE=live
MOCK_API=false
MOCK_DATABASE=false
MOCK_REALTIME=false
MOCK_SEARCH=false
MOCK_STORAGE=false

# Tests Run
- Unit Tests (All variations): 500+ tests
- Integration Tests (All variations): 300+ tests
- E2E Tests (Live): 100+ tests
- Performance Tests: 50+ tests
- Security Tests: 30+ tests
- Accessibility Tests: 20+ tests
- Total: 1,000+ tests in < 45 minutes
```

---

## 📊 **TEST CONFIGURATION BY TYPE**

### Unit Tests Configuration

```typescript
// vitest.config.unit.ts

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup/unit.setup.ts'],
    include: ['tests/frontend/**/*.test.tsx', 'tests/backend/**/*.test.ts'],
    exclude: ['tests/e2e/**'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'tests/'],
      lines: 85,
      functions: 85,
      branches: 80,
      statements: 85,
    },
  },
});
```

### Integration Tests Configuration

```typescript
// vitest.config.integration.ts

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./tests/setup/integration.setup.ts'],
    include: ['tests/backend/api/**/*.test.ts'],
    exclude: ['tests/e2e/**'],
    testTimeout: 30000,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      lines: 90,
      functions: 90,
      branches: 85,
      statements: 90,
    },
  },
});
```

### E2E Tests Configuration

```typescript
// playwright.config.ts

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## 🔧 **MOCK CONFIGURATION**

### Frontend Mock Configuration

```typescript
// tests/setup/unit.setup.ts

import { setupMocks, teardownMocks } from './frontend-mocks';
import { vi } from 'vitest';

beforeEach(() => {
  setupMocks();
});

afterEach(() => {
  teardownMocks();
});

// Mock fetch
global.fetch = vi.fn();

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock as any;

// Mock WebSocket
global.WebSocket = vi.fn() as any;
```

### Backend Mock Configuration

```go
// tests/setup/setup.go

package tests

import (
	"testing"
	"github.com/stretchr/testify/suite"
)

type MockTestSuite struct {
	suite.Suite
	mockDB       *mocks.MockDatabase
	mockSearch   *mocks.MockSearchService
	mockRealtime *mocks.MockRealtimeService
}

func (suite *MockTestSuite) SetupTest() {
	suite.mockDB = &mocks.MockDatabase{}
	suite.mockSearch = &mocks.MockSearchService{}
	suite.mockRealtime = &mocks.MockRealtimeService{}
}

func (suite *MockTestSuite) TearDownTest() {
	suite.mockDB.AssertExpectations(suite.T())
	suite.mockSearch.AssertExpectations(suite.T())
	suite.mockRealtime.AssertExpectations(suite.T())
}
```

---

## 🚀 **TEST EXECUTION COMMANDS**

### Development Commands

```bash
# Run mock tests (fast)
npm run test:mock

# Run mock tests in watch mode
npm run test:mock:watch

# Run specific test file
npm run test:mock -- tests/frontend/features/FR-1.1-CreateItem.mock-mock.test.tsx

# Run tests matching pattern
npm run test:mock -- --grep "FR-1.1"
```

### Pre-Commit Commands

```bash
# Run all tests
npm run test

# Run all tests with coverage
npm run test:coverage

# Run tests in parallel
npm run test:parallel

# Run tests with verbose output
npm run test:verbose
```

### CI/CD Commands

```bash
# Run full test suite
npm run test:ci

# Run full test suite with coverage
npm run test:ci:coverage

# Run performance tests
npm run test:performance

# Run security tests
npm run test:security

# Run accessibility tests
npm run test:a11y
```

---

## 📊 **TEST EXECUTION MATRIX**

### Unit Tests

```
┌─────────────────────────────────────────────────────────────┐
│ Unit Tests Execution Matrix                                 │
├─────────────────────────────────────────────────────────────┤
│ Mock-Mock (200+ tests)      │ ⚡⚡⚡ < 1 second              │
│ Mock-Live (100+ tests)      │ ⚡⚡ < 5 seconds              │
│ Live-Mock (100+ tests)      │ ⚡⚡ < 5 seconds              │
│ Live-Live (100+ tests)      │ ⚡ < 10 seconds              │
├─────────────────────────────────────────────────────────────┤
│ Total (500+ tests)          │ < 2 minutes                   │
└─────────────────────────────────────────────────────────────┘
```

### Integration Tests

```
┌─────────────────────────────────────────────────────────────┐
│ Integration Tests Execution Matrix                          │
├─────────────────────────────────────────────────────────────┤
│ Mock-Mock (100+ tests)      │ ⚡⚡⚡ < 2 seconds             │
│ Mock-Live (50+ tests)       │ ⚡⚡ < 5 seconds              │
│ Live-Mock (100+ tests)      │ ⚡⚡ < 10 seconds             │
│ Live-Live (50+ tests)       │ ⚡ < 15 seconds              │
├─────────────────────────────────────────────────────────────┤
│ Total (300+ tests)          │ < 5 minutes                   │
└─────────────────────────────────────────────────────────────┘
```

### E2E Tests

```
┌─────────────────────────────────────────────────────────────┐
│ E2E Tests Execution Matrix                                  │
├─────────────────────────────────────────────────────────────┤
│ Mock (30+ tests)            │ ⚡⚡⚡ < 5 seconds             │
│ Hybrid (40+ tests)          │ ⚡⚡ < 15 seconds             │
│ Live (30+ tests)            │ ⚡ < 20 seconds              │
├─────────────────────────────────────────────────────────────┤
│ Total (100+ tests)          │ < 10 minutes                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 **RECOMMENDED TEST STRATEGY**

### For Developers (Local Development)

```bash
# Run mock tests before committing
npm run test:mock

# Expected: < 20 seconds
# Coverage: 330+ tests
# Feedback: Immediate
```

### For CI/CD (Automated Testing)

```bash
# Run full test suite on every commit
npm run test:ci

# Expected: < 45 minutes
# Coverage: 1,000+ tests
# Feedback: Comprehensive
```

### For Release (Production Deployment)

```bash
# Run full test suite + performance + security
npm run test:release

# Expected: < 60 minutes
# Coverage: 1,000+ tests + performance + security
# Feedback: Complete
```

---

## 📈 **TEST COVERAGE TARGETS**

| Component | Mock | Hybrid | Live | Target |
|-----------|------|--------|------|--------|
| Frontend | 85% | 90% | 95% | >90% |
| Backend | 90% | 95% | 98% | >95% |
| Critical Paths | 95% | 98% | 100% | 100% |
| Error Handling | 90% | 95% | 100% | 100% |

---

## 🚀 **NEXT STEPS**

1. ✅ Create mock setup files
2. ✅ Create test configuration files
3. ✅ Create unit test variations
4. ✅ Create integration test variations
5. ✅ Create E2E test variations
6. ✅ Set up CI/CD test matrix
7. ✅ Create test reporting dashboard


