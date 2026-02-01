# QA Systems API Integration Patterns
## Technical Deep Dive into GitHub, TestRail, and Real-Time APIs

---

## 1. GitHub Checks API Deep Dive

### 1.1 Check Suite Creation (Automatic)

When a commit is pushed to GitHub, a check suite is automatically created if GitHub Apps with check permissions are installed.

```typescript
// Check Suite Structure
interface CheckSuite {
  id: number;
  head_sha: string;              // Commit SHA
  status: 'queued' | 'in_progress' | 'completed';
  conclusion: 'success' | 'failure' | 'neutral' | 'cancelled' | 'skipped' | 'timed_out' | 'action_required';
  app: App;
  created_at: string;
  updated_at: string;
  check_runs_url: string;
  url: string;
  before: string;
  after: string;
  pull_requests: Array<{
    id: number;
    number: number;
    head: { sha: string };
    base: { sha: string };
  }>;
}
```

### 1.2 Check Run Creation & Updates

```typescript
// Create a new check run
const checkRun = await github.rest.checks.create({
  owner: 'my-org',
  repo: 'my-repo',
  name: 'Playwright Tests',
  head_sha: 'abc123def456',

  // Optional: Specify check suite
  check_suite_id: 12345,

  // Status must be one of: queued, in_progress, completed
  status: 'in_progress',

  // Only relevant when status === 'in_progress'
  started_at: new Date().toISOString(),

  // Conclusion only relevant when status === 'completed'
  conclusion: 'success',
  completed_at: new Date().toISOString(),

  // Rich output
  output: {
    title: '12/50 tests passed',
    summary: `## Test Summary

| Metric | Value |
|--------|-------|
| Passed | 12 |
| Failed | 1 |
| Skipped | 37 |
| Duration | 2.5 minutes |
| Coverage | 85% |
`,
    text: 'Additional raw text output',

    // Annotations - appear inline in PR diffs
    annotations: [
      {
        path: 'src/components/Login.test.tsx',
        start_line: 45,
        end_line: 47,
        annotation_level: 'failure',  // 'notice', 'warning', 'failure'
        title: 'Test assertion failed',
        message: 'Expected email field to be visible',
        raw_details: 'Full error stack trace...'
      }
    ],

    // Embedded images and links
    images: [
      {
        alt: 'Screenshot of failure',
        image_url: 'https://example.com/failure.png',
        caption: 'Screenshot showing missing element'
      }
    ]
  },

  // External reference (e.g., CI build ID)
  external_id: 'build-12345',

  // Link to details page
  details_url: 'https://ci.example.com/builds/12345',

  // Request action from users
  actions: [
    {
      label: 'Fix This',
      description: 'Automatically fix the test',
      identifier: 'fix_test'
    }
  ]
});
```

### 1.3 Check Run Update Workflow

```typescript
// Workflow: Update check run with test progress

// 1. Create check run with initial status
const checkRun = await github.rest.checks.create({
  owner, repo, head_sha,
  name: 'Playwright Tests',
  status: 'in_progress',
  started_at: new Date().toISOString()
});

// 2. Run tests and collect events
const events = [];
testRunner.on('test:complete', (test, result) => {
  events.push({
    testId: test.id,
    status: result.status,
    duration: result.duration,
    error: result.error
  });
});

// 3. Periodically update check run with progress
const progressInterval = setInterval(async () => {
  const stats = calculateStats(events);

  await github.rest.checks.update({
    owner, repo,
    check_run_id: checkRun.data.id,
    status: 'in_progress',
    output: {
      title: `${stats.completed}/${stats.total} tests running...`,
      summary: `Progress: ${Math.round((stats.completed / stats.total) * 100)}%`
    }
  });
}, 10000); // Update every 10 seconds

// 4. Final update with results
clearInterval(progressInterval);
const finalStats = calculateStats(events);
const failures = events.filter(e => e.status === 'failed');

await github.rest.checks.update({
  owner, repo,
  check_run_id: checkRun.data.id,
  status: 'completed',
  conclusion: failures.length > 0 ? 'failure' : 'success',
  completed_at: new Date().toISOString(),
  output: {
    title: `${finalStats.passed}/${finalStats.total} tests passed`,
    summary: generateSummary(finalStats),
    annotations: failures.map(failure => ({
      path: failure.testFile,
      start_line: failure.line,
      annotation_level: 'failure',
      title: `Failed: ${failure.testName}`,
      message: failure.error
    }))
  }
});
```

