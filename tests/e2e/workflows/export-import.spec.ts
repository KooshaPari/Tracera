// Workflow: export-import
import { test, expect } from '@playwright/test';

test.describe('Workflow: export-import', () => {
  for (let i = 1; i <= 30; i++) {
    test(`Test ${i}`, async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard');
      await expect(page.locator('[data-testid="content"]')).toBeVisible();
    });
  }
});
