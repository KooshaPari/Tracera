// TraceRTM Backend Service Layer Load Testing Suite
// Load testing framework: k6 (https://k6.io/)
//
// Installation:
//   brew install k6  (macOS)
//   sudo snap install k6  (Linux)
//   choco install k6  (Windows)
//
// Running tests:
//   k6 run service_load_test.js                    # Run with default scenario
//   k6 run --env SCENARIO=normal service_load_test.js   # Normal load
//   k6 run --env SCENARIO=peak service_load_test.js     # Peak load
//   k6 run --env SCENARIO=stress service_load_test.js   # Stress test
//   k6 run --env SCENARIO=spike service_load_test.js    # Spike test
//   k6 run --env SCENARIO=soak service_load_test.js     # Soak test
//
// Custom configuration:
//   k6 run --env BASE_URL=https://api.example.com service_load_test.js
//   k6 run --env AUTH_TOKEN=<token> service_load_test.js

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { randomString, randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// ============================================================================
// Configuration
// ============================================================================

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const API_V1 = `${BASE_URL}/api/v1`;
const AUTH_TOKEN = __ENV.AUTH_TOKEN || ''; // Optional: set for authenticated requests
const SCENARIO = __ENV.SCENARIO || 'normal';

// ============================================================================
// Custom Metrics
// ============================================================================

const errorRate = new Rate('errors');
const successRate = new Rate('success');
const latencyTrend = new Trend('latency');
const requestDuration = new Trend('request_duration');
const throughput = new Counter('requests_total');
const activeConnections = new Gauge('active_connections');

// Endpoint-specific metrics
const healthCheckErrors = new Rate('health_check_errors');
const projectErrors = new Rate('project_errors');
const itemErrors = new Rate('item_errors');
const linkErrors = new Rate('link_errors');
const graphErrors = new Rate('graph_errors');
const searchErrors = new Rate('search_errors');

// ============================================================================
// Test Scenarios
// ============================================================================

export const options = {
  scenarios: {
    // Scenario 1: Normal Load (100 req/s)
    normal: {
      executor: 'constant-arrival-rate',
      rate: 100, // 100 requests per second
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: 50,
      maxVUs: 100,
      tags: { scenario: 'normal' },
      exec: 'normalLoad',
    },

    // Scenario 2: Peak Load (1000 req/s)
    peak: {
      executor: 'constant-arrival-rate',
      rate: 1000, // 1000 requests per second
      timeUnit: '1s',
      duration: '3m',
      preAllocatedVUs: 200,
      maxVUs: 500,
      tags: { scenario: 'peak' },
      exec: 'peakLoad',
    },

    // Scenario 3: Stress Test (5000 req/s)
    stress: {
      executor: 'constant-arrival-rate',
      rate: 5000, // 5000 requests per second
      timeUnit: '1s',
      duration: '2m',
      preAllocatedVUs: 500,
      maxVUs: 2000,
      tags: { scenario: 'stress' },
      exec: 'stressTest',
    },

    // Scenario 4: Spike Test (sudden traffic increase)
    spike: {
      executor: 'ramping-arrival-rate',
      startRate: 50,
      timeUnit: '1s',
      stages: [
        { duration: '30s', target: 50 },    // Normal load
        { duration: '10s', target: 3000 },  // Spike to 3000 req/s
        { duration: '1m', target: 3000 },   // Sustain spike
        { duration: '30s', target: 50 },    // Return to normal
      ],
      preAllocatedVUs: 300,
      maxVUs: 1000,
      tags: { scenario: 'spike' },
      exec: 'spikeTest',
    },

    // Scenario 5: Soak Test (sustained load over time)
    soak: {
      executor: 'constant-arrival-rate',
      rate: 200, // 200 requests per second
      timeUnit: '1s',
      duration: '30m', // 30 minutes
      preAllocatedVUs: 100,
      maxVUs: 200,
      tags: { scenario: 'soak' },
      exec: 'soakTest',
    },

    // Scenario 6: Ramp-up Test (gradual increase)
    rampup: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      stages: [
        { duration: '1m', target: 100 },
        { duration: '2m', target: 500 },
        { duration: '2m', target: 1000 },
        { duration: '2m', target: 2000 },
        { duration: '1m', target: 10 },
      ],
      preAllocatedVUs: 200,
      maxVUs: 800,
      tags: { scenario: 'rampup' },
      exec: 'rampupTest',
    },
  },

  // Thresholds for acceptable performance
  thresholds: {
    // Overall error rate should be less than 1%
    'errors': ['rate<0.01'],

    // 95% of requests should be under 500ms
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],

    // Request duration trends
    'request_duration': ['p(50)<200', 'p(95)<500', 'p(99)<1000'],

    // Endpoint-specific error rates
    'health_check_errors': ['rate<0.001'],
    'project_errors': ['rate<0.02'],
    'item_errors': ['rate<0.02'],
    'link_errors': ['rate<0.02'],
    'graph_errors': ['rate<0.05'], // Graph queries may be more complex
    'search_errors': ['rate<0.03'],

    // Check success rate
    'checks': ['rate>0.95'],
  },

  // Resource usage limits
  noConnectionReuse: false,
  userAgent: 'k6-load-test/1.0',
  insecureSkipTLSVerify: true, // For local testing only
};

