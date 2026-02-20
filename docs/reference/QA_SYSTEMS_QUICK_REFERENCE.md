# QA Systems Quick Reference Guide
## Essential Patterns & Implementation Checklist

---

## 1. Test Execution Environment Setup

### Docker-Based Isolation
```dockerfile
# Dockerfile for Playwright tests
FROM mcr.microsoft.com/playwright:v1.45.0-noble

WORKDIR /app
COPY package.json .
RUN npm install

COPY . .
CMD ["npx", "playwright", "test"]
```

**Key Config Values:**
- Shared memory: `--shm-size=1gb` (for browser rendering)
- Network: `--network=host` (direct access) or `bridge` (isolated)
- Volume mounts: Test code, artifacts, configurations
- CPU/Memory: 2 CPUs, 4GB RAM per container minimum

### GitHub Actions Parallel Execution
```yaml
strategy:
  matrix:
    shard: [1/4, 2/4, 3/4, 4/4]  # Creates 4 parallel jobs
    os: [ubuntu-latest]

steps:
  - run: npx playwright test --shard=${{ matrix.shard }}
```

**Speed Benefits:**
- 4 shards = ~3.8x faster (200s → 50s for large suites)
- Linear scaling up to 10-15 shards
- Beyond that: network/scheduler overhead dominates

---

## 2. Visual Artifact Capture & Storage

### Screenshot Capture Best Practices

**Playwright (Recommended)**
```typescript
// On every test failure only
await page.screenshot({
  path: `failures/${testName}.png`,
  fullPage: true,
  mask: [page.locator('[data-sensitive]')] // blur PII
});

// Trace recording for advanced debugging
await context.tracing.start({
  screenshots: true,
  snapshots: true
});
// ... test ...
await context.tracing.stop({ path: 'trace.zip' });
```

**Cypress (Video-based)**
```javascript
// video: true in cypress.config.js
// But prefer: videoOnFailOnly: true (save bandwidth)

Cypress.Video.compressVideo({
  quality: 75,
  compression: 51 // H.264 quality parameter
});
```

### Artifact Storage Strategy

| Artifact | Retention | Storage | Compression |
|----------|-----------|---------|-------------|
| Failing test screenshots | 90 days | S3 or GitHub | PNG |
| Passing test videos | 7 days | GitHub (auto-cleanup) | H.264 51% |
| Test traces | 30 days | S3 (expensive!) | ZIP |
| Test logs | 180 days | Elasticsearch/CloudWatch | JSON |
| Coverage reports | 365 days | Permanent storage | GZIP |

**Cost Optimization:**
- GitHub Actions: ~$0.50/GB/month (after free tier)
- S3 Standard: ~$0.023/GB/month (+ $0.09/GB data transfer)
- Lifecycle rules: Auto-delete after 90 days

---

## 3. Visual Regression Testing Approach Selection

### Decision Tree

```
START: Need visual regression testing?
  ├─ YES: Is it a design system / component library?
  │   ├─ YES → Use Chromatic + Storybook
  │   │   (Cost: $29+/month)
  │   └─ NO → Continue below
  │
  └─ For Web Applications:
      ├─ Budget conscious?
      │   ├─ YES → Playwright with DOM snapshots
      │   │   (Build custom with Percy SDK)
      │   └─ NO → Use Percy.io
      │       (Cost: $199+/month, 5k screenshots/mo free)
      │
      └─ Heavy visual requirements?
          ├─ YES → Applitools (AI-based, most accurate)
          │   (Cost: $500+/month)
          └─ NO → Perceptual hashing libraries
              (Free: djinni, phash, dHash)
```

### Algorithm Comparison

```
Pixel Diff:
✓ Fast, simple
✗ 50% false positives (rendering variance)
→ Use for: Unit-level component testing only

Perceptual Hash (pHash/dHash):
✓ Tolerant of compression, minor rendering changes
✓ Very fast (~0.5s per image)
✗ Moderate false negatives (~5%)
→ Use for: Full page regression testing

DOM-Based (Percy approach):
✓ Immune to rendering timing differences
✓ Multi-browser comparison built-in
✗ Slower, requires re-rendering
→ Use for: Critical user paths, design system changes

AI-Based (Applitools):
✓ Highest accuracy, human-like perception
✗ Expensive, slower
→ Use for: Enterprise applications with high visual complexity
```

