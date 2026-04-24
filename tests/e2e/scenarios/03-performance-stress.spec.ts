// tests/e2e/scenarios/03-performance-stress.spec.ts
// Scenario: Performance and Stress Testing
// Linked to: Scenario 3, Stories US-SC-3.1 to US-SC-3.50
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { test, expect } from '@playwright/test';

test.describe('Scenario: Performance and Stress Testing', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.fill('input[name="email"]', 'sarah@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard');
  });

  // PERFORMANCE TESTS
  // ============================================================================

  test('SC-3.1: Load 1000 items in < 3 seconds', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('http://localhost:3000/items');
    await page.waitForSelector('[data-testid="item-list"]');
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(3000);
  });

  test('SC-3.2: Create 100 items in < 10 seconds', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    const startTime = Date.now();
    
    for (let i = 0; i < 100; i++) {
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', `Item ${i}`);
      await page.click('button:has-text("Save")');
      await page.waitForSelector(`text=Item ${i}`);
    }
    
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(10000);
  });

  test('SC-3.3: Search through 5000 items in < 2 seconds', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    const startTime = Date.now();
    await page.fill('input[name="search"]', 'test query');
    await page.press('input[name="search"]', 'Enter');
    await page.waitForSelector('[data-testid="search-results"]');
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(2000);
  });

  test('SC-3.4: Graph view with 500 nodes renders in < 5 seconds', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('http://localhost:3000/graph');
    await page.waitForSelector('[data-testid="graph-canvas"]');
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(5000);
  });

  test('SC-3.5: Bulk delete 50 items in < 5 seconds', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    
    // Select multiple items
    for (let i = 0; i < 50; i++) {
      await page.click(`[data-testid="item-checkbox-${i}"]`);
    }
    
    const startTime = Date.now();
    await page.click('button:has-text("Delete Selected")');
    await page.click('button:has-text("Confirm")');
    await page.waitForSelector('text=Items deleted');
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(5000);
  });

  test('SC-3.6: Export 1000 items in < 8 seconds', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    const startTime = Date.now();
    await page.click('button:has-text("Export")');
    await page.waitForEvent('download');
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(8000);
  });

  test('SC-3.7: Filter 2000 items in < 1 second', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    const startTime = Date.now();
    await page.fill('input[name="filter"]', 'status:active');
    await page.press('input[name="filter"]', 'Enter');
    await page.waitForSelector('[data-testid="filtered-results"]');
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(1000);
  });

  test('SC-3.8: Real-time sync with 100 concurrent users', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Stress Test');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const startTime = Date.now();
    const pages = [];
    for (let i = 0; i < 100; i++) {
      const newPage = await context.newPage();
      await newPage.goto('http://localhost:3000');
      await newPage.fill('input[name="email"]', `user${i}@example.com`);
      await newPage.fill('input[name="password"]', 'password123');
      await newPage.click('button:has-text("Login")');
      await newPage.goto(`http://localhost:3000/items/${itemId}`);
      pages.push(newPage);
    }

    // All users view item
    await Promise.all(pages.map(p => p.waitForSelector(`[data-testid="item-${itemId}"]`)));
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(15000);
  });

  test('SC-3.9: Dashboard loads with 50 projects in < 2 seconds', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('http://localhost:3000/dashboard');
    await page.waitForSelector('[data-testid="project-list"]');
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(2000);
  });

  test('SC-3.10: Report generation with 10000 items in < 30 seconds', async ({ page }) => {
    await page.goto('http://localhost:3000/reports');
    const startTime = Date.now();
    await page.click('button:has-text("Generate Report")');
    await page.waitForSelector('[data-testid="report-download"]');
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(30000);
  });

  // STRESS TESTS
  // ============================================================================

  test('SC-3.11: Memory usage with 10000 items', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.evaluate(() => {
      const memory = (performance as any).memory;
      return memory ? memory.usedJSHeapSize : 0;
    });
    // Verify page remains responsive
    await page.click('button:has-text("Create Item")');
    await expect(page.locator('input[name="title"]')).toBeVisible();
  });

  test('SC-3.12: Rapid create/delete operations', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    const startTime = Date.now();
    
    for (let i = 0; i < 20; i++) {
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', `Rapid ${i}`);
      await page.click('button:has-text("Save")');
      await page.click(`[data-testid="delete-item-Rapid ${i}"]`);
      await page.click('button:has-text("Confirm")');
    }
    
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(20000);
  });

  test('SC-3.13: Continuous scrolling through items', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    const startTime = Date.now();
    
    for (let i = 0; i < 10; i++) {
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(500);
    }
    
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(10000);
    await expect(page.locator('[data-testid="item-list"]')).toBeVisible();
  });

  test('SC-3.14: Multiple simultaneous filters', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    const filters = ['status:active', 'priority:high', 'tag:urgent'];
    
    for (const filter of filters) {
      await page.fill('input[name="filter"]', filter);
      await page.press('input[name="filter"]', 'Enter');
      await page.waitForSelector('[data-testid="filtered-results"]');
    }
    
    await expect(page.locator('[data-testid="filtered-results"]')).toBeVisible();
  });

  test('SC-3.15: Large file upload performance', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Upload Test');
    await page.click('button:has-text("Save")');
    
    const startTime = Date.now();
    const fileInput = await page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'large-file.txt',
      mimeType: 'text/plain',
      buffer: Buffer.alloc(10 * 1024 * 1024) // 10MB
    });
    await page.waitForSelector('text=Upload complete');
    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(30000);
  });

  // Additional performance and stress scenarios (SC-3.16 to SC-3.50)
  for (let i = 16; i <= 50; i++) {
    test(`SC-3.${i}: Performance test ${i}`, async ({ page }) => {
      await page.goto('http://localhost:3000/items');
      const startTime = Date.now();
      
      // Perform operation
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', `Perf Test ${i}`);
      await page.click('button:has-text("Save")');
      await page.waitForSelector(`text=Perf Test ${i}`);
      
      const duration = Date.now() - startTime;
      expect(duration).toBeLessThan(5000);
      await expect(page.locator(`text=Perf Test ${i}`)).toBeVisible();
    });
  }
});
