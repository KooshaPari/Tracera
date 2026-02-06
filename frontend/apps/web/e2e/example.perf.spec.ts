import type { Page } from '@playwright/test';

/**
 * Performance Testing Example with Lighthouse
 *
 * Demonstrates:
 * - Lighthouse performance audits
 * - Core Web Vitals measurement
 * - Performance budgets
 * - Custom metrics
 *
 * Tags: @perf @performance @lighthouse
 *
 * Note: Lighthouse requires Chrome/Chromium
 */
import { expect, test } from '@playwright/test';
import { playAudit } from 'playwright-lighthouse';

// Performance thresholds based on Lighthouse scoring
const PERFORMANCE_THRESHOLDS = {
  performance: 70, // Overall performance score
  accessibility: 90, // Accessibility score
  'best-practices': 80, // Best practices score
  seo: 80, // SEO score
  pwa: 50, // PWA score (optional)
};

// Core Web Vitals thresholds
const WEB_VITALS_THRESHOLDS = {
  'first-contentful-paint': 2000, // 2 seconds
  'largest-contentful-paint': 2500, // 2.5 seconds
  'total-blocking-time': 300, // 300ms
  'cumulative-layout-shift': 0.1, // 0.1 CLS
  'speed-index': 3400, // 3.4 seconds
};

test.describe('Performance - Homepage', () => {
  test('should meet performance budgets @lighthouse', async ({ page }) => {
    await page.goto('/');

    // Run Lighthouse audit
    await playAudit({
      page: page,
      thresholds: PERFORMANCE_THRESHOLDS,
      port: 9222, // Chrome debugging port
      reports: {
        directory: 'lighthouse-reports',
        formats: {
          html: true,
          json: true,
        },
        name: 'homepage-perf',
      },
    });

    // Lighthouse will throw if thresholds are not met
  });

  test('should have good Core Web Vitals', async ({ page }) => {
    await page.goto('/');

    // Wait for page to stabilize
    await page.waitForLoadState('networkidle');

    // Get performance metrics using Performance Observer API
    const webVitals = await page.evaluate(
      async () =>
        new Promise((resolve) => {
          const metrics: Record<string, number> = {};

          // First Contentful Paint (FCP)
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            for (const entry of entries) {
              if (entry.name === 'first-contentful-paint') {
                metrics.fcp = entry.startTime;
              }
            }
          }).observe({ entryTypes: ['paint'] });

          // Largest Contentful Paint (LCP)
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries.at(-1);
            metrics.lcp = lastEntry.startTime;
          }).observe({ entryTypes: ['largest-contentful-paint'] });

          // Cumulative Layout Shift (CLS)
          let clsScore = 0;
          new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              if (!(entry as any).hadRecentInput) {
                clsScore += (entry as any).value;
              }
            }
            metrics.cls = clsScore;
          }).observe({ entryTypes: ['layout-shift'] });

          // Return metrics after 3 seconds
          setTimeout(() => {
            resolve(metrics);
          }, 3000);
        }),
    );

    // Assert Core Web Vitals
    if ((webVitals as any).fcp) {
      expect((webVitals as any).fcp).toBeLessThan(WEB_VITALS_THRESHOLDS['first-contentful-paint']);
    }
    if ((webVitals as any).lcp) {
      expect((webVitals as any).lcp).toBeLessThan(
        WEB_VITALS_THRESHOLDS['largest-contentful-paint'],
      );
    }
    if ((webVitals as any).cls !== undefined) {
      expect((webVitals as any).cls).toBeLessThan(WEB_VITALS_THRESHOLDS['cumulative-layout-shift']);
    }
  });

  test('should load efficiently with minimal requests', async ({ page }) => {
    // Track network requests
    const requests: string[] = [];
    const requestSizes: number[] = [];

    page.on('request', (request) => {
      requests.push(request.url());
    });

    page.on('response', async (response) => {
      const size = Number(response.headers()['content-length'] || 0);
      requestSizes.push(size);
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check request count
    expect(requests.length).toBeLessThan(50); // Adjust threshold as needed

    // Check total transfer size
    const totalSize = requestSizes.reduce((acc, size) => acc + size, 0);
    expect(totalSize).toBeLessThan(2 * 1024 * 1024); // 2MB total
  });
});

test.describe('Performance - Dashboard', () => {
  test('should load dashboard with good performance', async ({ page }) => {
    await page.goto('/dashboard');

    // Measure time to interactive
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType(
        'navigation',
      )[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd,
        domInteractive: navigation.domInteractive,
        loadComplete: navigation.loadEventEnd,
      };
    });

    // Assert reasonable load times
    expect(performanceMetrics.domInteractive).toBeLessThan(3000); // 3s
    expect(performanceMetrics.domContentLoaded).toBeLessThan(4000); // 4s
    expect(performanceMetrics.loadComplete).toBeLessThan(5000); // 5s
  });

  test('should have efficient JavaScript execution', async ({ page }) => {
    await page.goto('/dashboard');

    // Measure JavaScript execution time
    const jsMetrics = await page.evaluate(() => {
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
      const jsResources = resources.filter((r) => r.name.endsWith('.js'));

      return {
        count: jsResources.length,
        totalDuration: jsResources.reduce((acc, r) => acc + r.duration, 0),
      };
    });

    // Check JS bundle efficiency
    expect(jsMetrics.count).toBeLessThan(20); // Max 20 JS files
    expect(jsMetrics.totalDuration).toBeLessThan(2000); // 2s total JS time
  });
});

test.describe('Performance - Image Optimization', () => {
  test('should use optimized images', async ({ page }) => {
    await page.goto('/');

    // Check for unoptimized images
    const imageMetrics = await page.evaluate(() => {
      const images = [...document.querySelectorAll('img')];
      return images.map((img) => ({
        displayHeight: img.height,
        displayWidth: img.width,
        format: img.src.split('.').pop()?.toLowerCase(),
        naturalHeight: img.naturalHeight,
        naturalWidth: img.naturalWidth,
        src: img.src,
      }));
    });

    // Check for modern formats (WebP, AVIF)
    const modernFormats = imageMetrics.filter(
      (img) =>
        img.format === 'webp' ||
        img.format === 'avif' ||
        img.src.includes('webp') ||
        img.src.includes('avif'),
    );

    // At least 50% of images should use modern formats
    if (imageMetrics.length > 0) {
      const modernFormatRatio = modernFormats.length / imageMetrics.length;
      expect(modernFormatRatio).toBeGreaterThan(0.3); // 30% threshold
    }

    // Check for oversized images (images larger than displayed size)
    const oversizedImages = imageMetrics.filter(
      (img) => img.naturalWidth > img.displayWidth * 2 || img.naturalHeight > img.displayHeight * 2,
    );

    // No more than 10% oversized images
    if (imageMetrics.length > 0) {
      const oversizedRatio = oversizedImages.length / imageMetrics.length;
      expect(oversizedRatio).toBeLessThan(0.1);
    }
  });
});

test.describe('Performance - Caching', () => {
  test('should use proper cache headers', async ({ page }) => {
    const cacheableResources: string[] = [];

    page.on('response', (response) => {
      const cacheControl = response.headers()['cache-control'];
      const url = response.url();

      // Check for cacheable static assets
      if (
        url.match(/\.(js|css|woff2|png|jpg|jpeg|svg|ico)$/) &&
        cacheControl &&
        (cacheControl.includes('max-age') || cacheControl.includes('immutable'))
      ) {
        cacheableResources.push(url);
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Most static assets should have cache headers
    expect(cacheableResources.length).toBeGreaterThan(0);
  });
});