// ============================================================================
// Helper Functions
// ============================================================================

// Get request headers
function getHeaders() {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  if (AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }

  return headers;
}

// Create test project data
function createProjectData() {
  return {
    name: `Load Test Project ${randomString(8)}`,
    description: 'Generated by load testing suite',
    metadata: {
      test: true,
      timestamp: new Date().toISOString(),
    },
  };
}

// Create test item data
function createItemData(projectId) {
  return {
    project_id: projectId,
    title: `Test Item ${randomString(8)}`,
    type: randomItem(['requirement', 'feature', 'task', 'bug']),
    status: randomItem(['pending', 'in_progress', 'completed']),
    description: 'Generated by load testing suite',
    metadata: {
      test: true,
      priority: randomItem(['low', 'medium', 'high']),
    },
  };
}

// Create test link data
function createLinkData(sourceId, targetId) {
  return {
    source_id: sourceId,
    target_id: targetId,
    type: randomItem(['depends_on', 'implements', 'tests', 'relates_to']),
    metadata: {
      test: true,
    },
  };
}

// Check HTTP response
function checkResponse(response, expectedStatus, metricName) {
  const passed = check(response, {
    [`${metricName}: status is ${expectedStatus}`]: (r) => r.status === expectedStatus,
    [`${metricName}: response time < 1s`]: (r) => r.timings.duration < 1000,
    [`${metricName}: has body`]: (r) => r.body.length > 0,
  });

  errorRate.add(!passed);
  successRate.add(passed);
  latencyTrend.add(response.timings.duration);
  requestDuration.add(response.timings.duration);
  throughput.add(1);

  return passed;
}

// ============================================================================
// Test Data Setup
// ============================================================================

// Global test data (initialized in setup())
let testProjectId = null;
let testItemIds = [];
let testLinkIds = [];

export function setup() {
  console.log('Setting up test data...');

  const headers = getHeaders();

  // Create test project
  const projectResponse = http.post(
    `${API_V1}/projects`,
    JSON.stringify(createProjectData()),
    { headers }
  );

  if (projectResponse.status === 201) {
    const project = JSON.parse(projectResponse.body);
    testProjectId = project.id;
    console.log(`Created test project: ${testProjectId}`);

    // Create test items
    for (let i = 0; i < 10; i++) {
      const itemResponse = http.post(
        `${API_V1}/items`,
        JSON.stringify(createItemData(testProjectId)),
        { headers }
      );

      if (itemResponse.status === 201) {
        const item = JSON.parse(itemResponse.body);
        testItemIds.push(item.id);
      }
    }

    console.log(`Created ${testItemIds.length} test items`);

    // Create test links between items
    for (let i = 0; i < testItemIds.length - 1; i++) {
      const linkResponse = http.post(
        `${API_V1}/links`,
        JSON.stringify(createLinkData(testItemIds[i], testItemIds[i + 1])),
        { headers }
      );

      if (linkResponse.status === 201) {
        const link = JSON.parse(linkResponse.body);
        testLinkIds.push(link.id);
      }
    }

    console.log(`Created ${testLinkIds.length} test links`);
  }

  return {
    projectId: testProjectId,
    itemIds: testItemIds,
    linkIds: testLinkIds,
  };
}

// ============================================================================
// Test Scenarios - Workload Functions
// ============================================================================

// Scenario 1: Normal Load (100 req/s)
export function normalLoad(data) {
  const headers = getHeaders();

  group('Health Check', () => {
    const response = http.get(`${BASE_URL}/health`, { headers });
    const passed = checkResponse(response, 200, 'health_check');
    healthCheckErrors.add(!passed);
  });

  group('Read Operations', () => {
    // List projects
    const projectsResponse = http.get(`${API_V1}/projects`, { headers });
    checkResponse(projectsResponse, 200, 'list_projects');
    projectErrors.add(projectsResponse.status !== 200);

    // List items
    if (data.projectId) {
      const itemsResponse = http.get(`${API_V1}/items?project_id=${data.projectId}`, { headers });
      checkResponse(itemsResponse, 200, 'list_items');
      itemErrors.add(itemsResponse.status !== 200);
    }

    // Get specific item
    if (data.itemIds && data.itemIds.length > 0) {
      const itemId = randomItem(data.itemIds);
      const itemResponse = http.get(`${API_V1}/items/${itemId}`, { headers });
      checkResponse(itemResponse, 200, 'get_item');
      itemErrors.add(itemResponse.status !== 200);
    }
  });

  sleep(1);
}

