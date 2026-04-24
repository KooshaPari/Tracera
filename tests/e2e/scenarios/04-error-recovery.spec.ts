// tests/e2e/scenarios/04-error-recovery.spec.ts
// Scenario: Error Recovery
// Linked to: Scenario 4, Stories US-SC-4.1 to US-SC-4.50
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { test, expect } from '@playwright/test';

test.describe('Scenario: Error Recovery', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.fill('input[name="email"]', 'sarah@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard');
  });

  // NETWORK ERROR RECOVERY
  // ============================================================================

  test('SC-4.1: Recover from network timeout', async ({ page }) => {
    await page.route('**/api/items', route => route.abort());
    await page.goto('http://localhost:3000/items');
    
    // Verify error message
    await expect(page.locator('text=Network error')).toBeVisible();
    
    // Retry
    await page.route('**/api/items', route => route.continue());
    await page.click('button:has-text("Retry")');
    await expect(page.locator('[data-testid="item-list"]')).toBeVisible();
  });

  test('SC-4.2: Handle 500 server error', async ({ page }) => {
    await page.route('**/api/items', route => route.fulfill({ status: 500 }));
    await page.goto('http://localhost:3000/items');
    
    await expect(page.locator('text=Server error')).toBeVisible();
    await expect(page.locator('button:has-text("Retry")')).toBeVisible();
  });

  test('SC-4.3: Handle 404 not found', async ({ page }) => {
    await page.goto('http://localhost:3000/items/nonexistent-id');
    await expect(page.locator('text=Item not found')).toBeVisible();
    await expect(page.locator('button:has-text("Go Back")')).toBeVisible();
  });

  test('SC-4.4: Recover from connection loss', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Connection Test');
    
    // Simulate connection loss
    await page.route('**/api/items', route => route.abort());
    await page.click('button:has-text("Save")');
    
    await expect(page.locator('text=Connection lost')).toBeVisible();
    
    // Restore connection
    await page.route('**/api/items', route => route.continue());
    await page.click('button:has-text("Retry")');
    await expect(page.locator('text=Connection Test')).toBeVisible();
  });

  test('SC-4.5: Handle invalid data format', async ({ page }) => {
    await page.route('**/api/items', route => 
      route.fulfill({ 
        status: 200, 
        body: 'invalid json',
        headers: { 'Content-Type': 'application/json' }
      })
    );
    await page.goto('http://localhost:3000/items');
    
    await expect(page.locator('text=Invalid data format')).toBeVisible();
  });

  // VALIDATION ERROR RECOVERY
  // ============================================================================

  test('SC-4.6: Recover from validation error', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', ''); // Invalid: empty
    await page.click('button:has-text("Save")');
    
    await expect(page.locator('text=Title is required')).toBeVisible();
    
    // Fix and retry
    await page.fill('input[name="title"]', 'Valid Title');
    await page.click('button:has-text("Save")');
    await expect(page.locator('text=Valid Title')).toBeVisible();
  });

  test('SC-4.7: Handle duplicate item error', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Duplicate Test');
    await page.click('button:has-text("Save")');
    
    // Try to create duplicate
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Duplicate Test');
    await page.click('button:has-text("Save")');
    
    await expect(page.locator('text=Item already exists')).toBeVisible();
  });

  test('SC-4.8: Recover from permission error', async ({ page }) => {
    await page.route('**/api/items', route => 
      route.fulfill({ status: 403, body: JSON.stringify({ error: 'Forbidden' }) })
    );
    await page.goto('http://localhost:3000/items');
    
    await expect(page.locator('text=Permission denied')).toBeVisible();
  });

  // STATE RECOVERY
  // ============================================================================

  test('SC-4.9: Recover unsaved changes after error', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Unsaved Changes');
    await page.fill('textarea[name="description"]', 'Important description');
    
    // Simulate error
    await page.route('**/api/items', route => route.abort());
    await page.click('button:has-text("Save")');
    
    // Verify recovery option
    await expect(page.locator('button:has-text("Recover Draft")')).toBeVisible();
    await page.click('button:has-text("Recover Draft")');
    
    await expect(page.locator('input[name="title"]')).toHaveValue('Unsaved Changes');
    await expect(page.locator('textarea[name="description"]')).toHaveValue('Important description');
  });

  test('SC-4.10: Restore session after logout error', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    await page.route('**/api/logout', route => route.abort());
    await page.click('button:has-text("Logout")');
    
    // Verify error handling
    await expect(page.locator('text=Logout failed')).toBeVisible();
    
    // Retry
    await page.route('**/api/logout', route => route.continue());
    await page.click('button:has-text("Retry")');
    await expect(page).toHaveURL('**/login');
  });

  test('SC-4.11: Handle partial save failure', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Partial Save');
    await page.fill('textarea[name="description"]', 'Description');
    
    // Simulate partial failure
    await page.route('**/api/items', route => {
      if (route.request().postData()?.includes('description')) {
        route.abort();
      } else {
        route.continue();
      }
    });
    
    await page.click('button:has-text("Save")');
    await expect(page.locator('text=Partial save successful')).toBeVisible();
    await expect(page.locator('button:has-text("Retry Description")')).toBeVisible();
  });

  test('SC-4.12: Recover from browser crash simulation', async ({ page }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Crash Test');
    
    // Simulate crash by closing page
    await page.close();
    
    // Reopen and verify recovery
    const newPage = await page.context().newPage();
    await newPage.goto('http://localhost:3000');
    await newPage.fill('input[name="email"]', 'sarah@example.com');
    await newPage.fill('input[name="password"]', 'password123');
    await newPage.click('button:has-text("Login")');
    
    // Check for recovery prompt
    await expect(newPage.locator('button:has-text("Recover Draft")')).toBeVisible({ timeout: 5000 });
  });

  // Additional error recovery scenarios (SC-4.13 to SC-4.50)
  for (let i = 13; i <= 50; i++) {
    test(`SC-4.${i}: Error recovery scenario ${i}`, async ({ page }) => {
      await page.goto('http://localhost:3000/items');
      
      // Simulate various errors
      if (i % 3 === 0) {
        await page.route('**/api/items', route => route.abort());
      } else if (i % 3 === 1) {
        await page.route('**/api/items', route => route.fulfill({ status: 500 }));
      } else {
        await page.route('**/api/items', route => route.fulfill({ status: 404 }));
      }
      
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', `Error Test ${i}`);
      await page.click('button:has-text("Save")');
      
      // Verify error handling
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      await expect(page.locator('button:has-text("Retry")')).toBeVisible();
      
      // Recover
      await page.route('**/api/items', route => route.continue());
      await page.click('button:has-text("Retry")');
      await expect(page.locator(`text=Error Test ${i}`)).toBeVisible({ timeout: 5000 });
    });
  }
});
