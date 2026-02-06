/**
 * Web Vitals Monitoring
 *
 * Tracks Core Web Vitals and custom performance metrics for TraceRTM.
 * Exports metrics to backend for Prometheus ingestion.
 *
 * Core Web Vitals tracked:
 * - LCP (Largest Contentful Paint): <2.5s good, >4s poor
 * - FID (First Input Delay): <100ms good, >300ms poor
 * - CLS (Cumulative Layout Shift): <0.1 good, >0.25 poor
 * - TTFB (Time to First Byte): <800ms good, >1800ms poor
 * - INP (Interaction to Next Paint): <200ms good, >500ms poor
 */

import { onCLS, onINP, onLCP, onTTFB, type Metric } from 'web-vitals';

// ============================================================================
// Types
// ============================================================================

export interface WebVitalsMetric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  id: string;
  navigationType: string;
  timestamp: number;
}

export interface PerformanceMetrics {
  webVitals: WebVitalsMetric[];
  bundleSize: BundleSizeMetric;
  componentRenders: ComponentRenderMetric[];
  errors: ErrorMetric[];
}

export interface BundleSizeMetric {
  total: number;
  js: number;
  css: number;
  images: number;
  timestamp: number;
}

export interface ComponentRenderMetric {
  componentName: string;
  renderTime: number;
  phase: 'mount' | 'update';
  timestamp: number;
}

export interface ErrorMetric {
  message: string;
  stack?: string;
  componentName?: string;
  timestamp: number;
  severity: 'error' | 'warning';
}

// ============================================================================
// Thresholds
// ============================================================================

const THRESHOLDS = {
  LCP: { good: 2500, poor: 4000 },
  FID: { good: 100, poor: 300 },
  CLS: { good: 0.1, poor: 0.25 },
  TTFB: { good: 800, poor: 1800 },
  INP: { good: 200, poor: 500 },
} as const;

// ============================================================================
// Rating Functions
// ============================================================================

function getRating(
  metricName: keyof typeof THRESHOLDS,
  value: number,
): 'good' | 'needs-improvement' | 'poor' {
  const threshold = THRESHOLDS[metricName];
  if (value <= threshold.good) return 'good';
  if (value <= threshold.poor) return 'needs-improvement';
  return 'poor';
}

// ============================================================================
// Metrics Collection
// ============================================================================

class WebVitalsCollector {
  private metrics: WebVitalsMetric[] = [];
  private reportEndpoint = '/api/v1/metrics/web-vitals';
  private batchSize = 10;
  private batchTimeout = 5000; // 5 seconds
  private batchTimer: ReturnType<typeof setTimeout> | null = null;

  constructor() {
    this.initWebVitals();
    this.initBundleSizeTracking();
    this.initErrorTracking();
    this.initPerformanceObserver();
  }

  // --------------------------------------------------------------------------
  // Web Vitals Initialization
  // --------------------------------------------------------------------------

  private initWebVitals(): void {
    const handleMetric = (metric: Metric): void => {
      const webVital: WebVitalsMetric = {
        name: metric.name,
        value: metric.value,
        rating: getRating(metric.name as keyof typeof THRESHOLDS, metric.value),
        delta: metric.delta,
        id: metric.id,
        navigationType: metric.navigationType || 'navigate',
        timestamp: Date.now(),
      };

      this.metrics.push(webVital);
      this.scheduleBatch();

      // Log poor metrics immediately
      if (webVital.rating === 'poor') {
        console.warn(`Poor ${webVital.name}: ${webVital.value}`, webVital);
      }
    };

    // Attach observers
    onLCP(handleMetric);
    onCLS(handleMetric);
    onTTFB(handleMetric);
    onINP(handleMetric);
  }

  // --------------------------------------------------------------------------
  // Bundle Size Tracking
  // --------------------------------------------------------------------------