// Scenario 2: Peak Load (1000 req/s)
export function peakLoad(data) {
  const headers = getHeaders();

  group('Mixed Operations', () => {
    // 70% read, 30% write
    const operation = Math.random();

    if (operation < 0.7) {
      // Read operations
      const readOp = Math.random();

      if (readOp < 0.3) {
        // Get project
        if (data.projectId) {
          const response = http.get(`${API_V1}/projects/${data.projectId}`, { headers });
          checkResponse(response, 200, 'get_project');
          projectErrors.add(response.status !== 200);
        }
      } else if (readOp < 0.6) {
        // Get item
        if (data.itemIds && data.itemIds.length > 0) {
          const itemId = randomItem(data.itemIds);
          const response = http.get(`${API_V1}/items/${itemId}`, { headers });
          checkResponse(response, 200, 'get_item');
          itemErrors.add(response.status !== 200);
        }
      } else if (readOp < 0.8) {
        // List links
        const response = http.get(`${API_V1}/links`, { headers });
        checkResponse(response, 200, 'list_links');
        linkErrors.add(response.status !== 200);
      } else {
        // Graph traversal
        if (data.itemIds && data.itemIds.length > 0) {
          const itemId = randomItem(data.itemIds);
          const response = http.get(`${API_V1}/graph/descendants/${itemId}`, { headers });
          checkResponse(response, 200, 'graph_descendants');
          graphErrors.add(response.status !== 200);
        }
      }
    } else {
      // Write operations
      if (data.projectId) {
        // Create item
        const response = http.post(
          `${API_V1}/items`,
          JSON.stringify(createItemData(data.projectId)),
          { headers }
        );
        checkResponse(response, 201, 'create_item');
        itemErrors.add(response.status !== 201);
      }
    }
  });

  sleep(0.1);
}

// Scenario 3: Stress Test (5000 req/s)
export function stressTest(data) {
  const headers = getHeaders();

  group('High Throughput Operations', () => {
    // Rapid-fire read operations
    const operations = [
      () => http.get(`${BASE_URL}/health`, { headers }),
      () => http.get(`${API_V1}/projects`, { headers }),
      () => http.get(`${API_V1}/items`, { headers }),
      () => http.get(`${API_V1}/links`, { headers }),
    ];

    const op = randomItem(operations);
    const response = op();

    errorRate.add(response.status >= 400);
    successRate.add(response.status < 400);
    latencyTrend.add(response.timings.duration);
    throughput.add(1);
  });

  // Minimal sleep to maximize throughput
  sleep(0.01);
}

// Scenario 4: Spike Test
export function spikeTest(data) {
  const headers = getHeaders();

  group('Spike Load', () => {
    // Mix of all operation types
    const opType = Math.random();

    if (opType < 0.25) {
      // Health check
      const response = http.get(`${BASE_URL}/health`, { headers });
      healthCheckErrors.add(response.status !== 200);
    } else if (opType < 0.50) {
      // List operations
      const response = http.get(`${API_V1}/items`, { headers });
      itemErrors.add(response.status !== 200);
    } else if (opType < 0.75) {
      // Graph operations
      if (data.itemIds && data.itemIds.length > 0) {
        const itemId = randomItem(data.itemIds);
        const response = http.get(`${API_V1}/graph/ancestors/${itemId}`, { headers });
        graphErrors.add(response.status !== 200);
      }
    } else {
      // Search operations
      const response = http.get(`${API_V1}/search?q=test`, { headers });
      searchErrors.add(response.status !== 200);
    }
  });

  sleep(0.05);
}

