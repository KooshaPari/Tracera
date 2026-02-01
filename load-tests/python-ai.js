import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = __ENV.PYTHON_BACKEND_URL || 'http://localhost:4000';

export const options = {
  stages: [
    { duration: '1m', target: 10 },   // AI is expensive
    { duration: '2m', target: 20 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<10000'],  // 10s for AI
  },
};

export default function() {
  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
  };

  const res = http.post(
    `${BASE_URL}/api/v1/ai/stream-chat`,
    JSON.stringify({
      message: 'Analyze this specification',
      project_id: 'test-project',
    }),
    params
  );

  check(res, {
    'status 200': (r) => r.status === 200,
    'is SSE': (r) => r.headers['Content-Type'].includes('text/event-stream'),
  });
}
