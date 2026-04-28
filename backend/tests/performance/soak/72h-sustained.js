import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { htmlReport } from 'https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

// Custom metrics for 72-hour sustained load testing
const errorRate = new Rate('errors');
const apiDuration = new Trend('api_duration');
const slowRequests = new Counter('slow_requests');
const memoryWarnings = new Counter('memory_warnings');
const connectionErrors = new Counter('connection_errors');
const timeoutErrors = new Counter('timeout_errors');
const activeConnections = new Gauge('active_connections');
const memoryUsagePercent = new Gauge('memory_usage_percent');
const cacheSize = new Gauge('cache_size_mb');
const connectionPoolSize = new Gauge('connection_pool_size');

// 72-hour sustained load test configuration
export const options = {
  scenarios: {
    sustained_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        // Initial ramp up
        { duration: '10m', target: 30 },
        // Sustained load for 72 hours with realistic variations
        { duration: '8h', target: 30 },   // Business hours simulation
        { duration: '4h', target: 15 },   // Off-hours
        { duration: '8h', target: 30 },   // Next business day
        { duration: '4h', target: 15 },
        { duration: '8h', target: 30 },
        { duration: '4h', target: 15 },
        { duration: '8h', target: 30 },
        { duration: '4h', target: 15 },
        { duration: '8h', target: 30 },
        { duration: '4h', target: 15 },
        { duration: '8h', target: 30 },
        { duration: '4h', target: 15 },
        // Gradual ramp down
        { duration: '10m', target: 0 },
      ],
      gracefulRampDown: '5m',
    },
  },
  thresholds: {
    // Performance degradation checks
    http_req_duration: [
      'p(95)<700',   // Allow for some degradation over 72h
      'p(99)<1500',
    ],
    http_req_failed: ['rate<0.03'],  // Less than 3% errors over 72h
    errors: ['rate<0.05'],
    // Memory leak detection
    memory_warnings: ['count<100'],  // Should not accumulate warnings
    memory_usage_percent: ['value<90'], // Memory should stay below 90%
    // Connection pool monitoring
    connection_errors: ['count<200'],
    connection_pool_size: ['value<95'], // Should not max out pool
    timeout_errors: ['count<50'],
    // Cache growth monitoring
    cache_size_mb: ['value<1024'], // Cache should not grow beyond 1GB
    // Sustained throughput
    http_reqs: ['rate>12'], // Minimum average throughput
  },
  timeout: '180s',
  noConnectionReuse: false,
  userAgent: 'k6-soak-test/72h-sustained',
  summaryTimeUnit: 'ms',
};

// Environment configuration
const BASE_URL = __ENV.API_URL || 'http://localhost:3030';
const PROJECT_ID = __ENV.PROJECT_ID || 'soak-test-72h';
const AUTH_TOKEN = __ENV.AUTH_TOKEN || '';
const MONITORING_ENDPOINT = __ENV.MONITORING_ENDPOINT || '';

// Test state tracking
let iterationCount = 0;
let lastHealthCheck = Date.now();
let lastMemoryBaseline = 0;
let hourlyMetrics = [];
const HEALTH_CHECK_INTERVAL = 300000; // Check every 5 minutes
const HOURLY_REPORT_INTERVAL = 3600000; // Report every hour

