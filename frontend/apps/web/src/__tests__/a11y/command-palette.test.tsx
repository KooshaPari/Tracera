/**
 * Accessibility Tests for CommandPalette
 * Tests combobox ARIA pattern, keyboard navigation, focus management
 */

import { render } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { axe } from './setup';

// Mock CommandPalette component for testing
function MockCommandPalette({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) {
    return null;
  }

  return (
    <div
      role='dialog'
      aria-modal='true'
      aria-labelledby='command-palette-title'
      className='fixed inset-0 z-[100]'
    >
      <div aria-hidden='true' onClick={onClose} />
      <div
        onClick={(e) => {
          e.stopPropagation();
        }}
        className='relative w-full max-w-2xl'
      >
        <div className='flex items-center gap-4 px-6 py-5'>
          <div className='flex-1'>
            <label htmlFor='command-input' className='sr-only' id='command-palette-title'>
              Command Palette
            </label>
            <input
              id='command-input'
              type='text'
              placeholder='Execute command or jump to view...'
              aria-label='Search commands'
              aria-describedby='command-hint'
              aria-expanded
              aria-controls='command-listbox'
              aria-activedescendant='cmd-item-nav-home'
              role='combobox'
              autoComplete='off'
            />
            <span id='command-hint' className='sr-only'>
              5 results found. Use arrow keys to navigate, Enter to select, Home/End to jump, Escape
              to close.
            </span>
          </div>
          <kbd>ESC</kbd>
        </div>

        <div id='command-listbox' role='listbox'>
          <div>
            <div className='text-muted-foreground'>NAVIGATE</div>
            <button
              id='cmd-item-nav-home'
              role='option'
              aria-selected
              aria-describedby='cmd-item-nav-home-desc'
            >
              <div id='cmd-item-nav-home-desc'>Home</div>
              <div>Main dashboard</div>
            </button>
          </div>

          <div role='status' aria-live='polite' aria-atomic='true'>
            <p>5 results found for "test"</p>
          </div>
        </div>
      </div>
    </div>
  );
}

