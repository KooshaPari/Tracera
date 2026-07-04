/**
 * Accessibility Testing Setup
 * Configures jest-axe for WCAG 2.1 Level AA compliance testing
 */

import { configureAxe } from 'jest-axe';

// Configure axe-core with WCAG 2.1 Level AA standards
export const axe = configureAxe({
  rules: {
    // WCAG 2.1 Level A & AA rules
    'aria-allowed-attr': { enabled: true },
    'aria-required-attr': { enabled: true },
    'aria-valid-attr': { enabled: true },
    'aria-valid-attr-value': { enabled: true },
    'button-name': { enabled: true },
    'color-contrast': { enabled: true },
    'duplicate-id': { enabled: true },
    'form-field-multiple-labels': { enabled: true },
    'frame-title': { enabled: true },
    'html-has-lang': { enabled: true },
    'html-lang-valid': { enabled: true },
    'image-alt': { enabled: true },
    'input-image-alt': { enabled: true },
    label: { enabled: true },
    'link-name': { enabled: true },
    list: { enabled: true },
    listitem: { enabled: true },
    'meta-viewport': { enabled: true },
    'valid-lang': { enabled: true },
    'video-caption': { enabled: true },
  },
});

import { act } from '@testing-library/react';

/**
 * Helper to test keyboard navigation
 */
export function pressKey(key: string, options: KeyboardEventInit = {}) {
  let event: KeyboardEvent | null = null;
  act(() => {
    event = new KeyboardEvent('keydown', {
      key,
      bubbles: true,
      cancelable: true,
      ...options,
    });
    if (event) {
      document.dispatchEvent(event);
    }
  });
  return event;
}

/**
 * Helper to simulate Tab key navigation
 */
export function pressTab(shift = false) {
  return pressKey('Tab', { shiftKey: shift });
}

/**
 * Helper to simulate Enter key
 */
export function pressEnter() {
  return pressKey('Enter');
}

/**
 * Helper to simulate Escape key
 */
export function pressEscape() {
  return pressKey('Escape');
}

/**
 * Helper to simulate arrow keys
 */
export function pressArrowDown() {
  return pressKey('ArrowDown');
}

export function pressArrowUp() {
  return pressKey('ArrowUp');
}

/**
 * Get the currently focused element
 */
export function getFocusedElement() {
  return document.activeElement;
}

/**
 * Check if element has visible focus indicator
 */
export function hasFocusIndicator(element: Element | null) {
  if (!element) {
    return false;
  }
  const styles = globalThis.getComputedStyle(element);

  // Check for outline or box-shadow (common focus indicators)
  return styles.outline !== 'none' || styles.outlineWidth !== '0px' || styles.boxShadow !== 'none';
}

/**
 * Check if element is keyboard accessible
 */
export function isKeyboardAccessible(element: Element | null) {
  if (!element) {
    return false;
  }

  const tagName = element.tagName.toLowerCase();
  const tabIndex = element.getAttribute('tabindex');

  // Naturally keyboard accessible elements
  const interactiveElements = ['a', 'button', 'input', 'select', 'textarea'];
  if (interactiveElements.includes(tagName)) {
    return true;
  }

  // Check for explicit tabindex
  return tabIndex !== null && Number.parseInt(tabIndex, 10) >= 0;
}
