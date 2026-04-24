/**
 * Spike Test Scenario
 *
 * Tests system behavior under sudden load spikes.
 * - Sudden burst to 500 users
 * - Tests auto-scaling and rate limiting
 * - Validates graceful degradation
 *
 * Purpose: Verify system handles traffic spikes (e.g., marketing campaign, viral content)
 *
 * Run: k6 run tests/load/k6/scenarios/spike.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { authenticate, getAuthHeaders, getTestUser } from '../helpers/auth.js';
import { generateItem, generateSearchQuery } from '../helpers/data-generators.js';

// Custom metrics
const errorRate = new Rate('errors');
const apiResponseTime = new Trend('api_response_time');
const rateLimitHits = new Counter('rate_limit_hits');
const queuedRequests = new Counter('queued_requests');
const rejectedRequests = new Counter('rejected_requests');
const successfulRequests = new Counter('successful_requests');
const activeUsers = new Gauge('active_users');
const spikeRecoveryTime = new Trend('spike_recovery_time');

// Test configuration
export const options = {
  stages: [
    { duration: '1m', target: 10 }, // Normal load baseline
    { duration: '10s', target: 500 }, // SPIKE! 10 -> 500 users in 10 seconds
    { duration: '3m', target: 500 }, // Hold spike load
    { duration: '10s', target: 10 }, // Drop back to normal
    { duration: '2m', target: 10 }, // Recovery period
    { duration: '30s', target: 0 }, // Cool down
  ],
  thresholds: {
    // Error rate should stay reasonable even during spike
    'errors': ['rate<0.10'], // Allow up to 10% errors during spike

    // Response times will degrade but should recover
    'http_req_duration': [
      'p(95)<3000', // 95% under 3s (degraded but acceptable)
      'p(99)<5000', // 99% under 5s
    ],

    // API response time
    'api_response_time': ['p(95)<2000'],

    // Most requests should still succeed
    'http_req_failed': ['rate<0.15'], // Allow 15% failures during spike

    // Rate limiting should activate
    'rate_limit_hits': ['count>0'], // Expect rate limiting to kick in
  },
  tags: {
    test_type: 'spike',
    environment: __ENV.TEST_ENV || 'development',
  },
  timeout: '60s',
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:4000';
const API_BASE_URL = `${BASE_URL}/api/v1`;

// Track spike phases
let spikeStartTime = 0;
let spikeRecovered = false;

// Setup function
export function setup() {
  console.log('⚡ Starting Spike Test');
  console.log(`Target: ${BASE_URL}`);
  console.log(`Spike: 10 → 500 users in 10 seconds`);
  console.log(`Duration: ~7.5 minutes`);
  console.warn('⚠️  This test simulates sudden traffic spikes');

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
  const currentVUs = __VU;
  activeUsers.add(currentVUs);

  // Detect spike start (VU count jumps significantly)
  if (currentVUs > 100 && spikeStartTime === 0) {
    spikeStartTime = Date.now();
    console.log('🔥 SPIKE DETECTED! Users ramping up rapidly...');
  }

  let authData;

  // Simplified auth during spike
  const user = getTestUser();
  try {
    authData = authenticate(user);
  } catch (error) {
    errorRate.add(1);
    rejectedRequests.add(1);
    sleep(1);
    return;
  }

  const headers = getAuthHeaders(authData);

  // Execute high-value operations that are commonly accessed during spikes
  const scenario = Math.random();

  if (scenario < 0.4) {
    // 40% - Quick dashboard view (landing page during spike)
    quickDashboardView(headers);
  } else if (scenario < 0.7) {
    // 30% - Search (users looking for specific content)
    searchOperations(headers);
  } else if (scenario < 0.9) {
    // 20% - Item details view
    itemDetailsView(headers);
  } else {
    // 10% - Write operations (fewer during spike)
    createOperations(headers);
  }

  // Very short think time during spike to maximize load
  sleep(Math.random() * 1 + 0.5);
}

// Scenario: Quick dashboard view
function quickDashboardView(headers) {
  group('Quick Dashboard View', () => {
    const startTime = Date.now();

    const response = http.get(
      `${API_BASE_URL}/projects`,
      {
        headers,
        tags: { name: 'spike_dashboard', scenario: 'dashboard' },
      }
    );

    trackSpikeResponse(response, startTime);

    check(response, {
      'Dashboard accessible': (r) => r.status === 200 || r.status === 429,
    }) || errorRate.add(1);
  });
}

// Scenario: Search operations
function searchOperations(headers) {
  group('Search Operations', () => {
    const searchQuery = generateSearchQuery({ limit: 20 }); // Smaller limit during spike
    const startTime = Date.now();

    const response = http.get(
      `${API_BASE_URL}/search?q=${encodeURIComponent(searchQuery.query)}&limit=${searchQuery.limit}`,
      {
        headers,
        tags: { name: 'spike_search', scenario: 'search' },
      }
    );

    trackSpikeResponse(response, startTime);

    check(response, {
      'Search completed or queued': (r) => r.status === 200 || r.status === 202 || r.status === 429,
    }) || errorRate.add(1);
  });
}

// Scenario: Item details view
function itemDetailsView(headers) {
  group('Item Details View', () => {
    // Get random item (simulate clicking on an item from search/dashboard)
    const itemId = Math.floor(Math.random() * 1000) + 1;
    const startTime = Date.now();

    const response = http.get(
      `${API_BASE_URL}/items/${itemId}`,
      {
        headers,
        tags: { name: 'spike_item_details', scenario: 'item_view' },
      }
    );

    trackSpikeResponse(response, startTime);

    check(response, {
      'Item details loaded or queued': (r) => r.status === 200 || r.status === 202 || r.status === 404 || r.status === 429,
    }) || errorRate.add(1);
  });
}

// Scenario: Create operations
function createOperations(headers) {
  group('Create Operations', () => {
    const newItem = generateItem({ projectId: 1 });
    const startTime = Date.now();

    const response = http.post(
      `${API_BASE_URL}/items`,
      JSON.stringify(newItem),
      {
        headers,
        tags: { name: 'spike_create_item', scenario: 'create' },
      }
    );

    trackSpikeResponse(response, startTime);

    check(response, {
      'Create succeeded or queued': (r) => r.status === 200 || r.status === 201 || r.status === 202 || r.status === 429,
    }) || errorRate.add(1);
  });
}

// Helper function to track spike-specific metrics
function trackSpikeResponse(response, startTime) {
  const duration = Date.now() - startTime;
  apiResponseTime.add(response.timings.duration);

  // Track rate limiting (429 Too Many Requests)
  if (response.status === 429) {
    rateLimitHits.add(1);
    console.log('⚠️  Rate limit hit - system protecting itself');
  }

  // Track queued requests (202 Accepted)
  if (response.status === 202) {
    queuedRequests.add(1);
  }

  // Track successful requests
  if (response.status === 200 || response.status === 201) {
    successfulRequests.add(1);

    // Track recovery time after spike
    if (spikeStartTime > 0 && !spikeRecovered && __VU < 50) {
      const recoveryTime = Date.now() - spikeStartTime;
      spikeRecoveryTime.add(recoveryTime);
      spikeRecovered = true;
      console.log(`✅ System recovered in ${recoveryTime}ms`);
    }
  }

  // Track rejected/failed requests
  if (response.status >= 500 || response.status === 0) {
    rejectedRequests.add(1);
    errorRate.add(1);
  }

  // Log critical failures during spike
  if (response.status >= 500 && spikeStartTime > 0) {
    console.error(`❌ Server error during spike: ${response.status} - ${response.request.url}`);
  }
}

// Teardown function
export function teardown(data) {
  console.log('✅ Spike Test Complete');
  console.log(`Started: ${data.startTime}`);
  console.log(`Ended: ${new Date().toISOString()}`);
  console.log('\n📊 Review metrics for:');
  console.log('  - Rate limiting effectiveness');
  console.log('  - Queue depth during spike');
  console.log('  - Recovery time after spike');
  console.log('  - Error rate during peak');
  console.log('  - Graceful degradation patterns');
}

export {
  errorRate,
  apiResponseTime,
  rateLimitHits,
  queuedRequests,
  rejectedRequests,
  successfulRequests,
  activeUsers,
  spikeRecoveryTime,
};
