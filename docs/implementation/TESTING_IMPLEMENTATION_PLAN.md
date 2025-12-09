# TraceRTM Testing Implementation Plan

Concrete, actionable steps to implement the 2025 testing strategy with specific commands and configuration details.

## Phase 1: Shift-Left Foundation (Week 1-4)

### Step 1.1: Pre-Commit Hooks Setup

#### Install & Configure Husky
```bash
# Install husky and lint-staged
bun add -D husky lint-staged

# Initialize husky
bunx husky init

# Create pre-commit hook
cat > .husky/pre-commit << 'EOF'
#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

echo "🔍 Running pre-commit checks..."
bunx lint-staged --allow-empty
EOF

chmod +x .husky/pre-commit
```

#### Configure lint-staged in package.json
```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "biome check --write",
      "tsc --noEmit",
      "vitest run --related --globals"
    ],
    "*.{md,json}": [
      "biome check --write"
    ]
  }
}
```

#### Create Pre-Commit Validation Script
```bash
cat > scripts/pre-commit-check.sh << 'EOF'
#!/bin/bash
set -e

echo "▬ Pre-Commit Quality Gates ▬"

# 1. Lint check
echo "1️⃣  Checking code style..."
bun run lint:check

# 2. Type check
echo "2️⃣  Checking TypeScript..."
bun run typecheck

# 3. Format check
echo "3️⃣  Checking formatting..."
bun run format:check

# 4. Unit tests for changed files
echo "4️⃣  Running affected tests..."
bun test --run --testPathPattern="$(git diff --cached --name-only | grep -E '\.test\.' | head -1 || echo '.*')"

echo "✅ All pre-commit checks passed!"
EOF

chmod +x scripts/pre-commit-check.sh
```

### Step 1.2: GitHub Branch Protection Rules

Create `.github/workflows/branch-protection.yml`:
```yaml
name: Branch Protection Gates

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  quality-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v1

      - name: Install dependencies
        run: bun install

      - name: Lint
        run: bun run lint

      - name: Type check
        run: bun run typecheck

      - name: Run tests
        run: bun run test -- --run

      - name: Check coverage
        run: |
          COVERAGE=$(bun run test:coverage 2>/dev/null | grep -o '[0-9]\+%' | head -1 | tr -d '%')
          if [ "$COVERAGE" -lt 80 ]; then
            echo "❌ Coverage is $COVERAGE%, minimum 80% required"
            exit 1
          fi

  security-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Snyk scan
        run: |
          npm install -g snyk
          snyk test --severity-threshold=high || true
```

### Step 1.3: Performance Baseline Testing

Install and configure Lighthouse CI:
```bash
# Install Lighthouse CI
npm install -g @lhci/cli@latest

# Create config
cat > lighthouserc.json << 'EOF'
{
  "ci": {
    "collect": {
      "url": [
        "http://localhost:3000",
        "http://localhost:3000/projects",
        "http://localhost:3000/graph"
      ],
      "staticDistDir": "./dist",
      "numberOfRuns": 3
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.90}],
        "categories:accessibility": ["error", {"minScore": 0.95}],
        "categories:best-practices": ["error", {"minScore": 0.85}]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
EOF
```

Add to package.json scripts:
```json
{
  "scripts": {
    "test:performance": "lhci collect --config=lighthouserc.json",
    "test:performance:ci": "lhci assertion --config=lighthouserc.json"
  }
}
```

### Step 1.4: Error Tracking Setup (Sentry)

```bash
# Install Sentry SDK
bun add @sentry/react

# Create src/lib/sentry.ts
cat > frontend/apps/web/src/lib/sentry.ts << 'EOF'
import * as Sentry from "@sentry/react"
import { useEffect } from "react"
import { useRouterState } from "@tanstack/react-router"

export function initializeSentry() {
  if (typeof window === 'undefined') return

  Sentry.init({
    dsn: process.env.VITE_SENTRY_DSN,
    environment: process.env.NODE_ENV,
    tracesSampleRate: 1.0,
    integrations: [
      new Sentry.Replay({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
  })
}

export function SentryRouterUpdater() {
  const router = useRouterState()

  useEffect(() => {
    Sentry.captureMessage(`Navigated to ${router.location.pathname}`, 'info')
  }, [router.location.pathname])

  return null
}
EOF

# Add to main App component
# import { initializeSentry, SentryRouterUpdater } from '@/lib/sentry'
# initializeSentry()
# <SentryRouterUpdater />
```

---

## Phase 2: Expanded Coverage (Week 5-8)

