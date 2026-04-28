/**
 * Load Test Scenario
 *
 * Standard load test to verify system performance under expected load.
 * - 100 concurrent users
 * - 10 minutes duration
 * - Simulates typical production usage patterns
 *
 * Purpose: Validate performance under normal production load
 *
 * Run: k6 run tests/load/k6/scenarios/load.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { authenticate, getAuthHeaders, getTestUser } from '../helpers/auth.js';
import {
  generateItem,
  generateLink,
  generateTestCase,
  generateSearchQuery,
  generateGraph,
} from '../helpers/data-generators.js';

// Custom metrics
const errorRate = new Rate('errors');
const authDuration = new Trend('auth_duration');
const apiResponseTime = new Trend('api_response_time');
const graphRenderTime = new Trend('graph_render_time');
const searchResponseTime = new Trend('search_response_time');
const requestCounter = new Counter('total_requests');
const activeUsers = new Gauge('active_users');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 20 }, // Warm up to 20 users
    { duration: '3m', target: 100 }, // Ramp up to 100 users
    { duration: '10m', target: 100 }, // Stay at 100 users for 10 minutes
    { duration: '2m', target: 20 }, // Ramp down to 20 users
    { duration: '1m', target: 0 }, // Cool down to 0 users
  ],
  thresholds: {
    // Error rate must be below 0.1%
    'errors': ['rate<0.001'],

    // 95% of requests must complete within 500ms
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],

    // Authentication must complete within 2 seconds
    'auth_duration': ['p(95)<2000'],

    // API response time targets
    'api_response_time': ['p(95)<500', 'p(99)<800'],

    // Graph rendering must complete within 2 seconds
    'graph_render_time': ['p(95)<2000', 'p(99)<3000'],

    // Search must complete within 1 second
    'search_response_time': ['p(95)<1000'],

    // HTTP failure rate must be below 0.1%
    'http_req_failed': ['rate<0.001'],

    // Request rate should maintain at least 500 req/s
    'http_reqs': ['rate>500'],
  },
  tags: {
    test_type: 'load',
    environment: __ENV.TEST_ENV || 'development',
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:4000';
const API_BASE_URL = `${BASE_URL}/api/v1`;

// Setup function
export function setup() {
  console.log('⚡ Starting Load Test');
  console.log(`Target: ${BASE_URL}`);
  console.log(`Peak Concurrent Users: 100`);
  console.log(`Duration: 18 minutes`);

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
  activeUsers.add(1);
  let authData;

  // Group: Authentication (10% of users)
  if (Math.random() < 0.1) {
    group('Authentication', () => {
      const startAuth = Date.now();
      const user = getTestUser();

      try {
        authData = authenticate(user);
        authDuration.add(Date.now() - startAuth);

        check(authData, {
          'Authentication successful': (d) => d.token !== undefined,
        });
      } catch (error) {
        console.error(`Authentication failed: ${error}`);
        errorRate.add(1);
        return;
      }
    });

    sleep(1);
  } else {
    // Reuse existing auth for most users
    const user = getTestUser();
    try {
      authData = authenticate(user);
    } catch (error) {
      errorRate.add(1);
      return;
    }
  }

  const headers = getAuthHeaders(authData);

  // Simulate user behavior with weighted scenarios
  const scenario = Math.random();

  if (scenario < 0.3) {
    // 30% - Dashboard browsing
    dashboardScenario(headers);
  } else if (scenario < 0.5) {
    // 20% - Item management
    itemManagementScenario(headers);
  } else if (scenario < 0.7) {
    // 20% - Search operations
    searchScenario(headers);
  } else if (scenario < 0.85) {
    // 15% - Graph visualization
    graphScenario(headers);
  } else {
    // 15% - Test case management
    testCaseScenario(headers);
  }

  sleep(Math.random() * 3 + 2); // Random think time 2-5 seconds
}

// Scenario: Dashboard browsing
function dashboardScenario(headers) {
  group('Dashboard Browsing', () => {
    // Get projects
    const projectsResponse = http.get(`${API_BASE_URL}/projects`, {
      headers,
      tags: { name: 'get_projects', scenario: 'dashboard' },
    });

    requestCounter.add(1);
    apiResponseTime.add(projectsResponse.timings.duration);

    check(projectsResponse, {
      'Projects loaded': (r) => r.status === 200,
    }) || errorRate.add(1);

    sleep(1);

    // Get project dashboard
    const dashboardResponse = http.get(`${API_BASE_URL}/projects/1/dashboard`, {
      headers,
      tags: { name: 'get_dashboard', scenario: 'dashboard' },
    });

    requestCounter.add(1);
    apiResponseTime.add(dashboardResponse.timings.duration);

    check(dashboardResponse, {
      'Dashboard loaded': (r) => r.status === 200,
    }) || errorRate.add(1);

    sleep(1);

    // Get recent items
    const itemsResponse = http.get(`${API_BASE_URL}/items?limit=20&sort=updated_at`, {
      headers,
      tags: { name: 'get_recent_items', scenario: 'dashboard' },
    });

    requestCounter.add(1);
    apiResponseTime.add(itemsResponse.timings.duration);

    check(itemsResponse, {
      'Recent items loaded': (r) => r.status === 200,
    }) || errorRate.add(1);
  });
}

// Scenario: Item management
function itemManagementScenario(headers) {
  group('Item Management', () => {
    // Create item
    const newItem = generateItem({ projectId: 1 });
    const createResponse = http.post(
      `${API_BASE_URL}/items`,
      JSON.stringify(newItem),
      {
        headers,
        tags: { name: 'create_item', scenario: 'item_management' },
      }
    );

    requestCounter.add(1);
    apiResponseTime.add(createResponse.timings.duration);

    const createCheck = check(createResponse, {
      'Item created': (r) => r.status === 200 || r.status === 201,
    });

    if (!createCheck) {
      errorRate.add(1);
      return;
    }

    const createdItem = createResponse.json();
    const itemId = createdItem.id || createdItem.item_id;

    sleep(1);

    // Update item
    const updatedItem = { ...newItem, description: 'Updated description' };
    const updateResponse = http.put(
      `${API_BASE_URL}/items/${itemId}`,
      JSON.stringify(updatedItem),
      {
        headers,
        tags: { name: 'update_item', scenario: 'item_management' },
      }
    );

    requestCounter.add(1);
    apiResponseTime.add(updateResponse.timings.duration);

    check(updateResponse, {
      'Item updated': (r) => r.status === 200,
    }) || errorRate.add(1);

    sleep(1);

    // Create link
    const link = generateLink({ sourceId: itemId });
    const linkResponse = http.post(
      `${API_BASE_URL}/links`,
      JSON.stringify(link),
      {
        headers,
        tags: { name: 'create_link', scenario: 'item_management' },
      }
    );

    requestCounter.add(1);
    apiResponseTime.add(linkResponse.timings.duration);

    check(linkResponse, {
      'Link created': (r) => r.status === 200 || r.status === 201,
    }) || errorRate.add(1);
  });
}

// Scenario: Search operations
function searchScenario(headers) {
  group('Search Operations', () => {
    const searchQuery = generateSearchQuery({ limit: 50 });

    const startSearch = Date.now();
    const searchResponse = http.get(
      `${API_BASE_URL}/search?q=${encodeURIComponent(searchQuery.query)}&limit=${searchQuery.limit}&type=${searchQuery.filters.type || ''}`,
      {
        headers,
        tags: { name: 'search_items', scenario: 'search' },
      }
    );

    const searchDuration = Date.now() - startSearch;

    requestCounter.add(1);
    apiResponseTime.add(searchResponse.timings.duration);
    searchResponseTime.add(searchDuration);

    check(searchResponse, {
      'Search completed': (r) => r.status === 200,
      'Search results returned': (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body.results) || Array.isArray(body);
        } catch {
          return false;
        }
      },
    }) || errorRate.add(1);
  });
}

// Scenario: Graph visualization
function graphScenario(headers) {
  group('Graph Visualization', () => {
    const startGraph = Date.now();

    // Get graph data (simulate 1000 nodes)
    const graphResponse = http.get(
      `${API_BASE_URL}/graphs/1?nodes=1000`,
      {
        headers,
        tags: { name: 'get_graph', scenario: 'graph' },
      }
    );

    const graphDuration = Date.now() - startGraph;

    requestCounter.add(1);
    apiResponseTime.add(graphResponse.timings.duration);
    graphRenderTime.add(graphDuration);

    check(graphResponse, {
      'Graph data loaded': (r) => r.status === 200,
      'Graph has nodes': (r) => {
        try {
          const body = JSON.parse(r.body);
          return body.nodes && body.nodes.length > 0;
        } catch {
          return false;
        }
      },
    }) || errorRate.add(1);
  });
}

// Scenario: Test case management
function testCaseScenario(headers) {
  group('Test Case Management', () => {
    // Get test suites
    const suitesResponse = http.get(`${API_BASE_URL}/test-suites`, {
      headers,
      tags: { name: 'get_test_suites', scenario: 'test_cases' },
    });

    requestCounter.add(1);
    apiResponseTime.add(suitesResponse.timings.duration);

    check(suitesResponse, {
      'Test suites loaded': (r) => r.status === 200,
    }) || errorRate.add(1);

    sleep(1);

    // Create test case
    const testCase = generateTestCase({ projectId: 1 });
    const createResponse = http.post(
      `${API_BASE_URL}/test-cases`,
      JSON.stringify(testCase),
      {
        headers,
        tags: { name: 'create_test_case', scenario: 'test_cases' },
      }
    );

    requestCounter.add(1);
    apiResponseTime.add(createResponse.timings.duration);

    check(createResponse, {
      'Test case created': (r) => r.status === 200 || r.status === 201,
    }) || errorRate.add(1);
  });
}

// Teardown function
export function teardown(data) {
  console.log('✅ Load Test Complete');
  console.log(`Started: ${data.startTime}`);
  console.log(`Ended: ${new Date().toISOString()}`);
}

export {
  errorRate,
  authDuration,
  apiResponseTime,
  graphRenderTime,
  searchResponseTime,
  requestCounter,
  activeUsers,
};
