import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { htmlReport } from 'https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

// Custom metrics for detailed monitoring
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');
const slowRequests = new Counter('slow_requests');
const activeVUs = new Gauge('active_virtual_users');
const throughput = new Rate('throughput');

// Database-specific metrics
const dbConnectionErrors = new Counter('db_connection_errors');
const cacheHitRate = new Rate('cache_hit_rate');
const queryDuration = new Trend('query_duration');

// Test configuration for 10k concurrent users
export const options = {
  scenarios: {
    // Scenario 1: Gradual ramp-up to 10k users over 30 minutes
    ramp_up_phase: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '5m', target: 1000 },   // 0 -> 1k users in 5 min
        { duration: '5m', target: 2500 },   // 1k -> 2.5k users in 5 min
        { duration: '5m', target: 5000 },   // 2.5k -> 5k users in 5 min
        { duration: '5m', target: 7500 },   // 5k -> 7.5k users in 5 min
        { duration: '10m', target: 10000 }, // 7.5k -> 10k users in 10 min
      ],
      gracefulRampDown: '2m',
    },
    // Scenario 2: Sustained load at 10k users for 2 hours
    sustained_load: {
      executor: 'constant-vus',
      vus: 10000,
      duration: '2h',
      startTime: '30m', // Start after ramp-up
    },
    // Scenario 3: Spike testing - sudden bursts during sustained load
    spike_test: {
      executor: 'ramping-vus',
      startTime: '1h', // Start 1 hour into sustained load
      stages: [
        { duration: '30s', target: 12000 }, // Sudden spike to 12k
        { duration: '2m', target: 12000 },  // Hold spike
        { duration: '30s', target: 10000 }, // Return to baseline
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    // Response time thresholds
    'http_req_duration': [
      'p(50)<200',   // 50% of requests under 200ms
      'p(95)<500',   // 95% of requests under 500ms
      'p(99)<1000',  // 99% of requests under 1s
      'avg<300',     // Average response time under 300ms
    ],
    // Error rate thresholds
    'http_req_failed': ['rate<0.01'],      // Less than 1% HTTP errors
    'errors': ['rate<0.01'],               // Less than 1% custom errors
    // Throughput threshold
    'http_reqs': ['rate>1000'],            // At least 1000 req/s
    'throughput': ['rate>1000'],           // At least 1000 req/s throughput
    // Slow request threshold
    'slow_requests': ['count<10000'],      // Less than 10k slow requests total
    // Database-specific thresholds
    'db_connection_errors': ['count<100'], // Less than 100 DB connection errors
    'cache_hit_rate': ['rate>0.80'],       // At least 80% cache hit rate
    'query_duration': ['p(95)<100'],       // 95% of DB queries under 100ms
  },
  // External metrics output
  ext: {
    loadimpact: {
      projectID: __ENV.K6_CLOUD_PROJECT_ID,
      name: '10k Concurrent Users - Production Scale Test',
    },
  },
};

// Environment configuration
const BASE_URL = __ENV.API_URL || 'http://localhost:3030';
const PROJECT_ID = __ENV.PROJECT_ID || 'load-test-project';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';
const ENABLE_DETAILED_LOGS = __ENV.ENABLE_LOGS === 'true';

// Shared data for realistic testing
let itemIds = [];
let userProfiles = [];

// Setup function - runs once per VU
export function setup() {
  console.log('Setting up test data...');

  // Create test project if needed
  const projectRes = http.get(`${BASE_URL}/api/v1/projects/${PROJECT_ID}`, {
    headers: getHeaders(),
  });

  if (projectRes.status === 404) {
    console.log('Creating test project...');
    http.post(`${BASE_URL}/api/v1/projects`, JSON.stringify({
      id: PROJECT_ID,
      name: 'Load Test Project',
      description: '10k concurrent users load test',
    }), { headers: getHeaders() });
  }

  // Pre-populate some test data
  console.log('Pre-populating test data...');
  const setupData = {
    itemIds: [],
    userProfiles: [],
  };

  // Create 100 test items for realistic queries
  for (let i = 0; i < 100; i++) {
    const item = createTestItem(`Setup Item ${i}`);
    if (item && item.id) {
      setupData.itemIds.push(item.id);
    }
  }

  console.log(`Setup complete. Created ${setupData.itemIds.length} test items.`);
  return setupData;
}

