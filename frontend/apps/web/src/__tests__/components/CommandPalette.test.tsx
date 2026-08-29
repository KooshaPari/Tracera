/**
 * CommandPalette Component Tests
 *
 * Comprehensive tests covering:
 * - Rendering and visibility
 * - Keyboard shortcuts (Cmd/Ctrl+K)
 * - Search and filtering
 * - Command selection
 * - Navigation
 * - Arrow key interaction
 * - Edge cases and error states
 */

import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { CommandPalette } from '@/components/CommandPalette';

// Mock TanStack Router
const mockNavigate = vi.fn(async (options: { to: string; params?: Record<string, unknown> }) => {
  // Handle both old string format and new { to: '...' } format
  if (typeof options === 'string') {
    return;
  }
  if (options && typeof options === 'object' && 'to' in options) {
    return;
  }
  return;
});

// Track current mock pathname for dynamic location mocking
let mockPathname = '/';

vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useRouter: () => ({
      navigate: mockNavigate,
    }),
    useLocation: () => ({ pathname: mockPathname }),
    useParams: () => ({}),
    Link: ({
      children,
      to,
      ...props
    }: {
      children: React.ReactNode;
      to: string;
      [key: string]: unknown;
    }) => (
      <a href={typeof to === 'string' ? to : String((to as unknown) ?? '')} {...props}>
        {children}
      </a>
    ),
  };
});

// Helper to set mock location to a project page
const setProjectContext = (projectId = 'test-project-123') => {
  mockPathname = `/projects/${projectId}`;
};

// Helper to clear project context
const clearProjectContext = () => {
  mockPathname = '/';
};

const renderCommandPalette = () => render(<CommandPalette />);
const queryInput = () => screen.queryByRole('combobox', { name: /search commands/i });
const getInput = () => screen.getByRole('combobox', { name: /search commands/i });
const findInput = () => screen.findByRole('combobox', { name: /search commands/i });