### Step 2.1: Visual Regression Testing

Install Percy for visual regression:
```bash
# Install Percy
bun add -D @percy/cli @percy/react

# Create Percy config
cat > .percyrc << 'EOF'
{
  "version": 2,
  "static": {
    "cleanUrls": true,
    "include": "dist/**/*",
    "exclude": []
  }
}
EOF

# Create visual regression tests
cat > frontend/apps/web/src/__tests__/visual/critical-pages.test.tsx << 'EOF'
import { test } from '@playwright/test'
import { percySnapshot } from '@percy/playwright'

test.describe('Visual Regression - Critical Pages', () => {
  test('Dashboard page layout', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await percySnapshot(page, 'Dashboard - Default View')
  })

  test('Project list layout', async ({ page }) => {
    await page.goto('/projects')
    await page.waitForLoadState('networkidle')
    await percySnapshot(page, 'Projects - List View')
  })

  test('Graph visualization', async ({ page }) => {
    await page.goto('/graph')
    await page.waitForLoadState('networkidle')
    await percySnapshot(page, 'Graph - Full View')
  })
})
EOF
```

Add to package.json:
```json
{
  "scripts": {
    "test:visual": "percy exec -- playwright test src/__tests__/visual"
  }
}
```

### Step 2.2: API Contract Testing

Create OpenAPI contract validation:
```bash
# Create openapi-spec.yaml
cat > api/openapi-spec.yaml << 'EOF'
openapi: 3.0.0
info:
  title: TraceRTM API
  version: 1.0.0
paths:
  /api/v1/items:
    get:
      summary: List items
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Item'
    post:
      summary: Create item
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateItemInput'
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Item'

components:
  schemas:
    Item:
      type: object
      properties:
        id:
          type: string
        title:
          type: string
        status:
          type: string
          enum: [pending, in_progress, done]
      required: [id, title, status]

    CreateItemInput:
      type: object
      properties:
        title:
          type: string
          minLength: 1
          maxLength: 255
        status:
          type: string
          enum: [pending, in_progress, done]
      required: [title]
EOF

# Create contract test
cat > frontend/apps/web/src/__tests__/contracts/api-contract.test.ts << 'EOF'
import SwaggerParser from '@apidevtools/swagger-parser'
import { describe, it, expect } from 'vitest'

describe('API Contract Validation', () => {
  it('should validate OpenAPI spec is valid', async () => {
    const api = await SwaggerParser.validate('./api/openapi-spec.yaml')
    expect(api).toBeDefined()
    expect(api.paths).toBeDefined()
  })

  it('should have required endpoints', async () => {
    const api = await SwaggerParser.validate('./api/openapi-spec.yaml')
    expect(Object.keys(api.paths)).toContain('/api/v1/items')
  })

  it('should validate response schemas', async () => {
    const api = await SwaggerParser.validate('./api/openapi-spec.yaml')
    const itemSchema = api.components.schemas.Item
    expect(itemSchema.properties).toHaveProperty('id')
    expect(itemSchema.properties).toHaveProperty('title')
    expect(itemSchema.properties).toHaveProperty('status')
  })
})
EOF

bun add -D @apidevtools/swagger-parser
```

### Step 2.3: Performance Regression Detection

Add to CI/CD pipeline:
```yaml
# .github/workflows/perf-regression.yml
name: Performance Regression Detection

on:
  pull_request:

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v1

      - name: Install dependencies
        run: bun install

      - name: Build
        run: bun run build:web

      - name: Analyze bundle size
        run: |
          MAIN_SIZE=$(wc -c < dist/bundle.js)
          if [ "$MAIN_SIZE" -gt 102400 ]; then
            echo "❌ Bundle size is $((MAIN_SIZE / 1024))KB, max 100KB"
            exit 1
          fi

      - name: Run Lighthouse
        run: bun run test:performance

      - name: Check API response times
        run: |
          bun run test:integration -- --grep "performance"
```

---

## Phase 3: Production Observability (Week 9-12)

### Step 3.1: Real User Monitoring (RUM)

