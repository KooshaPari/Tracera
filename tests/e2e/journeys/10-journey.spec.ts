// Journey 10
import { test, expect } from '@playwright/test';

test.describe.serial('Journey 10', () => {
  test.beforeEach(async ({ page }) => { await page.goto('http://localhost:3000'); });
  
  for (let step = 1; step <= 12; step++) {
    test.describe.serial(`Step ${step}`, () => {
      test(`${step}.1: Action [CRITICAL]`, async ({ page }) => {
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
