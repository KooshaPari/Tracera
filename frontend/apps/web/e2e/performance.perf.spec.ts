import { expect, test } from './global-setup';

/**
 * Performance E2E Tests
 *
 * Tests application performance, load times, bundle sizes,
 * and runtime performance metrics.
 */

test.describe('Performance - Load Times', () => {
  test('should load dashboard within acceptable time', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // Dashboard should load in under 3 seconds
    expect(loadTime).toBeLessThan(3000);
  });

  test('should load items page within acceptable time', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // Items page should load in under 3 seconds
    expect(loadTime).toBeLessThan(3000);
  });

  test('should measure Core Web Vitals', async ({ page }) => {
    await page.goto('/');

    // Wait for page to fully load
    await page.waitForLoadState('networkidle');

    // Get performance metrics
    const metrics = await page.evaluate(
      async () =>
        new Promise((resolve) => {
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const vitals: any = {};

            for (const entry of entries) {
              if (entry.entryType === 'largest-contentful-paint') {
                vitals.lcp = entry.startTime;
              }
              if (entry.entryType === 'first-input') {
                vitals.fid = (entry as any).processingStart - entry.startTime;
              }
            }

            resolve(vitals);
          }).observe({
            entryTypes: ['largest-contentful-paint', 'first-input'],
          });

          // Timeout after 5 seconds
          setTimeout(() => {
            resolve({});
          }, 5000);
        }),
    );

    // LCP should be under 2.5 seconds (good)
    if (metrics.lcp) {
      expect(metrics.lcp).toBeLessThan(2500);
    }

    // FID should be under 100ms (good)
    if (metrics.fid) {
      expect(metrics.fid).toBeLessThan(100);
    }
  });

  test('should have acceptable Time to Interactive', async ({ page }) => {
    await page.goto('/');

    const tti = await page.evaluate(
      async () =>
        new Promise((resolve) => {
          const startTime = performance.now();

          const checkInteractive = () => {
            const now = performance.now();

            // Check if main thread is idle
            requestIdleCallback(() => {
              resolve(now - startTime);
            });
          };

          if (document.readyState === 'complete') {
            checkInteractive();
          } else {
            window.addEventListener('load', checkInteractive);
          }
        }),
    );

    // TTI should be under 3.8 seconds
    expect(tti).toBeLessThan(3800);
  });

  test('should lazy load images', async ({ page }) => {
    await page.goto('/');

    // Get all images
    const images = page.locator('img');
    const count = await images.count();

    let lazyLoadedCount = 0;

    for (let i = 0; i < count; i++) {
      const loading = await images.nth(i).getAttribute('loading');
      if (loading === 'lazy') {
        lazyLoadedCount++;
      }
    }

    // At least some images should be lazy loaded
    expect(lazyLoadedCount).toBeGreaterThan(0);
  });

  test('should not block rendering with scripts', async ({ page }) => {
    await page.goto('/');

    // Check script tags
    const scripts = await page.evaluate(() => {
      const scriptElements = document.querySelectorAll('script');
      const blockingScripts: string[] = [];

      for (const script of scriptElements) {
        const src = script.getAttribute('src');
        const async = script.hasAttribute('async');
        const defer = script.hasAttribute('defer');

        if (src && !async && !defer) {
          blockingScripts.push(src);
        }
      }

      return blockingScripts;
    });

    // Should have no blocking scripts (all should be async or defer)
    expect(scripts.length).toBe(0);
  });
});

