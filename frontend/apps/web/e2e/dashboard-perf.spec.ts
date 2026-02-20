import { expect, test } from '@playwright/test';

test.describe('Dashboard Performance @performance @dashboard', () => {
  test('loads /home within performance budget', async ({ page }) => {
    // Inject performance observer script BEFORE navigation
    await page.addInitScript(() => {
      (window as any).__perfMetrics = {
        lcpMs: 0,
        lcpObserved: false,
      };

      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lcpEntry = entries.at(-1);
        if (lcpEntry) {
          (window as any).__perfMetrics.lcpMs = lcpEntry.startTime;
          (window as any).__perfMetrics.lcpObserved = true;
        }
      });

      try {
        observer.observe({ type: 'largest-contentful-paint', buffered: true });
      } catch {
        // LCP not supported in this context
      }
    });

    // Navigate and wait for network idle
    const startTime = Date.now();
    await page.goto('/home', { waitUntil: 'networkidle' });
    const loadTime = Date.now() - startTime;

    // Collect metrics after navigation
    const metrics = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const { memory } = performance as any;
      const lcpMs = (window as any).__perfMetrics?.lcpMs ?? 0;

      return {
        loadTime: nav ? nav.loadEventEnd - nav.startTime : 0,
        navigatorLoadTime: loadTime,
        heapUsedMB: memory ? memory.usedJSHeapSize / (1024 * 1024) : 0,
        lcpMs: lcpMs,
      };
    });

    console.log('Dashboard perf metrics:', metrics);

    // Load time budget: <5s (use navigator timing as fallback)
    const finalLoadTime = metrics.loadTime > 0 ? metrics.loadTime : metrics.navigatorLoadTime;
    expect(finalLoadTime).toBeLessThan(5000);

    // Heap budget: <200MB
    if (metrics.heapUsedMB > 0) {
      expect(metrics.heapUsedMB).toBeLessThan(200);
    }

    // LCP budget: <4s
    if (metrics.lcpMs > 0) {
      expect(metrics.lcpMs).toBeLessThan(4000);
    }
  });

  test('does not trigger excessive network requests', async ({ page }) => {
    const requests: string[] = [];
    page.on('request', (req) => {
      if (req.url().includes('/api/')) {
        requests.push(req.url());
      }
    });

    await page.goto('/home', { waitUntil: 'networkidle' });

    const apiCalls = requests.filter((u) => u.includes('/api/v1/'));
    console.log(`API calls on /home: ${apiCalls.length}`, apiCalls);

    // Dashboard should not spawn excessive API calls
    // Budget: at most 50 concurrent/sequential API calls for full page load
    expect(apiCalls.length).toBeLessThan(50);
  });

  test('heap does not grow unboundedly during 10s idle', async ({ page }) => {
    await page.goto('/home', { waitUntil: 'networkidle' });

    const initialHeap = await page.evaluate(() => {
      const { memory } = performance as any;
      return memory ? memory.usedJSHeapSize / (1024 * 1024) : 0;
    });

    // Wait 10 seconds for any background work to settle
    await page.waitForTimeout(10_000);

    const finalHeap = await page.evaluate(() => {
      const { memory } = performance as any;
      return memory ? memory.usedJSHeapSize / (1024 * 1024) : 0;
    });

    if (initialHeap > 0 && finalHeap > 0) {
      const heapGrowthMB = finalHeap - initialHeap;
      console.log(
        `Heap growth over 10s: ${heapGrowthMB.toFixed(1)}MB (${initialHeap.toFixed(1)} -> ${finalHeap.toFixed(1)})`,
      );

      // Heap should not grow by more than 50MB during idle
      // This catches memory leaks in intervals/observers/subscriptions
      expect(heapGrowthMB).toBeLessThan(50);
    }
  });
});
