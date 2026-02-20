# Vitest 2.x Best Practices for AI-Coded Projects (2026)

**Research Date**: 2026-02-02
**Framework Version**: Vitest 2.x+
**Focus**: Best practices for AI-generated code testing, coverage enforcement, and large-scale TypeScript projects

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Latest Vitest Plugins & Extensions](#latest-vitest-plugins--extensions)
3. [AI-Coding Test Anti-Patterns](#ai-coding-test-anti-patterns)
4. [Coverage Configuration Best Practices](#coverage-configuration-best-practices)
5. [Test Organization for Large TypeScript Projects](#test-organization-for-large-typescript-projects)
6. [Storybook Integration](#storybook-integration)
7. [Performance Optimization](#performance-optimization)
8. [Mocking Strategies](#mocking-strategies)
9. [Advanced Testing Techniques](#advanced-testing-techniques)
10. [References](#references)

---

## Executive Summary

### Key Findings (2026)

**Critical Statistics:**
- **97% of developers** now use AI tools for code generation
- **40%+ of codebases** are AI-generated
- **62% of AI-generated solutions** contain design flaws and security vulnerabilities
- **86% of AI-generated code** fails XSS defenses
- AI code is **2.74x more likely** to contain XSS vulnerabilities than human-written code

### Urgent Recommendations

1. **NEVER trust AI-generated tests without review** - AI tests assumptions, not intent
2. **Enforce strict coverage thresholds** with per-file enforcement
3. **Use mutation testing** for critical business logic (not just line coverage)
4. **Implement anti-pattern detection** in CI/CD pipelines
5. **Adopt browser mode testing** for component tests over JSDOM

---

## Latest Vitest Plugins & Extensions

### Official Tools (2026)

#### 1. **Vitest VS Code Extension**

**Installation:**
```bash
# Via VS Code Marketplace
ext install vitest.explorer
```

**Features:**
- Test discovery and execution from IDE
- Integrated debugging
- Watch mode with instant feedback
- Test result visualization

**Configuration:**
```json
// .vscode/settings.json
{
  "vitest.enable": true,
  "vitest.commandLine": "bun run test",
  "vitest.watchOnStartup": true
}
```

#### 2. **Vitest UI**

**Installation:**
```bash
bun add -d @vitest/ui
```

**Configuration:**
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    ui: true, // Enable UI
    open: true, // Auto-open browser
  },
})
```

**Features:**
- Visual test runner in browser
- Coverage visualization
- Test filtering and search
- Real-time watch mode

**Run:**
```bash
bun run vitest --ui
```

#### 3. **Coverage Providers**

**V8 Coverage (Recommended for Speed):**
```bash
bun add -d @vitest/coverage-v8
```

**Istanbul Coverage (Recommended for Accuracy):**
```bash
bun add -d @vitest/coverage-istanbul
```

**Configuration:**
```typescript
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8', // or 'istanbul'
      reporter: ['text', 'html', 'json-summary', 'lcov'],
      // V8 now uses AST-based remapping (since v3.2.0)
      // Produces identical results to Istanbul with V8 speed
    },
  },
})
```

> **Note (2026)**: Since Vitest v3.2.0, V8 coverage uses AST-based remapping, producing identical coverage reports to Istanbul with superior speed.

#### 4. **Browser Mode Providers**

**Playwright (Recommended):**
```bash
bun add -d @vitest/browser-playwright playwright
```

**Configuration:**
```typescript
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    browser: {
      enabled: true,
      provider: 'playwright',
      name: 'chromium', // or 'firefox', 'webkit'
      headless: true,
    },
  },
})
```

**When to use:**
- Component testing requiring real browser APIs
- DOM manipulation tests
- CSS-in-JS testing
- Visual regression baseline generation

### Third-Party Plugins

#### 5. **Storybook Vitest Addon**

```bash
bun add -d @storybook/experimental-addon-vitest-plugin
```

**Key Features:**
- Transforms stories into Vitest tests automatically
- Runs tests in real browser environment
- IDE integration with debugging
- Accessibility, interaction, and visual testing
- Zero configuration setup

See [Storybook Integration](#storybook-integration) section for details.

---

## AI-Coding Test Anti-Patterns

### Critical Anti-Patterns to Detect

#### 1. **Testing Assumptions, Not Intent**

**Problem:**
AI-generated tests often verify the AI's assumptions about what the code should do, rather than the actual requirements.

**Example (Bad - AI-Generated):**
```typescript
// AI assumes the function should return uppercase
describe('formatName', () => {
  it('should format name', () => {
    expect(formatName('john')).toBe('JOHN')
  })
})
```

**Example (Good - Intent-Driven):**
```typescript
// Test actual requirement from spec
describe('formatName', () => {
  it('should format name as Title Case per user profile spec', () => {
    expect(formatName('john doe')).toBe('John Doe')
  })

  it('should handle hyphenated names', () => {
    expect(formatName('mary-jane')).toBe('Mary-Jane')
  })

  it('should preserve capitalization for acronyms', () => {
    expect(formatName('SMITH III')).toBe('Smith III')
  })
})
```

**Detection Strategy:**
```typescript
// ESLint rule to require descriptive test names
// vitest.config.ts
export default defineConfig({
  test: {
    // Require test names > 20 chars to force specificity
    testNamePattern: '^.{20,}$',
  },
})
```

#### 2. **Missing Edge Cases**

**Problem:**
AI rarely generates tests for:
- Null/undefined inputs
- Empty arrays/objects
- Boundary conditions
- Error states
- Legacy system integration quirks

**Solution - Pre-Test Checklist:**
```typescript
/**
 * REQUIRED TEST CATEGORIES (Check all before merging):
 * [ ] Happy path
 * [ ] Null/undefined inputs
 * [ ] Empty collections
 * [ ] Boundary values (0, -1, MAX_INT)
 * [ ] Error cases (network failures, validation errors)
 * [ ] Race conditions (async operations)
 * [ ] Legacy system compatibility
 */
```

**Enforcement:**
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    coverage: {
      // Force 100% branch coverage (catches missing edge cases)
      thresholds: {
        branches: 100,
        functions: 95,
        lines: 90,
        statements: 90,
      },
    },
  },
})
```

#### 3. **Hardcoded Credentials in Tests**

**Problem:**
AI models learn from training data containing credentials and reproduce them.

**Detection:**
```bash
# Add to CI/CD pipeline
bun add -d @nodesecure/scanner

# Scan test files
npx nsecure --depth=4 ./tests
```