### 1.4 Retrieve Check Run Results

```typescript
// List all check runs for a commit
const checkRuns = await github.rest.checks.listForRef({
  owner, repo,
  ref: 'main',  // Can be branch, tag, or commit SHA
  status: 'completed',  // Filter by status
  conclusion: 'failure'  // Filter by conclusion
});

// Get specific check run
const checkRun = await github.rest.checks.get({
  owner, repo,
  check_run_id: 12345
});

// Parse results
const testResults = parseCheckRunOutput(checkRun.data.output);
const failedTests = checkRun.data.output.annotations
  .filter(a => a.annotation_level === 'failure')
  .map(a => ({
    file: a.path,
    line: a.start_line,
    title: a.title,
    message: a.message
  }));
```

### 1.5 GitHub Actions Implementation

```yaml
name: Create Check Run

on:
  workflow_run:
    workflows: [Tests]
    types: [completed]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download test results
        uses: actions/download-artifact@v4
        with:
          name: test-results

      - name: Create check run
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(
              fs.readFileSync('test-results.json')
            );

            // Build annotations array
            const annotations = [];
            results.failures.forEach(failure => {
              annotations.push({
                path: failure.file,
                start_line: failure.line,
                end_line: failure.line,
                annotation_level: 'failure',
                title: `Test failed: ${failure.name}`,
                message: failure.error,
                raw_details: failure.stack
              });
            });

            // Create check run
            const checkRun = await github.rest.checks.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              name: 'Test Results',
              head_sha: context.payload.workflow_run.head_sha,
              status: 'completed',
              conclusion: results.failures.length > 0 ? 'failure' : 'success',
              completed_at: new Date().toISOString(),
              output: {
                title: `${results.passed}/${results.total} tests passed`,
                summary: `
                | Status | Count |
                |--------|-------|
                | Passed | ${results.passed} |
                | Failed | ${results.failures.length} |
                | Skipped | ${results.skipped} |
                `,
                annotations: annotations
              }
            });

            console.log('Check run created:', checkRun.data.html_url);
```

---

## 2. GitHub REST API for Test Artifacts

### 2.1 List Repository Contents (For Test Configs)

```typescript
// List test configuration files
const configs = await github.rest.repos.getContent({
  owner, repo,
  path: 'e2e',  // e2e/ directory
  ref: 'main'
});

// Retrieve specific test configuration
const playwrightConfig = await github.rest.repos.getContent({
  owner, repo,
  path: 'playwright.config.ts',
  ref: 'main'
});

// Content is base64-encoded
const configContent = Buffer.from(
  playwrightConfig.data.content,
  'base64'
).toString('utf-8');
```

### 2.2 Commit File Retrieval for Test Mapping

```typescript
// Get all test files changed in a commit
const commit = await github.rest.repos.getCommit({
  owner, repo,
  ref: 'abc123'
});

// Filter for test files
const changedTests = commit.data.files
  .filter(f => f.filename.includes('.test.') || f.filename.includes('.spec.'))
  .map(f => ({
    filename: f.filename,
    status: f.status,  // 'added', 'removed', 'modified'
    additions: f.additions,
    deletions: f.deletions,
    changes: f.changes
  }));

// Trigger tests only for changed files
const testsToRun = changedTests
  .filter(t => t.status !== 'removed')
  .map(t => t.filename.replace(/\.(test|spec)\.[jt]sx?$/, ''));
```

### 2.3 Status Checks (Legacy - Use Checks API Instead)

```typescript
// Create a commit status (older API, less rich)
const status = await github.rest.repos.createCommitStatus({
  owner, repo,
  sha: 'abc123',
  state: 'pending',  // 'pending', 'success', 'error', 'failure'
  context: 'continuous-integration/my-test-suite',
  description: 'Tests are running...',
  target_url: 'https://ci.example.com/build/123'
});

// Get combined status across all checks
const combinedStatus = await github.rest.repos.getCombinedStatusForRef({
  owner, repo,
  ref: 'main'
});

// Combined status shows pass/fail from all CI systems
console.log(combinedStatus.data.state);  // 'success' if all pass
combinedStatus.data.statuses.forEach(status => {
  console.log(status.context, status.state);
});
```

