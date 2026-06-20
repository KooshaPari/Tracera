// tests/e2e/support/fixtures/project.fixture.ts
// Fixture: Project Setup
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page, expect } from '@playwright/test';
import { DataHelper } from '../helpers/data.helper';

export class ProjectFixture {
  private dataHelper: DataHelper;
  private projectIds: string[] = [];

  constructor(private page: Page) {
    this.dataHelper = new DataHelper(page);
  }

  async createProject(name?: string): Promise<string> {
    const projectName = name || this.dataHelper.generateRandomProjectName();
    await this.page.goto('http://localhost:3000/projects');
    await this.page.click('button:has-text("New Project")');
    await this.page.fill('input[name="name"]', projectName);
    await this.page.click('button:has-text("Create")');
    await expect(this.page.locator(`text=${projectName}`)).toBeVisible();
    
    const projectId = await this.page.locator('[data-testid="project-id"]').textContent();
    if (projectId) {
      this.projectIds.push(projectId);
    }
    return projectId || '';
  }

  async deleteProject(projectId: string): Promise<void> {
    await this.page.goto(`http://localhost:3000/projects/${projectId}`);
    await this.page.click('button:has-text("Delete")');
    await this.page.click('button:has-text("Confirm")');
    await expect(this.page.locator('text=Project deleted')).toBeVisible();
  }

  async cleanup(): Promise<void> {
    for (const projectId of this.projectIds) {
      try {
        await this.deleteProject(projectId);
      } catch (error) {
        // Ignore errors during cleanup
      }
    }
    this.projectIds = [];
  }

  async getProjectId(): Promise<string | null> {
    return await this.page.locator('[data-testid="project-id"]').textContent();
  }

  async verifyProjectExists(projectName: string): Promise<void> {
    await expect(this.page.locator(`text=${projectName}`)).toBeVisible();
  }
}
