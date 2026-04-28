import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');
const slowRequests = new Counter('slow_requests');

// Test configuration
export const options = {
  stages: [
    { duration: '1m', target: 10 },  // Ramp up to 10 users
    { duration: '3m', target: 10 },  // Stay at 10 users
    { duration: '1m', target: 50 },  // Ramp up to 50 users
    { duration: '3m', target: 50 },  // Stay at 50 users
    { duration: '1m', target: 100 }, // Spike to 100 users
    { duration: '2m', target: 100 }, // Stay at 100 users
    { duration: '1m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% under 500ms, 99% under 1s
    http_req_failed: ['rate<0.01'],                  // Less than 1% errors
    errors: ['rate<0.05'],                           // Less than 5% error rate
  },
};

// Environment configuration
const BASE_URL = __ENV.API_URL || 'http://localhost:3030';
const PROJECT_ID = __ENV.PROJECT_ID || 'test-project-id';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';

// Helper function to generate headers
function getHeaders(includeAuth = true) {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (includeAuth && AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }
  return headers;
}

export default function() {
  // Test different API endpoints with weighted distribution
  const scenario = Math.random();

  if (scenario < 0.4) {
    // 40% - List items (most common read operation)
    testListItems();
  } else if (scenario < 0.6) {
    // 20% - Get single item
    testGetItem();
  } else if (scenario < 0.75) {
    // 15% - Search
    testSearch();
  } else if (scenario < 0.85) {
    // 10% - Graph viewport (expensive operation)
    testGraphViewport();
  } else if (scenario < 0.95) {
    // 10% - Create item
    testCreateItem();
  } else {
    // 5% - Complex graph operations
    testGraphOperations();
  }

  sleep(1); // Think time between requests
}

function testListItems() {
  group('List Items', function() {
    const url = `${BASE_URL}/api/v1/items?project_id=${PROJECT_ID}&limit=50&offset=0`;
    const res = http.get(url, { headers: getHeaders() });

    const success = check(res, {
      'list items status is 200': (r) => r.status === 200,
      'list items duration < 200ms': (r) => r.timings.duration < 200,
      'list items has data': (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body) || (body.items && Array.isArray(body.items));
        } catch {
          return false;
        }
      },
    });

    recordMetrics(res, success, 200);
  });
}

function testGetItem() {
  group('Get Single Item', function() {
    // In a real test, you'd use actual item IDs from setup
    const itemId = 'test-item-id';
    const url = `${BASE_URL}/api/v1/items/${itemId}`;
    const res = http.get(url, { headers: getHeaders() });

    const success = check(res, {
      'get item status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      'get item duration < 100ms': (r) => r.timings.duration < 100,
    });

    recordMetrics(res, success, 100);
  });
}

function testSearch() {
  group('Search', function() {
    const searchQuery = {
      query: 'test',
      project_id: PROJECT_ID,
      limit: 20,
      offset: 0,
    };

    const url = `${BASE_URL}/api/v1/search`;
    const res = http.post(url, JSON.stringify(searchQuery), { headers: getHeaders() });

    const success = check(res, {
      'search status is 200': (r) => r.status === 200,
      'search duration < 300ms': (r) => r.timings.duration < 300,
      'search has results': (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body.results) || Array.isArray(body);
        } catch {
          return false;
        }
      },
    });

    recordMetrics(res, success, 300);
  });
}

function testGraphViewport() {
  group('Graph Viewport', function() {
    const viewportQuery = {
      viewport: {
        minX: 0,
        minY: 0,
        maxX: 1920,
        maxY: 1080,
      },
      zoom: 1.0,
      bufferPx: 500,
    };

    const url = `${BASE_URL}/api/v1/graph/viewport/${PROJECT_ID}`;
    const res = http.post(url, JSON.stringify(viewportQuery), { headers: getHeaders() });

    const success = check(res, {
      'viewport status is 200': (r) => r.status === 200,
      'viewport duration < 500ms': (r) => r.timings.duration < 500,
      'viewport has nodes': (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body.nodes);
        } catch {
          return false;
        }
      },
    });

    recordMetrics(res, success, 500);
  });
}

