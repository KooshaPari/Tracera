/**
 * End-to-End Test: Real-time Updates via WebSocket
 *
 * Verifies that NATS events propagate to frontend via WebSocket
 * and trigger UI updates.
 */

import { expect, test } from '@playwright/test';

test.describe('Real-time Updates', () => {
  test.beforeEach(async ({ page }) => {
    // Mock authentication
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123');
    });
  });

  test('receives real-time updates when item is created via API', async ({ page }) => {
    // Navigate to project page
    await page.goto('/projects/test-project');

    // Wait for page to load
    await expect(page.getByRole('heading', { name: /items/i })).toBeVisible();

    // Create item via API (bypassing UI to test WebSocket)
    const response = await page.request.post('http://localhost:8080/api/v1/items', {
      data: {
        project_id: 'test-project',
        title: 'Real-time Test Item',
        type: 'requirement',
      },
      headers: {
        'Content-Type': 'application/json',
      },
    });

    expect(response.ok()).toBeTruthy();

    // Wait for item to appear in UI (via WebSocket real-time update)
    await expect(page.getByText('Real-time Test Item')).toBeVisible({
      timeout: 5000,
    });
  });

  test('receives real-time updates when item is updated', async ({ page }) => {
    // Navigate to project page
    await page.goto('/projects/test-project');

    // Create item first
    const createResponse = await page.request.post('http://localhost:8080/api/v1/items', {
      data: {
        project_id: 'test-project',
        title: 'Original Title',
        type: 'requirement',
      },
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const item = (await createResponse.json()) as { id: string };
    const itemId = item.id;

    // Wait for item to appear
    await expect(page.getByText('Original Title')).toBeVisible({
      timeout: 5000,
    });

    // Update item via API
    await page.request.put(`http://localhost:8080/api/v1/items/${itemId}`, {
      data: {
        title: 'Updated Title via WebSocket',
      },
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Wait for updated title to appear (via WebSocket)
    await expect(page.getByText('Updated Title via WebSocket')).toBeVisible({
      timeout: 5000,
    });
    await expect(page.getByText('Original Title')).not.toBeVisible();
  });

  test('receives real-time updates when link is created', async ({ page }) => {
    // Navigate to project page
    await page.goto('/projects/test-project/links');

    // Create two items for linking
    const item1Response = await page.request.post('http://localhost:8080/api/v1/items', {
      data: {
        project_id: 'test-project',
        title: 'Source Item',
        type: 'requirement',
      },
      headers: { 'Content-Type': 'application/json' },
    });
    const item1 = (await item1Response.json()) as { id: string };

    const item2Response = await page.request.post('http://localhost:8080/api/v1/items', {
      data: {
        project_id: 'test-project',
        title: 'Target Item',
        type: 'feature',
      },
      headers: { 'Content-Type': 'application/json' },
    });
    const item2 = (await item2Response.json()) as { id: string };

    // Create link via API
    await page.request.post('http://localhost:8080/api/v1/links', {
      data: {
        link_type: 'implements',
        project_id: 'test-project',
        source_id: item1.id,
        target_id: item2.id,
      },
      headers: { 'Content-Type': 'application/json' },
    });

    // Verify link appears in UI (via WebSocket)
    await expect(page.getByText(/implements/i)).toBeVisible({ timeout: 5000 });
  });

  test('receives toast notifications for real-time events', async ({ page }) => {
    // Navigate to project page
    await page.goto('/projects/test-project');

    // Create item via API
    await page.request.post('http://localhost:8080/api/v1/items', {
      data: {
        project_id: 'test-project',
        title: 'Toast Test Item',
        type: 'requirement',
      },
      headers: { 'Content-Type': 'application/json' },
    });

    // Wait for toast notification
    await expect(page.getByRole('status')).toContainText('New item created', {
      timeout: 5000,
    });
  });

  test('handles connection loss and reconnection', async ({ page, context }) => {
    // Navigate to project page
    await page.goto('/projects/test-project');

    // Simulate network offline
    await context.setOffline(true);

    // Wait a moment
    await page.waitForTimeout(1000);

    // Restore network
    await context.setOffline(false);

    // Create item - should work after reconnection
    await page.request.post('http://localhost:8080/api/v1/items', {
      data: {
        project_id: 'test-project',
        title: 'Reconnection Test Item',
        type: 'requirement',
      },
      headers: { 'Content-Type': 'application/json' },
    });

    // Verify item appears after reconnection
    await expect(page.getByText('Reconnection Test Item')).toBeVisible({
      timeout: 10_000,
    });
  });

  test('only receives events for subscribed project', async ({ page }) => {
    // Navigate to project A
    await page.goto('/projects/project-a');

    // Create item in project B (should NOT appear)
    await page.request.post('http://localhost:8080/api/v1/items', {
      data: {
        project_id: 'project-b',
        title: 'Project B Item',
        type: 'requirement',
      },
      headers: { 'Content-Type': 'application/json' },
    });

    // Item should NOT appear
    await page.waitForTimeout(2000);
    await expect(page.getByText('Project B Item')).not.toBeVisible();

    // Create item in project A (should appear)
    await page.request.post('http://localhost:8080/api/v1/items', {
      data: {
        project_id: 'project-a',
        title: 'Project A Item',
        type: 'requirement',
      },
      headers: { 'Content-Type': 'application/json' },
    });

    // Item SHOULD appear
    await expect(page.getByText('Project A Item')).toBeVisible({
      timeout: 5000,
    });
  });

  test('receives AI analysis complete notification', async ({ page }) => {
    // Navigate to specifications page
    await page.goto('/projects/test-project/specifications');

    // Mock AI analysis event (would normally come from Python backend via NATS)
    await page.evaluate(() => {
      // Simulate receiving NATS event via WebSocket
      const event = new CustomEvent('nats_event', {
        detail: {
          data: {
            analysis: 'Complete',
            spec_id: 'spec-123',
          },
          entity_id: 'spec-123',
          event_type: 'ai.analysis.complete',
          project_id: 'test-project',
        },
      });
      globalThis.dispatchEvent(event);
    });

    // Wait for toast notification
    await expect(page.getByRole('status')).toContainText('AI analysis complete', { timeout: 5000 });
  });

  test('WebSocket connection indicator shows status', async ({ page }) => {
    await page.goto('/projects/test-project');

    // Check for connection indicator (if implemented in UI)
    // This would show as a green dot or "Connected" status
    const statusIndicator = page.getByTestId('websocket-status');
    await expect(statusIndicator).toBeVisible({ timeout: 10_000 });
    await expect(statusIndicator).toContainText(/connected/i);
  });
});