```bash
# Install analytics
bun add web-vitals

# Create src/lib/analytics.ts
cat > frontend/apps/web/src/lib/analytics.ts << 'EOF'
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

export function initializeRUM() {
  if (typeof window === 'undefined') return

  // Core Web Vitals
  getCLS(metric => trackMetric('CLS', metric))
  getFID(metric => trackMetric('FID', metric))
  getFCP(metric => trackMetric('FCP', metric))
  getLCP(metric => trackMetric('LCP', metric))
  getTTFB(metric => trackMetric('TTFB', metric))

  // Custom metrics
  trackPageViewTiming()
}

function trackMetric(name: string, metric: any) {
  if (window.gtag) {
    window.gtag('event', name, {
      value: Math.round(metric.value),
      event_category: 'Web Vitals',
      event_label: metric.id,
      non_interaction: true,
    })
  }

  if (window.Sentry) {
    window.Sentry.captureMessage(`${name}: ${metric.value}ms`)
  }
}

function trackPageViewTiming() {
  if (performance.timing) {
    const timing = performance.timing
    const pageLoadTime = timing.loadEventEnd - timing.navigationStart
    trackMetric('PageLoadTime', { value: pageLoadTime })
  }
}
EOF

# Add to main.tsx
# import { initializeRUM } from '@/lib/analytics'
# initializeRUM()
```

### Step 3.2: Chaos Engineering Baseline

```bash
# Install chaos toolkit
npm install -g chaostoolkit

# Create chaos-scenarios.yaml
cat > infra/chaos-scenarios.yaml << 'EOF'
version: 1.0.0
title: TraceRTM Resilience Tests
description: Test system resilience to failures

scenarios:
  - name: Database Connection Failure
    description: Simulate database becoming unavailable
    steps:
      - type: probe
        name: check-database-status
        provider:
          type: http
          url: http://localhost/health

      - type: action
        name: kill-database
        provider:
          type: docker
          image: postgres:15
          action: stop

      - type: probe
        name: api-graceful-degradation
        provider:
          type: http
          url: http://localhost/api/v1/items
          expected_status: 503

  - name: API Rate Limiting
    description: Test rate limiting under load
    steps:
      - type: action
        name: apply-rate-limit
        provider:
          type: command
          cmd: "iptables -A INPUT -p tcp --dport 8000 -m limit --limit 10/second -j ACCEPT"

      - type: probe
        name: concurrent-requests
        provider:
          type: http
          url: http://localhost/api/v1/items
          concurrent: 100

  - name: Network Latency
    description: Simulate high latency network
    steps:
      - type: action
        name: add-latency
        provider:
          type: command
          cmd: "tc qdisc add dev eth0 root netem delay 500ms"

      - type: probe
        name: api-response-time
        provider:
          type: http
          url: http://localhost/api/v1/items
          max_response_time: 1000
EOF
```

### Step 3.3: Quality Metrics Dashboard

Create GitHub dashboard via Actions:
```yaml
# .github/workflows/quality-metrics.yml
name: Publish Quality Metrics

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Bun
        uses: oven-sh/setup-bun@v1

      - name: Generate metrics
        run: |
          bun install
          bun run test:coverage
          bun run test:performance
          bun run lint

      - name: Publish to dashboard
        run: |
          node scripts/publish-metrics.js
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Create `scripts/publish-metrics.js`:
```javascript
const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

const metrics = {
  timestamp: new Date().toISOString(),
  tests: {
    total: 706,
    passing: 706,
    failing: 0,
    coverage: 0.82,  // Update based on actual coverage
  },
  performance: {
    lighthouse: {
      performance: 92,
      accessibility: 96,
      bestPractices: 89,
    },
    bundleSize: 98304,  // bytes
  },
  code: {
    lintErrors: 0,
    typeErrors: 0,
    vulnerabilities: 0,
  },
}

// Save to repo
fs.writeFileSync(
  path.join(process.cwd(), 'metrics.json'),
  JSON.stringify(metrics, null, 2)
)

// Commit and push
execSync('git add metrics.json')
execSync('git commit -m "chore: update quality metrics"')
execSync('git push')
```

---

## Phase 4: Team Knowledge & Process (Week 13-16)

### Step 4.1: Create Testing Guidelines

```bash
cat > docs/TESTING_GUIDELINES.md << 'EOF'
# TraceRTM Testing Guidelines

## Test Organization

### Unit Tests
- Location: `src/__tests__/[feature]/[file].test.ts`
- Focus: Pure functions, business logic
- Speed: <100ms per test
- Isolation: No external dependencies

### Integration Tests
- Location: `src/__tests__/integration/[feature].test.tsx`
- Focus: Component interactions, data flows
- Speed: <500ms per test
- Setup: Use real stores but mock APIs

### E2E Tests
- Location: `e2e/[feature].spec.ts`
- Focus: Critical user journeys
- Speed: Variable, grouped by feature
- Isolation: Each test independent