function testCreateItem() {
  group('Create Item', function() {
    const newItem = {
      project_id: PROJECT_ID,
      title: `Load Test Item ${Date.now()}`,
      description: 'Created during load testing',
      type: 'task',
      status: 'todo',
      priority: 2,
    };

    const url = `${BASE_URL}/api/v1/items`;
    const res = http.post(url, JSON.stringify(newItem), { headers: getHeaders() });

    const success = check(res, {
      'create item status is 201': (r) => r.status === 201,
      'create item duration < 300ms': (r) => r.timings.duration < 300,
    });

    recordMetrics(res, success, 300);
  });
}

function testGraphOperations() {
  group('Graph Operations', function() {
    // Test graph ancestors/descendants
    const itemId = 'test-item-id';
    const url = `${BASE_URL}/api/v1/graph/ancestors/${itemId}`;
    const res = http.get(url, { headers: getHeaders() });

    const success = check(res, {
      'graph ops status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      'graph ops duration < 400ms': (r) => r.timings.duration < 400,
    });

    recordMetrics(res, success, 400);
  });
}

function recordMetrics(response, success, threshold) {
  apiDuration.add(response.timings.duration);
  errorRate.add(!success);

  if (response.timings.duration > threshold) {
    slowRequests.add(1);
  }
}

export function handleSummary(data) {
  const summary = textSummary(data);
  return {
    'stdout': summary,
    'performance-results/summary.json': JSON.stringify(data, null, 2),
  };
}

function textSummary(data) {
  const metrics = data.metrics || {};
  const state = data.state || {};

  // Extract key metrics
  const httpDuration = metrics.http_req_duration?.values || {};
  const httpFailed = metrics.http_req_failed?.values || {};
  const httpReqs = metrics.http_reqs?.values || {};
  const errors = metrics.errors?.values || {};
  const slowRequests = metrics.slow_requests?.values || {};

  const p50 = httpDuration['p(50)'] || 'N/A';
  const p95 = httpDuration['p(95)'] || 'N/A';
  const p99 = httpDuration['p(99)'] || 'N/A';
  const avgDuration = httpDuration.avg || 'N/A';
  const maxDuration = httpDuration.max || 'N/A';

  const totalRequests = httpReqs.count || 0;
  const failedRequests = httpFailed.count || 0;
  const failureRate = ((failedRequests / Math.max(totalRequests, 1)) * 100).toFixed(2);

  const duration = state.testRunDurationMs || 0;
  const durationSec = (duration / 1000).toFixed(2);
  const rps = (totalRequests / Math.max(durationSec, 1)).toFixed(2);

  let summary = `
╔════════════════════════════════════════════════════════════════╗
║                  Load Test Results Summary                     ║
╚════════════════════════════════════════════════════════════════╝

Test Duration:      ${durationSec}s
Total Requests:     ${totalRequests}
Failed Requests:    ${failedRequests} (${failureRate}%)
Requests/Second:    ${rps}

Response Time Metrics (ms):
  P50:              ${typeof p50 === 'number' ? p50.toFixed(2) : p50}
  P95:              ${typeof p95 === 'number' ? p95.toFixed(2) : p95}
  P99:              ${typeof p99 === 'number' ? p99.toFixed(2) : p99}
  Avg:              ${typeof avgDuration === 'number' ? avgDuration.toFixed(2) : avgDuration}
  Max:              ${typeof maxDuration === 'number' ? maxDuration.toFixed(2) : maxDuration}

Thresholds:
  ✓ P95 < 500ms:     ${typeof p95 === 'number' && p95 < 500 ? 'PASSED' : 'FAILED'}
  ✓ P99 < 1000ms:    ${typeof p99 === 'number' && p99 < 1000 ? 'PASSED' : 'FAILED'}
  ✓ Error Rate < 1%: ${parseFloat(failureRate) < 1 ? 'PASSED' : 'FAILED'}
  ✓ RPS > 100:       ${rps > 100 ? 'PASSED' : 'WARNING (may be normal in CI)'}

Custom Metrics:
  Slow Requests (>threshold): ${slowRequests.count || 0}
  Error Rate (custom):         ${errors.rate ? (errors.rate * 100).toFixed(2) + '%' : 'N/A'}
`;

  return summary;
}
