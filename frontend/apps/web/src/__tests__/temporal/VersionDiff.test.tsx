/**
 * Tests for VersionDiff component
 */

import type { VersionDiff as VersionDiffType } from '@repo/types';

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import VersionDiff from '@/components/temporal/VersionDiff';

const mockDiff: VersionDiffType = {
  added: [
    {
      changeType: 'added',
      itemId: 'item3',
      significance: 'major',
      title: 'New Authentication Feature',
      type: 'feature',
    },
    {
      changeType: 'added',
      itemId: 'item4',
      significance: 'minor',
      title: 'Performance Optimization',
      type: 'enhancement',
    },
  ],
  computedAt: new Date().toISOString(),
  modified: [
    {
      changeType: 'modified',
      fieldChanges: [
        {
          changeType: 'modified',
          field: 'status',
          newValue: 'approved',
          oldValue: 'draft',
        },
        {
          changeType: 'modified',
          field: 'description',
          newValue: 'New description with more details',
          oldValue: 'Old description',
        },
        {
          changeType: 'added',
          field: 'approvedBy',
          newValue: 'john.doe',
          oldValue: null,
        },
      ],
      itemId: 'item1',
      significance: 'major',
      title: 'Core API Specification',
      type: 'requirement',
    },
  ],
  removed: [
    {
      changeType: 'removed',
      itemId: 'item2',
      significance: 'minor',
      title: 'Legacy Bug Report',
      type: 'bug',
    },
  ],
  stats: {
    addedCount: 2,
    modifiedCount: 1,
    removedCount: 1,
    totalChanges: 4,
    unchangedCount: 15,
  },
  unchanged: 15,
  versionA: 'v1',
  versionANumber: 1,
  versionB: 'v2',
  versionBNumber: 2,
};

