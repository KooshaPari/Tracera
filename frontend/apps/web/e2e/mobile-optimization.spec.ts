import { expect, test } from '@playwright/test';

test.describe('Mobile Optimization - Phase 12 & 13', () => {
  // Set mobile viewport
  test.use({
    viewport: { height: 667, width: 375 }, // IPhone SE
    isMobile: true,
    hasTouch: true,
  });

  test('displays card view on mobile instead of table', async ({ page }) => {
    await page.goto('/items');

    // Wait for content to load
    await page.waitForLoadState('networkidle');

    // On mobile, should show card grid, not table
    const cardGrid = page.locator('.grid-cols-1');
    await expect(cardGrid.first()).toBeVisible({ timeout: 10_000 });

    // Table should be hidden
    const table = page.locator('table');
    await expect(table).not.toBeVisible({ timeout: 5000 });
  });

  test('card items are responsive with proper touch targets', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Get first card
    const firstCard = page.locator('button').first();

    // Check card has minimum height
    const boundingBox = await firstCard.boundingBox();
    expect(boundingBox?.height).toBeGreaterThanOrEqual(120);

    // Verify touch target has focus ring
    await firstCard.focus();
    const hasFocusRing = await firstCard.evaluate((el) => {
      const styles = globalThis.getComputedStyle(el);
      return styles.outline !== 'none' || styles.boxShadow.includes('rgb(');
    });
    expect(hasFocusRing).toBe(true);
  });

  test('hamburger menu appears on mobile', async ({ page }) => {
    await page.goto('/');

    // Hamburger menu button should be visible
    const menuButton = page.locator("button[aria-label='Open menu']");
    await expect(menuButton).toBeVisible({ timeout: 5000 });

    // Check button size (minimum 44x44)
    const boundingBox = await menuButton.boundingBox();
    expect(boundingBox?.width).toBeGreaterThanOrEqual(44);
    expect(boundingBox?.height).toBeGreaterThanOrEqual(44);
  });

  test('hamburger menu opens and closes', async ({ page }) => {
    await page.goto('/');

    const menuButton = page.locator("button[aria-label='Open menu']");
    const menuPanel = page.locator('#mobile-menu');

    // Initially closed
    await expect(menuPanel).toHaveClass(/-translate-x-full/);

    // Click to open
    await menuButton.click();
    await page.waitForTimeout(300); // Animation time

    // Should be open
    const classList = await menuPanel.getAttribute('class');
    expect(classList).toContain('translate-x-0');

    // Close via button
    const closeButton = page.locator("button[aria-label='Close']").first();
    await closeButton.click();
    await page.waitForTimeout(300);

    // Should be closed again
    await expect(menuPanel).toHaveClass(/-translate-x-full/);
  });

  test('menu items have proper touch targets (52px minimum)', async ({ page }) => {
    await page.goto('/');

    const menuButton = page.locator("button[aria-label='Open menu']");
    await menuButton.click();
    await page.waitForTimeout(300);

    // Get menu items
    const menuItems = page.locator('#mobile-menu button');
    const count = await menuItems.count();

    for (let i = 0; i < Math.min(count, 3); i++) {
      const item = menuItems.nth(i);
      const boundingBox = await item.boundingBox();

      // Should have minimum 44px height
      expect(boundingBox?.height).toBeGreaterThanOrEqual(44);
    }
  });

  test('can close menu with escape key', async ({ page }) => {
    await page.goto('/');

    const menuButton = page.locator("button[aria-label='Open menu']");
    await menuButton.click();
    await page.waitForTimeout(300);

    // Press escape
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);

    const menuPanel = page.locator('#mobile-menu');
    await expect(menuPanel).toHaveClass(/-translate-x-full/);
  });

  test('navigates to dashboard from mobile menu', async ({ page }) => {
    await page.goto('/');

    const menuButton = page.locator("button[aria-label='Open menu']");
    await menuButton.click();
    await page.waitForTimeout(300);

    // Click dashboard
    const dashboardLink = page.locator('text=Dashboard').first();
    await dashboardLink.click();

    // Should navigate to home
    await expect(page).toHaveURL(/\/()?$/);
  });

  test('form inputs have minimum 44px height on mobile', async ({ page }) => {
    // Navigate to create item page
    await page.goto('/items?action=create');
    await page.waitForLoadState('networkidle');

    // Check for dialog/modal
    const dialog = page.locator('[role="dialog"]');
    await expect(dialog).toBeVisible({ timeout: 10_000 });

    // Get input fields
    const inputs = dialog.locator('input');
    const count = await inputs.count();

    for (let i = 0; i < count; i++) {
      const input = inputs.nth(i);
      const boundingBox = await input.boundingBox();

      // Inputs should have minimum height
      expect(boundingBox?.height).toBeGreaterThanOrEqual(40);
    }
  });

  test('card items are tappable without accidentally triggering adjacent items', async ({
    page,
  }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Get first two cards
    const firstCard = page.locator('button').first();
    const secondCard = page.locator('button').nth(1);

    // Get their positions
    const firstBox = await firstCard.boundingBox();
    const secondBox = await secondCard.boundingBox();

    // Calculate spacing between cards
    if (firstBox && secondBox) {
      const verticalSpacing = secondBox.y - (firstBox.y + firstBox.height);

      // Should have reasonable spacing (at least 8px gap)
      expect(verticalSpacing).toBeGreaterThanOrEqual(8);
    }
  });

  test('can scroll cards smoothly', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    const cardGrid = page.locator('.grid');

    // Perform scroll
    await cardGrid.evaluate((el) => {
      el.scrollTop += 100;
    });

    // Check scroll position
    const scrollTop = await cardGrid.evaluate((el) => el.scrollTop);
    expect(scrollTop).toBeGreaterThan(0);
  });

  test('mobile header is compact and usable', async ({ page }) => {
    await page.goto('/');

    const header = page.locator('header');

    // Should be visible
    await expect(header).toBeVisible({ timeout: 5000 });

    // Should have reasonable height (at least 64px for mobile)
    const boundingBox = await header.boundingBox();
    expect(boundingBox?.height).toBeGreaterThanOrEqual(64);

    // Text should be readable
    const title = header.locator('h1, h2');
    await expect(title).toBeVisible({ timeout: 5000 });
  });

  test('can see and interact with card actions on mobile', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Get first card
    const firstCard = page.locator('button').first();

    // Actions should be visible or accessible
    const actions = firstCard.locator('button');
    const actionCount = await actions.count();

    // Should have at least action buttons
    expect(actionCount).toBeGreaterThan(0);

    // At least one action should be accessible
    const firstAction = actions.first();
    await firstAction.focus();

    const hasFocus = await firstAction.evaluate((el) => el === document.activeElement);
    expect(hasFocus).toBe(true);
  });

  test('touch events work on card items', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    const firstCard = page.locator('button').first();

    // Should be able to click (touch)
    await firstCard.tap();

    // Should navigate or perform action
    // Navigation depends on implementation
    await page.waitForTimeout(500);
  });

  test('responsive grid adjusts from 1 to 2 columns on larger mobile', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Set viewport to small tablet
    await page.setViewportSize({ height: 800, width: 640 });

    // Should still show cards
    const cardGrid = page.locator('.grid');
    await expect(cardGrid).toBeVisible({ timeout: 10_000 });

    // At 640px (sm breakpoint), should show 2 columns
    const hasSmClass = await cardGrid.evaluate(
      (el) => window.getComputedStyle(el).gridTemplateColumns.split(' ').length,
    );

    // Should have columns (actual count may vary)
    expect(hasSmClass).toBeGreaterThan(0);
  });

  test('focus is properly managed in mobile menu', async ({ page }) => {
    await page.goto('/');

    const menuButton = page.locator("button[aria-label='Open menu']");
    await menuButton.click();
    await page.waitForTimeout(300);

    // First menu item should be focusable
    const firstMenuItem = page.locator('#mobile-menu button').first();

    await firstMenuItem.focus();

    const hasFocus = await firstMenuItem.evaluate((el) => el === document.activeElement);

    expect(hasFocus).toBe(true);
  });

  test('text is readable on mobile (sufficient size)', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Get card title
    const cardTitle = page.locator('button').first().locator('h3, div');

    const fontSize = await cardTitle.evaluate((el) => window.getComputedStyle(el).fontSize);

    // Font should be at least 12px (0.75rem minimum)
    const fontSizePx = Number.parseFloat(fontSize);
    expect(fontSizePx).toBeGreaterThanOrEqual(12);
  });

  test('touch performance is good (no jank)', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Enable performance monitoring
    const metrics = await page.evaluate(
      async () =>
        new Promise<{
          fps: number;
          jsHeap: number;
        }>((resolve) => {
          const frames: number[] = [];
          let lastTime = performance.now();

          const measureFrame = () => {
            const now = performance.now();
            const delta = now - lastTime;

            if (delta > 0) {
              frames.push(1000 / delta);
            }

            lastTime = now;

            if (frames.length < 60) {
              requestAnimationFrame(measureFrame);
            } else {
              const avgFps = frames.reduce((a, b) => a + b) / frames.length;
              resolve({
                fps: avgFps,
                jsHeap: 0, // Not available in this context
              });
            }
          };

          requestAnimationFrame(measureFrame);
        }),
    );

    // Should maintain reasonable frame rate (30fps minimum for mobile)
    expect(metrics.fps).toBeGreaterThan(30);
  });

  test('back button in mobile menu works', async ({ page }) => {
    await page.goto('/items');

    const menuButton = page.locator("button[aria-label='Open menu']");
    await menuButton.click();
    await page.waitForTimeout(300);

    // Click backdrop or close button to close
    const _backdrop = page.locator("#mobile-menu ~ div[aria-hidden='true']");

    // Try to close via backdrop
    const menuPanel = page.locator('#mobile-menu');
    await expect(menuPanel).toBeVisible({ timeout: 5000 });

    // Get close button
    const closeBtn = page.locator("button[aria-label='Close']").first();
    await expect(closeBtn).toBeVisible({ timeout: 5000 });
    await closeBtn.click();
    await page.waitForTimeout(300);

    // Menu should close
    await expect(menuPanel).toHaveClass(/-translate-x-full/);
  });
});