// Main test function - runs for each VU
export default function(data) {
  // Update active VUs metric
  activeVUs.add(1);

  // Simulate realistic user behavior with weighted distribution
  const userBehavior = Math.random();

  if (userBehavior < 0.35) {
    // 35% - Browse and read operations (most common)
    browseItems(data);
  } else if (userBehavior < 0.60) {
    // 25% - Search and filter
    searchAndFilter(data);
  } else if (userBehavior < 0.75) {
    // 15% - View details and relationships
    viewItemDetails(data);
  } else if (userBehavior < 0.85) {
    // 10% - Graph visualization
    exploreGraphView(data);
  } else if (userBehavior < 0.93) {
    // 8% - Create and edit operations
    createAndEditOperations(data);
  } else {
    // 7% - Complex operations (analytics, reports)
    complexOperations(data);
  }

  // Realistic think time between actions
  sleep(Math.random() * 3 + 1); // 1-4 seconds
}

// User journey: Browse items
function browseItems(data) {
  group('Browse Items Journey', function() {
    // List items with pagination
    const page = Math.floor(Math.random() * 10);
    const limit = 50;
    const offset = page * limit;

    const listUrl = `${BASE_URL}/api/v1/items?project_id=${PROJECT_ID}&limit=${limit}&offset=${offset}`;
    const listRes = http.get(listUrl, { headers: getHeaders() });

    const success = check(listRes, {
      'browse: list status 200': (r) => r.status === 200,
      'browse: response time OK': (r) => r.timings.duration < 200,
      'browse: has items': (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body) || (body.items && Array.isArray(body.items));
        } catch {
          return false;
        }
      },
    });

    recordMetrics(listRes, success, 200, 'list_items');
    sleep(0.5);

    // Get counts/stats
    const statsUrl = `${BASE_URL}/api/v1/projects/${PROJECT_ID}/stats`;
    const statsRes = http.get(statsUrl, { headers: getHeaders() });

    check(statsRes, {
      'browse: stats status 200': (r) => r.status === 200,
      'browse: stats fast': (r) => r.timings.duration < 100,
    });

    recordMetrics(statsRes, true, 100, 'get_stats');
  });
}

// User journey: Search and filter
function searchAndFilter(data) {
  group('Search and Filter Journey', function() {
    const searchTerms = ['test', 'user', 'task', 'feature', 'bug', 'requirement'];
    const searchTerm = searchTerms[Math.floor(Math.random() * searchTerms.length)];

    const searchPayload = {
      query: searchTerm,
      project_id: PROJECT_ID,
      limit: 20,
      offset: 0,
      filters: {
        type: ['task', 'story', 'bug'],
        status: ['todo', 'in_progress'],
      },
    };

    const searchUrl = `${BASE_URL}/api/v1/search`;
    const searchRes = http.post(searchUrl, JSON.stringify(searchPayload), { headers: getHeaders() });

    const success = check(searchRes, {
      'search: status 200': (r) => r.status === 200,
      'search: response time OK': (r) => r.timings.duration < 300,
      'search: has results': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.results !== undefined || Array.isArray(body);
        } catch {
          return false;
        }
      },
    });

    recordMetrics(searchRes, success, 300, 'search');
    sleep(1);

    // Follow-up: Filter results
    const filterPayload = {
      project_id: PROJECT_ID,
      filters: {
        type: 'task',
        status: 'in_progress',
        priority: [2, 3],
      },
      limit: 30,
    };

    const filterUrl = `${BASE_URL}/api/v1/items/filter`;
    const filterRes = http.post(filterUrl, JSON.stringify(filterPayload), { headers: getHeaders() });

    check(filterRes, {
      'filter: status 200': (r) => r.status === 200,
      'filter: fast response': (r) => r.timings.duration < 250,
    });

    recordMetrics(filterRes, true, 250, 'filter');
  });
}