function getHeaders(includeAuth = true) {
  const headers = {
    'Content-Type': 'application/json',
    'X-Test-Type': '72h-sustained',
    'X-Test-Iteration': iterationCount.toString(),
    'X-Test-Hour': Math.floor((Date.now() - __ENV.START_TIME) / 3600000).toString(),
  };
  if (includeAuth && AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${AUTH_TOKEN}`;
  }
  return headers;
}

export function setup() {
  console.log('🚀 Starting 72-hour sustained load soak test');
  console.log(`Target URL: ${BASE_URL}`);
  console.log(`Project ID: ${PROJECT_ID}`);
  console.log(`Start time: ${new Date().toISOString()}`);
  console.log('Expected duration: 72 hours + ramp up/down');

  // Perform initial health check
  if (MONITORING_ENDPOINT) {
    const health = http.get(MONITORING_ENDPOINT);
    if (health.status === 200) {
      const metrics = JSON.parse(health.body);
      console.log(`Initial memory usage: ${metrics.memory_usage_percent}%`);
      console.log(`Initial connection pool: ${metrics.connection_pool_size}`);
    }
  }

  return {
    startTime: Date.now(),
    testType: '72h-sustained',
  };
}

export default function(data) {
  iterationCount++;
  const currentTime = Date.now();

  // Periodic health monitoring
  if (currentTime - lastHealthCheck > HEALTH_CHECK_INTERVAL) {
    performHealthCheck(data);
    lastHealthCheck = currentTime;
  }

  // Hourly trend analysis
  if (currentTime - data.startTime > hourlyMetrics.length * HOURLY_REPORT_INTERVAL) {
    recordHourlyMetrics(data);
  }

  // Realistic workload with variations based on time
  const hour = new Date().getHours();
  const isBusinessHours = hour >= 9 && hour <= 17;

  executeWorkload(isBusinessHours);

  // Variable think time based on business hours
  const thinkTime = isBusinessHours ? Math.random() * 2 + 1 : Math.random() * 5 + 3;
  sleep(thinkTime);
}

function executeWorkload(isBusinessHours) {
  const scenario = Math.random();

  if (isBusinessHours) {
    // Business hours: more writes and complex operations
    if (scenario < 0.30) {
      testListItems();
    } else if (scenario < 0.50) {
      testGetItem();
    } else if (scenario < 0.65) {
      testSearch();
    } else if (scenario < 0.75) {
      testGraphViewport();
    } else if (scenario < 0.85) {
      testCreateItem();
    } else if (scenario < 0.92) {
      testUpdateItem();
    } else {
      testComplexGraphQuery();
    }
  } else {
    // Off hours: more reads, fewer writes
    if (scenario < 0.40) {
      testListItems();
    } else if (scenario < 0.70) {
      testGetItem();
    } else if (scenario < 0.85) {
      testSearch();
    } else if (scenario < 0.95) {
      testGraphViewport();
    } else {
      testCreateItem();
    }
  }
}

function testListItems() {
  group('List Items', function() {
    const offset = Math.floor(Math.random() * 200);
    const limit = 20 + Math.floor(Math.random() * 30);
    const url = `${BASE_URL}/api/v1/items?project_id=${PROJECT_ID}&limit=${limit}&offset=${offset}`;

    const res = http.get(url, {
      headers: getHeaders(),
      tags: { operation: 'list_items' },
    });

    const success = check(res, {
      'list items status is 200': (r) => r.status === 200,
      'list items duration < 350ms': (r) => r.timings.duration < 350,
    });

    recordMetrics(res, success, 350, 'list_items');
  });
}

function testGetItem() {
  group('Get Item', function() {
    const itemId = `item-${Math.floor(Math.random() * 2000)}`;
    const url = `${BASE_URL}/api/v1/items/${itemId}`;

    const res = http.get(url, {
      headers: getHeaders(),
      tags: { operation: 'get_item' },
    });

    const success = check(res, {
      'get item status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      'get item duration < 200ms': (r) => r.timings.duration < 200,
    });

    recordMetrics(res, success, 200, 'get_item');
  });
}

function testSearch() {
  group('Search', function() {
    const searchTerms = ['test', 'feature', 'bug', 'task', 'requirement', 'story', 'epic', 'defect'];
    const query = searchTerms[Math.floor(Math.random() * searchTerms.length)];

    const searchQuery = {
      query: query,
      project_id: PROJECT_ID,
      limit: 25,
      offset: Math.floor(Math.random() * 50),
    };

    const url = `${BASE_URL}/api/v1/search`;
    const res = http.post(url, JSON.stringify(searchQuery), {
      headers: getHeaders(),
      tags: { operation: 'search' },
    });

    const success = check(res, {
      'search status is 200': (r) => r.status === 200,
      'search duration < 500ms': (r) => r.timings.duration < 500,
    });

    recordMetrics(res, success, 500, 'search');
  });
}

function testGraphViewport() {
  group('Graph Viewport', function() {
    const baseX = Math.floor(Math.random() * 10000);
    const baseY = Math.floor(Math.random() * 10000);

    const viewportQuery = {
      viewport: {
        minX: baseX,
        minY: baseY,
        maxX: baseX + 1920,
        maxY: baseY + 1080,
      },
      zoom: 0.5 + Math.random() * 2,
      bufferPx: 500,
    };

    const url = `${BASE_URL}/api/v1/graph/viewport/${PROJECT_ID}`;
    const res = http.post(url, JSON.stringify(viewportQuery), {
      headers: getHeaders(),
      tags: { operation: 'graph_viewport' },
    });

    const success = check(res, {
      'viewport status is 200': (r) => r.status === 200,
      'viewport duration < 700ms': (r) => r.timings.duration < 700,
    });

    recordMetrics(res, success, 700, 'graph_viewport');
  });
}

function testCreateItem() {
  group('Create Item', function() {
    const newItem = {
      project_id: PROJECT_ID,
      title: `72h Soak Item ${Date.now()}-${iterationCount}`,
      description: `Created during 72h soak test at iteration ${iterationCount}`,
      type: ['task', 'bug', 'feature', 'story'][Math.floor(Math.random() * 4)],
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
      'create item duration < 500ms': (r) => r.timings.duration < 500,
    });

    recordMetrics(res, success, 500, 'create_item');
  });
}

function testUpdateItem() {
  group('Update Item', function() {
    const itemId = `item-${Math.floor(Math.random() * 2000)}`;
    const updates = {
      status: ['todo', 'in_progress', 'review', 'done'][Math.floor(Math.random() * 4)],
      priority: Math.floor(Math.random() * 5) + 1,
      description: `Updated at ${Date.now()}`,
    };

    const url = `${BASE_URL}/api/v1/items/${itemId}`;
    const res = http.patch(url, JSON.stringify(updates), {
      headers: getHeaders(),
      tags: { operation: 'update_item' },
    });

    const success = check(res, {
      'update item status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      'update item duration < 400ms': (r) => r.timings.duration < 400,
    });

    recordMetrics(res, success, 400, 'update_item');
  });
}

function testComplexGraphQuery() {
  group('Complex Graph Query', function() {
    const itemId = `item-${Math.floor(Math.random() * 200)}`;
    const depth = 2 + Math.floor(Math.random() * 4);

    const url = `${BASE_URL}/api/v1/graph/descendants/${itemId}?depth=${depth}&include_metadata=true`;
    const res = http.get(url, {
      headers: getHeaders(),
      tags: { operation: 'graph_query' },
    });

    const success = check(res, {
      'graph query status is 200 or 404': (r) => r.status === 200 || r.status === 404,
      'graph query duration < 1000ms': (r) => r.timings.duration < 1000,
    });

    recordMetrics(res, success, 1000, 'graph_query');
  });
}

function performHealthCheck(data) {
  if (!MONITORING_ENDPOINT) return;

  group('System Health Check', function() {
    const res = http.get(MONITORING_ENDPOINT, {
      tags: { operation: 'health_check' },
      timeout: '30s',
    });

    if (res.status === 200) {
      try {
        const metrics = JSON.parse(res.body);
        const elapsedHours = ((Date.now() - data.startTime) / 3600000).toFixed(2);

        // Update gauge metrics
        memoryUsagePercent.add(metrics.memory_usage_percent || 0);
        cacheSize.add(metrics.cache_size_mb || 0);
        connectionPoolSize.add(metrics.connection_pool_size || 0);
        activeConnections.add(metrics.active_connections || 0);

        // Memory leak detection
        if (lastMemoryBaseline === 0) {
          lastMemoryBaseline = metrics.memory_usage_percent;
        } else {
          const memoryGrowth = metrics.memory_usage_percent - lastMemoryBaseline;
          if (memoryGrowth > 10) {
            memoryWarnings.add(1);
            console.warn(`⚠️  Memory growth detected: +${memoryGrowth.toFixed(2)}% over baseline (${elapsedHours}h elapsed)`);
          }
        }

        // High memory warning
        if (metrics.memory_usage_percent > 85) {
          memoryWarnings.add(1);
          console.warn(`⚠️  High memory usage: ${metrics.memory_usage_percent}% at ${elapsedHours}h`);
        }

        // Connection pool monitoring
        if (metrics.connection_pool_size > 90) {
          console.warn(`⚠️  Connection pool high: ${metrics.connection_pool_size} at ${elapsedHours}h`);
        }

        // Cache growth monitoring
        if (metrics.cache_size_mb > 512) {
          console.warn(`⚠️  Cache size large: ${metrics.cache_size_mb}MB at ${elapsedHours}h`);
        }

        console.log(`[${elapsedHours}h] Memory: ${metrics.memory_usage_percent}%, Connections: ${metrics.connection_pool_size}, Cache: ${metrics.cache_size_mb}MB`);

      } catch (e) {
        console.error(`Health check parsing error: ${e.message}`);
      }
    } else {
      console.error(`Health check failed with status ${res.status}`);
    }
  });
}

function recordHourlyMetrics(data) {
  const hour = hourlyMetrics.length + 1;
  console.log(`📊 Hourly checkpoint: ${hour} hour(s) elapsed`);

  hourlyMetrics.push({
    hour: hour,
    timestamp: Date.now(),
  });
}

function recordMetrics(response, success, threshold, operation) {
  apiDuration.add(response.timings.duration, { operation });
  errorRate.add(!success, { operation });

  if (response.timings.duration > threshold) {
    slowRequests.add(1, { operation });

    // Log significant slowdowns during 72h test
    if (response.timings.duration > threshold * 3) {
      const elapsedHours = ((Date.now() - __ENV.START_TIME) / 3600000).toFixed(2);
      console.warn(`🐌 Very slow ${operation}: ${response.timings.duration.toFixed(2)}ms at ${elapsedHours}h (threshold: ${threshold}ms)`);
    }
  }

  if (response.error) {
    connectionErrors.add(1, { operation });
  }

  if (response.error_code === 1050) { // Timeout
    timeoutErrors.add(1, { operation });
  }
}

export function teardown(data) {
  const endTime = Date.now();
  const duration = endTime - data.startTime;
  const durationHours = (duration / 3600000).toFixed(2);

  console.log('✅ 72-hour sustained soak test completed');
  console.log(`End time: ${new Date().toISOString()}`);
  console.log(`Total duration: ${durationHours} hours`);
  console.log(`Total hourly checkpoints: ${hourlyMetrics.length}`);

  if (MONITORING_ENDPOINT) {
    const health = http.get(MONITORING_ENDPOINT);
    if (health.status === 200) {
      const metrics = JSON.parse(health.body);
      console.log(`Final memory usage: ${metrics.memory_usage_percent}%`);
      console.log(`Final connection pool: ${metrics.connection_pool_size}`);
      console.log(`Final cache size: ${metrics.cache_size_mb}MB`);
    }
  }
}

export function handleSummary(data) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');

  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    [`soak-results/72h-sustained-${timestamp}.json`]: JSON.stringify(data, null, 2),
    [`soak-results/72h-sustained-${timestamp}.html`]: htmlReport(data),
    'soak-results/72h-sustained-latest.json': JSON.stringify(data, null, 2),
  };
}
