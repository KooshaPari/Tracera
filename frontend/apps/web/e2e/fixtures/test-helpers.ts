import type { Page } from '@playwright/test';

import { expect } from '@playwright/test';

/**
 * Test Helper Functions
 *
 * Reusable utilities for E2E tests including authentication,
 * navigation, data setup, and common assertions.
 */

export class TestHelpers {
  constructor(private page: Page) {}

  /**
   * Authentication Helpers
   */
  async login(email = 'test@example.com', password = 'password123') {
    await this.page.goto('/auth/login');
    await this.page.fill('input[name="email"]', email);
    await this.page.fill('input[name="password"]', password);
    await this.page.click('button[type="submit"]');
    await this.page.waitForURL('/');
  }

  async logout() {
    await this.page.click('[data-testid="user-menu"]');
    await this.page.click('[data-testid="logout-button"]');
    await this.page.waitForURL('/auth/login');
  }

  /**
   * Navigation Helpers
   */
  async navigateTo(route: string) {
    await this.page.goto(route);
    await this.page.waitForLoadState('networkidle');
  }

  async navigateToItems() {
    await this.page.click('a[href="/items"]');
    await this.page.waitForURL('/items');
  }

  async navigateToProjects() {
    await this.page.click('a[href="/projects"]');
    await this.page.waitForURL('/projects');
  }

  async navigateToAgents() {
    await this.page.click('a[href="/agents"]');
    await this.page.waitForURL('/agents');
  }

  /**
   * Item Creation Helpers
   */
  async createItem(data: { title: string; description?: string; type?: string; status?: string }) {
    await this.page.click('button:has-text("New Item")');

    await this.page.fill('input[name="title"]', data.title);

    if (data.description) {
      await this.page.fill('textarea[name="description"]', data.description);
    }

    if (data.type) {
      await this.page.selectOption('select[name="type"]', data.type);
    }

    if (data.status) {
      await this.page.selectOption('select[name="status"]', data.status);
    }

    await this.page.click('button:has-text("Save")');
    await this.page.waitForLoadState('networkidle');
  }

  async createProject(data: { name: string; description?: string }) {
    await this.page.click('button:has-text("New Project")');

    await this.page.fill('input[name="name"]', data.name);

    if (data.description) {
      await this.page.fill('textarea[name="description"]', data.description);
    }

    await this.page.click('button:has-text("Create")');
    await this.page.waitForLoadState('networkidle');
  }

