import type { Page } from '@playwright/test';

import { expect } from '@playwright/test';

/**
 * Critical Path Test Helpers
 *
 * Reusable functions for critical path E2E tests
 */

export interface TestProject {
  name: string;
  description?: string;
}

export interface TestItem {
  title: string;
  type?: string;
  status?: string;
  priority?: string;
  description?: string;
  projectId?: string;
}

export interface TestLink {
  sourceId: string;
  targetId: string;
  type: string;
  description?: string;
}

/**
 * Navigation Helpers
 */

export async function authenticateAndNavigate(page: Page, route: string): Promise<void> {
  const authState = {
    account: {
      account_type: 'personal',
      id: 'test-account',
      name: 'Test Account',
      slug: 'test-account',
    },
    isAuthenticated: true,
    token: 'test-token',
    user: {
      email: 'test@example.com',
      id: 'test-user',
      name: 'Test User',
      role: 'admin',
    },
  };

  await page.addInitScript((state) => {
    const serialized = JSON.stringify({ state, version: 0 });
    localStorage.setItem('tracertm-auth-store', serialized);
    if (state.token) {
      localStorage.setItem('auth_token', state.token);
      localStorage.setItem('authToken', state.token);
    }
  }, authState);

  await page.goto(route);
  await page.waitForLoadState('networkidle');
}

export async function navigateToDashboard(page: Page): Promise<void> {
  await page.goto('/');
  await page.waitForLoadState('networkidle');
}

export async function navigateToProjects(page: Page): Promise<void> {
  await page.goto('/projects');
  await page.waitForLoadState('networkidle');
}

export async function navigateToItems(page: Page): Promise<void> {
  await page.goto('/items');
  await page.waitForLoadState('networkidle');
}

export async function navigateToGraph(page: Page): Promise<void> {
  await page.goto('/graph');
  await page.waitForLoadState('networkidle');
}

export async function navigateToSettings(page: Page): Promise<void> {
  await page.goto('/settings');
  await page.waitForLoadState('networkidle');
}

export async function navigateToItemDetail(page: Page, itemId: string): Promise<void> {
  await page.goto(`/items/${itemId}`);
  await page.waitForLoadState('networkidle');
}

export async function navigateToProjectDetail(page: Page, projectId: string): Promise<void> {
  await page.goto(`/projects/${projectId}`);
  await page.waitForLoadState('networkidle');
}

/**
 * Project CRUD Helpers
 */

export async function createProject(page: Page, project: TestProject): Promise<boolean> {
  // Find and click create button
  const createBtn = page.getByRole('button', { name: /create|new|add.*project/i }).first();
  await expect(createBtn).toBeVisible({ timeout: 2000 });

  await createBtn.click();
  await page.waitForTimeout(500);

  // Fill form
  const nameInput = page
    .getByLabel(/name|project name/i)
    .or(page.getByPlaceholder(/name/i))
    .first();

  await expect(nameInput).toBeVisible({ timeout: 2000 });

  await nameInput.fill(project.name);

  if (project.description != null && project.description !== '') {
    const descInput = page
      .getByLabel(/description/i)
      .or(page.getByPlaceholder(/description/i))
      .first();

    await expect(descInput).toBeVisible({ timeout: 1000 });
    await descInput.fill(project.description);
  }

  // Submit
  const submitBtn = page.getByRole('button', {
    name: /create|save|submit/i,
  });

  await expect(submitBtn).toBeVisible({ timeout: 1000 });

  await submitBtn.click();
  await page.waitForLoadState('networkidle');

  // Verify creation
  const projectText = page.getByText(project.name);
  await expect(projectText).toBeVisible({ timeout: 5000 });
  return true;
}

/**
 * Item CRUD Helpers
 */