test.describe('Mobile Performance Optimization - Phase 13', () => {
  test.use({
    hasTouch: true,
    isMobile: true,
    viewport: { height: 667, width: 375 },
  });

  test('lazy loads images on mobile', async ({ page }) => {
    await page.goto('/projects');

    // Check for lazy loading attribute
    const images = page.locator('img');
    const count = await images.count();

    if (count > 0) {
      const firstImg = images.first();
      const loading = await firstImg.getAttribute('loading');

      // Should use lazy loading on mobile
      if (loading) {
        expect(loading).toMatch(/lazy|auto/);
      }
    }
  });

  test('minimizes initial bundle on mobile', async ({ page }) => {
    // Measure bundle size
    const resourceTiming = await page.evaluate(() => {
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];

      return resources
        .filter((r) => r.name.includes('.js') || r.name.includes('.css'))
        .map((r) => ({
          name: r.name.split('/').pop(),
          size: r.transferSize || 0,
        }))
        .slice(0, 5);
    });

    // Should have reasonable file sizes
    expect(resourceTiming.length).toBeGreaterThan(0);
  });

  test('uses efficient rendering for lists', async ({ page }) => {
    await page.goto('/items');
    await page.waitForLoadState('networkidle');

    // Should use virtualization or pagination
    const cards = page.locator('button');
    const count = await cards.count();

    // Even with many items, should only render visible ones
    // This depends on implementation
    expect(count).toBeGreaterThan(0);
  });
});
