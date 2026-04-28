// tests/e2e/support/fixtures/agents.fixture.ts
// Fixture: Agents Setup
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page, expect } from '@playwright/test';
import { DataHelper } from '../helpers/data.helper';

export class AgentsFixture {
  private dataHelper: DataHelper;
  private agentNames: string[] = [];

  constructor(private page: Page) {
    this.dataHelper = new DataHelper(page);
  }

  async createAgent(name?: string, type: string = 'default'): Promise<string> {
    const agentName = name || `Agent ${this.dataHelper.generateRandomString(6)}`;
    await this.page.goto('http://localhost:3000/agents');
    await this.page.click('button:has-text("Create Agent")');
    await this.page.fill('input[name="agent-name"]', agentName);
    await this.page.selectOption('select[name="agent-type"]', type);
    await this.page.click('button:has-text("Save")');
    await expect(this.page.locator(`text=${agentName}`)).toBeVisible();
    
    this.agentNames.push(agentName);
    return agentName;
  }

  async deleteAgent(agentName: string): Promise<void> {
    await this.page.goto('http://localhost:3000/agents');
    await this.page.click(`[data-testid="agent-${agentName}"]`);
    await this.page.click('button:has-text("Delete")');
    await this.page.click('button:has-text("Confirm")');
    await expect(this.page.locator('text=Agent deleted')).toBeVisible();
  }

  async cleanup(): Promise<void> {
    for (const agentName of this.agentNames) {
      try {
        await this.deleteAgent(agentName);
      } catch (error) {
        // Ignore errors during cleanup
      }
    }
    this.agentNames = [];
  }

  async runAgent(agentName: string): Promise<void> {
    await this.page.goto('http://localhost:3000/agents');
    await this.page.click(`[data-testid="agent-${agentName}"]`);
    await this.page.click('button:has-text("Run")');
    await expect(this.page.locator('[data-testid="agent-status"]')).toContainText('running');
  }

  async stopAgent(agentName: string): Promise<void> {
    await this.page.goto('http://localhost:3000/agents');
    await this.page.click(`[data-testid="agent-${agentName}"]`);
    await this.page.click('button:has-text("Stop")');
    await expect(this.page.locator('[data-testid="agent-status"]')).toContainText('stopped');
  }

  async verifyAgentExists(agentName: string): Promise<void> {
    await expect(this.page.locator(`text=${agentName}`)).toBeVisible();
  }
}
