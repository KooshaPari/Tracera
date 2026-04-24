/**
 * Smoke Test Scenario
 *
 * Minimal load test to verify system is functioning correctly.
 * - 1-5 concurrent users
 * - 1 minute duration
 * - Tests critical paths with minimal load
 *
 * Purpose: Quick sanity check before running larger load tests
 *
 * Run: k6 run tests/load/k6/scenarios/smoke.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { authenticate, getAuthHeaders, getTestUser } from '../helpers/auth.js';
import { generateItem, generateSearchQuery } from '../helpers/data-generators.js';

// Custom metrics
const errorRate = new Rate('errors');
const authDuration = new Trend('auth_duration');
const apiResponseTime = new Trend('api_response_time');
const requestCounter = new Counter('total_requests');

// Test configuration
export const options = {
  stages: [
    { duration: '10s', target: 1 }, // Ramp up to 1 user
    { duration: '30s', target: 5 }, // Ramp up to 5 users
    { duration: '20s', target: 0 }, // Ramp down to 0 users
  ],
  thresholds: {
    // Error rate must be below 1%
    'errors': ['rate<0.01'],

    // 95% of requests must complete within 500ms
    'http_req_duration': ['p(95)<500'],

    // Authentication must complete within 1 second
    'auth_duration': ['p(95)<1000'],

    // API response time targets
    'api_response_time': ['p(95)<300', 'p(99)<500'],

    // HTTP failure rate must be below 1%
    'http_req_failed': ['rate<0.01'],
  },
  tags: {
    test_type: 'smoke',
    environment: __ENV.TEST_ENV || 'development',
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:4000';
const API_BASE_URL = `${BASE_URL}/api/v1`;

// Setup function - runs once before test
export function setup() {
  console.log('🔥 Starting Smoke Test');
  console.log(`Target: ${BASE_URL}`);

  // Verify system is accessible
  const healthCheck = http.get(`${BASE_URL}/health`, {
    tags: { name: 'health_check' },
  });

  check(healthCheck, {
    'System is accessible': (r) => r.status === 200,
  });

  return {
    baseUrl: BASE_URL,
    apiBaseUrl: API_BASE_URL,
    startTime: new Date().toISOString(),
  };
}

// Main test function - runs for each VU iteration
export default function (data) {
  let authData;

  // Group: Authentication
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
      return; // Skip rest of test if auth fails
    }
  });

  sleep(1);

  // Group: Project Dashboard
  group('Project Dashboard', () => {
    const headers = getAuthHeaders(authData);

    // Get projects list
    const projectsResponse = http.get(
      `${API_BASE_URL}/projects`,
      {
        headers,
        tags: { name: 'get_projects' },
      }
    );

    requestCounter.add(1);
    apiResponseTime.add(projectsResponse.timings.duration);

    const projectsCheck = check(projectsResponse, {
      'Projects loaded': (r) => r.status === 200,
      'Projects response time OK': (r) => r.timings.duration < 500,
      'Projects has data': (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body.projects) || Array.isArray(body);
        } catch {
          return false;
        }
      },
    });

    if (!projectsCheck) {
      errorRate.add(1);
    }
  });

  sleep(1);

  // Group: Items CRUD
  group('Items Operations', () => {
    const headers = getAuthHeaders(authData);

    // Create a new item
    const newItem = generateItem({ projectId: 1 });
    const createResponse = http.post(
      `${API_BASE_URL}/items`,
      JSON.stringify(newItem),
      {
        headers,
        tags: { name: 'create_item' },
      }
    );

    requestCounter.add(1);
    apiResponseTime.add(createResponse.timings.duration);

    const createCheck = check(createResponse, {
      'Item created': (r) => r.status === 200 || r.status === 201,
      'Create response time OK': (r) => r.timings.duration < 500,
    });

    if (!createCheck) {
      errorRate.add(1);
      return;
    }

    const createdItem = createResponse.json();
    const itemId = createdItem.id || createdItem.item_id;

    sleep(0.5);

    // Get the created item
    const getResponse = http.get(
      `${API_BASE_URL}/items/${itemId}`,
      {
        headers,
        tags: { name: 'get_item' },
      }
    );

    requestCounter.add(1);
    apiResponseTime.add(getResponse.timings.duration);

    const getCheck = check(getResponse, {
      'Item retrieved': (r) => r.status === 200,
      'Get response time OK': (r) => r.timings.duration < 300,
    });

    if (!getCheck) {
      errorRate.add(1);
    }
  });

  sleep(1);

  // Group: Search
  group('Search Operations', () => {
    const headers = getAuthHeaders(authData);
    const searchQuery = generateSearchQuery({ limit: 20 });

    const searchResponse = http.get(
      `${API_BASE_URL}/search?q=${encodeURIComponent(searchQuery.query)}&limit=${searchQuery.limit}`,
      {
        headers,
        tags: { name: 'search_items' },
      }
    );

    requestCounter.add(1);
    apiResponseTime.add(searchResponse.timings.duration);

    const searchCheck = check(searchResponse, {
      'Search completed': (r) => r.status === 200,
      'Search response time OK': (r) => r.timings.duration < 500,
    });

    if (!searchCheck) {
      errorRate.add(1);
    }
  });

  sleep(2);
}

// Teardown function - runs once after test
export function teardown(data) {
  console.log('✅ Smoke Test Complete');
  console.log(`Started: ${data.startTime}`);
  console.log(`Ended: ${new Date().toISOString()}`);
}

export { errorRate, authDuration, apiResponseTime, requestCounter };
