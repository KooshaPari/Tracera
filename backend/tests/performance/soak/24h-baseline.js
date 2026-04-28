import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { htmlReport } from 'https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

// Custom metrics for soak testing
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');
const slowRequests = new Counter('slow_requests');
const memoryWarnings = new Counter('memory_warnings');
const connectionErrors = new Counter('connection_errors');
const activeConnections = new Gauge('active_connections');

// 24-hour baseline soak test configuration
export const options = {
  scenarios: {
    baseline_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        // Ramp up over 5 minutes
        { duration: '5m', target: 20 },
        // Maintain baseline load for 24 hours
        { duration: '24h', target: 20 },
        // Gradual ramp down
        { duration: '5m', target: 0 },
      ],
      gracefulRampDown: '2m',
    },
  },
  thresholds: {
    // Performance should remain stable throughout 24 hours
    http_req_duration: [
      'p(95)<600',  // Allow slightly higher P95 for long-running test
      'p(99)<1200',
    ],
    http_req_failed: ['rate<0.02'], // Less than 2% errors
    errors: ['rate<0.05'],
    // Memory and connection monitoring
    memory_warnings: ['count<10'],  // Should not see memory warnings
    connection_errors: ['count<50'], // Minimal connection issues
    // Throughput stability
    http_reqs: ['rate>15'], // Minimum 15 req/s with 20 VUs
  },
  // Extended timeouts for long-running test
  timeout: '120s',
  noConnectionReuse: false, // Allow connection reuse
  userAgent: 'k6-soak-test/24h-baseline',
  // Monitoring intervals
  summaryTimeUnit: 'ms',
};

// Environment configuration
const BASE_URL = __ENV.API_URL || 'http://localhost:3030';
const PROJECT_ID = __ENV.PROJECT_ID || 'soak-test-project';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';
const MONITORING_ENDPOINT = __ENV.MONITORING_ENDPOINT || '';

// Track test state
let iterationCount = 0;
let lastMemoryCheck = Date.now();
const MEMORY_CHECK_INTERVAL = 60000; // Check every minute

// Helper function to generate headers
function getHeaders(includeAuth = true) {
  const headers = {
    'Content-Type': 'application/json',
    'X-Test-Type': '24h-baseline',
    'X-Test-Iteration': iterationCount.toString(),
  };
  if (includeAuth && AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }
  return headers;
}

// Setup function - runs once at start
export function setup() {
  console.log('🚀 Starting 24-hour baseline soak test');
  console.log(`Target URL: ${BASE_URL}`);
  console.log(`Project ID: ${PROJECT_ID}`);
  console.log(`Start time: ${new Date().toISOString()}`);

  return {
    startTime: Date.now(),
    testType: '24h-baseline',
  };
}

// Main test iteration
export default function(data) {
  iterationCount++;

  // Periodic memory check
  if (Date.now() - lastMemoryCheck > MEMORY_CHECK_INTERVAL && MONITORING_ENDPOINT) {
    checkSystemHealth();
    lastMemoryCheck = Date.now();
  }

  // Realistic workload distribution
  const scenario = Math.random();

  if (scenario < 0.35) {
    // 35% - List operations (most common)
    testListItems();
  } else if (scenario < 0.60) {
    // 25% - Read single items
    testGetItem();
  } else if (scenario < 0.75) {
    // 15% - Search operations
    testSearch();
  } else if (scenario < 0.85) {
    // 10% - Graph viewport queries
    testGraphViewport();
  } else if (scenario < 0.92) {
    // 7% - Write operations
    testCreateItem();
  } else if (scenario < 0.97) {
    // 5% - Update operations
    testUpdateItem();
  } else {
    // 3% - Complex graph queries
    testComplexGraphQuery();
  }

  // Realistic think time between operations
  sleep(Math.random() * 3 + 2); // 2-5 seconds
}

function testListItems() {
  group('List Items', function() {
    const offset = Math.floor(Math.random() * 100);
    const limit = 20 + Math.floor(Math.random() * 30); // 20-50 items
    const url = `${BASE_URL}/api/v1/items?project_id=${PROJECT_ID}&limit=${limit}&offset=${offset}`;

    const res = http.get(url, {
      headers: getHeaders(),
      tags: { operation: 'list_items' },
    });

    const success = check(res, {
      'list items status is 200': (r) => r.status === 200,
      'list items duration < 300ms': (r) => r.timings.duration < 300,
      'list items has valid response': (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body) || (body.items && Array.isArray(body.items));
        } catch {
          return false;
        }
      },
    });

    recordMetrics(res, success, 300, 'list_items');
  });
}

function testGetItem() {
  group('Get Item', function() {
    // Simulate accessing different items
    const itemId = `item-${Math.floor(Math.random() * 1000)}`;
    const url = `${BASE_URL}/api/v1/items/${itemId}`;

    const res = http.get(url, {
      headers: getHeaders(),
      tags: { operation: 'get_item' },
    });

    const success = check(res, {
      'get item status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      'get item duration < 150ms': (r) => r.timings.duration < 150,
    });

    recordMetrics(res, success, 150, 'get_item');
  });
}

function testSearch() {
  group('Search', function() {
    const searchTerms = ['test', 'feature', 'bug', 'task', 'requirement', 'story'];
    const query = searchTerms[Math.floor(Math.random() * searchTerms.length)];

    const searchQuery = {
      query: query,
      project_id: PROJECT_ID,
      limit: 20,
      offset: 0,
    };

    const url = `${BASE_URL}/api/v1/search`;
    const res = http.post(url, JSON.stringify(searchQuery), {
      headers: getHeaders(),
      tags: { operation: 'search' },
    });

    const success = check(res, {
      'search status is 200': (r) => r.status === 200,
      'search duration < 400ms': (r) => r.timings.duration < 400,
    });

    recordMetrics(res, success, 400, 'search');
  });
}

