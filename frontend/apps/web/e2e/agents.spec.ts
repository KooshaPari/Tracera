import { expect, test } from './global-setup';

/**
 * E2E Tests for Agent Management
 * Tests agent listing, status monitoring, task execution, and configuration
 */
test.describe('Agents Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Agents List View', () => {
    test('should navigate to agents page', async ({ page }) => {
      // Navigate directly to agents page (no sidebar link exists)
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Verify URL
      await expect(page).toHaveURL(/\/agents/);

      // Verify page heading
      const heading = page.getByRole('heading', { name: /agents/i });
      await expect(heading).toBeVisible({ timeout: 5000 });
    });

    test('should display list of agents', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Look for agent cards - they are displayed as Cards in a grid
      // Check for agent names from mock data
      const syncAgent = page.getByText(/Sync Agent/);
      await expect(syncAgent).toBeVisible({ timeout: 5000 });

    // Verify at least one agent card is visible - using mock data names
    const agents = [/Sync Agent/, /Validation Agent/, /Coverage Agent/];
    for (const agent of agents) {
      await expect(page.getByText(agent).first()).toBeVisible({ timeout: 5000 });
    }
  });

    test('should show agent details', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Check for agent names from mock data
      const syncAgent = page.getByText(/Sync Agent/);
      await expect(syncAgent).toBeVisible({ timeout: 5000 });

      const validationAgent = page.getByText(/Validation Agent/);
      await expect(validationAgent).toBeVisible({ timeout: 5000 });

      const coverageAgent = page.getByText(/Coverage Agent/);
      await expect(coverageAgent).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Agent Status', () => {
    test('should display agent status badges', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Look for status badges - agents have status: active, idle, running
      const activeStatus = page.getByText(/active/i).first();
      await expect(activeStatus).toBeVisible({ timeout: 5000 });

      const idleStatus = page.getByText(/idle/i).first();
      await expect(idleStatus).toBeVisible({ timeout: 5000 });

      const runningStatus = page.getByText(/running/i).first();
      await expect(runningStatus).toBeVisible({ timeout: 5000 });
    });

    test('should show agent task information', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Check for task counts - agents display "X tasks completed"
      const tasksText = page.getByText(/tasks completed/i);
      await expect(tasksText.first()).toBeVisible({ timeout: 5000 });

      // Look for specific task counts
      const syncAgentTasks = page.getByText(/24 tasks completed/i);
      await expect(syncAgentTasks).toBeVisible({ timeout: 5000 });
    });

    test('should show last run information', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Look for last run information displayed on agent cards
      const lastRunText = page.getByText(/Last run:/i);
      await expect(lastRunText.first()).toBeVisible({ timeout: 5000 });
    });

    test('should show agent buttons', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Look for action buttons on agent cards (View Logs, Configure, etc.)
      const viewLogsBtn = page.getByRole('button', { name: /View Logs/i });
      await expect(viewLogsBtn.first()).toBeVisible({ timeout: 5000 });

      const configureBtn = page.getByRole('button', { name: /Configure/i });
      await expect(configureBtn.first()).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Agent Actions', () => {
    test('should show agent buttons', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Find an agent with idle status
      const idleAgent = page.getByText(/Validation Agent/).first();
      await expect(idleAgent).toBeVisible({ timeout: 2000 });

      // Agent is displayed, check for action buttons near it
      const buttons = page.getByRole('button', {
        name: /View Logs|Configure/i,
      });

      await expect(buttons.first()).toBeVisible({ timeout: 5000 });
    });

    test('should display running agent', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Find a running agent
      const runningAgent = page.getByText(/Coverage Agent/).first();
      await expect(runningAgent).toBeVisible({ timeout: 2000 });

      // Verify the agent is shown with running status
      const runningStatus = runningAgent.locator('..').getByText(/running/i);
      await expect(runningStatus).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Agent Display', () => {
    // Verify agents are displayed in grid layout
    const agents = [/Sync Agent/, /Validation Agent/, /Coverage Agent/];

    for (const agent of agents) {
      await expect(page.getByText(agent).first()).toBeVisible({ timeout: 5000 });
    }
  });

    test('should show agent task counts', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Verify task count information is displayed
      const taskInfo = page.getByText(/tasks completed/i);
      await expect(taskInfo.first()).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Agent Buttons', () => {
    test('should show View Logs button', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Look for View Logs button on agent cards
      const viewLogsBtn = page.getByRole('button', { name: /View Logs/i });
      await expect(viewLogsBtn.first()).toBeVisible({ timeout: 5000 });
    });

    test('should show Configure button', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Look for Configure button on agent cards
      const configureBtn = page.getByRole('button', { name: /Configure/i });
      await expect(configureBtn.first()).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Agent Status Information', () => {
    test('should display agent status', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Status should be displayed on agent cards
      const statusTexts = [/active/i, /idle/i, /running/i];

    // At least one status should be visible
    await expect(
      page
        .getByText(/active/i)
        .or(page.getByText(/idle/i))
        .or(page.getByText(/running/i))
        .first(),
    ).toBeVisible({ timeout: 5000 });
  });

    test('should display last run time', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Look for last run information
      const lastRunText = page.getByText(/Last run:/i);
      await expect(lastRunText.first()).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Agent Navigation', () => {
    test('should navigate to agents page', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Verify we're on the agents page
      await expect(page).toHaveURL(/\/agents/);

      // Verify agents content is shown
      const agentsHeading = page.getByRole('heading', { name: /agents/i });
      await expect(agentsHeading).toBeVisible({ timeout: 5000 });
    });

    test('should display all three agents', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Verify all three mock agents are displayed
      const syncAgent = page.getByText(/Sync Agent/);
      await expect(syncAgent).toBeVisible({ timeout: 5000 });

      const validationAgent = page.getByText(/Validation Agent/);
      await expect(validationAgent).toBeVisible({ timeout: 5000 });

      const coverageAgent = page.getByText(/Coverage Agent/);
      await expect(coverageAgent).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Agent List Verification', () => {
    test('should display agents with all required information', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Verify Sync Agent is displayed with all info
      const syncAgent = page.getByText(/Sync Agent/);
      await expect(syncAgent).toBeVisible({ timeout: 5000 });

      // Check that it shows tasks completed
      const syncTasks = page.getByText(/24 tasks completed/);
      await expect(syncTasks).toBeVisible({ timeout: 5000 });
    });

    test('should show agent action buttons', async ({ page }) => {
      await page.goto('/agents');
      await page.waitForLoadState('networkidle');

      // Verify action buttons are present
      const viewLogsButtons = page.getByRole('button', { name: /View Logs/i });
      const count = await viewLogsButtons.count();
      expect(count).toBeGreaterThan(0);
    });
  });
});
