import ws from 'k6/ws';
import { check } from 'k6';

// Align with frontend: gateway serves WebSocket at /api/v1/ws
const BASE_URL = __ENV.WS_URL || 'ws://localhost:4000/api/v1/ws';

export const options = {
  stages: [
    { duration: '1m', target: 500 },
    { duration: '3m', target: 1000 },
    { duration: '2m', target: 1500 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    'ws_connecting': ['p(95)<5000'],  // Connection under 5s
    'ws_msgs_received': ['count>1000'],
  },
};

export default function() {
  const url = BASE_URL;
  const params = { tags: { my_tag: 'websocket' } };

  const res = ws.connect(url, params, function(socket) {
    socket.on('open', () => {
      console.log('WebSocket connected');

      // Subscribe to project
      socket.send(JSON.stringify({
        type: 'subscribe_project',
        project_id: 'test-project',
      }));

      // Send ping every 30s
      socket.setInterval(() => {
        socket.send(JSON.stringify({ type: 'ping' }));
      }, 30000);
    });

    socket.on('message', (data) => {
      const msg = JSON.parse(data);
      check(msg, {
        'valid message': (m) => m.type !== undefined,
      });
    });

    socket.on('close', () => {
      console.log('WebSocket disconnected');
    });

    socket.setTimeout(() => {
      socket.close();
    }, 180000); // Stay connected for 3 minutes
  });

  check(res, { 'connected': (r) => r && r.status === 101 });
}
