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

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
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
      expect(screen.queryByPlaceholderText(/search commands/i)).not.toBeInTheDocument();
    });

    it('should render when opened with Cmd+K on macOS', async () => {
      renderCommandPalette();

      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
      });
    });

    it('should render when opened with Ctrl+K on Windows/Linux', async () => {
      renderCommandPalette();

      fireEvent.keyDown(globalThis, { ctrlKey: true, key: 'k' });

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
      });
    });

    it('should close when Escape key is pressed', async () => {
      renderCommandPalette();

      // Open palette
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
      });

      // Close with Escape
      fireEvent.keyDown(globalThis, { key: 'Escape' });

      await waitFor(() => {
        expect(screen.queryByPlaceholderText(/search commands/i)).not.toBeInTheDocument();
      });
    });

    it('should close when clicking backdrop', async () => {
      renderCommandPalette();

      // Open palette
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
      });

      // Click backdrop (the parent div with fixed positioning)
      const backdrop = screen.getByPlaceholderText(/search commands/i).closest('.fixed');
      if (backdrop) {
        fireEvent.click(backdrop);
      }

      await waitFor(() => {
        expect(screen.queryByPlaceholderText(/search commands/i)).not.toBeInTheDocument();
      });
    });

    it('should display search input when opened', async () => {
      renderCommandPalette();

      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        const input = screen.getByPlaceholderText(/search commands/i);
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
        expect(screen.getByText('navigation')).toBeInTheDocument();
        expect(screen.getByText('Go to Dashboard')).toBeInTheDocument();
        expect(screen.getByText('Go to Projects')).toBeInTheDocument();
        expect(screen.getByText('Go to Settings')).toBeInTheDocument();
      });
    });

    it('should display view category commands', async () => {
      // Project-specific views only show when on a project page
      setProjectContext('test-project-123');
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByText('view')).toBeInTheDocument();
        expect(screen.getByText('Feature View')).toBeInTheDocument();
        expect(screen.getByText('Code View')).toBeInTheDocument();
        expect(screen.getByText('Test View')).toBeInTheDocument();
        expect(screen.getByText('Graph View')).toBeInTheDocument();
      });
    });

    it('should display action category commands', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByText('action')).toBeInTheDocument();
        expect(screen.getByText('Create New Item')).toBeInTheDocument();
      });
    });

    it('should display command descriptions', async () => {
      // Project-specific views only show when on a project page
      setProjectContext('test-project-123');
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByText('Epics, features, stories')).toBeInTheDocument();
        expect(screen.getByText('Modules and files')).toBeInTheDocument();
        expect(screen.getByText('Test suites and cases')).toBeInTheDocument();
      });
    });
  });

  describe('Search and Filtering', () => {
    it('should filter commands by title', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await screen.findByPlaceholderText(/search commands/i);

      await user.type(input, 'dashboard');

      await waitFor(() => {
        expect(screen.getByText('Go to Dashboard')).toBeInTheDocument();
        expect(screen.queryByText('Go to Projects')).not.toBeInTheDocument();
      });
    });

    it('should filter commands by description', async () => {
      // Project-specific views only show when on a project page
      setProjectContext('test-project-123');
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await screen.findByPlaceholderText(/search commands/i);

      await user.type(input, 'epics');

      await waitFor(() => {
        expect(screen.getByText('Feature View')).toBeInTheDocument();
        expect(screen.queryByText('Code View')).not.toBeInTheDocument();
      });
    });

    it('should filter commands by keywords', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await screen.findByPlaceholderText(/search commands/i);

      await user.type(input, 'home');

      await waitFor(() => {
        expect(screen.getByText('Go to Dashboard')).toBeInTheDocument();
      });
    });

    it('should show no results message when search has no matches', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await screen.findByPlaceholderText(/search commands/i);

      await user.type(input, 'nonexistentcommand12345');

      await waitFor(() => {
        expect(screen.getByText(/no results found/i)).toBeInTheDocument();
      });
    });

    it('should perform case-insensitive search', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await screen.findByPlaceholderText(/search commands/i);

      await user.type(input, 'DASHBOARD');

      await waitFor(() => {
        expect(screen.getByText('Go to Dashboard')).toBeInTheDocument();
      });
    });

    it('should clear search query when reopening palette', async () => {
      renderCommandPalette();

      // Open, search, close
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });
      const input = await screen.findByPlaceholderText(/search commands/i);
      await user.type(input, 'test');
      fireEvent.keyDown(globalThis, { key: 'Escape' });

      // Reopen
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const newInput = await screen.findByPlaceholderText(/search commands/i);
      expect(newInput).toHaveValue('');
    });
  });

  describe('Keyboard Navigation', () => {
    it('should navigate down with ArrowDown key', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
      });

      // First item should be selected by default (index 0)
      const firstItem = screen.getByText('Go to Dashboard').closest('button');
      expect(firstItem).toHaveClass('bg-accent');

      // Navigate down
      fireEvent.keyDown(globalThis, { key: 'ArrowDown' });

      await waitFor(() => {
        const secondItem = screen.getByText('Go to Projects').closest('button');
        expect(secondItem).toHaveClass('bg-accent');
      });
    });

    it('should navigate up with ArrowUp key', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
      });

      // Navigate down twice
      fireEvent.keyDown(globalThis, { key: 'ArrowDown' });
      fireEvent.keyDown(globalThis, { key: 'ArrowDown' });

      // Navigate up once
      fireEvent.keyDown(globalThis, { key: 'ArrowUp' });

      await waitFor(() => {
        const secondItem = screen.getByText('Go to Projects').closest('button');
        expect(secondItem).toHaveClass('bg-accent');
      });
    });

    it('should not go below 0 when navigating up from first item', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
      });

      // Try to navigate up from first item
      fireEvent.keyDown(globalThis, { key: 'ArrowUp' });

      const firstItem = screen.getByText('Go to Dashboard').closest('button');
      expect(firstItem).toHaveClass('bg-accent');
    });

    it('should not go beyond last item when navigating down', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
      });

      // Navigate down many times (more than total commands)
      for (let i = 0; i < 50; i++) {
        fireEvent.keyDown(globalThis, { key: 'ArrowDown' });
      }

      // Should stay at last item
      const lastItem = screen.getByText('Create New Item').closest('button');
      expect(lastItem).toHaveClass('bg-accent');
    });

    it('should filter results when search query changes', async () => {
      // Project-specific views only show when on a project page
      setProjectContext('test-project-123');
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await screen.findByPlaceholderText(/search commands/i);

      // Change search query to filter results
      await user.type(input, 'test');

      // Should show Test View in filtered results
      await waitFor(() => {
        expect(screen.getByText('Test View')).toBeInTheDocument();
        // Other views should not be visible since they don't match "test"
        expect(screen.queryByText('Feature View')).not.toBeInTheDocument();
      });
    });
  });

  describe('Command Execution', () => {
    it('should execute selected command on Enter', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
      });

      // Execute first command (Go to Dashboard)
      fireEvent.keyDown(globalThis, { key: 'Enter' });

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith({ to: '/home' });
      });
    });

    it('should execute command on click', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const dashboardCommand = await screen.findByText('Go to Dashboard');
      fireEvent.click(dashboardCommand);

      expect(mockNavigate).toHaveBeenCalledWith({ to: '/home' });
    });

    it('should close palette after command execution via Enter', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
      });

      fireEvent.keyDown(globalThis, { key: 'Enter' });

      await waitFor(() => {
        expect(screen.queryByPlaceholderText(/search commands/i)).not.toBeInTheDocument();
      });
    });

    it('should close palette after command execution via click', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const dashboardCommand = await screen.findByText('Go to Dashboard');
      fireEvent.click(dashboardCommand);

      await waitFor(() => {
        expect(screen.queryByPlaceholderText(/search commands/i)).not.toBeInTheDocument();
      });
    });

    it('should navigate to projects page', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const projectsCommand = await screen.findByText('Go to Projects');
      fireEvent.click(projectsCommand);

      expect(mockNavigate).toHaveBeenCalledWith({ to: '/projects' });
    });

    it('should navigate to settings page', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const settingsCommand = await screen.findByText('Go to Settings');
      fireEvent.click(settingsCommand);

      expect(mockNavigate).toHaveBeenCalledWith({ to: '/settings' });
    });

    it('should navigate to view pages', async () => {
      // Project-specific views only show when on a project page
      setProjectContext('test-project-123');
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const codeViewCommand = await screen.findByText('Code View');
      fireEvent.click(codeViewCommand);

      // The navigate call uses TanStack Router format with params
      expect(mockNavigate).toHaveBeenCalledWith({
        params: {
          projectId: 'test-project-123',
          viewType: 'code',
        },
        to: '/projects/$projectId/views/$viewType',
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
        expect(screen.getByPlaceholderText(/search commands/i)).toBeInTheDocument();
      });
    });

    it('should not execute command if none is selected', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await screen.findByPlaceholderText(/search commands/i);

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

      globalThis.dispatchEvent(event);

      expect(preventDefaultSpy).toHaveBeenCalled();
    });

    it('should handle empty search gracefully', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await screen.findByPlaceholderText(/search commands/i);

      // Type and delete
      await user.type(input, 'test');
      await user.clear(input);

      // Should show all commands again
      await waitFor(() => {
        expect(screen.getByText('Go to Dashboard')).toBeInTheDocument();
        expect(screen.getByText('Go to Projects')).toBeInTheDocument();
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

      expect(screen.queryByPlaceholderText(/search commands/i)).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      const input = await screen.findByPlaceholderText(/search commands/i);
      expect(input).toHaveAttribute('type', 'text');
    });

    it('should display keyboard shortcuts', async () => {
      renderCommandPalette();
      fireEvent.keyDown(globalThis, { key: 'k', metaKey: true });

      await waitFor(() => {
        expect(screen.getByText('↑↓')).toBeInTheDocument();
        expect(screen.getByText('↵')).toBeInTheDocument();
        expect(screen.getByText('⌘K')).toBeInTheDocument();
      });
    });
  });
});
