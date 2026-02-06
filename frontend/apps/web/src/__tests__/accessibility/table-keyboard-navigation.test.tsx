/**
 * Accessibility Tests: Table Keyboard Navigation
 * Tests WCAG 2.1 AA compliance for data tables with keyboard support
 * Covers: Arrow key navigation, focus management, row selection
 */
/// <reference path="../a11y/jest-axe.d.ts" />

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { axe } from '../a11y/setup';

let user: ReturnType<typeof userEvent.setup>;

const getRow = (rows: HTMLElement[], index: number) => {
  const row = rows[index];
  expect(row).toBeTruthy();
  return row;
};

// Mock table component for testing
function MockDataTable({
  rows = [
    { id: '1', name: 'Item 1', priority: 'High', status: 'Active' },
    { id: '2', name: 'Item 2', priority: 'Low', status: 'Inactive' },
    { id: '3', name: 'Item 3', priority: 'Medium', status: 'Active' },
  ],
  onRowSelect = vi.fn(),
}: {
  rows?: { id: string; name: string; status: string; priority: string }[];
  onRowSelect?: (id: string) => void;
}) {
  const [selectedRow, setSelectedRow] = React.useState<string | null>(null);
  const [focusedRow, setFocusedRow] = React.useState(0);

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (index < rows.length - 1) {
        setFocusedRow(index + 1);
      }
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (index > 0) {
        setFocusedRow(index - 1);
      }
    } else if (e.key === 'Home') {
      e.preventDefault();
      setFocusedRow(0);
    } else if (e.key === 'End') {
      e.preventDefault();
      setFocusedRow(rows.length - 1);
    } else if (e.key === ' ') {
      e.preventDefault();
      setSelectedRow(rows[index].id);
      onRowSelect(rows[index].id);
    }
  };

  return (
    <table aria-label='Data table with keyboard navigation' aria-rowcount={rows.length}>
      <thead>
        <tr>
          <th>
            <input type='checkbox' aria-label='Select all rows' onChange={() => {}} />
          </th>
          <th>Name</th>
          <th>Status</th>
          <th>Priority</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row, index) => (
          <tr
            key={row.id}
            aria-rowindex={index + 2}
            tabIndex={focusedRow === index ? 0 : -1}
            aria-selected={selectedRow === row.id}
            onKeyDown={(e) => {
              handleKeyDown(index, e);
            }}
            data-testid={`table-row-${row.id}`}
            className={focusedRow === index ? 'ring-2' : ''}
          >
            <td>
              <input
                type='checkbox'
                aria-label={`Select ${row.name}`}
                checked={selectedRow === row.id}
                onChange={() => {}}
              />
            </td>
            <td>{row.name}</td>
            <td>{row.status}</td>
            <td>{row.priority}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

describe('Table Keyboard Navigation - Arrow Keys', () => {
  beforeEach(() => {
    user = userEvent.setup();
  });

  it('should support arrow down to move focus to next row', async () => {
    render(<MockDataTable />);

    const rows = screen.getAllByRole('row');
    const firstDataRow = getRow(rows, 1); // Skip header

    firstDataRow.focus();
    expect(firstDataRow).toHaveFocus();

    await user.keyboard('{ArrowDown}');
    // Focus should move to next row
    await waitFor(() => {
      const secondDataRow = getRow(rows, 2);
      expect(secondDataRow).toHaveFocus();
    });
  });

  it('should support arrow up to move focus to previous row', async () => {
    render(<MockDataTable />);

    const rows = screen.getAllByRole('row');
    const secondDataRow = getRow(rows, 2);

    secondDataRow.focus();
    await user.keyboard('{ArrowUp}');

    await waitFor(() => {
      const firstDataRow = getRow(rows, 1);
      expect(firstDataRow).toHaveFocus();
    });
  });

  it('should not navigate beyond first row with arrow up', async () => {
    render(<MockDataTable />);

    const rows = screen.getAllByRole('row');
    const firstDataRow = getRow(rows, 1);

    firstDataRow.focus();
    await user.keyboard('{ArrowUp}');

    // Should stay on first row
    expect(firstDataRow).toHaveFocus();
  });

  it('should not navigate beyond last row with arrow down', async () => {
    render(<MockDataTable />);

    const rows = screen.getAllByRole('row');
    const lastDataRow = getRow(rows, rows.length - 1);

    lastDataRow.focus();
    await user.keyboard('{ArrowDown}');

    // Should stay on last row
    expect(lastDataRow).toHaveFocus();
  });
});

describe('Table Keyboard Navigation - Home/End Keys', () => {
  beforeEach(() => {
    user = userEvent.setup();
  });

  it('should navigate to first row with Home key', async () => {
    render(<MockDataTable />);

    const rows = screen.getAllByRole('row');
    const lastDataRow = getRow(rows, rows.length - 1);

    lastDataRow.focus();
    await user.keyboard('{Home}');

    await waitFor(() => {
      const firstDataRow = getRow(rows, 1);
      expect(firstDataRow).toHaveFocus();
    });
  });

  it('should navigate to last row with End key', async () => {
    render(<MockDataTable />);

    const rows = screen.getAllByRole('row');
    const firstDataRow = getRow(rows, 1);

    firstDataRow.focus();
    await user.keyboard('{End}');

    await waitFor(() => {
      const lastDataRow = getRow(rows, rows.length - 1);
      expect(lastDataRow).toHaveFocus();
    });
  });
});

describe('Table Keyboard Navigation - Row Selection', () => {
  beforeEach(() => {
    user = userEvent.setup();
  });

  it('should select row with Space key', async () => {
    const handleRowSelect = vi.fn();
    render(<MockDataTable onRowSelect={handleRowSelect} />);

    const firstRow = screen.getByTestId('table-row-1');
    firstRow.focus();

    await user.keyboard(' ');
    expect(handleRowSelect).toHaveBeenCalledWith('1');
  });

  it('should maintain selection after navigation', async () => {
    render(<MockDataTable />);

    const firstRow = screen.getByTestId('table-row-1');
    firstRow.focus();

    await user.keyboard(' ');
    expect(firstRow).toHaveAttribute('aria-selected', 'true');

    await user.keyboard('{ArrowDown}');
    // Selection should persist
    expect(firstRow).toHaveAttribute('aria-selected', 'true');
  });
});

describe('Table Accessibility - ARIA Attributes', () => {
  it('should have proper table role and attributes', async () => {
    const { container } = render(<MockDataTable />);
    const table = screen.getByRole('grid');

    expect(table).toHaveAttribute('aria-label');
    expect(table).toHaveAttribute('aria-rowcount', '3');

    const results = await axe(container);
    expect(results.violations).toHaveLength(0);
  });

  it('should have aria-rowindex on all rows', () => {
    render(<MockDataTable />);

    const rows = screen.getAllByRole('row');
    rows.forEach((row, index) => {
      if (index > 0) {
        expect(row).toHaveAttribute('aria-rowindex', String(index + 1));
      }
    });
  });

  it('should have aria-selected on rows', () => {
    render(<MockDataTable />);

    const firstRow = screen.getByTestId('table-row-1');
    expect(firstRow).toHaveAttribute('aria-selected');
  });

  it('should have proper column header roles', () => {
    render(<MockDataTable />);

    const headers = screen.getAllByRole('columnheader');
    expect(headers.length).toBeGreaterThan(0);

    headers.forEach((header) => {
      expect(header).toHaveTextContent(/Name|Status|Priority|Select/);
    });
  });

  it('should have cell roles for all data cells', () => {
    render(<MockDataTable />);

    const cells = screen.getAllByRole('cell');
    expect(cells.length).toBeGreaterThan(0);
  });
});

describe('Table Focus Management', () => {
  beforeEach(() => {
    user = userEvent.setup();
  });

  it('should have visible focus indicator on focused row', () => {
    render(<MockDataTable />);

    const firstRow = screen.getByTestId('table-row-1');
    firstRow.focus();

    // Check for visual focus indicator
    // Should have ring or outline
    expect(firstRow.className).toContain('ring');
  });

  it('should trap focus within table for keyboard navigation', async () => {
    render(<MockDataTable />);

    const rows = screen.getAllByRole('row');
    const lastRow = getRow(rows, rows.length - 1);

    lastRow.focus();
    await user.keyboard('{ArrowDown}');

    // Should not move beyond table
    expect(lastRow).toHaveFocus();
  });
});

function ExpandableTableRow() {
  return (
    <tr
      tabIndex={0}
      aria-expanded={false}
      onKeyDown={(e) => {
        if (e.key === 'Enter') {
          e.currentTarget.setAttribute('aria-expanded', 'true');
        }
      }}
    >
      <td>
        <button aria-label='Expand row'>+</button>
      </td>
      <td>Expandable Item</td>
    </tr>
  );
}

describe('Table with Expandable Rows - Accessibility', () => {
  beforeEach(() => {
    user = userEvent.setup();
  });

  it('should support expand/collapse with keyboard', async () => {
    render(
      <table>
        <tbody>
          <ExpandableTableRow />
        </tbody>
      </table>,
    );

    const row = screen.getByRole('row');
    row.focus();
    await user.keyboard('{Enter}');

    expect(row).toHaveAttribute('aria-expanded', 'true');
  });
});

describe('Table Screen Reader Announcements', () => {
  it('should announce table dimensions', async () => {
    const { container } = render(<MockDataTable />);

    const table = screen.getByRole('grid');
    expect(table).toHaveAttribute('aria-rowcount', '3');
    expect(table).toHaveAttribute('aria-label', 'Data table with keyboard navigation');

    const results = await axe(container);
    expect(results.violations).toHaveLength(0);
  });

  it('should provide context for each cell', () => {
    render(<MockDataTable />);

    const cells = screen.getAllByRole('cell');
    cells.forEach((cell) => {
      expect(cell.textContent).toBeTruthy();
    });
  });
});

describe('Table Mobile Accessibility', () => {
  it('should have sufficient touch target size for checkboxes', () => {
    const { container } = render(<MockDataTable />);

    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach((checkbox) => {
      const rect = checkbox.getBoundingClientRect();
      // Touch target should be at least 44x44px
      expect(Math.min(rect.width, rect.height)).toBeGreaterThanOrEqual(44);
    });
  });
});