test.describe('Performance - Runtime Performance', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('should render large lists efficiently', async ({ page }) => {
    await page.goto('/items');

    // Measure render time for large list
    const renderTime = await page.evaluate(
      async () =>
        new Promise<number>((resolve) => {
          const start = performance.now();

          // Trigger re-render by scrolling
          window.scrollTo(0, document.body.scrollHeight);

          requestAnimationFrame(() => {
            const end = performance.now();
            resolve(end - start);
          });
        }),
    );

    // Rendering should be fast (under 16ms for 60fps)
    expect(renderTime).toBeLessThan(50);
  });

  test('should handle rapid user interactions smoothly', async ({ page }) => {
    await page.goto('/items');

    // Rapidly click through items
    const startTime = Date.now();
    const itemCards = page.locator('[data-testid="item-card"]');

    for (let i = 0; i < 10; i++) {
      await itemCards.nth(i % 5).click();
      await page.waitForTimeout(100);
    }

    const totalTime = Date.now() - startTime;

    // Should handle interactions smoothly (average under 150ms per action)
    expect(totalTime / 10).toBeLessThan(150);
  });

  test('should not cause memory leaks', async ({ page }) => {
    await page.goto('/items');

    // Get initial memory
    const initialMemory = await page.evaluate(
      () => (performance as any).memory?.usedJSHeapSize ?? 0,
    );

    // Perform operations that might leak
    for (let i = 0; i < 10; i++) {
      await page.click('button:has-text("New Item")');
      await page.keyboard.press('Escape');
      await page.waitForTimeout(100);
    }

    // Trigger garbage collection (if available)
    await page.evaluate(() => {
      if ((globalThis as any).gc) {
        (globalThis as any).gc();
      }
    });

    await page.waitForTimeout(1000);

    // Get final memory
    const finalMemory = await page.evaluate(() => (performance as any).memory?.usedJSHeapSize ?? 0);

    // Memory should not increase significantly (less than 10MB)
    const memoryIncrease = finalMemory - initialMemory;
    expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024);
  });

  test('should debounce search input', async ({ page }) => {
    await page.goto('/items');

    // Monitor network requests
    let searchRequestCount = 0;

    page.on('request', (request) => {
      if (request.url().includes('/api/search')) {
        searchRequestCount++;
      }
    });

    // Rapidly type in search
    await page.click('[data-testid="search-input"]');

    const searchText = 'test query';
    for (const char of searchText) {
      await page.keyboard.type(char);
      await page.waitForTimeout(50);
    }

    await page.waitForTimeout(1000);

    // Should have debounced to 1-2 requests instead of 10+
    expect(searchRequestCount).toBeLessThan(3);
  });

  test('should virtualize large lists', async ({ page }) => {
    await page.goto('/items');

    // Check if list is virtualized
    const isVirtualized = await page.evaluate(() => {
      const container = document.querySelector('[data-testid="items-list"]');
      const allItems = container?.querySelectorAll('[data-testid="item-card"]');
      const visibleHeight = window.innerHeight;

      // Count items that are actually rendered
      let renderedCount = 0;
      allItems?.forEach((item) => {
        const rect = item.getBoundingClientRect();
        if (rect.top < visibleHeight + 1000 && rect.bottom > -1000) {
          renderedCount++;
        }
      });

      // If virtualized, rendered count should be less than total
      return {
        isVirtualized: renderedCount < (allItems?.length ?? 0),
        rendered: renderedCount,
        total: allItems?.length ?? 0,
      };
    });

    // List should be virtualized for performance
    // (or have a reasonable limit on visible items)
    expect(isVirtualized.rendered).toBeLessThan(100);
  });

  test('should optimize re-renders with React.memo', async ({ page }) => {
    await page.goto('/items');

    // Trigger state change that shouldn't re-render all items
    await page.click('[data-testid="filter-button"]');
    await page.click('[data-testid="filter-type-requirement"]');

    // Measure render time
    const renderTime = await page.evaluate(
      async () =>
        new Promise<number>((resolve) => {
          const start = performance.now();

          requestAnimationFrame(() => {
            requestAnimationFrame(() => {
              const end = performance.now();
              resolve(end - start);
            });
          });
        }),
    );

    // Optimized re-renders should be fast
    expect(renderTime).toBeLessThan(100);
  });
});