  private initBundleSizeTracking(): void {
    if (typeof window === 'undefined') return;

    window.addEventListener('load', () => {
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];

      const bundleSize: BundleSizeMetric = {
        total: 0,
        js: 0,
        css: 0,
        images: 0,
        timestamp: Date.now(),
      };

      resources.forEach((resource) => {
        const size = resource.transferSize || resource.encodedBodySize || 0;
        bundleSize.total += size;

        if (resource.name.endsWith('.js') || resource.name.includes('/_next/static/chunks/')) {
          bundleSize.js += size;
        } else if (resource.name.endsWith('.css')) {
          bundleSize.css += size;
        } else if (resource.name.match(/\.(jpg|jpeg|png|gif|svg|webp|avif)(\?.*)?$/i)) {
          bundleSize.images += size;
        }
      });

      // Report bundle size
      this.reportBundleSize(bundleSize);
    });
  }

  // --------------------------------------------------------------------------
  // Error Tracking
  // --------------------------------------------------------------------------

  private initErrorTracking(): void {
    if (typeof window === 'undefined') return;

    // Global error handler
    window.addEventListener('error', (event) => {
      const errorMetric: ErrorMetric = {
        message: event.error?.message || event.message,
        stack: event.error?.stack,
        timestamp: Date.now(),
        severity: 'error',
      };
      this.reportError(errorMetric);
    });

    // Unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      const errorMetric: ErrorMetric = {
        message: `Unhandled Promise Rejection: ${event.reason}`,
        timestamp: Date.now(),
        severity: 'error',
      };
      this.reportError(errorMetric);
    });
  }

  // --------------------------------------------------------------------------
  // Performance Observer (for Long Tasks)
  // --------------------------------------------------------------------------

  private initPerformanceObserver(): void {
    if (typeof window === 'undefined' || !('PerformanceObserver' in window)) return;

    try {
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'longtask') {
            console.warn('Long Task detected:', {
              duration: entry.duration,
              startTime: entry.startTime,
            });
          }
        });
      });

      observer.observe({ entryTypes: ['longtask'] });
    } catch (e) {
      // PerformanceObserver may not be supported
      console.warn('PerformanceObserver not supported:', e);
    }
  }

  // --------------------------------------------------------------------------
  // Batch Reporting
  // --------------------------------------------------------------------------

  private scheduleBatch(): void {
    if (this.batchTimer) return;

    this.batchTimer = setTimeout(() => {
      this.flush();
    }, this.batchTimeout);

    // Also flush if we hit the batch size
    if (this.metrics.length >= this.batchSize) {
      this.flush();
    }
  }

  private async flush(): Promise<void> {
    if (this.metrics.length === 0) return;

    const metricsToSend = [...this.metrics];
    this.metrics = [];

    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }

    try {
      await fetch(this.reportEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          metrics: metricsToSend,
          userAgent: navigator.userAgent,
          url: window.location.href,
          timestamp: Date.now(),
        }),
        // Use keepalive to ensure metrics are sent even during page unload
        keepalive: true,
      });
    } catch (error) {
      console.error('Failed to report web vitals:', error);
      // Re-add metrics to queue for retry
      this.metrics.push(...metricsToSend);
    }
  }

  // --------------------------------------------------------------------------
  // Individual Metric Reporting
  // --------------------------------------------------------------------------

  private async reportBundleSize(bundleSize: BundleSizeMetric): Promise<void> {
    try {
      await fetch('/api/v1/metrics/bundle-size', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(bundleSize),
      });
    } catch (error) {
      console.error('Failed to report bundle size:', error);
    }
  }

  private async reportError(error: ErrorMetric): Promise<void> {
    try {
      await fetch('/api/v1/metrics/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(error),
        keepalive: true,
      });
    } catch (e) {
      console.error('Failed to report error metric:', e);
    }
  }

  // --------------------------------------------------------------------------
  // Public API
  // --------------------------------------------------------------------------

  public reportComponentRender(metric: ComponentRenderMetric): void {
    fetch('/api/v1/metrics/component-render', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(metric),
    }).catch((error) => {
      console.error('Failed to report component render:', error);
    });
  }

  public getMetrics(): WebVitalsMetric[] {
    return [...this.metrics];
  }

  public forceFlush(): Promise<void> {
    return this.flush();
  }
}

// ============================================================================
// React Profiler Integration
// ============================================================================

export function createProfilerOnRender(componentName: string) {
  return (
    id: string,
    phase: 'mount' | 'update',
    actualDuration: number,
    _baseDuration: number,
    _startTime: number,
    _commitTime: number,
  ) => {
    // Only report significant render times (>16ms = 1 frame at 60fps)
    if (actualDuration > 16) {
      webVitalsCollector.reportComponentRender({
        componentName: id || componentName,
        renderTime: actualDuration,
        phase,
        timestamp: Date.now(),
      });
    }
  };
}

// ============================================================================
// Singleton Instance & Initialization
// ============================================================================

let webVitalsCollector: WebVitalsCollector;

export function initWebVitals(): WebVitalsCollector {
  if (typeof window === 'undefined') {
    // Return a no-op collector for SSR
    return {
      reportComponentRender: () => {},
      getMetrics: () => [],
      forceFlush: async () => {},
    } as any;
  }

  if (!webVitalsCollector) {
    webVitalsCollector = new WebVitalsCollector();

    // Flush metrics before page unload
    window.addEventListener('beforeunload', () => {
      webVitalsCollector.forceFlush();
    });

    // Flush metrics on visibility change (tab switch)
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        webVitalsCollector.forceFlush();
      }
    });
  }

  return webVitalsCollector;
}

// ============================================================================
// Exports
// ============================================================================

export { webVitalsCollector };
export default initWebVitals;
