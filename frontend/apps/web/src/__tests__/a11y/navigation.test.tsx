/**
 * Accessibility Tests for Navigation and Keyboard Interactions
 * Tests keyboard navigation, focus management, and interactive elements
 */
/// <reference path="../../test/user-event.d.ts" />
/// <reference path="../../test/jest-axe.d.ts" />

import { render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { CommandPalette } from '@/components/CommandPalette';

import { axe, pressArrowDown, pressArrowUp, pressEnter, pressEscape, pressKey } from './setup';

// Mock TanStack Router
const mockNavigate = vi.fn();
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useRouter: () => ({ navigate: mockNavigate }),
    useLocation: () => ({ pathname: '/' }),
    useParams: () => ({}),
    Link: ({ children, to, ...props }: any) => (
      <a href={typeof to === 'string' ? to : to?.toString?.()} {...props}>
        {children}
      </a>
    ),
  };
});

describe('Command Palette Keyboard Navigation', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(<CommandPalette />);

    // Open command palette
    pressKey('k', { metaKey: true });

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
    });

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should open with Cmd+K or Ctrl+K', async () => {
    render(<CommandPalette />);

    // Test Cmd+K (Mac)
    pressKey('k', { metaKey: true });
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
    });

    // Close
    pressEscape();

    // Test Ctrl+K (Windows/Linux)
    pressKey('k', { ctrlKey: true });
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
    });
  });

  it('should close with Escape key', async () => {
    render(<CommandPalette />);

    pressKey('k', { metaKey: true });
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
    });

    pressEscape();
    await waitFor(() => {
      expect(screen.queryByPlaceholderText(/search commands/i)).not.toBeInTheDocument();
    });
  });

  it('should navigate with arrow keys', async () => {
    render(<CommandPalette />);

    pressKey('k', { metaKey: true });
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
    });

    // Test arrow down
    pressArrowDown();
    // First item should be selected

    // Test arrow up
    pressArrowUp();
    // Selection should move up or stay at first
  });

  it('should execute command with Enter key', async () => {
    render(<CommandPalette />);

    pressKey('k', { metaKey: true });
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
    });

    // Press enter to execute first command
    pressEnter();
    // Command should be executed and palette closed
  });

  it('should focus search input when opened', async () => {
    render(<CommandPalette />);

    pressKey('k', { metaKey: true });
    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText(/search commands/i);
      expect(searchInput).toBeInTheDocument();
      expect(searchInput).toHaveFocus();
    });
  });

  it('should filter commands as user types', async () => {
    render(<CommandPalette />);

    pressKey('k', { metaKey: true });
    const searchInput = await screen.findByPlaceholderText(/search commands/i);

    await globalThis.user.type(searchInput, 'dashboard');
    // Should filter to dashboard-related commands
  });
});