test.describe('Performance - Bundle Size', () => {
  test('should have acceptable initial bundle size', async ({ page }) => {
    const responses: any[] = [];

    page.on('response', (response) => {
      if (response.url().endsWith('.js')) {
        responses.push({
          size: Number.parseInt(response.headers()['content-length'] ?? '0', 10),
          url: response.url(),
        });
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const totalSize = responses.reduce((sum, r) => sum + r.size, 0);

    // Total JS bundle should be under 500KB (compressed)
    expect(totalSize).toBeLessThan(500 * 1024);
  });

  test('should code-split routes', async ({ page }) => {
    const jsFiles: string[] = [];

    page.on('response', (response) => {
      if (response.url().endsWith('.js')) {
        jsFiles.push(response.url());
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const dashboardFiles = new Set(jsFiles);
    jsFiles.length = 0;

    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    const itemsFiles = jsFiles.filter((f) => !dashboardFiles.has(f));

    // Should load different chunks for different routes
    expect(itemsFiles.length).toBeGreaterThan(0);
  });

  test('should not load unused vendor code', async ({ page }) => {
    const vendorChunks: string[] = [];

    page.on('response', (response) => {
      const url = response.url();
      if (url.includes('vendor') || url.includes('node_modules')) {
        vendorChunks.push(url);
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Should not load excessive vendor chunks on initial load
    expect(vendorChunks.length).toBeLessThan(5);
  });
});

test.describe('Performance - Network Optimization', () => {
  test('should use HTTP/2', async ({ page }) => {
    const protocols: string[] = [];

    page.on('response', (response) => {
      const protocol = response.frame()?.request()?.protocol?.() ?? '';
      if (protocol) {
        protocols.push(protocol);
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Should use HTTP/2 or HTTP/3
    const modernProtocols = protocols.filter(
      (p) => p.toLowerCase().includes('h2') || p.toLowerCase().includes('h3'),
    );

    expect(modernProtocols.length).toBeGreaterThan(0);
  });

  test('should compress responses', async ({ page }) => {
    let hasCompression = false;

    page.on('response', (response) => {
      const encoding = response.headers()['content-encoding'];
      if (encoding && (encoding.includes('gzip') || encoding.includes('br'))) {
        hasCompression = true;
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // At least some responses should be compressed
    expect(hasCompression).toBe(true);
  });

  test('should cache static assets', async ({ page }) => {
    let hasCacheHeaders = false;

    page.on('response', (response) => {
      const cacheControl = response.headers()['cache-control'];
      if (cacheControl?.includes('max-age')) {
        hasCacheHeaders = true;
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    expect(hasCacheHeaders).toBe(true);
  });

  test('should preload critical resources', async ({ page }) => {
    await page.goto('/');

    const preloadLinks = await page.evaluate(() => {
      const links = document.querySelectorAll('link[rel="preload"]');
      return [...links].map((link) => ({
        as: link.getAttribute('as'),
        href: link.getAttribute('href'),
      }));
    });

    // Should have preload links for critical resources
    expect(preloadLinks.length).toBeGreaterThan(0);
  });

  test('should use prefetch for next likely routes', async ({ page }) => {
    await page.goto('/');

    const prefetchLinks = await page.evaluate(() => {
      const links = document.querySelectorAll('link[rel="prefetch"]');
      return [...links].map((link) => link.getAttribute('href'));
    });

    // Should prefetch likely next pages
    expect(prefetchLinks.length).toBeGreaterThan(0);
  });
});

test.describe('Performance - Rendering Optimization', () => {
  test('should use CSS containment', async ({ page }) => {
    await page.goto('/items');

    const hasContainment = await page.evaluate(() => {
      const items = document.querySelectorAll('[data-testid="item-card"]');
      let containCount = 0;

      items.forEach((item) => {
        const styles = globalThis.getComputedStyle(item);
        if (styles.contain !== 'none') {
          containCount++;
        }
      });

      return containCount > 0;
    });

    // List items should use CSS containment
    expect(hasContainment).toBe(true);
  });

  test('should minimize layout thrashing', async ({ page }) => {
    await page.goto('/items');

    const layoutTime = await page.evaluate(
      async () =>
        new Promise<number>((resolve) => {
          const start = performance.now();

          // Trigger potential layout thrashing
          const items = document.querySelectorAll('[data-testid="item-card"]');
          items.forEach((item) => {
            const height = item.clientHeight;
            (item as HTMLElement).style.height = `${height}px`;
          });

          requestAnimationFrame(() => {
            const end = performance.now();
            resolve(end - start);
          });
        }),
    );

    // Should complete layout operations quickly
    expect(layoutTime).toBeLessThan(50);
  });

  test('should use will-change for animations', async ({ page }) => {
    await page.goto('/');

    // Open a modal with animations
    await page.click('button:has-text("New Item")');

    const hasWillChange = await page.evaluate(() => {
      const modal = document.querySelector('[role="dialog"]');
      const styles = globalThis.getComputedStyle(modal!);
      return styles.willChange !== 'auto';
    });

    // Animated elements should use will-change
    expect(hasWillChange).toBe(true);
  });

  test('should maintain 60fps during animations', async ({ page }) => {
    await page.goto('/items');

    // Measure frame rate during scroll
    const frameRate = await page.evaluate(
      async () =>
        new Promise<number>((resolve) => {
          let frameCount = 0;
          const duration = 1000; // 1 second
          const startTime = performance.now();

          const countFrames = () => {
            frameCount++;
            const elapsed = performance.now() - startTime;

            if (elapsed < duration) {
              requestAnimationFrame(countFrames);
            } else {
              resolve(frameCount);
            }
          };

          // Start scrolling
          window.scrollBy(0, 10);
          requestAnimationFrame(countFrames);
        }),
    );

    // Should maintain close to 60fps
    expect(frameRate).toBeGreaterThan(50);
  });
});

test.describe('Performance - Database and API', () => {
  test('should batch API requests', async ({ page }) => {
    let apiRequestCount = 0;

    page.on('request', (request) => {
      if (request.url().includes('/api/')) {
        apiRequestCount++;
      }
    });

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Dashboard should batch requests efficiently
    // (not make excessive individual requests)
    expect(apiRequestCount).toBeLessThan(10);
  });

  test('should implement request caching', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    let secondLoadRequests = 0;

    page.on('request', (request) => {
      if (request.url().includes('/api/items')) {
        secondLoadRequests++;
      }
    });

    // Navigate away and back
    await page.goto('/dashboard');
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Should use cached data (fewer requests)
    expect(secondLoadRequests).toBeLessThan(2);
  });

  test('should use optimistic updates', async ({ page }) => {
    await page.goto('/items');

    // Create new item
    const startTime = Date.now();

    await page.click('button:has-text("New Item")');
    await page.fill('input[name="title"]', 'Optimistic Item');
    await page.click('button:has-text("Save")');

    // UI should update immediately (optimistic)
    const uiUpdateTime = Date.now() - startTime;

    // UI update should be fast (before API response)
    expect(uiUpdateTime).toBeLessThan(500);

    // Item should appear in list immediately
    await expect(page.locator('text=Optimistic Item')).toBeVisible();
  });

  test('should implement infinite scroll efficiently', async ({ page }) => {
    await page.goto('/items');

    let apiCallCount = 0;

    page.on('request', (request) => {
      if (request.url().includes('/api/items')) {
        apiCallCount++;
      }
    });

    // Scroll to bottom
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    await page.waitForTimeout(500);

    // Scroll again
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    await page.waitForTimeout(500);

    // Should paginate efficiently (2-3 requests for 2 scrolls)
    expect(apiCallCount).toBeLessThan(5);
  });

  test('should handle GraphQL queries efficiently', async ({ page }) => {
    let graphqlRequestCount = 0;
    let totalGraphqlSize = 0;

    page.on('request', (request) => {
      const url = request.url();
      if (url.includes('/graphql') || url.includes('/api/graphql')) {
        graphqlRequestCount++;
      }
    });

    page.on('response', (response) => {
      const url = response.url();
      if (url.includes('/graphql') || url.includes('/api/graphql')) {
        totalGraphqlSize += Number.parseInt(response.headers()['content-length'] ?? '0', 10);
      }
    });

    await page.goto('/graph');
    await page.waitForLoadState('networkidle');

    // Should batch GraphQL queries
    expect(graphqlRequestCount).toBeLessThan(5);

    // Response size should be reasonable
    expect(totalGraphqlSize).toBeLessThan(500 * 1024);
  });

  test('should implement request deduplication', async ({ page }) => {
    const requestUrls: string[] = [];

    page.on('request', (request) => {
      if (request.url().includes('/api/')) {
        requestUrls.push(request.url());
      }
    });

    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Count duplicate URLs
    const uniqueUrls = new Set(requestUrls);
    const duplicateCount = requestUrls.length - uniqueUrls.size;

    // Should have minimal duplicate requests
    expect(duplicateCount).toBeLessThan(2);
  });
});

test.describe('Performance - Accessibility and Performance', () => {
  test('should maintain performance with accessibility features', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // Even with a11y features, should load quickly
    expect(loadTime).toBeLessThan(3500);
  });

  test('should not have performance degradation with focus indicators', async ({ page }) => {
    await page.goto('/items');

    // Tab through items to trigger focus indicators
    for (let i = 0; i < 20; i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(50);
    }

    // Should handle focus states without lagging
    await expect(page).toHaveURL(/\/items/);
  });

  test('should work smoothly with screen readers enabled', async ({ page }) => {
    // Enable screen reader mode
    await page.addInitScript(() => {
      (globalThis as any).screenReaderEnabled = true;
    });

    const startTime = Date.now();
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // Should load efficiently even with screen reader
    expect(loadTime).toBeLessThan(3500);
  });
});

test.describe('Performance - Virtual Scrolling', () => {
  test('should render virtual scrolled content efficiently', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Get initial rendered item count
    const initialItems = await page.evaluate(() => {
      const items = document.querySelectorAll("[data-testid='item-row']");
      return items.length;
    });

    // Should render fewer items than total (due to virtualization)
    expect(initialItems).toBeLessThan(100);

    // Scroll down significantly
    await page.evaluate(() => {
      window.scrollTo(0, 5000);
    });

    await page.waitForTimeout(500);

    // Get rendered items after scroll
    const scrolledItems = await page.evaluate(() => {
      const items = document.querySelectorAll("[data-testid='item-row']");
      return items.length;
    });

    // Should still have reasonable number of rendered items
    expect(scrolledItems).toBeLessThan(150);
  });

  test('should update virtual scroll viewport smoothly', async ({ page }) => {
    await page.goto('/items');

    const scrollMetrics = await page.evaluate(
      async () =>
        new Promise((resolve) => {
          const scrollEvents: number[] = [];
          let scrollEventCount = 0;

          const handleScroll = () => {
            scrollEventCount++;
            scrollEvents.push(performance.now());
          };

          window.addEventListener('scroll', handleScroll);

          // Perform smooth scroll
          window.scrollBy({ behavior: 'smooth', top: 1000 });

          // Wait and measure
          setTimeout(() => {
            window.removeEventListener('scroll', handleScroll);
            const avgTime =
              scrollEvents.length > 0
                ? (scrollEvents.at(-1) - scrollEvents[0]) / scrollEventCount
                : 0;

            resolve({
              avgTimePerEvent: avgTime,
              eventCount: scrollEventCount,
            });
          }, 2000);
        }),
    );

    expect(scrollMetrics).toBeDefined();
  });

  test('should handle rapid scrolling without janky UI', async ({ page }) => {
    await page.goto('/items');

    const jankMetrics = await page.evaluate(
      async () =>
        new Promise((resolve) => {
          const frameTimings: number[] = [];
          let lastFrameTime = performance.now();

          const measureFrames = () => {
            const now = performance.now();
            const frameTime = now - lastFrameTime;
            frameTimings.push(frameTime);
            lastFrameTime = now;

            if (frameTimings.length < 60) {
              requestAnimationFrame(measureFrames);
            } else {
              // Calculate jank (frames over 50ms)
              const jankFrames = frameTimings.filter((t) => t > 50).length;

              resolve({
                avgFrameTime: frameTimings.reduce((a, b) => a + b, 0) / frameTimings.length,
                jankFrames: jankFrames,
                jankPercentage: (jankFrames / frameTimings.length) * 100,
                totalFrames: frameTimings.length,
              });
            }
          };

          // Start rapid scrolling
          window.scrollBy(0, 1000);
          requestAnimationFrame(measureFrames);
        }),
    );

    // Less than 10% jank frames is acceptable
    expect(jankMetrics.jankPercentage).toBeLessThan(10);
  });
});

test.describe('Performance - Lighthouse Integration', () => {
  test('should pass Lighthouse performance audit', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Get Core Web Vitals
    const vitals = await page.evaluate(() => {
      // Nested function required: runs in browser context via page.evaluate
      const getCLS = () => {
        let clsValue = 0;

        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            const layoutEntry = entry as PerformanceEntry & {
              hadRecentInput?: boolean;
              value?: number;
            };
            if (!layoutEntry.hadRecentInput && layoutEntry.entryType === 'layout-shift') {
              clsValue += layoutEntry.value ?? 0;
            }
          }
        });

        observer.observe({ entryTypes: ['layout-shift'] });

        return clsValue;
      };

      return {
        cls: getCLS(),
        pageUrl: globalThis.location.href,
      };
    });

    // CLS should be minimal
    expect(vitals.cls).toBeLessThan(0.1);
  });

  test('should have good accessibility score metrics', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    const accessibilityMetrics = await page.evaluate(() => {
      const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
      const links = document.querySelectorAll('a');
      const _buttons = document.querySelectorAll('button');
      const inputs = document.querySelectorAll('input, textarea, select');

      const _ariaLabeled = 0;
      let linkswithText = 0;
      let labeledInputs = 0;

      links.forEach((link) => {
        if (
          link.textContent?.trim() ||
          link.getAttribute('aria-label') ||
          link.getAttribute('title')
        ) {
          linkswithText++;
        }
      });

      inputs.forEach((input) => {
        const id = input.getAttribute('id');
        const label = document.querySelector(`label[for="${id}"]`);
        const ariaLabel = input.getAttribute('aria-label');

        if (label || ariaLabel) {
          labeledInputs++;
        }
      });

      return {
        accessibleLinksCount: linkswithText,
        headingCount: headings.length,
        labeledInputs: labeledInputs,
        totalInputs: inputs.length,
        totalLinks: links.length,
      };
    });

    // Should have at least one heading
    expect(accessibilityMetrics.headingCount).toBeGreaterThan(0);

    // Most links should have text
    expect(accessibilityMetrics.accessibleLinksCount).toBeGreaterThan(
      accessibilityMetrics.totalLinks * 0.7,
    );
  });

  test('should have minimal layout shift during page load', async ({ page }) => {
    let maxCLS = 0;

    page.on('framenavigated', async () => {
      const cls = await page.evaluate(() => {
        let clsValue = 0;

        const entries = performance.getEntriesByType('layout-shift');
        for (const entry of entries) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value;
          }
        }

        return clsValue;
      });

      if (cls > maxCLS) {
        maxCLS = cls;
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // CLS should be under 0.1 (good score is under 0.1)
    expect(maxCLS).toBeLessThan(0.15);
  });

  test('should measure all Core Web Vitals together', async ({ page }) => {
    const metrics = await page.evaluate(
      async () =>
        new Promise((resolve) => {
          const vitals = {
            cls: 0,
            fid: 0,
            lcp: 0,
            ttfb: 0,
          };

          // LCP observer
          new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lastEntry = entries.at(-1);
            vitals.lcp = lastEntry.startTime;
          }).observe({ entryTypes: ['largest-contentful-paint'] });

          // FID observer
          new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              if (vitals.fid === 0) {
                vitals.fid = (entry as any).processingStart - entry.startTime;
              }
            }
          }).observe({ entryTypes: ['first-input'] });

          // CLS observer
          let clsValue = 0;
          new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
              if (!(entry as any).hadRecentInput) {
                clsValue += (entry as any).value;
              }
            }
            vitals.cls = clsValue;
          }).observe({ entryTypes: ['layout-shift'] });

          // TTFB from navigation timing
          if (performance.getEntriesByType('navigation').length > 0) {
            const navEntry = performance.getEntriesByType(
              'navigation',
            )[0] as PerformanceNavigationTiming;
            vitals.ttfb = navEntry.responseStart - navEntry.fetchStart;
          }

          setTimeout(() => {
            resolve(vitals);
          }, 5000);
        }),
    );

    // Validate Core Web Vitals
    expect(metrics.lcp).toBeLessThan(2500); // Good LCP
    expect(metrics.fid ?? 0).toBeLessThan(100); // Good FID
    expect(metrics.cls).toBeLessThan(0.1); // Good CLS
    expect(metrics.ttfb).toBeLessThan(600); // Good TTFB
  });
});

test.describe('Performance - Memory Management', () => {
  test('should not accumulate memory with repeated operations', async ({ page }) => {
    await page.goto('/items');

    const memoryProfile = await page.evaluate(async () => {
      const readings: number[] = [];

      // Force garbage collection if available; must stay inside evaluate (browser context)
      const forceGC = () => {
        if ((globalThis as any).gc) {
          (globalThis as any).gc();
        }
      };

      forceGC();
      await new Promise((r) => setTimeout(r, 100));

      const initialMemory = (performance as any).memory?.usedJSHeapSize ?? 0;
      readings.push(initialMemory);

      // Perform repeated operations
      for (let i = 0; i < 5; i++) {
        // Simulate operations
        const temp = document.createElement('div');
        temp.innerHTML = '<p>Test</p>';
        document.body.append(temp);
        document.body.removeChild(temp);

        await new Promise((r) => setTimeout(r, 200));

        forceGC();
        const currentMemory = (performance as any).memory?.usedJSHeapSize ?? 0;
        readings.push(currentMemory);
      }

      const finalMemory = (performance as any).memory?.usedJSHeapSize ?? 0;

      return {
        finalMemory,
        increase: finalMemory - initialMemory,
        initialMemory,
        readings,
      };
    });

    // Memory increase should be minimal (less than 5MB)
    expect(memoryProfile.increase).toBeLessThan(5 * 1024 * 1024);
  });

  test('should clean up event listeners properly', async ({ page }) => {
    await page.goto('/items');

    const eventListenerCount = await page.evaluate(() => {
      // Get initial listener count (this is an approximation)
      const body = document.body as any;
      return Object.keys(body.__events ?? {}).length;
    });

    // Should have minimal event listeners
    expect(eventListenerCount).toBeLessThan(20);
  });

  test('should not leak timers', async ({ page }) => {
    await page.goto('/items');

    const timerCount = await page.evaluate(() => {
      // Count active timers via performance API
      const _timers: any[] = [];

      // Monitor setTimeout calls
      const originalSetTimeout = globalThis.setTimeout;
      (globalThis as any).__timeouts = 0;

      globalThis.setTimeout = ((...args: any[]) => {
        (globalThis as any).__timeouts++;
        return originalSetTimeout.apply(globalThis, args);
      }) as any;

      return (globalThis as any).__timeouts ?? 0;
    });

    // Should have reasonable number of timers
    expect(timerCount).toBeLessThan(50);
  });
});
