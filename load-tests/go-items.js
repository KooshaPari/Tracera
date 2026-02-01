import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const BASE_URL = __ENV.GO_BACKEND_URL || 'http://localhost:8080';

const errorRate = new Rate('errors');
const itemCreateLatency = new Trend('item_create_latency');
const itemGetLatency = new Trend('item_get_latency');

export const options = {
  stages: [
    { duration: '30s', target: 100 },   // Ramp up
    { duration: '1m', target: 500 },    // Medium load
    { duration: '2m', target: 1000 },   // Target load
    { duration: '2m', target: 2000 },   // Peak load
    { duration: '30s', target: 0 },     // Ramp down
  ],
  thresholds: {
    'http_req_duration{type:create}': ['p(95)<50'],  // 95% under 50ms
    'http_req_duration{type:get}': ['p(95)<30'],     // 95% under 30ms
    'errors': ['rate<0.01'],                         // Error rate < 1%
    'http_reqs': ['rate>10000'],                     // 10k req/s
  },
};

export function setup() {
  // Create test project
  const res = http.post(`${BASE_URL}/api/v1/projects`, JSON.stringify({
    name: 'Load Test Project',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  return { projectId: JSON.parse(res.body).id };
}

export default function(data) {
  // Create item
  const createRes = http.post(
    `${BASE_URL}/api/v1/items`,
    JSON.stringify({
      title: `Item ${Date.now()}`,
      project_id: data.projectId,
      type: 'requirement',
    }),
    {
      headers: { 'Content-Type': 'application/json' },
      tags: { type: 'create' },
    }
  );

  const success = check(createRes, {
    'create status 201': (r) => r.status === 201,
    'create has id': (r) => JSON.parse(r.body).id !== undefined,
  });

  errorRate.add(!success);
  itemCreateLatency.add(createRes.timings.duration);

  if (success) {
    const itemId = JSON.parse(createRes.body).id;

    // Get item
    const getRes = http.get(`${BASE_URL}/api/v1/items/${itemId}`, {
      tags: { type: 'get' },
    });

    check(getRes, {
      'get status 200': (r) => r.status === 200,
    });

    itemGetLatency.add(getRes.timings.duration);
  }

  sleep(0.1); // 10 req/s per VU
}

export function teardown(data) {
  // Cleanup
  http.del(`${BASE_URL}/api/v1/projects/${data.projectId}`);
}
