// tests/e2e/support/page-objects/agents.page.ts
// Page Object: Agents
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page, Locator, expect } from '@playwright/test';

export class AgentsPage {
  readonly page: Page;
  readonly agentList: Locator;
  readonly createAgentButton: Locator;
  readonly agentNameInput: Locator;
  readonly agentTypeSelect: Locator;
  readonly saveButton: Locator;
  readonly runButton: Locator;
  readonly stopButton: Locator;
  readonly agentStatus: Locator;
  readonly agentLogs: Locator;

  constructor(page: Page) {
    this.page = page;
    this.agentList = page.locator('[data-testid="agent-list"]');
    this.createAgentButton = page.locator('button:has-text("Create Agent")');
    this.agentNameInput = page.locator('input[name="agent-name"]');
    this.agentTypeSelect = page.locator('select[name="agent-type"]');
    this.saveButton = page.locator('button:has-text("Save")');
    this.runButton = page.locator('button:has-text("Run")');
    this.stopButton = page.locator('button:has-text("Stop")');
    this.agentStatus = page.locator('[data-testid="agent-status"]');
    this.agentLogs = page.locator('[data-testid="agent-logs"]');
  }

  async navigate(): Promise<void> {
    await this.page.goto('http://localhost:3000/agents');
    await this.page.waitForLoadState('networkidle');
  }

  async createAgent(name: string, type: string): Promise<void> {
    await this.createAgentButton.click();
    await this.agentNameInput.fill(name);
    await this.agentTypeSelect.selectOption(type);
    await this.saveButton.click();
    await expect(this.page.locator(`text=${name}`)).toBeVisible();
  }

  async runAgent(agentName: string): Promise<void> {
    await this.page.click(`[data-testid="agent-${agentName}"]`);
    await this.runButton.click();
    await expect(this.agentStatus).toContainText('running');
  }

  async stopAgent(agentName: string): Promise<void> {
    await this.page.click(`[data-testid="agent-${agentName}"]`);
    await this.stopButton.click();
    await expect(this.agentStatus).toContainText('stopped');
  }

  async verifyAgentStatus(agentName: string, status: string): Promise<void> {
    await this.page.click(`[data-testid="agent-${agentName}"]`);
    await expect(this.agentStatus).toContainText(status);
  }

  async viewAgentLogs(agentName: string): Promise<void> {
    await this.page.click(`[data-testid="agent-${agentName}"]`);
    await this.page.click('button:has-text("View Logs")');
    await expect(this.agentLogs).toBeVisible();
  }

  async verifyAgentExists(agentName: string): Promise<void> {
    await expect(this.page.locator(`text=${agentName}`)).toBeVisible();
  }
}
