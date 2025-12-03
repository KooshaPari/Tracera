// tests/e2e/support/page-objects/graph.page.ts
// Page Object: Graph View
// Governance: AGENTS.md (≤350 lines, test-first, type-safe)
import { Page, Locator, expect } from '@playwright/test';

export class GraphPage {
  readonly page: Page;
  readonly graphCanvas: Locator;
  readonly graphNode: Locator;
  readonly graphEdge: Locator;
  readonly zoomInButton: Locator;
  readonly zoomOutButton: Locator;
  readonly resetViewButton: Locator;
  readonly nodeDetails: Locator;
  readonly searchInput: Locator;
  readonly filterInput: Locator;

  constructor(page: Page) {
    this.page = page;
    this.graphCanvas = page.locator('[data-testid="graph-canvas"]');
    this.graphNode = page.locator('[data-testid="graph-node"]');
    this.graphEdge = page.locator('[data-testid="graph-edge"]');
    this.zoomInButton = page.locator('button:has-text("Zoom In")');
    this.zoomOutButton = page.locator('button:has-text("Zoom Out")');
    this.resetViewButton = page.locator('button:has-text("Reset View")');
    this.nodeDetails = page.locator('[data-testid="node-details"]');
    this.searchInput = page.locator('input[name="search"]');
    this.filterInput = page.locator('input[name="filter"]');
  }

  async navigate(): Promise<void> {
    await this.page.goto('http://localhost:3000/graph');
    await this.page.waitForLoadState('networkidle');
    await expect(this.graphCanvas).toBeVisible();
  }

  async clickNode(index: number = 0): Promise<void> {
    await this.graphNode.nth(index).click();
    await expect(this.nodeDetails).toBeVisible();
  }

  async verifyNodeSelected(): Promise<void> {
    await expect(this.page.locator('[data-testid="node-selected"]')).toBeVisible();
  }

  async zoomIn(): Promise<void> {
    await this.zoomInButton.click();
  }

  async zoomOut(): Promise<void> {
    await this.zoomOutButton.click();
  }

  async resetView(): Promise<void> {
    await this.resetViewButton.click();
  }

  async searchNode(query: string): Promise<void> {
    await this.searchInput.fill(query);
    await this.page.press('input[name="search"]', 'Enter');
    await this.page.waitForSelector('[data-testid="search-results"]');
  }

  async filterNodes(filter: string): Promise<void> {
    await this.filterInput.fill(filter);
    await this.page.press('input[name="filter"]', 'Enter');
    await this.page.waitForSelector('[data-testid="filtered-nodes"]');
  }

  async verifyNodeCount(expectedCount: number): Promise<void> {
    const nodes = await this.graphNode.count();
    expect(nodes).toBeGreaterThanOrEqual(expectedCount);
  }

  async dragNode(nodeIndex: number, x: number, y: number): Promise<void> {
    const node = this.graphNode.nth(nodeIndex);
    await node.dragTo(this.graphCanvas, { targetPosition: { x, y } });
  }
}