**Prevention:**
```typescript
// tests/setup.ts
beforeAll(() => {
  // Require environment variables for sensitive data
  const required = ['DB_URL', 'API_KEY', 'JWT_SECRET']
  const missing = required.filter(key => !process.env[key])

  if (missing.length > 0) {
    throw new Error(
      `Missing required test environment variables: ${missing.join(', ')}\n` +
      'Load from .env.test file, never hardcode!'
    )
  }
})
```

#### 4. **Package Hallucination**

**Problem:**
AI generates imports for non-existent packages at a rate of **5.2-21.7%**.

**Detection:**
```bash
# Add to pre-commit hook
bun add -d depcheck

# Check for unused and missing dependencies
bun run depcheck --ignores="@types/*"
```

**CI Validation:**
```yaml
# .github/workflows/test.yml
- name: Verify all imports exist
  run: |
    bun install --frozen-lockfile
    bun run build # Will fail on missing imports
    bun run test # Ensure tests import correctly
```

#### 5. **Shallow Mocking**

**Problem:**
AI-generated mocks often return trivial values without validating call patterns.

**Example (Bad - AI-Generated):**
```typescript
vi.mock('./api', () => ({
  fetchUser: vi.fn(() => ({ id: 1, name: 'Test' }))
}))

// Test passes but doesn't verify API was called correctly
```

**Example (Good - Intent-Driven):**
```typescript
import { vi, expect } from 'vitest'

const mockFetchUser = vi.fn()
vi.mock('./api', () => ({
  fetchUser: mockFetchUser
}))

describe('UserProfile', () => {
  it('should fetch user with correct ID and include auth headers', async () => {
    mockFetchUser.mockResolvedValue({ id: 123, name: 'Alice' })

    await loadUserProfile(123)

    // Verify call pattern, not just return value
    expect(mockFetchUser).toHaveBeenCalledOnce()
    expect(mockFetchUser).toHaveBeenCalledWith(123, {
      headers: { Authorization: expect.stringContaining('Bearer ') }
    })
  })
})
```

### Anti-Pattern Detection Workflow

**1. Pre-Commit Hook:**
```bash
#!/bin/bash
# .husky/pre-commit

echo "🔍 Scanning for AI test anti-patterns..."

# Check for hardcoded credentials
if grep -r "password.*=.*['\"]" tests/; then
  echo "❌ Found hardcoded credentials in tests"
  exit 1
fi

# Check for shallow test descriptions
if grep -r "it('should.*')" tests/ | grep -v "# vitest-ignore"; then
  echo "⚠️  Found generic test descriptions (require specific intent)"
fi

# Require package validation
bun run depcheck --ignores="@types/*"
```

**2. CI Pipeline:**
```yaml
# .github/workflows/ai-code-quality.yml
name: AI Code Quality Checks

on: [push, pull_request]

jobs:
  anti-pattern-detection:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for security anti-patterns
        run: |
          # Use Arcanum sec-context rules
          curl -o .sec-patterns https://raw.githubusercontent.com/Arcanum-Sec/sec-context/main/ANTI_PATTERNS.md
          grep -f .sec-patterns tests/ || echo "✅ No security anti-patterns detected"

      - name: Enforce coverage thresholds
        run: bun run test --coverage --run

      - name: Check mutation coverage (critical paths only)
        run: bun run test:mutation src/core/**
```

**3. Testing Critic Agent Pattern:**

```typescript
/**
 * TWO-PHASE TESTING APPROACH FOR AI-GENERATED CODE:
 *
 * Phase 1: Human writes intent-driven tests FIRST
 * - Define expected behavior from requirements
 * - Include edge cases and error states
 * - Focus on contracts and business logic
 *
 * Phase 2: AI implements function to pass tests
 * - AI generates implementation only
 * - Tests were written by human (trusted)
 * - Separate "Testing Critic" AI reviews both
 */

// Example workflow:
// 1. tests/formatCurrency.spec.ts (HUMAN-WRITTEN)
describe('formatCurrency', () => {
  it('should format USD with 2 decimal places and comma separators', () => {
    expect(formatCurrency(1234.5, 'USD')).toBe('$1,234.50')
  })

  it('should handle negative values with parentheses per accounting standards', () => {
    expect(formatCurrency(-500, 'USD')).toBe('($500.00)')
  })

  it('should throw InvalidCurrencyError for unsupported currency codes', () => {
    expect(() => formatCurrency(100, 'FAKE')).toThrow(InvalidCurrencyError)
  })
})

// 2. src/formatCurrency.ts (AI-GENERATED)
// AI implements function to pass human-written tests

// 3. Review by Testing Critic AI:
// - Verifies tests match requirements doc
// - Checks for missing edge cases
// - Validates error handling patterns
```

### Recommended Anti-Pattern Avoidance Prompting

**Research shows that anti-pattern avoidance prompting reduced weakness density by:**
- **64% for OpenAI GPT-3**
- **59% for OpenAI GPT-4**

**Example Prompt Template:**
```
Generate tests for [function name] following these security patterns:

REQUIRED:
- Use environment variables for all credentials (process.env)
- Validate all external inputs with zod schemas
- Test error cases explicitly (network failures, validation errors)
- Mock external dependencies with call verification
- Include boundary tests (null, undefined, empty, max values)

FORBIDDEN PATTERNS:
- Hardcoded credentials or API keys
- Unvalidated user input
- Generic test descriptions ('should work')
- Shallow mocks without call verification
- Missing error case tests
```

---

## Coverage Configuration Best Practices

### Strict Thresholds Enforcement

