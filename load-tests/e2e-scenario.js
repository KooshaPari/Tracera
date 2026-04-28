import http from 'k6/http';
import { check, sleep } from 'k6';

const GO_URL = __ENV.GO_BACKEND_URL || 'http://localhost:8080';
const PYTHON_URL = __ENV.PYTHON_BACKEND_URL || 'http://localhost:4000';

export const options = {
  scenarios: {
    user_journey: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 100 },
        { duration: '5m', target: 500 },
        { duration: '2m', target: 0 },
      ],
    },
  },
  thresholds: {
    'http_req_duration': ['p(95)<1000'],
  },
};

export default function() {
  // 1. Create project (Go)
  let res = http.post(`${GO_URL}/api/v1/projects`, JSON.stringify({
    name: `Project ${__VU}-${Date.now()}`,
  }), { headers: { 'Content-Type': 'application/json' } });

  const projectId = JSON.parse(res.body).id;

  // 2. Create items (Go)
  for (let i = 0; i < 5; i++) {
    http.post(`${GO_URL}/api/v1/items`, JSON.stringify({
      title: `Item ${i}`,
      project_id: projectId,
    }), { headers: { 'Content-Type': 'application/json' } });
  }

  sleep(1);

  // 3. Create specification (Python)
  res = http.post(`${PYTHON_URL}/api/v1/specifications`, JSON.stringify({
    title: 'Test Spec',
    content: 'The system shall be reliable',
    project_id: projectId,
  }), { headers: { 'Content-Type': 'application/json' } });

  const specId = JSON.parse(res.body).id;

  // 4. Analyze spec (Python)
  http.post(`${PYTHON_URL}/api/v1/spec-analytics/analyze`, JSON.stringify({
    spec_id: specId,
    content: 'The system shall be reliable',
    project_id: projectId,
  }), { headers: { 'Content-Type': 'application/json' } });

  sleep(2);

  // 5. Get graph (Go)
  http.get(`${GO_URL}/api/v1/graph/${projectId}`);

  // 6. Search (Go)
  http.get(`${GO_URL}/api/v1/search?q=test&project_id=${projectId}`);

  sleep(1);
}
