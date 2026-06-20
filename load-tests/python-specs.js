import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = __ENV.PYTHON_BACKEND_URL || 'http://localhost:4000';

export const options = {
  stages: [
    { duration: '30s', target: 50 },
    { duration: '2m', target: 200 },
    { duration: '1m', target: 500 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500'],  // Python target: 500ms p95
    'http_reqs': ['rate>1000'],          // 1k req/s
  },
};

export default function() {
  const res = http.post(
    `${BASE_URL}/api/v1/spec-analytics/analyze`,
    JSON.stringify({
      spec_id: 'test-spec',
      content: 'The system shall respond within 100ms',
      project_id: 'test-project',
    }),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );

  check(res, {
    'status 200': (r) => r.status === 200,
    'has ISO compliance': (r) => JSON.parse(r.body).compliant_with_iso !== undefined,
    'has EARS patterns': (r) => JSON.parse(r.body).ears_patterns !== undefined,
  });
}
