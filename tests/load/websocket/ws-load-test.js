/**
 * WebSocket Load Test
 *
 * Tests WebSocket performance under high connection count and message throughput.
 * - 5000+ concurrent WebSocket connections
 * - Message broadcasting performance
 * - Connection stability over time
 * - Reconnection storm handling
 *
 * Run: k6 run tests/load/websocket/ws-load-test.js
 */

import ws from 'k6/ws';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter, Gauge } from 'k6/metrics';
import { authenticate, getTestUser } from '../k6/helpers/auth.js';
import { generateWebSocketMessage } from '../k6/helpers/data-generators.js';

// Custom metrics
const wsConnectionTime = new Trend('ws_connection_time');
const wsMessageLatency = new Trend('ws_message_latency');
const wsConnectionErrors = new Counter('ws_connection_errors');
const wsMessageErrors = new Counter('ws_message_errors');
const activeConnections = new Gauge('ws_active_connections');
const messagesReceived = new Counter('ws_messages_received');
const messagesSent = new Counter('ws_messages_sent');
const reconnectionAttempts = new Counter('ws_reconnection_attempts');
const connectionDrops = new Counter('ws_connection_drops');
const broadcastLatency = new Trend('ws_broadcast_latency');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 100 }, // Warm up to 100 connections
    { duration: '3m', target: 1000 }, // Ramp to 1000 connections
    { duration: '5m', target: 5000 }, // Scale to 5000 connections
    { duration: '10m', target: 5000 }, // Hold at 5000 connections
    { duration: '2m', target: 1000 }, // Scale down
    { duration: '1m', target: 0 }, // Close all connections
  ],
  thresholds: {
    // Connection establishment should be fast
    'ws_connection_time': ['p(95)<1000', 'p(99)<2000'],

    // Message latency should be low
    'ws_message_latency': ['p(95)<200', 'p(99)<500'],

    // Broadcast latency (fan-out)
    'ws_broadcast_latency': ['p(95)<500', 'p(99)<1000'],

    // Connection error rate should be minimal
    'ws_connection_errors': ['count<100'],

    // Message error rate should be very low
    'ws_message_errors': ['count<50'],

    // Connection drops should be minimal
    'ws_connection_drops': ['count<100'],
  },
  tags: {
    test_type: 'websocket_load',
    environment: __ENV.TEST_ENV || 'development',
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:4000';
const WS_URL = BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://');
const WS_ENDPOINT = `${WS_URL}/ws`;

// Setup function
export function setup() {
  console.log('🔌 Starting WebSocket Load Test');
  console.log(`Target: ${WS_URL}`);
  console.log(`Peak Concurrent Connections: 5000`);
  console.log(`Duration: 23 minutes`);

  return {
    wsUrl: WS_URL,
    wsEndpoint: WS_ENDPOINT,
    startTime: new Date().toISOString(),
  };
}

// Main test function
export default function (data) {
  const user = getTestUser();
  let authData;

  // Authenticate to get token for WebSocket connection
  try {
    authData = authenticate(user);
  } catch (error) {
    wsConnectionErrors.add(1);
    console.error(`Auth failed for WebSocket: ${error}`);
    sleep(5);
    return;
  }

  // Establish WebSocket connection with auth token
  const wsUrl = `${data.wsEndpoint}?token=${authData.token}`;
  const startConnection = Date.now();

  const params = {
    headers: {
      'Authorization': `Bearer ${authData.token}`,
    },
    tags: {
      ws_endpoint: 'main',
    },
  };

  const res = ws.connect(wsUrl, params, function (socket) {
    const connectionTime = Date.now() - startConnection;
    wsConnectionTime.add(connectionTime);
    activeConnections.add(1);

    socket.on('open', () => {
      console.log(`✅ WebSocket connected (VU: ${__VU}, Connection time: ${connectionTime}ms)`);

      // Send periodic messages
      socket.setInterval(() => {
        const message = generateWebSocketMessage();
        const messageSentTime = Date.now();

        socket.send(JSON.stringify({
          ...message,
          _sentAt: messageSentTime,
        }));

        messagesSent.add(1);
      }, 5000); // Send message every 5 seconds

      // Send a subscription message
      socket.send(JSON.stringify({
        type: 'subscribe',
        channels: ['project_updates', 'notifications'],
        timestamp: new Date().toISOString(),
      }));
    });

    socket.on('message', (data) => {
      messagesReceived.add(1);

      try {
        const message = JSON.parse(data);

        // Calculate message latency
        if (message._sentAt) {
          const latency = Date.now() - message._sentAt;
          wsMessageLatency.add(latency);
        }

        // Track broadcast latency (server timestamp to client receipt)
        if (message.timestamp) {
          const serverTime = new Date(message.timestamp).getTime();
          const latency = Date.now() - serverTime;
          broadcastLatency.add(latency);
        }

        // Validate message structure
        const validMessage = check(message, {
          'Message has type': (m) => m.type !== undefined,
          'Message has payload': (m) => m.payload !== undefined,
        });

        if (!validMessage) {
          wsMessageErrors.add(1);
        }
      } catch (error) {
        wsMessageErrors.add(1);
        console.error(`Failed to parse WebSocket message: ${error}`);
      }
    });

    socket.on('error', (error) => {
      wsConnectionErrors.add(1);
      console.error(`WebSocket error (VU: ${__VU}): ${error}`);
    });

    socket.on('close', () => {
      activeConnections.add(-1);
      connectionDrops.add(1);
      console.log(`❌ WebSocket closed (VU: ${__VU})`);

      // Attempt reconnection for long-running test
      if (__ITER < 5) {
        reconnectionAttempts.add(1);
        console.log(`🔄 Attempting reconnection (VU: ${__VU}, Attempt: ${reconnectionAttempts})`);
        sleep(2);
      }
    });

    // Keep connection open for realistic duration
    const connectionDuration = Math.random() * 60 + 30; // 30-90 seconds
    socket.setTimeout(() => {
      console.log(`⏱️  Closing WebSocket after ${connectionDuration}s (VU: ${__VU})`);
      socket.close();
    }, connectionDuration * 1000);
  });

  check(res, {
    'WebSocket connection established': (r) => r && r.status === 101,
  });

  if (!res || res.status !== 101) {
    wsConnectionErrors.add(1);
    console.error(`WebSocket connection failed (VU: ${__VU}): Status ${res ? res.status : 'N/A'}`);
  }

  // Wait before next iteration
  sleep(Math.random() * 10 + 5);
}

// Teardown function
export function teardown(data) {
  console.log('✅ WebSocket Load Test Complete');
  console.log(`Started: ${data.startTime}`);
  console.log(`Ended: ${new Date().toISOString()}`);
  console.log('\n📊 WebSocket Metrics Summary:');
  console.log('  - Check connection times');
  console.log('  - Verify message latency');
  console.log('  - Review broadcast performance');
  console.log('  - Analyze connection stability');
  console.log('  - Examine reconnection patterns');
}

export {
  wsConnectionTime,
  wsMessageLatency,
  wsConnectionErrors,
  wsMessageErrors,
  activeConnections,
  messagesReceived,
  messagesSent,
  reconnectionAttempts,
  connectionDrops,
  broadcastLatency,
};