describe('CommandPalette Component', () => {
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    mockNavigate.mockClear();
    clearProjectContext(); // Reset to homepage by default
    user = userEvent.setup();
  });

  afterEach(() => {
    vi.clearAllMocks();
    clearProjectContext();
  });

  describe('Visibility and Rendering', () => {
    it('should not render initially (closed by default)', () => {
      renderCommandPalette();
      expect(queryInput()).not.toBeInTheDocument();
    });

    it('should render when opened with Cmd+K on macOS', async () => {
      renderCommandPalette();

      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(getInput()).toBeInTheDocument();
      });
    });

    it('should render when opened with Ctrl+K on Windows/Linux', async () => {
      renderCommandPalette();

      fireEvent.keyDown(globalThis, { ctrlKey: true, key: 'k' });

      await waitFor(() => {
        expect(getInput()).toBeInTheDocument();
      });
    });

    it('should close when Escape key is pressed', async () => {
      renderCommandPalette();

      // Open palette
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });
      await waitFor(() => {
        expect(getInput()).toBeInTheDocument();
      });

      // Close with Escape
      fireEvent.keyDown(globalThis, { key: 'Escape' });

      await waitFor(() => {
        expect(queryInput()).not.toBeInTheDocument();
      });
    });

    it('should close when clicking backdrop', async () => {
      renderCommandPalette();

      // Open palette
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });
      await waitFor(() => {
        expect(getInput()).toBeInTheDocument();
      });

      // Click backdrop (the parent div with fixed positioning)
      const backdrop = getInput().closest('.fixed');
      if (backdrop) {
        fireEvent.click(backdrop);
      }

      await waitFor(() => {
        expect(queryInput()).not.toBeInTheDocument();
      });
    });

    it('should display search input when opened', async () => {
      renderCommandPalette();

      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        const input = getInput();
        expect(input).toBeInTheDocument();
        // Note: Component doesn't have autoFocus on the input element
      });
    });

    it('should display ESC keyboard hint', async () => {
      renderCommandPalette();

      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByText('ESC')).toBeInTheDocument();
      });
    });
  });

  describe('Command Categories', () => {
    it('should display navigation category commands', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getAllByText('NAVIGATE')).toHaveLength(2);
        expect(screen.getByText('Mission Control')).toBeInTheDocument();
        expect(screen.getByText('Project Registry')).toBeInTheDocument();
        expect(screen.getByText('System Parameters')).toBeInTheDocument();
      });
    });

    it('should display view category commands', async () => {
      // Project-specific views only show when on a project page
      setProjectContext('test-project-123');
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByText('VIEWS')).toBeInTheDocument();
        expect(screen.getByText('Feature Layer')).toBeInTheDocument();
        expect(screen.getByText('Source Mapping')).toBeInTheDocument();
        expect(screen.getByText('Validation Suite')).toBeInTheDocument();
        expect(screen.getByText('Workflow Runs')).toBeInTheDocument();
      });
    });

    it('should display system category commands', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByText('SYSTEM')).toBeInTheDocument();
        expect(screen.getByText('System Parameters')).toBeInTheDocument();
      });
    });

    it('should display command descriptions', async () => {
      // Project-specific views only show when on a project page
      setProjectContext('test-project-123');
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByText('Logic & requirements')).toBeInTheDocument();
        expect(screen.getByText('Repository links')).toBeInTheDocument();
        expect(screen.getByText('Test coverage matrix')).toBeInTheDocument();
      });
    });
  });

  describe('Search and Filtering', () => {
    it('should filter commands by title', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await findInput();

      await user.type(input, 'dashboard');

      await waitFor(() => {
        expect(screen.getByText('Mission Control')).toBeInTheDocument();
        expect(screen.queryByText('Project Registry')).not.toBeInTheDocument();
      });
    });

    it('should filter commands by description', async () => {
      // Project-specific views only show when on a project page
      setProjectContext('test-project-123');
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await findInput();

      await user.type(input, 'logic');

      await waitFor(() => {
        expect(screen.getByText('Feature Layer')).toBeInTheDocument();
        expect(screen.queryByText('Source Mapping')).not.toBeInTheDocument();
      });
    });

    it('should filter commands by keywords', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await findInput();

      await user.type(input, 'home');

      await waitFor(() => {
        expect(screen.getByText('Mission Control')).toBeInTheDocument();
      });
    });

    it('should show no results message when search has no matches', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await findInput();

      await user.type(input, 'nonexistentcommand12345');

      await waitFor(() => {
        expect(screen.getByText(/no results found/i)).toBeInTheDocument();
      });
    });

    it('should perform case-insensitive search', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await findInput();

      await user.type(input, 'DASHBOARD');

      await waitFor(() => {
        expect(screen.getByText('Mission Control')).toBeInTheDocument();
      });
    });

    it('should clear search query when reopening palette', async () => {
      renderCommandPalette();

      // Open, search, close
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });
      const input = await findInput();
      await user.type(input, 'test');
      fireEvent.keyDown(globalThis, { key: 'Escape' });

      // Reopen
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const newInput = await findInput();
      expect(newInput).toHaveValue('');
    });
  });

  describe('Keyboard Navigation', () => {
    it('should navigate down with ArrowDown key', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(getInput()).toBeInTheDocument();
      });

      // First item should be selected by default (index 0)
      const firstItem = screen.getByText('Mission Control').closest('button');
      expect(firstItem).toHaveAttribute('aria-selected', 'true');

      // Navigate down
      fireEvent.keyDown(globalThis, { key: 'ArrowDown' });

      await waitFor(() => {
        const secondItem = screen.getByText('Project Registry').closest('button');
        expect(secondItem).toHaveAttribute('aria-selected', 'true');
      });
    });

    it('should navigate up with ArrowUp key', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(getInput()).toBeInTheDocument();
      });

      // Navigate down twice
      fireEvent.keyDown(globalThis, { key: 'ArrowDown' });
      fireEvent.keyDown(globalThis, { key: 'ArrowDown' });

      // Navigate up once
      fireEvent.keyDown(globalThis, { key: 'ArrowUp' });

      await waitFor(() => {
        const secondItem = screen.getByText('Project Registry').closest('button');
        expect(secondItem).toHaveAttribute('aria-selected', 'true');
      });
    });

    it('should not go below 0 when navigating up from first item', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(getInput()).toBeInTheDocument();
      });

      // Try to navigate up from first item
      fireEvent.keyDown(globalThis, { key: 'ArrowUp' });

      const firstItem = screen.getByText('Mission Control').closest('button');
      expect(firstItem).toHaveAttribute('aria-selected', 'true');
    });

    it('should not go beyond last item when navigating down', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(getInput()).toBeInTheDocument();
      });

      // Navigate down many times (more than total commands)
      for (let i = 0; i < 50; i++) {
        fireEvent.keyDown(globalThis, { key: 'ArrowDown' });
      }

      // Should stay at last item
      const lastItem = screen.getByText('System Parameters').closest('button');
      expect(lastItem).toHaveAttribute('aria-selected', 'true');
    });

    it('should filter results when search query changes', async () => {
      // Project-specific views only show when on a project page
      setProjectContext('test-project-123');
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await findInput();

      // Change search query to filter results
      await user.type(input, 'test');

      // Should show the validation view in filtered results
      await waitFor(() => {
        expect(screen.getByText('Validation Suite')).toBeInTheDocument();
        // Other views should not be visible since they don't match "test"
        expect(screen.queryByText('Feature Layer')).not.toBeInTheDocument();
      });
    });
  });

  describe('Command Execution', () => {
    it('should execute selected command on Enter', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(getInput()).toBeInTheDocument();
      });

      // Execute first command (Mission Control)
      fireEvent.keyDown(globalThis, { key: 'Enter' });

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith({ to: '/home' });
      });
    });

    it('should execute command on click', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const dashboardCommand = await screen.findByText('Mission Control');
      fireEvent.click(dashboardCommand);

      expect(mockNavigate).toHaveBeenCalledWith({ to: '/home' });
    });

    it('should close palette after command execution via Enter', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(getInput()).toBeInTheDocument();
      });

      fireEvent.keyDown(globalThis, { key: 'Enter' });

      await waitFor(() => {
        expect(queryInput()).not.toBeInTheDocument();
      });
    });

    it('should close palette after command execution via click', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const dashboardCommand = await screen.findByText('Mission Control');
      fireEvent.click(dashboardCommand);

      await waitFor(() => {
        expect(queryInput()).not.toBeInTheDocument();
      });
    });

    it('should navigate to projects page', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const projectsCommand = await screen.findByText('Project Registry');
      fireEvent.click(projectsCommand);

      expect(mockNavigate).toHaveBeenCalledWith({ to: '/projects' });
    });

    it('should navigate to settings page', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const settingsCommand = await screen.findByText('System Parameters');
      fireEvent.click(settingsCommand);

      expect(mockNavigate).toHaveBeenCalledWith({ to: '/settings' });
    });

    it('should navigate to view pages', async () => {
      // Project-specific views only show when on a project page
      setProjectContext('test-project-123');
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const codeViewCommand = await screen.findByText('Source Mapping');
      fireEvent.click(codeViewCommand);

      expect(mockNavigate).toHaveBeenCalledWith({
        to: '/projects/test-project-123/views/code',
      });
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid toggling', async () => {
      renderCommandPalette();

      // Rapidly toggle open/close
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(getInput()).toBeInTheDocument();
      });
    });

    it('should not execute command if none is selected', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await findInput();

      // Search for something that doesn't exist
      await user.type(input, 'nonexistent');

      // Try to execute with Enter
      fireEvent.keyDown(globalThis, { key: 'Enter' });

      // Should not call navigate
      expect(mockNavigate).not.toHaveBeenCalled();
    });

    it('should prevent default on Cmd+K', () => {
      renderCommandPalette();

      const event = new KeyboardEvent('keydown', { key: 'k', metaKey: true });
      const preventDefaultSpy = vi.spyOn(event, 'preventDefault');

      act(() => {
        globalThis.dispatchEvent(event);
      });

      expect(preventDefaultSpy).toHaveBeenCalled();
    });

    it('should handle empty search gracefully', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await findInput();

      // Type and delete
      await user.type(input, 'test');
      await user.clear(input);

      // Should show all commands again
      await waitFor(() => {
        expect(screen.getByText('Mission Control')).toBeInTheDocument();
        expect(screen.getByText('Project Registry')).toBeInTheDocument();
      });
    });

    it.skip('should not render when window is undefined (SSR)', () => {
      // This test is skipped because setting window = undefined breaks React rendering in JSDOM
      // The component correctly checks for window existence (lines 202-203)
      // But React DOM requires window to render, making this test incompatible with JSDOM
      const originalWindow = globalThis.window;

      // Simulate SSR environment
      Object.defineProperty(globalThis, 'window', {
        configurable: true,
        value: undefined,
        writable: true,
      });

      renderCommandPalette();

      // Restore window
      Object.defineProperty(globalThis, 'window', {
        configurable: true,
        value: originalWindow,
        writable: true,
      });

      expect(queryInput()).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await findInput();
      expect(input).toHaveAttribute('type', 'text');
    });

    it('should display keyboard shortcuts', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByText('↑↓')).toBeInTheDocument();
        expect(screen.getByText('↵')).toBeInTheDocument();
        expect(screen.getByText('ESC')).toBeInTheDocument();
      });
    });
  });
});