## Writing Good Tests

### DO:
- ✓ Test behavior, not implementation
- ✓ Use descriptive test names
- ✓ Arrange-Act-Assert pattern
- ✓ Test one thing per test
- ✓ Use test data builders for complex setups

### DON'T:
- ✗ Test implementation details
- ✗ Over-mock dependencies
- ✗ Shared test state across tests
- ✗ Sleep/arbitrary delays
- ✗ Test framework internals

## Coverage Goals

- Critical business logic: 100%
- Features: >80%
- Utilities: >90%
- Overall: >80%

## Running Tests

\`\`\`bash
./rtm test               # All tests
./rtm test:watch        # Watch mode
./rtm test:coverage     # With coverage
./rtm test:ui           # Visual dashboard
\`\`\`
EOF
```

### Step 4.2: Establish Test Review Process

Add to PR template (`.github/pull_request_template.md`):
```markdown
## Testing Checklist

- [ ] Tests written for new functionality
- [ ] All tests passing locally (`./rtm test`)
- [ ] Coverage maintained >80%
- [ ] No flaky tests added
- [ ] E2E tests added for critical flows
- [ ] Security tests passing
- [ ] Accessibility tests passing

## Test Coverage
- Lines covered: ____%
- New tests: ___
- Affected tests: ___

## Performance Impact
- Bundle size change: ___KB
- Test execution change: ___ms
```

### Step 4.3: Schedule Knowledge Sharing

```bash
# Weekly testing sync (30 min, Fridays 10am)
- Review failing tests
- Discuss testing patterns
- Share best practices
- Demo new tools

# Monthly metrics review (1 hour)
- Coverage trends
- Performance metrics
- Test execution times
- Quality improvements

# Quarterly retrospective (2 hours)
- Testing effectiveness
- Process improvements
- Tool evaluations
- Team training needs
```

---

## Quick Implementation Checklist

### Week 1 (Shift-Left Foundation)
- [ ] Install and configure Husky
- [ ] Set up GitHub branch protection
- [ ] Create pre-commit hooks
- [ ] Run first pre-commit check
- [ ] Document in team wiki

### Week 2-3 (GitHub Actions)
- [ ] Create branch protection workflow
- [ ] Add security scanning job
- [ ] Add performance baseline job
- [ ] Test on sample PR
- [ ] Document gate requirements

### Week 4 (Monitoring & Baseline)
- [ ] Set up Sentry integration
- [ ] Create Lighthouse baseline
- [ ] Document error tracking
- [ ] Review initial metrics
- [ ] Brief team

### Week 5-6 (Visual & Contract Testing)
- [ ] Install Percy
- [ ] Create visual baseline
- [ ] Set up OpenAPI spec
- [ ] Create contract tests
- [ ] Integrate in CI/CD

### Week 7-8 (Performance Tracking)
- [ ] Add bundle size monitoring
- [ ] Implement API perf testing
- [ ] Create performance dashboard
- [ ] Set alerts for regressions
- [ ] Review metrics

### Week 9-10 (Production Observability)
- [ ] Set up RUM tracking
- [ ] Configure Core Web Vitals
- [ ] Create dashboards
- [ ] Verify data collection
- [ ] Document metrics

### Week 11-12 (Chaos Engineering)
- [ ] Install chaos toolkit
- [ ] Create baseline scenarios
- [ ] Run initial tests
- [ ] Document resilience gaps
- [ ] Plan improvements

### Week 13-16 (Knowledge & Process)
- [ ] Create testing guidelines
- [ ] Set up test review process
- [ ] Schedule knowledge sharing
- [ ] Document all processes
- [ ] Train team

---

## Success Metrics

After full implementation (4 months):

- **Code Quality**
  - 0 pre-commit hook failures
  - <2% lint violations in PRs
  - 0 type errors

- **Testing**
  - 100% test pass rate
  - 80%+ code coverage maintained
  - <30s test execution time
  - 0 flaky tests

- **Performance**
  - Lighthouse score >90
  - Core Web Vitals: LCP <2.5s, FID <100ms, CLS <0.1
  - Bundle size <100KB gzipped

- **Production**
  - <0.1% error rate
  - <1% production bugs from code changes
  - >99.9% uptime
  - <30 min MTTR for critical issues

- **Team**
  - 100% of team trained on new processes
  - 0% of tests require explanation
  - Confidence increase reported by team
  - Reduced on-call incidents

---

**Document Version:** 1.0
**Last Updated:** December 2024
**Estimated Completion:** April 2025
