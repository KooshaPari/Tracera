import { expect, test } from '@playwright/test';

const BASE_URL = process.env['BASE_URL'] || 'http://localhost:3001';

test.describe('Documentation Site E2E Tests', () => {
  test.describe('Navigation', () => {
    test('should load homepage successfully', async ({ page }) => {
      await page.goto(BASE_URL);

      // Check that page loads
      await expect(page).toHaveTitle(/TraceRTM/i);

      // Check for hero section
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible();

      // Verify no console errors
      const errors: string[] = [];
      page.on('console', (msg) => {
        if (msg.type() === 'error') {
          errors.push(msg.text());
        }
      });

      await page.waitForLoadState('networkidle');
      expect(errors).toHaveLength(0);
    });

    test('should navigate to docs section', async ({ page }) => {
      await page.goto(BASE_URL);

      // Click on docs link
      await page
        .getByRole('link', { name: /docs|documentation/i })
        .first()
        .click();

      // Should navigate to docs page
      await expect(page).toHaveURL(/\/docs/);

      // Sidebar should be visible
      await expect(page.locator('nav, aside').first()).toBeVisible();
    });

    test('should navigate between documentation pages', async ({ page }) => {
      await page.goto(`${BASE_URL}/docs`);

      // Click on a sidebar link
      const sidebarLinks = page.locator('nav a, aside a');
      const firstLink = sidebarLinks.first();

      await firstLink.click();
      await page.waitForLoadState('networkidle');

      // Should have navigated
      const currentUrl = page.url();
      expect(currentUrl).toContain('/docs');

      // Content should be visible
      await expect(page.locator('article, main').first()).toBeVisible();
    });

    test('should show breadcrumbs on deep pages', async ({ page }) => {
      await page.goto(`${BASE_URL}/docs/getting-started`);

      // Check for breadcrumb navigation
      const breadcrumb = page
        .locator('nav[aria-label*="breadcrumb" i], .breadcrumb, ol[role="list"]')
        .first();

      if (await breadcrumb.isVisible()) {
        const links = breadcrumb.locator('a');
        expect(await links.count()).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Search Functionality', () => {
    test('should open search dialog with keyboard shortcut', async ({ page }) => {
      await page.goto(`${BASE_URL}/docs`);

      // Press Cmd+K (Mac) or Ctrl+K (Windows/Linux)
      const modifier = process.platform === 'darwin' ? 'Meta' : 'Control';
      await page.keyboard.press(`${modifier}+k`);

      // Search dialog should appear
      await expect(page.locator('dialog, [role="dialog"], [cmdk-root]').first()).toBeVisible({
        timeout: 1000,
      });
    });

    test('should search and display results quickly', async ({ page }) => {
      await page.goto(`${BASE_URL}/docs`);

      // Open search
      const modifier = process.platform === 'darwin' ? 'Meta' : 'Control';
      await page.keyboard.press(`${modifier}+k`);

      // Wait for search input
      const searchInput = page
        .locator('input[type="search"], input[placeholder*="search" i]')
        .first();
      await expect(searchInput).toBeVisible({ timeout: 1000 });

      // Measure search performance
      const startTime = Date.now();

      await searchInput.fill('getting started');

      // Wait for results
      await page.waitForSelector('[cmdk-item], [role="option"]', { timeout: 500 });

      const searchTime = Date.now() - startTime;

      // Search should be fast (<100ms)
      expect(searchTime).toBeLessThan(100);

      // Results should be visible
      const results = page.locator('[cmdk-item], [role="option"]');
      expect(await results.count()).toBeGreaterThan(0);
    });

    test('should navigate to result when clicked', async ({ page }) => {
      await page.goto(`${BASE_URL}/docs`);

      // Open search
      const modifier = process.platform === 'darwin' ? 'Meta' : 'Control';
      await page.keyboard.press(`${modifier}+k`);

      const searchInput = page
        .locator('input[type="search"], input[placeholder*="search" i]')
        .first();
      await searchInput.fill('getting');

      // Wait for results and click first one
      const firstResult = page.locator('[cmdk-item], [role="option"]').first();
      await firstResult.waitFor({ state: 'visible' });
      await firstResult.click();

      // Should navigate to the result page
      await page.waitForURL(/\/docs\//);

      // Content should be visible
      await expect(page.locator('article, main').first()).toBeVisible();
    });
  });

  test.describe('OpenAPI Documentation', () => {
    test('should render API reference page', async ({ page }) => {
      await page.goto(`${BASE_URL}/api-reference`);

      // Page should load
      await expect(page).toHaveURL(/api-reference/);

      // API endpoints should be visible
      await expect(page.locator('h2, h3, .endpoint, [data-endpoint]').first()).toBeVisible({
        timeout: 3000,
      });
    });

    test('should expand/collapse API operations', async ({ page }) => {
      await page.goto(`${BASE_URL}/api-reference`);

      // Find expandable operations
      const operation = page.locator('summary, button[aria-expanded], .accordion-trigger').first();

      if (await operation.isVisible()) {
        await operation.click();

        // Details should expand
        await expect(
          page.locator('details[open], [data-state="open"], .expanded').first(),
        ).toBeVisible();
      }
    });

    test('should display request/response schemas', async ({ page }) => {
      await page.goto(`${BASE_URL}/api-reference`);

      // Look for schema sections
      const schemaSection = page.locator('pre, code, .schema, [data-schema]').first();

      await expect(schemaSection).toBeVisible({ timeout: 3000 });
    });
  });

  test.describe('Dark Mode', () => {
    test('should toggle dark mode', async ({ page }) => {
      await page.goto(BASE_URL);

      // Find theme toggle button
      const themeToggle = page
        .locator('button[aria-label*="theme" i], button[title*="theme" i], [data-theme-toggle]')
        .first();

      await expect(themeToggle).toBeVisible();

      // Get initial theme
      const htmlElement = page.locator('html');
      const initialTheme = await htmlElement.getAttribute('class');

      // Toggle theme
      await themeToggle.click();

      // Wait for theme change
      await page.waitForTimeout(100);

      // Theme should have changed
      const newTheme = await htmlElement.getAttribute('class');
      expect(newTheme).not.toBe(initialTheme);
    });

    test('should persist theme preference', async ({ page }) => {
      await page.goto(BASE_URL);

      // Toggle to dark mode
      const themeToggle = page
        .locator('button[aria-label*="theme" i], button[title*="theme" i], [data-theme-toggle]')
        .first();

      await themeToggle.click();
      await page.waitForTimeout(100);

      // Get dark mode class
      const htmlElement = page.locator('html');
      const darkTheme = await htmlElement.getAttribute('class');

      // Reload page
      await page.reload();

      // Theme should persist
      const persistedTheme = await htmlElement.getAttribute('class');
      expect(persistedTheme).toBe(darkTheme);
    });
  });

  test.describe('Performance', () => {
    test('should load page within performance budget', async ({ page }) => {
      const startTime = Date.now();

      await page.goto(`${BASE_URL}/docs`);
      await page.waitForLoadState('networkidle');

      const loadTime = Date.now() - startTime;

      // Page should load in under 3 seconds
      expect(loadTime).toBeLessThan(3000);
    });

    test('should have no layout shifts', async ({ page }) => {
      await page.goto(`${BASE_URL}/docs`);

      // Monitor for layout shifts
      const cls = await page.evaluate(
        () =>
          new Promise<number>((resolve) => {
            let clsValue = 0;

            const observer = new PerformanceObserver((list) => {
              for (const entry of list.getEntries()) {
                if ((entry as any).hadRecentInput) continue;
                clsValue += (entry as any).value;
              }
            });

            observer.observe({ buffered: true, type: 'layout-shift' });

            setTimeout(() => {
              observer.disconnect();
              resolve(clsValue);
            }, 2000);
          }),
      );

      // CLS should be < 0.1
      expect(cls).toBeLessThan(0.1);
    });

    test('should have fast time to interactive', async ({ page }) => {
      await page.goto(`${BASE_URL}/docs`);

      const tti = await page.evaluate(
        () =>
          new Promise<number>((resolve) => {
            const observer = new PerformanceObserver((list) => {
              for (const entry of list.getEntries()) {
                if (entry.entryType === 'navigation') {
                  const nav = entry as PerformanceNavigationTiming;
                  const tti = nav.domInteractive - nav.fetchStart;
                  resolve(tti);
                }
              }
            });

            observer.observe({ buffered: true, type: 'navigation' });

            setTimeout(() => {
              observer.disconnect();
              resolve(0);
            }, 1000);
          }),
      );

      // TTI should be < 2500ms
      if (tti > 0) {
        expect(tti).toBeLessThan(2500);
      }
    });
  });

  test.describe('Accessibility', () => {
    test('should have no automatic accessibility violations', async ({ page }) => {
      await page.goto(`${BASE_URL}/docs`);

      // Check for basic accessibility
      await expect(page.locator('main, [role="main"]').first()).toBeVisible();

      // Should have skip to content link
      const skipLink = page.locator('a[href="#main"], a[href="#content"]').first();
      if ((await skipLink.count()) > 0) {
        await expect(skipLink).toHaveAttribute('href');
      }

      // Check for heading hierarchy
      const h1Count = await page.locator('h1').count();
      expect(h1Count).toBeGreaterThan(0);
      expect(h1Count).toBeLessThanOrEqual(1); // Should have exactly one h1
    });

    test('should support keyboard navigation', async ({ page }) => {
      await page.goto(`${BASE_URL}/docs`);

      // Tab through focusable elements
      await page.keyboard.press('Tab');

      // Active element should be visible
      const activeElement = await page.evaluate(() => {
        const el = document.activeElement;
        return el ? el.tagName : null;
      });

      expect(activeElement).toBeTruthy();
    });
  });

  test.describe('Mobile Responsiveness', () => {
    test.use({
      viewport: { height: 667, width: 375 }, // IPhone SE size
    });

    test('should render correctly on mobile', async ({ page }) => {
      await page.goto(`${BASE_URL}/docs`);

      // Page should load
      await expect(page.locator('main, article').first()).toBeVisible();

      // Mobile menu button should be visible
      const menuButton = page
        .locator('button[aria-label*="menu" i], button[aria-controls*="menu" i]')
        .first();

      if ((await menuButton.count()) > 0) {
        await expect(menuButton).toBeVisible();
      }
    });

    test('should open mobile navigation', async ({ page }) => {
      await page.goto(`${BASE_URL}/docs`);

      const menuButton = page
        .locator('button[aria-label*="menu" i], button[aria-controls*="menu" i]')
        .first();

      if ((await menuButton.count()) > 0) {
        await menuButton.click();

        // Navigation should appear
        await expect(page.locator('nav, aside, [role="navigation"]').first()).toBeVisible();
      }
    });
  });
});