// Scenario 5: Soak Test (sustained load)
export function soakTest(data) {
  const headers = getHeaders();

  group('Sustained Load Operations', () => {
    // Realistic user workflow

    // 1. List projects
    http.get(`${API_V1}/projects`, { headers });

    // 2. Get project details
    if (data.projectId) {
      http.get(`${API_V1}/projects/${data.projectId}`, { headers });
    }

    // 3. List items in project
    if (data.projectId) {
      http.get(`${API_V1}/items?project_id=${data.projectId}`, { headers });
    }

    // 4. Get item details
    if (data.itemIds && data.itemIds.length > 0) {
      const itemId = randomItem(data.itemIds);
      http.get(`${API_V1}/items/${itemId}`, { headers });
    }

    // 5. Check graph relationships
    if (data.itemIds && data.itemIds.length > 0) {
      const itemId = randomItem(data.itemIds);
      http.get(`${API_V1}/graph/traverse/${itemId}`, { headers });
    }
  });

  sleep(2);
}

// Scenario 6: Ramp-up Test
export function rampupTest(data) {
  const headers = getHeaders();

  group('Gradual Load Increase', () => {
    // All critical endpoints
    const endpoints = [
      { url: `${BASE_URL}/health`, status: 200, metric: healthCheckErrors },
      { url: `${API_V1}/projects`, status: 200, metric: projectErrors },
      { url: `${API_V1}/items`, status: 200, metric: itemErrors },
      { url: `${API_V1}/links`, status: 200, metric: linkErrors },
    ];

    if (data.itemIds && data.itemIds.length > 0) {
      const itemId = randomItem(data.itemIds);
      endpoints.push(
        { url: `${API_V1}/graph/descendants/${itemId}`, status: 200, metric: graphErrors },
        { url: `${API_V1}/graph/ancestors/${itemId}`, status: 200, metric: graphErrors }
      );
    }

    const endpoint = randomItem(endpoints);
    const response = http.get(endpoint.url, { headers });
    endpoint.metric.add(response.status !== endpoint.status);

    checkResponse(response, endpoint.status, 'rampup_test');
  });

  sleep(0.5);
}

// ============================================================================
// Cleanup
// ============================================================================

export function teardown(data) {
  console.log('Cleaning up test data...');

  const headers = getHeaders();

  // Delete test links
  if (data.linkIds) {
    data.linkIds.forEach(linkId => {
      http.del(`${API_V1}/links/${linkId}`, null, { headers });
    });
    console.log(`Deleted ${data.linkIds.length} test links`);
  }

  // Delete test items
  if (data.itemIds) {
    data.itemIds.forEach(itemId => {
      http.del(`${API_V1}/items/${itemId}`, null, { headers });
    });
    console.log(`Deleted ${data.itemIds.length} test items`);
  }

  // Delete test project
  if (data.projectId) {
    http.del(`${API_V1}/projects/${data.projectId}`, null, { headers });
    console.log(`Deleted test project: ${data.projectId}`);
  }
}

// ============================================================================
// Default Export (runs when no scenario is specified)
// ============================================================================

export default function(data) {
  // Run normal load by default
  normalLoad(data);
}

// ============================================================================
// Custom Summary Handler
// ============================================================================

export function handleSummary(data) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const scenario = SCENARIO;

  return {
    [`results/load-test-${scenario}-${timestamp}.json`]: JSON.stringify(data, null, 2),
    stdout: textSummary(data, { indent: '  ', enableColors: true }),
  };
}

function textSummary(data, options = {}) {
  const indent = options.indent || '';
  const enableColors = options.enableColors !== false;

  let summary = `\n${indent}Load Test Summary (${SCENARIO})\n`;
  summary += `${indent}${'='.repeat(60)}\n\n`;

  if (data.metrics.http_reqs) {
    summary += `${indent}Requests:\n`;
    summary += `${indent}  Total: ${data.metrics.http_reqs.values.count}\n`;
    summary += `${indent}  Rate: ${data.metrics.http_reqs.values.rate.toFixed(2)}/s\n\n`;
  }

  if (data.metrics.http_req_duration) {
    summary += `${indent}Response Times:\n`;
    summary += `${indent}  Min: ${data.metrics.http_req_duration.values.min.toFixed(2)}ms\n`;
    summary += `${indent}  Max: ${data.metrics.http_req_duration.values.max.toFixed(2)}ms\n`;
    summary += `${indent}  Avg: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms\n`;
    summary += `${indent}  P50: ${data.metrics.http_req_duration.values['p(50)'].toFixed(2)}ms\n`;
    summary += `${indent}  P95: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms\n`;
    summary += `${indent}  P99: ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)}ms\n\n`;
  }

  if (data.metrics.errors) {
    const errorRate = (data.metrics.errors.values.rate * 100).toFixed(2);
    summary += `${indent}Error Rate: ${errorRate}%\n\n`;
  }

  if (data.metrics.checks) {
    const passRate = (data.metrics.checks.values.rate * 100).toFixed(2);
    summary += `${indent}Check Pass Rate: ${passRate}%\n\n`;
  }

  return summary;
}
