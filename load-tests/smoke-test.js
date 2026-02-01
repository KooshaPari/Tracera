/**
 * Smoke Test - Quick validation that services are working
 * Duration: ~1 minute
 * Load: Minimal (10 users)
 * Purpose: Validate functionality before running full load tests
 */

import http from 'k6/http';
import { check, group, sleep } from 'k6';

const GO_URL = __ENV.GO_BACKEND_URL || 'http://localhost:8080';
const PYTHON_URL = __ENV.PYTHON_BACKEND_URL || 'http://localhost:4000';

export const options = {
  vus: 10,
  duration: '1m',
  thresholds: {
    'http_req_failed': ['rate<0.01'],  // Less than 1% errors
    'http_req_duration': ['p(95)<1000'], // 95% under 1s
  },
};

export default function() {
  group('Go Backend Health', () => {
    const res = http.get(`${GO_URL}/health`);
    check(res, {
      'Go backend is healthy': (r) => r.status === 200,
    });
  });

  group('Python Backend Health', () => {
    const res = http.get(`${PYTHON_URL}/health`);
    check(res, {
      'Python backend is healthy': (r) => r.status === 200,
    });
  });

  group('Basic CRUD Operations', () => {
    // Create project
    let res = http.post(`${GO_URL}/api/v1/projects`, JSON.stringify({
      name: `Smoke Test Project ${Date.now()}`,
    }), {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'project created': (r) => r.status === 201,
    });

    if (res.status === 201) {
      const projectId = JSON.parse(res.body).id;

      // Create item
      res = http.post(`${GO_URL}/api/v1/items`, JSON.stringify({
        title: 'Smoke Test Item',
        project_id: projectId,
        type: 'requirement',
      }), {
        headers: { 'Content-Type': 'application/json' },
      });

      check(res, {
        'item created': (r) => r.status === 201,
      });

      if (res.status === 201) {
        const itemId = JSON.parse(res.body).id;

        // Get item
        res = http.get(`${GO_URL}/api/v1/items/${itemId}`);
        check(res, {
          'item retrieved': (r) => r.status === 200,
        });
      }
    }
  });

  sleep(1);
}

export function handleSummary(data) {
  const passed = data.metrics.checks.values.passes === data.metrics.checks.values.fails + data.metrics.checks.values.passes;

  return {
    'stdout': passed
      ? '\n✓ Smoke test PASSED - All services are healthy\n'
      : '\n✗ Smoke test FAILED - Check backend services\n',
  };
}
