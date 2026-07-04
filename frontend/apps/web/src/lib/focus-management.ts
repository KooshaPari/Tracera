/**
 * Focus Management Utilities
 * Provides helpers for managing focus, focus trapping, and restoration
 * Supports WCAG 2.1 AA focus management requirements
 */

/**
 * Get all focusable elements within a container
 * Includes buttons, links, inputs, selects, textareas, and elements with tabindex >= 0
 */
export function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const focusableSelectors = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
    '[contenteditable="true"]',
  ];

  const elements = container.querySelectorAll<HTMLElement>(focusableSelectors.join(','));

  return Array.from(elements).filter((el) => {
    // Check if visible
    const style = window.getComputedStyle(el);
    return style.visibility !== 'hidden' && style.display !== 'none';
  });
}

/**
 * Create a focus trap for a modal/dialog
 * Keeps focus within the container while Tab/Shift+Tab is pressed
 */
export function createFocusTrap(container: HTMLElement, onEscape?: () => void): () => void {
  const handleKeyDown = (event: KeyboardEvent) => {
    // Handle Escape key
    if (event.key === 'Escape' && onEscape) {
      event.preventDefault();
      onEscape();
      return;
    }

    // Only trap Tab key
    if (event.key !== 'Tab') return;

    const focusableElements = getFocusableElements(container);
    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    if (!firstElement || !lastElement) return;
    const activeElement = document.activeElement as HTMLElement;

    if (event.shiftKey) {
      // Shift+Tab: move to previous element
      if (activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      }
    } else {
      // Tab: move to next element
      if (activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    }
  };

  container.addEventListener('keydown', handleKeyDown);

  // Return cleanup function
  return () => {
    container.removeEventListener('keydown', handleKeyDown);
  };
}

/**
 * Store the current focus for later restoration
 */
export function saveFocus(): HTMLElement | null {
  return document.activeElement as HTMLElement | null;
}

/**
 * Restore focus to a previously saved element
 */
export function restoreFocus(element: HTMLElement | null): void {
  if (element && element instanceof HTMLElement) {
    element.focus();
  }
}

/**
 * Focus the first focusable element in a container
 */
export function focusFirst(container: HTMLElement): void {
  const focusableElements = getFocusableElements(container);
  focusableElements[0]?.focus();
}

/**
 * Focus the last focusable element in a container
 */
export function focusLast(container: HTMLElement): void {
  const focusableElements = getFocusableElements(container);
  focusableElements[focusableElements.length - 1]?.focus();
}

/**
 * Get the next focusable element from a starting point
 */
export function getNextFocusableElement(
  current: HTMLElement,
  container: HTMLElement,
): HTMLElement | null {
  const focusableElements = getFocusableElements(container);
  const currentIndex = focusableElements.indexOf(current);

  if (currentIndex === -1 || currentIndex === focusableElements.length - 1) {
    return focusableElements[0] || null;
  }

  return focusableElements[currentIndex + 1] || null;
}

/**
 * Get the previous focusable element from a starting point
 */
export function getPreviousFocusableElement(
  current: HTMLElement,
  container: HTMLElement,
): HTMLElement | null {
  const focusableElements = getFocusableElements(container);
  const currentIndex = focusableElements.indexOf(current);

  if (currentIndex <= 0) {
    return focusableElements[focusableElements.length - 1] || null;
  }

  return focusableElements[currentIndex - 1] || null;
}

/**
 * Check if an element has a visible focus indicator
 */
export function hasFocusIndicator(element: Element | null): boolean {
  if (!element) return false;
  const styles = window.getComputedStyle(element);

  // Check for outline or box-shadow (common focus indicators)
  return styles.outline !== 'none' || styles.outlineWidth !== '0px' || styles.boxShadow !== 'none';
}

/**
 * Check if element is keyboard accessible
 */
export function isKeyboardAccessible(element: Element | null): boolean {
  if (!element) return false;

  const tagName = element.tagName.toLowerCase();
  const tabIndex = element.getAttribute('tabindex');

  // Naturally keyboard accessible elements
  const interactiveElements = ['a', 'button', 'input', 'select', 'textarea'];
  if (interactiveElements.includes(tagName)) return true;

  // Check for explicit tabindex >= 0
  return tabIndex !== null && parseInt(tabIndex, 10) >= 0;
}

/**
 * Announce a message to screen readers using aria-live region
 */
export function announceToScreenReader(
  message: string,
  priority: 'polite' | 'assertive' = 'polite',
): void {
  // Create or get announcement region
  let announcer = document.getElementById('aria-announcer');

  if (!announcer) {
    announcer = document.createElement('div');
    announcer.id = 'aria-announcer';
    announcer.setAttribute('aria-live', priority);
    announcer.setAttribute('aria-atomic', 'true');
    announcer.className = 'sr-only';
    document.body.appendChild(announcer);
  }

  // Update priority if needed
  announcer.setAttribute('aria-live', priority);

  // Clear and set new message
  announcer.textContent = '';
  // Use setTimeout to ensure screen readers pick up the change
  setTimeout(() => {
    announcer!.textContent = message;
  }, 100);
}