// User journey: View item details
function viewItemDetails(data) {
  group('View Item Details Journey', function() {
    // Use a random item from setup data
    const itemId = data.itemIds && data.itemIds.length > 0
      ? data.itemIds[Math.floor(Math.random() * data.itemIds.length)]
      : 'default-item-id';

    // Get item details
    const itemUrl = `${BASE_URL}/api/v1/items/${itemId}`;
    const itemRes = http.get(itemUrl, { headers: getHeaders() });

    const success = check(itemRes, {
      'details: status 200 or 404': (r) => r.status === 200 || r.status === 404,
      'details: fast response': (r) => r.timings.duration < 100,
    });

    recordMetrics(itemRes, success, 100, 'get_item');

    if (itemRes.status === 200) {
      sleep(0.5);

      // Get related items (links)
      const linksUrl = `${BASE_URL}/api/v1/items/${itemId}/links`;
      const linksRes = http.get(linksUrl, { headers: getHeaders() });

      check(linksRes, {
        'links: status 200': (r) => r.status === 200,
        'links: response time OK': (r) => r.timings.duration < 150,
      });

      recordMetrics(linksRes, true, 150, 'get_links');
      sleep(0.3);

      // Get item history
      const historyUrl = `${BASE_URL}/api/v1/items/${itemId}/history`;
      const historyRes = http.get(historyUrl, { headers: getHeaders() });

      check(historyRes, {
        'history: status 200': (r) => r.status === 200,
        'history: response time OK': (r) => r.timings.duration < 200,
      });

      recordMetrics(historyRes, true, 200, 'get_history');
    }
  });
}

// User journey: Graph visualization
function exploreGraphView(data) {
  group('Graph Visualization Journey', function() {
    // Get graph viewport (expensive operation)
    const viewportPayload = {
      viewport: {
        minX: Math.floor(Math.random() * 1000),
        minY: Math.floor(Math.random() * 1000),
        maxX: Math.floor(Math.random() * 1000) + 1920,
        maxY: Math.floor(Math.random() * 1000) + 1080,
      },
      zoom: 0.5 + Math.random(),
      bufferPx: 500,
      includeLinks: true,
    };

    const viewportUrl = `${BASE_URL}/api/v1/graph/viewport/${PROJECT_ID}`;
    const viewportRes = http.post(viewportUrl, JSON.stringify(viewportPayload), { headers: getHeaders() });

    const success = check(viewportRes, {
      'graph: viewport status 200': (r) => r.status === 200,
      'graph: viewport response OK': (r) => r.timings.duration < 500,
      'graph: has nodes': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.nodes !== undefined;
        } catch {
          return false;
        }
      },
    });

    recordMetrics(viewportRes, success, 500, 'graph_viewport');
    sleep(1);

    // Get graph statistics
    const statsUrl = `${BASE_URL}/api/v1/graph/${PROJECT_ID}/stats`;
    const statsRes = http.get(statsUrl, { headers: getHeaders() });

    check(statsRes, {
      'graph: stats status 200': (r) => r.status === 200,
      'graph: stats fast': (r) => r.timings.duration < 150,
    });

    recordMetrics(statsRes, true, 150, 'graph_stats');
  });
}

// User journey: Create and edit
function createAndEditOperations(data) {
  group('Create and Edit Journey', function() {
    // Create a new item
    const newItem = {
      project_id: PROJECT_ID,
      title: `Load Test Item ${Date.now()}-${Math.random()}`,
      description: 'Created during 10k user load test',
      type: ['task', 'story', 'bug'][Math.floor(Math.random() * 3)],
      status: 'todo',
      priority: Math.floor(Math.random() * 4) + 1,
    };

    const createUrl = `${BASE_URL}/api/v1/items`;
    const createRes = http.post(createUrl, JSON.stringify(newItem), { headers: getHeaders() });

    const success = check(createRes, {
      'create: status 201': (r) => r.status === 201,
      'create: response time OK': (r) => r.timings.duration < 300,
      'create: returns item': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.id !== undefined;
        } catch {
          return false;
        }
      },
    });

    recordMetrics(createRes, success, 300, 'create_item');

    if (createRes.status === 201 && success) {
      sleep(0.5);

      // Update the created item
      let createdItem;
      try {
        createdItem = JSON.parse(createRes.body);
      } catch {
        return;
      }

      const updatePayload = {
        title: `Updated: ${newItem.title}`,
        status: 'in_progress',
      };

      const updateUrl = `${BASE_URL}/api/v1/items/${createdItem.id}`;
      const updateRes = http.put(updateUrl, JSON.stringify(updatePayload), { headers: getHeaders() });

      check(updateRes, {
        'update: status 200': (r) => r.status === 200,
        'update: response time OK': (r) => r.timings.duration < 250,
      });

      recordMetrics(updateRes, true, 250, 'update_item');
    }
  });
}