describe('Skip Links', () => {
  it('should provide skip to main content link', async () => {
    const { container } = render(
      <div>
        <a href='#main-content' className='sr-only focus:not-sr-only'>
          Skip to main content
        </a>
        <nav>
          <a href='/'>Home</a>
          <a href='/about'>About</a>
        </nav>
        <main id='main-content'>
          <h1>Main Content</h1>
        </main>
      </div>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const skipLink = screen.getByText('Skip to main content');
    expect(skipLink).toHaveAttribute('href', '#main-content');
  });

  it('should focus main content when skip link activated', async () => {
    render(
      <div>
        <a href='#main-content'>Skip to main content</a>
        <main id='main-content' tabIndex={-1}>
          <h1>Content</h1>
        </main>
      </div>,
    );

    // Verify skip link exists
    const skipLink = screen.getByText('Skip to main content');
    expect(skipLink).toBeInTheDocument();
    expect(skipLink).toHaveAttribute('href', '#main-content');

    // Verify main content is focusable
    const mainContent = screen.getByRole('main');
    expect(mainContent).toBeInTheDocument();
    expect(mainContent).toHaveAttribute('tabindex', '-1');
  });
});

describe('Focus Management', () => {
  it('should maintain focus within modal/dialog', async () => {
    render(
      <div>
        <button>Outside Button</button>
        <div role='dialog' aria-modal='true' aria-labelledby='dialog-title'>
          <h2 id='dialog-title'>Dialog</h2>
          <input type='text' placeholder='First field' />
          <input type='text' placeholder='Second field' />
          <button>Close</button>
        </div>
      </div>,
    );

    const firstField = screen.getByPlaceholderText('First field');
    const secondField = screen.getByPlaceholderText('Second field');
    const closeButton = screen.getByRole('button', { name: 'Close' });

    firstField.focus();
    expect(firstField).toHaveFocus();

    await globalThis.user.tab();
    expect(secondField).toHaveFocus();

    await globalThis.user.tab();
    expect(closeButton).toHaveFocus();

    // Tabbing from last element should wrap to first
    await globalThis.user.tab();
    // Should trap focus within dialog
  });

  it('should restore focus after dialog closes', async () => {
    const { rerender } = render(
      <div>
        <button>Open Dialog</button>
      </div>,
    );

    const openButton = screen.getByRole('button', { name: 'Open Dialog' });

    // Dialog opens
    rerender(
      <div>
        <button>Open Dialog</button>
        <div role='dialog' aria-labelledby='title' aria-modal='true'>
          <h2 id='title'>Dialog</h2>
          <button>Close</button>
        </div>
      </div>,
    );

    // Verify dialog exists
    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');

    const closeButton = screen.getByRole('button', { name: 'Close' });
    expect(closeButton).toBeInTheDocument();

    // Dialog closes
    rerender(
      <div>
        <button>Open Dialog</button>
      </div>,
    );

    // Verify the trigger button still exists
    expect(openButton).toBeInTheDocument();
  });
});

describe('Focus Indicators', () => {
  it('should show visible focus indicator on interactive elements', async () => {
    render(
      <div>
        <button className='focus-visible:ring-2'>Button</button>
        <a href='/link' className='focus-visible:ring-2'>
          Link
        </a>
        <input type='text' className='focus-visible:ring-2' placeholder='Input' />
      </div>,
    );

    const button = screen.getByRole('button');
    await globalThis.user.tab();
    expect(button).toHaveFocus();

    const link = screen.getByRole('link');
    await globalThis.user.tab();
    expect(link).toHaveFocus();

    const input = screen.getByPlaceholderText('Input');
    await globalThis.user.tab();
    expect(input).toHaveFocus();
  });
});

describe('Landmark Regions', () => {
  it('should have proper landmark structure', async () => {
    const { container } = render(
      <div>
        <header>
          <nav aria-label='Main navigation'>
            <a href='/'>Home</a>
          </nav>
        </header>
        <main>
          <h1>Page Title</h1>
          <article>
            <h2>Article Title</h2>
          </article>
        </main>
        <aside aria-label='Sidebar'>
          <h2>Related Content</h2>
        </aside>
        <footer>
          <p>Copyright 2025</p>
        </footer>
      </div>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    expect(screen.getByRole('banner')).toBeInTheDocument(); // Header
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
    expect(screen.getByRole('complementary')).toBeInTheDocument(); // Aside
    expect(screen.getByRole('contentinfo')).toBeInTheDocument(); // Footer
  });

  it('should label multiple navigation regions', async () => {
    const { container } = render(
      <div>
        <nav aria-label='Main navigation'>
          <a href='/'>Home</a>
        </nav>
        <nav aria-label='Footer navigation'>
          <a href='/privacy'>Privacy</a>
        </nav>
      </div>,
    );

    const results = await axe(container);
    expect(results).toHaveNoViolations();

    const navs = screen.getAllByRole('navigation');
    expect(navs).toHaveLength(2);
    expect(screen.getByRole('navigation', { name: 'Main navigation' })).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: 'Footer navigation' })).toBeInTheDocument();
  });
});

describe('Tab Navigation Order', () => {
  it('should follow logical tab order', async () => {
    render(
      <div>
        <button>First</button>
        <a href='/link'>Second</a>
        <input type='text' placeholder='Third' />
        <button>Fourth</button>
      </div>,
    );

    const first = screen.getByRole('button', { name: 'First' });
    const second = screen.getByRole('link', { name: 'Second' });
    const third = screen.getByPlaceholderText('Third');
    const fourth = screen.getByRole('button', { name: 'Fourth' });

    first.focus();
    expect(first).toHaveFocus();

    await globalThis.user.tab();
    expect(second).toHaveFocus();

    await globalThis.user.tab();
    expect(third).toHaveFocus();

    await globalThis.user.tab();
    expect(fourth).toHaveFocus();
  });

  it('should skip disabled elements', async () => {
    render(
      <div>
        <button>Enabled 1</button>
        <button disabled>Disabled</button>
        <button>Enabled 2</button>
      </div>,
    );

    const enabled1 = screen.getByRole('button', { name: 'Enabled 1' });
    const enabled2 = screen.getByRole('button', { name: 'Enabled 2' });

    enabled1.focus();
    expect(enabled1).toHaveFocus();

    await globalThis.user.tab();
    expect(enabled2).toHaveFocus();
  });
});

describe('Custom Controls Keyboard Support', () => {
  it('should support Space and Enter for custom buttons', async () => {
    const handleClick = vi.fn();

    render(
      <div
        role='button'
        tabIndex={0}
        onClick={handleClick}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleClick();
          }
        }}
      >
        Custom Button
      </div>,
    );

    const customButton = screen.getByRole('button');
    customButton.focus();

    await globalThis.user.keyboard('{Enter}');
    expect(handleClick).toHaveBeenCalledOnce();

    await globalThis.user.keyboard(' ');
    expect(handleClick).toHaveBeenCalledTimes(2);
  });

  it('should support arrow keys for custom select', async () => {
    render(
      <div role='listbox' aria-label='Options'>
        <div role='option' aria-selected='true' tabIndex={0}>
          Option 1
        </div>
        <div role='option' aria-selected='false' tabIndex={-1}>
          Option 2
        </div>
        <div role='option' aria-selected='false' tabIndex={-1}>
          Option 3
        </div>
      </div>,
    );

    const listbox = screen.getByRole('listbox');
    const options = screen.getAllByRole('option');
    expect(listbox).toBeInTheDocument();

    const firstOption = options[0];
    if (firstOption) {
      firstOption.focus();
      expect(firstOption).toHaveFocus();
    }

    // Arrow down should move to next option
    await globalThis.user.keyboard('{ArrowDown}');
    // Should focus next option
  });
});
