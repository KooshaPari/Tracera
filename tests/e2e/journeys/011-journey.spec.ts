// Journey 11 Test
import { test, expect } from '@playwright/test';

test.describe.serial('Journey 11', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  for (let step = 1; step <= 12; step++) {
    test.describe.serial(`Step ${step}`, () => {
      test(`${step}.1: Action [CRITICAL]`, async ({ page }) => {
        await page.goto('http://localhost:3000/dashboard');
        await expect(page.locator('[data-testid="content"]')).toBeVisible();
      });
    });
  }
});

test.describe('Performance Tests', () => {
  test('Dashboard < 2s', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('http://localhost:3000/dashboard');
    const endTime = Date.now();
    expect(endTime - startTime).toBeLessThan(2000);
  });
});