export async function createItem(page: Page, item: TestItem): Promise<boolean> {
  const createBtn = page.getByRole('button', { name: /create|new|add.*item/i }).first();
  await expect(createBtn).toBeVisible({ timeout: 2000 });

  await createBtn.click();
  await page.waitForTimeout(500);

  // Fill title
  const titleInput = page
    .getByLabel(/title|item title/i)
    .or(page.getByPlaceholder(/title/i))
    .first();

  await expect(titleInput).toBeVisible({ timeout: 2000 });

  await titleInput.fill(item.title);

  // Fill optional fields
  if (item.description != null && item.description !== '') {
    const descInput = page
      .getByLabel(/description/i)
      .or(page.getByPlaceholder(/description/i))
      .first();

    await expect(descInput).toBeVisible({ timeout: 1000 });
    await descInput.fill(item.description);
  }

  if (item.type != null && item.type !== '') {
    const typeSelect = page.getByLabel(/type/i).first();
    await expect(typeSelect).toBeVisible({ timeout: 1000 });
    await typeSelect.click();
    await page.waitForTimeout(300);

    const option = page.getByText(new RegExp(item.type, 'i'));
    await expect(option).toBeVisible({ timeout: 1000 });
    await option.click();
  }

  // Submit
  const submitBtn = page.getByRole('button', {
    name: /create|save|submit|add/i,
  });

  await expect(submitBtn).toBeVisible({ timeout: 1000 });

  await submitBtn.click();
  await page.waitForLoadState('networkidle');

  // Verify
  const itemText = page.getByText(item.title);
  await expect(itemText).toBeVisible({ timeout: 5000 });
  return true;
}

export async function updateItemStatus(page: Page, newStatus: string): Promise<boolean> {
  const statusField = page
    .getByLabel(/status/i)
    .first()
    .or(page.locator("[role='combobox']").filter({ hasText: /status/i }));

  await expect(statusField).toBeVisible({ timeout: 2000 });

  await statusField.click();
  await page.waitForTimeout(300);

  const option = page.getByText(new RegExp(newStatus, 'i'));
  await expect(option).toBeVisible({ timeout: 1000 });

  await option.click();
  await page.waitForLoadState('networkidle');

  return true;
}

export async function deleteItem(page: Page): Promise<boolean> {
  const deleteBtn = page.getByRole('button', { name: /delete/i }).first();

  await expect(deleteBtn).toBeVisible({ timeout: 2000 });

  await deleteBtn.click();
  await page.waitForTimeout(500);

  // Confirm deletion
  const confirmBtn = page.getByRole('button', {
    name: /confirm|yes|delete/i,
  });

  await expect(confirmBtn).toBeVisible({ timeout: 2000 });

  await confirmBtn.click();
  await page.waitForLoadState('networkidle');

  return true;
}

/**
 * Link Helpers
 */

export async function createLink(page: Page, link: TestLink): Promise<boolean> {
  const createLinkBtn = page.getByRole('button', {
    name: /add link|create link|new link/i,
  });

  await expect(createLinkBtn).toBeVisible({ timeout: 2000 });

  await createLinkBtn.click();
  await page.waitForTimeout(500);

  // Select target item
  const targetSelect = page.getByLabel(/target.*item|target/i).first();
  await expect(targetSelect).toBeVisible({ timeout: 2000 });

  await targetSelect.click();
  await page.waitForTimeout(300);

  // Type target item ID and select from dropdown
  // This would depend on the actual UI implementation
  const targetOption = page.locator(`text=${link.targetId}`).first();
  await expect(targetOption).toBeVisible({ timeout: 1000 });

  await targetOption.click();
  await page.waitForTimeout(300);

  // Select link type
  const typeSelect = page.getByLabel(/link type|type/i).first();
  await expect(typeSelect).toBeVisible({ timeout: 1000 });

  await typeSelect.click();
  await page.waitForTimeout(300);

  const typeOption = page.getByText(new RegExp(link.type, 'i'));
  await expect(typeOption).toBeVisible({ timeout: 1000 });

  await typeOption.click();
  await page.waitForTimeout(300);

  // Submit
  const submitBtn = page.getByRole('button', { name: /create|save/i });
  await expect(submitBtn).toBeVisible({ timeout: 1000 });

  await submitBtn.click();
  await page.waitForLoadState('networkidle');

  return true;
}

/**
 * Search and Filter Helpers
 */

export async function searchItems(page: Page, query: string): Promise<number> {
  const searchInput = page
    .getByRole('searchbox')
    .or(page.getByPlaceholder(/search/i))
    .first();

  await expect(searchInput).toBeVisible({ timeout: 2000 });

  await searchInput.fill(query);
  await page.waitForTimeout(500);

  const results = page.getByText(new RegExp(query, 'i'));
  return results.count();
}

