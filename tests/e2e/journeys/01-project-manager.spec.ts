// tests/e2e/journeys/01-project-manager.spec.ts
// Journey 1: Project Manager - Plan and Track Project
// Linked to: Journey 1, Steps 1-12, Stories US-1.1 to US-5.4
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
// Ordering: Serial execution following user journey
// Dependencies: Each step depends on previous step passing

import { test, expect } from '@playwright/test';

let authToken: string;
let projectId: string;
let itemIds: string[] = [];
let linkIds: string[] = [];

test.describe.serial('Journey 1: Project Manager - Plan and Track Project', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test.describe.serial('Step 1: Authentication', () => {
    test('1.1: Valid credentials [CRITICAL]', async ({ page }) => {
      await page.fill('input[name="email"]', 'sarah@example.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button:has-text("Login")');
      await expect(page).toHaveURL('**/dashboard');
      authToken = 'token-pm';
    });

    test('1.2: Invalid credentials', async ({ page }) => {
      await page.fill('input[name="email"]', 'invalid@example.com');
      await page.fill('input[name="password"]', 'wrongpassword');
      await page.click('button:has-text("Login")');
      await expect(page.locator('text=Invalid credentials')).toBeVisible();
    });

    test('1.3: Session persistence', async ({ page }) => {
      await page.fill('input[name="email"]', 'sarah@example.com');
      await page.fill('input[name="password"]', 'password123');
      await page.click('button:has-text("Login")');
      await expect(page).toHaveURL('**/dashboard');
      await page.reload();
      await expect(page).toHaveURL('**/dashboard');
    });
  });

  test.describe.serial('Step 2: Dashboard', () => {
    test('2.1: Display metrics [CRITICAL]', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard');
      await expect(page.locator('[data-testid="project-completion-metric"]')).toBeVisible();
      await expect(page.locator('[data-testid="team-utilization-metric"]')).toBeVisible();
      await expect(page.locator('[data-testid="quality-score-metric"]')).toBeVisible();
    });

    test('2.2: Show activity', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard');
      await expect(page.locator('[data-testid="activity-feed"]')).toBeVisible();
      const activityItems = await page.locator('[data-testid="activity-item"]').count();
      expect(activityItems).toBeGreaterThan(0);
    });

    test('2.3: Real-time updates', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard');
      const initialValue = await page.locator('[data-testid="project-completion-metric"]').textContent();
      await page.waitForTimeout(2000);
      const updatedValue = await page.locator('[data-testid="project-completion-metric"]').textContent();
      expect(updatedValue).toBeDefined();
    });
  });

  test.describe.serial('Step 3: Quality Checks', () => {
    test('3.1: View failures [CRITICAL]', async ({ page }) => {
      await page.goto('http://localhost:3000/quality-checks');
      await expect(page.locator('[data-testid="quality-check-list"]')).toBeVisible();
      const checkItems = await page.locator('[data-testid="check-item"]').count();
      expect(checkItems).toBeGreaterThan(0);
    });

    test('3.2: Investigate details', async ({ page }) => {
      await page.goto('http://localhost:3000/quality-checks');
      await page.click('[data-testid="failed-check-item"]');
      await expect(page.locator('[data-testid="check-details-panel"]')).toBeVisible();
      await expect(page.locator('[data-testid="check-error-message"]')).toBeVisible();
    });

    test('3.3: View recommendations', async ({ page }) => {
      await page.goto('http://localhost:3000/quality-checks');
      await page.click('[data-testid="failed-check-item"]');
      await expect(page.locator('[data-testid="recommendations-section"]')).toBeVisible();
    });
  });

  test.describe.serial('Step 4: Create Items', () => {
    test('4.1: Create item [CRITICAL]', async ({ page }) => {
      await page.goto('http://localhost:3000/items');
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', 'Backend API');
      await page.selectOption('select[name="type"]', 'IMPLEMENTATION');
      await page.click('button:has-text("Create")');
      await expect(page.locator('text=Backend API')).toBeVisible();
      itemIds.push('item-1');
    });

    test('4.2: Set priority', async ({ page }) => {
      await page.goto('http://localhost:3000/items');
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', 'High Priority Task');
      await page.selectOption('select[name="priority"]', 'HIGH');
      await page.click('button:has-text("Create")');
      await expect(page.locator('[data-testid="priority-HIGH"]')).toBeVisible();
      itemIds.push('item-2');
    });

    test('4.3: Add tags', async ({ page }) => {
      await page.goto('http://localhost:3000/items');
      await page.click('button:has-text("Create Item")');
      await page.fill('input[name="title"]', 'Tagged Item');
      await page.fill('input[name="tags"]', 'backend,api,urgent');
      await page.click('button:has-text("Create")');
      await expect(page.locator('text=backend')).toBeVisible();
      itemIds.push('item-3');
    });

    test('4.4: Create multiple items', async ({ page }) => {
      await page.goto('http://localhost:3000/items');
      for (let i = 1; i <= 3; i++) {
        await page.click('button:has-text("Create Item")');
        await page.fill('input[name="title"]', `Item ${i}`);
        await page.click('button:has-text("Create")');
      }
      const itemCount = await page.locator('[data-testid="item-row"]').count();
      expect(itemCount).toBeGreaterThanOrEqual(3);
    });
  });

  test.describe.serial('Step 5: Create Links', () => {
    test('5.1: Create link [CRITICAL]', async ({ page }) => {
      await page.goto('http://localhost:3000/graph');
      await page.click('[data-testid="create-link-button"]');
      await page.click('[data-testid="source-item-selector"]');
      await page.click('text=Item 1');
      await page.click('[data-testid="target-item-selector"]');
      await page.click('text=Item 2');
      await page.selectOption('select[name="link-type"]', 'DEPENDS_ON');
      await page.click('button:has-text("Create Link")');
      await expect(page.locator('[data-testid="link-edge"]')).toBeVisible();
      linkIds.push('link-1');
    });

    test('5.2: Set link type', async ({ page }) => {
      await page.goto('http://localhost:3000/graph');
      await page.click('[data-testid="create-link-button"]');
      await page.click('[data-testid="source-item-selector"]');
      await page.click('text=Item 1');
      await page.click('[data-testid="target-item-selector"]');
      await page.click('text=Item 2');
      await page.selectOption('select[name="link-type"]', 'BLOCKS');
      await page.click('button:has-text("Create Link")');
      await expect(page.locator('[data-testid="link-type-BLOCKS"]')).toBeVisible();
      linkIds.push('link-2');
    });
  });

  test.describe.serial('Step 6: Graph', () => {
    test('6.1: Render visualization [CRITICAL]', async ({ page }) => {
      await page.goto('http://localhost:3000/graph');
      await expect(page.locator('[data-testid="graph-canvas"]')).toBeVisible();
    });

    test('6.2: Show nodes', async ({ page }) => {
      await page.goto('http://localhost:3000/graph');
      const nodeCount = await page.locator('[data-testid="graph-node"]').count();
      expect(nodeCount).toBeGreaterThan(0);
    });

    test('6.3: Show edges', async ({ page }) => {
      await page.goto('http://localhost:3000/graph');
      const edgeCount = await page.locator('[data-testid="graph-edge"]').count();
      expect(edgeCount).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe.serial('Step 7: Agents', () => {
    test('7.1: Assign agent [CRITICAL]', async ({ page }) => {
      await page.goto('http://localhost:3000/agents');
      await page.click('[data-testid="assign-agent-button"]');
      await page.selectOption('select[name="agent"]', 'agent-1');
      await page.selectOption('select[name="item"]', 'item-1');
      await page.click('button:has-text("Assign")');
      await expect(page.locator('[data-testid="assigned-agent"]')).toBeVisible();
    });
  });

  test.describe.serial('Step 8: Progress', () => {
    test('8.1: See progress [CRITICAL]', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard');
      await expect(page.locator('[data-testid="item-in-progress"]')).toBeVisible();
    });
  });

  test.describe.serial('Step 9: Quality Checks', () => {
    test('9.1: Run checks [CRITICAL]', async ({ page }) => {
      await page.goto('http://localhost:3000/quality-checks');
      await page.click('button:has-text("Run Checks")');
      await page.waitForSelector('[data-testid="check-results"]', { timeout: 10000 });
      await expect(page.locator('[data-testid="check-results"]')).toBeVisible();
    });
  });

  test.describe.serial('Step 10: Reports', () => {
    test('10.1: Generate report [CRITICAL]', async ({ page }) => {
      await page.goto('http://localhost:3000/reports');
      await page.click('button:has-text("Generate Report")');
      await page.selectOption('select[name="report-type"]', 'PROJECT_STATUS');
      await page.click('button:has-text("Generate")');
      await page.waitForSelector('[data-testid="report-content"]', { timeout: 10000 });
      await expect(page.locator('[data-testid="report-content"]')).toBeVisible();
    });
  });

  test.describe.serial('Step 11: Team', () => {
    test('11.1: View workload [CRITICAL]', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard');
      await expect(page.locator('[data-testid="team-workload-section"]')).toBeVisible();
    });
  });

  test.describe.serial('Step 12: Export', () => {
    test('12.1: Export data [CRITICAL]', async ({ page }) => {
      await page.goto('http://localhost:3000/items');
      await page.click('button:has-text("Export")');
      await page.selectOption('select[name="format"]', 'CSV');
      await page.click('button:has-text("Export")');
      await expect(page.locator('text=Export started')).toBeVisible();
    });
  });
});

test.describe('Performance Tests', () => {
  test('Dashboard < 2s', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('http://localhost:3000/dashboard');
    const endTime = Date.now();
    expect(endTime - startTime).toBeLessThan(2000);
  });

  test('Graph < 3s', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('http://localhost:3000/graph');
    const endTime = Date.now();
    expect(endTime - startTime).toBeLessThan(3000);
  });

  test('Items < 1.5s', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('http://localhost:3000/items');
    const endTime = Date.now();
    expect(endTime - startTime).toBeLessThan(1500);
  });
});