#### Global and Per-File Thresholds

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',

      // Enable per-file enforcement
      perFile: true,

      // Global thresholds (applied to all files)
      thresholds: {
        lines: 85,
        functions: 90,
        branches: 80,
        statements: 85,
      },

      // Per-pattern thresholds (stricter for critical code)
      thresholds: {
        // Core business logic - require near-perfect coverage
        'src/core/**/*.ts': {
          lines: 95,
          functions: 100,
          branches: 90,
          statements: 95,
        },

        // Utilities - require complete coverage
        'src/utils/**/*.ts': {
          lines: 100,
          functions: 100,
          branches: 100,
          statements: 100,
        },

        // API routes - require high branch coverage (error handling)
        'src/api/**/*.ts': {
          branches: 95,
          lines: 90,
        },

        // UI components - moderate coverage (visual testing supplements)
        'src/components/**/*.tsx': {
          lines: 75,
          branches: 70,
        },
      },
    },
  },
})
```

#### Coverage Shortcuts

**100% Coverage Enforcement:**
```typescript
coverage: {
  thresholds: {
    100: true, // Sets all metrics to 100%
  },
}
```

#### Auto-Update Thresholds

```typescript
coverage: {
  // Automatically increase thresholds when coverage improves
  thresholdAutoUpdate: true,

  thresholds: {
    lines: 80, // Will auto-update to 85 if achieved
  },
}
```

**Workflow:**
1. Coverage improves from 80% → 87%
2. On next run, threshold auto-updates to 87%
3. Prevents coverage regression

### Coverage Reporters

**Recommended Setup:**
```typescript
coverage: {
  reporter: [
    'text',           // Terminal output
    'html',           // Browsable report
    'json-summary',   // For CI badges
    'lcov',           // For SonarQube/CodeCov
  ],

  // HTML report output directory
  reportsDirectory: './coverage',
}
```

**View HTML Report:**
```bash
bun run test --coverage
open coverage/index.html
```

### CI/CD Coverage Enforcement

**GitHub Actions Example:**
```yaml
# .github/workflows/test.yml
name: Test Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: bun install

      - name: Run tests with coverage
        run: bun run test --coverage --run

      - name: Check coverage thresholds
        run: |
          # Vitest exits with error if thresholds not met
          # No additional check needed

      - name: Upload coverage to CodeCov
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage/lcov.info
          fail_ci_if_error: true

      - name: Comment PR with coverage
        uses: davelosert/vitest-coverage-report-action@v2
        if: github.event_name == 'pull_request'
        with:
          json-summary-path: ./coverage/coverage-summary.json
```

### Coverage Exclusions

**Exclude specific patterns:**
```typescript
coverage: {
  exclude: [
    'node_modules/**',
    'dist/**',
    '**/*.d.ts',
    '**/*.config.ts',
    '**/generated/**',
    '**/__mocks__/**',
    'tests/fixtures/**',
  ],

  // Exclude specific files
  exclude: [
    'src/legacy/old-module.ts', // Deprecated code
    'src/experimental/**',       // Not production-ready
  ],
}
```

### Coverage in Vitest UI

**Enable coverage visualization:**
```typescript
test: {
  ui: true,
  coverage: {
    enabled: true, // Show coverage in UI
    reporter: ['html'], // Required for UI visualization
  },
}
```

**Run with UI:**
```bash
bun run vitest --ui --coverage
```

Coverage report appears in the UI iframe with interactive file browsing.

---

## Test Organization for Large TypeScript Projects

### Workspace/Projects Feature

**Best practice for large codebases:** Use Vitest's `projects` feature to split tests by:
- Type (unit, integration, e2e)
- Environment (node, browser, edge)
- Module (packages in monorepo)

#### Example: Multi-Environment Setup

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    projects: [
      // Unit tests (fast, isolated, Node.js)
      {
        name: 'unit',
        include: ['src/**/*.{test,spec}.ts'],
        environment: 'node',
        coverage: {
          thresholds: {
            branches: 90,
            functions: 95,
          },
        },
      },

      // Component tests (browser environment)
      {
        name: 'component',
        include: ['src/components/**/*.test.tsx'],
        environment: 'happy-dom', // or 'jsdom'
        setupFiles: ['./tests/setup/component.ts'],
      },

      // Browser tests (Playwright)
      {
        name: 'browser',
        include: ['tests/browser/**/*.test.ts'],
        browser: {
          enabled: true,
          provider: 'playwright',
          name: 'chromium',
        },
      },

      // Integration tests (slower, external dependencies)
      {
        name: 'integration',
        include: ['tests/integration/**/*.test.ts'],
        testTimeout: 30000,
        setupFiles: ['./tests/setup/integration.ts'],
      },
    ],
  },
})
```

#### Example: Monorepo Setup

```typescript
// vitest.workspace.ts
import { defineWorkspace } from 'vitest/config'

export default defineWorkspace([
  // Auto-discover all packages
  'packages/*',

  // Or explicit configurations
  {
    extends: './vitest.config.ts',
    test: {
      name: 'frontend',
      root: './packages/frontend',
      environment: 'happy-dom',
    },
  },
  {
    extends: './vitest.config.ts',
    test: {
      name: 'backend',
      root: './packages/backend',
      environment: 'node',
    },
  },
])
```

**Run specific projects:**
```bash
# Run only unit tests
bun run vitest --project=unit

# Run multiple projects
bun run vitest --project=unit --project=component

# Run all projects
bun run vitest
```

### Shared Configuration

**Create reusable base config:**
```typescript
// vitest.config.base.ts
import { defineConfig } from 'vitest/config'

export const baseConfig = defineConfig({
  test: {
    globals: true,
    restoreMocks: true,
    mockReset: true,
    clearMocks: true,
    unstubEnvs: true,
    unstubGlobals: true,
  },
})
```

**Extend in projects:**
```typescript
// vitest.config.ts
import { mergeConfig } from 'vitest/config'
import { baseConfig } from './vitest.config.base'

export default mergeConfig(baseConfig, {
  test: {
    // Project-specific overrides
    include: ['src/**/*.test.ts'],
  },
})
```

**Or use `extends` option:**
```typescript
export default defineConfig({
  test: {
    projects: [
      {
        extends: './vitest.config.base.ts',
        name: 'unit',
        include: ['src/**/*.test.ts'],
      },
    ],
  },
})
```

### File Naming Conventions

**Recommended structure for large projects:**

```
src/
├── core/
│   ├── user/
│   │   ├── user.ts                    # Implementation
│   │   ├── user.test.ts               # Unit tests (fast)
│   │   └── user.integration.test.ts   # Integration tests (slow)
│   └── auth/
│       ├── auth.ts
│       └── auth.test.ts
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx            # Component tests
│   │   ├── Button.stories.tsx         # Storybook stories
│   │   └── Button.visual.test.ts      # Visual regression tests
│   └── Form/
│       ├── Form.tsx
│       └── Form.test.tsx
└── utils/
    ├── formatters/
    │   ├── currency.ts
    │   └── currency.test.ts
    └── validators/
        ├── email.ts
        └── email.test.ts

tests/
├── setup/
│   ├── global.ts                      # Global test setup
│   ├── component.ts                   # Component test setup
│   └── integration.ts                 # Integration test setup
├── fixtures/
│   ├── users.ts                       # Test data
│   └── mocks.ts                       # Shared mocks
├── integration/
│   ├── api/
│   │   └── user-api.integration.test.ts
│   └── database/
│       └── migrations.integration.test.ts
└── browser/
    ├── login-flow.browser.test.ts
    └── checkout.browser.test.ts
```

