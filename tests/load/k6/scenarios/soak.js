/**
 * Soak Test Scenario (Endurance Test)
 *
 * Long-duration test to detect memory leaks and resource exhaustion.
 * - 50 concurrent users
 * - 2 hours duration
 * - Monitors for gradual performance degradation
 *
 * Purpose: Validate system stability over extended periods
 *
 * Run: k6 run tests/load/k6/scenarios/soak.js
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
} from '../helpers/data-generators.js';

// Custom metrics for long-running stability
const errorRate = new Rate('errors');
const apiResponseTime = new Trend('api_response_time');
const memoryLeakIndicator = new Trend('response_time_degradation');
const connectionErrors = new Counter('connection_errors');
const authFailures = new Counter('auth_failures');
const databaseErrors = new Counter('database_errors');
const activeConnections = new Gauge('active_connections');
const operationCounter = new Counter('total_operations');

// Baseline tracking for degradation detection
let baselineResponseTime = 0;
let iterationCount = 0;
const responseTimeSamples = [];

// Test configuration
export const options = {
  stages: [
    { duration: '5m', target: 50 }, // Ramp up to 50 users
    { duration: '2h', target: 50 }, // Hold for 2 hours
    { duration: '5m', target: 0 }, // Ramp down
  ],
  thresholds: {
    // Strict thresholds for stability
    'errors': ['rate<0.001'], // Less than 0.1% errors

    // Response times should remain consistent
    'http_req_duration': [
      'p(95)<600', // Should not degrade over time
      'p(99)<1000',
    ],

    // API response time should stay stable
    'api_response_time': [
      'p(95)<500',
      'p(99)<800',
    ],

    // Connection stability
    'connection_errors': ['count<100'], // Very few connection issues

    // Auth should remain stable
    'auth_failures': ['count<10'],

    // Minimal failures
    'http_req_failed': ['rate<0.001'],
  },
  tags: {
    test_type: 'soak',
    environment: __ENV.TEST_ENV || 'development',
  },
  timeout: '60s',
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:4000';
const API_BASE_URL = `${BASE_URL}/api/v1`;

// Setup function
export function setup() {
  console.log('🕐 Starting Soak Test (Endurance Test)');
  console.log(`Target: ${BASE_URL}`);
  console.log(`Concurrent Users: 50`);
  console.log(`Duration: 2 hours 10 minutes`);
  console.warn('⚠️  This is a long-running test - monitor for:');
  console.warn('   - Memory leaks');
  console.warn('   - Connection pool exhaustion');
  console.warn('   - Gradual performance degradation');
  console.warn('   - Resource cleanup issues');

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

// Main test function - simulates realistic long-term usage
export default function (data) {
  activeConnections.add(__VU);
  iterationCount++;
  let authData;

  // Authenticate (reuse auth for multiple iterations)
  if (iterationCount % 100 === 1) {
    // Re-authenticate every 100 iterations to test auth system over time
    const user = getTestUser();
    try {
      authData = authenticate(user);
    } catch (error) {
      authFailures.add(1);
      errorRate.add(1);
      sleep(5);
      return;
    }
  } else {
    // Reuse previous auth
    const user = getTestUser();
    try {
      authData = authenticate(user);
    } catch (error) {
      authFailures.add(1);
      errorRate.add(1);
      sleep(5);
      return;
    }
  }

  const headers = getAuthHeaders(authData);

  // Realistic long-term usage patterns
  const scenario = Math.random();

  if (scenario < 0.30) {
    // 30% - Regular browsing
    regularBrowsingScenario(headers);
  } else if (scenario < 0.55) {
    // 25% - Content creation and updates
    contentManagementScenario(headers);
  } else if (scenario < 0.75) {
    // 20% - Search and discovery
    searchScenario(headers);
  } else if (scenario < 0.90) {
    // 15% - Test case management
    testManagementScenario(headers);
  } else {
    // 10% - Link management
    linkManagementScenario(headers);
  }

  // Realistic think time for long-term usage
  sleep(Math.random() * 5 + 3); // 3-8 seconds between actions
}

// Scenario: Regular browsing
function regularBrowsingScenario(headers) {
  group('Regular Browsing', () => {
    const operations = [
      { name: 'get_projects', url: `${API_BASE_URL}/projects` },
      { name: 'get_items', url: `${API_BASE_URL}/items?limit=20` },
      { name: 'get_dashboard', url: `${API_BASE_URL}/projects/1/dashboard` },
    ];

    operations.forEach((op) => {
      const response = executeOperation(op.name, () =>
        http.get(op.url, { headers, tags: { name: op.name, scenario: 'browsing' } })
      );

      trackLongRunningMetrics(response);
    });
  });
}

// Scenario: Content management
function contentManagementScenario(headers) {
  group('Content Management', () => {
    // Create item
    const newItem = generateItem({ projectId: 1 });
    const createResponse = executeOperation('create_item', () =>
      http.post(`${API_BASE_URL}/items`, JSON.stringify(newItem), {
        headers,
        tags: { name: 'create_item', scenario: 'content' },
      })
    );

    trackLongRunningMetrics(createResponse);

    if (createResponse.status === 200 || createResponse.status === 201) {
      const itemId = createResponse.json().id || createResponse.json().item_id;

      sleep(2);

      // Update item
      const updatedItem = { ...newItem, description: 'Updated for soak test' };
      const updateResponse = executeOperation('update_item', () =>
        http.put(`${API_BASE_URL}/items/${itemId}`, JSON.stringify(updatedItem), {
          headers,
          tags: { name: 'update_item', scenario: 'content' },
        })
      );

      trackLongRunningMetrics(updateResponse);
    }
  });
}

// Scenario: Search
function searchScenario(headers) {
  group('Search Operations', () => {
    const searchQuery = generateSearchQuery({ limit: 30 });

    const response = executeOperation('search', () =>
      http.get(
        `${API_BASE_URL}/search?q=${encodeURIComponent(searchQuery.query)}&limit=${searchQuery.limit}`,
        {
          headers,
          tags: { name: 'search', scenario: 'search' },
        }
      )
    );

    trackLongRunningMetrics(response);
  });
}

// Scenario: Test management
function testManagementScenario(headers) {
  group('Test Management', () => {
    // Get test suites
    const suitesResponse = executeOperation('get_test_suites', () =>
      http.get(`${API_BASE_URL}/test-suites`, {
        headers,
        tags: { name: 'get_test_suites', scenario: 'testing' },
      })
    );

    trackLongRunningMetrics(suitesResponse);

    sleep(1);

    // Create test case
    const testCase = generateTestCase({ projectId: 1 });
    const createResponse = executeOperation('create_test_case', () =>
      http.post(`${API_BASE_URL}/test-cases`, JSON.stringify(testCase), {
        headers,
        tags: { name: 'create_test_case', scenario: 'testing' },
      })
    );

    trackLongRunningMetrics(createResponse);
  });
}

// Scenario: Link management
function linkManagementScenario(headers) {
  group('Link Management', () => {
    // Create link
    const link = generateLink();
    const response = executeOperation('create_link', () =>
      http.post(`${API_BASE_URL}/links`, JSON.stringify(link), {
        headers,
        tags: { name: 'create_link', scenario: 'links' },
      })
    );

    trackLongRunningMetrics(response);
  });
}

// Helper: Execute operation with error tracking
function executeOperation(name, operation) {
  operationCounter.add(1);

  try {
    const response = operation();

    // Track connection errors
    if (response.status === 0 || response.error_code) {
      connectionErrors.add(1);
      errorRate.add(1);
    }

    // Track database errors (503 Service Unavailable often indicates DB issues)
    if (response.status === 503) {
      databaseErrors.add(1);
      errorRate.add(1);
    }

    return response;
  } catch (error) {
    console.error(`Operation ${name} failed: ${error}`);
    connectionErrors.add(1);
    errorRate.add(1);
    throw error;
  }
}

// Helper: Track long-running metrics for degradation detection
function trackLongRunningMetrics(response) {
  const duration = response.timings.duration;
  apiResponseTime.add(duration);

  // Collect samples for baseline
  if (responseTimeSamples.length < 100) {
    responseTimeSamples.push(duration);

    if (responseTimeSamples.length === 100) {
      // Calculate baseline after 100 samples
      baselineResponseTime =
        responseTimeSamples.reduce((sum, val) => sum + val, 0) / responseTimeSamples.length;
      console.log(`📊 Baseline response time established: ${baselineResponseTime.toFixed(2)}ms`);
    }
  }

  // Detect degradation after baseline is established
  if (baselineResponseTime > 0 && responseTimeSamples.length >= 100) {
    const degradation = ((duration - baselineResponseTime) / baselineResponseTime) * 100;
    memoryLeakIndicator.add(degradation);

    // Alert on significant degradation (>50% slower than baseline)
    if (degradation > 50) {
      console.warn(
        `⚠️  Performance degradation detected: ${degradation.toFixed(2)}% slower than baseline`
      );
    }
  }

  // Check response validity
  const success = check(response, {
    'Response successful': (r) => r.status === 200 || r.status === 201,
    'Response time acceptable': (r) => r.timings.duration < 2000,
  });

  if (!success) {
    errorRate.add(1);
  }
}

// Teardown function
export function teardown(data) {
  console.log('✅ Soak Test Complete');
  console.log(`Started: ${data.startTime}`);
  console.log(`Ended: ${new Date().toISOString()}`);
  console.log(`Total iterations: ${iterationCount}`);

  if (baselineResponseTime > 0) {
    console.log(`\n📊 Performance Analysis:`);
    console.log(`  Baseline response time: ${baselineResponseTime.toFixed(2)}ms`);
    console.log(`  Total operations: ${operationCounter}`);
  }

  console.log('\n🔍 Check for:');
  console.log('  - Memory leaks (gradual response time increase)');
  console.log('  - Connection pool issues');
  console.log('  - Database connection leaks');
  console.log('  - Resource cleanup problems');
  console.log('  - Log file growth');
}

export {
  errorRate,
  apiResponseTime,
  memoryLeakIndicator,
  connectionErrors,
  authFailures,
  databaseErrors,
  activeConnections,
  operationCounter,
};