---

## 3. TestRail API Integration

### 3.1 Test Case Management

```typescript
// TestRail configuration
const TESTRAIL_HOST = 'https://testrail.example.com';
const TESTRAIL_USER = 'user@example.com';
const TESTRAIL_PASS = 'api-token';

// Auth header
const auth = Buffer.from(`${TESTRAIL_USER}:${TESTRAIL_PASS}`).toString('base64');
const headers = {
  'Authorization': `Basic ${auth}`,
  'Content-Type': 'application/json'
};

// Create test case
async function createTestCase(projectId, suiteId, sectionId, testData) {
  const response = await fetch(
    `${TESTRAIL_HOST}/index.php?/api/v2/add_case/${sectionId}`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify({
        title: testData.name,
        type_id: 3,  // Automated
        priority_id: 5,
        estimate: '5m',
        refs: testData.requirementId,  // Requirement reference
        custom_execution_type: 2  // Automated execution
      })
    }
  );

  return response.json();  // Returns { id: 123, ... }
}

// Get test case
async function getTestCase(caseId) {
  const response = await fetch(
    `${TESTRAIL_HOST}/index.php?/api/v2/get_case/${caseId}`,
    { headers }
  );

  const testCase = await response.json();
  return {
    id: testCase.id,
    title: testCase.title,
    sectionId: testCase.section_id,
    typeId: testCase.type_id,
    priorityId: testCase.priority_id,
    customFields: testCase.custom_*  // Custom field values
  };
}

// Update test case
async function updateTestCase(caseId, updates) {
  const response = await fetch(
    `${TESTRAIL_HOST}/index.php?/api/v2/update_case/${caseId}`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify(updates)
    }
  );

  return response.json();
}

// List test cases in section
async function listTestCases(sectionId) {
  const response = await fetch(
    `${TESTRAIL_HOST}/index.php?/api/v2/get_cases/${sectionId}`,
    { headers }
  );

  const data = await response.json();
  return data.cases;  // Array of test cases
}
```

### 3.2 Test Run Management

```typescript
// Create test run (execute specific test cases)
async function createTestRun(projectId, suiteId, caseIds) {
  const response = await fetch(
    `${TESTRAIL_HOST}/index.php?/api/v2/add_run/${projectId}`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify({
        name: `Test Run - ${new Date().toISOString()}`,
        suite_id: suiteId,
        case_ids: caseIds,  // Test case IDs to include
        include_all: false,
        milestone_id: 5,  // Optional: associate with milestone
        assignedto_id: 1  // Optional: assign to user
      })
    }
  );

  const run = await response.json();
  return run.id;  // Test run ID for result submission
}

// Add test result
async function addTestResult(runId, caseId, result) {
  const response = await fetch(
    `${TESTRAIL_HOST}/index.php?/api/v2/add_result/${runId}/${caseId}`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify({
        status_id: result.status,  // 1=passed, 5=failed, 3=untested
        comment: result.message,
        elapsed: `${Math.round(result.duration / 1000)}s`,
        defects: result.defects,  // Bug IDs
        version: result.version || 'main',

        // Attachments (screenshots, logs)
        attachment_ids: result.attachmentIds
      })
    }
  );

  return response.json();
}

// Batch add results
async function addTestResults(runId, results) {
  const response = await fetch(
    `${TESTRAIL_HOST}/index.php?/api/v2/add_results/${runId}`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify({
        results: results.map(r => ({
          case_id: r.caseId,
          status_id: r.status,
          comment: r.message,
          elapsed: `${Math.round(r.duration / 1000)}s`,
          defects: r.defects
        }))
      })
    }
  );

  return response.json();
}

// Get test run summary
async function getTestRunSummary(runId) {
  const response = await fetch(
    `${TESTRAIL_HOST}/index.php?/api/v2/get_run/${runId}`,
    { headers }
  );

  const run = await response.json();
  return {
    id: run.id,
    name: run.name,
    passed: run.passed_count,
    failed: run.failed_count,
    blocked: run.blocked_count,
    untested: run.untested_count,
    custom: run.custom_*  // Custom fields
  };
}
```

### 3.3 Automated Test Result Mapping