**Project configuration for this structure:**
```typescript
projects: [
  {
    name: 'unit',
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['**/*.integration.test.ts', '**/*.browser.test.ts'],
  },
  {
    name: 'integration',
    include: ['src/**/*.integration.test.ts', 'tests/integration/**/*.test.ts'],
  },
  {
    name: 'browser',
    include: ['tests/browser/**/*.test.ts'],
    browser: { enabled: true },
  },
]
```

### Test Suite Hierarchy Best Practice

**Recommended describe/it structure:**
```typescript
// src/core/user/user-service.test.ts
import { describe, it, expect } from 'vitest'

// Top-level: File path after src/
describe('core/user/user-service', () => {

  // Second level: Class/Module name
  describe('UserService', () => {

    // Third level: Function/method name
    describe('createUser', () => {
      it('should create user with valid email and hashed password', async () => {
        // Test implementation
      })

      it('should throw ValidationError for invalid email format', async () => {
        // Test implementation
      })

      it('should throw ConflictError if email already exists', async () => {
        // Test implementation
      })
    })

    describe('updateUser', () => {
      it('should update user profile fields', async () => {
        // Test implementation
      })
    })
  })
})
```

**Benefits:**
- Clear test output hierarchy
- Easy filtering by path/class/function
- Supports editor test navigation

### Performance Optimization for Large Projects

**Parallel execution:**
```typescript
test: {
  // Use threads for better parallelism in large projects
  pool: 'threads',

  // Control thread count (default: os.cpus().length)
  poolOptions: {
    threads: {
      maxThreads: 8,
      minThreads: 2,
    },
  },
}
```

**Disable isolation for faster tests (use cautiously):**
```typescript
test: {
  // Improves speed but shares state between tests
  isolate: false, // Only if tests are truly independent
}
```

**Run only changed tests:**
```bash
# Only test files affected by git changes
bun run vitest --changed
```

---

## Storybook Integration

### Overview

**Storybook Vitest addon** transforms your stories into real browser-based component tests with zero manual setup.

### Installation

**Automated setup (recommended):**
```bash
npx storybook@latest add @storybook/experimental-addon-vitest-plugin
```

**Manual installation:**
```bash
bun add -d @storybook/experimental-addon-vitest-plugin @vitest/browser playwright
```

**Install Playwright browsers:**
```bash
npx playwright install chromium
```

### Configuration

**Vitest config:**
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import { storybookTest } from '@storybook/experimental-addon-vitest-plugin/vitest-plugin'

export default defineConfig({
  plugins: [
    storybookTest({
      // Specify Storybook config location
      configDir: '.storybook',
    }),
  ],
  test: {
    browser: {
      enabled: true,
      provider: 'playwright',
      name: 'chromium',
      headless: true,
    },
  },
})
```

**Storybook config:**
```typescript
// .storybook/main.ts
import type { StorybookConfig } from '@storybook/react-vite'

const config: StorybookConfig = {
  framework: '@storybook/react-vite',
  stories: ['../src/**/*.stories.@(ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/experimental-addon-vitest-plugin',
  ],
}

export default config
```

### Writing Testable Stories

**Example component:**
```tsx
// src/components/Button/Button.tsx
export interface ButtonProps {
  label: string
  variant?: 'primary' | 'secondary'
  onClick?: () => void
  disabled?: boolean
}

export const Button = ({ label, variant = 'primary', ...props }: ButtonProps) => {
  return (
    <button className={`btn btn-${variant}`} {...props}>
      {label}
    </button>
  )
}
```

**Stories with play functions:**
```tsx
// src/components/Button/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { expect, userEvent, within } from '@storybook/test'
import { Button } from './Button'

const meta: Meta<typeof Button> = {
  component: Button,
  title: 'Components/Button',
}

export default meta
type Story = StoryObj<typeof Button>

export const Primary: Story = {
  args: {
    label: 'Click me',
    variant: 'primary',
  },
}

export const WithInteraction: Story = {
  args: {
    label: 'Interactive Button',
    onClick: () => console.log('Clicked!'),
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button')

    // Interaction test
    await userEvent.click(button)

    // Assertion
    expect(button).toBeInTheDocument()
  },
}

export const Disabled: Story = {
  args: {
    label: 'Disabled',
    disabled: true,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    const button = canvas.getByRole('button')

    // Accessibility test
    expect(button).toBeDisabled()
    expect(button).toHaveAttribute('aria-disabled', 'true')
  },
}
```

**Run tests:**
```bash
# Run all story tests
bun run vitest

# Watch mode
bun run vitest --watch

# IDE integration automatically picks up stories
```

### Advanced: Custom Test Files with Stories

**Share interaction logic between Vitest and Storybook:**
```tsx
// src/components/Form/Form.test.tsx
import { render } from '@testing-library/react'
import { composeStories } from '@storybook/react'
import * as stories from './Form.stories'

const { FilledForm, EmptyForm } = composeStories(stories)

describe('Form', () => {
  it('should render filled form story', () => {
    const { container } = render(<FilledForm />)
    expect(container.querySelector('input[name="email"]')).toHaveValue('test@example.com')
  })

  it('should run story play function', async () => {
    const { container } = render(<FilledForm />)

    // Execute the play function from story
    await FilledForm.play!({ canvasElement: container })

    // Additional assertions
    expect(container.querySelector('.success-message')).toBeInTheDocument()
  })
})
```

### CI/CD Integration

**GitHub Actions:**
```yaml
# .github/workflows/storybook-tests.yml
name: Storybook Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: bun install

      - name: Install Playwright browsers
        run: npx playwright install --with-deps chromium

      - name: Run Storybook tests
        run: bun run vitest --run --browser.headless

      - name: Build Storybook
        run: bun run build-storybook
```

### Key Benefits

1. **Zero Configuration** - Stories automatically become tests
2. **Real Browser Testing** - Tests run in actual browser environment
3. **IDE Integration** - Debug stories as Vitest tests in VS Code
4. **Watch Mode** - Instant feedback during development
5. **Comprehensive Testing** - Interaction, accessibility, and visual tests in one

---

## Performance Optimization

### Test Sharding for Large Suites

**When to use sharding:**
- Test suites with 1000+ test files
- CI environments with multiple runners
- High CPU-count machines (main thread bottleneck)

**How sharding works:**
Vitest splits **test files** (not individual tests) across shards.

**Example: 1000 test files, 4 shards:**
- Shard 1: Files 1-250
- Shard 2: Files 251-500
- Shard 3: Files 501-750
- Shard 4: Files 751-1000

**Local usage:**
```bash
# Run 1st shard of 4
bun run vitest --shard=1/4

