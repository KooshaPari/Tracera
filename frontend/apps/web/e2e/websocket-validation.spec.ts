import { expect, test } from '@playwright/test';

import { collectBrowserLogs } from './fixtures/test-helpers';

test.describe('WebSocket CORS Validation', () => {
  test('should establish WebSocket connection with CORS headers', async ({ page }) => {
    const logs: Record<string, any[]> = {
      console: [],
      network: [],
      errors: [],
    };

    // Capture console logs
    page.on('console', (msg) => {
      logs.console.push({
        type: msg.type(),
        text: msg.text(),
        location: msg.location(),
      });
    });

    // Capture network requests
    page.on('response', (response) => {
      if (response.url().includes('/ws')) {
        logs.network.push({
          url: response.url(),
          status: response.status(),
          headers: {
            'access-control-allow-origin': response.headers()['access-control-allow-origin'],
            'access-control-allow-credentials':
              response.headers()['access-control-allow-credentials'],
          },
        });
      }
    });

    // Capture page errors
    page.on('pageerror', (error) => {
      logs.errors.push({
        message: error.message,
        stack: error.stack,
      });
    });

    // Navigate to app
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');

    // Wait for WebSocket to establish (check console logs)
    await expect(async () => {
      const wsConnected = logs.console.some(
        (log) => log.text?.includes('[WebSocket]') && log.text?.includes('Connection established'),
      );
      expect(wsConnected).toBeTruthy();
    }).toPass({ timeout: 10_000 });

    // Verify CORS headers were present
    const corsHeaders = logs.network.find((n) => n.url?.includes('/ws'));
    if (corsHeaders) {
      expect(corsHeaders.headers['access-control-allow-origin']).toMatch(/http:\/\/localhost:\d+/);
      expect(corsHeaders.headers['access-control-allow-credentials']).toBe('true');
    }

    // No JavaScript errors during connection
    expect(logs.errors, 'No JavaScript errors should occur during WebSocket connection').toEqual(
      [],
    );

    // Log results for CI/CD
    console.log('WebSocket Validation Results:', JSON.stringify(logs, null, 2));
  });

  test('should authenticate via WebSocket after connection', async ({ page }) => {
    const wsMessages: string[] = [];

    page.on('console', (msg) => {
      if (msg.text().includes('[WebSocket]')) {
        wsMessages.push(msg.text());
      }
    });

    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');

    // Wait for authentication success
    await expect(async () => {
      const authSuccess = wsMessages.some((msg) => msg.includes('Authentication successful'));
      expect(authSuccess).toBeTruthy();
    }).toPass({ timeout: 10_000 });
  });

  test('should handle WebSocket reconnection gracefully', async ({ page }) => {
    const wsEvents: string[] = [];

    page.on('websocket', (ws) => {
      wsEvents.push('WebSocket created');

      ws.on('close', () => {
        wsEvents.push('WebSocket closed');
      });

      ws.on('framesent', (payload) => {
        wsEvents.push(`Frame sent: ${payload.payload}`);
      });

      ws.on('framereceived', (payload) => {
        wsEvents.push(`Frame received: ${payload.payload}`);
      });
    });

    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Connection should be established
    await expect(async () => {
      expect(wsEvents.some((event) => event.includes('WebSocket created'))).toBeTruthy();
      expect(wsEvents.some((event) => event.includes('Frame received'))).toBeTruthy();
    }).toPass({ timeout: 10_000 });

    console.log('WebSocket Event Log:', wsEvents);
  });

  test('should include proper CORS headers in WebSocket upgrade request', async ({ page }) => {
    let corsHeadersFound = false;
    const headers: Record<string, string> = {};

    page.on('request', (request) => {
      if (request.url().includes('/ws') || request.url().includes('WebSocket')) {
        const allHeaders = request.allHeaders();
        Object.assign(headers, allHeaders);

        // Check for CORS-related headers
        if (
          allHeaders['origin'] ||
          allHeaders['sec-websocket-key'] ||
          allHeaders['sec-websocket-version']
        ) {
          corsHeadersFound = true;
        }
      }
    });

    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    await expect(async () => {
      expect(corsHeadersFound).toBeTruthy();
    }).toPass({ timeout: 10_000 });
    console.log('WebSocket Request Headers:', headers);
  });

  test('should not expose sensitive data in WebSocket logs', async ({ page }) => {
    const logs: string[] = [];

    page.on('console', (msg) => {
      logs.push(msg.text());
    });

    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Verify no sensitive data patterns in logs
    const sensitivePatterns = [
      /password[:\s]*[^\s]+/i,
      /token[:\s]*[a-z0-9]+/i,
      /api[_-]?key[:\s]*[a-z0-9]+/i,
      /secret[:\s]*[a-z0-9]+/i,
    ];

    const sensitiveFound = logs.some((log) =>
      sensitivePatterns.some((pattern) => pattern.test(log)),
    );

    expect(sensitiveFound, 'WebSocket logs should not contain sensitive data').toBeFalsy();
    console.log('Verified: No sensitive data in WebSocket logs');
  });
});
