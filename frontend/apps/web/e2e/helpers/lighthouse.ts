/**
 * Lighthouse Performance Testing Helpers
 *
 * Utilities for running Lighthouse audits and checking performance metrics
 */
import type { Page } from '@playwright/test';

import { playAudit } from 'playwright-lighthouse';

/**
 * Default Lighthouse thresholds
 */
export const DEFAULT_THRESHOLDS = {
  accessibility: 90,
  'best-practices': 80,
  performance: 70,
  pwa: 50,
  seo: 80,
};

/**
 * Core Web Vitals thresholds (in milliseconds, except CLS)
 */
export const WEB_VITALS_THRESHOLDS = {
  'cumulative-layout-shift': 0.1,
  'first-contentful-paint': 2000,
  'largest-contentful-paint': 2500,
  'speed-index': 3400,
  'time-to-interactive': 3800,
  'total-blocking-time': 300,
};

/**
 * Run Lighthouse audit with custom thresholds
 */
export async function runLighthouseAudit(
  page: Page,
  name: string,
  options?: {
    thresholds?: Record<string, number>;
    port?: number;
    disableStorageReset?: boolean;
  },
) {
  await playAudit({
    disableStorageReset: options?.disableStorageReset ?? false,
    page,
    port: options?.port ?? 9222,
    reports: {
      directory: 'lighthouse-reports',
      formats: {
        html: true,
        json: true,
      },
      name,
    },
    thresholds: options?.thresholds ?? DEFAULT_THRESHOLDS,
  });
}

/**
 * Get Core Web Vitals from Performance API
 */
export async function getCoreWebVitals(page: Page) {
  return page.evaluate(
    async () =>
      new Promise((resolve) => {
        const metrics: Record<string, number> = {};

        // First Contentful Paint (FCP)
        const paintObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          for (const entry of entries) {
            if (entry.name === 'first-contentful-paint') {
              metrics.fcp = entry.startTime;
            }
          }
        });
        paintObserver.observe({ entryTypes: ['paint'] });

        // Largest Contentful Paint (LCP)
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries.at(-1);
          metrics.lcp = lastEntry.startTime;
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

        // Cumulative Layout Shift (CLS)
        let clsScore = 0;
        const clsObserver = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!(entry as any).hadRecentInput) {
              clsScore += (entry as any).value;
            }
          }
          metrics.cls = clsScore;
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });

        // First Input Delay (FID) - via PerformanceEventTiming
        const fidObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          if (entries.length > 0) {
            metrics.fid = (entries[0] as any).processingStart - entries[0].startTime;
          }
        });
        fidObserver.observe({ entryTypes: ['first-input'] });

        // Return metrics after 3 seconds
        setTimeout(() => {
          paintObserver.disconnect();
          lcpObserver.disconnect();
          clsObserver.disconnect();
          fidObserver.disconnect();
          resolve(metrics);
        }, 3000);
      }),
  );
}

/**
 * Check if Core Web Vitals meet thresholds
 */
export function assertWebVitals(
  metrics: Record<string, number>,
  thresholds = WEB_VITALS_THRESHOLDS,
): { passed: boolean; failures: string[] } {
  const failures: string[] = [];

  if (metrics.fcp && metrics.fcp > thresholds['first-contentful-paint']) {
    failures.push(`FCP: ${metrics.fcp.toFixed(0)}ms > ${thresholds['first-contentful-paint']}ms`);
  }

  if (metrics.lcp && metrics.lcp > thresholds['largest-contentful-paint']) {
    failures.push(`LCP: ${metrics.lcp.toFixed(0)}ms > ${thresholds['largest-contentful-paint']}ms`);
  }

  if (metrics.cls && metrics.cls > thresholds['cumulative-layout-shift']) {
    failures.push(`CLS: ${metrics.cls.toFixed(3)} > ${thresholds['cumulative-layout-shift']}`);
  }

  if (metrics.fid && metrics.fid > 100) {
    // FID threshold is 100ms
    failures.push(`FID: ${metrics.fid.toFixed(0)}ms > 100ms`);
  }

  return {
    failures,
    passed: failures.length === 0,
  };
}