# Run 2nd shard of 4
bun run vitest --shard=2/4
```

**CI/CD parallel execution:**
```yaml
# .github/workflows/test-sharded.yml
name: Test (Sharded)

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: bun install

      - name: Run tests (shard ${{ matrix.shard }}/4)
        run: |
          bun run vitest run \
            --shard=${{ matrix.shard }}/4 \
            --reporter=blob \
            --coverage

      - name: Upload test results
        uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.shard }}
          path: .vitest-results/**

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.shard }}
          path: coverage/**

  merge-results:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - name: Download all test results
        uses: actions/download-artifact@v4
        with:
          pattern: test-results-*
          merge-multiple: true

      - name: Merge coverage reports
        run: |
          bun add -d nyc
          npx nyc merge coverage/ .nyc_output/coverage.json
          npx nyc report --reporter=lcov --reporter=text
```

### Pool Configuration

**Threads vs Forks:**

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    // Option 1: Threads (faster for large projects)
    pool: 'threads',
    poolOptions: {
      threads: {
        maxThreads: 8,
        minThreads: 2,
      },
    },

    // Option 2: Forks (better isolation, slightly slower)
    // pool: 'forks',
    // poolOptions: {
    //   forks: {
    //     singleFork: false,
    //   },
    // },
  },
})
```

**Benchmark (1000 test files):**
- `pool: 'threads'` - ~45s
- `pool: 'forks'` - ~52s

**Recommendation:** Use `threads` for large projects unless you need stronger isolation.

### Parallelism Control

**Match CI environment:**
```typescript
test: {
  poolOptions: {
    threads: {
      // Match available CPUs in CI
      maxThreads: process.env.CI ? 2 : 8,
    },
  },
}
```

**Disable file parallelism (faster startup):**
```bash
# Run tests sequentially (one file at a time)
bun run vitest --no-file-parallelism
```

**Use case:** Small projects where startup time > execution time.

### Isolation Toggle

**Default behavior:**
```typescript
test: {
  isolate: true, // Each test file in isolated environment
}
```

**Faster but riskier:**
```typescript
test: {
  isolate: false, // Shared environment across test files
}
```

**⚠️ Warning:** Only disable isolation if:
- Tests don't modify global state
- No database/file system side effects
- Pure unit tests without mocks

**Speed improvement:** 2-5x faster for large suites.

### Run Only Changed Tests

**Git-aware testing:**
```bash
# Test only files affected by uncommitted changes
bun run vitest --changed

# Test files changed since specific commit
bun run vitest --changed=HEAD~5
```

**Watch mode integration:**
```bash
# Automatically test changed files
bun run vitest --watch --changed
```

**Use case:** Pre-commit hook validation.

### Sequence Optimization

**Test execution order:**
```typescript
test: {
  sequence: {
    // Run slower tests first (better parallelism)
    shuffle: true,

    // Or deterministic order
    // shuffle: false,

    // Seed for reproducible shuffling
    seed: 12345,
  },
}
```

### Additional Performance Tips

**1. Minimize setup overhead:**
```typescript
// ❌ Bad: Expensive setup in each test file
beforeEach(async () => {
  await setupDatabase()
  await seedData()
})

// ✅ Good: Shared setup in global config
// vitest.config.ts
test: {
  setupFiles: ['./tests/setup/global.ts'],
}

// tests/setup/global.ts
beforeAll(async () => {
  await setupDatabase()
})
```

**2. Use `test.concurrent` for async tests:**
```typescript
describe('API tests', () => {
  // Run all tests in parallel
  it.concurrent('should fetch user', async () => {
    // ...
  })

  it.concurrent('should fetch posts', async () => {
    // ...
  })
})
```

**3. Set appropriate timeouts:**
```typescript
test: {
  testTimeout: 5000, // Default: 5s (adjust for your tests)
  hookTimeout: 10000, // beforeAll/afterAll timeout
}
```

**4. Reduce reporter overhead:**
```bash
# Minimal output for CI
bun run vitest --reporter=basic

# Detailed output for local dev
bun run vitest --reporter=verbose
```

---

## Mocking Strategies

### vi.mock vs vi.spyOn

**Decision Matrix:**

| Use Case | Tool | Why |
|----------|------|-----|
| Replace entire module | `vi.mock` | Full control over module behavior |
| Monitor existing method | `vi.spyOn` | Preserve original, track calls |
| Partial module mock | `vi.mock` + `importActual` | Mix real and fake exports |
| Type-safe mocking | `vi.spyOn` | Better TypeScript inference |
| Async/await clarity | `vi.spyOn` | More explicit with promises |

### vi.mock Best Practices

**Complete module replacement:**
```typescript
import { vi, describe, it, expect } from 'vitest'

// Hoisted to top of file automatically
vi.mock('./api', () => ({
  fetchUser: vi.fn(() => Promise.resolve({ id: 1, name: 'Alice' })),
  updateUser: vi.fn(),
}))

describe('UserService', () => {
  it('should call fetchUser with correct ID', async () => {
    const { fetchUser } = await import('./api')
    await getUserProfile(123)

    expect(fetchUser).toHaveBeenCalledWith(123)
  })
})
```

**Partial mocking with `importActual`:**
```typescript
vi.mock('./utils', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./utils')>()

  return {
    ...actual,              // Keep all real exports
    generateId: vi.fn(() => 'test-id'), // Mock only this function
  }
})
```

**Type-safe mocking:**
```typescript
import type * as ApiModule from './api'

vi.mock('./api', async (importOriginal) => {
  const actual = await importOriginal<typeof ApiModule>()

  return {
    ...actual,
    fetchUser: vi.fn(async (id: number) => ({ id, name: 'Mock User' })),
  }
})
```

**Using vi.hoisted for external variables:**
```typescript
import { vi } from 'vitest'

// Variables must be hoisted to be accessible in vi.mock
const mockConfig = vi.hoisted(() => ({
  apiUrl: 'https://test.api',
  timeout: 5000,
}))

vi.mock('./config', () => ({
  config: mockConfig,
}))
```

### vi.spyOn Best Practices

**Monitor without replacing:**
```typescript
import { vi, describe, it, expect } from 'vitest'
import * as logger from './logger'

describe('Error handling', () => {
  it('should log error when API fails', async () => {
    const logSpy = vi.spyOn(logger, 'error')

    await callFailingApi()

    expect(logSpy).toHaveBeenCalledWith('API Error:', expect.any(Error))

    logSpy.mockRestore() // Restore original
  })
})
```

**Spy with custom implementation:**
```typescript
const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {
  // Silent logging during tests
})
```

**Spy on object methods:**
```typescript
const user = {
  save: async () => { /* real implementation */ }
}

