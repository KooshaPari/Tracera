import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = __ENV.GO_BACKEND_URL || 'http://localhost:8080';

export const options = {
  stages: [
    { duration: '1m', target: 50 },
    { duration: '3m', target: 100 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<100'],  // Graph ops can be slower
  },
};

export default function() {
  const res = http.post(
    `${BASE_URL}/api/v1/graph/analyze`,
    JSON.stringify({
      project_id: 'test-project',
      algorithm: 'shortest_path',
      source: 'item-1',
      target: 'item-2',
    }),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );

  check(res, {
    'status 200': (r) => r.status === 200,
    'has path': (r) => JSON.parse(r.body).path !== undefined,
  });
}
