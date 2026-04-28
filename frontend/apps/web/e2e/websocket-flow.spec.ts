import { expect, test } from '@playwright/test';

import { authenticateAndNavigate } from './critical-path-helpers';

test.describe('WebSocket Real-time Flow', () => {
  const projectId = 'test-project-ws';
  const itemName = `WS-Item-${Date.now()}`;

  test('should receive real-time item creation event', async ({ page }) => {
    // 1. Authenticate and navigate to project detail
    // This will trigger useRealtimeUpdates(projectId)
    await authenticateAndNavigate(page, `/projects/${projectId}`);

    // Verify we are on the project page
    await expect(page.getByText(`Project: ${projectId}`)).toBeVisible();

    // 2. Setup WebSocket message listener in browser context to verify event reception
    const eventReceivedPromise = page.evaluate(
      async () =>
        new Promise((resolve) => {
          // Access the global realtimeClient (assuming it's attached to window or accessible)
          // Since it's a module, we might need to use a hook or capture logs
          // Alternatively, we can just look for the UI change
          console.log('Waiting for item.created event...');
        }),
    );

    // 3. Trigger item creation via API (simulating another user/process)
    // We use page.evaluate to make a fetch request with the same auth token
    await page.evaluate(
      async ({ projectId, itemName }) => {
        const authData = JSON.parse(localStorage.getItem('tracertm-auth-store') ?? '{}');
        const token = authData.state?.token;

        const response = await fetch('http://localhost:4000/api/v1/items', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            title: itemName,
            project_id: projectId,
            type: 'requirement',
            status: 'pending',
          }),
        });

        if (!response.ok) {
          throw new Error(`API call failed: ${response.statusText}`);
        }
      },
      { projectId, itemName },
    );

    // 4. Verify UI updates automatically
    // We'll look for the new item title in the page
    // The useRealtimeUpdates hook should have invalidated the query, triggering a refetch
    await expect(page.getByText(itemName)).toBeVisible({ timeout: 10_000 });

    console.log('✅ Real-time UI update verified via WebSocket flow');
  });

  test('should receive real-time project update event', async ({ page }) => {
    await authenticateAndNavigate(page, `/projects/${projectId}`);

    const newDescription = `Updated via WS at ${new Date().toISOString()}`;

    // Trigger project update via API
    await page.evaluate(
      async ({ projectId, newDescription }) => {
        const authData = JSON.parse(localStorage.getItem('tracertm-auth-store') ?? '{}');
        const token = authData.state?.token;

        await fetch(`http://localhost:4000/api/v1/projects/${projectId}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            description: newDescription,
          }),
        });
      },
      { projectId, newDescription },
    );

    // Verify UI updates automatically
    await expect(page.getByText(newDescription)).toBeVisible({ timeout: 10_000 });

    console.log('✅ Real-time project update verified via WebSocket flow');
  });
});