---

## 4. GitHub Integration Checklist

### Check Runs API (For PR Status)

```javascript
// 1. Create check run for test suite
github.rest.checks.create({
  owner: context.repo.owner,
  repo: context.repo.repo,
  name: 'Playwright Tests',
  head_sha: context.sha,
  status: 'completed',
  conclusion: testResults.failed > 0 ? 'failure' : 'success',
  output: {
    title: `${testResults.passed}/${testResults.total} tests passed`,
    summary: generateMarkdownSummary(testResults)
  }
});

// 2. Optional: Add annotations for failures
testResults.failures.forEach(failure => {
  annotations.push({
    path: failure.testFile,
    start_line: failure.line,
    title: `Test Failed: ${failure.testName}`,
    message: failure.error,
    annotation_level: 'failure'
  });
});
```

**Result:** Status appears in PR "Checks" tab with:
- Pass/fail conclusion
- Rich summary with metrics
- Line-specific annotations (if provided)
- External links (to Allure report, artifacts, etc.)

### Artifact Storage & Retention

```yaml
- uses: actions/upload-artifact@v6
  with:
    name: test-results-${{ matrix.shard }}
    path: |
      playwright-report/
      test-results/
    retention-days: 30
    compression-level: 6  # Balance speed vs. size
    overwrite: true       # Replace if re-run
```

**Free Tier:** 500MB storage, 90 days retention
**Paid:** $0.50/GB/month beyond free tier

---

## 5. Node Graph Visualization Patterns

### Test Hierarchy Node Styling

```javascript
// Color by status
function getNodeColor(test) {
  const passRate = test.passed / test.total;
  if (passRate === 1.0) return '#27ae60';      // Green
  if (passRate >= 0.8) return '#f39c12';       // Amber
  if (passRate >= 0.5) return '#e67e22';       // Orange
  return '#c0392b';                            // Red
}

// Size by test count or execution time
function getNodeRadius(test) {
  return Math.sqrt(test.testCount) * 5;
  // OR: Math.log(test.duration) * 3;
}

// Stroke width by priority/criticality
function getStrokeWidth(test) {
  if (test.priority === 'critical') return 3;
  if (test.priority === 'high') return 2;
  return 1;
}
```

### D3 Hierarchy Quick Setup

```javascript
import { hierarchy, tree } from 'd3-hierarchy';

const data = {
  name: "All Tests",
  children: [
    { name: "Auth", status: "passed", testCount: 24 },
    { name: "Dashboard", status: "failed", testCount: 18 }
  ]
};

const svg = d3.select('svg');
const root = hierarchy(data).sort((a,b) => b.value - a.value);
const layout = tree().size([width, height]);
const treeData = layout(root);

// Draw links
svg.selectAll('line')
  .data(treeData.links())
  .enter()
  .append('line')
  .attr('x1', d => d.source.x)
  .attr('y1', d => d.source.y)
  .attr('x2', d => d.target.x)
  .attr('y2', d => d.target.y)
  .attr('stroke', '#ccc');

// Draw nodes
svg.selectAll('circle')
  .data(treeData.descendants())
  .enter()
  .append('circle')
  .attr('cx', d => d.x)
  .attr('cy', d => d.y)
  .attr('r', d => getNodeRadius(d.data))
  .attr('fill', d => getNodeColor(d.data));
```

---

## 6. Real-Time Dashboard via WebSocket

### Server (Node.js + Express)

```typescript
import { WebSocketServer } from 'ws';
import express from 'express';

const app = express();
const wss = new WebSocketServer({ server });
const clients = new Set();

// Receive test events from CI system
app.post('/api/test-event', (req, res) => {
  const event = req.body;

  // Broadcast to all connected dashboard clients
  clients.forEach(client => {
    if (client.readyState === 1) { // OPEN
      client.send(JSON.stringify(event));
    }
  });

  res.json({ ok: true });
});

wss.on('connection', (ws) => {
  clients.add(ws);
  ws.on('close', () => clients.delete(ws));
});
```