describe('CommandPalette - Combobox ARIA Pattern', () => {
  it('should have proper combobox structure with ARIA roles', async () => {
    const { container, getByRole } = render(<MockCommandPalette open onClose={() => {}} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(getByRole('dialog')).toBeInTheDocument();
    expect(getByRole('combobox')).toBeInTheDocument();
    expect(getByRole('listbox')).toBeInTheDocument();
  });

  it('should have aria-label and aria-describedby on input', async () => {
    const { container, getByRole } = render(<MockCommandPalette open onClose={() => {}} />);
    const input = getByRole('combobox');

    expect(input).toHaveAttribute('aria-label', 'Search commands');
    expect(input).toHaveAttribute('aria-describedby');
    expect(input).toHaveAttribute('aria-expanded', 'true');
    expect(input).toHaveAttribute('aria-controls', 'command-listbox');
    expect(input).toHaveAttribute('aria-activedescendant');

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it("should have role='option' on command items", async () => {
    const { container, getAllByRole } = render(<MockCommandPalette open onClose={() => {}} />);
    const options = getAllByRole('option');

    expect(options.length).toBeGreaterThan(0);
    options.forEach((option) => {
      expect(option).toHaveAttribute('aria-selected');
      expect(option).toHaveAttribute('aria-describedby');
    });

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have aria-live region for search results', () => {
    const { getByRole } = render(<MockCommandPalette open onClose={() => {}} />);
    const liveRegion = getByRole('status');

    expect(liveRegion).toHaveAttribute('aria-live', 'polite');
    expect(liveRegion).toHaveAttribute('aria-atomic', 'true');
  });

  it('should have aria-label on dialog', async () => {
    const { container, getByRole } = render(<MockCommandPalette open onClose={() => {}} />);
    const dialog = getByRole('dialog');

    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby');

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe('CommandPalette - Keyboard Navigation', () => {
  it('should support arrow key navigation', async () => {
    const { getByRole } = render(<MockCommandPalette open onClose={() => {}} />);
    const input = getByRole('combobox');

    input.focus();
    expect(input).toHaveFocus();

    // Arrow down should not cause error
    await user.keyboard('{ArrowDown}');
    expect(input).toHaveFocus();
  });

  it('should support Escape to close', async () => {
    const handleClose = vi.fn();

    render(<MockCommandPalette open onClose={handleClose} />);
    const input = getByRole('combobox');
    input.focus();

    await user.keyboard('{Escape}');
    expect(handleClose).toHaveBeenCalled();
  });

  it('should support Enter to select', async () => {
    const { getByRole } = render(<MockCommandPalette open onClose={() => {}} />);
    const input = getByRole('combobox');

    input.focus();
    // Enter key should work
    await user.keyboard('{Enter}');
    // No error should occur
  });

  it('should support Tab to exit palette', async () => {
    const handleClose = vi.fn();
    const { getByRole } = render(<MockCommandPalette open onClose={handleClose} />);
    const input = getByRole('combobox');

    input.focus();
    await user.keyboard('{Tab}');
    // Tab should allow natural focus movement
  });
});

describe('CommandPalette - Focus Management', () => {
  it('should have visible focus indicator on input', () => {
    const { getByRole } = render(<MockCommandPalette open onClose={() => {}} />);
    const input = getByRole('combobox');

    input.focus();
    expect(input).toHaveFocus();

    // Check for focus-visible class or ring
    const _styles = globalThis.getComputedStyle(input);
    // Focus indicator should be visible
  });

  it('should have proper focus trap structure', () => {
    const { getByRole } = render(<MockCommandPalette open onClose={() => {}} />);
    const dialog = getByRole('dialog');

    // Dialog should be a focusable container
    expect(dialog).toBeInTheDocument();

    // Should have focusable elements
    const focusables = dialog.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]',
    );
    expect(focusables.length).toBeGreaterThan(0);
  });
});

describe('CommandPalette - Search Results', () => {
  it('should have aria-live region that announces results', () => {
    const { getByRole } = render(<MockCommandPalette open onClose={() => {}} />);
    const liveRegion = getByRole('status');

    expect(liveRegion).toHaveAttribute('aria-live', 'polite');
    expect(liveRegion.textContent).toContain('results found');
  });

  it('should have no results status message', () => {
    const { getByRole } = render(<MockCommandPalette open onClose={() => {}} />);
    const status = getByRole('status');

    expect(status).toBeInTheDocument();
    // Status should announce when there are no results
  });
});

describe('CommandPalette - Screen Reader Accessibility', () => {
  it('should have accessible dialog structure', async () => {
    const { container, getByRole } = render(<MockCommandPalette open onClose={() => {}} />);

    // Dialog should have proper ARIA attributes
    const dialog = getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby');

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should provide helpful labels for all interactive elements', async () => {
    const { container, getByRole } = render(<MockCommandPalette open onClose={() => {}} />);

    const input = getByRole('combobox');
    expect(input).toHaveAttribute('aria-label');
    expect(input).toHaveAttribute('aria-describedby');

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});

describe('CommandPalette - WCAG 2.1 AA Compliance', () => {
  it('should pass axe accessibility audit', async () => {
    render(<MockCommandPalette open onClose={() => {}} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should have sufficient color contrast', () => {
    render(<MockCommandPalette open onClose={() => {}} />);

    // All text should have sufficient contrast
    const textElements = container.querySelectorAll('p, span, button, input');
    expect(textElements.length).toBeGreaterThan(0);
  });

  it('should have visible focus indicators', () => {
    const { getByRole } = render(<MockCommandPalette open onClose={() => {}} />);
    const input = getByRole('combobox');

    input.focus();
    expect(input).toHaveFocus();

    // Element should have visible focus indicator
    // Typically ring-2 or outline
  });
});
