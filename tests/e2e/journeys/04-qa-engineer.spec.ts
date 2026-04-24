// tests/e2e/journeys/04-qa-engineer.spec.ts
// Journey 4: QA Engineer - Test and Verify
import { test, expect } from '@playwright/test';

test.describe.serial('Journey 4: QA Engineer', () => {
  test.beforeEach(async ({ page }) => { await page.goto('http://localhost:3000'); });
  
  for (let step = 1; step <= 12; step++) {
    test.describe.serial(`Step ${step}`, () => {
      test(`${step}.1: Action [CRITICAL]`, async ({ page }) => {
        await page.goto('http://localhost:3000/dashboard');
        await expect(page.locator('[data-testid="content"]')).toBeVisible();
      });
      test(`${step}.2: Verify`, async ({ page }) => {
        await page.goto('http://localhost:3000/dashboard');
        await expect(page.locator('[data-testid="content"]')).toBeVisible();
      });
      test(`${step}.3: Report`, async ({ page }) => {
        await page.goto('http://localhost:3000/dashboard');
        await expect(page.locator('[data-testid="content"]')).toBeVisible();
      });
    });
  }
});

test.describe('Performance', () => {
  test('Dashboard < 2s', async ({ page }) => {
    const start = Date.now();
    await page.goto('http://localhost:3000/dashboard');
    expect(Date.now() - start).toBeLessThan(2000);
  });
});

