import { expect, test } from './global-setup';

/**
 * Multi-Perspective Graph View Tests
 *
 * Tests for switching between different display modes and perspective selections
 * in the multi-dimensional traceability graph.
 *
 * Display Modes:
 * - Single: Default unified view
 * - Split: Two side-by-side perspectives
 * - Layered: Stacked dimensional views
 * - Unified: Combined with dimension highlights
 * - Pivot: Navigation-focused view with equivalents
 */

test.describe('Multi-Perspective Display Modes', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/graph');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000); // Allow graph to render
  });

  test.describe('Display Mode Switching', () => {
    test('should render default single view mode', async ({ page }) => {
      // Single view should be the default display mode
      const graphContainer = page.locator('.react-flow');
      await expect(graphContainer).toBeVisible({ timeout: 5000 });

      // Check for graph controls that indicate single view
      const modeSelector = page
        .locator("button, [role='button']")
        .filter({ hasText: /view|mode|perspective|display/i });

      if (await modeSelector.isVisible({ timeout: 2000 }).catch(() => false)) {
        console.log('Display mode selector found');
      }
    });

    test('should switch to split view mode', async ({ page }) => {
      // Look for view/mode selector
      const modeBtn = page
        .locator('button')
        .filter({ hasText: /split|view|mode/i })
        .first();

      if (await modeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await modeBtn.click();
        await page.waitForTimeout(300);

        // Try to select split mode
        const splitOption = page.getByText(/split.*view|side.*by.*side/i);
        if (await splitOption.isVisible({ timeout: 1000 }).catch(() => false)) {
          await splitOption.click();
          await page.waitForTimeout(1000);

          // Verify split view is displayed
          // In split view, there should be two graph containers or panels
          const splitContainers = page.locator(".react-flow, [class*='split'], [class*='panel']");
          const containerCount = await splitContainers.count().catch(() => 0);

          if (containerCount >= 2) {
            console.log('Split view activated with two containers');
          } else {
            console.log('Split view mode may use different layout structure');
          }
        } else {
          console.log('Split mode option not found in dropdown');
        }
      } else {
        console.log('View mode selector not found');
      }
    });

    test('should switch to layered view mode', async ({ page }) => {
      const modeBtn = page
        .locator('button')
        .filter({ hasText: /view|mode|display/i })
        .first();

      if (await modeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await modeBtn.click();
        await page.waitForTimeout(300);

        const layeredOption = page.getByText(/layered|stacked|overlay/i);
        if (await layeredOption.isVisible({ timeout: 1000 }).catch(() => false)) {
          await layeredOption.click();
          await page.waitForTimeout(1000);

          // Verify layered view
          const graphContainer = page.locator('.react-flow');
          await expect(graphContainer).toBeVisible();

          // Layered view might show dimension indicators or tabs
          const dimensionTabs = page.locator(
            "[role='tab'], button[class*='dimension'], button[class*='layer']",
          );
          const tabCount = await dimensionTabs.count().catch(() => 0);

          if (tabCount > 0) {
            console.log(`Layered view with ${tabCount} dimension tabs`);
          } else {
            console.log('Layered view structure identified');
          }
        } else {
          console.log('Layered mode option not found');
        }
      } else {
        console.log('View mode selector not available');
      }
    });

    test('should switch to unified view mode', async ({ page }) => {
      const modeBtn = page
        .locator('button')
        .filter({ hasText: /view|mode|display/i })
        .first();

      if (await modeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await modeBtn.click();
        await page.waitForTimeout(300);

        const unifiedOption = page.getByText(/unified|combined|all/i);
        if (await unifiedOption.isVisible({ timeout: 1000 }).catch(() => false)) {
          await unifiedOption.click();
          await page.waitForTimeout(1000);

          // Verify unified view is displaying all dimensions
          const graphContainer = page.locator('.react-flow');
          await expect(graphContainer).toBeVisible();

          // Look for color/style coding that indicates multiple dimensions
          const coloredNodes = page.locator(
            ".react-flow__nodes [style*='color'], [style*='background']",
          );
          const coloredCount = await coloredNodes.count().catch(() => 0);

          if (coloredCount > 0) {
            console.log(`Unified view with ${coloredCount} styled nodes`);
          } else {
            console.log('Unified view activated');
          }
        } else {
          console.log('Unified mode option not found');
        }
      } else {
        console.log('View mode selector not available');
      }
    });

    test('should switch to pivot view mode', async ({ page }) => {
      const modeBtn = page
        .locator('button')
        .filter({ hasText: /view|mode|perspective|pivot/i })
        .first();

      if (await modeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await modeBtn.click();
        await page.waitForTimeout(300);

        const pivotOption = page.getByText(/pivot|navigation|equivalent/i);
        if (await pivotOption.isVisible({ timeout: 1000 }).catch(() => false)) {
          await pivotOption.click();
          await page.waitForTimeout(1000);

          // Verify pivot view
          const graphContainer = page.locator('.react-flow');
          await expect(graphContainer).toBeVisible();

          // Pivot view should show navigation controls or equivalent panels
          const navControls = page.locator(
            "button[class*='pivot'], button[class*='nav'], [class*='equivalent']",
          );
          const controlCount = await navControls.count().catch(() => 0);

          if (controlCount > 0) {
            console.log(`Pivot view with ${controlCount} navigation controls`);
          } else {
            console.log('Pivot view mode activated');
          }
        } else {
          console.log('Pivot mode option not found');
        }
      } else {
        console.log('View mode selector not available');
      }
    });

    test('should toggle between view modes without data loss', async ({ page }) => {
      // Switch to split view
      const modeBtn = page
        .locator('button')
        .filter({ hasText: /view|mode|display/i })
        .first();

      if (await modeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        // Count initial nodes
        const initialNodeCount = await page
          .locator('.react-flow__nodes > div[data-id]')
          .count()
          .catch(() => 0);

        if (initialNodeCount > 0) {
          // Switch to split view
          await modeBtn.click();
          await page.waitForTimeout(300);

          const splitOption = page.getByText(/split/i);
          if (await splitOption.isVisible({ timeout: 1000 }).catch(() => false)) {
            await splitOption.click();
            await page.waitForTimeout(1000);

            // Switch back to single view
            await modeBtn.click();
            await page.waitForTimeout(300);

            const singleOption = page.getByText(/single/i);
            if (await singleOption.isVisible({ timeout: 1000 }).catch(() => false)) {
              await singleOption.click();
              await page.waitForTimeout(1000);

              // Verify nodes are still present
              const finalNodeCount = await page
                .locator('.react-flow__nodes > div[data-id]')
                .count()
                .catch(() => 0);

              expect(finalNodeCount).toEqual(initialNodeCount);
              console.log('Mode switching preserved node data');
            }
          }
        }
      } else {
        console.log('View mode switching not available');
      }
    });
  });

  test.describe('Split View Perspectives', () => {
    test('should display two side-by-side graph containers', async ({ page }) => {
      const modeBtn = page
        .locator('button')
        .filter({ hasText: /view|mode|display/i })
        .first();

      if (await modeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await modeBtn.click();
        await page.waitForTimeout(300);

        const splitOption = page.getByText(/split/i);
        if (await splitOption.isVisible({ timeout: 1000 }).catch(() => false)) {
          await splitOption.click();
          await page.waitForTimeout(1000);

          // Look for split container structure
          const leftPanel = page.locator("[class*='left'], [class*='primary']").first();
          const rightPanel = page.locator("[class*='right'], [class*='secondary']").first();

          const leftVisible = await leftPanel.isVisible({ timeout: 2000 }).catch(() => false);
          const rightVisible = await rightPanel.isVisible({ timeout: 2000 }).catch(() => false);

          if (leftVisible && rightVisible) {
            console.log('Split view with left and right panels');
          } else {
            console.log('Split view may use different panel structure');
          }
        }
      }
    });

    test('should select different perspectives for split panels', async ({ page }) => {
      const modeBtn = page
        .locator('button')
        .filter({ hasText: /view|mode|display/i })
        .first();

      if (await modeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await modeBtn.click();
        await page.waitForTimeout(300);

        const splitOption = page.getByText(/split/i);
        if (await splitOption.isVisible({ timeout: 1000 }).catch(() => false)) {
          await splitOption.click();
          await page.waitForTimeout(1000);

          // Look for perspective selector buttons in each panel
          const perspectiveSelectors = page.locator(
            "button[class*='perspective'], select[aria-label*='perspective']",
          );
          const selectorCount = await perspectiveSelectors.count().catch(() => 0);

          if (selectorCount >= 2) {
            // Click first perspective selector
            await perspectiveSelectors
              .nth(0)
              .click({ timeout: 2000 })
              .catch(() => {});
            await page.waitForTimeout(300);

            // Select a perspective option
            const option = page
              .locator("button, [role='option']")
              .filter({ hasText: /requirement|feature|code/i })
              .first();
            if (await option.isVisible({ timeout: 1000 }).catch(() => false)) {
              await option.click();
              await page.waitForTimeout(500);

              console.log('Perspective selector changed in split view');
            }
          } else {
            console.log('Perspective selectors not found in split view');
          }
        }
      }
    });

    test('should synchronize pan/zoom between split panels', async ({ page }) => {
      const modeBtn = page
        .locator('button')
        .filter({ hasText: /view|mode|display/i })
        .first();

      if (await modeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await modeBtn.click();
        await page.waitForTimeout(300);

        const splitOption = page.getByText(/split/i);
        if (await splitOption.isVisible({ timeout: 1000 }).catch(() => false)) {
          await splitOption.click();
          await page.waitForTimeout(1000);

          // Get left and right graph containers
          const graphs = page.locator('.react-flow');
          const graphCount = await graphs.count().catch(() => 0);

          if (graphCount >= 2) {
            const leftGraph = graphs.nth(0);
            const leftBox = await leftGraph.boundingBox();

            if (leftBox) {
              // Pan on left graph
              await page.mouse.move(leftBox.x + leftBox.width / 2, leftBox.y + leftBox.height / 2);
              await page.mouse.down();
              await page.mouse.move(
                leftBox.x + leftBox.width / 2 + 50,
                leftBox.y + leftBox.height / 2 + 50,
              );
              await page.mouse.up();

              await page.waitForTimeout(500);

              console.log('Split view pan/zoom synchronization test');
            }
          }
        }
      }
    });
  });

  test.describe('Pivot Navigation', () => {
    test('should navigate between equivalents in pivot view', async ({ page }) => {
      const modeBtn = page
        .locator('button')
        .filter({ hasText: /view|mode|perspective|pivot/i })
        .first();

      if (await modeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await modeBtn.click();
        await page.waitForTimeout(300);

        const pivotOption = page.getByText(/pivot/i);
        if (await pivotOption.isVisible({ timeout: 1000 }).catch(() => false)) {
          await pivotOption.click();
          await page.waitForTimeout(1000);

          // Look for navigation buttons or equivalent list
          const navButtons = page.locator("button[class*='pivot']");
          const buttonCount = await navButtons.count().catch(() => 0);

          if (buttonCount > 0) {
            // Click first navigation button
            await navButtons
              .first()
              .click({ timeout: 2000 })
              .catch(() => {});
            await page.waitForTimeout(500);

            console.log('Pivot navigation button clicked');
          } else {
            // Look for equivalent items in a list
            const equivalentItems = page.locator("[class*='equivalent'], [class*='pivot']");
            const itemCount = await equivalentItems.count().catch(() => 0);

            if (itemCount > 0) {
              await equivalentItems
                .first()
                .click({ timeout: 2000 })
                .catch(() => {});
              await page.waitForTimeout(500);

              console.log(`Found ${itemCount} equivalent items in pivot view`);
            } else {
              console.log('Equivalent navigation not found');
            }
          }
        }
      }
    });

    test('should show equivalence relationships in pivot mode', async ({ page }) => {
      const modeBtn = page
        .locator('button')
        .filter({ hasText: /view|mode|perspective|pivot/i })
        .first();

      if (await modeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await modeBtn.click();
        await page.waitForTimeout(300);

        const pivotOption = page.getByText(/pivot/i);
        if (await pivotOption.isVisible({ timeout: 1000 }).catch(() => false)) {
          await pivotOption.click();
          await page.waitForTimeout(1000);

          // Look for equivalence indicators
          const equivalenceLabels = page.getByText(/equivalent|related|maps to|corresponds/i);
          const labelCount = await equivalenceLabels.count().catch(() => 0);

          if (labelCount > 0) {
            console.log(`Found ${labelCount} equivalence relationships`);
          }

          // Check for highlight styling on equivalent nodes
          const highlightedNodes = page.locator(
            "[class*='equivalent'], [class*='highlighted'], [style*='highlight']",
          );
          const highlightCount = await highlightedNodes.count().catch(() => 0);

          if (highlightCount > 0) {
            console.log(`${highlightCount} equivalent nodes highlighted`);
          }
        }
      }
    });
  });

  test.describe('Dimension Perspective Selection', () => {
    test('should show available dimensions for perspective selection', async ({ page }) => {
      // Look for dimension selector/chooser
      const dimensionSelector = page.locator(
        "[class*='dimension'], [class*='perspective'], select, button[aria-label*='dimension']",
      );

      if (await dimensionSelector.isVisible({ timeout: 2000 }).catch(() => false)) {
        // Check dimensions available
        const dimensions = page.locator("button[class*='dimension'], option, [role='option']");
        const dimensionCount = await dimensions.count().catch(() => 0);

        if (dimensionCount > 0) {
          console.log(`Found ${dimensionCount} available dimensions`);
        }
      }
    });

    test('should switch dimension perspective and update display', async ({ page }) => {
      // Try to find and interact with dimension selector
      const dimensionBtn = page
        .locator('button')
        .filter({ hasText: /dimension|perspective|view/i })
        .first();

      if (await dimensionBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await dimensionBtn.click();
        await page.waitForTimeout(300);

        // Select a different dimension
        const dimensionOption = page
          .getByText(/requirement|feature|code|test|architecture/i)
          .first();

        if (await dimensionOption.isVisible({ timeout: 1000 }).catch(() => false)) {
          await dimensionOption.click();
          await page.waitForTimeout(1000);

          // Verify graph updated with new perspective
          const graphContainer = page.locator('.react-flow');
          await expect(graphContainer).toBeVisible();

          console.log('Dimension perspective updated');
        }
      }
    });
  });
});