```typescript
// Map Allure test results to TestRail
async function pushResultsToTestRail(projectId, suiteId, allureResults) {
  // 1. Create test run in TestRail
  const caseIds = allureResults.tests.map(t => {
    // Map Allure test ID to TestRail case ID
    const mapping = {
      'test-login-valid': 123,
      'test-login-invalid': 124,
      'test-dashboard-load': 125
    };
    return mapping[t.id];
  });

  const runId = await createTestRun(projectId, suiteId, caseIds);

  // 2. Push test results
  const results = allureResults.tests.map(test => ({
    case_id: getCaseIdFromMapping(test.id),
    status: test.status === 'passed' ? 1 : 5,  // 1=pass, 5=fail
    comment: test.error || test.message,
    duration: test.duration,
    defects: extractBugIds(test.error)  // Parse bug IDs from error
  }));

  await addTestResults(runId, results);

  return runId;
}

// Requirement traceability (map test to requirement)
async function linkTestToRequirement(caseId, requirementId) {
  return updateTestCase(caseId, {
    refs: requirementId  // e.g., "REQ-123"
  });
}

// Get coverage report
async function getCoverageReport(suiteId) {
  const response = await fetch(
    `${TESTRAIL_HOST}/index.php?/api/v2/get_coverage/${suiteId}`,
    { headers }
  );

  const coverage = await response.json();
  return {
    total: coverage.total,
    covered: coverage.covered,
    percentage: (coverage.covered / coverage.total) * 100
  };
}
```

---

## 4. Real-Time WebSocket APIs

### 4.1 WebSocket Server Implementation

