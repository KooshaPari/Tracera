// tests/e2e/support/helpers/navigation.helper.ts
// Helper: Navigation
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page, expect } from '@playwright/test';

export class NavigationHelper {
  constructor(private page: Page) {}

  async gotoDashboard(): Promise<void> {
    await this.page.goto('http://localhost:3000/dashboard');
    await this.page.waitForLoadState('networkidle');
    await expect(this.page).toHaveURL(/.*dashboard/);
  }

  async gotoItems(): Promise<void> {
    await this.page.goto('http://localhost:3000/items');
    await this.page.waitForLoadState('networkidle');
    await expect(this.page).toHaveURL(/.*items/);
  }

  async gotoGraph(): Promise<void> {
    await this.page.goto('http://localhost:3000/graph');
    await this.page.waitForLoadState('networkidle');
    await expect(this.page).toHaveURL(/.*graph/);
  }

  async gotoAgents(): Promise<void> {
    await this.page.goto('http://localhost:3000/agents');
    await this.page.waitForLoadState('networkidle');
    await expect(this.page).toHaveURL(/.*agents/);
  }

  async gotoSettings(): Promise<void> {
    await this.page.goto('http://localhost:3000/settings');
    await this.page.waitForLoadState('networkidle');
    await expect(this.page).toHaveURL(/.*settings/);
  }

  async gotoProjects(): Promise<void> {
    await this.page.goto('http://localhost:3000/projects');
    await this.page.waitForLoadState('networkidle');
    await expect(this.page).toHaveURL(/.*projects/);
  }

  async gotoItem(itemId: string): Promise<void> {
    await this.page.goto(`http://localhost:3000/items/${itemId}`);
    await this.page.waitForLoadState('networkidle');
    await expect(this.page).toHaveURL(new RegExp(`.*items/${itemId}`));
  }

  async gotoProject(projectId: string): Promise<void> {
    await this.page.goto(`http://localhost:3000/projects/${projectId}`);
    await this.page.waitForLoadState('networkidle');
    await expect(this.page).toHaveURL(new RegExp(`.*projects/${projectId}`));
  }

  async clickNavLink(linkText: string): Promise<void> {
    await this.page.click(`nav a:has-text("${linkText}")`);
    await this.page.waitForLoadState('networkidle');
  }

  async verifyCurrentUrl(pattern: string | RegExp): Promise<void> {
    await expect(this.page).toHaveURL(pattern);
  }

  async goBack(): Promise<void> {
    await this.page.goBack();
    await this.page.waitForLoadState('networkidle');
  }

  async reload(): Promise<void> {
    await this.page.reload();
    await this.page.waitForLoadState('networkidle');
  }
}
