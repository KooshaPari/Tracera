// MSW browser setup for TraceRTM
import { setupWorker } from 'msw/browser';

import { logger } from '@/lib/logger';

import { handlers } from './handlers';

// This configures a Service Worker with the given request handlers.
export const worker = setupWorker(...handlers);

// Start the worker with custom options
export async function startMockServiceWorker() {
  if (typeof globalThis.window === 'undefined') {
    return;
  }

  try {
    await worker.start({
      onUnhandledRequest: 'bypass', // Don't warn about unhandled requests
      serviceWorker: {
        url: '/mockServiceWorker.js',
      },
    });
    logger.info('[MSW] Mock Service Worker started successfully');
  } catch (error) {
    logger.error('[MSW] Failed to start Mock Service Worker:', error);
  }
}