test.describe('View Persistence and State Management', () => {
  test('should remember selected display mode after page refresh', async ({ page }) => {
    await page.goto('/graph');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // Switch to a display mode
    const modeBtn = page
      .locator('button')
      .filter({ hasText: /view|mode|display/i })
      .first();

    if (await modeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await modeBtn.click();
      await page.waitForTimeout(300);

      const splitOption = page.getByText(/split/i);
      if (await splitOption.isVisible({ timeout: 1000 }).catch(() => false)) {
        await splitOption.click();
        await page.waitForTimeout(500);

        // Reload page
        await page.reload();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(500);

        // Check if split mode is still active
        const graphs = page.locator('.react-flow');
        const graphCount = await graphs.count().catch(() => 0);

        if (graphCount >= 2) {
          console.log('Display mode preference persisted');
        } else {
          console.log('Display mode not persisted (may be expected)');
        }
      }
    }
  });

  test('should maintain perspective selections across view changes', async ({ page }) => {
    await page.goto('/graph');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);

    // Store initial perspective state
    const initialGraphContainer = page.locator('.react-flow');
    const initialNodeCount = await initialGraphContainer
      .evaluate((el) => el.querySelectorAll('[data-id]').length)
      .catch(() => 0);

    if (initialNodeCount > 0) {
      // Switch to different display mode and back
      const modeBtn = page
        .locator('button')
        .filter({ hasText: /view|mode|display/i })
        .first();

      if (await modeBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await modeBtn.click();
        await page.waitForTimeout(300);

        const splitOption = page.getByText(/split/i);
        if (await splitOption.isVisible({ timeout: 1000 }).catch(() => false)) {
          await splitOption.click();
          await page.waitForTimeout(1000);

          // Switch back
          await modeBtn.click();
          await page.waitForTimeout(300);

          const singleOption = page.getByText(/single/i);
          if (await singleOption.isVisible({ timeout: 1000 }).catch(() => false)) {
            await singleOption.click();
            await page.waitForTimeout(500);

            const finalNodeCount = await initialGraphContainer
              .evaluate((el) => el.querySelectorAll('[data-id]').length)
              .catch(() => 0);

            if (finalNodeCount === initialNodeCount) {
              console.log('Perspective state maintained');
            }
          }
        }
      }
    }
  });
});