```typescript
import express from 'express';
import { WebSocketServer } from 'ws';
import { Server as HttpServer } from 'http';
import { v4 as uuidv4 } from 'uuid';

interface Client {
  id: string;
  ws: WebSocket;
  filters?: {
    projectId?: string;
    suiteName?: string;
    status?: string;
  };
}

class TestDashboardServer {
  private httpServer: HttpServer;
  private wss: WebSocketServer;
  private clients = new Map<string, Client>();
  private eventHistory: TestEvent[] = [];
  private maxHistorySize = 10000;

  constructor(port: number = 3000) {
    const app = express();
    this.httpServer = app.listen(port, () => {
      console.log(`Server running on port ${port}`);
    });

    this.wss = new WebSocketServer({ server: this.httpServer });
    this.setupWebSocket();
    this.setupRoutes(app);
  }

  private setupWebSocket() {
    this.wss.on('connection', (ws) => {
      const clientId = uuidv4();
      const client: Client = { id: clientId, ws, filters: {} };
      this.clients.set(clientId, client);

      console.log(`[WS] Client connected: ${clientId}`);

      // Send recent events to new client
      this.sendHistoryToClient(client);

      // Handle client messages (filters, commands)
      ws.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString());
          this.handleClientMessage(client, message);
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      });

      // Clean up on disconnect
      ws.on('close', () => {
        this.clients.delete(clientId);
        console.log(`[WS] Client disconnected: ${clientId}`);
      });

      ws.on('error', (error) => {
        console.error(`[WS] Client error (${clientId}):`, error);
        this.clients.delete(clientId);
      });
    });
  }

  private setupRoutes(app: express.Application) {
    app.use(express.json());

    // Receive individual test event
    app.post('/api/test-event', (req, res) => {
      const event: TestEvent = {
        id: uuidv4(),
        timestamp: Date.now(),
        ...req.body
      };

      this.storeEvent(event);
      this.broadcastEvent(event);

      res.json({ status: 'received', eventId: event.id });
    });

    // Batch event submission (more efficient)
    app.post('/api/batch-events', (req, res) => {
      const events = req.body.events || [];
      const storedEvents = [];

      events.forEach(eventData => {
        const event: TestEvent = {
          id: uuidv4(),
          timestamp: Date.now(),
          ...eventData
        };

        this.storeEvent(event);
        storedEvents.push(event);
      });

      // Broadcast all events
      storedEvents.forEach(e => this.broadcastEvent(e));

      res.json({
        status: 'received',
        count: storedEvents.length
      });
    });

    // Get aggregated statistics
    app.get('/api/stats', (req, res) => {
      const stats = this.calculateStats();
      res.json(stats);
    });

    // Get event history (for recovery/replay)
    app.get('/api/history', (req, res) => {
      const { limit = 100, offset = 0, type } = req.query;

      let events = this.eventHistory;
      if (type) {
        events = events.filter(e => e.type === type);
      }

      const paginated = events.slice(offset, offset + limit);
      res.json({
        events: paginated,
        total: events.length
      });
    });

    // Health check
    app.get('/health', (req, res) => {
      res.json({
        status: 'ok',
        connectedClients: this.clients.size,
        eventCount: this.eventHistory.length
      });
    });
  }

  private handleClientMessage(client: Client, message: any) {
    switch (message.type) {
      case 'set-filters':
        // Client specifies what events to receive
        client.filters = message.filters;
        this.sendMessage(client, {
          type: 'filters-updated',
          filters: client.filters
        });
        break;

      case 'request-history':
        // Client requests event history
        this.sendHistoryToClient(client);
        break;

      case 'ping':
        // Keep-alive ping
        this.sendMessage(client, { type: 'pong' });
        break;
    }
  }

  private storeEvent(event: TestEvent) {
    this.eventHistory.push(event);

    // Maintain size limit
    if (this.eventHistory.length > this.maxHistorySize) {
      this.eventHistory = this.eventHistory.slice(-this.maxHistorySize);
    }

    // Persist to database (optional)
    this.persistEvent(event);
  }

  private broadcastEvent(event: TestEvent) {
    const message = JSON.stringify(event);

    // Send to all connected clients that match filters
    this.clients.forEach((client) => {
      if (this.matchesFilters(event, client.filters)) {
        this.sendMessage(client, event);
      }
    });
  }

  private sendMessage(client: Client, message: any) {
    if (client.ws.readyState === 1) { // OPEN
      try {
        client.ws.send(JSON.stringify(message));
      } catch (error) {
        console.error(`Failed to send message to ${client.id}:`, error);
      }
    }
  }

  private sendHistoryToClient(client: Client) {
    // Send recent events on connection for state recovery
    const recentEvents = this.eventHistory.slice(-100);
    this.sendMessage(client, {
      type: 'history',
      events: recentEvents
    });
  }

  private matchesFilters(event: TestEvent, filters?: any): boolean {
    if (!filters) return true;

    if (filters.projectId && event.projectId !== filters.projectId) {
      return false;
    }

    if (filters.suiteName && event.suiteName !== filters.suiteName) {
      return false;
    }

    if (filters.status && event.status !== filters.status) {
      return false;
    }

    return true;
  }

  private calculateStats() {
    const stats = {
      totalTests: 0,
      passed: 0,
      failed: 0,
      running: 0,
      totalDuration: 0,
      startTime: null,
      endTime: null
    };

    const statusMap = new Map<string, number>();

    this.eventHistory.forEach(event => {
      if (event.type === 'test:complete') {
        stats.totalTests++;
        if (event.status === 'passed') stats.passed++;
        else if (event.status === 'failed') stats.failed++;
        stats.totalDuration += event.duration || 0;
      } else if (event.type === 'test:start') {
        if (!stats.startTime) stats.startTime = event.timestamp;
      } else if (event.type === 'suite:complete') {
        stats.endTime = event.timestamp;
      }
    });

    return stats;
  }

  private async persistEvent(event: TestEvent) {
    // Store in database for long-term retention
    // Example: MongoDB, PostgreSQL, etc.
    // This is optional but recommended for analytics
  }
}

// Event type definition
interface TestEvent {
  id: string;
  type: 'test:start' | 'test:assertion' | 'test:complete' | 'suite:complete';
  timestamp: number;
  testId: string;
  testName: string;
  suiteName?: string;
  projectId?: string;
  status?: 'passed' | 'failed' | 'skipped';
  duration?: number;
  error?: string;
  screenshot?: string;
  assertions?: number;
  [key: string]: any;
}

export { TestDashboardServer, TestEvent };
```

### 4.2 React Client Implementation