const saveSpy = vi.spyOn(user, 'save')
  .mockResolvedValue({ id: 1, saved: true })

await user.save()

expect(saveSpy).toHaveBeenCalledOnce()
```

### Cleanup Patterns

**Automatic cleanup (recommended):**
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    mockReset: true,        // Reset mock call history after each test
    restoreMocks: true,     // Restore original implementations
    clearMocks: true,       // Clear mock call history
    unstubEnvs: true,       // Restore process.env
    unstubGlobals: true,    // Restore global variables
  },
})
```

**Manual cleanup:**
```typescript
import { afterEach, vi } from 'vitest'

afterEach(() => {
  vi.clearAllMocks()     // Clear call history
  vi.resetAllMocks()     // Reset + clear implementations
  vi.restoreAllMocks()   // Restore original implementations
})
```

### Spy Option for Automatic Spying

**Auto-spy all module exports:**
```typescript
vi.mock('./api', { spy: true })

// All exports are automatically spied
import { fetchUser, updateUser } from './api'

// Real implementations run, but calls are tracked
await fetchUser(1)

expect(fetchUser).toHaveBeenCalledWith(1)
```

### Advanced Mocking Patterns

**Conditional mocking based on arguments:**
```typescript
const fetchUser = vi.fn((id: number) => {
  if (id === 999) {
    throw new Error('User not found')
  }
  return Promise.resolve({ id, name: `User ${id}` })
})

vi.mock('./api', () => ({ fetchUser }))
```

**Stateful mocks:**
```typescript
let callCount = 0

const rateLimitedFetch = vi.fn(() => {
  callCount++
  if (callCount > 3) {
    throw new Error('Rate limit exceeded')
  }
  return Promise.resolve({ data: 'success' })
})

vi.mock('./api', () => ({ fetch: rateLimitedFetch }))
```

**Mock timers:**
```typescript
import { vi, beforeEach, afterEach } from 'vitest'

beforeEach(() => {
  vi.useFakeTimers()
})

afterEach(() => {
  vi.restoreAllMocks()
})

it('should retry after delay', async () => {
  const promise = retryWithDelay(() => fetchData(), 1000)

  // Fast-forward 1 second
  await vi.advanceTimersByTimeAsync(1000)

  await expect(promise).resolves.toBeDefined()
})
```

### Common Pitfalls

**❌ Forgetting async with importActual:**
```typescript
// Wrong
vi.mock('./api', (importOriginal) => {
  const actual = importOriginal() // ❌ Missing await
  return { ...actual }
})

// Correct
vi.mock('./api', async (importOriginal) => {
  const actual = await importOriginal() // ✅ Async
  return { ...actual }
})
```

**❌ Not cleaning up between tests:**
```typescript
// Wrong
describe('tests', () => {
  const mock = vi.fn()

  it('test 1', () => {
    mock()
    expect(mock).toHaveBeenCalledOnce() // ✅ Pass
  })

  it('test 2', () => {
    expect(mock).toHaveBeenCalledOnce() // ❌ Fail (called twice)
  })
})

// Correct
describe('tests', () => {
  const mock = vi.fn()

  afterEach(() => {
    mock.mockClear() // ✅ Clear between tests
  })

  // Or use config.mockReset: true
})
```

---

## Advanced Testing Techniques

### Snapshot Testing

**When to use snapshots:**
- Component rendering output
- API response structures
- Configuration objects
- Error messages
- Generated code

**When NOT to use snapshots:**
- Dynamic data (timestamps, IDs)
- Large complex objects
- Frequently changing output

#### Inline Snapshots

```typescript
import { it, expect } from 'vitest'

it('should format user profile', () => {
  const profile = formatUserProfile({ name: 'Alice', age: 30 })

  expect(profile).toMatchInlineSnapshot(`
    {
      "displayName": "Alice",
      "age": 30,
      "joinedDate": "2024-01-15",
    }
  `)
})
```

**Update snapshots:**
```bash
# Update all snapshots
bun run vitest -u

# Watch mode: press 'u' to update
bun run vitest --watch
```

#### File Snapshots

```typescript
it('should generate correct HTML', () => {
  const html = renderTemplate({ title: 'Home' })

  expect(html).toMatchFileSnapshot('./snapshots/home.html')
})
```

**Benefits:**
- Readable file format (HTML, CSS, JSON)
- Easier code review
- Custom file extensions

#### Best Practices

**1. Add descriptive hints:**
```typescript
expect(value).toMatchSnapshot('user profile with admin role')
expect(value).toMatchSnapshot('error state')
```

**2. Commit snapshots to version control:**
```bash
git add **/__snapshots__/**
```

**3. Review snapshot changes carefully:**
```bash
# Show snapshot diffs
git diff **/__snapshots__/**
```

**4. Use for async tests with test context:**
```typescript
it.concurrent('parallel test 1', async ({ expect }) => {
  const data = await fetchData()
  expect(data).toMatchSnapshot()
})

it.concurrent('parallel test 2', async ({ expect }) => {
  const data = await fetchOtherData()
  expect(data).toMatchSnapshot()
})
```

### Mutation Testing (Beyond Line Coverage)

**Why mutation testing matters:**
- Line coverage: "What code was executed?"
- Mutation coverage: "Do tests detect bugs?"

**Example:**
```typescript
// Code with 100% line coverage
function divide(a: number, b: number) {
  if (b === 0) {
    throw new Error('Division by zero')
  }
  return a / b
}

// Bad test (100% line coverage, 0% mutation coverage)
it('should divide numbers', () => {
  divide(10, 2) // No assertion!
})

// Good test (100% line coverage, 100% mutation coverage)
it('should divide numbers', () => {
  expect(divide(10, 2)).toBe(5)
})

it('should throw on division by zero', () => {
  expect(() => divide(10, 0)).toThrow('Division by zero')
})
```

**Mutation testing tools:**
```bash
# Stryker (most popular)
bun add -d @stryker-mutator/core @stryker-mutator/vitest-runner

# Configuration
npx stryker init
```