### Client (React)

```typescript
import { useEffect, useState } from 'react';

export function Dashboard() {
  const [tests, setTests] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:3000');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'test:start') {
        setTests(prev => [...prev, { ...data, status: 'running' }]);
      } else if (data.type === 'test:complete') {
        setTests(prev => prev.map(t =>
          t.id === data.id ? { ...t, status: data.status, duration: data.duration } : t
        ));
      }
    };

    return () => ws.close();
  }, []);

  return (
    <div>
      {tests.map(test => (
        <TestNode key={test.id} test={test} />
      ))}
    </div>
  );
}
```

**Performance:** 50-70ms latency vs 500ms for polling

---

## 7. Test Result Aggregation Pattern

### Multi-Job Merging (GitHub Actions)

```yaml
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - run: npx playwright test --shard=${{ matrix.shard }}/4
      - uses: actions/upload-artifact@v6
        with:
          name: results-${{ matrix.shard }}
          path: test-results/

  merge:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          path: all-results/

      # Merge Junit XML files
      - run: |
          npx junit-merge \
            all-results/*/results.xml \
            > merged-results.xml

      # Generate HTML report
      - run: npx allure generate merged-results.xml
```

### Gradle Multi-Module Aggregation

```gradle
plugins {
  id 'test-report-aggregation'
}

dependencies {
  testReportAggregation project(':app-backend')
  testReportAggregation project(':app-frontend')
}

tasks.named('testAggregateTestReport') {
  testResults.from(
    project(':app-backend').tasks.test,
    project(':app-frontend').tasks.test
  )
}
```

---

## 8. Allure Report Integration

### Pytest Configuration

```python
# conftest.py
import allure

@pytest.fixture(autouse=True)
def screenshot_on_failure(request):
    """Attach screenshot on test failure"""
    yield
    if request.node.rep_call.failed:
        driver = request.getfixturevalue("selenium_driver")
        allure.attach(
            driver.get_screenshot_as_png(),
            name="failure-screenshot",
            attachment_type=allure.attachment_type.PNG
        )

@allure.step
def login_user(username, password):
    """Login step with automatic allure reporting"""
    # ... login logic ...
```

### Pytest CLI

```bash
# Run with Allure reporting
pytest tests/ \
  --alluredir=allure-results \
  --durations=10  # Slowest 10 tests

# Generate Allure report
allure serve allure-results

# OR: Generate static report
allure generate allure-results -o allure-report
```

### Playwright Configuration

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [
    ['html', { outputFolder: 'test-results' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['list'],
    [require.resolve('@ashyantony/allure-playwright/reporter'), {}]
  ]
});
```

---

## 9. Platform Selection Matrix

### Execution Environment

| Need | Best Choice | Alternative |
|------|-------------|-------------|
| Small team, simple tests | GitHub Actions | CircleCI free tier |
| Multi-browser testing | BrowserStack Live | Sauce Labs |
| Component testing | Chromatic + Storybook | Percy |
| High-scale (1000+ tests) | Kubernetes + Docker | CircleCI parallelism |

### Test Management

| Org Size | Best Choice | Cost |
|----------|-------------|------|
| <5 people | Allure Report (free) + Qase free tier | $0 |
| 5-20 people | Qase.io | $99-199/mo |
| 20-100 people | TestRail | $399-999/mo |
| 100+ people | TestRail Enterprise + custom integration | $5000+/mo |

### Visual Regression

| Requirement | Best Choice | Cost |
|-------------|-------------|------|
| Design system components | Chromatic | $29+/mo |
| Web app (budget) | Playwright + Percy SDK | Free-$199/mo |
| Enterprise | Applitools | $500+/mo |

---

## 10. Implementation Checklist

### Phase 1: Basic Setup (Week 1)
- [ ] Create Dockerfile with Playwright
- [ ] Setup GitHub Actions workflow with matrix
- [ ] Configure artifact upload (30-day retention)
- [ ] Add Allure report generation
- [ ] Create basic dashboard view

### Phase 2: Visual Regression (Week 2)
- [ ] Decide on visual regression approach
- [ ] Integrate Percy SDK or perceptual hashing
- [ ] Configure baseline screenshots
- [ ] Setup approval workflow for visual changes

### Phase 3: Aggregation & Reporting (Week 3)
- [ ] Implement test result merger (Junit XML)
- [ ] Setup GitHub Checks API integration
- [ ] Create merged HTML report
- [ ] Add code coverage tracking

### Phase 4: Real-Time Dashboard (Week 4)
- [ ] Build WebSocket server for live events
- [ ] Create React dashboard component
- [ ] Implement test node graph visualization
- [ ] Add coverage matrix view

### Phase 5: Scale & Optimize (Week 5+)
- [ ] Optimize artifact storage (S3 lifecycle rules)
- [ ] Implement test sharding across more jobs
- [ ] Setup Kubernetes deployment (if needed)
- [ ] Integrate with TestRail or custom test management

---

## 11. Performance Targets

```
Target Metrics for Enterprise QA System:

Test Execution:
├─ Suite completion: < 5 minutes (with 4 shards)
├─ Per-test average: < 10 seconds
└─ Test flakiness: < 1% (retries allowed)

Artifact Upload:
├─ Video (500MB): < 30 seconds
├─ Screenshots: < 5 seconds
└─ Traces: < 10 seconds

Dashboard:
├─ Test status update: < 50ms latency
├─ Node render: < 100ms
├─ Report load: < 2 seconds
└─ WebSocket connection: < 100ms

Visual Regression:
├─ Screenshot comparison: < 0.5 seconds
├─ Diff generation: < 1 second
└─ Report generation: < 5 seconds
```

---

## 12. Troubleshooting Guide

### Problem: Test timeouts in Docker
**Solution:** Increase container resources
```bash
docker run --cpus="2" --memory="4g" playwright-test
```

### Problem: Flaky visual regression tests
**Solution:** Use perceptual hashing, increase threshold
```typescript
// Example: Percy tolerance setting
percy.snapshot(page, { widths: [1280, 375], minHeight: 1024 });
```

### Problem: Slow artifact uploads
**Solution:** Compress, parallelize, use faster network
```yaml
compression-level: 9  # Maximum compression
# OR: Upload to S3 directly (faster than GitHub)
```

### Problem: Dashboard WebSocket disconnections
**Solution:** Implement reconnection logic
```typescript
const ws = new ReconnectingWebSocket('ws://server');
ws.retryCount = 5;
ws.timeoutInterval = 5000;
```

### Problem: High storage costs
**Solution:** Implement aggressive retention policies
```
Screenshots: Keep 30 days
Videos: Keep 7 days (passing), 90 days (failing)
Traces: Keep 30 days (failures only)
Logs: Keep 180 days (compressed)
```

---

## 13. Essential Links by Topic

**Execution Environments:**
- [Playwright Docker Docs](https://playwright.dev/docs/docker)
- [GitHub Actions Matrix](https://docs.github.com/actions/writing-workflows/choosing-what-your-workflow-does/running-variations-of-jobs-in-a-workflow)
- [CircleCI Parallelism](https://circleci.com/docs/test/)

**Visual Testing:**
- [Percy Documentation](https://docs.percy.io/)
- [Chromatic Setup Guide](https://www.chromatic.com/)
- [Playwright Visual Testing](https://playwright.dev/docs/test-snapshots)

**Test Management:**
- [TestRail API](https://www.testrail.com/integrations/)
- [Qase Dashboard Docs](https://docs.qase.io/general/analytics/dashboards)
- [Allure Report](https://allurereport.org/)

**Visualization:**
- [D3.js Hierarchy](https://d3js.org/d3-hierarchy/)
- [Socket.io Documentation](https://socket.io/docs/)

---

**Last Updated:** January 28, 2026
**Version:** 1.0 Quick Reference