/**
 * Get page load metrics from Navigation Timing API
 */
export async function getLoadMetrics(page: Page) {
  return page.evaluate(() => {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

    if (!navigation) {
      return null;
    }

    return {
      // Time to first byte
      ttfb: navigation.responseStart - navigation.requestStart,

      // DOM Content Loaded
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,

      // Load Complete
      loadComplete: navigation.loadEventEnd - navigation.loadEventStart,

      // DOM Interactive
      domInteractive: navigation.domInteractive - navigation.fetchStart,

      // Total page load time
      totalTime: navigation.loadEventEnd - navigation.fetchStart,

      // DNS lookup time
      dnsTime: navigation.domainLookupEnd - navigation.domainLookupStart,

      // TCP connection time
      tcpTime: navigation.connectEnd - navigation.connectStart,

      // SSL/TLS negotiation time (if HTTPS)
      tlsTime:
        navigation.secureConnectionStart > 0
          ? navigation.connectEnd - navigation.secureConnectionStart
          : 0,

      // Request + Response time
      requestTime: navigation.responseEnd - navigation.requestStart,

      // DOM Processing time
      domProcessingTime: navigation.domComplete - navigation.domInteractive,
    };
  });
}

/**
 * Get resource performance metrics
 */
export async function getResourceMetrics(page: Page) {
  return page.evaluate(() => {
    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];

    const byType: Record<string, { count: number; totalSize: number; totalDuration: number }> = {};

    for (const resource of resources) {
      // Extract file extension or type
      let type = 'other';
      if (resource.name.endsWith('.js')) {
        type = 'script';
      } else if (resource.name.endsWith('.css')) {
        type = 'stylesheet';
      } else if (/\.(png|jpg|jpeg|gif|svg|webp|avif)$/.test(resource.name)) {
        type = 'image';
      } else if (/\.(woff|woff2|ttf|otf)$/.test(resource.name)) {
        type = 'font';
      } else if (resource.name.includes('/api/')) {
        type = 'api';
      }

      if (!byType[type]) {
        byType[type] = { count: 0, totalDuration: 0, totalSize: 0 };
      }

      byType[type].count++;
      byType[type].totalSize += resource.transferSize || 0;
      byType[type].totalDuration += resource.duration;
    }

    return {
      byType,
      totalDuration: resources.reduce((acc, r) => acc + r.duration, 0),
      totalResources: resources.length,
      totalSize: resources.reduce((acc, r) => acc + (r.transferSize || 0), 0),
    };
  });
}

/**
 * Measure JavaScript execution time
 */
export async function measureJavaScriptExecution(page: Page) {
  return page.evaluate(() => {
    const jsResources = performance
      .getEntriesByType('resource')
      .filter((r) => r.name.endsWith('.js')) as PerformanceResourceTiming[];

    return {
      avgDuration:
        jsResources.length > 0
          ? jsResources.reduce((acc, r) => acc + r.duration, 0) / jsResources.length
          : 0,
      count: jsResources.length,
      totalDuration: jsResources.reduce((acc, r) => acc + r.duration, 0),
      totalSize: jsResources.reduce((acc, r) => acc + (r.transferSize || 0), 0),
    };
  });
}

/**
 * Check for render-blocking resources
 */
export async function checkRenderBlockingResources(page: Page) {
  return page.evaluate(() => {
    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];

    // Resources that block rendering
    const blocking = resources.filter((r) => {
      const name = r.name.toLowerCase();
      return (
        (name.endsWith('.css') || name.endsWith('.js')) &&
        r.startTime < 1000 && // Loaded early
        r.renderBlockingStatus === 'blocking'
      );
    });

    return {
      count: blocking.length,
      resources: blocking.map((r) => ({
        duration: r.duration,
        size: r.transferSize,
        url: r.name,
      })),
    };
  });
}