  async createAgent(data: { name: string; role?: string }) {
    await this.page.click('button:has-text("New Agent")');

    await this.page.fill('input[name="name"]', data.name);

    if (data.role) {
      await this.page.selectOption('select[name="role"]', data.role);
    }

    await this.page.click('button:has-text("Create")');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Search and Filter Helpers
   */
  async search(query: string) {
    await this.page.fill('[data-testid="search-input"]', query);
    await this.page.waitForTimeout(500); // Debounce
  }

  async globalSearch(query: string) {
    await this.page.keyboard.press('Meta+k');
    await this.page.fill('[data-testid="search-input"]', query);
    await this.page.waitForTimeout(500);
  }

  async applyFilter(filterType: string, value: string) {
    await this.page.click('button:has-text("Filter")');
    await this.page.click(`[data-testid="filter-${filterType}"]`);
    await this.page.fill(`input[name="${filterType}"]`, value);
    await this.page.click('button:has-text("Apply")');
  }

  /**
   * Assertion Helpers
   */
  async assertItemExists(title: string) {
    const item = this.page.locator(`[data-testid="item-card"]:has-text("${title}")`);
    await expect(item).toBeVisible();
  }

  async assertProjectExists(name: string) {
    const project = this.page.locator(`[data-testid="project-card"]:has-text("${name}")`);
    await expect(project).toBeVisible();
  }

  async assertErrorMessage(message: string) {
    const error = this.page.locator('[role="alert"]');
    await expect(error).toBeVisible();
    await expect(error).toContainText(new RegExp(message, 'i'));
  }

  async assertSuccessMessage(message: string) {
    const success = this.page.locator('[data-testid="success-message"]');
    await expect(success).toBeVisible();
    await expect(success).toContainText(new RegExp(message, 'i'));
  }

  /**
   * Modal Helpers
   */
  async openModal(buttonText: string) {
    await this.page.click(`button:has-text("${buttonText}")`);
    const dialog = this.page.locator('[role="dialog"]');
    await expect(dialog).toBeVisible();
  }

  async closeModal() {
    await this.page.keyboard.press('Escape');
    const dialog = this.page.locator('[role="dialog"]');
    await expect(dialog).not.toBeVisible();
  }

  async submitModal() {
    const dialog = this.page.locator('[role="dialog"]');
    await dialog.locator('button:has-text("Save")').click();
    await expect(dialog).not.toBeVisible();
  }

  /**
   * Wait Helpers
   */
  async waitForApiResponse(url: string, timeout = 5000) {
    return this.page.waitForResponse((response) => response.url().includes(url), {
      timeout,
    });
  }

  async waitForToast(text?: string, timeout = 5000) {
    const toast = this.page.locator('[data-testid="toast"]');
    await expect(toast).toBeVisible({ timeout });

    if (text) {
      await expect(toast).toContainText(text);
    }

    return toast;
  }

  /**
   * Bulk Operation Helpers
   */
  async selectMultipleItems(count: number) {
    await this.page.click('button:has-text("Select")');

    for (let i = 0; i < count; i++) {
      await this.page.locator(`[data-testid="item-checkbox"]`).nth(i).click();
    }

    const toolbar = this.page.locator('[data-testid="bulk-toolbar"]');
    await expect(toolbar).toContainText(`${count} selected`);
  }

  async bulkDelete(count: number) {
    await this.selectMultipleItems(count);
    await this.page.click('button:has-text("Delete")');
    await this.page.click('button:has-text("Confirm")');
  }

  /**
   * Link Management Helpers
   */
  async createLink(sourceType: string, targetTitle: string) {
    await this.page.click('button:has-text("Add Link")');
    await this.page.selectOption('select[name="linkType"]', sourceType);
    await this.page.fill('input[name="targetItem"]', targetTitle);
    await this.page.waitForTimeout(500);
    await this.page.click(`[data-testid="search-result"]:has-text("${targetTitle}")`);
    await this.page.click('button:has-text("Create Link")');
  }

  /**
   * Graph View Helpers
   */
  async navigateToGraph() {
    await this.page.click('a[href="/graph"]');
    await this.page.waitForURL('/graph');
    await this.page.waitForSelector('[data-testid="graph-canvas"]');
  }

  async filterGraph(query: string) {
    await this.page.fill('[data-testid="graph-search"]', query);
    await this.page.waitForTimeout(500);
  }

  async getGraphNodeCount(): Promise<number> {
    const nodes = this.page.locator('[data-testid="graph-node"]');
    return nodes.count();
  }

  async getGraphEdgeCount(): Promise<number> {
    const edges = this.page.locator('[data-testid="graph-edge"]');
    return edges.count();
  }

  /**
   * Form Helpers
   */
  async fillForm(formData: Record<string, string>) {
    for (const [name, value] of Object.entries(formData)) {
      const input = this.page.locator(`input[name="${name}"]`);
      const textarea = this.page.locator(`textarea[name="${name}"]`);
      const select = this.page.locator(`select[name="${name}"]`);

      if ((await input.count()) > 0) {
        await input.fill(value);
      } else if ((await textarea.count()) > 0) {
        await textarea.fill(value);
      } else if ((await select.count()) > 0) {
        await select.selectOption(value);
      }
    }
  }

  async getFormValues(fields: string[]): Promise<Record<string, string>> {
    const values: Record<string, string> = {};

    for (const field of fields) {
      const input = this.page.locator(`input[name="${field}"]`);
      const textarea = this.page.locator(`textarea[name="${field}"]`);
      const select = this.page.locator(`select[name="${field}"]`);

      if ((await input.count()) > 0) {
        values[field] = await input.inputValue();
      } else if ((await textarea.count()) > 0) {
        values[field] = await textarea.inputValue();
      } else if ((await select.count()) > 0) {
        values[field] = await select.inputValue();
      }
    }

    return values;
  }

  /**
   * Screenshot Helpers
   */
  async takeScreenshot(name: string) {
    await this.page.screenshot({
      fullPage: true,
      path: `screenshots/${name}.png`,
    });
  }

  async takeElementScreenshot(selector: string, name: string) {
    const element = this.page.locator(selector);
    await element.screenshot({ path: `screenshots/${name}.png` });
  }

  /**
   * Network Helpers
   */
  async mockApiResponse(url: string, response: any, status = 200) {
    await this.page.route(`**${url}**`, (route) => {
      void route.fulfill({
        body: JSON.stringify(response),
        status,
      });
    });
  }

  async mockApiError(url: string, status = 500, message = 'Internal Server Error') {
    await this.page.route(`**${url}**`, (route) => {
      void route.fulfill({
        body: JSON.stringify({ error: message }),
        status,
      });
    });
  }

  /**
   * Storage Helpers
   */
  async getLocalStorage(key?: string): Promise<any> {
    return this.page.evaluate((k) => {
      if (k) {
        return localStorage.getItem(k);
      }
      return JSON.stringify(localStorage);
    }, key);
  }

  async setLocalStorage(key: string, value: string) {
    await this.page.evaluate(
      ({ k, v }) => {
        localStorage.setItem(k, v);
      },
      { k: key, v: value },
    );
  }

  async clearLocalStorage() {
    await this.page.evaluate(() => {
      localStorage.clear();
    });
  }

  /**
   * Keyboard Navigation Helpers
   */
  async tabThrough(count: number) {
    for (let i = 0; i < count; i++) {
      await this.page.keyboard.press('Tab');
      await this.page.waitForTimeout(100);
    }
  }

  async getFocusedElement() {
    return this.page.evaluate(() => {
      const el = document.activeElement;
      return {
        id: el?.id,
        tagName: el?.tagName,
        testId: el?.getAttribute('data-testid'),
        text: el?.textContent?.slice(0, 50),
      };
    });
  }

  /**
   * Performance Helpers
   */
  async measureLoadTime(): Promise<number> {
    return this.page.evaluate(() => {
      // Use PerformanceNavigationTiming instead of deprecated timing API
      const navEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return navEntry?.loadEventEnd || 0;
    });
  }

  async getPerformanceMetrics() {
    return this.page.evaluate(() => {
      const navEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paintEntries = performance.getEntriesByType('paint');

      return {
        domContentLoaded: navEntry?.domContentLoadedEventEnd || 0,
        firstContentfulPaint: paintEntries.find((e) => e.name === 'first-contentful-paint')
          ?.startTime,
        firstPaint: paintEntries.find((e) => e.name === 'first-paint')?.startTime,
        loadTime: navEntry?.loadEventEnd || 0,
      };
    });
  }

  /**
   * Utility Methods
   */
  async wait(ms: number) {
    await this.page.waitForTimeout(ms);
  }

  async scrollToBottom() {
    await this.page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
  }

  async scrollToTop() {
    await this.page.evaluate(() => {
      window.scrollTo(0, 0);
    });
  }

  async getPageTitle(): Promise<string> {
    return this.page.title();
  }

  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }

