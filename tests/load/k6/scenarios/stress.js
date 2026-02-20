/**
 * Stress Test Scenario
 *
 * High-load test to find system breaking points.
 * - Ramp up to 1000 concurrent users over 10 minutes
 * - Identifies performance degradation and failure points
 * - Tests system resilience under extreme load
 *
 * Purpose: Discover capacity limits and breaking points
 *
 * Run: k6 run tests/load/k6/scenarios/stress.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { authenticate, getAuthHeaders, getTestUser } from '../helpers/auth.js';
import {
  generateItem,
  generateSearchQuery,
  generateBatch,
} from '../helpers/data-generators.js';

// Custom metrics
const errorRate = new Rate('errors');
const apiResponseTime = new Trend('api_response_time');
const slowRequests = new Rate('slow_requests'); // Requests > 1s
const timeouts = new Counter('timeouts');
const serverErrors = new Counter('server_errors');
const clientErrors = new Counter('client_errors');
const activeConnections = new Gauge('active_connections');
const requestRate = new Rate('request_rate');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 100 }, // Warm up to 100 users
    { duration: '3m', target: 300 }, // Ramp up to 300 users
    { duration: '5m', target: 600 }, // Ramp up to 600 users
    { duration: '5m', target: 1000 }, // Push to 1000 users
    { duration: '5m', target: 1000 }, // Hold at peak load
    { duration: '3m', target: 500 }, // Start recovery
    { duration: '2m', target: 0 }, // Full recovery
  ],
  thresholds: {
    // Relaxed thresholds - we expect some failures at peak load
    'errors': ['rate<0.05'], // Allow up to 5% errors at peak

    // Performance degradation is expected
    'http_req_duration': ['p(95)<2000', 'p(99)<5000'],

    // Track slow requests
    'slow_requests': ['rate<0.20'], // Allow 20% slow requests

    // API response time - degraded performance expected
    'api_response_time': ['p(95)<2000', 'p(99)<3000'],

    // HTTP failure rate - allow some failures
    'http_req_failed': ['rate<0.05'],
  },
  tags: {
    test_type: 'stress',
    environment: __ENV.TEST_ENV || 'development',
  },
  // Increase timeout for high-load scenarios
  timeout: '60s',
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:4000';
const API_BASE_URL = `${BASE_URL}/api/v1`;

// Setup function
export function setup() {
  console.log('💥 Starting Stress Test');
  console.log(`Target: ${BASE_URL}`);
  console.log(`Peak Concurrent Users: 1000`);
  console.log(`Duration: 25 minutes`);
  console.warn('⚠️  This test is designed to push the system to its limits');
  console.warn('⚠️  Performance degradation and errors are expected');

  // Verify system is accessible
  const healthCheck = http.get(`${BASE_URL}/health`);

  check(healthCheck, {
    'System is accessible': (r) => r.status === 200,
  });

  return {
    baseUrl: BASE_URL,
    apiBaseUrl: API_BASE_URL,
    startTime: new Date().toISOString(),
  };
}

// Main test function
export default function (data) {
  activeConnections.add(__VU);
  let authData;

  // Simplified auth for stress test
  const user = getTestUser();
  try {
    authData = authenticate(user);
  } catch (error) {
    errorRate.add(1);
    clientErrors.add(1);
    sleep(1);
    return;
  }

  const headers = getAuthHeaders(authData);

  // Mix of heavy operations
  const scenario = Math.random();

  if (scenario < 0.25) {
    // 25% - Heavy read operations
    heavyReadScenario(headers);
  } else if (scenario < 0.45) {
    // 20% - Bulk write operations
    bulkWriteScenario(headers);
  } else if (scenario < 0.65) {
    // 20% - Complex search queries
    complexSearchScenario(headers);
  } else if (scenario < 0.85) {
    // 20% - Graph operations (resource intensive)
    graphOperationsScenario(headers);
  } else {
    // 15% - Mixed operations
    mixedOperationsScenario(headers);
  }

  // Shorter think time to increase load
  sleep(Math.random() * 2 + 0.5);
}

// Scenario: Heavy read operations
function heavyReadScenario(headers) {
  group('Heavy Read Operations', () => {
    // Multiple concurrent reads
    const batch = http.batch([
      ['GET', `${API_BASE_URL}/projects`, null, { headers, tags: { name: 'batch_get_projects' } }],
      ['GET', `${API_BASE_URL}/items?limit=100`, null, { headers, tags: { name: 'batch_get_items' } }],
      ['GET', `${API_BASE_URL}/test-cases?limit=100`, null, { headers, tags: { name: 'batch_get_tests' } }],
      ['GET', `${API_BASE_URL}/links?limit=100`, null, { headers, tags: { name: 'batch_get_links' } }],
    ]);

    batch.forEach((response) => {
      requestRate.add(1);
      trackResponse(response);
    });
  });
}

// Scenario: Bulk write operations
function bulkWriteScenario(headers) {
  group('Bulk Write Operations', () => {
    // Create multiple items in quick succession
    const items = generateBatch(10, { projectId: 1 });

    items.forEach((item) => {
      const response = http.post(
        `${API_BASE_URL}/items`,
        JSON.stringify(item),
        {
          headers,
          tags: { name: 'bulk_create_item', scenario: 'bulk_write' },
        }
      );

      requestRate.add(1);
      trackResponse(response);

      // Very short sleep between writes
      sleep(0.1);
    });
  });
}

// Scenario: Complex search queries
function complexSearchScenario(headers) {
  group('Complex Search Queries', () => {
    // Multiple search queries with different filters
    const queries = [
      generateSearchQuery({ limit: 100 }),
      generateSearchQuery({ limit: 200 }),
      generateSearchQuery({ limit: 50 }),
    ];

    queries.forEach((query) => {
      const params = new URLSearchParams({
        q: query.query,
        limit: query.limit,
        type: query.filters.type || '',
        status: query.filters.status || '',
        sort: query.sort,
        order: query.order,
      });

      const response = http.get(
        `${API_BASE_URL}/search?${params}`,
        {
          headers,
          tags: { name: 'complex_search', scenario: 'search' },
        }
      );

      requestRate.add(1);
      trackResponse(response);

      sleep(0.2);
    });
  });
}

// Scenario: Graph operations (resource intensive)
function graphOperationsScenario(headers) {
  group('Graph Operations', () => {
    // Request large graph with many nodes
    const response = http.get(
      `${API_BASE_URL}/graphs/1?nodes=10000&edges=15000`,
      {
        headers,
        tags: { name: 'large_graph', scenario: 'graph' },
        timeout: '30s',
      }
    );

    requestRate.add(1);
    trackResponse(response);

    // Check if graph data is valid
    check(response, {
      'Graph data structure valid': (r) => {
        if (r.status !== 200) return false;
        try {
          const body = JSON.parse(r.body);
          return body.nodes !== undefined && body.edges !== undefined;
        } catch {
          return false;
        }
      },
    }) || errorRate.add(1);
  });
}

// Scenario: Mixed operations
function mixedOperationsScenario(headers) {
  group('Mixed Operations', () => {
    // Random mix of operations
    const operations = [
      () => http.get(`${API_BASE_URL}/projects`, { headers }),
      () => http.get(`${API_BASE_URL}/items?limit=50`, { headers }),
      () => http.post(`${API_BASE_URL}/items`, JSON.stringify(generateItem()), { headers }),
      () => http.get(`${API_BASE_URL}/search?q=test&limit=20`, { headers }),
    ];

    // Execute 3-5 random operations
    const opCount = Math.floor(Math.random() * 3) + 3;
    for (let i = 0; i < opCount; i++) {
      const operation = operations[Math.floor(Math.random() * operations.length)];
      const response = operation();

      requestRate.add(1);
      trackResponse(response);

      sleep(0.1);
    }
  });
}

// Helper function to track response metrics
function trackResponse(response) {
  apiResponseTime.add(response.timings.duration);

  // Track slow requests (>1s)
  if (response.timings.duration > 1000) {
    slowRequests.add(1);
  }

  // Track timeouts
  if (response.status === 0 || response.error_code === 1050) {
    timeouts.add(1);
    errorRate.add(1);
  }

  // Track server errors (5xx)
  if (response.status >= 500 && response.status < 600) {
    serverErrors.add(1);
    errorRate.add(1);
  }

  // Track client errors (4xx, excluding 401 auth)
  if (response.status >= 400 && response.status < 500 && response.status !== 401) {
    clientErrors.add(1);
    errorRate.add(1);
  }

  // Basic success check
  const success = check(response, {
    'Request successful': (r) => r.status === 200 || r.status === 201,
  });

  if (!success && response.status !== 0) {
    console.error(`Request failed: ${response.request.url} - Status: ${response.status}`);
  }
}

// Teardown function
export function teardown(data) {
  console.log('✅ Stress Test Complete');
  console.log(`Started: ${data.startTime}`);
  console.log(`Ended: ${new Date().toISOString()}`);
  console.log('\n📊 Review metrics for:');
  console.log('  - Error rate and types');
  console.log('  - Response time degradation');
  console.log('  - Resource exhaustion points');
  console.log('  - Recovery behavior');
}

export {
  errorRate,
  apiResponseTime,
  slowRequests,
  timeouts,
  serverErrors,
  clientErrors,
  activeConnections,
  requestRate,
};