**Example config:**
```javascript
// stryker.config.mjs
export default {
  testRunner: 'vitest',
  mutate: [
    'src/core/**/*.ts',
    '!src/**/*.test.ts',
  ],
  thresholds: { high: 80, low: 60, break: 50 },
  coverageAnalysis: 'perTest',
}
```

**Run mutation tests:**
```bash
# Run mutation testing (slow - only for critical code)
npx stryker run

# CI: Run on critical paths only
npx stryker run --mutate="src/core/auth/**"
```

**Mutation score interpretation:**
- **90-100%**: Excellent test quality
- **70-89%**: Good, some gaps
- **50-69%**: Weak tests, needs improvement
- **<50%**: Inadequate testing

### Browser Testing Patterns

**Real browser vs JSDOM:**

| Feature | JSDOM | happy-dom | Browser Mode |
|---------|-------|-----------|--------------|
| Speed | Fast | Faster | Slower |
| Accuracy | Good | Good | Perfect |
| CSS support | Limited | Limited | Full |
| Layout/rendering | No | No | Yes |
| Web APIs | Most | Most | All |

**Use browser mode when:**
- Testing drag-and-drop
- CSS-in-JS rendering
- Intersection observers
- Canvas/WebGL
- Browser-specific APIs

**Example:**
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    projects: [
      // Fast unit tests (JSDOM)
      {
        name: 'unit',
        environment: 'jsdom',
        include: ['src/**/*.test.ts'],
      },

      // Visual component tests (Browser)
      {
        name: 'visual',
        browser: {
          enabled: true,
          provider: 'playwright',
          name: 'chromium',
        },
        include: ['tests/visual/**/*.test.ts'],
      },
    ],
  },
})
```

**Visual regression testing:**
```typescript
import { test, expect } from '@playwright/test'

test('button should render correctly', async ({ page }) => {
  await page.goto('http://localhost:6006/iframe.html?id=button--primary')

  // Visual snapshot
  await expect(page).toHaveScreenshot('button-primary.png')
})
```

### Test Context and Fixtures

**Reusable test context:**
```typescript
import { test, expect } from 'vitest'

// Define fixtures
interface Fixtures {
  authenticatedUser: User
  database: Database
}

const test = baseTest.extend<Fixtures>({
  authenticatedUser: async ({}, use) => {
    const user = await createTestUser()
    await authenticateUser(user)
    await use(user)
    await deleteTestUser(user.id)
  },

  database: async ({}, use) => {
    const db = await setupTestDatabase()
    await use(db)
    await teardownTestDatabase(db)
  },
})

// Use in tests
test('should fetch user data', async ({ authenticatedUser, database }) => {
  const data = await database.query('SELECT * FROM users WHERE id = ?', [authenticatedUser.id])
  expect(data).toBeDefined()
})
```

### Watch Mode Filters

**Interactive filtering:**
```bash
# Start watch mode
bun run vitest

# Press 'p' to filter by filename
# Type: "user" → runs only *user*.test.ts files

# Press 't' to filter by test name
# Type: "should create" → runs only tests matching pattern
```

**CLI filters:**
```bash
# Run tests matching filename pattern
bun run vitest user

# Run tests matching name pattern
bun run vitest -t "should create"

# Combine filters
bun run vitest user -t "validation"
```

**Run specific test by line number:**
```bash
# Run test at specific line
bun run vitest src/user.test.ts:42
```

### Test-Only Mode

**Focus on specific tests:**
```typescript
describe.only('UserService', () => {
  it.only('should create user', () => {
    // Only this test runs
  })

  it('should update user', () => {
    // Skipped
  })
})
```

**⚠️ Warning:** Never commit `.only` - add pre-commit hook:
```bash
#!/bin/bash
# .husky/pre-commit

if grep -r "\.only(" tests/ src/; then
  echo "❌ Found .only() in tests - remove before committing"
  exit 1