describe('VersionDiff Component', () => {
  describe('Rendering', () => {
    it('should render version diff component', () => {
      render(<VersionDiff diff={mockDiff} />);
      expect(screen.getByText('Version Comparison')).toBeInTheDocument();
    });

    it('should display version numbers', () => {
      render(<VersionDiff diff={mockDiff} />);
      expect(screen.getByText(/Version 1.*Version 2/)).toBeInTheDocument();
    });

    it('should show statistics cards', () => {
      render(<VersionDiff diff={mockDiff} />);
      expect(screen.getByText('Added')).toBeInTheDocument();
      expect(screen.getByText('Removed')).toBeInTheDocument();
      expect(screen.getByText('Modified')).toBeInTheDocument();
      expect(screen.getByText('Unchanged')).toBeInTheDocument();
    });

    it('should display total changes count', () => {
      render(<VersionDiff diff={mockDiff} />);
      expect(screen.getByText('4')).toBeInTheDocument();
      expect(screen.getByText('total changes')).toBeInTheDocument();
    });

    it('should render tab navigation', () => {
      render(<VersionDiff diff={mockDiff} />);
      expect(screen.getByText('added')).toBeInTheDocument();
      expect(screen.getByText('removed')).toBeInTheDocument();
      expect(screen.getByText('modified')).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    it('should show added items tab by default', () => {
      render(<VersionDiff diff={mockDiff} />);
      const addedTab = screen.getByRole('button', { name: /added/ });
      expect(addedTab).toHaveClass('border-blue-500');
    });

    it('should switch to removed tab', async () => {
      render(<VersionDiff diff={mockDiff} />);
      const removedTab = screen.getByRole('button', { name: /removed/ });
      fireEvent.click(removedTab);

      await waitFor(() => {
        expect(removedTab).toHaveClass('border-blue-500');
      });
    });

    it('should switch to modified tab', async () => {
      render(<VersionDiff diff={mockDiff} />);
      const modifiedTab = screen.getByRole('button', { name: /modified/ });
      fireEvent.click(modifiedTab);

      await waitFor(() => {
        expect(modifiedTab).toHaveClass('border-blue-500');
      });
    });

    it('should display correct item count in tabs', () => {
      render(<VersionDiff diff={mockDiff} />);
      expect(screen.getByText(/added.*\(2\)/)).toBeInTheDocument();
      expect(screen.getByText(/removed.*\(1\)/)).toBeInTheDocument();
      expect(screen.getByText(/modified.*\(1\)/)).toBeInTheDocument();
    });
  });

  describe('Item Display', () => {
    it('should display added items', async () => {
      render(<VersionDiff diff={mockDiff} />);
      const addedTab = screen.getByRole('button', { name: /added/ });
      fireEvent.click(addedTab);

      await waitFor(() => {
        expect(screen.getByText('New Authentication Feature')).toBeInTheDocument();
        expect(screen.getByText('Performance Optimization')).toBeInTheDocument();
      });
    });

    it('should display removed items', async () => {
      render(<VersionDiff diff={mockDiff} />);
      const removedTab = screen.getByRole('button', { name: /removed/ });
      fireEvent.click(removedTab);

      await waitFor(() => {
        expect(screen.getByText('Legacy Bug Report')).toBeInTheDocument();
      });
    });

    it('should display modified items', async () => {
      render(<VersionDiff diff={mockDiff} />);
      const modifiedTab = screen.getByRole('button', { name: /modified/ });
      fireEvent.click(modifiedTab);

      await waitFor(() => {
        expect(screen.getByText('Core API Specification')).toBeInTheDocument();
      });
    });

    it('should show change type badges', async () => {
      render(<VersionDiff diff={mockDiff} />);
      const addedTab = screen.getByRole('button', { name: /added/ });
      fireEvent.click(addedTab);

      await waitFor(() => {
        const badges = screen.getAllByText('added');
        expect(badges.length).toBeGreaterThan(0);
      });
    });

    it('should show significance level', async () => {
      render(<VersionDiff diff={mockDiff} />);
      const addedTab = screen.getByRole('button', { name: /added/ });
      fireEvent.click(addedTab);

      await waitFor(() => {
        expect(screen.getByText('major')).toBeInTheDocument();
        expect(screen.getByText('minor')).toBeInTheDocument();
      });
    });
  });

  describe('Search Functionality', () => {
    it('should filter items by title', async () => {
      const user = userEvent.setup();
      render(<VersionDiff diff={mockDiff} />);

      const searchInput = screen.getByPlaceholderText(/Search added items/i);
      await user.type(searchInput, 'Authentication');

      await waitFor(() => {
        expect(screen.getByText('New Authentication Feature')).toBeInTheDocument();
        expect(screen.queryByText('Performance Optimization')).not.toBeInTheDocument();
      });
    });

    it('should filter items by ID', async () => {
      const user = userEvent.setup();
      render(<VersionDiff diff={mockDiff} />);

      const searchInput = screen.getByPlaceholderText(/Search added items/i);
      await user.type(searchInput, 'item3');

      await waitFor(() => {
        expect(screen.getByText('New Authentication Feature')).toBeInTheDocument();
      });
    });

    it('should show no results message', async () => {
      const user = userEvent.setup();
      render(<VersionDiff diff={mockDiff} />);

      const searchInput = screen.getByPlaceholderText(/Search added items/i);
      await user.type(searchInput, 'nonexistent');

      await waitFor(() => {
        expect(screen.getByText('No items match your search')).toBeInTheDocument();
      });
    });

    it('should clear search and show all items again', async () => {
      const user = userEvent.setup();
      render(<VersionDiff diff={mockDiff} />);

      const searchInput = screen.getByPlaceholderText(/Search added items/i);
      await user.type(searchInput, 'Authentication');
      await user.clear(searchInput);

      await waitFor(() => {
        expect(screen.getByText('New Authentication Feature')).toBeInTheDocument();
        expect(screen.getByText('Performance Optimization')).toBeInTheDocument();
      });
    });
  });

  describe('Item Expansion', () => {
    it('should expand modified item to show field changes', async () => {
      render(<VersionDiff diff={mockDiff} />);
      const modifiedTab = screen.getByRole('button', { name: /modified/ });
      fireEvent.click(modifiedTab);

      await waitFor(() => {
        const itemRow = screen.getByText('Core API Specification');
        fireEvent.click(itemRow.closest("div[class*='hover']") ?? itemRow);
      });

      await waitFor(() => {
        expect(screen.getByText('status')).toBeInTheDocument();
        expect(screen.getByText('description')).toBeInTheDocument();
      });
    });

    it('should show field change details', async () => {
      render(<VersionDiff diff={mockDiff} />);
      const modifiedTab = screen.getByRole('button', { name: /modified/ });
      fireEvent.click(modifiedTab);

      await waitFor(() => {
        const item = screen.getByText('Core API Specification');
        fireEvent.click(item.closest('div') ?? item);
      });

      await waitFor(() => {
        expect(screen.getByText('Old Value')).toBeInTheDocument();
        expect(screen.getByText('New Value')).toBeInTheDocument();
      });
    });
  });

  describe('Export Functionality', () => {
    it('should display export buttons', () => {
      render(<VersionDiff diff={mockDiff} />);
      expect(screen.getByRole('button', { name: /JSON/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /CSV/i })).toBeInTheDocument();
    });

    it('should handle export to JSON', async () => {
      const onExport = vi.fn();
      render(<VersionDiff diff={mockDiff} onExport={onExport} />);

      const jsonButton = screen.getByRole('button', { name: /JSON/i });
      fireEvent.click(jsonButton);

      await waitFor(() => {
        expect(onExport).toHaveBeenCalled();
      });
    });
  });

  describe('Empty State', () => {
    it('should render null diff gracefully', () => {
      render(<VersionDiff diff={null} />);
      expect(screen.getByText('No diff available')).toBeInTheDocument();
    });

    it('should show loading state', () => {
      render(<VersionDiff diff={null} isLoading />);
      const spinner = document.querySelector("div[class*='animate-spin']");
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading structure', () => {
      render(<VersionDiff diff={mockDiff} />);
      expect(screen.getByRole('heading', { level: 2 })).toBeInTheDocument();
    });

    it('should have accessible buttons', () => {
      render(<VersionDiff diff={mockDiff} />);
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
      buttons.forEach((button) => {
        expect(button).toHaveAccessibleName();
      });
    });

    it('should have accessible search input', () => {
      render(<VersionDiff diff={mockDiff} />);
      const searchInput = screen.getByPlaceholderText(/Search/i);
      expect(searchInput).toHaveAttribute('type', 'text');
    });
  });

  describe('Custom Labels', () => {
    it('should use custom version labels', () => {
      render(
        <VersionDiff diff={mockDiff} versionALabel='Release 1.0' versionBLabel='Release 2.0' />,
      );
      expect(screen.getByText(/Release 1.0.*Release 2.0/)).toBeInTheDocument();
    });
  });
});