```typescript
import { useEffect, useReducer, useCallback } from 'react';

interface DashboardState {
  tests: Map<string, TestNode>;
  stats: {
    total: number;
    passed: number;
    failed: number;
    running: number;
  };
  isConnected: boolean;
  autoScroll: boolean;
}

type DashboardAction =
  | { type: 'test:start'; test: TestNode }
  | { type: 'test:assertion'; testId: string; passed: number; total: number }
  | { type: 'test:complete'; testId: string; result: TestResult }
  | { type: 'ws:connected' }
  | { type: 'ws:disconnected' }
  | { type: 'history'; events: TestEvent[] };

interface TestNode {
  id: string;
  name: string;
  status: 'running' | 'passed' | 'failed' | 'skipped';
  duration?: number;
  progress: number;
  error?: string;
  startTime: number;
}

interface TestResult {
  status: 'passed' | 'failed' | 'skipped';
  duration: number;
  error?: string;
  screenshot?: string;
}

const initialState: DashboardState = {
  tests: new Map(),
  stats: { total: 0, passed: 0, failed: 0, running: 0 },
  isConnected: false,
  autoScroll: true
};

function dashboardReducer(
  state: DashboardState,
  action: DashboardAction
): DashboardState {
  switch (action.type) {
    case 'test:start': {
      const tests = new Map(state.tests);
      tests.set(action.test.id, action.test);
      return {
        ...state,
        tests,
        stats: { ...state.stats, running: state.stats.running + 1 }
      };
    }

    case 'test:assertion': {
      const test = state.tests.get(action.testId);
      if (test) {
        const newTest = {
          ...test,
          progress: Math.round((action.passed / action.total) * 100)
        };
        const tests = new Map(state.tests);
        tests.set(action.testId, newTest);
        return { ...state, tests };
      }
      return state;
    }

    case 'test:complete': {
      const test = state.tests.get(action.testId);
      if (test) {
        const newTest = {
          ...test,
          status: action.result.status,
          duration: action.result.duration,
          error: action.result.error,
          progress: 100
        };
        const tests = new Map(state.tests);
        tests.set(action.testId, newTest);

        let passed = state.stats.passed;
        let failed = state.stats.failed;

        if (action.result.status === 'passed') passed++;
        else if (action.result.status === 'failed') failed++;

        return {
          ...state,
          tests,
          stats: {
            total: state.stats.total + 1,
            passed,
            failed,
            running: Math.max(0, state.stats.running - 1)
          }
        };
      }
      return state;
    }

    case 'ws:connected':
      return { ...state, isConnected: true };

    case 'ws:disconnected':
      return { ...state, isConnected: false };

    case 'history': {
      // Replay history events to restore state
      let newState = state;
      action.events.forEach(event => {
        if (event.type === 'test:start') {
          newState = dashboardReducer(newState, {
            type: 'test:start',
            test: {
              id: event.testId,
              name: event.testName,
              status: 'running',
              progress: 0,
              startTime: event.timestamp
            }
          });
        } else if (event.type === 'test:complete') {
          newState = dashboardReducer(newState, {
            type: 'test:complete',
            testId: event.testId,
            result: {
              status: event.status as any,
              duration: event.duration || 0,
              error: event.error
            }
          });
        }
      });
      return newState;
    }

    default:
      return state;
  }
}

export function Dashboard() {
  const [state, dispatch] = useReducer(dashboardReducer, initialState);
  const ws = useRef<WebSocket | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Connect to WebSocket server
    const wsUrl = `ws://${window.location.host}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      dispatch({ type: 'ws:connected' });
      console.log('WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case 'history':
          dispatch({ type: 'history', events: message.events });
          break;

        case 'test:start':
          dispatch({
            type: 'test:start',
            test: {
              id: message.testId,
              name: message.testName,
              status: 'running',
              progress: 0,
              startTime: message.timestamp
            }
          });
          break;

        case 'test:assertion':
          dispatch({
            type: 'test:assertion',
            testId: message.testId,
            passed: message.passed,
            total: message.total
          });
          break;

        case 'test:complete':
          dispatch({
            type: 'test:complete',
            testId: message.testId,
            result: {
              status: message.status,
              duration: message.duration,
              error: message.error
            }
          });
          break;
      }
    };

    ws.current.onclose = () => {
      dispatch({ type: 'ws:disconnected' });
      console.log('WebSocket disconnected');

      // Attempt reconnection
      setTimeout(() => {
        window.location.reload();
      }, 5000);
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, []);

  // Auto-scroll to latest test
  useEffect(() => {
    if (state.autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [state.tests, state.autoScroll]);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Test Execution Dashboard</h1>
        <div className="metrics">
          <div className={`metric ${state.isConnected ? 'connected' : 'disconnected'}`}>
            {state.isConnected ? '● Connected' : '● Disconnected'}
          </div>
          <div className="metric">Passed: {state.stats.passed}</div>
          <div className="metric">Failed: {state.stats.failed}</div>
          <div className="metric">Running: {state.stats.running}</div>
        </div>
      </header>

      <div className="dashboard-content" ref={containerRef}>
        {Array.from(state.tests.values()).map(test => (
          <TestNodeComponent key={test.id} test={test} />
        ))}
      </div>
    </div>
  );
}