fi
```

---

## References

### Official Documentation

- [Vitest Guide](https://vitest.dev/guide/)
- [Vitest Configuration](https://vitest.dev/config/)
- [Vitest API Reference](https://vitest.dev/api/)
- [Coverage Guide](https://vitest.dev/guide/coverage)
- [Browser Mode](https://vitest.dev/guide/browser/)
- [Mocking Guide](https://vitest.dev/guide/mocking)
- [Test Projects](https://vitest.dev/guide/projects)
- [CLI Reference](https://vitest.dev/guide/cli)
- [Improving Performance](https://vitest.dev/guide/improving-performance)

### Vitest Ecosystem

- [Vitest VS Code Extension](https://marketplace.visualstudio.com/items?itemName=vitest.explorer)
- [Storybook Vitest Addon](https://storybook.js.org/docs/writing-tests/integrations/vitest-addon/index)
- [Component Testing Guide](https://vitest.dev/guide/browser/component-testing)

### Best Practices & Guides

- [Vitest Best Practices - Project Rules](https://www.projectrules.ai/rules/vitest)
- [Best Techniques with Vitest Framework](https://dev.to/wallacefreitas/best-techniques-to-create-tests-with-the-vitest-framework-9al)
- [Unit Testing with Vitest - Better Stack](https://betterstack.com/community/guides/testing/vitest-explained/)
- [Why Vitest Projects Configuration](https://howtotestfrontend.com/resources/vitest-config-projects)
- [Vitest Code Coverage Configuration - Frontend Masters](https://frontendmasters.com/courses/enterprise-ui-dev/vitest-code-coverage-configuration/)

### AI Code Testing Research

- [AI Code Security Anti-Patterns (Arcanum-Sec)](https://github.com/Arcanum-Sec/sec-context)
- [Anti-Pattern Avoidance Prompting - Endor Labs](https://www.endorlabs.com/learn/anti-pattern-avoidance-a-simple-prompt-pattern-for-safer-ai-generated-code)
- [5 Code Review Anti-Patterns AI Can Eliminate](https://www.coderabbit.ai/blog/5-code-review-anti-patterns-you-can-eliminate-with-ai)
- [8 AI Code Generation Mistakes (2026)](https://vocal.media/futurism/8-ai-code-generation-mistakes-devs-must-fix-to-win-2026)
- [Secure Code Generation via AI](https://ghuntley.com/secure-codegen/)

### Coverage & Quality Metrics

- [Code Coverage vs Mutation Testing](https://journal.optivem.com/p/code-coverage-vs-mutation-testing)
- [The Pitfalls of Test Coverage - Mutation Testing with Stryker](https://dev.to/wintrover/the-pitfalls-of-test-coverage-introducing-mutation-testing-with-stryker-and-cosmic-ray-1kcg)
- [Test Coverage Metrics Guide - BrowserStack](https://www.browserstack.com/guide/test-coverage-metrics-in-software-testing)
- [Mutation Testing Ultimate Guide (2025)](https://mastersoftwaretesting.com/testing-fundamentals/types-of-testing/mutation-testing)
- [Comparing Coverage Techniques - Sven Ruppert](https://svenruppert.com/2024/05/31/comparing-code-coverage-techniques-line-property-based-and-mutation-testing/)

### TypeScript & Component Testing

- [Jest vs Vitest for TypeScript Projects](https://medium.com/on-tech-by-leighton/jest-vs-vitest-choosing-the-right-testing-framework-for-your-typescript-projects-07f23c4aa76c)
- [Why Vitest for TypeScript - DEV Community](https://dev.to/itsweshy/why-vitest-is-a-powerful-testing-framework-for-typescript-projects-844)
- [React Testing Setup: Vitest + TypeScript + RTL](https://dev.to/kevinccbsg/react-testing-setup-vitest-typescript-react-testing-library-42c8)
- [Choosing Testing Framework 2026 - Jest vs Vitest vs Playwright](https://dev.to/agent-tools-dev/choosing-a-typescript-testing-framework-jest-vs-vitest-vs-playwright-vs-cypress-2026-7j9)

### Storybook Integration

- [Component Testing with Storybook and Vitest](https://storybook.js.org/blog/component-test-with-storybook-and-vitest/)
- [Next Level Component Testing](https://medium.com/towardsdev/next-level-component-testing-with-storybook-5c11381c7c97)
- [Sharing Interaction Tests Between Vitest and Storybook](https://scottnath.com/blahg/sharing-tests-between-vitest-and-storybook/)
- [Mastering Unit Testing in Storybook with Vitest](https://javascript.plainenglish.io/mastering-unit-testing-in-storybook-with-vitest-and-react-testing-library-an-advanced-guide-to-8b675f05759a)

### Performance & Optimization

- [How to Speed Up Vitest - BuildPulse](https://buildpulse.io/blog/how-to-speed-up-vitest)
- [Speed Up Test Suites with Sharding - Michael Guay](https://michaelguay.dev/speed-up-jest-test-suites-with-sharding/)
- [Vitest Sharding Troubleshooting](https://runebook.dev/en/articles/vitest/guide/cli/shard)

### Mocking & Advanced Techniques

- [vi.spyOn vs vi.mock Discussion](https://github.com/vitest-dev/vitest/discussions/4224)
- [More Mocks! Mocking Modules in Vitest - Bitovi](https://www.bitovi.com/blog/more-mocks-mocking-modules-in-vitest)
- [Advanced Guide to Vitest Mocking - LogRocket](https://blog.logrocket.com/advanced-guide-vitest-testing-mocking/)
- [Effective Unit Testing: Mocks in Vitest](https://medium.com/@ryanmambou/effective-unit-testing-using-mocks-in-vitest-4737f63f88c3)
- [Mock vs SpyOn Guide](https://dev.to/axsh/mock-vs-spyon-in-vitest-with-typescript-a-guide-for-unit-and-integration-tests-2ge6)

### Browser Mode & Playwright

- [Vitest Browser Mode vs Playwright - Epic Web](https://www.epicweb.dev/vitest-browser-mode-vs-playwright)
- [Configuring Playwright with Vitest](https://vitest.dev/config/browser/playwright)
- [Reliable Component Testing with Browser Mode](https://mayashavin.com/articles/component-testing-browser-vitest)
- [How to Run Playwright within Vitest](https://www.the-koi.com/projects/how-to-run-playwright-within-vitest/)
- [Component Testing with Playwright and Vitest](https://www.thecandidstartup.org/2025/01/06/component-test-playwright-vitest.html)

### Snapshot Testing

- [Master Snapshot Testing with Vitest](https://blog.seancoughlin.me/mastering-snapshot-testing-with-vite-vitest-or-jest-in-typescript)
- [Snapshot Testing Styled-Components](https://brightinventions.pl/blog/snapshot-testing-styled-components-with-vitest/)
- [Snapshot Testing - Storybook](https://storybook.js.org/docs/writing-tests/snapshot-testing)

### GitHub Issues & Discussions

- [Coverage Threshold Decimal Places](https://github.com/vitest-dev/vitest/discussions/6143)
- [Coverage Threshold Bumper](https://github.com/vitest-dev/vitest/issues/1241)
- [Absolute Coverage Thresholds](https://github.com/vitest-dev/vitest/issues/7056)
- [Filter Tests in CLI Discussion](https://github.com/vitest-dev/vitest/discussions/6833)
- [Filter by Filename in Watch Mode](https://github.com/vitest-dev/vitest/issues/1797)

---

## Appendix: Quick Reference

### Essential Commands

```bash
# Install Vitest
bun add -d vitest

# Run tests
bun run vitest

# Run with coverage
bun run vitest --coverage

# Run in UI mode
bun run vitest --ui

# Run in watch mode
bun run vitest --watch

# Run only changed files
bun run vitest --changed

# Run with sharding
bun run vitest --shard=1/4

# Update snapshots
bun run vitest -u

# Run specific project
bun run vitest --project=unit
```

### Configuration Template

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    // Environment
    environment: 'node', // or 'jsdom', 'happy-dom'

    // Global test APIs
    globals: true,

    // Setup files
    setupFiles: ['./tests/setup.ts'],

    // Coverage
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json-summary'],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },

    // Mocking
    mockReset: true,
    restoreMocks: true,

    // Timeouts
    testTimeout: 10000,
    hookTimeout: 10000,

    // Browser mode
    browser: {
      enabled: false,
      provider: 'playwright',
      name: 'chromium',
    },
  },
})
```

### AI Testing Checklist

- [ ] Write tests BEFORE implementation (TDD)
- [ ] Review all AI-generated tests manually
- [ ] Check for hardcoded credentials
- [ ] Verify edge cases are tested
- [ ] Ensure error states are covered
- [ ] Validate mock call patterns (not just return values)
- [ ] Run mutation testing on critical paths
- [ ] Enforce coverage thresholds in CI
- [ ] Use descriptive test names (>20 chars)
- [ ] Clean up mocks between tests
- [ ] Never commit `.only()` or `.skip()`

---

**Document Status**: ✅ Complete
**Last Updated**: 2026-02-02
**Next Review**: 2026-Q2
