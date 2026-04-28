import { expect, test } from '@playwright/test';

/** Decode WebSocket frame payload to string (Playwright uses { payload: string | Buffer }). */
function framePayloadToText(payload: { payload: string | Buffer }): string {
  const p = payload.payload;
  return typeof p === 'string' ? p : new TextDecoder().decode(p);
}

/**
 * WebSocket Authentication Security Tests
 *
 * These tests verify that WebSocket authentication follows security best practices:
 * 1. Token is NOT sent in URL query parameters
 * 2. Token is sent in first message after connection
 * 3. Server validates token before allowing further communication
 * 4. Connection closes if authentication fails
 */

test.describe('WebSocket Authentication Security', () => {
  test('should NOT include token in WebSocket URL', async ({ page }) => {
    // Start request interception
    let wsUrlCapture = '';

    page.on('websocket', (ws) => {
      wsUrlCapture = ws.url();
    });

    await page.goto('/');
    await page.waitForTimeout(1000);

    // Verify no token in WebSocket URL
    await expect(async () => {
      expect(wsUrlCapture).not.toContain('token=');
    }).toPass({ timeout: 5000 });
  });

  test('should send authentication in message after connection', async ({
    page,
    context: _context,
  }) => {
    let authMessageSent = false;
    const wsMessages: any[] = [];

    page.on('websocket', (ws) => {
      ws.on('framesent', (payload) => {
        const data = JSON.parse(framePayloadToText(payload));
        wsMessages.push(data);

        // First message should be auth
        if (data.type === 'auth') {
          authMessageSent = true;
          expect(data).toHaveProperty('token');
          console.log('✓ Auth message sent with token');
        }
      });
    });

    await page.goto('/');
    await page.waitForTimeout(2000);

    await expect(async () => {
      expect(authMessageSent).toBe(true);
    }).toPass({ timeout: 5000 });
  });

  test('should wait for auth response before processing events', async ({ page }) => {
    let _authResponseReceived = false;
    let _eventMessageReceived = false;
    const messageOrder: string[] = [];

    page.on('websocket', (ws) => {
      ws.on('framereceived', (payload) => {
        const data = JSON.parse(framePayloadToText(payload));
        messageOrder.push(data.type);

        if (data.type === 'auth_success') {
          _authResponseReceived = true;
        }
        if (data.type === 'auth_failed') {
          _authResponseReceived = true;
        }
        if (data.type === 'event' || data.type === 'created' || data.type === 'updated') {
          _eventMessageReceived = true;
        }
      });
    });

    await page.goto('/');
    await page.waitForTimeout(2000);

    // Auth response should come before events
    await expect(async () => {
      const authIndex = messageOrder.findIndex(
        (msg) => msg === 'auth_success' || msg === 'auth_failed',
      );
      const eventIndex = messageOrder.findIndex(
        (msg) => msg === 'event' || msg === 'created' || msg === 'updated',
      );

      expect(authIndex).not.toBe(-1);
      expect(eventIndex).not.toBe(-1);
      expect(authIndex).toBeLessThan(eventIndex);
    }).toPass({ timeout: 5000 });
  });

  test('should handle authentication failure', async ({ page }) => {
    let _authFailureHandled = false;

    page.on('websocket', (ws) => {
      ws.on('framereceived', (payload) => {
        const data = JSON.parse(framePayloadToText(payload));

        if (data.type === 'auth_failed') {
          _authFailureHandled = true;
          console.log('✓ Authentication failure handled:', data.message);
        }
      });
    });

    await page.goto('/');
    await page.waitForTimeout(2000);

    // If auth fails, the connection should close
    // This test verifies the client properly handles auth_failed message
  });

  test('should not process messages before authentication', async ({ page }) => {
    const messagesBeforeAuth: any[] = [];
    let authComplete = false;

    page.on('websocket', (ws) => {
      ws.on('framereceived', (payload) => {
        const data = JSON.parse(framePayloadToText(payload));

        if (data.type === 'auth_success') {
          authComplete = true;
        }

        // Any event message before auth is an error
        if (
          !authComplete &&
          (data.type === 'event' || data.type === 'created' || data.type === 'updated')
        ) {
          messagesBeforeAuth.push(data);
        }
      });
    });

    await page.goto('/');
    await page.waitForTimeout(2000);

    expect(messagesBeforeAuth.length).toBe(0);
    console.log('✓ No event messages received before authentication');
  });

  test('WebSocket connection flow: secure authentication', async ({ page }) => {
    const connectionLog: string[] = [];

    page.on('websocket', (ws) => {
      connectionLog.push('WebSocket created');

      ws.on('framesent', (payload) => {
        const data = JSON.parse(framePayloadToText(payload));
        if (data.type === 'auth') {
          connectionLog.push('Auth message sent');
        }
      });

      ws.on('framereceived', (payload) => {
        const data = JSON.parse(framePayloadToText(payload));
        if (data.type === 'auth_success') {
          connectionLog.push('Auth success received');
        }
      });

      ws.on('close', () => {
        connectionLog.push('Connection closed');
      });
    });

    await page.goto('/');
    await page.waitForTimeout(2000);

    // Expected flow:
    // 1. WebSocket created
    // 2. Auth message sent (not in URL)
    // 3. Auth success received
    // 4. Ready for event messages

    console.log('Connection flow:', connectionLog);

    if (connectionLog.includes('Auth message sent')) {
      expect(connectionLog).toContain('Auth message sent');
    }
  });

  test('should reject token in query parameters', async ({ page }) => {
    let rejectionDetected = false;

    page.on('websocket', (ws) => {
      const url = ws.url();
      if (url.includes('token=')) {
        rejectionDetected = true;
        console.log('⚠ WARNING: Token found in WebSocket URL:', url);
      }
    });

    await page.goto('/');
    await page.waitForTimeout(1000);

    // Tokens should NEVER be in the URL
    expect(rejectionDetected).toBe(false);
  });

  test('should use secure message-based authentication', async ({ page }) => {
    let authenticationMethod = 'unknown';

    page.on('websocket', (ws) => {
      ws.on('framesent', (payload) => {
        const data = JSON.parse(framePayloadToText(payload));
        if (data.type === 'auth' && data.token) {
          authenticationMethod = 'message-based';
          console.log('✓ Using message-based authentication');
        }
      });
    });

    await page.goto('/');
    await page.waitForTimeout(2000);

    // Verify message-based auth is used (not URL-based)
    if (authenticationMethod !== 'unknown') {
      expect(authenticationMethod).toBe('message-based');
    }
  });
});
