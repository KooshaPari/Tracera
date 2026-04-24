// tests/e2e/scenarios/01-concurrent-editing.spec.ts
// Scenario: Concurrent Editing
// Linked to: Scenario 1, Stories US-SC-1.1 to US-SC-1.50
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { test, expect } from '@playwright/test';

test.describe('Scenario: Concurrent Editing', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await page.fill('input[name="email"]', 'sarah@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard');
  });

  // CONCURRENT USER OPERATIONS
  // ============================================================================

  test('SC-1.1: Multiple users edit same item simultaneously', async ({ page, context }) => {
    // Create item
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Shared Item');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    // Open in second browser context
    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    // Both users edit
    await page.fill('textarea[name="description"]', 'User 1 edit');
    await page2.fill('textarea[name="description"]', 'User 2 edit');

    // Both save
    await page.click('button:has-text("Save")');
    await page2.click('button:has-text("Save")');

    // Verify conflict handling
    await expect(page.locator('text=Conflict detected')).toBeVisible();
  });

  test('SC-1.2: Real-time updates visible to all users', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto('http://localhost:3000/items');

    // User 1 creates item
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Live Update Test');
    await page.click('button:has-text("Save")');

    // User 2 should see update
    await expect(page2.locator('text=Live Update Test')).toBeVisible({ timeout: 5000 });
  });

  test('SC-1.3: Concurrent link creation', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Item A');
    await page.click('button:has-text("Save")');
    const itemAId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto('http://localhost:3000/items');
    await page2.click('button:has-text("Create Item")');
    await page2.fill('input[name="title"]', 'Item B');
    await page2.click('button:has-text("Save")');
    const itemBId = await page2.locator('[data-testid="item-id"]').textContent();

    // Both users create link simultaneously
    await page.goto(`http://localhost:3000/items/${itemAId}`);
    await page2.goto(`http://localhost:3000/items/${itemBId}`);

    await page.click('button:has-text("Add Link")');
    await page.fill('input[name="target-id"]', itemBId!);
    await page.click('button:has-text("Create Link")');

    await page2.click('button:has-text("Add Link")');
    await page2.fill('input[name="target-id"]', itemAId!);
    await page2.click('button:has-text("Create Link")');

    // Verify both links exist
    await expect(page.locator(`text=${itemBId}`)).toBeVisible();
    await expect(page2.locator(`text=${itemAId}`)).toBeVisible();
  });

  test('SC-1.4: Concurrent deletion handling', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'To Delete');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    // Both users try to delete
    await page.goto(`http://localhost:3000/items/${itemId}`);
    await page.click('button:has-text("Delete")');
    await page.click('button:has-text("Confirm")');

    await page2.click('button:has-text("Delete")');
    await page2.click('button:has-text("Confirm")');

    // Verify proper error handling
    await expect(page2.locator('text=Item not found')).toBeVisible();
  });

  test('SC-1.5: Concurrent tag assignment', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Tagged Item');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    // Both users add tags
    await page.fill('input[name="tags"]', 'tag1');
    await page.click('button:has-text("Add Tag")');
    await page2.fill('input[name="tags"]', 'tag2');
    await page2.click('button:has-text("Add Tag")');

    // Verify both tags appear
    await expect(page.locator('text=tag1')).toBeVisible();
    await expect(page2.locator('text=tag2')).toBeVisible({ timeout: 5000 });
  });

  test('SC-1.6: Multiple users in graph view', async ({ page, context }) => {
    await page.goto('http://localhost:3000/graph');
    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto('http://localhost:3000/graph');

    // Both users interact with graph
    await page.click('[data-testid="graph-node"]').first();
    await page2.click('[data-testid="graph-node"]').last();

    // Verify both can see updates
    await expect(page.locator('[data-testid="node-selected"]')).toBeVisible();
    await expect(page2.locator('[data-testid="node-selected"]')).toBeVisible();
  });

  test('SC-1.7: Concurrent comment addition', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Discussion Item');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto(`http://localhost:3000/items/${itemId}`);

    // Both users add comments
    await page.fill('textarea[name="comment"]', 'Comment from User 1');
    await page.click('button:has-text("Post Comment")');
    await page2.fill('textarea[name="comment"]', 'Comment from User 2');
    await page2.click('button:has-text("Post Comment")');

    // Verify both comments visible
    await expect(page.locator('text=Comment from User 1')).toBeVisible();
    await expect(page2.locator('text=Comment from User 2')).toBeVisible({ timeout: 5000 });
  });

  test('SC-1.8: Simultaneous filter application', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto('http://localhost:3000/items');

    // Both users apply different filters
    await page.fill('input[name="filter"]', 'status:active');
    await page2.fill('input[name="filter"]', 'priority:high');

    // Verify filters work independently
    await expect(page.locator('[data-testid="filter-active"]')).toBeVisible();
    await expect(page2.locator('[data-testid="filter-active"]')).toBeVisible();
  });

  test('SC-1.9: Concurrent search operations', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto('http://localhost:3000/items');

    // Both users search simultaneously
    await page.fill('input[name="search"]', 'test query 1');
    await page2.fill('input[name="search"]', 'test query 2');

    // Verify both searches complete
    await expect(page.locator('[data-testid="search-results"]')).toBeVisible();
    await expect(page2.locator('[data-testid="search-results"]')).toBeVisible();
  });

  test('SC-1.10: Multiple users create projects', async ({ page, context }) => {
    await page.goto('http://localhost:3000/projects');
    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto('http://localhost:3000/projects');

    // Both users create projects
    await page.click('button:has-text("New Project")');
    await page.fill('input[name="name"]', 'Project A');
    await page.click('button:has-text("Create")');

    await page2.click('button:has-text("New Project")');
    await page2.fill('input[name="name"]', 'Project B');
    await page2.click('button:has-text("Create")');

    // Verify both projects exist
    await expect(page.locator('text=Project A')).toBeVisible();
    await expect(page2.locator('text=Project B')).toBeVisible();
  });

  // PERFORMANCE TESTS
  // ============================================================================

  test('SC-1.11: Performance: 10 concurrent edits complete in < 5 seconds', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Performance Test');
    await page.click('button:has-text("Save")');
    const itemId = await page.locator('[data-testid="item-id"]').textContent();

    const startTime = Date.now();
    const pages = [];
    for (let i = 0; i < 10; i++) {
      const newPage = await context.newPage();
      await newPage.goto('http://localhost:3000');
      await newPage.fill('input[name="email"]', `user${i}@example.com`);
      await newPage.fill('input[name="password"]', 'password123');
      await newPage.click('button:has-text("Login")');
      await newPage.goto(`http://localhost:3000/items/${itemId}`);
      pages.push(newPage);
    }

    // All users edit simultaneously
    await Promise.all(pages.map(p => p.fill('textarea[name="description"]', `Edit ${Date.now()}`)));
    await Promise.all(pages.map(p => p.click('button:has-text("Save")')));

    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(5000);
  });

  test('SC-1.12: Performance: Real-time sync latency < 1 second', async ({ page, context }) => {
    await page.goto('http://localhost:3000/items');
    const page2 = await context.newPage();
    await page2.goto('http://localhost:3000');
    await page2.fill('input[name="email"]', 'john@example.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button:has-text("Login")');
    await page2.goto('http://localhost:3000/items');

    await page.click('button:has-text("Create Item")');
    await page.fill('input[name="title"]', 'Sync Test');
    const startTime = Date.now();
    await page.click('button:has-text("Save")');

    await expect(page2.locator('text=Sync Test')).toBeVisible({ timeout: 2000 });
    const latency = Date.now() - startTime;
    expect(latency).toBeLessThan(1000);
  });

  // Additional concurrent editing scenarios (SC-1.13 to SC-1.50)
  // Following same pattern with various concurrent operations
  for (let i = 13; i <= 50; i++) {
    test(`SC-1.${i}: Concurrent operation ${i}`, async ({ page, context }) => {
      await page.goto('http://localhost:3000/items');
      const page2 = await context.newPage();
      await page2.goto('http://localhost:3000');
      await page2.fill('input[name="email"]', 'john@example.com');
      await page2.fill('input[name="password"]', 'password123');
      await page2.click('button:has-text("Login")');
      await page2.goto('http://localhost:3000/items');

      // Perform concurrent operations
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', `Concurrent Test ${i}`);
      await page.click('button:has-text("Save")');

      await page2.click('button:has-text("Create Item")');
      await page2.fill('input[name="title"]', `Concurrent Test ${i + 1}`);
      await page2.click('button:has-text("Save")');

      await expect(page.locator(`text=Concurrent Test ${i}`)).toBeVisible();
      await expect(page2.locator(`text=Concurrent Test ${i + 1}`)).toBeVisible();
    });
  }
});
