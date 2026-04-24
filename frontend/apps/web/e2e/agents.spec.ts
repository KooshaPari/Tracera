import type { Page } from '@playwright/test';

import { expect, test } from './global-setup';

const shortTimeoutMs = 2000;
const defaultTimeoutMs = 5000;

const knownAgentNameMatchers = [/Sync Agent/, /Validation Agent/, /Coverage Agent/];

async function gotoAgentsPage(page: Page): Promise<void> {
  await page.goto('/agents');
  await page.waitForLoadState('networkidle');
}

/**
 * E2E Tests for Agent Management
 * Tests agent listing, status monitoring, and basic actions.
 */
test.describe('Agents Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test.describe('Agents List View', () => {
    test('should navigate to agents page', async ({ page }) => {
      await gotoAgentsPage(page);
      await expect(page).toHaveURL(/\/agents/);

      const heading = page.getByRole('heading', { name: /agents/i });
      await expect(heading).toBeVisible({ timeout: defaultTimeoutMs });
    });

    test('should display list of known agents', async ({ page }) => {
      await gotoAgentsPage(page);

      for (const agentNameMatcher of knownAgentNameMatchers) {
        await expect(page.getByText(agentNameMatcher).first()).toBeVisible({
          timeout: defaultTimeoutMs,
        });
      }
    });
  });

  test.describe('Agent Status', () => {
    test('should display agent status badges', async ({ page }) => {
      await gotoAgentsPage(page);

      await expect(page.getByText(/active/i).first()).toBeVisible({ timeout: defaultTimeoutMs });
      await expect(page.getByText(/idle/i).first()).toBeVisible({ timeout: defaultTimeoutMs });
      await expect(page.getByText(/running/i).first()).toBeVisible({ timeout: defaultTimeoutMs });
    });

    test('should show last run information', async ({ page }) => {
      await gotoAgentsPage(page);

      const lastRunText = page.getByText(/Last run:/i);
      await expect(lastRunText.first()).toBeVisible({ timeout: defaultTimeoutMs });
    });

    test('should show task count information', async ({ page }) => {
      await gotoAgentsPage(page);

      const tasksText = page.getByText(/tasks completed/i);
      await expect(tasksText.first()).toBeVisible({ timeout: defaultTimeoutMs });
    });
  });

  test.describe('Agent Actions', () => {
    test('should show View Logs and Configure buttons', async ({ page }) => {
      await gotoAgentsPage(page);

      const viewLogsButton = page.getByRole('button', { name: /View Logs/i });
      await expect(viewLogsButton.first()).toBeVisible({ timeout: defaultTimeoutMs });

      const configureButton = page.getByRole('button', { name: /Configure/i });
      await expect(configureButton.first()).toBeVisible({ timeout: defaultTimeoutMs });
    });

    test('should display a running agent', async ({ page }) => {
      await gotoAgentsPage(page);

      const runningAgent = page.getByText(/Coverage Agent/).first();
      await expect(runningAgent).toBeVisible({ timeout: shortTimeoutMs });

      const runningStatus = runningAgent.locator('..').getByText(/running/i);
      await expect(runningStatus).toBeVisible({ timeout: defaultTimeoutMs });
    });
  });
});
