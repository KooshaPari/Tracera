import { expect, test } from '@playwright/test';

import {
  assertWebVitals,
  getCoreWebVitals,
  getLoadMetrics,
  runLighthouseAudit,
} from './helpers/lighthouse';

// Perf budgets: these should catch pathological CPU/memory regressions without being brittle.
const MAX_TOTAL_LOAD_MS = 8000;
const MAX_TASK_DURATION_MS = 1500;
const MAX_SCRIPT_DURATION_MS = 1000;
const MAX_HEAP_DELTA_BYTES = 100 * 1024 * 1024; // 100MB

test.describe('Performance - Dashboard (/home)', () => {
  test('should load dashboard within budgets (timing + vitals)', async ({ page }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    const load = await getLoadMetrics(page);
    if (load) {
      expect(load.totalTime).toBeLessThan(MAX_TOTAL_LOAD_MS);
    }

    const vitals = await getCoreWebVitals(page);
    const { failures } = assertWebVitals(vitals);
    expect(failures, failures.join('; ')).toHaveLength(0);

    // Lighthouse is the strictest high-level signal. Keep thresholds centralized and override per-test if needed.
    await runLighthouseAudit(page, 'dashboard-home');
  });

  test('should not spike CPU or heap during initial render', async ({ page, browserName }) => {
    await page.goto('/home');
    await page.waitForLoadState('networkidle');

    const beforeMetrics = await page.metrics();
    const beforeHeap = await page.evaluate(
      () => (performance as any).memory?.usedJSHeapSize ?? null,
    );

    // Let the UI settle across a couple frames.
    await page.evaluate(
      async () =>
        new Promise<void>((resolve) => {
          requestAnimationFrame(() =>
            requestAnimationFrame(() => {
              resolve();
            }),
          );
        }),
    );

    const afterMetrics = await page.metrics();
    const afterHeap = await page.evaluate(
      () => (performance as any).memory?.usedJSHeapSize ?? null,
    );

    expect(afterMetrics.TaskDuration - beforeMetrics.TaskDuration).toBeLessThan(
      MAX_TASK_DURATION_MS,
    );
    expect(afterMetrics.ScriptDuration - beforeMetrics.ScriptDuration).toBeLessThan(
      MAX_SCRIPT_DURATION_MS,
    );

    // `performance.memory` is Chromium-only. Treat missing memory API as unsupported on this browser.
    if (browserName === 'chromium' && beforeHeap != null && afterHeap != null) {
      expect(afterHeap - beforeHeap).toBeLessThan(MAX_HEAP_DELTA_BYTES);
    }
  });
});