  async reload() {
    await this.page.reload();
    await this.page.waitForLoadState('networkidle');
  }
}

/**
 * Data Generators
 */
export function randomString(length = 10): string {
  return Math.random()
    .toString(36)
    .slice(2, length + 2);
}

export function randomEmail(): string {
  return `test-${randomString()}@example.com`;
}

export function randomItem() {
  return {
    description: `Description for test item ${randomString()}`,
    status: ['open', 'in-progress', 'done'][Math.floor(Math.random() * 3)],
    title: `Test Item ${randomString()}`,
    type: ['requirement', 'task', 'bug', 'feature'][Math.floor(Math.random() * 4)],
  };
}

export function randomProject() {
  return {
    description: `Description for test project ${randomString()}`,
    name: `Test Project ${randomString()}`,
  };
}

export function randomAgent() {
  return {
    name: `Test Agent ${randomString()}`,
    role: ['developer', 'designer', 'tester', 'manager'][Math.floor(Math.random() * 4)],
  };
}

/**
 * Log Collection Interfaces
 */
export interface BrowserLogs {
  console: { level: string; message: string; timestamp: number }[];
  errors: { message: string; stack?: string; timestamp: number }[];
  warnings: string[];
}

export interface NetworkLog {
  url: string;
  status: number;
  method: string;
  headers: Record<string, string>;
  timing: number;
}

/**
 * Log Collection Helpers
 */
export async function collectBrowserLogs(page: Page): Promise<BrowserLogs> {
  const logs: BrowserLogs = {
    console: [],
    errors: [],
    warnings: [],
  };

  page.on('console', (msg) => {
    logs.console.push({
      level: msg.type(),
      message: msg.text(),
      timestamp: Date.now(),
    });
  });

  page.on('pageerror', (error) => {
    logs.errors.push({
      message: error.message,
      stack: error.stack,
      timestamp: Date.now(),
    });
  });

  return logs;
}

export async function collectNetworkLogs(page: Page): Promise<NetworkLog[]> {
  const networkLogs: NetworkLog[] = [];

  page.on('response', (response) => {
    networkLogs.push({
      url: response.url(),
      status: response.status(),
      method: response.request().method(),
      headers: response.headers(),
      timing: response.request().timing()?.responseEnd || 0,
    });
  });

  return networkLogs;
}

/**
 * Custom Matchers
 */
export const customMatchers = {
  async toBeWithinViewport(locator: any) {
    const box = await locator.boundingBox();
    const viewport = await locator.page().viewportSize();

    if (!box || !viewport) {
      return { message: () => 'Element not found or no viewport', pass: false };
    }

    const isWithin =
      box.y >= 0 &&
      box.x >= 0 &&
      box.y + box.height <= viewport.height &&
      box.x + box.width <= viewport.width;

    return {
      message: () =>
        isWithin ? 'Element is within viewport' : 'Element is outside viewport boundaries',
      pass: isWithin,
    };
  },
};
