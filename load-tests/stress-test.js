/**
 * Stress Test - Find breaking point of the system
 * Duration: ~15 minutes
 * Load: Ramps up to extreme levels
 * Purpose: Identify maximum capacity and failure modes
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

const GO_URL = __ENV.GO_BACKEND_URL || 'http://localhost:8080';
const PYTHON_URL = __ENV.PYTHON_BACKEND_URL || 'http://localhost:4000';

// Custom metrics
const errorRate = new Rate('errors');
const latencyTrend = new Trend('custom_latency');
const requestCounter = new Counter('custom_requests');

export const options = {
  stages: [
    // Normal load
    { duration: '2m', target: 100 },

    // Ramp up to target load
    { duration: '3m', target: 1000 },

    // Sustain target load
    { duration: '2m', target: 1000 },

    // Push beyond target
    { duration: '3m', target: 2000 },

    // Stress to breaking point
    { duration: '2m', target: 5000 },

    // Sustain stress
    { duration: '1m', target: 5000 },

    // Recovery
    { duration: '2m', target: 0 },
  ],

  thresholds: {
    'http_req_duration': ['p(99)<5000'],  // 99% under 5s (stress conditions)
    'http_req_failed': ['rate<0.05'],     // Accept up to 5% errors under stress
  },
};

export function setup() {
  // Create test projects
  const projects = [];

  for (let i = 0; i < 10; i++) {
    const res = http.post(`${GO_URL}/api/v1/projects`, JSON.stringify({
      name: `Stress Test Project ${i}`,
    }), {
      headers: { 'Content-Type': 'application/json' },
    });

    if (res.status === 201) {
      projects.push(JSON.parse(res.body).id);
    }
  }

  return { projects };
}

export default function(data) {
  const projectId = data.projects[Math.floor(Math.random() * data.projects.length)];

  // Mix of operations
  const operation = Math.random();

  if (operation < 0.4) {
    // 40% - Create items
    const start = Date.now();
    const res = http.post(
      `${GO_URL}/api/v1/items`,
      JSON.stringify({
        title: `Stress Item ${Date.now()}`,
        project_id: projectId,
        type: 'requirement',
      }),
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );

    const success = check(res, {
      'create item success': (r) => r.status === 201,
    });

    errorRate.add(!success);
    latencyTrend.add(Date.now() - start);
    requestCounter.add(1);

  } else if (operation < 0.7) {
    // 30% - List items
    const start = Date.now();
    const res = http.get(`${GO_URL}/api/v1/items?project_id=${projectId}`);

    const success = check(res, {
      'list items success': (r) => r.status === 200,
    });

    errorRate.add(!success);
    latencyTrend.add(Date.now() - start);
    requestCounter.add(1);

  } else if (operation < 0.9) {
    // 20% - Search
    const start = Date.now();
    const res = http.get(`${GO_URL}/api/v1/search?q=test&project_id=${projectId}`);

    const success = check(res, {
      'search success': (r) => r.status === 200,
    });

    errorRate.add(!success);
    latencyTrend.add(Date.now() - start);
    requestCounter.add(1);

  } else {
    // 10% - Python spec analytics
    const start = Date.now();
    const res = http.post(
      `${PYTHON_URL}/api/v1/spec-analytics/analyze`,
      JSON.stringify({
        spec_id: `spec-${Date.now()}`,
        content: 'The system shall respond within 100ms',
        project_id: projectId,
      }),
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );

    const success = check(res, {
      'analytics success': (r) => r.status === 200,
    });

    errorRate.add(!success);
    latencyTrend.add(Date.now() - start);
    requestCounter.add(1);
  }

  sleep(0.05 + Math.random() * 0.1); // Random sleep 50-150ms
}

export function handleSummary(data) {
  const maxVUs = Math.max(...data.metrics.vus.values);
  const totalRequests = data.metrics.http_reqs.values.count;
  const failedRequests = data.metrics.http_req_failed.values.rate * totalRequests;
  const p95Latency = data.metrics.http_req_duration.values['p(95)'];
  const p99Latency = data.metrics.http_req_duration.values['p(99)'];

  console.log('\n=== Stress Test Summary ===');
  console.log(`Peak Concurrent Users: ${maxVUs}`);
  console.log(`Total Requests: ${totalRequests.toFixed(0)}`);
  console.log(`Failed Requests: ${failedRequests.toFixed(0)} (${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%)`);
  console.log(`P95 Latency: ${p95Latency.toFixed(2)}ms`);
  console.log(`P99 Latency: ${p99Latency.toFixed(2)}ms`);
  console.log('===========================\n');

  return {
    'stdout': '',
    'load-test-results/stress-test-summary.json': JSON.stringify({
      peak_vus: maxVUs,
      total_requests: totalRequests,
      failed_requests: failedRequests,
      error_rate: data.metrics.http_req_failed.values.rate,
      p95_latency: p95Latency,
      p99_latency: p99Latency,
    }, null, 2),
  };
}
