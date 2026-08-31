import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';
import config from './config.json';

const failRate = new Rate('failed_requests');

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8080';

export const options = {
  stages: config.ramp_stages,
  thresholds: config.thresholds,
};

export default function () {
  const endpoints = Object.values(config.endpoints);
  
  // Weighted random selection
  const totalWeight = endpoints.reduce((sum, e) => sum + e.weight, 0);
  let random = Math.random() * totalWeight;
  let selected;
  
  for (const endpoint of endpoints) {
    random -= endpoint.weight;
    if (random <= 0) {
      selected = endpoint;
      break;
    }
  }

  if (!selected) return;

  const url = `${BASE_URL}${selected.path}`;
  let res;

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (selected.method === 'GET') {
    res = http.get(url, params);
  } else {
    const payload = JSON.stringify({ test: true, timestamp: Date.now() });
    res = http.post(url, payload, params);
  }

  const passed = check(res, {
    'status is correct': (r) => r.status === 200 || r.status === 201,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  failRate.add(!passed);
  sleep(0.1);
}
