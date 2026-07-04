/**
 * Sentry Error Tracking Configuration
 *
 * Provides centralized error tracking and monitoring for the TraceRTM frontend.
 *
 * Features:
 * - Automatic error capture and reporting
 * - Performance monitoring with tracing
 * - User context and breadcrumbs
 * - Environment-based configuration
 * - Source map support for production debugging
 *
 * @see https://docs.sentry.io/platforms/javascript/guides/react/
 */

import * as Sentry from '@sentry/react';

const SENTRY_DSN = import.meta.env['VITE_SENTRY_DSN'];
const BUILD_ID = import.meta.env['VITE_BUILD_ID'] || 'local';
const SAMPLE_RATE_LOW = 0.1;
const SAMPLE_RATE_HUNDRED_PERCENT = 1.0;
const TIMESTAMP_MILLISECONDS_DIVISOR = 1000;

/**
 * Initialize Sentry error tracking
 *
 * Only initializes in production or when VITE_SENTRY_DSN is explicitly set.
 * Includes performance monitoring, replay sessions, and React-specific integrations.
 */
export const initSentry = (): void => {
  const environment = import.meta.env.MODE;

  // Skip initialization if no DSN is provided or in test environment
  if (!SENTRY_DSN || environment === 'test') {
    console.log('[Sentry] Skipping initialization (no DSN or test environment)');
    return;
  }

  Sentry.init({
    dsn: SENTRY_DSN,
    environment,

    // Integrations
    integrations: [
      // Browser tracing for performance monitoring
      Sentry.browserTracingIntegration({
        // Enable automatic route tracking with TanStack Router
        enableInp: true,
      }),

      // Session replay for debugging (only in production)
      ...(environment === 'production'
        ? [
            Sentry.replayIntegration({
              // Mask all text and images for privacy
              maskAllText: true,
              maskAllInputs: true,
              blockAllMedia: true,
            }),
          ]
        : []),
    ],

    // Performance Monitoring
    // Lower sample rate in production to reduce bandwidth
    tracesSampleRate: environment === 'production' ? SAMPLE_RATE_LOW : SAMPLE_RATE_HUNDRED_PERCENT,

    // Session Replay
    // Capture replays for 10% of sessions, 100% of error sessions
    replaysSessionSampleRate: SAMPLE_RATE_LOW,
    replaysOnErrorSampleRate: SAMPLE_RATE_HUNDRED_PERCENT,

    // Release tracking for versioning
    release: import.meta.env.VITE_APP_VERSION || 'unknown',

    // Dist tracking for deployment identification
    dist: BUILD_ID,

    // Hook for filtering errors before sending to Sentry
    beforeSend(event, hint) {
      // Filter out known non-critical errors
      const error = hint.originalException;

      if (error instanceof Error) {
        // Ignore network errors that are expected (user offline, etc.)
        if (
          error.message.includes('Failed to fetch') ||
          error.message.includes('Network request failed')
        ) {
          return null;
        }

        // Ignore chunk loading errors (usually transient)
        if (error.message.includes('Loading chunk') || error.message.includes('ChunkLoadError')) {
          return null;
        }
      }

      return event;
    },

    // Ignore specific errors from browser extensions
    ignoreErrors: [
      // Browser extension errors
      'ResizeObserver loop limit exceeded',
      'Non-Error promise rejection captured',
      // Chrome extensions
      'chrome-extension://',
      'moz-extension://',
      // Browser quirks
      'ResizeObserver loop completed with undelivered notifications',
    ],

    // Denylist for URLs that shouldn't trigger error reports
    denyUrls: [
      // Browser extensions
      /extensions\//i,
      /^chrome:\/\//i,
      /^moz-extension:\/\//i,
      // Development tools
      /^webpack-internal:\/\//i,
    ],
  });

  console.log(`[Sentry] Initialized for ${environment} environment`);
};

/**
 * Set user context for error tracking
 *
 * @param userId - User ID
 * @param email - User email (optional)
 * @param username - Username (optional)
 */
export const setSentryUser = (userId: string, email?: string, username?: string): void => {
  Sentry.setUser({
    id: userId,
    ...(email !== undefined ? { email } : {}),
    ...(username !== undefined ? { username } : {}),
  });
};

/**
 * Clear user context (e.g., on logout)
 */
export const clearSentryUser = (): void => {
  Sentry.setUser(null);
};

/**
 * Add custom context to error reports
 *
 * @param context - Context name
 * @param data - Context data
 */
export const setSentryContext = (context: string, data: Record<string, unknown>): void => {
  Sentry.setContext(context, data);
};

/**
 * Add breadcrumb for debugging
 *
 * @param message - Breadcrumb message
 * @param category - Breadcrumb category
 * @param level - Severity level
 */
export const addSentryBreadcrumb = (
  message: string,
  category: string = 'custom',
  level: 'info' | 'warning' | 'error' | 'debug' = 'info',
): void => {
  Sentry.addBreadcrumb({
    message,
    category,
    level,
    timestamp: Date.now() / TIMESTAMP_MILLISECONDS_DIVISOR,
  });
};

/**
 * Manually capture an exception
 *
 * @param error - Error to capture
 * @param context - Additional context (optional)
 */
export const captureException = (error: Error, context?: Record<string, unknown>): void => {
  if (context) {
    Sentry.withScope((scope) => {
      Object.entries(context).forEach(([key, value]) => {
        scope.setContext(key, value as Record<string, unknown>);
      });
      Sentry.captureException(error);
    });
  } else {
    Sentry.captureException(error);
  }
};

/**
 * Manually capture a message
 *
 * @param message - Message to capture
 * @param level - Severity level
 */
export const captureMessage = (
  message: string,
  level: 'info' | 'warning' | 'error' | 'debug' = 'info',
): void => {
  Sentry.captureMessage(message, level);
};

// Re-export Sentry for advanced usage
export { Sentry };