// User journey: Complex operations
function complexOperations(data) {
  group('Complex Operations Journey', function() {
    const itemId = data.itemIds && data.itemIds.length > 0
      ? data.itemIds[Math.floor(Math.random() * data.itemIds.length)]
      : 'default-item-id';

    // Get graph ancestors (recursive query)
    const ancestorsUrl = `${BASE_URL}/api/v1/graph/ancestors/${itemId}?depth=5`;
    const ancestorsRes = http.get(ancestorsUrl, { headers: getHeaders() });

    const success1 = check(ancestorsRes, {
      'complex: ancestors status OK': (r) => r.status === 200 || r.status === 404,
      'complex: ancestors response OK': (r) => r.timings.duration < 400,
    });

    recordMetrics(ancestorsRes, success1, 400, 'graph_ancestors');
    sleep(0.5);

    // Get graph descendants (recursive query)
    const descendantsUrl = `${BASE_URL}/api/v1/graph/descendants/${itemId}?depth=5`;
    const descendantsRes = http.get(descendantsUrl, { headers: getHeaders() });

    const success2 = check(descendantsRes, {
      'complex: descendants status OK': (r) => r.status === 200 || r.status === 404,
      'complex: descendants response OK': (r) => r.timings.duration < 400,
    });

    recordMetrics(descendantsRes, success2, 400, 'graph_descendants');
    sleep(0.5);

    // Coverage analytics (expensive aggregation)
    const coverageUrl = `${BASE_URL}/api/v1/projects/${PROJECT_ID}/coverage/summary`;
    const coverageRes = http.get(coverageUrl, { headers: getHeaders() });

    check(coverageRes, {
      'complex: coverage status 200': (r) => r.status === 200,
      'complex: coverage response OK': (r) => r.timings.duration < 600,
    });

    recordMetrics(coverageRes, true, 600, 'coverage_analytics');
  });
}

// Helper function to generate headers
function getHeaders(includeAuth = true) {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  if (includeAuth && AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }
  return headers;
}

// Helper function to create test item
function createTestItem(title) {
  const item = {
    project_id: PROJECT_ID,
    title: title,
    description: 'Setup item for load testing',
    type: 'task',
    status: 'todo',
    priority: 2,
  };

  const res = http.post(`${BASE_URL}/api/v1/items`, JSON.stringify(item), {
    headers: getHeaders(),
    timeout: '10s',
  });

  if (res.status === 201) {
    try {
      return JSON.parse(res.body);
    } catch {
      return null;
    }
  }
  return null;
}

// Record custom metrics
function recordMetrics(response, success, threshold, operation) {
  // Record duration
  apiDuration.add(response.timings.duration);
  queryDuration.add(response.timings.waiting); // Backend processing time

  // Record error rate
  errorRate.add(!success);

  // Track throughput
  throughput.add(1);

  // Count slow requests
  if (response.timings.duration > threshold) {
    slowRequests.add(1);
    if (ENABLE_DETAILED_LOGS) {
      console.log(`Slow request detected: ${operation} took ${response.timings.duration}ms (threshold: ${threshold}ms)`);
    }
  }

  // Track database connection errors
  if (response.status === 503 || response.status === 504) {
    dbConnectionErrors.add(1);
  }

  // Estimate cache hit rate from response headers
  if (response.headers['X-Cache-Hit']) {
    cacheHitRate.add(response.headers['X-Cache-Hit'] === 'true' ? 1 : 0);
  }
}

// Teardown function
export function teardown(data) {
  console.log('Test teardown complete.');
  console.log(`Total test items created: ${data.itemIds ? data.itemIds.length : 0}`);
}

// Custom summary with detailed metrics
export function handleSummary(data) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    [`performance-results/10k-users-${timestamp}.json`]: JSON.stringify(data, null, 2),
    [`performance-results/10k-users-${timestamp}.html`]: htmlReport(data),
    [`performance-results/10k-users-summary.txt`]: generateDetailedSummary(data),
  };
}

