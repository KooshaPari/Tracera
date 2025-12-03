// tests/e2e/support/page-objects/dashboard.page.ts
// Page Object: Dashboard
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page, Locator, expect } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;
  readonly projectCompletionMetric: Locator;
  readonly teamUtilizationMetric: Locator;
  readonly recentItemsList: Locator;
  readonly projectList: Locator;
  readonly createProjectButton: Locator;
  readonly filterInput: Locator;
  readonly searchInput: Locator;

  constructor(page: Page) {
    this.page = page;
    this.projectCompletionMetric = page.locator('[data-testid="project-completion-metric"]');
    this.teamUtilizationMetric = page.locator('[data-testid="team-utilization-metric"]');
    this.recentItemsList = page.locator('[data-testid="recent-items-list"]');
    this.projectList = page.locator('[data-testid="project-list"]');
    this.createProjectButton = page.locator('button:has-text("New Project")');
    this.filterInput = page.locator('input[name="filter"]');
    this.searchInput = page.locator('input[name="search"]');
  }

  async navigate(): Promise<void> {
    await this.page.goto('http://localhost:3000/dashboard');
    await this.page.waitForLoadState('networkidle');
  }

  async verifyMetricsVisible(): Promise<void> {
    await expect(this.projectCompletionMetric).toBeVisible();
    await expect(this.teamUtilizationMetric).toBeVisible();
  }

  async verifyRecentItemsVisible(): Promise<void> {
    await expect(this.recentItemsList).toBeVisible();
  }

  async createProject(name: string): Promise<void> {
    await this.createProjectButton.click();
    await this.page.fill('input[name="name"]', name);
    await this.page.click('button:has-text("Create")');
    await expect(this.page.locator(`text=${name}`)).toBeVisible();
  }

  async filterProjects(filter: string): Promise<void> {
    await this.filterInput.fill(filter);
    await this.page.press('input[name="filter"]', 'Enter');
    await this.page.waitForSelector('[data-testid="filtered-results"]');
  }

  async searchProjects(query: string): Promise<void> {
    await this.searchInput.fill(query);
    await this.page.press('input[name="search"]', 'Enter');
    await this.page.waitForSelector('[data-testid="search-results"]');
  }

  async clickProject(projectName: string): Promise<void> {
    await this.page.click(`text=${projectName}`);
    await this.page.waitForURL('**/projects/**');
  }

  async verifyProjectExists(projectName: string): Promise<void> {
    await expect(this.page.locator(`text=${projectName}`)).toBeVisible();
  }
}
