/**
 * Accessibility Testing Helpers
 *
 * Wrapper functions for axe-core accessibility testing
 */
import type { Page } from '@playwright/test';
import type { AxeResults, Result } from 'axe-core';

import AxeBuilder from '@axe-core/playwright';

/**
 * Run a comprehensive accessibility scan on the page
 */
export async function runAccessibilityScan(
  page: Page,
  options?: {
    wcagLevel?: 'A' | 'AA' | 'AAA';
    tags?: string[];
    rules?: string[];
    excludeRules?: string[];
    include?: string[];
    exclude?: string[];
  },
): Promise<AxeResults> {
  let builder = new AxeBuilder({ page });

  // Set WCAG level
  if (options?.wcagLevel) {
    const tags = [
      'wcag2a',
      'wcag21a',
      ...(options.wcagLevel === 'AA' || options.wcagLevel === 'AAA' ? ['wcag2aa', 'wcag21aa'] : []),
      ...(options.wcagLevel === 'AAA' ? ['wcag2aaa', 'wcag21aaa'] : []),
    ];
    builder = builder.withTags(tags);
  }

  // Add custom tags
  if (options?.tags) {
    builder = builder.withTags(options.tags);
  }

  // Add custom rules
  if (options?.rules) {
    builder = builder.withRules(options.rules);
  }

  // Disable rules
  if (options?.excludeRules) {
    builder = builder.disableRules(options.excludeRules);
  }

  // Include/exclude selectors
  if (options?.include) {
    for (const selector of options.include) {
      builder = builder.include(selector);
    }
  }

  if (options?.exclude) {
    for (const selector of options.exclude) {
      builder = builder.exclude(selector);
    }
  }

  return builder.analyze();
}

/**
 * Check if page has any critical accessibility violations
 */
export function hasCriticalViolations(results: AxeResults): boolean {
  return results.violations.some((v) => v.impact === 'critical');
}

/**
 * Get violation summary grouped by impact
 */
export function getViolationSummary(results: AxeResults) {
  const summary = {
    critical: 0,
    minor: 0,
    moderate: 0,
    serious: 0,
    total: 0,
  };

  for (const violation of results.violations) {
    summary.total++;
    if (violation.impact === 'critical') {
      summary.critical++;
    } else if (violation.impact === 'serious') {
      summary.serious++;
    } else if (violation.impact === 'moderate') {
      summary.moderate++;
    } else if (violation.impact === 'minor') {
      summary.minor++;
    }
  }

  return summary;
}

/**
 * Format violations into readable report
 */
export function formatViolationReport(results: AxeResults): string {
  if (results.violations.length === 0) {
    return '✅ No accessibility violations found!';
  }

  const lines: string[] = ['❌ Accessibility Violations Found:\n'];

  for (const violation of results.violations) {
    lines.push(`\n[${violation.impact?.toUpperCase()}] ${violation.help}`);
    lines.push(`  Rule: ${violation.id}`);
    lines.push(`  WCAG: ${violation.tags.filter((t) => t.startsWith('wcag')).join(', ')}`);
    lines.push(`  Affected elements: ${violation.nodes.length}`);

    for (const node of violation.nodes.slice(0, 3)) {
      // Show first 3
      lines.push(`    - ${node.html}`);
      if (node.failureSummary) {
        lines.push(`      ${node.failureSummary}`);
      }
    }

    if (violation.nodes.length > 3) {
      lines.push(`    ... and ${violation.nodes.length - 3} more`);
    }
  }

  return lines.join('\n');
}

/**
 * Test keyboard navigation on page
 */
export async function testKeyboardNavigation(page: Page): Promise<{
  canTabThrough: boolean;
  focusableElements: number;
  focusTrapped: boolean;
}> {
  // Get all focusable elements
  const focusableElements = await page.evaluate(() => {
    const selectors = [
      'a[href]:not([disabled])',
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
    ];

    const elements = document.querySelectorAll(selectors.join(','));
    return elements.length;
  });

  // Try to tab through elements
  let canTabThrough = false;
  try {
    await page.keyboard.press('Tab');
    const activeElement = await page.evaluate(() => document.activeElement?.tagName);
    canTabThrough = activeElement !== 'BODY';
  } catch {
    canTabThrough = false;
  }

  // Check if focus is trapped (simplified check)
  const focusTrapped = await page.evaluate(() => {
    const modal = document.querySelector('[role="dialog"]');
    if (!modal) {
      return false;
    }

    // Check if focus is restricted to modal
    const { activeElement } = document;
    return modal.contains(activeElement);
  });

  return {
    canTabThrough,
    focusTrapped,
    focusableElements,
  };
}

/**
 * Check for proper ARIA landmarks
 */
export async function checkLandmarks(page: Page) {
  return page.evaluate(() => {
    const landmarks = {
      complementary: document.querySelectorAll('[role="complementary"]').length,
      footer: document.querySelectorAll('footer, [role="contentinfo"]').length,
      header: document.querySelectorAll('header, [role="banner"]').length,
      main: document.querySelectorAll('main, [role="main"]').length,
      navigation: document.querySelectorAll('nav, [role="navigation"]').length,
      search: document.querySelectorAll('[role="search"]').length,
    };

    return {
      landmarks,
      hasMain: landmarks.main > 0,
      hasMultipleMain: landmarks.main > 1, // Should be only 1
      hasNavigation: landmarks.navigation > 0,
    };
  });
}

/**
 * Check color contrast ratios
 */
export async function checkColorContrast(page: Page): Promise<AxeResults> {
  return new AxeBuilder({ page }).withRules(['color-contrast']).analyze();
}

/**
 * Check form accessibility
 */
export async function checkFormAccessibility(
  page: Page,
  formSelector = 'form',
): Promise<AxeResults> {
  return new AxeBuilder({ page })
    .include(formSelector)
    .withRules(['label', 'label-content-name-mismatch', 'input-button-name'])
    .analyze();
}

/**
 * Check for screen reader announcements (aria-live regions)
 */
export async function checkLiveRegions(page: Page) {
  return page.evaluate(() => {
    const liveRegions = document.querySelectorAll('[aria-live]');
    return {
      count: liveRegions.length,
      regions: [...liveRegions].map((region) => ({
        atomic: region.getAttribute('aria-atomic'),
        politeness: region.getAttribute('aria-live'),
        relevant: region.getAttribute('aria-relevant'),
      })),
    };
  });
}