// Generate detailed summary report
function generateDetailedSummary(data) {
  const metrics = data.metrics || {};

  // Extract key metrics
  const httpDuration = metrics.http_req_duration?.values || {};
  const httpFailed = metrics.http_req_failed?.values || {};
  const httpReqs = metrics.http_reqs?.values || {};
  const errors = metrics.errors?.values || {};
  const slowRequests = metrics.slow_requests?.values || {};
  const dbErrors = metrics.db_connection_errors?.values || {};
  const cacheHit = metrics.cache_hit_rate?.values || {};
  const queryDur = metrics.query_duration?.values || {};
  const throughputMetric = metrics.throughput?.values || {};

  const duration = data.state?.testRunDurationMs || 0;
  const durationMin = (duration / 60000).toFixed(2);
  const totalRequests = httpReqs.count || 0;
  const failedRequests = httpFailed.count || 0;
  const failureRate = ((failedRequests / Math.max(totalRequests, 1)) * 100).toFixed(2);
  const rps = (totalRequests / Math.max(duration / 1000, 1)).toFixed(2);

  return `
╔══════════════════════════════════════════════════════════════════════════════╗
║                     10K CONCURRENT USERS LOAD TEST REPORT                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

Test Duration:          ${durationMin} minutes (${(duration / 1000).toFixed(0)}s)
Test Started:           ${new Date(data.state?.startTime || Date.now()).toISOString()}
Target Load:            10,000 concurrent users
Ramp-up Period:         30 minutes
Sustained Load:         2 hours at 10k users

═══════════════════════════════════════════════════════════════════════════════
REQUEST STATISTICS
═══════════════════════════════════════════════════════════════════════════════

Total Requests:         ${totalRequests.toLocaleString()}
Failed Requests:        ${failedRequests.toLocaleString()} (${failureRate}%)
Successful Requests:    ${(totalRequests - failedRequests).toLocaleString()} (${(100 - parseFloat(failureRate)).toFixed(2)}%)
Requests per Second:    ${parseFloat(rps).toLocaleString()} req/s

═══════════════════════════════════════════════════════════════════════════════
RESPONSE TIME METRICS (milliseconds)
═══════════════════════════════════════════════════════════════════════════════

  Metric        Value       Target      Status
  ─────────────────────────────────────────────────────────────────────────────
  P50 (Median)  ${(httpDuration['p(50)'] || 0).toFixed(2).padEnd(10)} < 200ms     ${httpDuration['p(50)'] < 200 ? '✓ PASS' : '✗ FAIL'}
  P95           ${(httpDuration['p(95)'] || 0).toFixed(2).padEnd(10)} < 500ms     ${httpDuration['p(95)'] < 500 ? '✓ PASS' : '✗ FAIL'}
  P99           ${(httpDuration['p(99)'] || 0).toFixed(2).padEnd(10)} < 1000ms    ${httpDuration['p(99)'] < 1000 ? '✓ PASS' : '✗ FAIL'}
  Average       ${(httpDuration.avg || 0).toFixed(2).padEnd(10)} < 300ms     ${httpDuration.avg < 300 ? '✓ PASS' : '✗ FAIL'}
  Minimum       ${(httpDuration.min || 0).toFixed(2).padEnd(10)} N/A         -
  Maximum       ${(httpDuration.max || 0).toFixed(2).padEnd(10)} N/A         -

Backend Processing Time (Query Duration):
  P50:          ${(queryDur['p(50)'] || 0).toFixed(2)}ms
  P95:          ${(queryDur['p(95)'] || 0).toFixed(2)}ms
  P99:          ${(queryDur['p(99)'] || 0).toFixed(2)}ms

═══════════════════════════════════════════════════════════════════════════════
THROUGHPUT & PERFORMANCE
═══════════════════════════════════════════════════════════════════════════════

Throughput:             ${parseFloat(rps).toLocaleString()} req/s (Target: > 1000 req/s)
Status:                 ${parseFloat(rps) > 1000 ? '✓ PASS' : '✗ FAIL - Below target'}
Slow Requests:          ${(slowRequests.count || 0).toLocaleString()} (${((slowRequests.count / Math.max(totalRequests, 1)) * 100).toFixed(2)}%)
Cache Hit Rate:         ${((cacheHit.rate || 0) * 100).toFixed(2)}% (Target: > 80%)

═══════════════════════════════════════════════════════════════════════════════
ERROR ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

HTTP Errors:            ${failedRequests.toLocaleString()} (${failureRate}%)
Custom Errors:          ${((errors.rate || 0) * 100).toFixed(2)}%
DB Connection Errors:   ${(dbErrors.count || 0).toLocaleString()}

Error Rate Status:      ${parseFloat(failureRate) < 1 ? '✓ PASS (< 1%)' : '✗ FAIL (≥ 1%)'}

═══════════════════════════════════════════════════════════════════════════════
THRESHOLD VALIDATION
═══════════════════════════════════════════════════════════════════════════════

${generateThresholdResults(data)}

═══════════════════════════════════════════════════════════════════════════════
RECOMMENDATIONS
═══════════════════════════════════════════════════════════════════════════════

${generateRecommendations(data)}

═══════════════════════════════════════════════════════════════════════════════
Test completed at: ${new Date().toISOString()}
═══════════════════════════════════════════════════════════════════════════════
`;
}