function testGraphViewport() {
  group('Graph Viewport', function() {
    // Simulate different viewport positions
    const baseX = Math.floor(Math.random() * 5000);
    const baseY = Math.floor(Math.random() * 5000);

    const viewportQuery = {
      viewport: {
        minX: baseX,
        minY: baseY,
        maxX: baseX + 1920,
        maxY: baseY + 1080,
      },
      zoom: 0.5 + Math.random() * 1.5, // 0.5 to 2.0
      bufferPx: 500,
    };

    const url = `${BASE_URL}/api/v1/graph/viewport/${PROJECT_ID}`;
    const res = http.post(url, JSON.stringify(viewportQuery), {
      headers: getHeaders(),
      tags: { operation: 'graph_viewport' },
    });

    const success = check(res, {
      'viewport status is 200': (r) => r.status === 200,
      'viewport duration < 600ms': (r) => r.timings.duration < 600,
    });

    recordMetrics(res, success, 600, 'graph_viewport');
  });
}

function testCreateItem() {
  group('Create Item', function() {
    const newItem = {
      project_id: PROJECT_ID,
      title: `Soak Test Item ${Date.now()}-${iterationCount}`,
      description: 'Created during 24h soak test',
      type: 'task',
      status: 'todo',
      priority: Math.floor(Math.random() * 5) + 1,
    };

    const url = `${BASE_URL}/api/v1/items`;
    const res = http.post(url, JSON.stringify(newItem), {
      headers: getHeaders(),
      tags: { operation: 'create_item' },
    });

    const success = check(res, {
      'create item status is 201': (r) => r.status === 201,
      'create item duration < 400ms': (r) => r.timings.duration < 400,
    });

    recordMetrics(res, success, 400, 'create_item');
  });
}

function testUpdateItem() {
  group('Update Item', function() {
    const itemId = `item-${Math.floor(Math.random() * 1000)}`;
    const updates = {
      status: ['todo', 'in_progress', 'done'][Math.floor(Math.random() * 3)],
      priority: Math.floor(Math.random() * 5) + 1,
    };

    const url = `${BASE_URL}/api/v1/items/${itemId}`;
    const res = http.patch(url, JSON.stringify(updates), {
      headers: getHeaders(),
      tags: { operation: 'update_item' },
    });

    const success = check(res, {
      'update item status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      'update item duration < 300ms': (r) => r.timings.duration < 300,
    });

    recordMetrics(res, success, 300, 'update_item');
  });
}

function testComplexGraphQuery() {
  group('Complex Graph Query', function() {
    const itemId = `item-${Math.floor(Math.random() * 100)}`;
    const depth = 2 + Math.floor(Math.random() * 3); // 2-4 levels

    const url = `${BASE_URL}/api/v1/graph/descendants/${itemId}?depth=${depth}`;
    const res = http.get(url, {
      headers: getHeaders(),
      tags: { operation: 'graph_query' },
    });

    const success = check(res, {
      'graph query status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      'graph query duration < 800ms': (r) => r.timings.duration < 800,
    });

    recordMetrics(res, success, 800, 'graph_query');
  });
}

function checkSystemHealth() {
  if (!MONITORING_ENDPOINT) return;

  group('Health Check', function() {
    const res = http.get(MONITORING_ENDPOINT, {
      tags: { operation: 'health_check' },
    });

    if (res.status === 200) {
      try {
        const metrics = JSON.parse(res.body);

        // Check memory usage
        if (metrics.memory_usage_percent > 85) {
          memoryWarnings.add(1);
          console.warn(`⚠️  High memory usage: ${metrics.memory_usage_percent}%`);
        }

        // Check connection pool
        if (metrics.connection_pool_size > metrics.connection_pool_max * 0.9) {
          console.warn(`⚠️  Connection pool near capacity: ${metrics.connection_pool_size}/${metrics.connection_pool_max}`);
        }

        activeConnections.add(metrics.active_connections || 0);
      } catch (e) {
        console.error('Failed to parse health metrics:', e.message);
      }
    }
  });
}

function recordMetrics(response, success, threshold, operation) {
  apiDuration.add(response.timings.duration, { operation });
  errorRate.add(!success, { operation });

  if (response.timings.duration > threshold) {
    slowRequests.add(1, { operation });
  }

  // Track connection errors
  if (response.error) {
    connectionErrors.add(1, { operation });
  }

  // Log slow requests during soak test
  if (response.timings.duration > threshold * 2) {
    console.warn(`Slow ${operation} request: ${response.timings.duration.toFixed(2)}ms (threshold: ${threshold}ms)`);
  }
}

// Teardown function - runs once at end
export function teardown(data) {
  const endTime = Date.now();
  const duration = endTime - data.startTime;
  const durationHours = (duration / (1000 * 60 * 60)).toFixed(2);

  console.log('✅ 24-hour baseline soak test completed');
  console.log(`End time: ${new Date().toISOString()}`);
  console.log(`Total duration: ${durationHours} hours`);
}

// Custom summary with trend analysis
export function handleSummary(data) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    [`soak-results/24h-baseline-${timestamp}.json`]: JSON.stringify(data, null, 2),
    [`soak-results/24h-baseline-${timestamp}.html`]: htmlReport(data),
    'soak-results/24h-baseline-latest.json': JSON.stringify(data, null, 2),
  };
}