export async function filterByType(page: Page, type: string): Promise<boolean> {
  const typeFilter = page
    .getByLabel(/type|filter.*type/i)
    .first()
    .or(page.locator('select').filter({ hasText: /type/i }).first());

  await expect(typeFilter).toBeVisible({ timeout: 2000 });

  await typeFilter.click();
  await page.waitForTimeout(300);

  const option = page.getByText(new RegExp(type, 'i')).first();
  await expect(option).toBeVisible({ timeout: 1000 });

  await option.click();
  await page.waitForTimeout(500);

  return true;
}

export async function filterByStatus(page: Page, status: string): Promise<boolean> {
  const statusFilter = page
    .getByLabel(/status|filter.*status/i)
    .first()
    .or(
      page
        .locator('select')
        .filter({ hasText: /status/i })
        .first(),
    );

  await expect(statusFilter).toBeVisible({ timeout: 2000 });

  await statusFilter.click();
  await page.waitForTimeout(300);

  const option = page.getByText(new RegExp(status, 'i'));
  await expect(option).toBeVisible({ timeout: 1000 });

  await option.click();
  await page.waitForTimeout(500);

  return true;
}

export async function clearSearchAndFilters(page: Page): Promise<boolean> {
  const clearBtn = page.getByRole('button', { name: /clear|reset/i }).first();

  await expect(clearBtn).toBeVisible({ timeout: 2000 });

  await clearBtn.click();
  await page.waitForTimeout(300);

  return true;
}

/**
 * Assertion Helpers
 */

export async function expectPageUrl(page: Page, urlPattern: RegExp | string) {
  if (typeof urlPattern === 'string') {
    await expect(page).toHaveURL(urlPattern);
  } else {
    await expect(page).toHaveURL(urlPattern);
  }
}

export async function expectElementVisible(page: Page, selector: string, timeout = 5000) {
  const element = page.locator(selector);
  await expect(element).toBeVisible({ timeout });
}

export async function expectText(page: Page, text: string, timeout = 5000) {
  const element = page.getByText(text);
  await expect(element).toBeVisible({ timeout });
}

/**
 * Utility Helpers
 */

export async function waitForLoadComplete(page: Page): Promise<void> {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);
}

export function generateUniqueId(prefix = ''): string {
  return `${prefix}${Date.now()}_${Math.random().toString(36).slice(2, 11)}`;
}

export function generateProject(overrides?: Partial<TestProject>): TestProject {
  return {
    name: `Test Project ${Date.now()}`,
    description: 'Test project created via critical path test',
    ...overrides,
  };
}

export function generateItem(overrides?: Partial<TestItem>): TestItem {
  return {
    title: `Test Item ${Date.now()}`,
    type: 'Requirement',
    status: 'Pending',
    priority: 'Medium',
    description: 'Test item created via critical path test',
    ...overrides,
  };
}

/**
 * Table/List Helpers
 */

export async function getTableRowCount(page: Page): Promise<number> {
  const rows = page.locator('tbody tr').or(page.locator("[role='row']"));
  return rows.count();
}

export async function getTableHeaderCount(page: Page): Promise<number> {
  const headers = page.locator("thead [role='columnheader']");
  return headers.count();
}

export async function clickTableRowByText(page: Page, text: string): Promise<boolean> {
  const row = page.getByText(text).first();

  await expect(row).toBeVisible({ timeout: 2000 });

  await row.click();
  await page.waitForLoadState('networkidle');

  return true;
}

/**
 * Dialog/Modal Helpers
 */

export async function expectDialogOpen(page: Page): Promise<boolean> {
  const dialog = page.getByRole('dialog').first();
  await expect(dialog).toBeVisible({ timeout: 2000 });
  return true;
}

export async function closeDialog(page: Page): Promise<boolean> {
  // Try ESC key
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);

  // Check if dialog is closed
  const dialog = page.getByRole('dialog').first();
  await expect(dialog).not.toBeVisible({ timeout: 1000 });
  return true;
}

/**
 * Performance Helpers
 */

export async function measurePageLoadTime(page: Page): Promise<number> {
  const startTime = Date.now();
  await page.waitForLoadState('networkidle');
  return Date.now() - startTime;
}
