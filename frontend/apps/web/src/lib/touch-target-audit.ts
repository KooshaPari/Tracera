import { logger } from '@/lib/logger';
/**
 * Touch Target Audit Utility
 *
 * WCAG 2.5.5: Target Size (Enhanced) - Level AAA
 * All touch targets should be at least 44x44 CSS pixels (or 44x44 device pixels)
 *
 * This module provides utilities for auditing and ensuring accessibility
 * compliance for touch targets across the application.
 */

const MINIMUM_TOUCH_TARGET_SIZE = 44; // pixels

export interface TouchTargetIssue {
  element: Element;
  width: number;
  height: number;
  selector: string;
  message: string;
}

/**
 * Audit all interactive elements for proper touch target sizing
 * Returns an array of elements that don't meet minimum size requirements
 */
export function auditTouchTargets(container: Document | Element = document): TouchTargetIssue[] {
  const issues: TouchTargetIssue[] = [];

  // Elements that should have touch targets
  const interactiveSelectors = [
    'button',
    'a',
    "input[type='button']",
    "input[type='checkbox']",
    "input[type='radio']",
    "input[type='submit']",
    "input[type='reset']",
    'select',
    "[role='button']",
    "[role='link']",
    "[role='checkbox']",
    "[role='radio']",
    "[role='tab']",
    "[role='switch']",
    "[role='menuitem']",
    '[onclick]',
  ];

  const selector = interactiveSelectors.join(',');
  const elements = container.querySelectorAll(selector);

  elements.forEach((element) => {
    const rect = element.getBoundingClientRect();
    const { width, height } = rect;

    // Check if element is visible (not display:none, visibility:hidden, etc.)
    if (width === 0 || height === 0) return;

    // Check if element is hidden or has opacity 0
    const computedStyle = window.getComputedStyle(element);
    if (
      computedStyle.display === 'none' ||
      computedStyle.visibility === 'hidden' ||
      Number(computedStyle.opacity) === 0
    ) {
      return;
    }

    // Check if element is within a smaller parent (icon inside button)
    // Skip if parent is a button (common pattern for icons)
    const parent = element.parentElement;
    if (parent?.tagName === 'BUTTON' || parent?.tagName === 'A') {
      return;
    }

    const isTooSmall = width < MINIMUM_TOUCH_TARGET_SIZE || height < MINIMUM_TOUCH_TARGET_SIZE;

    if (isTooSmall) {
      const selector = getElementSelector(element);
      issues.push({
        element,
        width: Math.round(width),
        height: Math.round(height),
        selector,
        message: `Touch target too small: ${Math.round(width)}x${Math.round(height)}px (minimum: 44x44px)`,
      });
    }
  });

  return issues;
}

/**
 * Get a unique selector for an element
 */
function getElementSelector(element: Element): string {
  if (element.id) return `#${element.id}`;

  let selector = element.tagName.toLowerCase();

  if (element.className) {
    selector += `.${element.className.split(' ').join('.')}`;
  }

  if (element.parentElement && element.parentElement !== document.body) {
    const parentSelector = getElementSelector(element.parentElement);
    const index = Array.from(element.parentElement.children).indexOf(element);
    selector = `${parentSelector} > ${selector}:nth-child(${index + 1})`;
  }

  return selector;
}

/**
 * Log audit results to console with formatted output
 */
export function logTouchTargetAudit(issues: TouchTargetIssue[]): void {
  if (issues.length === 0) {
    logger.info(
      '%c✓ All touch targets meet minimum 44x44px size requirement',
      'color: green; font-weight: bold;',
    );
    return;
  }

  logger.warn(
    `%c⚠ Found ${issues.length} touch target(s) below 44x44px minimum:`,
    'color: #ff6b6b; font-weight: bold;',
  );

  issues.forEach((issue) => {
    logger.warn(`  ${issue.selector} - ${issue.width}x${issue.height}px`);
  });
}

/**
 * Highlight touch target issues in the DOM for debugging
 */
export function highlightTouchTargetIssues(issues: TouchTargetIssue[]): void {
  const style = document.createElement('style');
  style.textContent = `
    [data-touch-target-issue] {
      outline: 2px dashed #ff6b6b !important;
      outline-offset: 2px !important;
    }
  `;
  document.head.appendChild(style);

  issues.forEach((issue) => {
    issue.element.setAttribute('data-touch-target-issue', issue.message);
  });
}

/**
 * Remove highlighting from touch target issues
 */
export function clearTouchTargetHighlights(): void {
  document.querySelectorAll('[data-touch-target-issue]').forEach((el) => {
    el.removeAttribute('data-touch-target-issue');
  });

  const style = document.querySelector('style[data-touch-target-audit]') as HTMLStyleElement | null;
  if (style) {
    style.remove();
  }
}

/**
 * CSS class utilities to ensure 44x44px minimum touch targets
 */
export const touchTargetClasses = {
  // Minimum height for buttons and inputs
  minTouchHeight: 'min-h-[44px]',
  // Minimum width for buttons and inputs
  minTouchWidth: 'min-w-[44px]',
  // Combined minimum height and width
  minTouchTarget: 'min-h-[44px] min-w-[44px]',
  // Padding to ensure target size
  touchPadding: 'p-2.5', // 10px padding = 44px with normal text size
  // Reduced padding if text provides height
  touchPaddingSmall: 'p-2', // 8px padding = 40px with normal text
};

/**
 * Get recommended styling for a touch target based on its content
 */
export function getTouchTargetStyle(
  options: {
    hasText?: boolean;
    hasIcon?: boolean;
    size?: 'sm' | 'md' | 'lg';
  } = {},
): string {
  const { hasText = true, hasIcon = true, size = 'md' } = options;

  const baseClasses = ['focus:outline-none', 'focus:ring-2', 'focus:ring-primary'];

  if (hasIcon && !hasText) {
    // Icon-only button: ensure it's 44x44
    baseClasses.push('h-11 w-11');
  } else if (hasText && !hasIcon) {
    // Text-only button: ensure minimum height
    baseClasses.push('min-h-[44px]', 'px-4');
  } else {
    // Text with icon or complex content
    baseClasses.push('min-h-[44px]');
    if (size === 'sm') {
      baseClasses.push('px-3', 'py-2');
    } else if (size === 'md') {
      baseClasses.push('px-4', 'py-3');
    } else {
      baseClasses.push('px-6', 'py-4');
    }
  }

  return baseClasses.join(' ');
}