function generateThresholdResults(data) {
  const metrics = data.metrics || {};
  const thresholds = data.thresholds || {};

  let results = [];
  for (const [name, result] of Object.entries(thresholds)) {
    const status = result.ok ? '✓ PASS' : '✗ FAIL';
    results.push(`  ${status} ${name}`);
  }

  return results.length > 0 ? results.join('\n') : '  No threshold results available';
}

function generateRecommendations(data) {
  const metrics = data.metrics || {};
  const httpDuration = metrics.http_req_duration?.values || {};
  const httpFailed = metrics.http_req_failed?.values || {};
  const dbErrors = metrics.db_connection_errors?.values || {};
  const cacheHit = metrics.cache_hit_rate?.values || {};
  const totalReqs = metrics.http_reqs?.values?.count || 0;
  const failedReqs = httpFailed.count || 0;
  const failureRate = (failedReqs / Math.max(totalReqs, 1)) * 100;
  const rps = totalReqs / Math.max(data.state?.testRunDurationMs / 1000, 1);

  const recommendations = [];

  // Response time recommendations
  if (httpDuration['p(95)'] > 500) {
    recommendations.push('⚠ P95 response time exceeds 500ms target');
    recommendations.push('  → Optimize database queries and add indexes');
    recommendations.push('  → Implement query result caching');
    recommendations.push('  → Consider read replicas for database');
  }

  if (httpDuration['p(99)'] > 1000) {
    recommendations.push('⚠ P99 response time exceeds 1000ms target');
    recommendations.push('  → Investigate slow queries in 99th percentile');
    recommendations.push('  → Implement request timeout and circuit breakers');
    recommendations.push('  → Consider connection pooling optimization');
  }

  // Throughput recommendations
  if (rps < 1000) {
    recommendations.push('⚠ Throughput below 1000 req/s target');
    recommendations.push('  → Scale horizontally (add more backend instances)');
    recommendations.push('  → Optimize handler performance');
    recommendations.push('  → Consider load balancer configuration');
  }

  // Error rate recommendations
  if (failureRate >= 1) {
    recommendations.push('⚠ Error rate exceeds 1% threshold');
    recommendations.push('  → Review error logs for patterns');
    recommendations.push('  → Implement retry logic with exponential backoff');
    recommendations.push('  → Monitor database connection pool saturation');
  }

  // Database recommendations
  if ((dbErrors.count || 0) > 100) {
    recommendations.push('⚠ High database connection errors detected');
    recommendations.push('  → Increase database connection pool size');
    recommendations.push('  → Implement connection health checks');
    recommendations.push('  → Consider database scaling or optimization');
  }

  // Cache recommendations
  if ((cacheHit.rate || 0) < 0.8) {
    recommendations.push('⚠ Cache hit rate below 80% target');
    recommendations.push('  → Review cache key strategy');
    recommendations.push('  → Increase cache TTL for stable data');
    recommendations.push('  → Implement cache warming strategies');
  }

  if (recommendations.length === 0) {
    recommendations.push('✓ All performance targets met');
    recommendations.push('✓ System performing within acceptable parameters');
    recommendations.push('✓ No immediate optimization required');
  }

  return recommendations.join('\n');
}