function TestNodeComponent({ test }: { test: TestNode }) {
  const statusColor = {
    running: '#3498db',
    passed: '#2ecc71',
    failed: '#e74c3c',
    skipped: '#95a5a6'
  }[test.status];

  return (
    <div className="test-node" style={{ borderLeftColor: statusColor }}>
      <div className="test-header">
        <span className="test-status">{test.status}</span>
        <span className="test-name">{test.name}</span>
        {test.duration && <span className="test-duration">{test.duration}ms</span>}
      </div>
      {test.status === 'running' && (
        <div className="test-progress">
          <div className="progress-bar" style={{ width: `${test.progress}%` }} />
        </div>
      )}
      {test.error && (
        <div className="test-error">{test.error}</div>
      )}
    </div>
  );
}
```

---

## 5. Error Handling & Retry Strategies

### 5.1 Resilient GitHub API Client

```typescript
class GitHubAPIClient {
  private maxRetries = 3;
  private baseDelay = 1000; // ms

  async createCheckRun(params: any, retries = 0): Promise<any> {
    try {
      const response = await fetch(
        'https://api.github.com/repos/owner/repo/check-runs',
        {
          method: 'POST',
          headers: {
            'Authorization': `token ${process.env.GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github+json'
          },
          body: JSON.stringify(params)
        }
      );

      if (response.status === 429) {
        // Rate limited
        const resetTime = parseInt(response.headers.get('X-RateLimit-Reset') || '0');
        const delayMs = (resetTime * 1000) - Date.now();
        console.log(`Rate limited, waiting ${delayMs}ms`);
        await new Promise(r => setTimeout(r, delayMs));
        return this.createCheckRun(params, retries);
      }

      if (response.status >= 500) {
        // Server error, retry
        if (retries < this.maxRetries) {
          const delay = this.baseDelay * Math.pow(2, retries);
          console.log(`Server error, retrying in ${delay}ms`);
          await new Promise(r => setTimeout(r, delay));
          return this.createCheckRun(params, retries + 1);
        }
        throw new Error(`Server error after ${this.maxRetries} retries`);
      }

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`API Error: ${response.status} - ${error}`);
      }

      return response.json();
    } catch (error) {
      if (retries < this.maxRetries && this.isRetryable(error)) {
        const delay = this.baseDelay * Math.pow(2, retries);
        console.log(`Request failed, retrying in ${delay}ms`);
        await new Promise(r => setTimeout(r, delay));
        return this.createCheckRun(params, retries + 1);
      }
      throw error;
    }
  }

  private isRetryable(error: any): boolean {
    // Network errors are retryable
    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
      return true;
    }

    // Certain status codes are retryable
    if (error.status && [408, 429, 500, 502, 503, 504].includes(error.status)) {
      return true;
    }

    return false;
  }
}
```

---

## 6. Integration Testing Checklist

### 6.1 Test Your Integration

```typescript
// test/github-integration.test.ts
describe('GitHub Checks Integration', () => {
  it('should create check run on test completion', async () => {
    const mockResults = {
      passed: 45,
      failed: 2,
      total: 50
    };

    const checkRun = await createCheckRun({
      head_sha: 'abc123',
      conclusion: 'failure',
      output: {
        title: `${mockResults.passed}/${mockResults.total} tests passed`
      }
    });

    expect(checkRun.id).toBeDefined();
    expect(checkRun.status).toBe('completed');
  });

  it('should handle rate limiting gracefully', async () => {
    // Test retry logic with mocked rate limit response
  });

  it('should add annotations for failed tests', async () => {
    const annotations = [
      {
        path: 'src/Login.test.tsx',
        start_line: 45,
        annotation_level: 'failure',
        message: 'Expected element not found'
      }
    ];

    const result = await addAnnotations(checkRunId, annotations);
    expect(result.annotations.length).toBe(1);
  });
});
```

---

**Document Version:** 1.0
**Last Updated:** January 28, 2026

